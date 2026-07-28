#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "odstavky-elektriny-autokemp-prunerov-srpen-2026"
ARTICLE_PATH = ROOT / "clanky" / f"{SLUG}.html"
ARTICLE_URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
ARTICLE_HREF = f"/clanky/{SLUG}.html"
PUBLISHED = "2026-07-28T11:30:00+02:00"
TITLE = "Odstávky elektřiny omezí v srpnu provoz restaurace v Autokempu Prunéřov"
DESC = "Restaurace v Autokempu Prunéřov otevře 3. a 10. srpna až po 18. hodině a 14. srpna po 16. hodině. Recepce zůstane otevřená, kartou ale nepůjde platit."

ARTICLE = '''<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Odstávky elektřiny omezí provoz restaurace v Autokempu Prunéřov | Naše Kadaň</title>
  <meta name="description" content="Restaurace v Autokempu Prunéřov otevře 3. a 10. srpna až po 18. hodině a 14. srpna po 16. hodině. Recepce zůstane otevřená, kartou ale nepůjde platit.">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../style.css">
  <link rel="canonical" href="https://nasekadan.cz/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#a9232b">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="Odstávky elektřiny omezí v srpnu provoz restaurace v Autokempu Prunéřov">
  <meta property="og:description" content="Dvakrát se otevře až po 18. hodině, potřetí po 16. hodině. Recepce zůstane otevřená, platby kartou ale nebudou možné.">
  <meta property="og:url" content="https://nasekadan.cz/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">
  <meta property="og:image" content="https://nasekadan.cz/social-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta property="article:published_time" content="2026-07-28T11:30:00+02:00">
  <meta property="article:modified_time" content="2026-07-28T11:30:00+02:00">
  <style>
    .article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}
    .article h1{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}
    .article h2{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}
    .article p,.article li{font-size:18px}.article .leadtext{font-size:23px;color:#465862;line-height:1.55}
    .article a{color:#9f2626;text-decoration:underline;text-underline-offset:3px}
    .hero-visual{min-height:340px;border-radius:24px;background:radial-gradient(circle at 82% 18%,#ffffff22,transparent 27%),linear-gradient(135deg,#172c37,#6d3030 58%,#ba2027);display:flex;align-items:flex-end;padding:30px;color:#fff;box-shadow:var(--shadow);margin:30px 0;position:relative;overflow:hidden}
    .hero-visual:after{content:'3/8 · 10/8 · 14/8';position:absolute;right:-18px;top:24px;font:900 62px/1 Arial;color:#ffffff12;white-space:nowrap}
    .hero-visual strong{font:800 31px Georgia,serif;max-width:650px;position:relative;z-index:1;text-shadow:0 2px 16px #000}
    .dates{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:30px 0}.dates div{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 8px 25px #16242d0a}.dates b{display:block;color:var(--red);font-size:30px}.dates span{font-size:16px;color:var(--muted)}
    .callout{border-left:6px solid var(--red);background:var(--cream);margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}.callout strong{font:800 24px Georgia,serif;display:block;margin-bottom:6px}
    .source-list{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}.source-list li{font-size:15px;margin-bottom:8px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px}
    @media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}@media(max-width:700px){.dates{grid-template-columns:1fr}.hero-visual{min-height:270px}.hero-visual:after{font-size:38px}.article h1{font-size:42px}.article .leadtext{font-size:20px}}
  </style>
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"Odstávky elektřiny omezí v srpnu provoz restaurace v Autokempu Prunéřov","description":"Restaurace v Autokempu Prunéřov otevře 3. a 10. srpna až po 18. hodině a 14. srpna po 16. hodině. Recepce zůstane otevřená, kartou ale nepůjde platit.","datePublished":"2026-07-28T11:30:00+02:00","dateModified":"2026-07-28T11:30:00+02:00","author":{"@type":"Organization","name":"Naše Kadaň"},"publisher":{"@type":"Organization","name":"Naše Kadaň"},"mainEntityOfPage":"https://nasekadan.cz/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html","inLanguage":"cs-CZ"}</script>
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
</head>
<body>
<header><div class="wrap head"><a class="logo" href="../index.html"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="../index.html">Úvod</a><a href="/clanky/">Články</a><a href="../index.html#akce">Akce</a><a href="../pruvodce/">Průvodce</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1">
<article class="article">
  <p class="tag">PRAKTICKÉ INFORMACE · PRUNÉŘOV · 28. ČERVENCE 2026</p>
  <h1>Odstávky elektřiny omezí v srpnu provoz restaurace v Autokempu Prunéřov</h1>
  <p class="leadtext"><strong>Tři plánované odstávky elektřiny ovlivní v srpnu provoz restaurace v Autokempu Prunéřov. V pondělí 3. srpna a v pondělí 10. srpna otevře až po 18. hodině, v pátek 14. srpna pak po 16. hodině.</strong></p>
  <div class="hero-visual"><strong>Ubytovaní hosté se na recepci dostanou i během odstávek. Platební terminál ale bez elektřiny nebude fungovat, proto bude potřeba hotovost.</strong></div>
  <div class="dates"><div><b>3. srpna</b><span>restaurace otevře po 18:00</span></div><div><b>10. srpna</b><span>restaurace otevře po 18:00</span></div><div><b>14. srpna</b><span>restaurace otevře po 16:00</span></div></div>
  <p>Provozovatel Autokempu Prunéřov zveřejnil upozornění, podle něhož omezení souvisí s plánovanými odstávkami společnosti ČEZ. Restaurace proto v uvedených dnech zůstane do odpoledních nebo podvečerních hodin zavřená.</p>
  <h2>Recepce zůstane otevřená</h2>
  <p>Omezení restaurace neznamená úplné uzavření areálu. Recepce pro ubytované hosty má zůstat otevřená, takže příjezdy, odjezdy a nezbytné záležitosti spojené s ubytováním bude možné řešit i během odstávky.</p>
  <div class="callout"><strong>Kartu nechte jako záložní možnost</strong><p>Během přerušení dodávky elektřiny nebude možné platit kartou. Provozovatel proto návštěvníkům doporučuje připravit si hotovost.</p></div>
  <h2>Omezení se týká restaurace, rozsah odstávky může být širší</h2>
  <p>Z oznámení kempu nelze určit úplný seznam dalších dotčených adres ani přesný čas, kdy ČEZ dodávku elektřiny vypne a znovu obnoví. Jisté je provozní opatření kempu: restaurace otevře v každém ze tří termínů až po uvedené hodině.</p>
  <p>ČEZ Distribuce umožňuje plánované odstávky ověřit podle konkrétní adresy. Autokemp se nachází na adrese Prunéřov 383. Lidé z okolí si proto mohou zkontrolovat, zda se plánované přerušení týká také jejich odběrného místa.</p>
  <h2>Informaci jsme doplnili také do kulturního přehledu</h2>
  <p>Autokemp a prunéřovské koupaliště jsou součástí našeho pravidelného přehledu volnočasových možností. Upozornění na srpnová omezení jsme proto doplnili i do článku <a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kam v Kadani a okolí od 27. července do 2. srpna</a>, aby návštěvníci našli provozní změnu také u původního tipu.</p>
  <div class="source-list"><h2>Zdroje</h2><ul><li>Veřejné provozní oznámení Autokempu Prunéřov zveřejněné na Facebooku a sdílené stránkou Kultura v Kadani.</li><li><a href="https://www.autokemp-prunerov.cz/" target="_blank" rel="noopener noreferrer">Autokemp Prunéřov – oficiální web a kontakt</a></li><li><a href="https://www.cezdistribuce.cz/pro-zakazniky/potrebuji-vyresit/stavajici-pripojeni/overeni-planovane-odstavky" target="_blank" rel="noopener noreferrer">ČEZ Distribuce – ověření plánované odstávky podle adresy</a></li></ul></div>
</article>
<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>3. 8. po 18:00</li><li>10. 8. po 18:00</li><li>14. 8. po 16:00</li><li>Recepce otevřená</li><li>Platba pouze hotově</li></ul></div><div data-promos data-context="sidebar"></div></aside>
</main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/o-webu/#provozovatel">Provozovatel</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/site.js" defer></script><script src="/reklamy.js?v=20260726-unified-article-1"></script><script src="/reklamy-oprava-obrazku.js?v=20260726-unified-article-1"></script><script src="/obsah-doplnky.js?v=20260726-unified-article-1"></script>
</body></html>
'''

HERO_SECTION = '''  <section class="wrap hero" id="clanky">
    <article class="lead" data-autokemp-outages-hero>
      <div class="photo" style="background:linear-gradient(135deg,#172c37,#6d3030 58%,#ba2027)"><span>PRAKTICKÉ INFORMACE</span><strong>3 ODSTÁVKY</strong></div>
      <div class="copy">
        <small>PRUNÉŘOV · 28. 07. 2026 · 11:30</small>
        <h1>Odstávky elektřiny omezí provoz restaurace v Autokempu Prunéřov</h1>
        <p>Ve dvou termínech otevře restaurace až po 18. hodině, potřetí po 16. hodině. Recepce zůstane otevřená, kartou ale nepůjde platit.</p>
        <a class="btn" href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst praktické informace →</a>
      </div>
    </article>
    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">28. 7. 2026 v 5:00</p>
      <h2>ARC-MED za 16 milionů: dva posudky, nejasné schválení a spor o dvanáct milionů</h2>
      <p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p>
      <a class="aside-button" href="/clanky/arc-med-nemocnice-kadan.html">Přečíst celý článek →</a>
      <div class="aside-links">
        <a href="/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html">Výcvik hasičů na Nechranicích</a>
        <a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kulturní přehled na tento týden</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>
  </section>'''

HOME_CARD = '''    <article class="article-card service" data-autokemp-outages-card>
      <div class="visual" style="background:linear-gradient(135deg,#172c37,#6d3030 58%,#ba2027)"><strong>Odstávky v autokempu</strong></div>
      <div class="article-body"><span class="meta">28. 7. 2026 · 11:30 · Praktické informace</span><h3>Restaurace v Prunéřově třikrát otevře později</h3><p>Recepce zůstane otevřená, během odstávek ale nebude možné platit kartou.</p><a class="read-more" href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst článek →</a></div>
    </article>'''

ARCHIVE_CARD = '''    <article class="archive-item service" data-autokemp-outages-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#172c37,#6d3030 58%,#ba2027)"><strong>Odstávky v autokempu</strong></div>
      <div class="archive-body"><span class="archive-meta">28. července 2026 v 11:30 · Praktické informace · Prunéřov</span><h2>Odstávky elektřiny omezí v srpnu provoz restaurace v Autokempu Prunéřov</h2><p>Restaurace otevře 3. a 10. srpna až po 18. hodině a 14. srpna po 16. hodině. Recepce zůstane otevřená, kartou ale nepůjde platit.</p><a href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst praktické informace →</a></div>
    </article>'''

RSS_ITEM = '''    <item>
      <title>Odstávky elektřiny omezí v srpnu provoz restaurace v Autokempu Prunéřov</title>
      <description><![CDATA[Restaurace otevře 3. a 10. srpna až po 18. hodině a 14. srpna po 16. hodině. Recepce zůstane otevřená, kartou ale nepůjde platit.]]></description>
      <link>https://nasekadan.cz/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html</guid>
      <pubDate>Tue, 28 Jul 2026 11:30:00 +0200</pubDate>
      <category>Praktické informace</category><category>Prunéřov</category><category>Elektřina</category><category>Autokemp</category>
      <szn:image><szn:url>https://nasekadan.cz/social-card.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>
    </item>
'''

NEWS_URL = '''  <url><loc>https://nasekadan.cz/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>2026-07-28T11:30:00+02:00</news:publication_date><news:title>Odstávky elektřiny omezí v srpnu provoz restaurace v Autokempu Prunéřov</news:title></news:news></url>
'''

CULTURE_NOTE = '''  <div class="warning" data-autokemp-outages-note><strong>Důležité upozornění na srpnový provoz Autokempu Prunéřov.</strong> Restaurace kvůli plánovaným odstávkám elektřiny otevře v pondělí 3. srpna a 10. srpna až po 18. hodině a v pátek 14. srpna po 16. hodině. Recepce pro ubytované zůstane otevřená, během odstávek ale nebude možné platit kartou. <a href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Podrobné praktické informace</a>.</div>'''


def replace_hero_and_home_card() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(r'  <section class="wrap hero" id="clanky">.*?</section>', HERO_SECTION, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Nenalezena hero sekce titulní stránky")
    text = re.sub(r'\s*<article\b[^>]*data-autokemp-outages-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
    marker = '<div class="article-list">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam článků na titulní stránce")
    text = text.replace(marker, marker + "\n" + HOME_CARD, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<article\b[^>]*data-autokemp-outages-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam archivu")
    text = text.replace(marker, marker + "\n" + ARCHIVE_CARD, 1)

    for match in list(re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)):
        try:
            data = json.loads(match.group(1))
        except Exception:
            continue
        itemlist = next((x for x in data.get("@graph", []) if x.get("@type") == "ItemList"), None) if isinstance(data, dict) else None
        if not itemlist:
            continue
        existing = [x for x in itemlist.get("itemListElement", []) if x.get("url") != ARTICLE_URL]
        existing.insert(0, {"@type": "ListItem", "url": ARTICLE_URL, "name": TITLE})
        for pos, item in enumerate(existing, 1):
            item["position"] = pos
        itemlist["itemListElement"] = existing
        itemlist["numberOfItems"] = len(existing)
        replacement = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + '</script>'
        text = text[:match.start()] + replacement + text[match.end():]
        break
    path.write_text(text, encoding="utf-8", newline="\n")


def update_culture() -> None:
    path = ROOT / "clanky" / "kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<meta property="article:modified_time" content="[^"]+">', f'<meta property="article:modified_time" content="{PUBLISHED}">', text, count=1)
    text = re.sub(r'"dateModified":"[^"]+"', f'"dateModified":"{PUBLISHED}"', text, count=1)
    text = re.sub(r'\s*<div class="warning" data-autokemp-outages-note>.*?</div>\s*', '\n', text, flags=re.S)
    pattern = re.compile(r'(<section class="event">\s*<time>ČERVENEC A SRPEN · PODLE POČASÍ</time><h3>Koupaliště Prunéřov</h3>.*?</section>)', re.S)
    text, count = pattern.subn(r'\1\n' + CULTURE_NOTE, text, count=1)
    if count != 1:
        raise RuntimeError("Nenalezena část o Prunéřovu v kulturním přehledu")
    if 'data-autokemp-outages-source' not in text:
        source = '<li data-autokemp-outages-source><a href="https://www.autokemp-prunerov.cz/" target="_blank" rel="noopener noreferrer">Autokemp Prunéřov – provozní informace a kontakt</a></li>'
        text = text.replace('</ul>', source + '\n  </ul>', 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<item>.*?<link>' + re.escape(ARTICLE_URL) + r'</link>.*?</item>\s*', '\n', text, flags=re.S)
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', '<lastBuildDate>Tue, 28 Jul 2026 11:30:00 +0200</lastBuildDate>', text, count=1)
    marker = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if marker not in text:
        raise RuntimeError("Nenalezen RSS marker")
    text = text.replace(marker, marker + '\n' + RSS_ITEM, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_sitemaps() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url><loc>' + re.escape(ARTICLE_URL) + r'</loc>.*?</url>\s*', '\n', text, flags=re.S)
    text = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', r'\g<1>2026-07-28', text, count=1)
    text = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', r'\g<1>2026-07-28', text, count=1)
    text = re.sub(r'(<loc>https://nasekadan\.cz/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026\.html</loc><lastmod>)[^<]+', r'\g<1>2026-07-28', text, count=1)
    text = text.replace('</urlset>', f'  <url><loc>{ARTICLE_URL}</loc><lastmod>2026-07-28</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n</urlset>')
    path.write_text(text, encoding="utf-8", newline="\n")

    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url>\s*<loc>' + re.escape(ARTICLE_URL) + r'</loc>.*?</url>\s*', '\n', text, flags=re.S)
    text = text.replace('>', '>\n' + NEWS_URL, 1) if '<urlset' in text else text
    news.write_text(text, encoding="utf-8", newline="\n")


def update_manifest() -> None:
    path = ROOT / "production-content-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = [x for x in data.get("required_articles", []) if x.get("path") != f"clanky/{SLUG}.html"]
    items.insert(0, {"path": f"clanky/{SLUG}.html", "needle": "Odstávky elektřiny omezí v srpnu provoz restaurace", "must_be_on_home": True, "must_be_in_archive": True})
    data["required_articles"] = items
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def remove_client_override() -> None:
    path = ROOT / "app.js"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\n?const FIREFIGHTERS_HREF=.*?document\.addEventListener\('DOMContentLoaded',lockHomepageEditorialOrder\);\n?", "\n", text, flags=re.S)
    path.write_text(text, encoding="utf-8", newline="\n")


def protect_from_old_order_scripts() -> None:
    for name in ("enforce_current_article_order.py", "ensure_kolobezky_order.py", "enforce_production_article_order.py"):
        path = ROOT / "scripts" / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        token = "LATEST_AUTOKEMP_GUARD"
        if token in text:
            continue
        marker = "ROOT = Path(__file__).resolve().parents[1]"
        guard = marker + f'''\n# LATEST_AUTOKEMP_GUARD: staré opravné skripty nesmějí přepsat novější titulní článek.\nif (ROOT / "clanky" / "{SLUG}.html").exists():\n    print("Novější článek o odstávkách Autokempu Prunéřov je již publikován; staré pořadí se nepoužije.")\n    raise SystemExit(0)'''
        if marker in text:
            text = text.replace(marker, guard, 1)
            path.write_text(text, encoding="utf-8", newline="\n")


def rewrite_latest_enforcer() -> None:
    path = ROOT / "scripts" / "enforce_homepage_latest_order.py"
    content = f'''#!/usr/bin/env python3\nfrom pathlib import Path\nimport re\nROOT=Path(__file__).resolve().parents[1]\nHOME=ROOT/"index.html"\nARTICLE=ROOT/"clanky"/"{SLUG}.html"\nHERO={HERO_SECTION!r}\nCARD={HOME_CARD!r}\nif not ARTICLE.exists():\n    raise SystemExit("Chybí nejnovější článek Autokempu Prunéřov")\ntext=HOME.read_text(encoding="utf-8")\ntext,count=re.subn(r'  <section class="wrap hero" id="clanky">.*?</section>',HERO,text,count=1,flags=re.S)\nif count!=1: raise SystemExit("Nenalezena hero sekce")\ntext=re.sub(r'\\s*<article\\b[^>]*data-autokemp-outages-card[^>]*>.*?</article>\\s*','\\n',text,flags=re.S)\nmarker='<div class="article-list">'\nif marker not in text: raise SystemExit("Nenalezen seznam článků")\ntext=text.replace(marker,marker+'\\n'+CARD,1)\nHOME.write_text(text,encoding="utf-8",newline="\\n")\nprint("Titulní stránka zachovává nejnovější článek o odstávkách v Autokempu Prunéřov.")\n'''
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    ARTICLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTICLE_PATH.write_text(ARTICLE, encoding="utf-8", newline="\n")
    replace_hero_and_home_card()
    update_archive()
    update_culture()
    update_rss()
    update_sitemaps()
    update_manifest()
    remove_client_override()
    protect_from_old_order_scripts()
    rewrite_latest_enforcer()
    print("Článek o odstávkách Autokempu Prunéřov a kulturní přehled jsou připravené.")


if __name__ == "__main__":
    main()
