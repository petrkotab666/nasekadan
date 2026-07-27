#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / 'clanky'

ADS = [
    ('https://pojistime.to','/assets/reklamy/pojistime-300x600.svg','Pojistime.to'),
    ('https://vaseuklizecka.cz','/assets/reklamy/vaseuklizecka-300x600.svg','VašeUklízečka.cz'),
    ('https://vyklidime.to','/assets/reklamy/vyklidime-300x600.svg','Vyklidime.to'),
    ('https://realitykadan.cz','/assets/reklamy/realitykadan-300x600.svg','RealityKadan.cz'),
]

BLOCK = '<div class="static-article-ads" aria-label="Reklamy v pravém sloupci článku">' + ''.join(
    f'<a class="static-article-ad" href="{url}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span>REKLAMA</span><img src="{img}" width="300" height="600" alt="{alt}" loading="lazy" decoding="async"></a>'
    for url,img,alt in ADS
) + '</div>'

CSS = '''
<style id="static-article-ads-style">
main.article-shell{grid-template-columns:minmax(0,820px) 320px!important;align-items:stretch!important}
aside.sticky{position:relative!important;top:auto!important;align-self:stretch!important;display:flex!important;flex-direction:column!important}
.static-article-ads{display:flex;flex:1;flex-direction:column;justify-content:space-between;gap:72px;margin-top:28px;padding-bottom:24px}
.static-article-ad{display:block;width:300px;max-width:100%;margin:0 auto;background:#fff;border:1px solid #d8e0e4;border-radius:18px;overflow:hidden;box-shadow:0 14px 38px rgba(18,35,45,.14);text-decoration:none}
.static-article-ad>span{display:block;padding:7px 9px 6px;color:#747f85;background:#f5f7f8;border-bottom:1px solid #e1e6e8;font-size:9px;font-weight:900;letter-spacing:.12em;text-align:center}
.static-article-ad img{display:block;width:100%;height:auto;aspect-ratio:1/2;object-fit:contain;background:#fff}
@media(max-width:980px){main.article-shell{grid-template-columns:1fr!important}.static-article-ads{display:none!important}}
</style>
'''

for path in ARTICLES.glob('*.html'):
    if path.name == 'index.html':
        continue
    text = path.read_text(encoding='utf-8')
    if '<main class="wrap article-shell"' not in text or '<aside class="sticky"' not in text:
        continue
    text = re.sub(r'<div class="static-article-ads".*?</div>', '', text, flags=re.S)
    if 'id="static-article-ads-style"' not in text:
        text = text.replace('</head>', CSS + '</head>', 1)
    text = text.replace('<aside class="sticky">', '<aside class="sticky">' + BLOCK, 1)
    path.write_text(text, encoding='utf-8', newline='\n')
    print('Doplněno:', path.name)
