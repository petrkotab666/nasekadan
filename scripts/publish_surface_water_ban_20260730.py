#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026"
ARTICLE_PATH = ROOT / "clanky" / f"{SLUG}.html"
ARTICLE_HREF = f"/clanky/{SLUG}.html"
ARTICLE_URL = f"https://nasekadan.cz{ARTICLE_HREF}"
TITLE = "Kvůli suchu platí na Kadaňsku zákaz odběru vody ze čtrnácti toků"
PUBLISHED = "2026-07-30T07:45:00+02:00"
DATE_RSS = "Thu, 30 Jul 2026 07:45:00 +0200"

ARTICLE = '''<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Kvůli suchu platí na Kadaňsku zákaz odběru vody ze čtrnácti toků | Naše Kadaň</title>
  <meta name="description" content="Vodoprávní úřad v Kadani zakázal do odvolání odběr povrchové vody ze čtrnácti toků. Opatření platí od 27. července 2026, výjimkou je pitná voda a hašení požárů.">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../style.css">
  <link rel="canonical" href="https://nasekadan.cz/clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#a9232b">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="Kvůli suchu platí na Kadaňsku zákaz odběru vody ze čtrnácti toků">
  <meta property="og:description" content="Zákaz platí od 27. července do odvolání. Úřad ho vydal kvůli velmi nízkým průtokům a ochraně vodních ekosystémů.">
  <meta property="og:url" content="https://nasekadan.cz/clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html">
  <meta property="og:image" content="https://nasekadan.cz/social-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta property="article:published_time" content="2026-07-30T07:45:00+02:00">
  <meta property="article:modified_time" content="2026-07-30T07:45:00+02:00">
  <style>
    .article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}
    .article h1{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}
    .article h2{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}
    .article p,.article li{font-size:18px}.article .leadtext{font-size:23px;color:#465862;line-height:1.55}
    .article a{color:#9f2626;text-decoration:underline;text-underline-offset:3px}
    .hero-visual{min-height:330px;border-radius:24px;background:radial-gradient(circle at 82% 18%,#ffffff22,transparent 27%),linear-gradient(135deg,#173b4c,#2c7180 58%,#a9232b);display:flex;align-items:flex-end;padding:30px;color:#fff;box-shadow:var(--shadow);margin:30px 0;position:relative;overflow:hidden}
    .hero-visual:after{content:'DO ODVOLÁNÍ';position:absolute;right:-18px;top:24px;font:900 58px/1 Arial;color:#ffffff12;white-space:nowrap}
    .hero-visual strong{font:800 31px Georgia,serif;max-width:680px;position:relative;z-index:1;text-shadow:0 2px 16px #000}
    .stream-list{columns:2;column-gap:32px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:24px 28px;box-shadow:0 8px 25px #16242d0a}.stream-list li{break-inside:avoid;margin-bottom:9px}
    .callout{border-left:6px solid var(--red);background:var(--cream);margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}.callout strong{font:800 24px Georgia,serif;display:block;margin-bottom:6px}
    .source-list{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}.source-list li{font-size:15px;margin-bottom:8px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px}
    @media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}@media(max-width:620px){.stream-list{columns:1}.hero-visual{min-height:260px}.hero-visual:after{font-size:34px}.article h1{font-size:42px}.article .leadtext{font-size:20px}}
  </style>
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"Kvůli suchu platí na Kadaňsku zákaz odběru vody ze čtrnácti toků","description":"Vodoprávní úřad v Kadani zakázal do odvolání odběr povrchové vody ze čtrnácti toků. Opatření platí od 27. července 2026.","datePublished":"2026-07-30T07:45:00+02:00","dateModified":"2026-07-30T07:45:00+02:00","author":{"@type":"Organization","name":"Naše Kadaň"},"publisher":{"@type":"Organization","name":"Naše Kadaň"},"mainEntityOfPage":"https://nasekadan.cz/clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html","inLanguage":"cs-CZ","isAccessibleForFree":true}</script>
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
</head>
<body>
<header><div class="wrap head"><a class="logo" href="../index.html"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="../index.html">Úvod</a><a href="/clanky/">Články</a><a href="../index.html#akce">Akce</a><a href="../pruvodce/">Průvodce</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1">
<article class="article">
  <p class="tag">DŮLEŽITÉ UPOZORNĚNÍ · VODA · 30. ČERVENCE 2026</p>
  <h1>Kvůli suchu platí na Kadaňsku zákaz odběru vody ze čtrnácti toků</h1>
  <p class="leadtext"><strong>Městský úřad Kadaň jako vodoprávní úřad zakázal kvůli velmi nízkým průtokům odběr povrchové vody ze čtrnácti toků a jejich vymezených úseků. Opatření platí od zveřejnění 27. července 2026 až do odvolání.</strong></p>
  <div class="hero-visual"><strong>Zákaz se týká odběrů vody například pro zalévání, napouštění nádrží nebo jiné běžné využití. Úřad avizuje kontroly odběrných míst.</strong></div>
  <h2>Kterých toků se zákaz týká</h2>
  <ul class="stream-list">
    <li>Dobřenecký potok, říční km 0,000–5,000</li>
    <li>Dubá I, říční km 0,000–4,400</li>
    <li>Dubá II, říční km 0,100–12,700</li>
    <li>Hájský potok, říční km 0,000–3,400</li>
    <li>Hasnický potok – levostranný přítok Liboce, říční km 0,000–9,800</li>
    <li>Leska, říční km 15,700–20,000</li>
    <li>Lettengrabenbach, od ústí po pramen</li>
    <li>Liboc, říční km 8,300–27,400</li>
    <li>Miřetický potok, od ústí po pramen</li>
    <li>Němčanský potok, říční km 6,600–7,700</li>
    <li>Růžovský potok, říční km 0,000–1,400</li>
    <li>Travná, říční km 0,000–1,100</li>
    <li>Třebčický potok, říční km 1,400–9,400</li>
    <li>Vintířovský potok, od ústí po pramen</li>
  </ul>
  <h2>Výjimkou je pitná voda a hašení požárů</h2>
  <p>Opatření se nevztahuje na odběry určené pro zásobování obyvatel pitnou vodou a na použití vody při hašení požárů. Dokument připouští také vybrané odběry z vodních nádrží pro zemědělskou a potravinářskou závlahu, pokud jde o veřejný zájem a jsou splněny stanovené podmínky.</p>
  <div class="callout"><strong>Platnost není stanovena pevným datem</strong><p>Zákaz platí do odvolání. Úřad v odůvodnění uvádí, že může trvat až do konce října, podle vývoje hydrologické situace však může být zrušen dříve.</p></div>
  <h2>Proč úřad zákaz vydal</h2>
  <p>Vodoprávní úřad opatření zdůvodnil dlouhodobě velmi nízkými průtoky. Další odběry by podle dokumentu mohly zhoršit stav toků, poškodit vodní organismy a omezit základní ekologické funkce vodních ekosystémů.</p>
  <p>Majitelé čerpadel a lidé, kteří vodu z dotčených toků používají, by měli odběr zastavit a sledovat další oznámení města. Kontroly se mohou zaměřit přímo na odběrná místa.</p>
  <div class="source-list"><h2>Zdroje</h2><ul><li><a href="https://www.mesto-kadan.cz/cs/system/uredni-deska-nova.html" target="_blank" rel="noopener noreferrer">Město Kadaň – úřední deska</a>, opatření MUKK/28368/2026 „Zákaz odběru povrchových vod do odvolání“, zveřejněné 27. července 2026.</li></ul><p><small>Stav ověřen 30. července 2026 v 7:45.</small></p></div>
</article>
<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>Platí od 27. července</li><li>Do odvolání</li><li>14 toků a jejich úseků</li><li>Důvodem jsou nízké průtoky</li><li>Výjimka pro pitnou vodu</li><li>Výjimka pro hašení</li><li>Úřad avizuje kontroly</li></ul></div><div data-promos data-context="sidebar"></div></aside>
</main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/o-webu/#provozovatel">Provozovatel</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/site.js" defer></script><script src="/reklamy.js"></script><script src="/reklamy-oprava-obrazku.js"></script><script src="/obsah-doplnky.js"></script><script src="/horko-feed.js"></script>
</body></html>
'''

HOME_CARD = '''    <article class="article-card service" data-surface-water-ban-card>
      <div class="visual" style="background:linear-gradient(135deg,#173b4c,#2c7180 58%,#a9232b)"><strong>Zákaz odběru vody</strong></div>
      <div class="article-body"><span class="meta">30. 7. 2026 · 7:45 · Důležité upozornění</span><h3>Kvůli suchu platí zákaz odběru vody ze čtrnácti toků</h3><p>Opatření vodoprávního úřadu platí od 27. července do odvolání. Výjimkou je pitná voda a hašení požárů.</p><a class="read-more" href="/clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html">Přečíst podrobnosti →</a></div>
    </article>'''

ARCHIVE_CARD = '''    <article class="archive-item service" data-surface-water-ban-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#173b4c,#2c7180 58%,#a9232b)"><strong>Zákaz odběru vody</strong></div>
      <div class="archive-body"><span class="archive-meta">30. července 2026 v 7:45 · Důležité upozornění · Kadaňsko</span><h2>Kvůli suchu platí na Kadaňsku zákaz odběru vody ze čtrnácti toků</h2><p>Vodoprávní úřad opatření vydal kvůli velmi nízkým průtokům. Platí od 27. července do odvolání.</p><a href="/clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html">Přečíst článek →</a></div>
    </article>'''

RSS_ITEM = f'''    <item>
      <title>{TITLE}</title>
      <description><![CDATA[Vodoprávní úřad v Kadani zakázal do odvolání odběr povrchové vody ze čtrnácti toků. Výjimkou je pitná voda a hašení požárů.]]></description>
      <link>{ARTICLE_URL}</link>
      <guid isPermaLink="true">{ARTICLE_URL}</guid>
      <pubDate>{DATE_RSS}</pubDate>
      <category>Důležité upozornění</category><category>Voda</category><category>Kadaňsko</category>
      <szn:image><szn:url>https://nasekadan.cz/social-card.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>
    </item>
'''

NEWS_URL = f'''  <url><loc>{ARTICLE_URL}</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>{PUBLISHED}</news:publication_date><news:title>{TITLE}</news:title></news:news></url>
'''


def update_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<article\b[^>]*data-surface-water-ban-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
    marker = '<div class="article-list">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam článků na titulní stránce")
    text = text.replace(marker, marker + "\n" + HOME_CARD, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<article\b[^>]*data-surface-water-ban-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
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
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{DATE_RSS}</lastBuildDate>', text, count=1)
    marker = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if marker not in text:
        raise RuntimeError("Nenalezen RSS marker")
    text = text.replace(marker, marker + "\n" + RSS_ITEM, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_sitemaps() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url><loc>' + re.escape(ARTICLE_URL) + r'</loc>.*?</url>\s*', '\n', text, flags=re.S)
    text = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', r'\g<1>2026-07-30', text, count=1)
    text = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', r'\g<1>2026-07-30', text, count=1)
    text = text.replace('</urlset>', f'  <url><loc>{ARTICLE_URL}</loc><lastmod>2026-07-30</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>\n</urlset>')
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
    items.insert(0, {"path": f"clanky/{SLUG}.html", "needle": "Kvůli suchu platí na Kadaňsku zákaz odběru vody", "must_be_on_home": True, "must_be_in_archive": True})
    data["required_articles"] = items
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ARTICLE_PATH.write_text(ARTICLE, encoding="utf-8", newline="\n")
    update_home()
    update_archive()
    update_rss()
    update_sitemaps()
    update_manifest()
    print(ARTICLE_PATH)


if __name__ == "__main__":
    main()
