#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'clanky' / 'arc-med-nemocnice-kadan.html'
t = p.read_text(encoding='utf-8')

t = t.replace('content="noindex,nofollow"', 'content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"')
t = t.replace('PŘIPRAVOVANÝ ČLÁNEK', '28. ČERVENCE 2026')
t = t.replace('<article>', '<article class="article">', 1)
t = t.replace('../../favicon.svg', '../favicon.svg').replace('../../style.css', '../style.css')
t = t.replace('../../index.html', '../index.html').replace('../../pruvodce/', '../pruvodce/')
t = re.sub(r'<div class="sidebox"><h3>Pracovní verze</h3>.*?</div>\s*', '', t, count=1, flags=re.S)
t = re.sub(r'<div data-promos data-context="sidebar"></div>\s*', '', t, flags=re.S)
t = re.sub(r'\s*<script src="/reklamy\.js[^>]*></script>', '', t)
t = re.sub(r'\s*<script src="/reklamy-oprava-obrazku\.js[^>]*></script>', '', t)
t = re.sub(r'\s*<script src="/obsah-doplnky\.js[^>]*></script>', '', t)

published = '2026-07-28T05:00:00+02:00'
if 'article:published_time' not in t:
    t = t.replace('</head>', f'<meta property="article:published_time" content="{published}"><meta property="article:modified_time" content="{published}">\n</head>', 1)
else:
    t = re.sub(r'(<meta property="article:published_time" content=")[^"]+', r'\g<1>'+published, t)
    t = re.sub(r'(<meta property="article:modified_time" content=")[^"]+', r'\g<1>'+published, t)

p.write_text(t, encoding='utf-8', newline='\n')

# Použít stejný statický reklamní systém jako u ostatních článků.
import subprocess
subprocess.run(['python3', str(ROOT/'scripts'/'embed_static_article_ads.py')], check=True)

# Povinné kontroly – článek nesmí znovu skončit jako návrh.
final = p.read_text(encoding='utf-8')
assert 'noindex' not in final
assert 'PŘIPRAVOVANÝ ČLÁNEK' not in final
assert '<article class="article">' in final
assert final.count('class="static-article-ad"') == 4
print('ARC-MED obnoven jako veřejný článek se sjednocenými reklamami.')
