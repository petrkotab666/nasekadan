from pathlib import Path
import re

ARTICLE_PATH = Path('clanky/nemocnice-kadan-software-kyberbezpecnost.html')
DRAFT_PATH = Path('.github/drafts/nemocnice-kadan-software-kyberbezpecnost.html')
ARTICLE_URL = '/clanky/nemocnice-kadan-software-kyberbezpecnost.html'
ABSOLUTE_URL = 'https://nasekadan.cz' + ARTICLE_URL


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8', newline='\n')


if not ARTICLE_PATH.exists():
    if not DRAFT_PATH.is_file():
        raise SystemExit('Chybí připravený draft článku.')
    write(ARTICLE_PATH, DRAFT_PATH.read_text(encoding='utf-8'))

# Pondělní upoutávka dole nad zdroji.
text = ARTICLE_PATH.read_text(encoding='utf-8')
monday = '''
  <section id="pondelni-clanek" style="margin:44px 0 24px;padding:28px;border-radius:20px;background:linear-gradient(135deg,#14232d,#355d70 62%,#9f2626);color:#fff;box-shadow:0 18px 45px rgba(20,35,45,.20)">
    <p style="margin:0 0 8px;color:#ffd9d9;font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase">PONDĚLÍ V 5:00 · NAVAZUJÍCÍ ANALÝZA</p>
    <h2 style="margin:0 0 12px;color:#fff;font:800 32px/1.15 Georgia,serif">Kdo nastavil nákupy léčiv od AVIES? Nemocnice za sedm let zaplatila téměř 170 milionů</h2>
    <p style="margin:0 0 16px;color:#edf3f5;font-size:18px">Zmapovali jsme dlouhodobý vztah nemocnice s AVIES, jednotlivá vedení, konsignační sklad i chybějící veřejně dohledatelný dokument pro dodávky v roce 2024.</p>
    <span data-avies-teaser-state="scheduled" style="display:inline-block;padding:10px 14px;border:1px solid rgba(255,255,255,.4);border-radius:999px;color:#fff;font-weight:900">Vyjde v pondělí 27. 7. v 5:00</span>
  </section>
'''
if 'id="pondelni-clanek"' not in text:
    marker = '  <div class="source-list">'
    if marker not in text:
        raise SystemExit('Nový článek nemá blok zdrojů.')
    text = text.replace(marker, monday + marker, 1)
write(ARTICLE_PATH, text)

# Aktivní odkaz ze včerejšího článku.
petice = Path('clanky/petice-nemocnice-kadan.html')
p = petice.read_text(encoding='utf-8')
active_teaser = '''
  <section id="nedelni-clanek" style="margin:44px 0 24px;padding:28px;border-radius:20px;background:linear-gradient(135deg,#14232d,#355d70 62%,#9f2626);color:#fff;box-shadow:0 18px 45px rgba(20,35,45,.20)">
    <p style="margin:0 0 8px;color:#ffd9d9;font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase">NOVĚ ZVEŘEJNĚNÁ NAVAZUJÍCÍ ANALÝZA</p>
    <h2 style="margin:0 0 12px;color:#fff;font:800 32px/1.15 Georgia,serif">64,7 milionu za software: Nemocnice Kadaň ukázala jen část skládačky</h2>
    <p style="margin:0 0 16px;color:#edf3f5;font-size:18px">Rozebíráme, co se skrývá pod účetní položkou software, proč kybernetická bezpečnost nebyla dobrovolný luxus a proč zákonná povinnost sama nevysvětluje rozsah ani cenu investic.</p>
    <a href="/clanky/nemocnice-kadan-software-kyberbezpecnost.html" style="display:inline-flex;padding:13px 18px;border-radius:10px;background:#fff;color:#8f2027;font-weight:900;text-decoration:none">Přečíst navazující analýzu →</a>
  </section>
'''
pattern = r'\s*<section[^>]+id="nedelni-clanek".*?</section>\s*'
if re.search(pattern, p, flags=re.S):
    p = re.sub(pattern, '\n' + active_teaser + '\n', p, count=1, flags=re.S)
else:
    marker = '<div class="source-list">'
    if marker not in p:
        raise SystemExit('Včerejší článek nemá blok zdrojů.')
    p = p.replace(marker, active_teaser + marker, 1)
write(petice, p)

# Titulní stránka.
index = Path('index.html')
h = index.read_text(encoding='utf-8')
hero = '''<article class="lead">
        <div class="photo" style="background:linear-gradient(135deg,#14232d,#345b70 58%,#b72c2c)"><span>NEJNOVĚJŠÍ ANALÝZA</span><strong>64,7 MILIONU</strong></div>
        <div class="copy">
          <small>ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · 26. 7. 2026 V 5:00</small>
          <h1>64,7 milionu za software: Nemocnice Kadaň ukázala jen část skládačky</h1>
          <p>Prověřili jsme kybernetické projekty, smlouvy se STAPRO, zákonné povinnosti i otázky, které konečný účet stále nevysvětluje.</p>
          <a class="btn" href="/clanky/nemocnice-kadan-software-kyberbezpecnost.html">Přečíst novou analýzu →</a>
        </div>
      </article>'''
h, n = re.subn(r'<article class="lead">.*?</article>', hero, h, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Nepodařilo se nahradit hlavní článek na titulní stránce.')
aside = '''<aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">25. 7. 2026 v 20:42</p>
      <h2>Interní ambulance Nemocnice Kadaň bude tři týdny uzavřená</h2>
      <p>Omezení začne v pondělí 27. července a potrvá do 14. srpna. Nemocnice zároveň na týden uzavře pokladnu.</p>
      <a class="aside-button" href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      <div class="aside-links">
        <a href="/clanky/petice-nemocnice-kadan.html">Petice, 100 milionů a údajný prodej nemocnice</a>
        <a href="/clanky/nemocnice-kadan.html">První analýza Nemocnice Kadaň</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>'''
h, n = re.subn(r'<aside class="current-aside">.*?</aside>', aside, h, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Nepodařilo se nahradit pravý panel titulní stránky.')
card = '''
      <article class="article-card hospital" data-software-card>
        <div class="visual"><strong>64,7 milionu za software</strong></div>
        <div class="article-body">
          <span class="meta">26. 7. 2026 · 5:00 · Zdravotnictví a veřejné peníze</span>
          <h3>Nemocnice Kadaň ukázala jen část skládačky</h3>
          <p>Co nemocnice skutečně pořizovala, proč kybernetická ochrana nebyla dobrovolný luxus a které části konečného účtu stále chybějí.</p>
          <a class="read-more" href="/clanky/nemocnice-kadan-software-kyberbezpecnost.html">Přečíst novou analýzu →</a>
        </div>
      </article>
'''
if 'data-software-card' not in h:
    h = h.replace('    <div class="article-list">', '    <div class="article-list">' + card, 1)
write(index, h)

# Archiv.
archive = Path('clanky/index.html')
a = archive.read_text(encoding='utf-8')
archive_item = '''
    <article class="archive-item hospital" data-software-card>
      <div class="archive-visual"><strong>64,7 milionu za software</strong></div>
      <div class="archive-body">
        <span class="archive-meta">26. července 2026 v 5:00 · Zdravotnictví a veřejné peníze</span>
        <h2>64,7 milionu za software: Nemocnice Kadaň ukázala jen část skládačky</h2>
        <p>Analýza kybernetických projektů, smluv se STAPRO, zákonných povinností a veřejně nevysvětlených částí konečného účtu.</p>
        <a href="/clanky/nemocnice-kadan-software-kyberbezpecnost.html">Přečíst novou analýzu →</a>
      </div>
    </article>
'''
if 'data-software-card' not in a:
    a = a.replace('  <section class="archive-list" aria-label="Chronologický přehled článků">', '  <section class="archive-list" aria-label="Chronologický přehled článků">' + archive_item, 1)
write(archive, a)

# RSS.
rss = Path('rss.xml')
r = rss.read_text(encoding='utf-8')
r = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', '<lastBuildDate>Sun, 26 Jul 2026 05:00:00 +0200</lastBuildDate>', r, count=1)
item = '''
    <item>
      <title>64,7 milionu za software: Nemocnice Kadaň ukázala jen část skládačky</title>
      <description><![CDATA[Co nemocnice skutečně pořizovala, proč kybernetická ochrana nebyla dobrovolný luxus a které části konečného účtu stále chybějí.]]></description>
      <link>https://nasekadan.cz/clanky/nemocnice-kadan-software-kyberbezpecnost.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/nemocnice-kadan-software-kyberbezpecnost.html</guid>
      <pubDate>Sun, 26 Jul 2026 05:00:00 +0200</pubDate>
      <category>Zdravotnictví</category>
      <category>Veřejné peníze</category>
      <category>Kybernetická bezpečnost</category>
      <category>Nemocnice Kadaň</category>
      <szn:image><szn:url>https://nasekadan.cz/social-card.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>
'''
if ABSOLUTE_URL not in r:
    anchor = '    <atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    r = r.replace(anchor, anchor + '\n' + item, 1)
write(rss, r)

# Sitemap.
sitemap = Path('sitemap.xml')
s = sitemap.read_text(encoding='utf-8')
s = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', r'\g<1>2026-07-26', s)
s = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', r'\g<1>2026-07-26', s)
entry = '  <url><loc>https://nasekadan.cz/clanky/nemocnice-kadan-software-kyberbezpecnost.html</loc><lastmod>2026-07-26</lastmod></url>\n'
if ABSOLUTE_URL not in s:
    needle = '  <url><loc>https://nasekadan.cz/clanky/</loc><lastmod>2026-07-26</lastmod></url>\n'
    s = s.replace(needle, needle + entry, 1)
write(sitemap, s)

checks = {
    ARTICLE_PATH: ['64,7 milionu za software', 'id="pondelni-clanek"'],
    petice: [ARTICLE_URL, 'NOVĚ ZVEŘEJNĚNÁ NAVAZUJÍCÍ ANALÝZA'],
    index: [ARTICLE_URL, 'data-software-card', 'NEJNOVĚJŠÍ ANALÝZA'],
    archive: [ARTICLE_URL, 'data-software-card'],
    rss: [ABSOLUTE_URL, 'Sun, 26 Jul 2026 05:00:00 +0200'],
    sitemap: [ABSOLUTE_URL, '2026-07-26'],
}
for path, needles in checks.items():
    data = path.read_text(encoding='utf-8')
    for needle in needles:
        if needle not in data:
            raise SystemExit(f'Kontrola selhala: {needle} v {path}')

print('Publikační soubory byly připraveny a zkontrolovány.')
