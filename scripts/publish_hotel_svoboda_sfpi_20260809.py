#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "hotel-svoboda-dostupne-bydleni-knihovna-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
URL = f"https://nasekadan.cz/{ARTICLE_REL}"
SOCIAL_REL = f"social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL
SOCIAL_URL = f"https://nasekadan.cz/{SOCIAL_REL}"
TITLE = "Svoboda má stavební povolení. Kadaň chystá byty i knihovnu a připravuje dvě dotační žádosti"
DESC = "Projektová dokumentace bývalého hotelu Svoboda je hotová a město má stavební povolení. V roce 2026 připravuje zvlášť žádost na knihovnu a zvlášť na dostupné bydlení."
PUBLISHED = "2026-08-09T04:00:00+02:00"
ARTICLE_SOURCE_COMMIT = os.environ.get("ARTICLE_SOURCE_COMMIT", "pending-publication-commit")

SOURCES = [
    ("https://www.mesto-kadan.cz/filemanager/files/file.php?file=5095064", "Město Kadaň: Plán investiční výstavby na rok 2026 – stav projektu Svoboda"),
    ("https://smlouvy.gov.cz/vyhledavani?subject_name=M%C4%9Bsto+Kada%C5%88", "Registr smluv – Město Kadaň: smlouvy a objednávky k objektu Svoboda"),
    ("https://smlouvy.gov.cz/smlouva/30509420", "Registr smluv: architektonická studie objektu Svoboda"),
    ("https://smlouvy.gov.cz/smlouva/31385896", "Registr smluv: projektová dokumentace KAP ATELIER"),
    ("https://mmr.gov.cz/getattachment/79c01485-7b07-4155-b290-48a802ced818/Seznam-schvalenych-a-neschvalenych-projektu-1-vyzva-4-1-3-13-11-2024.pdf.aspx?ext=.pdf&lang=cs-CZ", "MMR: konečný seznam 1. výzvy NPO – projekt Svoboda, požadavek 2 mil. Kč a 0 Kč v kolonce lze poskytnout"),
    ("https://opst.cz/files/documents/storage/2024/10/01/1727761040_20240910_Z%C3%A1pis_17.%20VK_priloha.pdf", "OP Spravedlivá transformace: projekt Svoboda doporučený k financování"),
    ("https://mmr.gov.cz/cs/ostatni/web/novinky/mmr-zajistilo-pres-8-miliard-korun-na-dostupne-naj", "MMR: nový program Dostupné nájemní bydlení 2.0, 18. června 2026"),
    ("https://sever.rozhlas.cz/budova-byvaleho-hotelu-svoboda-na-namesti-v-kadani-se-promeni-na-bytovy-dum-a-9257960", "Český rozhlas Sever: plán bytů a knihovny, 18. června 2024"),
    ("https://chomutovsky.denik.cz/zpravy_region/hotel-svoboda-kadan-nove-byty.html", "Chomutovský deník: zhruba 25 bytových jednotek v návrhu z července 2024"),
    ("https://chomutovsky.denik.cz/zpravy_region/kadan-si-chce-pujcit-nejmene-sto-milionu-zaplati-byty-knihovnu-i-pamatku-2025091.html", "Chomutovský deník: rozšíření knihovny do části prvního patra, září 2025"),
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    image = Image.new("RGB", (W, H), "#132832")
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(H):
        t = y / H
        c = (int(19 + 35*t), int(40 + 29*t), int(50 + 25*t))
        draw.line((0, y, W, y), fill=(*c, 255))
    draw.rectangle((760, 175, 1110, 520), fill=(236,229,211,235), outline=(255,255,255,120), width=3)
    draw.polygon([(740,175),(935,90),(1130,175)], fill=(151,56,48,245))
    for row in range(3):
        for col in range(4):
            x = 800 + col*72
            y = 225 + row*78
            draw.rectangle((x,y,x+42,y+48), fill=(57,91,104,245), outline=(255,255,255,130), width=2)
    draw.rectangle((900,430,970,520), fill=(74,68,58,255))
    draw.rectangle((760,500,1110,535), fill=(126,107,78,255))
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fbrand = ImageFont.truetype(bold, 23)
    fbig = ImageFont.truetype(bold, 49)
    fmid = ImageFont.truetype(bold, 27)
    fsmall = ImageFont.truetype(regular, 22)
    draw.rounded_rectangle((62, 52, 388, 104), radius=25, fill=(159,38,38,255))
    draw.text((84,68), "NAŠE KADAŇ · BYDLENÍ", font=fbrand, fill="white")
    draw.text((62,155), "HOTEL SVOBODA:", font=fbig, fill="white")
    draw.text((62,217), "BYTY I KNIHOVNA", font=fbig, fill="white")
    draw.text((64,330), "STAVEBNÍ POVOLENÍ JE VYDANÉ", font=fmid, fill=(248,220,156,255))
    draw.text((64,379), "Město připravuje dvě nové dotační žádosti", font=fsmall, fill=(238,243,244,255))
    draw.text((64,552), "NASEKADAN.CZ", font=fbrand, fill="white")
    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image.save(SOCIAL, format="PNG", optimize=True)


def footer() -> str:
    sys.path.insert(0, str(ROOT / "scripts"))
    import publish_gymnastika_kadan_20260806 as helper
    return helper.footer()


def article_html() -> str:
    schema = {
        "@context":"https://schema.org","@type":"NewsArticle","headline":TITLE,"description":DESC,
        "datePublished":PUBLISHED,"dateModified":PUBLISHED,
        "author":{"@type":"Organization","@id":"https://nasekadan.cz/#organization","name":"Naše Kadaň","url":"https://nasekadan.cz/o-webu/"},
        "publisher":{"@id":"https://nasekadan.cz/#organization"},
        "mainEntityOfPage":{"@type":"WebPage","@id":URL},"image":[SOCIAL_URL],"inLanguage":"cs-CZ","isAccessibleForFree":True,
        "about":[
            {"@type":"Place","name":"Kadaň"},
            {"@type":"Thing","name":"Hotel Svoboda"},
            {"@type":"Thing","name":"Dostupné nájemní bydlení"},
            {"@type":"Thing","name":"Městská knihovna"},
            {"@type":"Organization","name":"Státní fond podpory investic"},
        ],
    }
    breadcrumbs = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Naše Kadaň","item":"https://nasekadan.cz/"},
        {"@type":"ListItem","position":2,"name":"Články","item":"https://nasekadan.cz/clanky/"},
        {"@type":"ListItem","position":3,"name":TITLE,"item":URL},
    ]}
    sources = "".join(f'<li><a href="{u}" rel="noopener">{escape(label)}</a></li>' for u,label in SOURCES)
    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title><meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260805-event-hotfix-3">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:secure_url" content="{SOCIAL_URL}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',',':'))}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumbs, ensure_ascii=False, separators=(',',':'))}</script>
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,840px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,64px)/1.03 Georgia,serif;letter-spacing:-.038em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #16242d22}}.fact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:28px 0}}.fact{{background:#f5f0e8;border:1px solid #dfd3bf;border-radius:17px;padding:18px}}.fact strong{{display:block;color:#9f2626;font:900 25px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.callout{{border-left:7px solid #9f2626;background:#f7f1e7;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.neutral{{background:#eef3f5;border:1px solid #d5e0e4;border-radius:18px;padding:23px 25px;margin:30px 0}}.money-table{{width:100%;border-collapse:collapse;margin:25px 0}}.money-table th,.money-table td{{padding:13px 14px;border-bottom:1px solid #d9e0e3;text-align:left;vertical-align:top}}.money-table th{{background:#152a34;color:#fff}}.timeline{{border-left:4px solid #d7dde0;margin:30px 0;padding-left:24px}}.timeline div{{position:relative;padding:0 0 25px}}.timeline div:before{{content:'';position:absolute;left:-33px;top:7px;width:14px;height:14px;border-radius:50%;background:#9f2626;border:4px solid #fff}}.timeline b{{display:block;font:800 21px Georgia,serif}}.timeline p{{margin:5px 0}}.sources{{background:#eef3f5;padding:24px;border-radius:18px;margin-top:42px}}.sources h2{{margin-top:0}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dde3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:800 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:680px){{.article{{padding:26px 20px}}.fact-grid{{grid-template-columns:1fr}}.money-table{{display:block;overflow:auto}}}}
</style></head><body>
<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article">
<p class="tag">BYDLENÍ · INVESTICE · KNIHOVNA · 9. SRPNA 2026 · 04:00</p><h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>Bývalý hotel Svoboda už není jen ve fázi studie. Oficiální plán investiční výstavby města uvádí, že projektová dokumentace je dokončená a stavební povolení vydané. V roce 2026 se zároveň rozbíhají dvě samostatné dotační větve: v červnu si Kadaň objednala za 150 tisíc korun bez DPH přípravu žádosti na knihovnu a 7. srpna za 130 tisíc přípravu žádosti do programu označeného jako „Dostupné bydlení 2“. Přesto stále veřejně neznáme konečný počet bytů ani současný celkový rozpočet rekonstrukce.</strong></p>
<img class="hero-image" src="/{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k připravovaným bytům a knihovně v bývalém hotelu Svoboda v Kadani">
<div class="fact-grid"><div class="fact"><strong>Stavební povolení</strong><span>projektová dokumentace je podle plánu města dokončena a povolení vydáno</span></div><div class="fact"><strong>3 mil. Kč</strong><span>investiční položka města pro Svobodu v roce 2026; nejde o celkovou cenu stavby</span></div><div class="fact"><strong>150 + 130 tis.</strong><span>dvě letošní objednávky na přípravu dotačních žádostí, vždy bez DPH</span></div></div>

<h2>Projektová dokumentace je hotová a stavební povolení vydané</h2>
<p>Nejnovější oficiální plán investiční výstavby města posouvá projekt Svobody o důležitý krok dál. U obnovy čp. 122 – bývalého hotelu Svoboda – už uvádí, že <strong>projektová dokumentace je dokončená a bylo vydáno stavební povolení</strong>. Město zároveň připravuje podklady pro soutěž na dodavatele projektové dokumentace vybavení interiéru knihovny.</p>
<p>To ale ještě neznamená, že je vybraný stavební dodavatel celé rekonstrukce. Veřejné podklady zatím neukazují soutěž na hlavního zhotovitele přestavby Svobody ani smlouvu, která by stanovila cenu celé stavby a pevný termín zahájení.</p>
<div class="callout"><strong>Tři miliony nejsou cena rekonstrukce.</strong><p>V podkladech k zastupitelstvu z 25. června 2026 je u řádku „rekonstrukce objektu Svoboda – investice“ částka 3 miliony korun. Jde o letošní rozpočtovou položku. Samotný investiční plán u Svobody – na rozdíl od některých jiných městských projektů – současnou celkovou cenu díla neuvádí.</p></div>

<h2>Byty a knihovna nejsou dvě soupeřící varianty</h2>
<p>V Registru smluv se 7. srpna 2026 objevil nový záznam města na <strong>zajištění přípravy žádosti do programu „Dostupné bydlení 2“ v rámci SFPI</strong>, včetně doplnění příloh a formulářů pro objekt označený jako „SVOBODA čp. 122-3“. Dodavatelem je Regionální rozvojová agentura Ústeckého kraje, a.s. a cena služby činí 130 tisíc korun bez DPH.</p>
<p>Jen o necelé dva měsíce dříve, 12. června, město stejné agentuře objednalo za <strong>150 tisíc korun bez DPH</strong> zpracování žádosti o dotaci včetně projektového záměru pro projekt výslovně nazvaný „Kadaň, Mírové náměstí čp. 122 a 123, objekt Svoboda – vybudování knihovny“.</p>
<p>Veřejná smluvní stopa tedy ukazuje dvě současně připravované finanční větve pro jeden dům: jednu pro knihovnu a druhou pro dostupné bydlení. Není to důkaz, že by byty nahradily knihovnu. Při projednávání investičního plánu 25. června se zastupitelka Jindra Zalabáková přímo zeptala, zda ve Svobodě knihovna bude. Místostarosta Jan Vaic odpověděl, že objekt je koncipovaný pro <strong>byty i knihovnu</strong>.</p>

<h2>Jedna žádost o dva miliony nevyšla. Jiná dotační cesta projekt podpořila</h2>
<p>Dotační historie Svobody je delší než letošní dvě objednávky. Už 10. ledna 2024 si město za 50 tisíc korun bez DPH objednalo přípravu žádosti do Národního plánu obnovy na projektovou přípravu Svobody. Oficiální seznam MMR následně eviduje projekt pod registračním číslem <strong>CZ.31.7.0/0.0/0.0/23_104/0009445</strong>, podaný 27. února 2024, s požadavkem na <strong>2 miliony korun</strong>. V pozdějším konečném seznamu má ale projekt v kolonce částky, kterou lze poskytnout, <strong>0 Kč</strong>.</p>
<p>Město paralelně zkusilo jinou cestu. Dne 11. března 2024 objednalo za 90 tisíc korun bez DPH zpracování kompletní žádosti, studie proveditelnosti a příloh do 23. výzvy Operačního programu Spravedlivá transformace. Výběrová komise OPST následně projekt „Kadaň, Mírové náměstí čp. 122 a 123, objekt Svoboda“ zařadila mezi projekty doporučené k financování.</p>
<table class="money-table"><thead><tr><th>OPST – projekt Svoboda</th><th>Částka</th></tr></thead><tbody>
<tr><td>Celkové způsobilé výdaje projektu přípravy</td><td><strong>1 294 700 Kč</strong></td></tr>
<tr><td>Příspěvek Evropské unie</td><td><strong>971 025 Kč</strong></td></tr>
<tr><td>Národní část</td><td><strong>323 675 Kč</strong></td></tr>
</tbody></table>
<div class="neutral"><strong>To není milion na samotnou rekonstrukci domu.</strong><p>OPST částka patří projektu v programu „Obnova území – Koncepce a příprava projektů“. Jde tedy o financování projektové přípravy, nikoli o stavební rozpočet celé přestavby Svobody. Stejně tak z veřejného názvu projektu nelze poctivě tvrdit, že všech 971 025 korun evropského příspěvku bylo určeno výhradně na budoucí knihovnu.</p></div>

<h2>Kolik bytů nakonec vznikne? Veřejné číslo se v čase měnilo</h2>
<p>Právě počet bytů je příklad, proč není bezpečné přebírat staré plány jako dnešní stav. Při koupi domu na konci roku 2023 se veřejně mluvilo až o přibližně <strong>30 bytech</strong>. V červnu 2024 starosta Jan Losenický Českému rozhlasu popsal představu přibližně <strong>20 bytů, možná i více</strong>, převážně 2+1. O měsíc později vedoucí investičního odboru Jan Hnídek hovořil už o <strong>zhruba 25 bytových jednotkách</strong> – 1+1, 2+1 a případně 2+kk či 3+kk.</p>
<p>V září 2025 se navíc veřejně objevila informace, že knihovna, původně plánovaná hlavně do přízemí, se má rozšířit <strong>i do části prvního patra</strong>. Dispozice domu se tedy proti prvním představám měnila. Proto stará čísla 20, 25 ani 30 nevydáváme za současný počet bytů. Konečný počet bytů zatím město ve zveřejněných podkladech neuvedlo.</p>

<h2>Co už má projekt za sebou – a kolik stojí jednotlivé kroky</h2>
<table class="money-table"><thead><tr><th>Krok</th><th>Veřejně dohledatelná částka</th></tr></thead><tbody>
<tr><td>Koupě bývalého hotelu městem na konci roku 2023</td><td><strong>25 mil. Kč</strong></td></tr>
<tr><td>Příprava žádosti NPO na projektovou přípravu, leden 2024</td><td><strong>50 tis. Kč bez DPH</strong></td></tr>
<tr><td>Příprava žádosti OPST včetně studie proveditelnosti, březen 2024</td><td><strong>90 tis. Kč bez DPH</strong></td></tr>
<tr><td>Architektonická studie Ing. arch. Márie Maninové</td><td><strong>280 tis. Kč bez DPH</strong></td></tr>
<tr><td>Projektová dokumentace KAP ATELIER</td><td><strong>původně 1,918 mil. Kč, pozdější smluvní záznam 2,118 mil. Kč bez DPH</strong></td></tr>
<tr><td>Investiční položka v rozpočtu města pro rok 2026</td><td><strong>3 mil. Kč</strong> – není to cena celé stavby</td></tr>
<tr><td>Příprava dotační žádosti na knihovnu, červen 2026</td><td><strong>150 tis. Kč bez DPH</strong></td></tr>
<tr><td>Příprava žádosti „Dostupné bydlení 2“, srpen 2026</td><td><strong>130 tis. Kč bez DPH</strong></td></tr>
</tbody></table>
<p>Tyto částky se nesmějí mechanicky sečíst jako „cena Svobody“. Část představuje kupní cenu nemovitosti, část administraci dotací, část projektování a tři miliony jsou rozpočtová položka pro konkrétní rok. Navíc původní a pozdější hodnotu smlouvy KAP ATELIER nelze sčítat mezi sebou.</p>
<p>Historicky vedení města po koupi domu pracovalo s velmi hrubým odhadem přestavby přibližně <strong>100 až 200 milionů korun</strong>. Ten pochází ještě z doby před hotovou projektovou dokumentací a před změnami dispozic, takže jej nelze používat jako dnešní stavební rozpočet. Současnou celkovou cenu město ve zveřejněných dokumentech zatím neuvedlo.</p>

<h2>„Dostupné bydlení 2“ nejspíš míří na nový program 2.0. Přesnou výzvu ale objednávka neříká</h2>
<p>Ministerstvo pro místní rozvoj 18. června 2026 představilo nový program <strong>Dostupné nájemní bydlení 2.0</strong> s alokací 5,8 miliardy korun z IROP a Operačního programu Spravedlivá transformace. Ministerstvo u obecného nastavení uvádí kombinaci zvýhodněného úvěru a dotace, podporu až do 85 procent způsobilých nákladů, dotační složku 15 až 30 procent a úvěr se splatností až 40 let a úrokem kolem jednoho procenta.</p>
<p>Označení srpnové kadaňské objednávky „Dostupné bydlení 2“ časově i názvem tomuto novému programu odpovídá. <strong>Je to ale zatím kvalifikovaná souvislost, nikoli potvrzený parametr kadaňské žádosti.</strong> Veřejný záznam objednávky neuvádí číslo konkrétní výzvy, částku, o kterou chce město požádat, ani poměr dotace, úvěru a vlastních peněz.</p>

<h2>Časová osa Svobody</h2><div class="timeline">
<div><b>Konec roku 2023</b><p>Kadaň kupuje bývalý hotel Svoboda za 25 milionů korun. Veřejně se mluví až o zhruba 30 bytech a hrubém odhadu rekonstrukce 100 až 200 milionů.</p></div>
<div><b>10. ledna 2024</b><p>Město objednává za 50 tisíc Kč bez DPH přípravu žádosti do NPO na projektovou přípravu.</p></div>
<div><b>27. února 2024</b><p>Žádost NPO požaduje 2 miliony Kč; pozdější konečný seznam uvádí 0 Kč v kolonce lze poskytnout.</p></div>
<div><b>11.–25. března 2024</b><p>Za 90 tisíc Kč bez DPH se připravuje žádost OPST a 25. března je projekt poprvé podán. Později je doporučen k financování s 971 025 Kč z EU.</p></div>
<div><b>Červen–červenec 2024</b><p>Veřejné představy o počtu bytů se pohybují od přibližně 20 k přibližně 25 jednotkám.</p></div>
<div><b>Říjen 2024–2025</b><p>Vzniká architektonická studie a navazující projektová dokumentace. Později se rozšiřuje plánovaný prostor knihovny i do části prvního patra.</p></div>
<div><b>Rok 2026</b><p>Podle investičního plánu je projektová dokumentace dokončena a stavební povolení vydáno.</p></div>
<div><b>12. června 2026</b><p>Město objednává za 150 tisíc Kč bez DPH přípravu nové dotační žádosti na vybudování knihovny.</p></div>
<div><b>25. června 2026</b><p>Zastupitelstvo probírá investiční plán; vedení potvrzuje kombinaci bytů a knihovny. Rozpočtové podklady mají pro Svobodu investiční položku 3 miliony Kč.</p></div>
<div><b>7. srpna 2026</b><p>Do Registru smluv přibývá příprava žádosti „Dostupné bydlení 2“ za 130 tisíc Kč bez DPH.</p></div>
</div>

<h2>Co stále chybí k úplnému účtu</h2>
<p>Stavební povolení a dokončení projektové dokumentace jsou už doložené. Nadále však nejsou zveřejněné čtyři klíčové údaje: <strong>konečný počet bytů podle hotového projektu, současný položkový rozpočet celé rekonstrukce, přesná částka žádaná v programu dostupného bydlení a harmonogram soutěže a stavebních prací</strong>.</p>
<p>Pro úplný obraz budou rozhodující zejména konečná dispozice domu, položkový rozpočet, parametry připravované žádosti na dostupné bydlení a zadávací podmínky budoucí soutěže na zhotovitele. Do jejich zveřejnění nelze přesnou cenu stavby ani termín zahájení prací spolehlivě určit.</p>

<div class="sources"><h2>Zdroje a ověření</h2><p>Stav projektové dokumentace a stavebního povolení vychází z oficiálního Plánu investiční výstavby města Kadaně pro rok 2026. Zdrojem smluvních a objednávkových částek je Registr smluv. Dotační historie vychází z konečného seznamu MMR k výzvě NPO a z přílohy výběrové komise Operačního programu Spravedlivá transformace. Historické počty bytů jsou uvedeny pouze jako časová osa vývoje návrhu, nikoli jako současný stav.</p><ul>{sources}</ul></div>
</article><aside class="sticky"><div class="sidebox"><h3>Co už je jisté</h3><ul><li>projektová dokumentace je hotová</li><li>stavební povolení je vydané</li><li>objekt má kombinovat byty a knihovnu</li><li>město v roce 2026 připravuje dvě nové dotační žádosti</li></ul></div><div class="sidebox"><h3>Co stále nevíme</h3><ul><li>konečný počet bytů</li><li>celkovou cenu rekonstrukce</li><li>částku žádanou na dostupné bydlení</li><li>termín soutěže a zahájení stavby</li></ul></div><div data-promos data-context="sidebar"></div></aside></main>
{footer()}<script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script></body></html>'''


def ensure_article_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        write(path, text.replace("</urlset>", f"  <url><loc>{URL}</loc><lastmod>2026-08-09</lastmod></url>\n</urlset>"))


def strip_trailing_whitespace(path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip(" \t") for line in text.splitlines()) + "\n"
    if cleaned != text:
        write(path, cleaned)


def normalize_generated_whitespace() -> None:
    paths = [ROOT/"index.html",ROOT/"rss.xml",ROOT/"sitemap.xml",ROOT/"news-sitemap.xml",ROOT/"llms.txt",ROOT/"clanky/index.html",ARTICLE]
    paths.extend(sorted((ROOT/"clanky").glob("strana-*.html")))
    for path in paths:
        strip_trailing_whitespace(path)


def upsert_registry() -> None:
    path = ROOT / "data/published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    entry = {
        "title":TITLE,"h1":TITLE,"url":URL,"published_at":PUBLISHED,"modified_at":PUBLISHED,
        "persons":["Jan Losenický","Jan Vaic","Jindra Zalabáková","Jan Hnídek"],
        "organizations":["Město Kadaň","Regionální rozvojová agentura Ústeckého kraje, a.s.","Státní fond podpory investic","Ministerstvo pro místní rozvoj","Operační program Spravedlivá transformace","Městská knihovna Kadaň","Naše Kadaň"],
        "places":["Kadaň","Mírové náměstí","Hotel Svoboda"],
        "cases":["Rekonstrukce bývalého hotelu Svoboda"],
        "topics":["Dostupné bydlení","Nájemní bydlení","Městská knihovna","Městské investice","SFPI","OPST","Stavební povolení"],
        "fingerprint":sha256("kadan|hotel-svoboda|dostupne-bydleni-2|knihovna|20260807".encode()).hexdigest()[:24],
        "status":{"homepage":True,"archive":True,"rss":True,"sitemap":True,"news_sitemap":True},
        "source_path":ARTICLE_REL,"publication_status":"published","source_commit":ARTICLE_SOURCE_COMMIT,
    }
    existing = next((i for i in articles if i.get("url") == URL), None)
    if existing is None:
        articles.append(entry)
    else:
        existing.clear()
        existing.update(entry)
    articles.sort(key=lambda i:i.get("published_at",""), reverse=True)
    urls=[i.get("url") for i in articles if i.get("url")]
    fps=[i.get("fingerprint") for i in articles if i.get("fingerprint")]
    dup_urls=sorted({x for x in urls if urls.count(x)>1})
    dup_fps=sorted({x for x in fps if fps.count(x)>1})
    if dup_urls or dup_fps:
        raise RuntimeError(f"Duplicita registru: URL={dup_urls}, fingerprinty={dup_fps}")
    now=datetime.now(timezone.utc).isoformat()
    data["generated_at"]=now
    data["article_count"]=len(articles)
    data.setdefault("validation",{})["last_publication"]={
        "status":"prepared_for_publication","checked_at":now,"article_url":URL,
        "classification":"municipal_housing_library_investment","source_commit":ARTICLE_SOURCE_COMMIT,
        "public_verified_at":None,
    }
    write(path,json.dumps(data,ensure_ascii=False,indent=2)+"\n")


def validate() -> None:
    text=ARTICLE.read_text(encoding="utf-8")
    surfaces={name:path.read_text(encoding="utf-8") for name,path in {
        "home":ROOT/"index.html","archive":ROOT/"clanky/index.html","rss":ROOT/"rss.xml",
        "sitemap":ROOT/"sitemap.xml","news":ROOT/"news-sitemap.xml","llms":ROOT/"llms.txt",
        "registry":ROOT/"data/published-content-index.json","manifest":ROOT/"data/article-integrity-manifest.json"
    }.items()}
    checks={
        "h1":f"<h1>{TITLE}</h1>" in text,
        "canonical":f'<link rel="canonical" href="{URL}">' in text,
        "indexable":"noindex" not in text.lower(),
        "social":SOCIAL.is_file(),
        "home":ARTICLE_REL in surfaces["home"],
        "archive":ARTICLE_REL in surfaces["archive"],
        "rss":URL in surfaces["rss"],
        "sitemap":URL in surfaces["sitemap"],
        "news":URL in surfaces["news"],
        "llms":ARTICLE_REL in surfaces["llms"],
        "registry":URL in surfaces["registry"],
        "manifest":URL in surfaces["manifest"],
        "building_permit":"stavební povolení" in text.lower(),
        "opst":"971 025 Kč" in text,
        "budget_2026":"3 mil. Kč" in text,
    }
    from PIL import Image
    with Image.open(SOCIAL) as im:
        checks["social_dimensions"] = im.size == (1200,630)
    failed=[k for k,v in checks.items() if not v]
    if failed:
        raise RuntimeError("Neúplná publikace Svobody: "+", ".join(failed))
    ET.parse(ROOT/"rss.xml")
    ET.parse(ROOT/"sitemap.xml")
    ET.parse(ROOT/"news-sitemap.xml")
    print(json.dumps({"status":"prepared","url":URL,"checks":checks},ensure_ascii=False,indent=2))


def main() -> int:
    make_social()
    write(ARTICLE,article_html())
    sys.path.insert(0,str(ROOT/"scripts"))
    import publish_gymnastika_kadan_20260806 as helper
    helper.rebuild_surfaces()
    ensure_article_sitemap()
    helper.rebuild_integrity_manifest()
    upsert_registry()
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_footers.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_articles.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/sort_articles_chronologically.py")],cwd=ROOT,check=True)
    normalize_generated_whitespace()
    validate()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
