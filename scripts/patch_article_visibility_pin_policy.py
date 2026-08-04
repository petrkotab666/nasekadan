#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'scripts' / 'enforce_all_article_visibility.py'
PIN_HREF = '/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html'
PIN_UNTIL_ISO = '2026-08-05T16:00:00+00:00'
MARKER = 'NK-STADIUM-PIN-POLICY-20260804'


def main() -> None:
    text = PATH.read_text(encoding='utf-8')

    old_setup = '''    # Jednorázové připnutí zimního stadionu bylo příčinou soupeřících verzí
    # titulky. Kanonická obnova proto vždy používá skutečné chronologické pořadí.
    engine.article_info = safe_article_info
    engine.HOMEPAGE_PIN_UNTIL = datetime.fromtimestamp(0, tz=timezone.utc)
    engine.main()
'''
    new_setup = f'''    # {MARKER}
    # Do stanoveného termínu je článek o zpřístupnění zimního stadionu
    # redakčně připnutý pouze na titulce. Archiv a RSS zůstávají chronologické.
    pin_href = {PIN_HREF!r}
    pin_until = datetime.fromisoformat({PIN_UNTIL_ISO!r})
    pin_active = datetime.now(timezone.utc) <= pin_until
    engine.article_info = safe_article_info
    if pin_active:
        engine.HOMEPAGE_PIN_HREF = pin_href
        engine.HOMEPAGE_PIN_UNTIL = pin_until
    else:
        engine.HOMEPAGE_PIN_HREF = ''
        engine.HOMEPAGE_PIN_UNTIL = datetime.fromtimestamp(0, tz=timezone.utc)
    engine.main()
'''
    if MARKER not in text:
        if old_setup not in text:
            raise RuntimeError('Původní blok nastavení titulky nebyl nalezen.')
        text = text.replace(old_setup, new_setup, 1)

    old_validation = '''    home = (ROOT / "index.html").read_text(encoding="utf-8")
    latest = all_hrefs[0]
    hero = re.search(r'<section\\b[^>]*class=["\\'][^"\\']*\\bhero\\b[^"\\']*["\\'][^>]*\\bid=["\\']clanky["\\'][^>]*>.*?</section>', home, re.I | re.S)
    if not hero or f'data-latest-article-href="{latest}"' not in hero.group(0):
        raise RuntimeError(f"Titulka nemá skutečně nejnovější článek: {latest}")
'''
    new_validation = '''    home = (ROOT / "index.html").read_text(encoding="utf-8")
    latest = all_hrefs[0]
    expected_hero = pin_href if pin_active else latest
    hero = re.search(r'<section\\b[^>]*class=["\\'][^"\\']*\\bhero\\b[^"\\']*["\\'][^>]*\\bid=["\\']clanky["\\'][^>]*>.*?</section>', home, re.I | re.S)
    if not hero or f'data-latest-article-href="{expected_hero}"' not in hero.group(0):
        raise RuntimeError(f"Titulka nemá očekávaný hlavní článek: {expected_hero}")
    if pin_active:
        aside = re.search(r'<aside\\b[^>]*class=["\\'][^"\\']*current-aside[^"\\']*["\\'][^>]*>.*?</aside>', hero.group(0), re.I | re.S)
        if not aside or latest not in aside.group(0):
            raise RuntimeError(f"Boční blok nemá skutečně nejnovější článek: {latest}")
'''
    if old_validation in text:
        text = text.replace(old_validation, new_validation, 1)
    elif 'expected_hero = pin_href if pin_active else latest' not in text:
        raise RuntimeError('Validační blok titulky nebyl nalezen.')

    compile(text, str(PATH), 'exec')
    PATH.write_text(text, encoding='utf-8', newline='\n')
    print('Kanonická pojistka respektuje časově omezené připnutí titulky.')


if __name__ == '__main__':
    main()
