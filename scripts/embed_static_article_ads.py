#!/usr/bin/env python3
"""Kompatibilní název starého skriptu.

Dříve vkládal pevnou čtveřici bannerů. Nyní naopak všechny takové bloky
odstraňuje a obnovuje jednotný dynamický reklamní systém s různými nabídkami.
Starší workflow jej mohou dál bezpečně volat.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / 'clanky'

SCRIPTS = '''
<script src="/reklamy.js?v=20260728-dynamic-2"></script>
<script src="/reklamy-sidebar.js?v=20260728-adstream-4"></script>
<script src="/reklamy-oprava-obrazku.js?v=20260728-dynamic-2"></script>
<script src="/obsah-doplnky.js?v=20260728-dynamic-2"></script>
'''

for path in ARTICLES.glob('*.html'):
    if path.name == 'index.html':
        continue

    text = path.read_text(encoding='utf-8')
    if '<main class="wrap article-shell"' not in text or '<aside class="sticky"' not in text:
        continue

    # Odstranit všechny historické pevné reklamní bloky a jejich CSS.
    text = re.sub(r'<style id="static-article-ads-style">.*?</style>\s*', '', text, flags=re.S)
    text = re.sub(r'<div class="static-article-ads".*?</div>', '', text, flags=re.S)
    text = re.sub(r'<div class="article-aside-tower".*?</div>', '', text, flags=re.S)

    # Článková třída je nutná pro dynamické rozmisťování reklam uvnitř textu.
    text = re.sub(r'<article(?![^>]*class=)>', '<article class="article">', text, count=1)

    # Jedna standardní pozice v pravém sloupci; reklamy-sidebar.js ji rozšíří
    # na proud různých partnerů podle skutečné výšky článku.
    text = re.sub(r'<div\s+data-promos\s+data-context="sidebar"[^>]*>.*?</div>', '', text, flags=re.S)
    text = text.replace('</aside>', '  <div data-promos data-context="sidebar"></div>\n</aside>', 1)

    # Odstranit starší verze reklamních skriptů a vložit jedinou aktuální sadu.
    for script_name in ('reklamy.js', 'reklamy-sidebar.js', 'reklamy-oprava-obrazku.js', 'obsah-doplnky.js'):
        text = re.sub(rf'\s*<script[^>]+src="/{re.escape(script_name)}[^>]*></script>', '', text)
    text = text.replace('</body>', SCRIPTS + '</body>', 1)

    if 'static-article-ads' in text:
        raise RuntimeError(f'{path.name}: nepodařilo se odstranit pevný reklamní systém')
    if 'data-promos data-context="sidebar"' not in text or '/reklamy-sidebar.js?' not in text:
        raise RuntimeError(f'{path.name}: nepodařilo se obnovit dynamický reklamní proud')

    path.write_text(text, encoding='utf-8', newline='\n')
    print('Dynamické reklamy obnoveny:', path.name)
