#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
path = root / 'clanky' / 'arc-med-nemocnice-kadan.html'
text = path.read_text(encoding='utf-8')

# Veřejná verze a standardní cesty.
text = text.replace('content="noindex,nofollow"', 'content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"')
text = text.replace('href="../../favicon.svg"', 'href="../favicon.svg"')
text = text.replace('href="../../style.css"', 'href="../style.css"')
text = text.replace('href="../../index.html"', 'href="../index.html"')
text = text.replace('href="../../pruvodce/"', 'href="../pruvodce/"')
text = text.replace('ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · PŘIPRAVOVANÝ ČLÁNEK', 'ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · 28. ČERVENCE 2026')

# Stejná struktura jako u ostatních článků.
text = re.sub(r'<article(?![^>]*class=)>', '<article class="article">', text, count=1)
text = re.sub(r'<article\s+class="(?![^"]*\barticle\b)([^"]*)">', r'<article class="article \1">', text, count=1)

# Odstranit pracovní a dynamické reklamní prvky; statické reklamy vloží společný generátor.
text = re.sub(r'\s*<div class="sidebox"><h3>Pracovní verze</h3>.*?</div>', '', text, count=1, flags=re.S)
text = re.sub(r'\s*<div\s+data-promos[^>]*>.*?</div>', '', text, flags=re.S)
text = re.sub(r'\s*<script[^>]+src="/reklamy(?:-oprava-obrazku)?\.js[^>]*></script>', '', text)
text = re.sub(r'\s*<script[^>]+src="/obsah-doplnky\.js[^>]*></script>', '', text)

# Doplnit datum publikace, pokud chybí.
published = '2026-07-28T05:00:00+02:00'
if 'article:published_time' not in text:
    text = text.replace('</head>', f'<meta property="article:published_time" content="{published}"><meta property="article:modified_time" content="{published}">\n</head>', 1)

# Přepsat společný reklamní blok vždy znovu.
ads = [
    ('https://pojistime.to','/assets/reklamy/pojistime-300x600.svg','Pojistime.to'),
    ('https://vaseuklizecka.cz','/assets/reklamy/vaseuklizecka-300x600.svg','VašeUklízečka.cz'),
    ('https://vyklidime.to','/assets/reklamy/vyklidime-300x600.svg','Vyklidime.to'),
    ('https://realitykadan.cz','/assets/reklamy/realitykadan-300x600.svg','RealityKadan.cz'),
]
block = '<div class="static-article-ads" data-static-ads="locked-v1" aria-label="Reklamy v pravém sloupci článku">' + ''.join(
    f'<a class="static-article-ad" href="{url}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span>REKLAMA</span><img src="{img}" width="300" height="600" alt="{alt}" loading="lazy" decoding="async"></a>'
    for url, img, alt in ads
) + '</div>'
text = re.sub(r'<div class="static-article-ads".*?</div>', '', text, flags=re.S)
text = text.replace('<aside class="sticky">', '<aside class="sticky">' + block, 1)

path.write_text(text, encoding='utf-8', newline='\n')
print('ARC-MED sjednocen se standardní šablonou a reklamním systémem.')
