#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path('.github/research/hossner-cases-2026/infosoud-cases')
ROOT.mkdir(parents=True, exist_ok=True)
BASE = 'https://infosoud.gov.cz'
CASES = [84, 211]


def save(name: str, data) -> None:
    p = ROOT / name
    if isinstance(data, (dict, list)):
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        p.write_text(str(data), encoding='utf-8')


def capture_case(page, number: int) -> dict:
    calls = []
    def on_response(resp):
        if '/api/' not in resp.url:
            return
        item = {
            'url': resp.url,
            'status': resp.status,
            'method': resp.request.method,
            'post_data': resp.request.post_data,
        }
        try:
            item['body'] = resp.body().decode('utf-8', 'replace')[:2_000_000]
        except Exception as exc:
            item['body_error'] = str(exc)
        calls.append(item)

    page.on('response', on_response)
    page.goto(BASE + '/InfoSoud', wait_until='networkidle', timeout=90_000)
    page.wait_for_timeout(2000)

    # Exact form field names observed in the live DOM.
    page.locator('select[name="typOrganizace"]').select_option('0')
    page.wait_for_timeout(500)
    page.locator('select[name="druhOrganizace"]').select_option('7')
    page.wait_for_timeout(1000)
    page.locator('select[name="okresniSoud"]').select_option('19')
    page.wait_for_timeout(500)
    page.locator('input[name="znackaSenat"]').fill('30')
    page.locator('input[name="znackaDruh"]').fill('C')
    page.locator('input[name="znackaCislo"]').fill(str(number))
    page.locator('input[name="znackaRok"]').fill('2025')

    buttons = page.locator('button')
    submit_info = []
    clicked = False
    for i in range(buttons.count()):
        b = buttons.nth(i)
        try:
            info = {
                'index': i,
                'text': b.inner_text().strip(),
                'type': b.get_attribute('type'),
                'visible': b.is_visible(),
                'disabled': b.is_disabled(),
            }
            submit_info.append(info)
            if not clicked and info['visible'] and not info['disabled'] and (info['type'] == 'submit' or any(x in info['text'].lower() for x in ('vyhled', 'zobraz', 'odeslat'))):
                b.click()
                clicked = True
                break
        except Exception:
            pass
    if not clicked:
        page.locator('form').first.evaluate('f => f.requestSubmit()')
        clicked = True

    page.wait_for_timeout(8000)
    body = page.locator('body').inner_text()
    html = page.content()
    result = {
        'case': f'30 C {number}/2025',
        'clicked': clicked,
        'final_url': page.url,
        'title': page.title(),
        'buttons': submit_info,
        'visible_text': body,
        'network': calls,
    }
    save(f'30-C-{number}-2025.json', result)
    save(f'30-C-{number}-2025.html', html)
    save(f'30-C-{number}-2025.txt', body)
    page.remove_listener('response', on_response)
    return result


def capture_infojednani(page, number: int) -> dict:
    calls = []
    def on_response(resp):
        if '/api/' not in resp.url:
            return
        item = {'url': resp.url, 'status': resp.status, 'method': resp.request.method, 'post_data': resp.request.post_data}
        try: item['body'] = resp.body().decode('utf-8', 'replace')[:2_000_000]
        except Exception as exc: item['body_error'] = str(exc)
        calls.append(item)
    page.on('response', on_response)
    page.goto(BASE + '/InfoJednani', wait_until='networkidle', timeout=90_000)
    page.wait_for_timeout(2500)
    dom = {'selects': [], 'inputs': [], 'buttons': []}
    for i in range(page.locator('select').count()):
        s = page.locator('select').nth(i)
        dom['selects'].append({'index': i, 'name': s.get_attribute('name'), 'options': s.locator('option').evaluate_all("els => els.map(e=>({text:(e.textContent||'').trim(),value:e.value}))")})
    for i in range(page.locator('input').count()):
        inp = page.locator('input').nth(i)
        dom['inputs'].append({'index': i, 'name': inp.get_attribute('name'), 'type': inp.get_attribute('type'), 'placeholder': inp.get_attribute('placeholder'), 'visible': inp.is_visible()})
    # Fill court and case wherever fields exist.
    for selector, value in [
        ('select[name="typOrganizace"]','0'), ('select[name="druhOrganizace"]','7'), ('select[name="okresniSoud"]','19'),
    ]:
        if page.locator(selector).count():
            try: page.locator(selector).select_option(value); page.wait_for_timeout(700)
            except Exception: pass
    field_values = {'znackaSenat':'30','znackaDruh':'C','znackaCislo':str(number),'znackaRok':'2025'}
    for name, value in field_values.items():
        loc = page.locator(f'input[name="{name}"]')
        if loc.count():
            try: loc.fill(value)
            except Exception: pass
    # If exact spis fields absent, leave form untouched; page itself may show all next-30-day hearings.
    for i in range(page.locator('button').count()):
        b = page.locator('button').nth(i)
        try: dom['buttons'].append({'index':i,'text':b.inner_text().strip(),'type':b.get_attribute('type'),'visible':b.is_visible(),'disabled':b.is_disabled()})
        except Exception: pass
    for i, info in enumerate(dom['buttons']):
        if info['visible'] and not info['disabled'] and (info['type']=='submit' or any(x in info['text'].lower() for x in ('vyhled','zobraz'))):
            try: page.locator('button').nth(i).click(); page.wait_for_timeout(7000); break
            except Exception: pass
    body = page.locator('body').inner_text()
    result = {'case':f'30 C {number}/2025','url':page.url,'dom':dom,'visible_text':body,'network':calls}
    save(f'jednani-30-C-{number}-2025.json', result)
    save(f'jednani-30-C-{number}-2025.html', page.content())
    save(f'jednani-30-C-{number}-2025.txt', body)
    page.remove_listener('response', on_response)
    return result


def main():
    from playwright.sync_api import sync_playwright
    summary = {'generated_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'cases': []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        for n in CASES:
            try:
                case_result = capture_case(page, n)
                summary['cases'].append({'case':case_result['case'],'final_url':case_result['final_url'],'chars':len(case_result['visible_text']),'api_calls':len(case_result['network'])})
            except Exception as exc:
                summary['cases'].append({'case':f'30 C {n}/2025','error':f'{type(exc).__name__}: {exc}'})
            try:
                hearing = capture_infojednani(page, n)
                summary['cases'][-1]['jednani_chars'] = len(hearing['visible_text'])
                summary['cases'][-1]['jednani_api_calls'] = len(hearing['network'])
            except Exception as exc:
                summary['cases'][-1]['jednani_error'] = f'{type(exc).__name__}: {exc}'
        browser.close()
    save('summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
