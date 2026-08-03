#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape, unescape
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = "klasterec-ochlazeni-zimni-stadion-kadan-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Klášterec otevřel zimní stadion lidem před vedrem. Mohla by se přidat i Kadaň?"
DESC = (
    "Klášterec nabízí lidem v horku posezení na zimním stadionu. "
    "Kadaňský stadion má od srpna denní provoz, město ale podobnou možnost zatím neoznámilo."
)
PUBLISHED = "2026-08-03T22:05:00+02:00"
PUBLISHED_HUMAN = "3. SRPNA 2026 · 22:05"
KADAN_SOURCE = "https://www.sportkadan.cz/arealy/zimni-stadion"
KLASTEREC_ARCHIVE_SOURCE = "https://www.klasterec.cz/kontakty/tiskove-zpravy/v-extremnich-vedrech-se-muzete-zchladit-na-zimnim-stadione-201cs.html"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def clean_html(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", value)).replace("\n", " ").strip()


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#09263b")
    draw = ImageDraw.Draw(image)
    for y in range(630):
        ratio = y / 629
        r = int(9 + (24 - 9) * ratio)
        g = int(38 + (106 - 38) * ratio)
        b = int(59 + (139 - 59) * ratio)
        draw.line((0, y, 1200, y), fill=(r, g, b))
    draw.rounded_rectangle((650, 70, 1135, 560), radius=38, fill="#dff6ff", outline="#ffffff", width=6)
    draw.rounded_rectangle((695, 150, 1090, 470), radius=145, fill="#f7fdff", outline="#7bc5e5", width=12)
    draw.arc((760, 190, 1025, 455), 180, 360, fill="#b82b39", width=15)
    draw.line((892, 175, 892, 465), fill="#b82b39", width=10)
    for x in (740, 810, 975, 1045):
        draw.ellipse((x, 250, x + 26, 276), fill="#1a5d83")
    draw.rounded_rectangle((58, 55, 350, 105), radius=25, fill="#b32632")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 62)
    medium = ImageFont.truetype(bold_path, 30)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 22)

    draw.text((82, 68), "NAŠE KADAŇ · PODNĚT", font=tiny, fill="white")
    lines = ["Klášterec nabízí", "ochlazení na zimáku.", "Přidá se Kadaň?"]
    y = 145
    for line in lines:
        draw.text((62, y), line, font=bold, fill="white")
        y += 78
    draw.text((66, 420), "Kadaňský stadion má od srpna provoz.", font=medium, fill="#dff6ff")
    draw.text((66, 466), "Volný vstup k posezení ale zatím oznámen nebyl.", font=small, fill="#dff6ff")
    draw.text((66, 568), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def article_page() -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": TITLE,
        "description": DESC,
        "datePublished": PUBLISHED,
        "dateModified": PUBLISHED,
        "author": {"@type": "Organization", "@id": "https://nasekadan.cz/#organization", "name": "Naše Kadaň", "url": "https://nasekadan.cz/o-webu/"},
        "publisher": {"@id": "https://nasekadan.cz/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
        "image": [SOCIAL_URL],
        "inLanguage": "cs-CZ",
        "isAccessibleForFree": True,
        "about": [
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Place", "name": "Klášterec nad Ohří"},
            {"@type": "Thing", "name": "ochlazení během veder"},
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Naše Kadaň", "item": "https://nasekadan.cz/"},
            {"@type": "ListItem", "position": 2, "name": "Články", "item": "https://nasekadan.cz/clanky/"},
            {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL},
        ],
    }
    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title>
<meta name="description" content="{escape(DESC)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE)}"><meta property="og:description" content="{escape(DESC)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE)}"><meta name="twitter:description" content="{escape(DESC)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626"><link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #0b385544}}.fact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:28px 0}}.fact{{background:#edf7fb;border:1px solid #cce1ea;border-radius:17px;padding:20px}}.fact strong{{display:block;color:#145a7a;font:900 24px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.clarity{{background:#fff5df;border:1px solid #ead0a1;border-left:7px solid #c57b18;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.clarity strong{{display:block;font:900 24px Georgia,serif;color:#74440c;margin-bottom:6px}}.proposal{{background:#eef6f8;border-radius:20px;padding:25px;margin:30px 0}}.proposal h2{{margin-top:0}}.poll{{margin:44px 0 22px;padding:28px;border-radius:22px;background:linear-gradient(145deg,#102f43,#176d8d);color:#fff}}.poll .eyebrow{{font-size:12px;font-weight:900;letter-spacing:.09em;color:#ffe298}}.poll h2{{color:#fff;margin:7px 0 10px}}.poll p{{font-size:16px;color:#e8f7fb}}.poll-option{{display:block;width:100%;background:#fff;color:#14232d;padding:13px 15px;border:1px solid #cfd9dd;border-radius:13px;margin:9px 0;font-weight:800;text-align:left;cursor:pointer}}.poll-option:hover,.poll-option:focus{{background:#fff7f7;border-color:#a9232b;outline:none}}.poll-option:disabled{{cursor:default;opacity:.75}}.poll-message{{display:none!important;margin-top:16px!important;padding:13px 15px;border-radius:12px;background:#eaf4ed!important;color:#245d36!important;font-weight:800}}.poll-message.show{{display:block!important}}.sources{{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}}.sources h2{{margin-top:0}}.sources li,.sources p{{font-size:14px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:900 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:700px){{.article{{padding:27px 21px}}.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.fact-grid{{grid-template-columns:1fr}}}}
</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="tag">KADAŇ · KLÁŠTEREC NAD OHŘÍ · VEDRO · PODNĚT · {PUBLISHED_HUMAN}</p><h1>{escape(TITLE)}</h1><p class="leadtext"><strong>{escape(DESC)}</strong></p>
<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika se zimním stadionem a otázkou, zda se k nabídce ochlazení přidá Kadaň">
<p>Chomutovský deník v pondělí 3. srpna informoval, že Klášterec nad Ohří umožňuje lidem během horkých dnů přijít posedět do chladnějšího prostředí zimního stadionu. Nabídka míří zejména na obyvatele přehřátých bytů, seniory a lidi, kterým vysoké teploty působí obtíže.</p>
<p>Podle zveřejněné informace mohou lidé přijít během dne, kdy se na stadionu zároveň konají tréninky krasobruslení nebo ledního hokeje. Nejde tedy o veřejné bruslení, ale o možnost na určitou dobu uniknout z rozpáleného bytu a posedět v chladnější budově.</p>
<h2>Stejná otázka se nabízí v Kadani</h2>
<p>Kadaňský zimní stadion zahajuje sezonu právě v srpnu. Oficiální web Sportovních zařízení Kadaň uvádí pro období od srpna do března každodenní provoz od 8 do 21 hodin. Led a potřebná technologie jsou tedy v sezonním provozu.</p>
<div class="fact-grid"><div class="fact"><strong>srpen–březen</strong><span>oficiálně uváděná sezona kadaňského zimního stadionu</span></div><div class="fact"><strong>8:00–21:00</strong><span>uvedená denní provozní doba v tomto období</span></div><div class="fact"><strong>zatím ne</strong><span>veřejné oznámení, že lze přijít pouze posedět a ochladit se</span></div></div>
<div class="clarity"><strong>Provozní doba neznamená automaticky volný vstup</strong><p>Údaj na webu potvrzuje provoz stadionu, nikoli možnost přijít bez domluvy na tribunu. Dokud město nebo provozovatel podobnou nabídku výslovně neoznámí, nelze lidem radit, aby na stadion jednoduše dorazili.</p></div>
<p>Příklad ze sousedního města ale ukazuje konkrétní možnost, kterou by Kadaň mohla prověřit. Nemuselo by jít o otevření celého areálu. Stačilo by určit vyhrazený vstup, část tribuny, časové rozmezí a pravidla tak, aby posezení veřejnosti nenarušovalo tréninky ani běžný provoz.</p>
<div class="proposal"><h2>Co by bylo potřeba upřesnit</h2><ul><li>ve které dny a hodiny mohou lidé přijít,</li><li>kterým vchodem a do jaké části stadionu,</li><li>zda bude vstup zdarma,</li><li>zda bude místo dostupné také lidem s omezenou pohyblivostí,</li><li>jak bude zajištěn bezpečný souběh s tréninky.</li></ul></div>
<h2>V Klášterci už podobný nápad fungoval dříve</h2>
<p>Nejde o úplně nový klášterecký nápad. V oficiálním archivu města je dohledatelné stejné opatření už z mimořádně horkého srpna 2015. Tehdy město uvádělo, že lidé mohou na stadion přijít během dne, posedět si s knihou nebo novinami a vstup mají zdarma.</p>
<p><strong>Pro Kadaň je proto otázka jednoduchá: může během nejteplejších dnů nabídnout podobné chladné místo také svým obyvatelům?</strong></p>
<section class="poll" data-poll-id="ochlazeni-zimni-stadion-kadan-2026"><span class="eyebrow">ANKETA NAŠE KADAŇ</span><h2>Měla by Kadaň během veder zpřístupnit část zimního stadionu k ochlazení?</h2><p>Vyberte jednu možnost. Průběžné výsledky se zobrazí přímo pod hlasováním.</p><div class="poll-options"><button class="poll-option" type="button" data-poll-vote="ano-vsichni">Ano, pro všechny během nejteplejších dnů.</button><button class="poll-option" type="button" data-poll-vote="ano-prioritne">Ano, hlavně pro seniory a nemocné.</button><button class="poll-option" type="button" data-poll-vote="jine-prostory">Raději by město mělo nabídnout jiné chladné prostory.</button><button class="poll-option" type="button" data-poll-vote="ne">Ne, není to potřeba.</button></div><p class="poll-message" role="status" aria-live="polite"></p></section>
<div class="sources"><h2>Zdroje a upřesnění</h2><ul><li>Chomutovský deník: „Teploty šplhají vzhůru. Klášterec nabízí úlevu na zimním stadionu“, publikováno 3. 8. 2026 ve 14:40.</li><li><a href="{KADAN_SOURCE}" rel="noopener">Sportovní zařízení Kadaň: Zimní stadion – sezona a provozní doba</a>.</li><li><a href="{KLASTEREC_ARCHIVE_SOURCE}" rel="noopener">Město Klášterec nad Ohří: archivní nabídka ochlazení na stadionu z roku 2015</a>.</li></ul><p>Redakční text rozlišuje mezi doloženým provozem kadaňského stadionu a návrhem na jeho možné zpřístupnění. Kadaň zatím takovou službu veřejně nepotvrdila.</p></div></article>
<aside class="sticky"><div class="sidebox"><h3>Co je ověřeno</h3><ul><li>stadion v Kadani má od srpna sezonu,</li><li>uvádí provoz 8:00–21:00,</li><li>Klášterec nabízí ochlazení veřejnosti,</li><li>Kadaň stejnou nabídku zatím neoznámila.</li></ul></div><div class="sidebox"><h3>Adresa stadionu</h3><p><strong>U Stadionu 2028, Kadaň</strong><br>kontakt stadionu: 777 805 290</p></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body></html>'''


def update_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<section class="wrap hero"[^>]*>.*?</section>', text, flags=re.S)
    if not match:
        raise RuntimeError("Na titulce nebyla nalezena hlavní sekce hero.")
    old = match.group(0)
    href_match = re.search(r'data-latest-article-href="([^"]+)"', old)
    h1_match = re.search(r'<h1>(.*?)</h1>', old, flags=re.S)
    desc_match = re.search(r'<div class="copy">.*?<p>(.*?)</p>', old, flags=re.S)
    old_href = href_match.group(1) if href_match else "/clanky/"
    old_title = clean_html(h1_match.group(1)) if h1_match else "Další aktuální články"
    old_desc = clean_html(desc_match.group(1)) if desc_match else "Přečtěte si další zprávy a ověřené informace z Kadaně a okolí."
    if old_href == REL:
        old_href = "/clanky/"
        old_title = "Další aktuální články"
    hero = f'''<section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{REL}">
    <article class="lead"><div class="photo" style="background-image:linear-gradient(180deg,transparent,#08263dbb),url('{SOCIAL_REL}');background-size:cover;background-position:center"><span>KADAŇ · KLÁŠTEREC · VEDRO · PODNĚT · {PUBLISHED_HUMAN}</span><strong>3. 8. 2026</strong></div><div class="copy"><small>KADAŇ · KLÁŠTEREC · VEDRO · {PUBLISHED_HUMAN}</small><h1>{escape(TITLE)}</h1><p>{escape(DESC)}</p><a class="btn" href="{REL}">Přečíst nejnovější článek →</a></div></article>
    <aside class="current-aside"><p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p><h2>{escape(old_title)}</h2><p>{escape(old_desc)}</p><a class="aside-button" href="{escape(old_href)}">Přečíst článek →</a><div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div></aside>
  </section>'''
    text = text[:match.start()] + hero + text[match.end():]
    write(path, text)


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    if f'data-auto-article="{SLUG}"' not in text:
        card = f'''\n    <article class="article-card regional" data-auto-article="{SLUG}"><div class="visual" style="background-image:linear-gradient(180deg,transparent,#08263dcc),url('{SOCIAL_REL}');background-size:cover;background-position:center"><strong>{escape(TITLE)}</strong></div><div class="article-body"><span class="meta">3. 8. 2026 · 22:05 · KADAŇ · KLÁŠTEREC · VEDRO · PODNĚT</span><h3>{escape(TITLE)}</h3><p>{escape(DESC)}</p><a class="read-more" href="{REL}">Přečíst článek →</a></div></article>\n'''
        text = text.replace('<div class="archive-list">', '<div class="archive-list">' + card, 1)

    pattern = re.compile(r'(<script type="application/ld\+json">\s*)(\{.*?\})(\s*</script>)', re.S)
    for match in list(pattern.finditer(text)):
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph") if isinstance(data, dict) else None
        if not isinstance(graph, list):
            continue
        itemlist = next((node for node in graph if isinstance(node, dict) and node.get("@type") == "ItemList"), None)
        if not itemlist:
            continue
        items = itemlist.setdefault("itemListElement", [])
        if not any(isinstance(item, dict) and item.get("url") == URL for item in items):
            items.insert(0, {"@type": "ListItem", "position": 1, "url": URL, "name": TITLE})
        for pos, item in enumerate(items, 1):
            if isinstance(item, dict):
                item["position"] = pos
        itemlist["numberOfItems"] = len(items)
        replacement = match.group(1) + json.dumps(data, ensure_ascii=False, indent=2) + match.group(3)
        text = text[:match.start()] + replacement + text[match.end():]
        break
    write(path, text)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    rss_date = format_datetime(datetime.fromisoformat(PUBLISHED))
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{rss_date}</lastBuildDate>', text, count=1)
    if URL not in text:
        item = f'''<item><title>{escape(TITLE)}</title><description><![CDATA[{DESC}]]></description><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{rss_date}</pubDate><category>Kadaň</category><category>Klášterec nad Ohří</category><category>Vedro</category><category>Podnět</category><szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>\n    '''
        text = text.replace('<item>', item + '<item>', 1)
    write(path, text)


def update_sitemaps() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    if URL not in text:
        text = text.replace('</urlset>', f'  <url><loc>{URL}</loc></url>\n</urlset>', 1)
    write(sitemap, text)

    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    if URL not in text:
        node = f'''  <url>\n    <loc>{URL}</loc>\n    <news:news>\n      <news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication>\n      <news:publication_date>{PUBLISHED}</news:publication_date>\n      <news:title>{escape(TITLE)}</news:title>\n    </news:news>\n  </url>\n'''
        if '<url>' in text:
            text = text.replace('  <url>', node + '  <url>', 1)
        else:
            text = text.replace('</urlset>', node + '</urlset>', 1)
    write(news, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        entry = f'- [{TITLE}]({URL})\n  {DESC}\n'
        marker = '## Nejnovější vlastní články\n\n'
        text = text.replace(marker, marker + entry, 1) if marker in text else entry + '\n' + text
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    if not any(isinstance(item, dict) and item.get("url") == URL for item in articles):
        try:
            source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        except Exception:
            source_commit = ""
        articles.insert(0, {
            "title": TITLE,
            "h1": TITLE,
            "url": URL,
            "published_at": PUBLISHED,
            "modified_at": PUBLISHED,
            "persons": [],
            "organizations": ["Město Kadaň", "Sportovní zařízení Kadaň", "Město Klášterec nad Ohří"],
            "places": ["Kadaň", "Klášterec nad Ohří"],
            "cases": ["Možnost ochlazení veřejnosti na zimním stadionu"],
            "topics": ["Vedro", "Veřejná služba", "Zimní stadion", "Podnět"],
            "fingerprint": sha256(URL.encode()).hexdigest()[:24],
            "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
            "source_path": f"clanky/{SLUG}.html",
            "publication_status": "published",
            "source_commit": source_commit,
        })
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation["homepage_count"] = sum(1 for item in articles if isinstance(item, dict) and item.get("status", {}).get("homepage"))
    validation["archive_count"] = sum(1 for item in articles if isinstance(item, dict) and item.get("status", {}).get("archive"))
    validation["rss_count"] = sum(1 for item in articles if isinstance(item, dict) and item.get("status", {}).get("rss"))
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    make_social()
    write(ARTICLE, article_page())
    update_home()
    update_archive()
    update_rss()
    update_sitemaps()
    update_llms()
    update_registry()
    weather_script = ROOT / "scripts" / "ensure_weather_loader.py"
    if weather_script.exists():
        subprocess.run(["python3", str(weather_script)], cwd=ROOT, check=True)
    required = [ARTICLE, SOCIAL, ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "llms.txt"]
    for path in required:
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Chybí výstup {path}.")
    article = ARTICLE.read_text(encoding="utf-8")
    if f'<h1>{TITLE}</h1>' not in article or 'data-poll-id="ochlazeni-zimni-stadion-kadan-2026"' not in article:
        raise RuntimeError("Článek nebo anketa nejsou kompletní.")
    for path in [ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml"]:
        if REL not in path.read_text(encoding="utf-8", errors="replace") and URL not in path.read_text(encoding="utf-8", errors="replace"):
            raise RuntimeError(f"V souboru {path} chybí článek.")
    if '/pocasi.js' not in (ROOT / "index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Publikace by odstranila loader počasí.")
    print(f"Připraveno k publikaci: {URL}")


if __name__ == "__main__":
    main()
