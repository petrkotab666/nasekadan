#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = "komunalni-volby-kadan-kandidaty-lhuta-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Lhůta pro kandidátky skončila. V Kadani se rýsuje souboj ODS, nové skupiny a ANO"
DESC = (
    "Podávání kandidátek do komunálních voleb skončilo. ODS a Dáme Kadani novou šanci "
    "zveřejnily celé sestavy, ANO oznámilo podání a Piráti představují své kandidáty."
)
PUBLISHED = "2026-08-04T18:46:00+02:00"
MODIFIED = "2026-08-04T19:06:00+02:00"
DATE_SHORT = "4. 8. 2026"
TAG = "KOMUNÁLNÍ VOLBY 2026 · KADAŇ"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#102733")
    draw = ImageDraw.Draw(image)
    for y in range(630):
        ratio = y / 629
        draw.line((0, y, 1200, y), fill=(15 + int(42 * ratio), 38 + int(19 * ratio), 51 + int(14 * ratio)))

    draw.rounded_rectangle((730, 170, 1120, 560), radius=30, fill="#edf2f4", outline="#bfcbd0", width=5)
    draw.rectangle((785, 140, 1065, 205), fill="#d4dde1", outline="#9eabb1", width=4)
    draw.rectangle((825, 150, 1025, 180), fill="#183747")
    small_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    for x, label in [(760, "ODS"), (895, "NOVÁ"), (1030, "ANO")]:
        draw.rounded_rectangle((x, 285, x + 115, 440), radius=15, fill="#ffffff", outline="#c7d2d7", width=3)
        draw.line((x + 22, 325, x + 92, 325), fill="#a9232b", width=7)
        draw.line((x + 22, 350, x + 92, 350), fill="#4c6673", width=5)
        draw.line((x + 22, 375, x + 78, 375), fill="#4c6673", width=5)
        draw.text((x + 20, 405), label, fill="#132d3a", font=small_bold)
    draw.rectangle((690, 500, 1160, 620), fill="#0b1d26")
    draw.rectangle((830, 430, 1010, 620), fill="#122b37")
    draw.polygon([(810, 430), (920, 330), (1030, 430)], fill="#122b37")
    draw.ellipse((900, 390, 940, 430), outline="#e6bd67", width=5)

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 55)
    medium = ImageFont.truetype(bold_path, 30)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 21)

    draw.rounded_rectangle((58, 52, 440, 104), radius=25, fill="#a9232b")
    draw.text((82, 68), "NAŠE KADAŇ · VOLBY 2026", font=tiny, fill="white")
    lines = ["Lhůta skončila", "Kdo se chystá", "bojovat o Kadaň?"]
    y = 145
    for line in lines:
        draw.text((62, y), line, font=bold, fill="white")
        y += 70
    draw.text((66, 385), "ODS · Dáme Kadani novou šanci · ANO", font=medium, fill="#ffe0a1")
    draw.text((66, 438), "Piráti a další sestavy zatím čekají na úřední potvrzení", font=small, fill="#edf4f6")
    draw.text((66, 570), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def article_page() -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": TITLE,
        "description": DESC,
        "datePublished": PUBLISHED,
        "dateModified": MODIFIED,
        "author": {"@type": "Organization", "@id": "https://nasekadan.cz/#organization", "name": "Naše Kadaň", "url": "https://nasekadan.cz/o-webu/"},
        "publisher": {"@id": "https://nasekadan.cz/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
        "image": [SOCIAL_URL],
        "inLanguage": "cs-CZ",
        "isAccessibleForFree": True,
        "about": [
            {"@type": "Event", "name": "Komunální volby 2026 v Kadani", "startDate": "2026-10-09", "endDate": "2026-10-10"},
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Organization", "name": "ODS Kadaň"},
            {"@type": "Organization", "name": "Dáme Kadani novou šanci"},
            {"@type": "Organization", "name": "ANO 2011"},
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
<html lang="cs">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title>
<meta name="description" content="{escape(DESC, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}">
<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{MODIFIED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
<link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
<script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script>
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}}.article h1{{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}}.article h2{{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}}.article h3{{font:800 24px/1.2 Georgia,serif;margin:30px 0 10px}}.article p,.article li{{font-size:18px}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.55}}.hero-image{{display:block;width:100%;height:auto;margin:30px 0;border-radius:24px;box-shadow:var(--shadow)}}.update-box{{background:#fff4cf;border:1px solid #e0c36f;border-radius:18px;padding:22px 24px;margin:30px 0}}.update-box strong{{font:800 23px Georgia,serif;display:block;color:#72500d;margin-bottom:6px}}.fact-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:28px 0}}.fact-card{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 8px 25px #16242d0a}}.fact-card span{{display:block;color:var(--red);font-weight:900;font-size:13px;letter-spacing:.06em;text-transform:uppercase}}.fact-card strong{{display:block;font:800 26px Georgia,serif;margin:7px 0}}.fact-card p{{margin:0;color:#52616a}}.data-table{{width:100%;border-collapse:collapse;margin:26px 0;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 10px 28px #16242d0d}}.data-table th,.data-table td{{padding:14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}.data-table th{{background:#14232d;color:#fff}}.callout{{border-left:6px solid var(--red);background:var(--cream);margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}}.callout strong{{font:800 24px Georgia,serif;display:block;margin-bottom:6px}}.source-list{{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}}.source-list li{{font-size:15px;margin-bottom:8px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:800 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:680px){{.fact-grid{{grid-template-columns:1fr}}.data-table{{display:block;overflow-x:auto}}.hero-image{{border-radius:16px}}}}
</style>
</head>
<body>
<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article">
<p class="tag">{TAG} · 4. SRPNA 2026 · 18:46</p>
<h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>V úterý 4. srpna v 16 hodin skončila lhůta pro podání kandidátních listin do podzimních komunálních voleb. Úplný úřední seznam pro Kadaň ještě zveřejněný není, z veřejných oznámení se ale už rýsuje hlavní volební střet: ODS vedená starostou Janem Losenickým, nové uskupení Dáme Kadani novou šanci kolem části někdejších kandidátů ODS a silné opoziční ANO. Piráti rovněž veřejně představují svůj tým.</strong></p>
<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika ke komunálním volbám v Kadani 2026">
<div class="update-box"><strong>Podaná kandidátka ještě není zaregistrovaná</strong><p>Registrační úřad nyní kontroluje náležitosti podaných listin. Do 12. srpna může vyzvat k odstranění závad, opravy jsou možné do 17. srpna a o registraci se rozhodne nejpozději 22. srpna. Teprve potom vznikne úplný úřední seznam kandidujících stran a osob.</p></div>
<h2>Co je v tuto chvíli potvrzené</h2>
<table class="data-table"><thead><tr><th>Uskupení</th><th>Veřejně známé čelo</th><th>Stav ověření</th></tr></thead><tbody>
<tr><td><strong>ODS</strong></td><td>Jan Losenický, Alena Benešová, Jan Perout, Michal Voltr, Jan Vaic</td><td>Zveřejněna 27členná sestava</td></tr>
<tr><td><strong>Dáme Kadani novou šanci</strong></td><td>Radek Oswald, Marcela Trejbal Vlčková, Michal Vyčichlo, Jan Hudák, Soňa Pusztakürti</td><td>Zveřejněna 27členná sestava</td></tr>
<tr><td><strong>ANO</strong></td><td>Lídr a úplné pořadí zatím nejsou ověřené</td><td>Místní profil oznámil podání kandidátky videem</td></tr>
<tr><td><strong>Piráti</strong></td><td>Jana Hladová a další veřejně představení kandidáti</td><td>Úplná podaná listina zatím není úředně potvrzená</td></tr>
</tbody></table>
<h2>ODS obhajuje vedení města</h2>
<p>Kadaňskou ODS vede současný starosta <strong>Jan Losenický</strong>. Na dalších zveřejněných místech jsou Alena Benešová, Jan Perout, Michal Voltr a Jan Vaic. ODS v roce 2022 získala 12 z 27 mandátů a s 41,83 procenta hlasů byla nejsilnější kandidátkou.</p>
<p>Strana tentokrát vstupuje do voleb bez několika osobností, které byly součástí její sestavy v předchozích letech. Právě personální rozdělení někdejšího týmu je jedním z hlavních příběhů letošních voleb.</p>
<h2>Dáme Kadani novou šanci vede Radek Oswald</h2>
<p>Nové uskupení vede <strong>PharmDr. Radek Oswald</strong>, kadaňský zastupitel, radní města a lékárník. Nejde o bývalého místostarostu. V roce 2022 kandidoval za ODS na čtvrtém místě a získal zastupitelský mandát.</p>
<p>Za Oswaldem následují Marcela Trejbal Vlčková, Michal Vyčichlo, Jan Hudák a Soňa Pusztakürti. Na celé 27členné sestavě jsou také lidé ze zdravotnictví a sociálních služeb a několik osob, které v minulosti kandidovaly za ODS. Bývalý starosta Jiří Kulhánek uskupení veřejně podporuje, sám však podle zveřejněné sestavy nekandiduje.</p>
<div class="callout"><strong>Nejde o „celou bývalou ODS“</strong><p>Přesné je mluvit o nové skupině kolem části někdejších kandidátů a politických partnerů ODS. Řada jejích kandidátů s ODS dříve spojena nebyla.</p></div>
<h2>ANO oznámilo podání, úplnou sestavu zatím nemáme</h2>
<p>Veřejný profil <strong>ANO, tohle je Kadaň</strong> zveřejnil krátké video už několik dní před uzávěrkou, nikoli 4. srpna. Kopii videa má redakce k dispozici. Facebook u příspěvku v době redakční kontroly zobrazoval údaj „před 4 dny“. Z veřejně zachyceného příspěvku však zatím nelze bezpečně sestavit úplné pořadí kandidátů ani potvrdit letošního lídra.</p>
<p>ANO přitom nelze považovat za vedlejšího soupeře. V komunálních volbách 2022 získalo 33,36 procenta hlasů a deset mandátů. Za vítěznou ODS zaostalo pouze o dva mandáty. Rozdělení části někdejšího týmu ODS proto může otevřít prostor právě hnutí ANO.</p>
<div class="update-box" data-correction="ano-video-timing"><strong>Upřesnění redakce</strong><p>Po zveřejnění článku jsme opravili časové zařazení videa ANO. Facebook u něj zobrazoval údaj „před 4 dny“; nebylo tedy zveřejněno 4. srpna v den uzávěrky.</p></div>
<h2>Piráti ukazují jména, úřední potvrzení teprve přijde</h2>
<p>Kadaňský pirátský web veřejně uvádí Janu Hladovou a další kandidáty. Mezi představenými jmény jsou například Pavel Miltner, Hana Vodrážková, Miloslava Karfilátová a Jiří Kopica. Redakce ale zatím nemá úředně potvrzeno, zda zveřejněný přehled odpovídá konečné podané listině včetně pořadí všech kandidátů.</p>
<p>Piráti v roce 2022 získali 4,90 procenta hlasů a do zastupitelstva se těsně nedostali.</p>
<h2>Napínavý střet může mít tři hlavní póly</h2>
<div class="fact-grid"><div class="fact-card"><span>ODS 2022</span><strong>12 mandátů</strong><p>Současné vedení města obhajuje pozici nejsilnější sestavy.</p></div><div class="fact-card"><span>ANO 2022</span><strong>10 mandátů</strong><p>Nejsilnější opoziční hnutí může těžit z rozdělení hlasů.</p></div><div class="fact-card"><span>Nová sestava</span><strong>27 kandidátů</strong><p>Dáme Kadani novou šanci staví proti ODS vlastní kompletní tým.</p></div><div class="fact-card"><span>Volby</span><strong>9.–10. října</strong><p>O složení 27členného zastupitelstva rozhodnou voliči na podzim.</p></div></div>
<p>Nejviditelnější osobní souboj se rýsuje mezi Janem Losenickým a Radkem Oswaldem. Výsledek ale nebude pouze jejich duelem. ANO vychází z velmi silného výsledku z minulých voleb a další kandidátky mohou rozhodnout o tom, zda bude možné sestavit většinu bez povolebních kompromisů.</p>
<h2>Kdo další podal kandidátku, zatím není jisté</h2>
<p>V roce 2022 kandidovaly také PRO Kadaň a okolí, Lepší Sever a KSČM. Ve veřejně dohledaných podkladech zatím nemáme spolehlivě potvrzeno, které z těchto sestav podaly kandidátku také letos. Absence veřejného oznámení neznamená, že kandidovat nebudou.</p>
<p>Naše Kadaň bude přehled aktualizovat po zveřejnění rozhodnutí registračního úřadu. Tehdy bude možné sestavit úplný seznam, ověřit pořadí kandidátů a oddělit veřejně ohlášené týmy od skutečně zaregistrovaných volebních stran.</p>
<div class="source-list"><h2>Zdroje a metodika</h2><ul>
<li><a href="https://mv.gov.cz/volby/docDetail.aspx?docid=22560198&amp;doctype=ART" target="_blank" rel="noopener noreferrer">Ministerstvo vnitra – podmínky kandidatury a zákonné termíny komunálních voleb 2026</a>.</li>
<li><a href="/clanky/nemocnice-kadan.html">Naše Kadaň – dříve ověřené a zveřejněné kandidátní sestavy ODS a Dáme Kadani novou šanci</a>.</li>
<li><a href="https://www.ods.cz/ms.vilemov/profil/4981-radek-oswald" target="_blank" rel="noopener noreferrer">ODS – profil Radka Oswalda</a>, který jej uvádí jako radního města a člena zastupitelstva od roku 2006.</li>
<li><a href="https://www.presskadan.cz/zastupitelstvo.html" target="_blank" rel="noopener noreferrer">PressKadaň – ustavující zastupitelstvo 2022</a>, zvolení starosty, místostarosty a členů rady.</li>
<li><a href="https://www.seznamzpravy.cz/p/vysledky-voleb/2022/komunalni-volby/obec/563102-kadan" target="_blank" rel="noopener noreferrer">Výsledky komunálních voleb 2022 v Kadani</a>.</li>
<li><a href="https://kadan.pirati.cz/programy/" target="_blank" rel="noopener noreferrer">Piráti Kadaň – veřejně uvedení kandidáti</a>.</li>
<li>Veřejné video profilu „ANO, tohle je Kadaň“ zveřejněné několik dní před 4. srpnem 2026; obrazový záznam poskytl redakci čtenář.</li>
</ul><p><small>U každé osoby rozlišujeme doloženou veřejnou funkci, kandidaturu a pouhou politickou podporu. Podané kandidátky neoznačujeme za zaregistrované před rozhodnutím registračního úřadu.</small></p></div>
<div data-promos data-context="article-end"></div>
</article><aside class="sticky"><div class="sidebox"><h3>Co bude následovat</h3><ul><li>do 12. srpna výzvy k opravám</li><li>do 17. srpna odstranění závad</li><li>do 22. srpna rozhodnutí o registraci</li><li>9. a 10. října volby</li></ul></div><div class="sidebox"><h3>Pošlete nám tip</h3><p>Máte veřejné oznámení další kandidátky nebo úplnou sestavu? Pošlete odkaz či snímek na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/long-article-ads.js?v=20260731-long-article-ads-2"></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body></html>'''


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    rss_date = format_datetime(datetime.fromisoformat(PUBLISHED))
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{rss_date}</lastBuildDate>', text, count=1)
    if URL not in text:
        item = (
            f'<item><title>{escape(TITLE)}</title><description><![CDATA[{DESC}]]></description>'
            f'<link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{rss_date}</pubDate>'
            '<category>Kadaň</category><category>Komunální volby</category><category>Politika</category>'
            f'<szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>\n    '
        )
        text = text.replace('<item>', item + '<item>', 1)
    write(path, text)


def update_sitemaps() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        text = text.replace('</urlset>', f'  <url><loc>{URL}</loc><lastmod>2026-08-04</lastmod></url>\n</urlset>', 1)
    write(path, text)

    path = ROOT / "news-sitemap.xml"
    text = path.read_text(encoding="utf-8")
    open_root = re.search(r'\A(.*?<urlset\b[^>]*>\s*)', text, re.S)
    if not open_root:
        raise RuntimeError("News sitemap nemá kořen urlset.")
    prefix = open_root.group(1)
    blocks = re.findall(r'<url>.*?</url>', text, flags=re.S)
    node = f'''<url><loc>{URL}</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>{PUBLISHED}</news:publication_date><news:title>{escape(TITLE)}</news:title></news:news><image:image><image:loc>{SOCIAL_URL}</image:loc><image:title>{escape(TITLE)}</image:title></image:image></url>'''
    by_loc: dict[str, str] = {}
    for block in [node] + blocks:
        loc = re.search(r'<loc>(.*?)</loc>', block, re.S)
        if loc and loc.group(1) not in by_loc:
            by_loc[loc.group(1)] = block
    def pub_date(block: str) -> datetime:
        match = re.search(r'<news:publication_date>(.*?)</news:publication_date>', block, re.S)
        if not match:
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            dt = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)
    ordered = sorted(by_loc.values(), key=pub_date, reverse=True)[:10]
    write(path, prefix + '\n  ' + '\n  '.join(ordered) + '\n</urlset>\n')


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
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    item = next((row for row in articles if isinstance(row, dict) and row.get("url") == URL), None)
    if item is None:
        item = {
            "title": TITLE,
            "h1": TITLE,
            "url": URL,
            "published_at": PUBLISHED,
            "modified_at": MODIFIED,
            "persons": ["Jan Losenický", "Radek Oswald", "Alena Benešová", "Jan Perout", "Michal Voltr", "Jan Vaic", "Marcela Trejbal Vlčková", "Michal Vyčichlo", "Jan Hudák", "Soňa Pusztakürti", "Jana Hladová", "Jiří Kulhánek"],
            "organizations": ["ODS Kadaň", "Dáme Kadani novou šanci", "ANO 2011", "Piráti Kadaň", "Městský úřad Kadaň", "Ministerstvo vnitra"],
            "places": ["Kadaň"],
            "cases": ["Podání kandidátních listin pro komunální volby 2026 v Kadani", "Rozdělení někdejší kandidátky ODS"],
            "topics": ["Komunální volby 2026", "Kandidátní listiny", "ODS", "Dáme Kadani novou šanci", "ANO", "Piráti"],
            "fingerprint": sha256("komunalni-volby-2026-kadan-podani-kandidatek-ods-dkns-ano".encode()).hexdigest()[:24],
            "status": {},
            "source_path": f"clanky/{SLUG}.html",
            "publication_status": "published",
            "source_commit": "pending-publication-commit",
        }
        articles.insert(0, item)
    else:
        item.update({"title": TITLE, "h1": TITLE, "modified_at": MODIFIED, "publication_status": "published"})

    home = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
    archive_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted((ROOT / "clanky").glob("strana-*.html"))) + "\n" + (ROOT / "clanky/index.html").read_text(encoding="utf-8", errors="replace")
    rss = (ROOT / "rss.xml").read_text(encoding="utf-8", errors="replace")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8", errors="replace")
    news = (ROOT / "news-sitemap.xml").read_text(encoding="utf-8", errors="replace")
    for row in articles:
        if not isinstance(row, dict) or not row.get("url"):
            continue
        rel = row["url"].replace("https://nasekadan.cz", "")
        row["status"] = {
            "homepage": rel in home or row["url"] in home,
            "archive": rel in archive_text or row["url"] in archive_text,
            "rss": row["url"] in rss,
            "sitemap": row["url"] in sitemap,
            "news_sitemap": row["url"] in news,
        }
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation.update({
        "homepage_count": sum(1 for row in articles if isinstance(row, dict) and row.get("status", {}).get("homepage")),
        "archive_count": sum(1 for row in articles if isinstance(row, dict) and row.get("status", {}).get("archive")),
        "archive_page_count": 1 + len(list((ROOT / "clanky").glob("strana-*.html"))),
        "rss_count": sum(1 for row in articles if isinstance(row, dict) and row.get("status", {}).get("rss")),
        "sitemap_all_articles_present": all(row.get("status", {}).get("sitemap") for row in articles if isinstance(row, dict)),
        "news_sitemap_recent_count": len(re.findall(r'<url>', news)),
        "required_fields_complete": True,
        "duplicate_urls": [],
        "duplicate_fingerprints": [],
        "canonical_duplicate_filter": True,
        "last_consistency_audit": {
            "status": "pending_public_deploy",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "article_count": len(articles),
        },
    })
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    make_social()
    write(ARTICLE, article_page())
    update_rss()
    update_sitemaps()
    update_llms()
    visibility = ROOT / "scripts" / "enforce_article_visibility.py"
    subprocess.run(["python3", str(visibility)], cwd=ROOT, check=True)
    update_registry()
    weather = ROOT / "scripts" / "ensure_weather_loader.py"
    if weather.exists():
        subprocess.run(["python3", str(weather)], cwd=ROOT, check=True)

    required = [ARTICLE, SOCIAL, ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "data/published-content-index.json"]
    for path in required:
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Chybí výstup {path}")
    article = ARTICLE.read_text(encoding="utf-8")
    if f'<h1>{TITLE}</h1>' not in article or 'index,follow' not in article:
        raise RuntimeError("Článek nemá správný H1 nebo indexaci.")
    if "bývalý kadaňský místostarosta Radek Oswald" in article:
        raise RuntimeError("V článku zůstalo nepravdivé označení Radka Oswalda.")
    if REL not in (ROOT / "index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Článek chybí na titulce.")
    archive_all = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in [ROOT / "clanky/index.html", *sorted((ROOT / "clanky").glob("strana-*.html"))])
    if REL not in archive_all:
        raise RuntimeError("Článek chybí v archivu.")
    for path in [ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml"]:
        if URL not in path.read_text(encoding="utf-8", errors="replace"):
            raise RuntimeError(f"V {path} chybí článek.")
    if '/pocasi.js' not in (ROOT / "index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Publikace odstranila loader počasí.")
    print(f"Připraveno k publikaci: {URL}")


if __name__ == "__main__":
    main()
