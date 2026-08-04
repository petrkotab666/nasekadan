#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures
import hashlib
import html
import json
import os
import re
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

ROOT = Path('.github/research/hossner-cases-2026')
RAW = ROOT / 'raw'
TEXT = ROOT / 'text'
FILES = ROOT / 'files'
for p in (ROOT, RAW, TEXT, FILES):
    p.mkdir(parents=True, exist_ok=True)

UA = 'Mozilla/5.0 (compatible; NaseKadanResearch/1.0; +https://nasekadan.cz/)'
S = requests.Session()
S.headers.update({'User-Agent': UA, 'Accept-Language': 'cs,en;q=0.7'})

SPIS_RE = re.compile(r'(?i)(?:sp\.?\s*zn\.?|č\.?\s*j\.?)?\s*(\d{1,3})\s*(C|Nc|Co|Nco|Cm)\s*(\d{1,5})\s*/\s*(20\d{2})(?:\s*-\s*\d+)?')
TARGET_WORDS = ('hossner', 'nemocnice kadaň', 'nemocnice kadan', 'mediátor', 'mediator', '25,9', '25.9', '25900000', 'předběžné opatření', 'predbezne opatreni')


def get(url: str, *, timeout: int = 35, params: dict[str, Any] | None = None) -> requests.Response | None:
    try:
        r = S.get(url, timeout=timeout, params=params, allow_redirects=True)
        return r
    except Exception as exc:
        (ROOT / 'errors.log').open('a', encoding='utf-8').write(f'{url}\t{type(exc).__name__}: {exc}\n')
        return None


def write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding='utf-8')


def slug(value: str) -> str:
    value = re.sub(r'[^a-zA-Z0-9._-]+', '-', value).strip('-')
    return value[:180] or hashlib.sha256(value.encode()).hexdigest()[:16]


def visible_text(content: str) -> str:
    soup = BeautifulSoup(content, 'lxml')
    for node in soup(['script', 'style', 'noscript', 'svg']):
        node.decompose()
    return re.sub(r'\s+', ' ', soup.get_text(' ', strip=True)).strip()


def extract_document(path: Path) -> str:
    suffix = path.suffix.lower()
    out = ''
    try:
        if suffix == '.pdf':
            proc = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, timeout=90)
            out = proc.stdout.decode('utf-8', 'replace')
        elif suffix in {'.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp'}:
            import zipfile
            with zipfile.ZipFile(path) as zf:
                parts = []
                for name in zf.namelist():
                    if name.endswith('.xml') and any(k in name for k in ('document', 'sharedStrings', 'sheet', 'slide', 'content.xml')):
                        raw = zf.read(name).decode('utf-8', 'replace')
                        parts.append(visible_text(raw))
                out = '\n'.join(parts)
        elif suffix in {'.txt', '.csv', '.html', '.htm', '.xml', '.json'}:
            out = path.read_text(encoding='utf-8', errors='replace')
    except Exception as exc:
        (ROOT / 'errors.log').open('a', encoding='utf-8').write(f'extract {path}: {exc}\n')
    if out:
        write(TEXT / f'{path.name}.txt', out)
    return out


def download(url: str, label: str | None = None) -> Path | None:
    r = get(url, timeout=60)
    if not r or r.status_code != 200 or not r.content:
        return None
    parsed = urllib.parse.urlparse(r.url)
    name = Path(parsed.path).name or label or hashlib.sha256(r.url.encode()).hexdigest()[:20]
    if label and '.' not in name and '.' in label:
        name = label
    name = slug(name)
    p = FILES / name
    if p.exists() and p.stat().st_size == len(r.content):
        return p
    write(p, r.content)
    meta = {'requested_url': url, 'final_url': r.url, 'status': r.status_code, 'content_type': r.headers.get('content-type'), 'bytes': len(r.content), 'sha256': hashlib.sha256(r.content).hexdigest()}
    write(FILES / f'{name}.meta.json', json.dumps(meta, ensure_ascii=False, indent=2))
    return p


def discover_court_code() -> tuple[list[str], dict[str, Any]]:
    evidence: dict[str, Any] = {'html_options': [], 'browser_options': [], 'network_urls': [], 'js_hits': []}
    codes: list[str] = []
    home_url = 'https://infosoud.gov.cz/InfoSoud'
    r = get(home_url)
    if r:
        write(RAW / 'infosoud-home.html', r.text)
        soup = BeautifulSoup(r.text, 'lxml')
        for opt in soup.select('option'):
            text = re.sub(r'\s+', ' ', opt.get_text(' ', strip=True))
            value = opt.get('value') or ''
            if 'chomutov' in text.lower():
                evidence['html_options'].append({'text': text, 'value': value})
                if value: codes.append(value)
        for script in soup.select('script[src]'):
            src = urllib.parse.urljoin(home_url, script.get('src'))
            rr = get(src)
            if not rr or rr.status_code != 200: continue
            name = slug(Path(urllib.parse.urlparse(src).path).name)
            write(RAW / 'infosoud-js' / name, rr.text)
            low = rr.text.lower()
            pos = low.find('chomutov')
            if pos >= 0:
                excerpt = rr.text[max(0, pos-400):pos+500]
                evidence['js_hits'].append({'url': src, 'excerpt': excerpt})
                for m in re.finditer(r'[A-Z]{2,12}', excerpt):
                    token = m.group(0)
                    if token.startswith(('OS', 'SO')): codes.append(token)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on('response', lambda resp: evidence['network_urls'].append(resp.url) if ('api' in resp.url.lower() or 'cisel' in resp.url.lower() or 'soud' in resp.url.lower()) else None)
            page.goto(home_url, wait_until='networkidle', timeout=90000)
            page.wait_for_timeout(3000)
            # Select values progressively if the application requires court type and region first.
            for _ in range(3):
                selects = page.locator('select')
                for i in range(selects.count()):
                    sel = selects.nth(i)
                    opts = sel.locator('option').evaluate_all("els => els.map(e => ({text:(e.textContent||'').trim(), value:e.value}))")
                    for opt in opts:
                        t = opt['text'].lower()
                        if 'okresní' in t and opt['value']:
                            try: sel.select_option(opt['value']); page.wait_for_timeout(1200)
                            except Exception: pass
                        if 'ústí nad labem' in t and 'krajský' in t and opt['value']:
                            try: sel.select_option(opt['value']); page.wait_for_timeout(1200)
                            except Exception: pass
                page.wait_for_timeout(1000)
            options = page.locator('option').evaluate_all("els => els.map(e => ({text:(e.textContent||'').trim(), value:e.value}))")
            for opt in options:
                if 'chomutov' in opt['text'].lower():
                    evidence['browser_options'].append(opt)
                    if opt['value']: codes.append(opt['value'])
            write(RAW / 'infosoud-browser.html', page.content())
            browser.close()
    except Exception as exc:
        evidence['browser_error'] = f'{type(exc).__name__}: {exc}'
    # Plausible ministry organization identifiers, tested against a known published case below.
    codes.extend(['OSULCV', 'OSCV', 'OSCHCV', 'OSULCH', 'OSULCVV', 'OSZPCCH'])
    return list(dict.fromkeys(codes)), evidence


def case_url(code: str, number: int, year: int = 2025, senate: int = 30, kind: str = 'C') -> str:
    q = {'bcVec': number, 'cisloSenatu': senate, 'druhVeci': kind, 'okresniSoud': code, 'organizaceId': code, 'rocnik': year}
    return 'https://infosoud.gov.cz/InfoSoud/detail-rizeni?' + urllib.parse.urlencode(q)


def fetch_case(code: str, number: int, year: int = 2025, senate: int = 30, kind: str = 'C') -> dict[str, Any] | None:
    url = case_url(code, number, year, senate, kind)
    r = get(url, timeout=25)
    if not r or r.status_code != 200:
        return None
    text = visible_text(r.text)
    patterns = [
        rf'{senate}\s*{re.escape(kind)}\s*{number}\s*/\s*{year}',
        rf'{senate}\s*{re.escape(kind)}\s*{number}\s+-\s*{year}',
    ]
    valid = any(re.search(p, text, re.I) for p in patterns)
    # Some versions omit the heading but show a non-empty event table.
    if not valid and ('Průběh řízení' in text or 'Datum události' in text) and 'Tato stránka neexistuje' not in text:
        valid = len(text) > 700 and str(number) in text and str(year) in text
    if not valid:
        return None
    return {'code': code, 'number': number, 'year': year, 'senate': senate, 'kind': kind, 'url': url, 'text': text, 'html': r.text}


def identify_code(codes: list[str]) -> str | None:
    # 30 C 131/2025 is an independently published decision by judge Hana Jakubcová.
    for code in codes:
        case = fetch_case(code, 131)
        if case:
            write(RAW / 'known-case-30-C-131-2025.html', case['html'])
            write(TEXT / 'known-case-30-C-131-2025.txt', case['text'])
            return code
    return None


def scan_cases(code: str) -> list[dict[str, Any]]:
    valid: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(fetch_case, code, n): n for n in range(1, 501)}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid.append(result)
    valid.sort(key=lambda x: x['number'])
    index = []
    candidates = []
    for c in valid:
        txt = c['text']
        low = txt.lower()
        dates = sorted(set(re.findall(r'\b\d{1,2}\.\s*\d{1,2}\.\s*20\d{2}\b', txt)))
        score = 0
        reasons = []
        if re.search(r'23\.\s*0?3\.\s*2026', txt): score += 12; reasons.append('23.03.2026')
        if re.search(r'\b(?:0?[1-3])\.\s*0?1\.\s*2026|\b(?:1[0-9]|2[0-9]|3[01])\.\s*0?1\.\s*2026', txt): score += 3; reasons.append('leden 2026')
        for word, points in [('medi', 8), ('přeruš', 5), ('pracovn', 4), ('neplatnost', 5), ('jednání', 2), ('odvolání', 2), ('předběžné', 4)]:
            if word in low: score += points; reasons.append(word)
        # Initiation windows: March 2025 and July 2025.
        if re.search(r'\b\d{1,2}\.\s*0?3\.\s*2025', txt): score += 4; reasons.append('březen 2025')
        if re.search(r'\b\d{1,2}\.\s*0?7\.\s*2025', txt): score += 4; reasons.append('červenec 2025')
        item = {'spis': f"30 C {c['number']}/2025", 'url': c['url'], 'dates': dates, 'score': score, 'reasons': reasons, 'chars': len(txt)}
        index.append(item)
        if score >= 6:
            candidates.append(item)
            write(RAW / 'infosoud-candidates' / f"30-C-{c['number']}-2025.html", c['html'])
            write(TEXT / 'infosoud-candidates' / f"30-C-{c['number']}-2025.txt", txt)
    write(ROOT / 'infosoud-valid-cases.json', json.dumps(index, ensure_ascii=False, indent=2))
    write(ROOT / 'infosoud-candidates.json', json.dumps(sorted(candidates, key=lambda x: (-x['score'], x['spis'])), ensure_ascii=False, indent=2))
    return valid


def crawl_hossner() -> dict[str, Any]:
    base = 'https://petrhossnerkadan.cz'
    summary: dict[str, Any] = {'posts': [], 'media': [], 'sitemaps': [], 'downloaded': [], 'errors': []}
    links: set[str] = set()
    # WordPress REST API.
    for endpoint, bucket in [('posts', 'posts'), ('pages', 'posts'), ('media', 'media')]:
        for page in range(1, 30):
            url = f'{base}/wp-json/wp/v2/{endpoint}'
            r = get(url, params={'per_page': 100, 'page': page})
            if not r or r.status_code not in (200, 400):
                summary['errors'].append({'url': url, 'status': None if not r else r.status_code})
                break
            if r.status_code == 400: break
            try: rows = r.json()
            except Exception: break
            if not rows: break
            write(RAW / 'hossner-wp' / f'{endpoint}-{page}.json', json.dumps(rows, ensure_ascii=False, indent=2))
            for row in rows:
                rendered = html.unescape((row.get('content') or {}).get('rendered', ''))
                title = html.unescape((row.get('title') or {}).get('rendered', ''))
                source = row.get('source_url') or row.get('link')
                summary[bucket].append({'id': row.get('id'), 'date': row.get('date'), 'title': visible_text(title), 'url': source})
                for found in re.findall(r'(?:href|src)=["\']([^"\']+)', rendered, re.I):
                    links.add(urllib.parse.urljoin(base, html.unescape(found)))
                if source and endpoint == 'media': links.add(source)
            if len(rows) < 100: break
    # XML sitemaps and URLs.
    sitemap_queue = [f'{base}/wp-sitemap.xml', f'{base}/sitemap_index.xml', f'{base}/sitemap.xml']
    seen_maps = set()
    while sitemap_queue and len(seen_maps) < 30:
        url = sitemap_queue.pop(0)
        if url in seen_maps: continue
        seen_maps.add(url)
        r = get(url)
        if not r or r.status_code != 200: continue
        write(RAW / 'hossner-sitemaps' / f'{slug(url)}.xml', r.text)
        locs = re.findall(r'<loc>(.*?)</loc>', r.text, re.I | re.S)
        for loc in map(html.unescape, locs):
            if loc.endswith('.xml'): sitemap_queue.append(loc)
            else: links.add(loc)
        summary['sitemaps'].append({'url': url, 'count': len(locs)})
    # Fetch pages, inspect embedded files and textual clues.
    page_urls = [u for u in links if u.startswith(base) and not re.search(r'\.(?:jpg|jpeg|png|gif|webp|svg|pdf|docx?|xlsx?|pptx?|zip)(?:\?|$)', u, re.I)]
    for i, url in enumerate(sorted(page_urls)[:350]):
        r = get(url)
        if not r or r.status_code != 200: continue
        name = f'{i:03d}-{slug(urllib.parse.urlparse(url).path)}.html'
        write(RAW / 'hossner-pages' / name, r.text)
        txt = visible_text(r.text)
        write(TEXT / 'hossner-pages' / f'{name}.txt', txt)
        for found in re.findall(r'(?:href|src)=["\']([^"\']+)', r.text, re.I):
            absolute = urllib.parse.urljoin(url, html.unescape(found))
            if re.search(r'\.(?:pdf|docx?|xlsx?|pptx?|odt|ods|odp|txt|csv|zip)(?:\?|$)', absolute, re.I):
                links.add(absolute)
    file_urls = sorted(u for u in links if re.search(r'\.(?:pdf|docx?|xlsx?|pptx?|odt|ods|odp|txt|csv|zip)(?:\?|$)', u, re.I))
    for url in file_urls:
        p = download(url)
        if p:
            summary['downloaded'].append({'url': url, 'file': str(p), 'bytes': p.stat().st_size})
            extract_document(p)
    write(ROOT / 'hossner-crawl.json', json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def search_public_web() -> list[dict[str, Any]]:
    queries = [
        '"Petr Hossner" "sp. zn."',
        '"Petr Hossner" "30 C"',
        '"Nemocnice Kadaň" "30 C"',
        '"Nemocnice Kadaň" "č. j." Hossner',
        '"Petr Hossner" filetype:pdf',
        '"Nemocnice Kadaň" Hossner filetype:pdf',
        '"25 900 000" Hossner',
        '"25,9 milionu" "Okresní soud v Chomutově"',
        'site:mesto-kadan.cz Hossner soud',
        'site:nemkadan.cz Hossner žaloba',
        'site:smlouvy.gov.cz "Nemocnice Kadaň" Deloitte',
    ]
    rows = []
    discovered = set()
    for q in queries:
        url = 'https://html.duckduckgo.com/html/?' + urllib.parse.urlencode({'q': q})
        r = get(url)
        if not r: continue
        write(RAW / 'search' / f'{slug(q)}.html', r.text)
        soup = BeautifulSoup(r.text, 'lxml')
        for a in soup.select('.result__a, a.result__url'):
            href = a.get('href') or ''
            parsed = urllib.parse.urlparse(href)
            if 'uddg=' in href:
                href = urllib.parse.parse_qs(parsed.query).get('uddg', [href])[0]
            title = a.get_text(' ', strip=True)
            if href.startswith('http'):
                rows.append({'query': q, 'title': title, 'url': href})
                discovered.add(href)
    # Download document-like results.
    for url in sorted(discovered):
        if re.search(r'\.(?:pdf|docx?|xlsx?|pptx?)(?:\?|$)', url, re.I):
            p = download(url)
            if p: extract_document(p)
    write(ROOT / 'public-search-results.json', json.dumps(rows, ensure_ascii=False, indent=2))
    return rows


def crawl_wayback() -> list[dict[str, Any]]:
    patterns = [
        'petrhossnerkadan.cz/*',
        'nemkadan.cz/*hossner*',
        'mesto-kadan.cz/*hossner*',
        'mesto-kadan.cz/*nemocnice*',
    ]
    all_rows = []
    for pattern in patterns:
        params = [('url', pattern), ('output', 'json'), ('filter', 'statuscode:200'), ('filter', 'collapse:digest'), ('fl', 'timestamp,original,mimetype,statuscode,digest'), ('limit', '5000')]
        r = get('https://web.archive.org/cdx/search/cdx', params=dict(params), timeout=90)
        if not r or r.status_code != 200: continue
        try: data = r.json()
        except Exception: continue
        if not data: continue
        headers, *items = data
        rows = [dict(zip(headers, item)) for item in items]
        all_rows.extend(rows)
        write(RAW / 'wayback' / f'{slug(pattern)}.json', json.dumps(rows, ensure_ascii=False, indent=2))
    # Download a bounded set of archived PDFs/documents and unique Hossner pages.
    selected = []
    for row in all_rows:
        original = row.get('original', '')
        mime = row.get('mimetype', '')
        if ('hossner' in original.lower() or mime in {'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}):
            selected.append(row)
    for row in selected[:250]:
        archived = f"https://web.archive.org/web/{row['timestamp']}id_/{row['original']}"
        p = download(archived, label=f"wayback-{row['timestamp']}-{Path(urllib.parse.urlparse(row['original']).path).name or 'page.html'}")
        if p: extract_document(p)
    write(ROOT / 'wayback-index.json', json.dumps(all_rows, ensure_ascii=False, indent=2))
    return all_rows


def collect_spis_hits() -> list[dict[str, Any]]:
    hits = []
    for p in list(TEXT.rglob('*')) + list(RAW.rglob('*.html')) + list(RAW.rglob('*.json')):
        if not p.is_file(): continue
        try: content = p.read_text(encoding='utf-8', errors='replace')
        except Exception: continue
        low = content.lower()
        matches = []
        for m in SPIS_RE.finditer(content):
            context = re.sub(r'\s+', ' ', content[max(0, m.start()-250):m.end()+350])
            matches.append({'match': m.group(0), 'normalized': f'{m.group(1)} {m.group(2)} {m.group(3)}/{m.group(4)}', 'context': context})
        target_context = any(w in low for w in TARGET_WORDS)
        if matches or target_context:
            hits.append({'file': str(p), 'spis_matches': matches, 'target_words': [w for w in TARGET_WORDS if w in low]})
    write(ROOT / 'spis-hits.json', json.dumps(hits, ensure_ascii=False, indent=2))
    return hits


def main() -> None:
    started = time.time()
    codes, code_evidence = discover_court_code()
    write(ROOT / 'court-code-evidence.json', json.dumps(code_evidence, ensure_ascii=False, indent=2))
    code = identify_code(codes)
    court_summary: dict[str, Any] = {'candidate_codes': codes, 'verified_code': code}
    if code:
        valid = scan_cases(code)
        court_summary['valid_30C_2025_count'] = len(valid)
    else:
        court_summary['error'] = 'Nepodařilo se ověřit organizační kód soudu proti známé věci 30 C 131/2025.'
    write(ROOT / 'court-summary.json', json.dumps(court_summary, ensure_ascii=False, indent=2))
    hossner = crawl_hossner()
    public = search_public_web()
    wayback = crawl_wayback()
    hits = collect_spis_hits()
    final = {
        'generated_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'elapsed_seconds': round(time.time() - started, 1),
        'court': court_summary,
        'hossner_posts': len(hossner.get('posts', [])),
        'hossner_media': len(hossner.get('media', [])),
        'hossner_downloads': len(hossner.get('downloaded', [])),
        'public_search_results': len(public),
        'wayback_rows': len(wayback),
        'files_with_spis_or_target_hits': len(hits),
    }
    write(ROOT / 'summary.json', json.dumps(final, ensure_ascii=False, indent=2))
    print(json.dumps(final, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
