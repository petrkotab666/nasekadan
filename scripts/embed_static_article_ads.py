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

BLOCK = '<div class="static-article-ads" data-static-article-ads="locked-v1" aria-label="Reklamy v pravém sloupci článku">' + ''.join(
    f'<a class="static-article-ad" href="{url}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span>REKLAMA</span><img src="{img}" width="300" height="600" alt="{alt}" loading="lazy" decoding="async"></a>'
    for url,img,alt in ADS
) + '</div>'

CSS = '''
<style id="static-article-ads-style">
/* Jediný povolený reklamní systém uvnitř článků. */
main.article-shell.wrap{width:min(1280px,calc(100% - 40px))!important;max-width:1280px!important;grid-template-columns:minmax(0,1fr) 300px!important;column-gap:40px!important;align-items:start!important}
main.article-shell>article{min-width:0!important}
main.article-shell>aside.sticky{box-sizing:border-box!important;width:300px!important;min-width:300px!important;max-width:300px!important;position:relative!important;top:auto!important;align-self:start!important;display:block!important;overflow:visible!important}
.article-side-ad-column,.article-ad-rail,.article-aside-tower,.article-ad-auto,article.article>[data-promos],aside.sticky>[data-promos]{display:none!important}
.static-article-ads{box-sizing:border-box!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;gap:36px!important;width:300px!important;min-width:300px!important;max-width:300px!important;margin:0!important;padding:0 0 24px!important;overflow:visible!important}
.static-article-ad{box-sizing:border-box!important;display:block!important;flex:0 0 auto!important;width:300px!important;min-width:300px!important;max-width:300px!important;height:626px!important;min-height:626px!important;margin:0!important;padding:0!important;background:#fff!important;border:1px solid #d8e0e4!important;border-radius:18px!important;overflow:hidden!important;box-shadow:0 14px 38px rgba(18,35,45,.14)!important;text-decoration:none!important}
.static-article-ad>span{box-sizing:border-box!important;display:block!important;height:26px!important;padding:7px 9px 6px!important;color:#747f85!important;background:#f5f7f8!important;border-bottom:1px solid #e1e6e8!important;font:900 9px/1 Arial,sans-serif!important;letter-spacing:.12em!important;text-align:center!important}
.static-article-ad img{box-sizing:border-box!important;display:block!important;width:300px!important;min-width:300px!important;max-width:300px!important;height:600px!important;min-height:600px!important;max-height:600px!important;object-fit:contain!important;object-position:center!important;background:#fff!important;border:0!important;margin:0!important;padding:0!important;transform:none!important}
@media(max-width:1120px){main.article-shell.wrap{grid-template-columns:1fr!important}.static-article-ads{display:none!important}}
</style>
'''

for path in ARTICLES.glob('*.html'):
    if path.name == 'index.html':
        continue
    text = path.read_text(encoding='utf-8')
    if '<main class="wrap article-shell"' not in text or '<aside class="sticky"' not in text:
        continue
    text = re.sub(r'<div class="static-article-ads".*?</div>', '', text, flags=re.S)
    text = re.sub(r'<style id="static-article-ads-style">.*?</style>\s*', '', text, flags=re.S)
    text = text.replace('</head>', CSS + '</head>', 1)
    text = text.replace('<aside class="sticky">', '<aside class="sticky">' + BLOCK, 1)
    path.write_text(text, encoding='utf-8', newline='\n')
    print('Doplněno:', path.name)
