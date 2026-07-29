#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "zs-chomutovska-kadan-stravne-zari-2026"
ARTICLE_PATH = ROOT / "clanky" / f"{SLUG}.html"
ARTICLE_HREF = f"/clanky/{SLUG}.html"
ARTICLE_URL = f"https://nasekadan.cz{ARTICLE_HREF}"
TITLE = "ZŠ Chomutovská od září zdraží obědy. Rodiče mají zvýšit limit inkasa"
PUBLISHED = "2026-07-29T16:44:00+02:00"

ARTICLE = '''<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ZŠ Chomutovská od září zdraží obědy | Naše Kadaň</title>
  <meta name="description" content="ZŠ Kadaň v Chomutovské ulici mění od 1. září 2026 ceny obědů. Rodiče mají od 15. srpna zvýšit limit inkasa na 700 nebo 900 Kč.">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../style.css">
  <link rel="canonical" href="https://nasekadan.cz/clanky/zs-chomutovska-kadan-stravne-zari-2026.html">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#a9232b">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="ZŠ Chomutovská od září zdraží obědy">
  <meta property="og:description" content="Nové ceny budou 26 až 32 Kč. Limit inkasa je potřeba upravit od 15. srpna na 700 Kč bez družiny nebo 900 Kč s družinou.">
  <meta property="og:url" content="https://nasekadan.cz/clanky/zs-chomutovska-kadan-stravne-zari-2026.html">
  <meta property="og:image" content="https://nasekadan.cz/social-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta property="article:published_time" content="2026-07-29T16:44:00+02:00">
  <meta property="article:modified_time" content="2026-07-29T16:44:00+02:00">
  <style>
    .article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}
    .article h1{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}
    .article h2{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}
    .article p,.article li{font-size:18px}.article .leadtext{font-size:23px;color:#465862;line-height:1.55}
    .article a{color:#9f2626;text-decoration:underline;text-underline-offset:3px}
    .hero-visual{min-height:330px;border-radius:24px;background:radial-gradient(circle at 82% 18%,#ffffff22,transparent 27%),linear-gradient(135deg,#173044,#47778a 58%,#a9232b);display:flex;align-items:flex-end;padding:30px;color:#fff;box-shadow:var(--shadow);margin:30px 0;position:relative;overflow:hidden}
    .hero-visual:after{content:'15. SRPNA';position:absolute;right:-18px;top:24px;font:900 62px/1 Arial;color:#ffffff12;white-space:nowrap}
    .hero-visual strong{font:800 31px Georgia,serif;max-width:680px;position:relative;z-index:1;text-shadow:0 2px 16px #000}
    .prices{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:30px 0}.prices div{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 8px 25px #16242d0a}.prices b{display:block;color:var(--red);font-size:30px}.prices span{font-size:15px;color:var(--muted)}
    .callout{border-left:6px solid var(--red);background:var(--cream);margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}.callout strong{font:800 24px Georgia,serif;display:block;margin-bottom:6px}
    .source-list{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}.source-list li{font-size:15px;margin-bottom:8px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px}
    @media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}@media(max-width:760px){.prices{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:520px){.prices{grid-template-columns:1fr}.hero-visual{min-height:260px}.hero-visual:after{font-size:38px}.article h1{font-size:42px}.article .leadtext{font-size:20px}}
  </style>
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"ZŠ Chomutovská od září zdraží obědy. Rodiče mají zvýšit limit inkasa","description":"ZŠ Kadaň v Chomutovské ulici mění od 1. září 2026 ceny obědů. Rodiče mají od 15. srpna zvýšit limit inkasa na 700 nebo 900 Kč.","datePublished":"2026-07-29T16:44:00+02:00","dateModified":"2026-07-29T16:44:00+02:00","author":{"@type":"Organization","name":"Naše Kadaň"},"publisher":{"@type":"Organization","name":"Naše Kadaň"},"mainEntityOfPage":"https://nasekadan.cz/clanky/zs-chomutovska-kadan-stravne-zari-2026.html","inLanguage":"cs-CZ"}</script>
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
</head>
<body>
<header><div class="wrap head"><a class="logo" href="../index.html"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="../index.html">Úvod</a><a href="/clanky/">Články</a><a href="../index.html#akce">Akce</a><a href="../pruvodce/">Průvodce</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1">
<article class="article">
  <p class="tag">PRAKTICKÉ INFORMACE · ŠKOLY · 29. ČERVENCE 2026</p>
  <h1>ZŠ Chomutovská od září zdraží obědy. Rodiče mají zvýšit limit inkasa</h1>
  <p class="leadtext"><strong>Školní jídelna Základní školy Kadaň v Chomutovské ulici změní od 1. září ceny obědů. Rodiče platící inkasem mají současně s platností od 15. srpna zvýšit bankovní limit na 700 korun, případně na 900 korun u strávníků s družinou.</strong></p>
  <div class="hero-visual"><strong>Nejdůležitější termín je 15. srpna. Příliš nízký limit může zabránit správnému provedení inkasa za zářijové stravné.</strong></div>
  <div class="prices"><div><b>26 Kč</b><span>děti 3–6 let</span></div><div><b>29 Kč</b><span>strávníci 7–10 let</span></div><div><b>31 Kč</b><span>strávníci 11–14 let</span></div><div><b>32 Kč</b><span>strávníci od 15 let</span></div></div>
  <h2>Jaké limity mají rodiče nastavit</h2>
  <p>Škola žádá rodiče, aby od 15. srpna nastavili limit inkasa na <strong>700 Kč u strávníků bez družiny</strong> a na <strong>900 Kč u strávníků s družinou</strong>. Dosavadní informace na stejné stránce uvádějí nižší limity 620 a 770 Kč; nové oznámení má proto přednost.</p>
  <div class="callout"><strong>Prodej stravného na září</strong><p>Osobní prodej stravného je podle školy naplánován na úterý 25. srpna a úterý 1. září 2026, v obou dnech od 6:00 do 14:00.</p></div>
  <h2>Zařazení do věkové skupiny platí na celý školní rok</h2>
  <p>Škola upozorňuje, že dítě je do věkové kategorie zařazeno podle věku, kterého dosáhne kdykoli během školního roku od 1. září 2026 do 31. srpna 2027. Vyšší cena tedy může platit už od začátku září, i když dítě narozeniny oslaví až později.</p>
  <h2>Kontakty na školní jídelnu</h2>
  <p>Vedoucí školní jídelny je Romana Bárová. Škola uvádí telefon <a href="tel:+420739623288">739 623 288</a> a e-mail <a href="mailto:jidelna-3zs@ktkadan.cz">jidelna-3zs@ktkadan.cz</a>. Platba inkasem se provádí k 15. dni v měsíci.</p>
  <h2>Ostatní kadaňské jídelny zatím sledujeme samostatně</h2>
  <p>Změna je v tuto chvíli potvrzená pro jídelnu ZŠ Chomutovská. U ostatních kadaňských škol jsme při stejné kontrole nenašli nové oznámení se stejným termínem a limity. Jakmile další škola zveřejní změnu, přehled doplníme.</p>
  <div class="source-list"><h2>Zdroje</h2><ul><li><a href="https://3zskadan.cz/?page_id=768" target="_blank" rel="noopener noreferrer">ZŠ Kadaň, Chomutovská 1683 – oficiální stránka školní jídelny</a>: nové ceny, limity inkasa, termíny prodeje a kontakty.</li></ul><p><small>Stav ověřen 29. července 2026 v 16:44.</small></p></div>
</article>
<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>Ceny od 1. září</li><li>26 až 32 Kč za oběd</li><li>Limit 700 Kč bez družiny</li><li>Limit 900 Kč s družinou</li><li>Změna limitu od 15. srpna</li></ul></div><div data-promos data-context="sidebar"></div></aside>
</main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/o-webu/#provozovatel">Provozovatel</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/site.js" defer></script><script src="/reklamy.js"></script><script src="/reklamy-oprava-obrazku.js"></script><script src="/obsah-doplnky.js"></script><script src="/horko-feed.js"></script>
</body></html>
'''

HOME_CARD = '''<article class="article-card service" data-school-meals-card><div class="visual" style="background:linear-gradient(135deg,#173044,#47778a 58%,#a9232b)"><strong>Nové ceny obědů</strong></div><div class="article-body"><span class="meta">29. 7. 2026 · 16:44 · Školy a praktické informace</span><h3>ZŠ Chomutovská od září zdraží obědy</h3><p>Rodiče mají od 15. srpna zvýšit limit inkasa na 700 Kč, případně 900 Kč u dětí s družinou.</p><a class="read-more" href="/clanky/zs-chomutovska-kadan-stravne-zari-2026.html">Přečíst praktické informace →</a></div></article>'''

ARCHIVE_CARD = '''<article class="archive-item service" data-school-meals-card><div class="archive-visual" style="background:linear-gradient(135deg,#173044,#47778a 58%,#a9232b)"><strong>Nové ceny obědů</strong></div><div class="archive-body"><span class="archive-meta">29. července 2026 v 16:44 · Školy a praktické informace</span><h2>ZŠ Chomutovská od září zdraží obědy. Rodiče mají zvýšit limit inkasa</h2><p>Nové ceny budou 26 až 32 Kč. Bankovní limit je potřeba upravit od 15. srpna na 700 nebo 900 Kč.</p><a href="/clanky/zs-chomutovska-kadan-stravne-zari-2026.html">Přečíst praktické informace →</a></div></article>'''

RSS_ITEM = '''<item><title>ZŠ Chomutovská od září zdraží obědy. Rodiče mají zvýšit limit inkasa</title><link>https://nasekadan.cz/clanky/zs-chomutovska-kadan-stravne-zari-2026.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/zs-chomutovska-kadan-stravne-zari-2026.html</guid><pubDate>Wed, 29 Jul 2026 16:44:00 +0200</pubDate><description><![CDATA[Nové ceny budou 26 až 32 Kč. Rodiče mají od 15. srpna zvýšit limit inkasa na 700 nebo 900 Kč.]]></description></item>'''

NEWS_URL = '''<url><loc>https://nasekadan.cz/clanky/zs-chomutovska-kadan-stravne-zari-2026.html</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>2026-07-29T16:44:00+02:00</news:publication_date><news:title>ZŠ Chomutovská od září zdraží obědy</news:title></news:news></url>'''


def update_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\s*<article\b[^>]*data-school-meals-card[^>]*>.*?</article>\s*", "\n", text, flags=re.S)
    marker = '<div class="article-list">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam článků na titulní stránce")
    text = text.replace(marker, marker + "\n" + HOME_CARD, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\s*<article\b[^>]*data-school-meals-card[^>]*>.*?</article>\s*", "\n", text, flags=re.S)
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam archivu")
    text = text.replace(marker, marker + "\n" + ARCHIVE_CARD, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\s*<item>.*?<link>" + re.escape(ARTICLE_URL) + r"</link>.*?</item>\s*", "\n", text, flags=re.S)
    marker = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if marker not in text:
        raise RuntimeError("Nenalezen RSS marker")
    text = text.replace(marker, marker + "\n" + RSS_ITEM, 1)
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", "<lastBuildDate>Wed, 29 Jul 2026 16:44:00 +0200</lastBuildDate>", text, count=1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_sitemaps() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\s*<url><loc>" + re.escape(ARTICLE_URL) + r"</loc>.*?</url>\s*", "\n", text, flags=re.S)
    text = re.sub(r"(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+", r"\g<1>2026-07-29", text, count=1)
    text = re.sub(r"(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+", r"\g<1>2026-07-29", text, count=1)
    text = text.replace("</urlset>", f"  <url><loc>{ARTICLE_URL}</loc><lastmod>2026-07-29</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n</urlset>")
    path.write_text(text, encoding="utf-8", newline="\n")

    news = ROOT / "news-sitemap.xml"
    if news.exists():
        text = news.read_text(encoding="utf-8")
        text = re.sub(r"\s*<url>\s*<loc>" + re.escape(ARTICLE_URL) + r"</loc>.*?</url>\s*", "\n", text, flags=re.S)
        text = text.replace("</urlset>", "  " + NEWS_URL + "\n</urlset>")
        news.write_text(text, encoding="utf-8", newline="\n")


def update_manifest() -> None:
    path = ROOT / "production-content-manifest.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    items = [x for x in data.get("required_articles", []) if x.get("path") != f"clanky/{SLUG}.html"]
    items.insert(0, {"path": f"clanky/{SLUG}.html", "needle": "ZŠ Chomutovská od září zdraží obědy", "must_be_on_home": True, "must_be_in_archive": True})
    data["required_articles"] = items
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ARTICLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTICLE_PATH.write_text(ARTICLE, encoding="utf-8", newline="\n")
    update_home()
    update_archive()
    update_rss()
    update_sitemaps()
    update_manifest()
    print("Praktická zpráva o stravném ZŠ Chomutovská je připravena.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
