#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

# Jediným zdrojem pravdy je normalizační skript. Ten článek zveřejní,
# odstraní návrhové a statické reklamní prvky a zapojí dynamický proud nabídek.
subprocess.run(['python3', str(ROOT / 'scripts' / 'normalize_arc_med_article.py')], check=True)

p = ROOT / 'clanky' / 'arc-med-nemocnice-kadan.html'
final = p.read_text(encoding='utf-8')

assert 'noindex' not in final
assert 'PŘIPRAVOVANÝ ČLÁNEK' not in final
assert 'Pracovní verze' not in final
assert 'static-article-ads' not in final
assert '<article class="article">' in final
assert '<div data-promos data-context="sidebar"></div>' in final
assert '/reklamy.js?' in final
assert '/reklamy-sidebar.js?' in final

print('ARC-MED obnoven jako veřejný článek s dynamickým proudem různých reklam.')
