#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path('.github/research/hossner-cases-2026')
RAW = ROOT / 'raw'
OUT = ROOT / 'infosoud-api'
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'https://infosoud.gov.cz'
S = requests.Session()
S.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; NaseKadanResearch/1.1; +https://nasekadan.cz/)', 'Accept-Language': 'cs,en;q=0.7'})


def save(name: str, value) -> None:
    p = OUT / name
    if isinstance(value, (dict, list)):
        p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    elif isinstance(value, bytes):
        p.write_bytes(value)
    else:
        p.write_text(str(value), encoding='utf-8')


def request(path: str):
    url = path if path.startswith('http') else urljoin(BASE, path)
    try:
        r = S.get(url, timeout=45)
        record = {'url': r.url, 'status': r.status_code, 'content_type': r.headers.get('content-type'), 'text': r.text[:500000]}
        return r, record
    except Exception as exc:
        return None, {'url': url, 'error': f'{type(exc).__name__}: {exc}'}


# Extract every API-looking string from all downloaded JS bundles.
api_strings = set()
for js in (RAW / 'infosoud-js').glob('*.js'):
    text = js.read_text(encoding='utf-8', errors='replace')
    for m in re.finditer(r'(?:https?://[^"\'`\\ ]+)?/api/v1/[A-Za-z0-9_?=&./{}:${}-]+', text):
        api_strings.add(m.group(0))
    for m in re.finditer(r'["\'`]([^"\'`]{0,80}(?:rizeni|řízení|udalost|událost|spisova|jednani|jednání)[^"\'`]{0,120})["\'`]', text, re.I):
        api_strings.add(m.group(1))
save('js-api-strings.json', sorted(api_strings))

# Probe public dictionaries and API documentation.
probes = [
    '/api/v1/env',
    '/api/v1/organizace/lov',
    '/api/v1/organizace/podrizene/lov?idOrganizace=KSSCEUL',
    '/api/v1/spisova-znacka/druh/lovkod?typ=rizeni',
    '/v3/api-docs', '/api-docs', '/swagger-ui/index.html', '/swagger-ui.html', '/openapi.json',
]
probe_records = []
for path in probes:
    r, rec = request(path)
    probe_records.append(rec)
    if r and r.status_code == 200:
        suffix = re.sub(r'[^A-Za-z0-9.-]+', '-', path).strip('-') or 'root'
        save(f'probe-{suffix}.txt', r.text)
save('probe-records.json', probe_records)

# Parse organization JSON and preserve all Chomutov references.
chomutov_hits = []
for rec in probe_records:
    text = rec.get('text', '')
    if 'chomutov' in text.lower():
        try:
            data = json.loads(text)
        except Exception:
            data = text
        chomutov_hits.append({'url': rec.get('url'), 'data': data})
save('chomutov-organization-hits.json', chomutov_hits)

# Browser: fill a known valid case and record exact requests plus response bodies.
network = []
dom = {}
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def on_response(resp):
            if '/api/' not in resp.url:
                return
            item = {'url': resp.url, 'status': resp.status, 'method': resp.request.method, 'post_data': resp.request.post_data}
            try:
                body = resp.body()
                item['body'] = body.decode('utf-8', 'replace')[:1000000]
            except Exception as exc:
                item['body_error'] = str(exc)
            network.append(item)

        page.on('response', on_response)
        page.goto(BASE + '/InfoSoud', wait_until='networkidle', timeout=90000)
        page.wait_for_timeout(2500)

        selects = page.locator('select')
        dom['selects_initial'] = []
        for i in range(selects.count()):
            sel = selects.nth(i)
            dom['selects_initial'].append({
                'index': i,
                'name': sel.get_attribute('name'),
                'id': sel.get_attribute('id'),
                'aria': sel.get_attribute('aria-label'),
                'options': sel.locator('option').evaluate_all("els => els.map(e => ({text:(e.textContent||'').trim(), value:e.value}))"),
            })

        # Progressive selection: district-court type, Ústí region, Chomutov district court and C register.
        for wanted in ['Okresní', 'Krajský soud v Ústí nad Labem', 'Okresní soud Chomutov', 'C']:
            chosen = False
            for i in range(page.locator('select').count()):
                sel = page.locator('select').nth(i)
                options = sel.locator('option').evaluate_all("els => els.map(e => ({text:(e.textContent||'').trim(), value:e.value}))")
                exact = [o for o in options if o['text'].strip().lower() == wanted.lower() and o['value']]
                contains = [o for o in options if wanted.lower() in o['text'].lower() and o['value']]
                pool = exact or contains
                if pool:
                    try:
                        sel.select_option(pool[0]['value'])
                        page.wait_for_timeout(1400)
                        chosen = True
                        break
                    except Exception:
                        pass
            dom.setdefault('selection', []).append({'wanted': wanted, 'chosen': chosen})

        inputs = page.locator('input')
        dom['inputs'] = []
        visible_text_inputs = []
        for i in range(inputs.count()):
            inp = inputs.nth(i)
            info = {k: inp.get_attribute(k) for k in ('name', 'id', 'type', 'placeholder', 'aria-label', 'formcontrolname')}
            info['index'] = i
            info['visible'] = inp.is_visible()
            dom['inputs'].append(info)
            if inp.is_visible() and (info.get('type') in (None, '', 'text', 'number')):
                visible_text_inputs.append(inp)

        # Prefer semantic names. Fallback to visible input order: senate, ordinary number, year.
        values = [('senat', '30'), ('cislo', '131'), ('rocnik', '2025')]
        used = set()
        for needle, value in values:
            for i in range(inputs.count()):
                inp = inputs.nth(i)
                attrs = ' '.join(str(inp.get_attribute(k) or '') for k in ('name', 'id', 'placeholder', 'aria-label', 'formcontrolname')).lower()
                if inp.is_visible() and needle in attrs and i not in used:
                    inp.fill(value); used.add(i); break
        remaining_values = ['30', '131', '2025']
        # Remove values already present.
        for inp in visible_text_inputs:
            try:
                if inp.input_value() in remaining_values:
                    remaining_values.remove(inp.input_value())
            except Exception:
                pass
        for inp, value in zip([x for x in visible_text_inputs if not x.input_value()], remaining_values):
            try: inp.fill(value)
            except Exception: pass

        dom['buttons'] = []
        buttons = page.locator('button')
        for i in range(buttons.count()):
            b = buttons.nth(i)
            dom['buttons'].append({'index': i, 'text': b.inner_text().strip(), 'type': b.get_attribute('type'), 'aria': b.get_attribute('aria-label'), 'visible': b.is_visible(), 'disabled': b.is_disabled()})

        submitted = False
        for i in range(buttons.count()):
            b = buttons.nth(i)
            text = b.inner_text().strip().lower()
            if b.is_visible() and not b.is_disabled() and ('zobraz' in text or b.get_attribute('type') == 'submit'):
                try:
                    b.click(); submitted = True; break
                except Exception:
                    pass
        if not submitted:
            try:
                page.locator('form').first.evaluate('f => f.requestSubmit()')
                submitted = True
            except Exception:
                pass
        page.wait_for_timeout(7000)
        dom['submitted'] = submitted
        dom['final_url'] = page.url
        save('known-case-page.html', page.content())
        save('known-case-visible.txt', page.locator('body').inner_text())
        save('browser-dom.json', dom)
        save('browser-network.json', network)
        browser.close()
except Exception as exc:
    save('browser-error.txt', f'{type(exc).__name__}: {exc}')

# Summarize promising API calls.
promising = []
for item in network:
    low = (item.get('url', '') + ' ' + item.get('body', '')).lower()
    if any(k in low for k in ('131', 'rizeni', 'udál', 'udal', 'spis')):
        promising.append(item)
save('promising-network.json', promising)

summary = {
    'generated_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'js_strings': len(api_strings),
    'network_calls': len(network),
    'promising_calls': len(promising),
    'chomutov_hits': len(chomutov_hits),
    'final_url': dom.get('final_url'),
    'submitted': dom.get('submitted'),
}
save('summary.json', summary)
print(json.dumps(summary, ensure_ascii=False, indent=2))
