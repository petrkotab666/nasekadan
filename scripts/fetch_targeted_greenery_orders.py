#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.github' / 'research' / 'greenery-kadan-2026'
TEXTS = OUT / 'targeted-texts'
WORK = OUT / 'targeted-work'
TEXTS.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

S = requests.Session()
S.headers.update({
    'User-Agent': 'Mozilla/5.0 (compatible; NaseKadanResearch/1.4; +https://nasekadan.cz)',
    'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.5',
})

TARGETS = {
    'KU-KU': {
        'objednávka 5/Jan/2026', 'objednávka 6/Jan/2026',
        'objednávka 10/Jan/2026', 'objednávka 12/Jan/2026',
        'objednávka 82/Jan/2026', 'objednávka 83/Jan/2026',
        'objednávka 104/Jan/2026', 'objednávka 119/Jan/2026',
    },
    'Zalabák': {
        'objednávka 20/Jan/2026', 'objednávka 22/Jan/2026',
        'objednávka 25/Jan/2026', 'objednávka 80/Jan/2026',
    },
    'Čepelák': {'objednávka 33/Jan/2026'},
}

KNOWN = {
    'objednávka 6/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36408293',
    'objednávka 20/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36407905',
    'objednávka 22/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36407989',
    'objednávka 25/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36408137',
    'objednávka 33/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36438289',
    'objednávka 80/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36685065',
    'objednávka 82/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36641861',
    'objednávka 83/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36641905',
    'objednávka 104/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36685141',
    'objednávka 119/Jan/2026': 'https://smlouvy.gov.cz/smlouva/36737225',
}


def request(url: str, *, binary: bool = False, referer: str = ''):
    headers = {'Referer': referer} if referer else {}
    last = ''
    for attempt in range(8):
        try:
            response = S.get(url, headers=headers, timeout=90, allow_redirects=True)
            if response.status_code in (429, 502, 503, 504):
                last = f'HTTP {response.status_code}'
                time.sleep(min(150, 8 * (2 ** attempt)))
                continue
            response.raise_for_status()
            time.sleep(5)
            return response.content if binary else response.text
        except Exception as exc:
            last = f'{type(exc).__name__}: {exc}'
            time.sleep(min(150, 8 * (2 ** attempt)))
    raise RuntimeError(f'{url}: {last}')


def detail_links(page: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(page, 'html.parser')
    rows: list[tuple[str, str]] = []
    for tr in soup.select('table tr'):
        text = ' '.join(tr.get_text(' ', strip=True).split())
        link = tr.select_one('a[href^="/smlouva/"]')
        if link:
            rows.append((text, urljoin('https://smlouvy.gov.cz/', link.get('href', '')).split('?')[0]))
    if rows:
        return rows
    for link in soup.select('a[href^="/smlouva/"]'):
        parent = link.find_parent(['tr', 'div', 'li'])
        text = ' '.join((parent or link).get_text(' ', strip=True).split())
        rows.append((text, urljoin('https://smlouvy.gov.cz/', link.get('href', '')).split('?')[0]))
    return rows


def discover() -> dict[str, str]:
    result = dict(KNOWN)
    wanted = set().union(*TARGETS.values())

    searches = [
        'https://smlouvy.gov.cz/vyhledavani?party_box=v37djpw&searchResultList-limit=500',
        'https://smlouvy.gov.cz/vyhledavani?party_idnum=04946081&searchResultList-limit=500',
        'https://smlouvy.gov.cz/vyhledavani?party_idnum=63165902&searchResultList-limit=500',
    ]
    for base in searches:
        for offset in (0, 10, 20, 30, 40):
            separator = '&' if '?' in base else '?'
            url = base if offset == 0 else f'{base}{separator}searchResultList-offset={offset}'
            try:
                page = request(url)
            except Exception:
                continue
            for text, detail in detail_links(page):
                lower = text.lower()
                for target in wanted:
                    if target.lower() in lower:
                        result[target] = detail
            if wanted.issubset(result):
                return result

    # Poslední cílený pokus pro objednávky, které na stránkovaném seznamu nebyly nalezeny.
    for target in sorted(wanted - result.keys()):
        url = (
            'https://smlouvy.gov.cz/vyhledavani?subject_name=M%C4%9Bsto+Kada%C5%88'
            f'&contract_descr={quote(target)}&searchResultList-limit=50'
        )
        try:
            page = request(url)
        except Exception:
            continue
        for text, detail in detail_links(page):
            if target.lower() in text.lower():
                result[target] = detail
                break
    return result


def pdf_text(pdf: Path, stem: str) -> tuple[str, str]:
    txt = TEXTS / f'{stem}.txt'
    subprocess.run(['pdftotext', '-layout', str(pdf), str(txt)], text=True, capture_output=True)
    text = txt.read_text(encoding='utf-8', errors='replace') if txt.exists() else ''
    if len(re.sub(r'\s+', '', text)) >= 150:
        return text, 'pdftotext'

    folder = WORK / stem
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    subprocess.run(
        ['pdftoppm', '-r', '250', '-png', str(pdf), str(folder / 'page')],
        text=True, capture_output=True, timeout=300,
    )
    chunks: list[str] = []
    for index, image in enumerate(sorted(folder.glob('page-*.png'))[:20], 1):
        base = folder / f'ocr-{index:03d}'
        subprocess.run(
            ['tesseract', str(image), str(base), '-l', 'ces+eng', '--psm', '6'],
            text=True, capture_output=True, timeout=180,
        )
        path = base.with_suffix('.txt')
        if path.exists():
            chunks.append(path.read_text(encoding='utf-8', errors='replace'))
    text = '\n\n'.join(chunks)
    txt.write_text(text, encoding='utf-8')
    shutil.rmtree(folder, ignore_errors=True)
    return text, 'ocr-tesseract'


def parse(target: str, url: str) -> dict:
    page = request(url)
    soup = BeautifulSoup(page, 'html.parser')
    plain = '\n'.join(x.strip() for x in soup.get_text('\n').splitlines() if x.strip())
    links: list[tuple[str, str]] = []
    for link in soup.select('a[href*="/smlouva/soubor/"]'):
        href = urljoin(url, link.get('href', ''))
        if '.pdf' in href.lower():
            links.append((link.get_text(' ', strip=True), href))

    match = re.search(r'/smlouva/(\d+)', url)
    contract_id = match.group(1) if match else re.sub(r'\D+', '', url)[-12:] or 'unknown'
    extracted: list[dict] = []
    seen: set[str] = set()
    for index, (name, href) in enumerate(links, 1):
        if href in seen:
            continue
        seen.add(href)
        safe = re.sub(r'[^0-9A-Za-zÀ-ž._-]+', '-', name).strip('-')[:90] or 'priloha'
        stem = f'{contract_id}-{index:02d}-{safe}'
        pdf = WORK / f'{stem}.pdf'
        pdf.write_bytes(request(href, binary=True, referer=url))
        text, method = pdf_text(pdf, stem)
        extracted.append({
            'name': name,
            'url': href,
            'text_file': str((TEXTS / f'{stem}.txt').relative_to(ROOT)),
            'method': method,
            'characters': len(text),
            'text': text,
        })
        pdf.unlink(missing_ok=True)
    return {'target': target, 'url': url, 'page_text': plain, 'attachments': extracted}


def main() -> None:
    found = discover()
    wanted = set().union(*TARGETS.values())
    missing = sorted(wanted - found.keys())
    rows: list[dict] = []
    for target, url in sorted(found.items()):
        if target not in wanted:
            continue
        try:
            rows.append(parse(target, url))
            print('OK', target, url)
        except Exception as exc:
            rows.append({'target': target, 'url': url, 'error': f'{type(exc).__name__}: {exc}'})
            print('FAIL', target, exc)

    payload = {'found': len(found), 'requested': len(wanted), 'missing': missing, 'orders': rows}
    (OUT / 'targeted-orders.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    md = [
        '# Klíčové celoroční objednávky zeleně – OCR', '',
        f'Vyžádáno: **{len(wanted)}**, nalezeno: **{len(found)}**, chybí: **{len(missing)}**.', '',
    ]
    if missing:
        md += ['Chybějící: ' + ', '.join(missing), '']
    for row in rows:
        md += [f"## {row['target']}", '', f"- Registr: {row['url']}"]
        if row.get('error'):
            md += [f"- Chyba: {row['error']}", '']
            continue
        if not row.get('attachments'):
            md += ['- Ve veřejném záznamu nebyla nalezena PDF příloha.', '']
        for attachment in row.get('attachments', []):
            md += [
                f"- Příloha: {attachment['name']} – **{attachment['method']}**, {attachment['characters']} znaků",
                '', '```text', attachment['text'].strip(), '```', '',
            ]
    (OUT / 'TARGETED-ORDERS.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    shutil.rmtree(WORK, ignore_errors=True)
    print(json.dumps({'requested': len(wanted), 'found': len(found), 'missing': missing, 'processed': len(rows)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
