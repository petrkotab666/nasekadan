from pathlib import Path
import json
import re

SLUG = "kadan-tropicke-dny-koupaliste-cervenec-2026"
ARTICLE_URL = f"/clanky/{SLUG}.html"
ABS_URL = "https://nasekadan.cz" + ARTICLE_URL
PUB_RFC = "Tue, 28 Jul 2026 17:45:00 +0200"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def write(path, text):
    Path(path).write_text(text, encoding="utf-8", newline="\n")


path = Path("index.html")
h = read(path)
hero = '''<article class="lead" data-heat-article-hero>
      <div class="photo" style="background:linear-gradient(rgba(14,34,45,.18),rgba(14,34,45,.58)),url('/obrazky/koupaliste-kadan-budova-2026.jpg') center/cover no-repeat"><span>POČASÍ · PRAKTICKÁ KADAŇ</span><strong>AŽ 35 °C</strong></div>
      <div class="copy">
        <small>KADAŇ · 28. 07. 2026 · 17:45</small>
        <h1>Kadaň čekají tropické dny. Ve čtvrtek může být až 35 stupňů</h1>
        <p>Kde se zchladit, jak bude otevřené koupaliště a proč může být nová skluzavka během největšího horka dočasně uzavřena.</p>
        <a class="btn" href="/clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html">Přečíst praktický přehled →</a>
      </div>
    </article>'''
h, n = re.subn(r'<article class="lead"[^>]*>.*?</article>', hero, h, count=1, flags=re.S)
if n != 1:
    raise SystemExit("Nepodařilo se nahradit hlavní článek na titulní stránce.")

aside = '''<aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">28. 7. 2026 v 11:30</p>
      <h2>Odstávky elektřiny omezí provoz restaurace v Autokempu Prunéřov</h2>
      <p>Ve dvou termínech otevře restaurace až po 18. hodině, potřetí po 16. hodině. Recepce zůstane otevřená.</p>
      <a class="aside-button" href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst praktické informace →</a>
      <div class="aside-links">
        <a href="/clanky/arc-med-nemocnice-kadan.html">ARC-MED za 16 milionů</a>
        <a href="/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html">Výcvik hasičů na Nechranicích</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>'''
h, n = re.subn(r'<aside class="current-aside">.*?</aside>', aside, h, count=1, flags=re.S)
if n != 1:
    raise SystemExit("Nepodařilo se nahradit pravý panel titulní stránky.")

card = '''
<article class="article-card service" data-heat-article-card>
  <div class="visual" style="background:linear-gradient(rgba(19,48,68,.15),rgba(169,35,43,.62)),url('/obrazky/koupaliste-kadan-budova-2026.jpg') center/cover no-repeat"><strong>Tropické dny v Kadani</strong></div>
  <div class="article-body"><span class="meta">28. 7. 2026 · 17:45 · Počasí a praktické informace</span><h3>Ve čtvrtek může být až 35 stupňů</h3><p>Otevírací doba koupaliště, upozornění na novou skluzavku a tipy, kde se zchladit.</p><a class="read-more" href="/clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html">Přečíst článek →</a></div>
</article>
'''
if 'data-heat-article-card' not in h:
    h = h.replace('    <div class="article-list">', '    <div class="article-list">' + card, 1)
write(path, h)

path = Path("clanky/index.html")
a = read(path)
archive_item = '''
<article class="archive-item service" data-heat-article-card>
  <div class="archive-visual" style="background:linear-gradient(rgba(19,48,68,.15),rgba(169,35,43,.62)),url('/obrazky/koupaliste-kadan-budova-2026.jpg') center/cover no-repeat"><strong>Tropické dny v Kadani</strong></div>
  <div class="archive-body"><span class="archive-meta">28. července 2026 v 17:45 · Počasí a praktické informace</span><h2>Kadaň čekají tropické dny. Ve čtvrtek může být až 35 stupňů</h2><p>Otevírací doba koupaliště, upozornění na novou skluzavku a přehled míst, kde se během vedra zchladit.</p><a href="/clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html">Přečíst článek →</a></div>
</article>
'''
if 'data-heat-article-card' not in a:
    a = a.replace('  <section class="archive-list" aria-label="Chronologický přehled článků">', '  <section class="archive-list" aria-label="Chronologický přehled článků">' + archive_item, 1)

scripts = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', a, flags=re.S))
updated = False
for m in scripts:
    raw = m.group(1)
    if '"@type": "CollectionPage"' not in raw:
        continue
    data = json.loads(raw)
    graph = data.get('@graph', [])
    itemlist = next((x for x in graph if x.get('@type') == 'ItemList'), None)
    if itemlist is None:
        continue
    items = [x for x in itemlist.get('itemListElement', []) if x.get('url') != ABS_URL]
    items.insert(0, {'@type': 'ListItem', 'position': 1, 'url': ABS_URL, 'name': 'Kadaň čekají tropické dny. Ve čtvrtek může být až 35 stupňů'})
    for pos, item in enumerate(items, 1):
        item['position'] = pos
    itemlist['itemListElement'] = items
    itemlist['numberOfItems'] = len(items)
    replacement = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + '</script>'
    a = a[:m.start()] + replacement + a[m.end():]
    updated = True
    break
if not updated:
    raise SystemExit("Nepodařilo se aktualizovat JSON-LD archivu.")
write(path, a)

path = Path("rss.xml")
r = read(path)
r = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{PUB_RFC}</lastBuildDate>', r, count=1)
item = '''
    <item>
      <title>Kadaň čekají tropické dny. Ve čtvrtek může být až 35 stupňů</title>
      <description><![CDATA[Otevírací doba koupaliště, upozornění na novou skluzavku a přehled míst, kde se během vedra zchladit.]]></description>
      <link>https://nasekadan.cz/clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html</guid>
      <pubDate>Tue, 28 Jul 2026 17:45:00 +0200</pubDate>
      <category>Počasí</category><category>Praktická Kadaň</category><category>Koupaliště Kadaň</category>
      <szn:image><szn:url>https://nasekadan.cz/social-card.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>
    </item>
'''
if ABS_URL not in r:
    anchor = '    <atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if anchor not in r:
        raise SystemExit("RSS nemá očekávaný anchor.")
    r = r.replace(anchor, anchor + '\n' + item, 1)
write(path, r)

path = Path("sitemap.xml")
s = read(path)
s = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', r'\g<1>2026-07-28', s)
s = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', r'\g<1>2026-07-28', s)
entry = '  <url><loc>https://nasekadan.cz/clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html</loc><lastmod>2026-07-28</lastmod></url>\n'
if ABS_URL not in s:
    needle_match = re.search(r'  <url><loc>https://nasekadan\.cz/clanky/</loc><lastmod>[^<]+</lastmod></url>\n?', s)
    if not needle_match:
        raise SystemExit("Sitemap nemá očekávaný záznam archivu.")
    s = s[:needle_match.end()] + entry + s[needle_match.end():]
write(path, s)

checks = {
    Path('clanky/kadan-tropicke-dny-koupaliste-cervenec-2026.html'): ['Ve čtvrtek může být až 35 stupňů', 'koupaliste-kadan-budova-2026.jpg', 'Nová skluzavka'],
    Path('index.html'): [ARTICLE_URL, 'data-heat-article-card', 'data-heat-article-hero'],
    Path('clanky/index.html'): [ABS_URL, 'data-heat-article-card', 'numberOfItems'],
    Path('rss.xml'): [ABS_URL, PUB_RFC],
    Path('sitemap.xml'): [ABS_URL, '2026-07-28'],
}
for p, needles in checks.items():
    text = read(p)
    for needle in needles:
        if needle not in text:
            raise SystemExit(f'{p}: chybí {needle}')
print('Článek i všechny indexační vazby jsou připravené.')
