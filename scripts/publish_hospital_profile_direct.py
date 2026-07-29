#!/usr/bin/env python3
from pathlib import Path
import re
from html import escape

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.github/drafts/nemocnice-kadan-profil-sluzby-budoucnost.html'
ARTICLE = ROOT / 'clanky/nemocnice-kadan-profil-sluzby-budoucnost.html'
URL = '/clanky/nemocnice-kadan-profil-sluzby-budoucnost.html'
ABS = 'https://nasekadan.cz' + URL
TITLE = 'Nemocnice Kadaň není jen spor o miliony. Co všechno zajišťuje pro region'
DESC = 'Závěrečný díl série představuje nemocnici jako celek: služby, 254 lůžek, téměř 480 úvazků, výkony, regionální význam a otázky budoucnosti.'
PUBLISHED = '2026-07-29T05:00:00+02:00'

text = DRAFT.read_text(encoding='utf-8')
text = text.replace('noindex,nofollow', 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1')
text = text.replace('../../', '../').replace('PŘIPRAVOVANÝ ZÁVĚREČNÝ DÍL', '29. ČERVENCE 2026')
text = re.sub(r'<div class="sidebox preview-note">.*?</div>', '', text, count=1, flags=re.S)
if 'data-next-syringe-article' not in text:
    teaser = '''<section class="callout" data-next-syringe-article><strong>Příště: stříkačky ve vchodech a podezřelé byty</strong><p>Ve čtvrtek 31. července v 5:00 zveřejníme článek o odhozených injekčních stříkačkách, podnětech obyvatel na podezřelé byty a o tom, co může Kadaň dělat kromě samotného sběru jehel.</p></section>'''
    text = text.replace('<div class="source-list">', teaser + '\n<div class="source-list">', 1)
if 'article:published_time' not in text:
    text = text.replace('</head>', f'<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">\n</head>', 1)
if '"datePublished"' not in text:
    text = text.replace('"isAccessibleForFree":true}', f'"isAccessibleForFree":true,"datePublished":"{PUBLISHED}","dateModified":"{PUBLISHED}"}}', 1)
ARTICLE.write_text(text, encoding='utf-8', newline='\n')

home_card = f'''<article class="article-card hospital" data-hospital-profile-card><div class="visual" style="background:linear-gradient(135deg,#10242e,#22606b 55%,#9d222a)"><strong>Nemocnice jako celek</strong></div><div class="article-body"><span class="meta">29. 7. 2026 · 5:00 · Zdravotnictví a region</span><h3>{TITLE}</h3><p>254 lůžek, téměř 480 úvazků a více než 114 tisíc ambulantních vyšetření. Co nemocnice zajišťuje a co rozhodne o její budoucnosti.</p><a class="read-more" href="{URL}">Přečíst závěrečný díl →</a></div></article>\n'''

index = ROOT / 'index.html'
it = index.read_text(encoding='utf-8')
if URL not in it:
    marker = '<div class="article-list">'
    it = it.replace(marker, marker + '\n' + home_card, 1)
index.write_text(it, encoding='utf-8', newline='\n')

archive = ROOT / 'clanky/index.html'
at = archive.read_text(encoding='utf-8')
if URL not in at:
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    at = at.replace(marker, marker + '\n' + home_card, 1)
archive.write_text(at, encoding='utf-8', newline='\n')

rss = ROOT / 'rss.xml'
rt = rss.read_text(encoding='utf-8')
if ABS not in rt:
    item = f'''<item><title>{escape(TITLE)}</title><link>{ABS}</link><guid>{ABS}</guid><pubDate>Wed, 29 Jul 2026 03:00:00 GMT</pubDate><description>{escape(DESC)}</description></item>\n'''
    rt = rt.replace('<item>', item + '<item>', 1) if '<item>' in rt else rt.replace('</channel>', item + '</channel>', 1)
rss.write_text(rt, encoding='utf-8', newline='\n')

sitemap = ROOT / 'sitemap.xml'
st = sitemap.read_text(encoding='utf-8')
if ABS not in st:
    st = st.replace('</urlset>', f'<url><loc>{ABS}</loc><lastmod>2026-07-29</lastmod></url>\n</urlset>', 1)
sitemap.write_text(st, encoding='utf-8', newline='\n')

news = ROOT / 'news-sitemap.xml'
if news.exists():
    nt = news.read_text(encoding='utf-8')
    if ABS not in nt:
        entry = f'<url><loc>{ABS}</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>{PUBLISHED}</news:publication_date><news:title>{escape(TITLE)}</news:title></news:news></url>\n'
        nt = nt.replace('</urlset>', entry + '</urlset>', 1)
    news.write_text(nt, encoding='utf-8', newline='\n')

llms = ROOT / 'llms.txt'
if llms.exists():
    lt = llms.read_text(encoding='utf-8')
    if ABS not in lt:
        lt += f'\n- {TITLE}: {ABS}\n'
    llms.write_text(lt, encoding='utf-8', newline='\n')

for path in [ARTICLE, index, archive, rss, sitemap]:
    body = path.read_text(encoding='utf-8')
    if path == ARTICLE:
        assert TITLE in body and 'data-next-syringe-article' in body
    else:
        assert 'nemocnice-kadan-profil-sluzby-budoucnost.html' in body
print('Přímé vydání profilu nemocnice je připravené.')
