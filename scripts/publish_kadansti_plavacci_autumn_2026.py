#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "kadansti-plavacci-zapis-podzim-2026"
ARTICLE_PATH = ROOT / "clanky" / f"{SLUG}.html"
ARTICLE_URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
ARTICLE_HREF = f"/clanky/{SLUG}.html"
IMAGE_URL = "https://nasekadan.cz/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png"
PUBLISHED = "2026-07-31T21:30:00+02:00"
TITLE = "Kadaňští Plaváčci otevřeli zápis do podzimních kurzů. Nabídka je pro děti i dospělé"
DESC = "Kadaňští Plaváčci zahájili zápis do podzimních kurzů 2026. Nabízejí deset lekcí pro děti různých věkových kategorií, dospělé i AquaFIT."

ARTICLE = '''<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Kadaňští Plaváčci otevřeli zápis do podzimních kurzů | Naše Kadaň</title>
  <meta name="description" content="Kadaňští Plaváčci zahájili zápis do podzimních kurzů 2026. Nabízejí deset lekcí pro děti různých věkových kategorií, dospělé i AquaFIT.">
  <link rel="canonical" href="https://nasekadan.cz/clanky/kadansti-plavacci-zapis-podzim-2026.html">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../style.css">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#116f9d">
  <meta property="article:published_time" content="2026-07-31T21:30:00+02:00">
  <meta property="article:modified_time" content="2026-07-31T21:30:00+02:00">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="Kadaňští Plaváčci otevřeli zápis do podzimních kurzů">
  <meta property="og:description" content="Kurzy jsou určené dětem různých věkových kategorií, dospělým i zájemcům o AquaFIT. Kapacita je omezená.">
  <meta property="og:url" content="https://nasekadan.cz/clanky/kadansti-plavacci-zapis-podzim-2026.html">
  <meta property="og:image" content="https://nasekadan.cz/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Kadaňští Plaváčci otevřeli zápis do podzimních kurzů">
  <meta name="twitter:description" content="Kurzy pro děti i dospělé a AquaFIT. Kapacita je omezená.">
  <meta name="twitter:image" content="https://nasekadan.cz/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png">
  <link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml">
  <link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
  <meta name="geo.region" content="CZ-42">
  <meta name="geo.placename" content="Kadaň">
  <meta name="geo.position" content="50.375984;13.271307">
  <meta name="ICBM" content="50.375984, 13.271307">
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"Kadaňští Plaváčci otevřeli zápis do podzimních kurzů. Nabídka je pro děti i dospělé","description":"Kadaňští Plaváčci zahájili zápis do podzimních kurzů 2026. Nabízejí deset lekcí pro děti různých věkových kategorií, dospělé i AquaFIT.","datePublished":"2026-07-31T21:30:00+02:00","dateModified":"2026-07-31T21:30:00+02:00","author":{"@type":"Organization","@id":"https://nasekadan.cz/#organization","name":"Naše Kadaň","url":"https://nasekadan.cz/o-webu/"},"publisher":{"@id":"https://nasekadan.cz/#organization"},"mainEntityOfPage":{"@type":"WebPage","@id":"https://nasekadan.cz/clanky/kadansti-plavacci-zapis-podzim-2026.html"},"inLanguage":"cs-CZ","isAccessibleForFree":true,"image":["https://nasekadan.cz/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png"]}</script>
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Naše Kadaň","item":"https://nasekadan.cz/"},{"@type":"ListItem","position":2,"name":"Články","item":"https://nasekadan.cz/clanky/"},{"@type":"ListItem","position":3,"name":"Kadaňští Plaváčci otevřeli zápis do podzimních kurzů","item":"https://nasekadan.cz/clanky/kadansti-plavacci-zapis-podzim-2026.html"}]}</script>
  <style>
    .article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}
    .article h1{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}
    .article h2{font:800 34px/1.15 Georgia,serif;margin:46px 0 14px}
    .article p,.article li{font-size:18px}.article .leadtext{font-size:23px;color:#465862;line-height:1.55}
    .article a{color:#9f2626;text-decoration:underline;text-underline-offset:3px}
    .article-image{width:100%;height:auto;border-radius:24px;box-shadow:var(--shadow);margin:30px 0;display:block}
    .course-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:28px 0}
    .course-card{background:#eef7fb;border:1px solid #cbe2ec;border-radius:18px;padding:21px}
    .course-card strong{display:block;font:800 24px/1.15 Georgia,serif;color:#0b668f;margin-bottom:7px}
    .course-card span{color:#4e616b;font-size:15px;line-height:1.45}
    .callout{border-left:6px solid #1597c6;background:#eff9fc;margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}
    .callout strong{font:800 24px Georgia,serif;display:block;margin-bottom:6px}
    .source-list{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}.source-list li{font-size:15px;margin-bottom:8px}
    .sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px}
    @media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}
    @media(max-width:680px){.course-grid{grid-template-columns:1fr}.article h1{font-size:42px}.article .leadtext{font-size:20px}}
  </style>
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
</head>
<body>
<header data-site-header="v1">
  <div class="wrap head">
    <a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
    <nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav>
  </div>
</header>
<main class="wrap article-shell" data-article-template="unified-v1">
<article class="article">
  <p class="tag">VOLNÝ ČAS · PRAKTICKÉ INFORMACE · 31. ČERVENCE 2026</p>
  <h1>Kadaňští Plaváčci otevřeli zápis do podzimních kurzů. Nabídka je pro děti i dospělé</h1>
  <p class="leadtext"><strong>Plavecká škola Kadaňští Plaváčci zahájila přihlašování do podzimních kurzů 2026. Nabídka zahrnuje lekce pro děti od tří let, starší školáky, dospělé i cvičení AquaFIT. Organizátoři upozorňují, že kapacita je omezená a oblíbené časy se mohou rychle zaplnit.</strong></p>
  <img class="article-image" src="/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png" width="1200" height="630" alt="Kadaňští Plaváčci otevřeli zápis do podzimních kurzů 2026">
  <p>Podle zveřejněného oznámení jsou kurzy určené začátečníkům i dětem a dospělým, kteří chtějí svou techniku dále zlepšovat. Přihlášení a podrobnosti pořadatelé zveřejnili na svém webu.</p>

  <h2>Pro koho jsou kurzy určené</h2>
  <div class="course-grid">
    <div class="course-card"><strong>Děti od 3 do 4 let</strong><span>Začátečnické lekce bez rodičů zaměřené na seznámení s vodou a první plavecké dovednosti.</span></div>
    <div class="course-card"><strong>Děti od 4 do 8 let</strong><span>Začátečnické i zdokonalovací lekce s vodními hrami a rozvojem základních dovedností.</span></div>
    <div class="course-card"><strong>Děti od 8 do 15 let</strong><span>Výuka a prohlubování plaveckých stylů, techniky a fyzické zdatnosti ve skupinách podle věku.</span></div>
    <div class="course-card"><strong>Dospělí a AquaFIT</strong><span>Plavání pro začátečníky i zdokonalení techniky; AquaFIT nabízí cvičení ve vodě s menší zátěží kloubů.</span></div>
  </div>

  <p>Oficiální stránka uvádí u jednotlivých skupin kurz v rozsahu deseti lekcí. Přesné rozdělení termínů a dostupnost konkrétních časů je potřeba ověřit při přihlášení.</p>

  <div class="callout"><strong>Jak se přihlásit</strong><p>Přihlášky a aktuální informace jsou na webu <a href="https://sites.google.com/kadanplavacci.com/kadat-plavci/domovsk%C3%A1-str%C3%A1nka" target="_blank" rel="noopener noreferrer">Kadaňských Plaváčků</a>. Dotazy lze směřovat Janě Špičkové na telefon <a href="tel:+420724900986">724 900 986</a> nebo e-mail <a href="mailto:info@kadanplavacci.com">info@kadanplavacci.com</a>.</p></div>

  <h2>Kde kurzy probíhají</h2>
  <p>Kadaňští Plaváčci patří mezi poskytovatele plaveckých kurzů v plavecké hale Koupaliště Kadaň. Samotné rozvržení jednotlivých skupin a případné organizační pokyny sděluje pořadatel při registraci.</p>

  <div class="source-list">
    <h2>Zdroje a stav informace</h2>
    <ul>
      <li><a href="https://sites.google.com/kadanplavacci.com/kadat-plavci/domovsk%C3%A1-str%C3%A1nka" target="_blank" rel="noopener noreferrer">Kadaňští Plaváčci – oficiální web</a>: věkové skupiny, deset lekcí, plavání pro dospělé, AquaFIT a kontakty.</li>
      <li><a href="https://www.koupalistekadan.cz/inpage/plavecke-kurzy/" target="_blank" rel="noopener noreferrer">Koupaliště Kadaň – plavecké kurzy</a>: zařazení Kadaňských Plaváčků mezi kurzy v plavecké hale a kontaktní údaje.</li>
      <li>Veřejné oznámení Kadaňských Plaváčků na Facebooku z 31. července 2026: zahájení zápisu a upozornění na omezenou kapacitu.</li>
    </ul>
    <p><small>Stav ověřen 31. července 2026 ve 21:30. Dostupnost míst se může průběžně měnit.</small></p>
  </div>
</article>
<aside class="sticky">
  <div class="sidebox"><h3>Rychlý přehled</h3><ul><li>Zápis je spuštěný</li><li>Podzimní kurzy 2026</li><li>Děti od 3 let</li><li>Kurzy pro dospělé</li><li>AquaFIT</li><li>10 lekcí</li></ul></div>
  <div class="sidebox"><h3>Kontakt</h3><p><strong>Jana Špičková</strong><br><a href="tel:+420724900986">724 900 986</a><br><a href="mailto:info@kadanplavacci.com">info@kadanplavacci.com</a></p></div>
  <div data-promos data-context="sidebar"></div>
</aside>
</main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/o-webu/#provozovatel">Provozovatel</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/site.js" defer></script>
<script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script>
<script src="/reklamy-oprava-obrazku.js"></script>
<script src="/obsah-doplnky.js"></script>
</body></html>
'''

HERO_SECTION = '''  <section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="/clanky/kadansti-plavacci-zapis-podzim-2026.html">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(90deg,rgba(3,28,49,.35),rgba(3,28,49,.1)),url('/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png') center/cover no-repeat"><span>VOLNÝ ČAS · PRAKTICKÉ INFORMACE · 31. ČERVENCE 2026</span><strong>PODZIM 2026</strong></div>
      <div class="copy">
        <small>VOLNÝ ČAS · PRAKTICKÉ INFORMACE · 31. 7. 2026 · 21:30</small>
        <h1>Kadaňští Plaváčci otevřeli zápis do podzimních kurzů</h1>
        <p>Nabídka zahrnuje lekce pro děti od tří let, starší školáky, dospělé i AquaFIT. Kapacita je omezená.</p>
        <a class="btn" href="/clanky/kadansti-plavacci-zapis-podzim-2026.html">Přečíst praktické informace →</a>
      </div>
    </article>
    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">31. 7. 2026 v 19:34</p>
      <h2>Další plán krajiny pro Kadaň za 1,45 milionu. Co se překrývá se starší studií?</h2>
      <p>Město zadalo další plán krajiny. Dokumenty ukazují obsahový překryv, nikoli důkaz dvojího placení.</p>
      <a class="aside-button" href="/clanky/plan-uses-kadan-krajina-zakazky-2026.html">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html">Srpnový program galerií</a><a href="/clanky/">Všechny články podle data</a></div>
    </aside>
  </section>'''

HOME_CARD = '''    <article class="article-card service" data-plavacci-autumn-card>
      <div class="visual" style="background:linear-gradient(90deg,rgba(3,28,49,.28),rgba(3,28,49,.08)),url('/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png') center/cover no-repeat"><strong>Kadaňští Plaváčci otevřeli zápis do podzimních kurzů</strong></div>
      <div class="article-body"><span class="meta">31. 7. 2026 · 21:30 · Volný čas · Praktické informace</span><h3>Nové kurzy jsou pro děti, dospělé i zájemce o AquaFIT</h3><p>Podzimní zápis je spuštěný. Organizátoři upozorňují na omezenou kapacitu.</p><a class="read-more" href="/clanky/kadansti-plavacci-zapis-podzim-2026.html">Přečíst článek →</a></div>
    </article>'''

ARCHIVE_CARD = '''    <article class="archive-item service" data-plavacci-autumn-card>
      <div class="archive-visual" style="background:linear-gradient(90deg,rgba(3,28,49,.28),rgba(3,28,49,.08)),url('/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png') center/cover no-repeat"><strong>Zápis do kurzů plavání</strong></div>
      <div class="archive-body"><span class="archive-meta">31. července 2026 ve 21:30 · Volný čas · Praktické informace</span><h2>Kadaňští Plaváčci otevřeli zápis do podzimních kurzů. Nabídka je pro děti i dospělé</h2><p>Kurzy zahrnují skupiny pro děti od tří let, starší školáky, dospělé i AquaFIT. Kapacita je omezená.</p><a href="/clanky/kadansti-plavacci-zapis-podzim-2026.html">Přečíst praktické informace →</a></div>
    </article>'''

RSS_ITEM = '''    <item><title>Kadaňští Plaváčci otevřeli zápis do podzimních kurzů</title><description><![CDATA[Kadaňští Plaváčci zahájili zápis do podzimních kurzů 2026. Nabízejí deset lekcí pro děti různých věkových kategorií, dospělé i AquaFIT.]]></description><link>https://nasekadan.cz/clanky/kadansti-plavacci-zapis-podzim-2026.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/kadansti-plavacci-zapis-podzim-2026.html</guid><pubDate>Fri, 31 Jul 2026 21:30:00 +0200</pubDate><category>Volný čas</category><category>Praktické informace</category><category>Plavání</category><szn:image><szn:url>https://nasekadan.cz/social/kadansti-plavacci-zapis-podzim-2026-15a89a2edb.png</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>
'''

NEWS_URL = '''  <url><loc>https://nasekadan.cz/clanky/kadansti-plavacci-zapis-podzim-2026.html</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>2026-07-31T21:30:00+02:00</news:publication_date><news:title>Kadaňští Plaváčci otevřeli zápis do podzimních kurzů</news:title></news:news></url>
'''


def write_article() -> None:
    ARTICLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTICLE_PATH.write_text(ARTICLE, encoding="utf-8", newline="\n")


def replace_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(r'  <section class="wrap hero" id="clanky".*?</section>', HERO_SECTION, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Nenalezena hero sekce titulní stránky")
    text = re.sub(r'\s*<article\b[^>]*data-plavacci-autumn-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
    marker = '<div class="article-list">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam článků na titulní stránce")
    text = text.replace(marker, marker + "\n" + HOME_CARD, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<article\b[^>]*data-plavacci-autumn-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
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


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<item>.*?<link>' + re.escape(ARTICLE_URL) + r'</link>.*?</item>\s*', '\n', text, flags=re.S)
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', '<lastBuildDate>Fri, 31 Jul 2026 21:30:00 +0200</lastBuildDate>', text, count=1)
    marker = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if marker not in text:
        raise RuntimeError("Nenalezen RSS marker")
    text = text.replace(marker, marker + "\n" + RSS_ITEM, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_sitemaps() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url><loc>' + re.escape(ARTICLE_URL) + r'</loc>.*?</url>\s*', '\n', text, flags=re.S)
    text = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', r'\g<1>2026-07-31', text, count=1)
    text = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', r'\g<1>2026-07-31', text, count=1)
    text = text.replace('</urlset>', f'  <url><loc>{ARTICLE_URL}</loc><lastmod>2026-07-31</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n</urlset>')
    path.write_text(text, encoding="utf-8", newline="\n")

    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url>\s*<loc>' + re.escape(ARTICLE_URL) + r'</loc>.*?</url>\s*', '\n', text, flags=re.S)
    text = re.sub(r'(<urlset\b[^>]*>)', lambda match: match.group(1) + '\n' + NEWS_URL, text, count=1) if '<urlset' in text else text
    news.write_text(text, encoding="utf-8", newline="\n")


def update_llms() -> None:
    path = ROOT / "llms.txt"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    line = f"- [{TITLE}]({ARTICLE_URL}) — {DESC}\n"
    text = re.sub(r'^- \[Kadaňští Plaváčci otevřeli zápis.*?\n', '', text, flags=re.M)
    marker = "## Nejnovější články\n"
    if marker in text:
        text = text.replace(marker, marker + line, 1)
    else:
        text += "\n" + line
    path.write_text(text, encoding="utf-8", newline="\n")


def update_manifest() -> None:
    path = ROOT / "production-content-manifest.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    items = [x for x in data.get("required_articles", []) if x.get("path") != f"clanky/{SLUG}.html"]
    items.insert(0, {
        "path": f"clanky/{SLUG}.html",
        "needle": "Kadaňští Plaváčci otevřeli zápis do podzimních kurzů",
        "must_be_on_home": True,
        "must_be_in_archive": True
    })
    data["required_articles"] = items
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rewrite_latest_enforcer() -> None:
    path = ROOT / "scripts" / "enforce_homepage_latest_order.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f'''#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"index.html"
ARTICLE=ROOT/"clanky"/"{SLUG}.html"
HERO={HERO_SECTION!r}
CARD={HOME_CARD!r}
if not ARTICLE.exists(): raise SystemExit("Chybí nejnovější zpráva o zápisu do kurzů")
text=HOME.read_text(encoding="utf-8")
text,count=re.subn(r'  <section class="wrap hero" id="clanky".*?</section>',HERO,text,count=1,flags=re.S)
if count!=1: raise SystemExit("Nenalezena hero sekce")
text=re.sub(r'\\s*<article\\b[^>]*data-plavacci-autumn-card[^>]*>.*?</article>\\s*','\\n',text,flags=re.S)
marker='<div class="article-list">'
if marker not in text: raise SystemExit("Nenalezen seznam článků")
text=text.replace(marker,marker+'\\n'+CARD,1)
HOME.write_text(text,encoding="utf-8",newline="\\n")
print("Titulní stránka zachovává nejnovější zprávu o kurzech plavání.")
'''
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    write_article()
    replace_home()
    update_archive()
    update_rss()
    update_sitemaps()
    update_llms()
    update_manifest()
    print("Článek o zápisu do podzimních kurzů Kadaňských Plaváčků byl publikován.")


if __name__ == "__main__":
    main()
