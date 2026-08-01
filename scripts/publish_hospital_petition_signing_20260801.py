#!/usr/bin/env python3
from pathlib import Path
import json
import re

URL = 'https://nasekadan.cz/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html'
PATH = '/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html'
TITLE = 'Petice za nemocnici míří do ulic. Podepisovat se bude na třech místech'
DESCRIPTION = 'Podpisové archy budou v Kadani dostupné od 3. do 15. srpna. Přinášíme adresy i přehled událostí, které petici předcházely.'
DATE_ISO = '2026-08-01'
RSS_DATE = 'Sat, 01 Aug 2026 12:19:00 +0200'
IMAGE = 'https://nasekadan.cz/social/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas-1a4e355b20.png'


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8', newline='\n')

path = Path('index.html')
text = path.read_text(encoding='utf-8')
hero = '''<article class="lead">
        <div class="photo" style="background:radial-gradient(circle at 78% 18%,rgba(255,255,255,.17),transparent 27%),linear-gradient(135deg,#173746,#315d70 58%,#9f2626)"><span>AKTUÁLNĚ</span><strong>PETICE</strong></div>
        <div class="copy">
          <small>NEMOCNICE KADAŇ · PETICE · 1. 8. 2026 V 12:19</small>
          <h1>Petice za nemocnici míří do ulic. Podepisovat se bude na třech místech</h1>
          <p>Od 3. do 15. srpna budou v Kadani k dispozici podpisové archy. Přinášíme adresy i přehled změn vedení a neuzavřených sporů.</p>
          <a class="btn" href="/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html">Přečíst článek →</a>
        </div>
      </article>'''
text, count = re.subn(r'<article class="lead">.*?</article>', hero, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Nepodařilo se nahradit hlavní článek na titulní straně.')
if 'data-petice-podpisy-card' not in text:
    card = '''
      <article class="article-card hospital" data-petice-podpisy-card>
        <div class="visual" style="background:linear-gradient(135deg,#173746,#9f2626)"><strong>Petice za nemocnici</strong></div>
        <div class="article-body">
          <span class="meta">1. 8. 2026 · 12:19 · Zdravotnictví</span>
          <h3>Petici bude možné podepsat na třech místech</h3>
          <p>Podpisová místa, termín sběru a přehled událostí, které současné iniciativě předcházely.</p>
          <a class="read-more" href="/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html">Přečíst článek →</a>
        </div>
      </article>
'''
    marker = '<div class="article-list">'
    if marker not in text:
        raise SystemExit('Na titulní straně chybí seznam článků.')
    text = text.replace(marker, marker + card, 1)
write(path, text)

path = Path('clanky/index.html')
text = path.read_text(encoding='utf-8')
match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)
if not match:
    raise SystemExit('V archivu chybí JSON-LD.')
data = json.loads(match.group(1))
graph = data.get('@graph', [])
itemlist = next((item for item in graph if item.get('@type') == 'ItemList'), None)
if itemlist is None:
    raise SystemExit('V JSON-LD chybí ItemList.')
existing = [item for item in itemlist.get('itemListElement', []) if item.get('url') != URL]
elements = [{'@type':'ListItem','position':1,'url':URL,'name':TITLE}]
for position, item in enumerate(existing, start=2):
    item['position'] = position
    elements.append(item)
itemlist['itemListElement'] = elements
itemlist['numberOfItems'] = len(elements)
replacement = '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n  </script>'
text = text[:match.start()] + replacement + text[match.end():]
if 'data-petice-podpisy-card' not in text:
    item = '''
    <article class="archive-item hospital" data-petice-podpisy-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#173746,#9f2626)"><strong>Petice za nemocnici</strong></div>
      <div class="archive-body">
        <span class="archive-meta">1. srpna 2026 v 12:19 · Zdravotnictví · Petice</span>
        <h2>Petice za nemocnici míří do ulic. Podepisovat se bude na třech místech</h2>
        <p>Od 3. do 15. srpna budou v Kadani k dispozici podpisové archy. Přinášíme adresy i přehled změn vedení a neuzavřených sporů.</p>
        <a href="/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html">Přečíst článek →</a>
      </div>
    </article>
'''
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if marker not in text:
        raise SystemExit('V archivu chybí seznam článků.')
    text = text.replace(marker, marker + item, 1)
write(path, text)

path = Path('rss.xml')
text = path.read_text(encoding='utf-8')
text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{RSS_DATE}</lastBuildDate>', text, count=1)
if URL not in text:
    item = f'''    <item>
      <title>{TITLE}</title>
      <description><![CDATA[{DESCRIPTION}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{RSS_DATE}</pubDate>
      <category>Nemocnice Kadaň</category>
      <category>Petice</category>
      <category>Zdravotnictví</category>
      <szn:image><szn:url>{IMAGE}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>

'''
    marker = '    <item>'
    if marker not in text:
        raise SystemExit('RSS neobsahuje položku.')
    text = text.replace(marker, item + marker, 1)
write(path, text)

path = Path('sitemap.xml')
text = path.read_text(encoding='utf-8')
text = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', rf'\g<1>{DATE_ISO}', text, count=1)
text = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', rf'\g<1>{DATE_ISO}', text, count=1)
if URL not in text:
    addition = f'  <url><loc>{URL}</loc><lastmod>{DATE_ISO}</lastmod></url>\n'
    pos = text.rfind('</urlset>')
    if pos < 0:
        raise SystemExit('Sitemap nemá uzavírací urlset.')
    text = text[:pos] + addition + text[pos:]
write(path, text)

path = Path('news-sitemap.xml')
if path.exists():
    text = path.read_text(encoding='utf-8')
    if URL not in text:
        entry = f'''  <url>
    <loc>{URL}</loc>
    <news:news>
      <news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication>
      <news:publication_date>2026-08-01T12:19:00+02:00</news:publication_date>
      <news:title>{TITLE}</news:title>
    </news:news>
  </url>
'''
        pos = text.rfind('</urlset>')
        if pos < 0:
            raise SystemExit('News sitemap nemá uzavírací urlset.')
        text = text[:pos] + entry + text[pos:]
        write(path, text)

print('Článek byl zařazen na titulní stranu, do archivu, RSS a sitemap.')
