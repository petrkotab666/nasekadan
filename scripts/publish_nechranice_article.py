#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'hasici-kadan-vycvik-zachrana-voda-nechranice'
HREF = f'/clanky/{SLUG}.html'
URL = f'https://nasekadan.cz{HREF}'
TITLE = 'Kadaňští hasiči cvičili na Nechranicích záchranu lidí z vody'
DESC = 'Na Nechranické přehradě proběhl společný výcvik hasičů, policistů a vodních záchranářů zaměřený na záchranu osob z vodní hladiny.'
PUBLISHED = '2026-07-27T22:35:00+02:00'


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def make_article() -> None:
    article = f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} | Naše Kadaň</title><meta name="description" content="{DESC}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}"><meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{TITLE}"><meta property="og:description" content="{DESC}"><meta property="og:url" content="{URL}"><meta property="og:image" content="https://nasekadan.cz/social-card.png"><meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"NewsArticle","headline":"{TITLE}","description":"{DESC}","datePublished":"{PUBLISHED}","dateModified":"{PUBLISHED}","author":{{"@type":"Organization","name":"Naše Kadaň"}},"publisher":{{"@type":"Organization","name":"Naše Kadaň"}},"mainEntityOfPage":"{URL}","inLanguage":"cs-CZ"}}</script>
<style>.article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}}.article h1{{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}}.article h2{{font:800 34px/1.15 Georgia,serif;margin:52px 0 14px}}.article p{{font-size:18px}}.article .leadtext{{font-size:23px;color:#465862;line-height:1.55}}.hero-visual{{min-height:350px;border-radius:24px;background:linear-gradient(135deg,#12313f,#28617a 52%,#a56b24);display:flex;align-items:flex-end;padding:30px;color:#fff;box-shadow:var(--shadow);margin:30px 0}}.hero-visual strong{{font:800 31px Georgia,serif;max-width:650px}}.source-list{{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}</style></head>
<body><header><div class="wrap head"><a class="logo" href="../index.html"><span class="logo-mark"></span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="../index.html">Úvod</a><a href="../index.html#akce">Akce</a><a href="../pruvodce/">Průvodce</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="tag">HASIČI · BEZPEČNOST · NECHRANICE</p><h1>{TITLE}</h1><p class="leadtext"><strong>Na Nechranické přehradě proběhl každoroční výcvik zaměřený na záchranu osob z vodní plochy. Hasiči si procvičili vytažení člověka z vody do člunu, pomoc lidem po pádu z plavidla, součinnost několika posádek i správné používání záchranného vybavení.</strong></p><div class="hero-visual"><strong>Společný nácvik prověřil rychlost, komunikaci i bezpečnou součinnost zasahujících posádek.</strong></div>
<p>Výcvik se uskutečnil 25. července na vodním díle Nechranice. Zapojili se do něj Hasiči královského města Kadaň společně s jednotkou dobrovolných hasičů z Libědic, profesionálními hasiči ze stanice Žatec, Vodní záchrannou službou Nechranice a Policií České republiky.</p>
<p>Cílem nebylo pouze procvičit samotné vytažení člověka z vody. Účastníci se zaměřili také na spolupráci několika člunů, koordinaci jednotlivých posádek a postupy, které mohou při skutečné události rozhodovat o rychlosti i bezpečnosti zásahu.</p>
<h2>Záchrana do člunu i pomoc lidem po pádu do vody</h2><p>Součástí výcviku bylo vytažení zachraňované osoby z vody do člunu, pomoc lidem po pádu z plavidla, spolupráce několika člunů současně, práce se záchrannými prostředky a koordinace hasičů, policistů a vodních záchranářů.</p>
<p>Právě společný nácvik je důležitý proto, že při zásahu na rozsáhlé vodní ploše může být současně nasazeno více jednotek a různých složek integrovaného záchranného systému.</p>
<h2>Výcvik, který může rozhodovat o životě</h2><p>Zásah na vodě se výrazně liší od běžného zásahu na souši. Posádka musí správně ovládat člun, rychle se přiblížit k člověku ve vodě a přitom neohrozit zachraňovaného ani samotné zasahující.</p>
<p>Společný výcvik proto není formalita. Pomáhá sjednotit postupy, prověřit komunikaci a připravit posádky na situace, kdy o výsledku zásahu rozhodují minuty.</p>
<h2>Poděkování všem zapojeným</h2><p>Kadaňští hasiči poděkovali JSDH Libědice, HZS Ústeckého kraje – stanici Žatec, Vodní záchranné službě Nechranice a Policii České republiky.</p>
<p><strong>Nechranická přehrada je během léta vyhledávaným místem pro koupání, vodní sporty i rybaření. Právě proto je důležité, aby hasiči, policisté a vodní záchranáři byli připraveni rychle a společně zasáhnout, kdykoliv se někdo na vodě ocitne v nebezpečí.</strong></p>
<div class="source-list"><strong>Zdroj</strong><p>Veřejný příspěvek Hasičů královského města Kadaň o výcviku záchrany osob na VD Nechranice.</p></div></article><aside class="sticky"><div class="sidebox"><h3>Hlavní body</h3><p>Výcvik na vodní hladině, více člunů, spolupráce hasičů, policie a vodních záchranářů.</p></div></aside></main><script src="/site.js" defer></script></body></html>'''
    write(ROOT / 'clanky' / f'{SLUG}.html', article)


def update_home() -> None:
    p = ROOT / 'index.html'; text = p.read_text(encoding='utf-8')
    hero = f'''<article class="lead" data-nechranice-hero><div class="photo" style="background:linear-gradient(135deg,#12313f,#28617a 58%,#a56b24)"><span>HASIČI</span><strong>Nechranice</strong></div><div class="copy"><small>BEZPEČNOST · 27. 07. 2026 · 22:35</small><h1>Kadaňští hasiči cvičili záchranu lidí z vody</h1><p>Na Nechranické přehradě procvičili zásah z člunů společně s dalšími složkami.</p><a class="btn" href="{HREF}">Přečíst celý článek →</a></div></article>'''
    text = re.sub(r'<article class="lead"[^>]*>.*?</article>', hero, text, count=1, flags=re.S)
    card = f'''<article class="article-card transport" data-nechranice-card><div class="visual" style="background:linear-gradient(135deg,#12313f,#28617a 58%,#a56b24)"><strong>Záchrana na vodě</strong></div><div class="article-body"><span class="meta">27. 7. 2026 · 22:35 · Hasiči</span><h3>Kadaňští hasiči cvičili na Nechranicích</h3><p>Společný výcvik prověřil práci člunů i součinnost záchranných složek.</p><a class="read-more" href="{HREF}">Přečíst článek →</a></div></article>'''
    if 'data-nechranice-card' not in text:
        text = text.replace('<div class="article-list">', '<div class="article-list">' + card, 1)
    write(p, text)


def update_archive() -> None:
    p = ROOT / 'clanky' / 'index.html'; text = p.read_text(encoding='utf-8')
    item = f'''<article class="archive-item transport" data-nechranice-card><div class="archive-visual" style="background:linear-gradient(135deg,#12313f,#28617a 58%,#a56b24)"><strong>Záchrana na vodě</strong></div><div class="archive-body"><span class="archive-meta">27. července 2026 v 22:35 · Hasiči</span><h2>{TITLE}</h2><p>{DESC}</p><a href="{HREF}">Přečíst celý článek →</a></div></article>'''
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if 'data-nechranice-card' not in text:
        text = text.replace(marker, marker + item, 1)
    write(p, text)


def update_feeds() -> None:
    p = ROOT / 'rss.xml'; text = p.read_text(encoding='utf-8')
    if URL not in text:
        node = f'''    <item><title>{TITLE}</title><description><![CDATA[{DESC}]]></description><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>Mon, 27 Jul 2026 22:35:00 +0200</pubDate><category>Hasiči</category><category>Bezpečnost</category></item>'''
        text = text.replace('    <item>', node + '\n\n    <item>', 1)
    write(p, text)
    for name in ('sitemap.xml', 'news-sitemap.xml'):
        p = ROOT / name
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        if URL not in text:
            if name == 'news-sitemap.xml':
                node = f'''  <url><loc>{URL}</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>{PUBLISHED}</news:publication_date><news:title>{TITLE}</news:title></news:news></url>\n'''
            else:
                node = f'''  <url><loc>{URL}</loc><lastmod>2026-07-27</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n'''
            text = text.replace('</urlset>', node + '</urlset>', 1)
        write(p, text)


if __name__ == '__main__':
    make_article(); update_home(); update_archive(); update_feeds()
    print('Článek o výcviku na Nechranicích připraven.')
