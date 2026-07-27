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
main.article-shell.wrap{max-width:1240px!important;grid-template-columns:minmax(0,1fr) 300px!important;gap:36px!important;align-items:stretch!important}
main.article-shell>article.article{min-width:0!important}
main.article-shell>aside.sticky{width:300px!important;min-width:300px!important;max-width:300px!important;position:relative!important;top:auto!important;align-self:stretch!important;display:flex!important;flex-direction:column!important;overflow:visible!important}
.article-side-ad-column,.article-ad-rail,.article-aside-tower{display:none!important}
.static-article-ads{display:flex!important;flex:1;flex-direction:column;justify-content:space-between;gap:72px;margin-top:28px;padding-bottom:24px;width:300px!important;overflow:visible!important}
.static-article-ad{display:block!important;width:300px!important;height:auto!important;margin:0!important;background:#fff;border:1px solid #d8e0e4;border-radius:18px;overflow:hidden;box-shadow:0 14px 38px rgba(18,35,45,.14);text-decoration:none;box-sizing:border-box}
.static-article-ad>span{display:block;padding:7px 9px 6px;color:#747f85;background:#f5f7f8;border-bottom:1px solid #e1e6e8;font-size:9px;font-weight:900;letter-spacing:.12em;text-align:center}
.static-article-ad img{display:block!important;width:298px!important;height:auto!important;aspect-ratio:1/2;object-fit:contain!important;object-position:center;background:#fff;border:0;margin:0;padding:0}
@media(max-width:1180px) and (min-width:981px){
  main.article-shell.wrap{max-width:1100px!important;grid-template-columns:minmax(0,1fr) 260px!important;gap:28px!important}
  main.article-shell>aside.sticky,.static-article-ads{width:260px!important;min-width:260px!important;max-width:260px!important}
  .static-article-ad{width:260px!important}
  .static-article-ad img{width:258px!important}
}
@media(max-width:980px){main.article-shell.wrap{grid-template-columns:1fr!important}.static-article-ads{display:none!important}}
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
