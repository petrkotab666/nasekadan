#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.github/drafts/kulturni-zarizeni-kadan.html'
ARTICLE = ROOT / 'clanky/kulturni-zarizeni-kadan.html'
SOCIAL = ROOT / 'social/kulturni-zarizeni-kadan-20260802.png'
URL = 'https://nasekadan.cz/clanky/kulturni-zarizeni-kadan.html'
REL = '/clanky/kulturni-zarizeni-kadan.html'
TITLE = 'Od Střelnice po klášter. Co všechno pro Kadaň zajišťuje KZK'
DESC = 'KZK zastřešuje kulturní domy, knihovnu, muzeum, galerii, památky, Konírnu, turistické služby i největší městskou slavnost.'
IMAGE_URL = 'https://nasekadan.cz/social/kulturni-zarizeni-kadan-20260802.png'
PUBLISHED = '2026-08-02T04:00:00+02:00'
RSS_DATE = 'Sun, 02 Aug 2026 04:00:00 +0200'
DATE_ISO = '2026-08-02'


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def add_head_meta(text: str) -> str:
    text = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">', text, count=1)
    text = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{URL}">', text, count=1)
    text = re.sub(r'<meta property="og:title"[^>]*>', f'<meta property="og:title" content="{TITLE}">', text, count=1)
    text = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{DESC}">', text, count=1)
    extras = f'''
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:url" content="{URL}">
  <meta property="og:image" content="{IMAGE_URL}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE}">
  <meta name="twitter:description" content="{DESC}">
  <meta name="twitter:image" content="{IMAGE_URL}">
  <meta property="article:published_time" content="{PUBLISHED}">
  <meta property="article:modified_time" content="{PUBLISHED}">
  <link rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml">
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
  <meta name="theme-color" content="#9f2626">
  <script type="application/ld+json">{json.dumps({
      '@context':'https://schema.org','@type':'NewsArticle','headline':TITLE,'description':DESC,
      'datePublished':PUBLISHED,'dateModified':PUBLISHED,
      'author':{'@type':'Organization','@id':'https://nasekadan.cz/#organization','name':'Naše Kadaň','url':'https://nasekadan.cz/o-webu/'},
      'publisher':{'@id':'https://nasekadan.cz/#organization'},
      'mainEntityOfPage':{'@type':'WebPage','@id':URL},'image':[IMAGE_URL],
      'inLanguage':'cs-CZ','isAccessibleForFree':True
  }, ensure_ascii=False)}</script>
'''
    text = text.replace('</head>', extras + '</head>', 1)
    return text


def build_article() -> str:
    text = DRAFT.read_text(encoding='utf-8')
    text = add_head_meta(text)
    text = re.sub(r'\s*<div class="preview-note">.*?</div>', '', text, flags=re.S)
    text = re.sub(r'\s*<div class="sidebox editor-box">.*?</div>', '', text, count=1, flags=re.S)
    text = text.replace('KULTURA · VOLNÝ ČAS · PŘIPRAVOVANÝ ČLÁNEK', 'KULTURA · VOLNÝ ČAS · NEDĚLNÍ ČTENÍ · 2. SRPNA 2026 V 04:00')
    text = re.sub(r'<main class="wrap article-shell"(?:[^>]*)>', '<main class="wrap article-shell" data-article-template="unified-v1">', text, count=1)
    text = text.replace('<header><div class="wrap head"><a class="logo" href="/"><span class="logo-mark"></span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="/">Úvod</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></nav></div></header>', '<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>')

    konirna = '''
    <h2 id="konirna">Konírna: sezonní zastávka ve františkánských zahradách</h2>
    <div class="place-card"><div class="place-icon">☕</div><div><h3>Konírna u františkánského kláštera</h3><p>Sezonní občerstvení provozované KZK nabízí návštěvníkům pití, drobné jídlo a místo k odpočinku. Zároveň tvoří zázemí venkovního kulturního programu.</p></div></div>
    <p>Konírna ukazuje, že práce KZK nekončí u sálů, knihovny a prohlídkových tras. V teplejší části roku doplňuje návštěvu kláštera a zahrad o možnost posedět, občerstvit se a strávit v areálu více času.</p>
    <p>Prostor u Konírny slouží také jako orientační bod pro kulturní program ve františkánských zahradách. U venkovního pódia se konají koncerty a další menší akce využívající klidnější atmosféru zahrad.</p>
'''
    if 'id="konirna"' not in text:
        text = text.replace('    <h2 id="turistika">', konirna + '\n    <h2 id="turistika">', 1)
    text = text.replace('<li><a href="#turistika">Infocentrum a turistika</a></li>', '<li><a href="#konirna">Konírna</a></li><li><a href="#turistika">Infocentrum a turistika</a></li>', 1)
    text = text.replace('<li>Turistické informační centrum</li><li>Venkovní kulturní místa</li>', '<li>Turistické informační centrum</li><li>Konírnu</li><li>Venkovní kulturní místa</li>', 1)

    if 'Kadaňský pohádkový festival není akcí KZK' not in text:
        raise SystemExit('V návrhu chybí oprava pořadatele Kadaňského pohádkového festivalu.')
    if 'Císařský den je největší kadaňská kulturní akce' not in text:
        raise SystemExit('V návrhu chybí pasáž o Císařském dni.')

    aside = re.search(r'(<aside\b[^>]*class="sticky"[^>]*>)(.*?)(</aside>)', text, re.S)
    if not aside:
        raise SystemExit('Článek nemá přímý pravý sloupec.')
    body = aside.group(2)
    body = re.sub(r'\s*<div data-promos[^>]*>.*?</div>', '', body, flags=re.S)
    body = body.rstrip() + '\n    <div data-promos data-context="sidebar"></div>\n  '
    text = text[:aside.start()] + aside.group(1) + body + aside.group(3) + text[aside.end():]

    footer = '''<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div><strong>Naše Kadaň</strong><p>Místní zprávy, souvislosti a praktické informace z Kadaně a okolí.</p></div><div><strong>Obsah</strong><a href="/clanky/">Články</a><a href="/pruvodce/">Průvodce</a><a href="/#akce">Akce</a></div><div><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>'''
    text = re.sub(r'<footer>.*?</footer>', footer, text, count=1, flags=re.S)
    text = re.sub(r'\s*<script[^>]+src="/(?:site|reklamy|ad-spacing-guard|reklamy-oprava-obrazku|obsah-doplnky)[^"]*"[^>]*></script>', '', text)
    scripts = '''
<script src="/analytics.js" defer></script>
<script src="/site.js" defer></script>
<script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script>
<script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script>
<script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script>
<script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script>
'''
    text = text.replace('</body>', scripts + '</body>', 1)
    return text


def social_image() -> None:
    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), (18, 39, 49))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=(int(18*(1-t)+92*t), 39, int(49*(1-t)+48*t)))
    draw.rectangle([0, 0, 18, H], fill=(169, 35, 43))
    draw.rectangle([0, H-18, W, H], fill=(201, 164, 90))
    draw.ellipse([880, -120, 1320, 320], fill=(169, 35, 43))
    draw.ellipse([970, 320, 1250, 600], fill=(201, 164, 90))
    bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    regular = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    draw.text((58, 48), 'NAŠE KADAŇ', font=ImageFont.truetype(bold, 38), fill='white')
    draw.rounded_rectangle([58, 120, 300, 166], radius=18, fill=(169, 35, 43))
    draw.text((78, 128), 'NEDĚLNÍ ČTENÍ', font=ImageFont.truetype(bold, 24), fill='white')
    y = 200
    for line in textwrap.wrap('Od Střelnice po klášter', width=25):
        draw.text((58, y), line, font=ImageFont.truetype(bold, 62), fill='white'); y += 72
    for line in textwrap.wrap('Co všechno pro Kadaň zajišťuje KZK', width=40):
        draw.text((60, y+8), line, font=ImageFont.truetype(regular, 28), fill=(232,239,242)); y += 40
    draw.rounded_rectangle([58, 520, 790, 585], radius=22, fill='white')
    draw.text((82, 537), 'Střelnice • Orfeum • Konírna • Císařský den', font=ImageFont.truetype(bold, 22), fill=(19,35,45))
    draw.text((900, 168), 'KZK', font=ImageFont.truetype(bold, 90), fill='white')
    for pos, label in [(290,'KULTURA'),(350,'PAMÁTKY'),(410,'SLAVNOSTI')]:
        draw.text((900, pos), label, font=ImageFont.truetype(bold, 34), fill='white')
    img.save(SOCIAL, optimize=True)


def update_home() -> None:
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')
    hero = '''<article class="lead">
        <div class="photo" style="background:radial-gradient(circle at 78% 18%,rgba(255,255,255,.17),transparent 27%),linear-gradient(135deg,#152b37,#426777 58%,#a9232b)"><span>NEDĚLNÍ ČTENÍ</span><strong>KZK</strong></div>
        <div class="copy">
          <small>KULTURA · VOLNÝ ČAS · 2. 8. 2026 V 04:00</small>
          <h1>Od Střelnice po klášter. Co všechno pro Kadaň zajišťuje KZK</h1>
          <p>Kulturní domy, knihovna, galerie, památky, Konírna i největší městská slavnost pod jednou organizací.</p>
          <a class="btn" href="/clanky/kulturni-zarizeni-kadan.html">Přečíst článek →</a>
        </div>
      </article>'''
    text, count = re.subn(r'<article class="lead">.*?</article>', hero, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('Nepodařilo se vyměnit hlavní článek.')
    text = re.sub(r'data-latest-article-href="[^"]+"', f'data-latest-article-href="{REL}"', text, count=1)
    aside = '''<aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p><p class="aside-date">1. 8. 2026 v 12:19</p>
      <h2>Petice za nemocnici míří do ulic. Podepisovat se bude na třech místech</h2>
      <p>Podpisová místa, elektronická petice a přehled změn vedení i neuzavřených sporů.</p>
      <a class="aside-button" href="/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div>
    </aside>'''
    text = re.sub(r'<aside class="current-aside">.*?</aside>', aside, text, count=1, flags=re.S)
    write(path, text)


def update_archive() -> None:
    path = ROOT / 'clanky/index.html'
    text = path.read_text(encoding='utf-8')
    match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)
    if match:
        data = json.loads(match.group(1)); graph = data.get('@graph', [])
        itemlist = next((x for x in graph if x.get('@type') == 'ItemList'), None)
        if itemlist:
            existing = [x for x in itemlist.get('itemListElement', []) if x.get('url') != URL]
            elements = [{'@type':'ListItem','position':1,'url':URL,'name':TITLE}]
            for pos, item in enumerate(existing, 2): item['position'] = pos; elements.append(item)
            itemlist['itemListElement'] = elements; itemlist['numberOfItems'] = len(elements)
            replacement = '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n  </script>'
            text = text[:match.start()] + replacement + text[match.end():]
    text = re.sub(r'\s*<article\b[^>]*data-auto-article="kulturni-zarizeni-kadan"[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
    item = '''
    <article class="article-card service" data-auto-article="kulturni-zarizeni-kadan">
      <div class="visual" style="background:linear-gradient(135deg,#152b37,#426777 58%,#a9232b)"><strong>Od Střelnice po klášter. Co všechno pro Kadaň zajišťuje KZK</strong></div>
      <div class="article-body"><span class="meta">2. 8. 2026 · 04:00 · Kultura · Volný čas</span><h3>Od Střelnice po klášter. Co všechno pro Kadaň zajišťuje KZK</h3><p>Kulturní domy, knihovna, galerie, památky, Konírna i Císařský den.</p><a class="read-more" href="/clanky/kulturni-zarizeni-kadan.html">Přečíst článek →</a></div>
    </article>
'''
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if marker not in text: raise SystemExit('Archiv nemá seznam článků.')
    text = text.replace(marker, marker + item, 1)
    write(path, text)


def update_feeds() -> None:
    path = ROOT / 'rss.xml'; text = path.read_text(encoding='utf-8')
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{RSS_DATE}</lastBuildDate>', text, count=1)
    if URL not in text:
        item = f'''    <item><title>{TITLE}</title><description><![CDATA[{DESC}]]></description><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{RSS_DATE}</pubDate><category>Kultura</category><category>Kadaň</category><szn:image><szn:url>{IMAGE_URL}</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>\n\n'''
        text = text.replace('    <item>', item + '    <item>', 1)
    write(path, text)
    path = ROOT / 'sitemap.xml'; text = path.read_text(encoding='utf-8')
    text = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', rf'\g<1>{DATE_ISO}', text, count=1)
    text = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', rf'\g<1>{DATE_ISO}', text, count=1)
    if URL not in text: text = text.replace('</urlset>', f'  <url><loc>{URL}</loc><lastmod>{DATE_ISO}</lastmod></url>\n</urlset>')
    write(path, text)
    path = ROOT / 'news-sitemap.xml'
    if path.exists():
        text = path.read_text(encoding='utf-8')
        if URL not in text:
            entry = f'''  <url><loc>{URL}</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>{PUBLISHED}</news:publication_date><news:title>{TITLE}</news:title></news:news></url>\n'''
            text = text.replace('</urlset>', entry + '</urlset>')
            write(path, text)


def validate() -> None:
    article = ARTICLE.read_text(encoding='utf-8')
    required = [TITLE, 'id="konirna"', 'Císařský den je největší kadaňská kulturní akce', 'Kadaňský pohádkový festival není akcí KZK', 'data-promos data-context="sidebar"', '/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3']
    missing = [x for x in required if x not in article]
    if missing: raise SystemExit(f'Článek postrádá: {missing}')
    for rel in ('index.html','clanky/index.html','rss.xml','sitemap.xml','news-sitemap.xml'):
        p = ROOT / rel
        if p.exists() and REL not in p.read_text(encoding='utf-8') and URL not in p.read_text(encoding='utf-8'):
            raise SystemExit(f'{rel} neobsahuje článek.')
    if not SOCIAL.is_file() or SOCIAL.stat().st_size < 10000:
        raise SystemExit('Sociální obrázek nebyl vytvořen.')


def main() -> None:
    write(ARTICLE, build_article())
    social_image(); update_home(); update_archive(); update_feeds()
    # Po aktualizaci hero teprve srovnat pořadí chráněných karet.
    import subprocess
    subprocess.run(['python3', str(ROOT / 'scripts/ensure_recent_home_articles_20260801.py')], check=True, cwd=ROOT)
    validate()
    print('KZK článek připraven k veřejnému nasazení.')


if __name__ == '__main__':
    main()
