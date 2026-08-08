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
TITLE = "Byty i knihovna ve Svobodě: Kadaň připravuje novou žádost na dostupné bydlení"
DESC = "Kadaň si objednala přípravu žádosti do programu Dostupné bydlení 2 pro bývalý hotel Svoboda. V červnu přitom řešila samostatnou žádost na knihovnu ve stejném objektu."
PUBLISHED = "2026-08-09T04:00:00+02:00"
ARTICLE_SOURCE_COMMIT = os.environ.get("ARTICLE_SOURCE_COMMIT", "pending-publication-commit")

SOURCES = [
    ("https://smlouvy.gov.cz/vyhledavani?subject_name=M%C4%9Bsto+Kada%C5%88", "Registr smluv – Město Kadaň: aktuální smlouvy a objednávky k objektu Svoboda"),
    ("https://smlouvy.gov.cz/smlouva/31385896", "Registr smluv: projektová dokumentace rekonstrukce objektů čp. 122 a 123"),
    ("https://sever.rozhlas.cz/budova-byvaleho-hotelu-svoboda-na-namesti-v-kadani-se-promeni-na-bytovy-dum-a-9257960", "Český rozhlas Sever: plán bytového domu a knihovny, 18. června 2024"),
    ("https://mmr.gov.cz/cs/ministerstvo/bytova-politika/rozvoj-dostupneho-bydleni", "Ministerstvo pro místní rozvoj: Rozvoj dostupného bydlení"),
    ("https://sfpi.cz/dostupne-bydleni/", "SFPI: Dostupné nájemní bydlení"),
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
    # Stylizované průčelí domu, nikoli tvrzení o přesné podobě budoucí rekonstrukce.
    draw.rectangle((760, 175, 1110, 520), fill=(236,229,211,235), outline=(255,255,255,120), width=3)
    draw.polygon([(740,175),(935,90),(1130,175)], fill=(151,56,48,245))
    for row in range(3):
        for col in range(4):
            x = 800 + col*72; y = 225 + row*78
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
    draw.text((64,330), "Nová žádost na dostupné bydlení", font=fmid, fill=(248,220,156,255))
    draw.text((64,379), "Knihovna se řešila samostatnou žádostí už v červnu", font=fsmall, fill=(238,243,244,255))
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
        "about":[{"@type":"Place","name":"Kadaň"},{"@type":"Thing","name":"Hotel Svoboda"},{"@type":"Thing","name":"Dostupné nájemní bydlení"},{"@type":"Organization","name":"Státní fond podpory investic"}],
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
<p class="leadtext"><strong>Projekt bývalého hotelu Svoboda na Mírovém náměstí dostává další konkrétní finanční stopu. Město si nechává za 130 tisíc korun bez DPH připravit žádost do programu označeného jako „Dostupné bydlení 2“ v rámci SFPI. Jen o necelé dva měsíce dříve přitom objednalo za 150 tisíc přípravu samostatné dotační žádosti na vybudování knihovny ve stejném objektu. Z červnového jednání zastupitelstva vyplývá, že současná koncepce nadále počítá s oběma funkcemi – s byty i knihovnou.</strong></p>
<img class="hero-image" src="/{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k připravovaným bytům a knihovně v bývalém hotelu Svoboda v Kadani">
<div class="fact-grid"><div class="fact"><strong>130 000 Kč</strong><span>příprava nové žádosti na dostupné bydlení bez DPH</span></div><div class="fact"><strong>150 000 Kč</strong><span>červnová příprava žádosti na knihovnu bez DPH</span></div><div class="fact"><strong>Byty + knihovna</strong><span>kombinovanou koncepci potvrdilo vedení města ještě 25. června 2026</span></div></div>

<h2>Nová srpnová objednávka míří na dostupné bydlení</h2>
<p>V Registru smluv se 7. srpna 2026 objevil nový záznam města Kadaně na <strong>zajištění přípravy žádosti do programu „Dostupné bydlení 2“ v rámci Státního fondu podpory investic</strong>, včetně doplnění příloh a formulářů pro objekt označený jako „SVOBODA čp. 122-3“. Dodavatelem je Regionální rozvojová agentura Ústeckého kraje, a.s. a cena služby činí 130 tisíc korun bez DPH.</p>
<p>Samotný název objednávky ještě neříká, kolik bytů bude do žádosti zahrnuto, o jak vysokou podporu město požádá ani zda půjde v konkrétním případě o dotaci, úvěr nebo jejich kombinaci. Tyto údaje proto nelze z veřejného záznamu poctivě dovodit.</p>

<h2>V červnu se u stejného domu připravovala žádost na knihovnu</h2>
<p>Nový srpnový krok je zajímavý ve spojení s jinou letošní smlouvou. Dne 12. června byla zveřejněna objednávka stejné Regionální rozvojové agentuře na <strong>zpracování žádosti o dotaci pro projekt „Kadaň, Mírové náměstí čp. 122 a 123, objekt Svoboda – vybudování knihovny“</strong>. Cena této služby je 150 tisíc korun bez DPH.</p>
<p>Veřejná smluvní stopa tak nyní ukazuje dva samostatně připravované finanční proudy pro jeden městský objekt: jeden výslovně k nové knihovně a druhý k dostupnému bydlení.</p>
<div class="callout"><strong>Nejde o změnu z knihovny na byty.</strong><p>Ještě 25. června 2026 se při projednávání letošního plánu výstavby zastupitelka Jindra Zalabáková ptala, zda bude v hotelu Svoboda knihovna. Místostarosta Jan Vaic odpověděl, že objekt je koncipovaný tak, že v něm budou <strong>byty a knihovna</strong>. Nová srpnová objednávka je tedy v souladu s kombinovaným využitím, nikoli sama o sobě důkazem, že jedna funkce nahradila druhou.</p></div>

<h2>Počet bytů se v minulosti měnil. Současné číslo proto nebudeme hádat</h2>
<p>Když město bývalý hotel na konci roku 2023 koupilo za 25 milionů korun, veřejně se objevovaly různé počty plánovaných bytů. V červnu 2024 starosta Jan Losenický Českému rozhlasu popsal představu přibližně <strong>20 bytů, možná i více</strong>, převážně dispozice 2+1; přízemí a suterén měly sloužit jinak a hlavním návrhem byla knihovna. Byty tehdy město spojovalo zejména s mladými rodinami a seniory.</p>
<p>Protože se od té doby zpracovávala nová architektonická studie i projektová dokumentace, staré počty není správné vydávat za současný stav. V aktuálně dostupných srpnových podkladech přesný počet bytů uveden není.</p>

<h2>Příprava projektu už stála další miliony</h2>
<table class="money-table"><thead><tr><th>Krok</th><th>Veřejně dohledatelná částka</th></tr></thead><tbody>
<tr><td>Koupě bývalého hotelu městem na konci roku 2023</td><td><strong>25 mil. Kč</strong></td></tr>
<tr><td>Architektonická studie objektu, zveřejněná v roce 2024</td><td><strong>280 tis. Kč bez DPH</strong></td></tr>
<tr><td>Projektová dokumentace KAP ATELIER – původní smluvní hodnota</td><td><strong>1,918 mil. Kč bez DPH</strong></td></tr>
<tr><td>Projektová dokumentace – smluvní záznam po dalších změnách v srpnu 2025</td><td><strong>2,118 mil. Kč bez DPH</strong></td></tr>
<tr><td>Příprava dotační žádosti na knihovnu, červen 2026</td><td><strong>150 tis. Kč bez DPH</strong></td></tr>
<tr><td>Příprava žádosti „Dostupné bydlení 2“, srpen 2026</td><td><strong>130 tis. Kč bez DPH</strong></td></tr>
</tbody></table>
<p>Tyto položky nejsou celkovou cenou budoucí rekonstrukce. Jde o veřejně dohledatelné majetkové a přípravné kroky, které ukazují, jak se projekt od koupě domu postupně posouvá.</p>

<h2>Co obecně znamená dostupné nájemní bydlení</h2>
<p>Program dostupného nájemního bydlení, který připravilo Ministerstvo pro místní rozvoj se SFPI, slouží ke vzniku nájemních bytů výstavbou, pořízením nebo rekonstrukcí. Obecný finanční nástroj kombinuje dotaci a zvýhodněný úvěr; ministerstvo u něj uvádí podporu do 250 milionů korun na projekt, dotační část typicky 25 až 40 procent a možnost kombinace s úvěrem až do 90 procent způsobilých nákladů.</p>
<p>Dostupné byty jsou určeny vymezeným skupinám, například mladším domácnostem, střední třídě nebo lidem v potřebných profesích. Pro veřejné subjekty se dostupný nájem odvozuje od nákladového nájemného a zároveň musí zůstat pod obvyklým nájemným v obdobných bytech.</p>
<div class="neutral"><strong>Pozor na označení „Dostupné bydlení 2“.</strong><p>Nová kadaňská objednávka používá právě tento název, ale z jejího veřejného záznamu zatím nevyplývá přesné znění konkrétní výzvy ani finanční parametry žádosti města. Obecné podmínky programu proto uvádíme jen jako kontext, nikoli jako potvrzené parametry kadaňského projektu.</p></div>

<h2>Časová osa Svobody</h2><div class="timeline">
<div><b>Konec roku 2023</b><p>Kadaň kupuje bývalý hotel Svoboda za 25 milionů korun a plánuje jeho přeměnu.</p></div>
<div><b>18. června 2024</b><p>Vedení města veřejně popisuje kombinaci bytů a nové bezbariérové knihovny.</p></div>
<div><b>2024–2025</b><p>Vzniká nová architektonická studie a projektová dokumentace rekonstrukce čp. 122 a 123.</p></div>
<div><b>12. června 2026</b><p>Město objednává za 150 tisíc Kč bez DPH přípravu dotační žádosti na vybudování knihovny.</p></div>
<div><b>25. června 2026</b><p>Při jednání zastupitelstva vedení města potvrzuje, že objekt je koncipovaný pro byty i knihovnu.</p></div>
<div><b>7. srpna 2026</b><p>Do Registru smluv přibývá příprava žádosti „Dostupné bydlení 2“ za 130 tisíc Kč bez DPH.</p></div>
</div>

<h2>Čtyři čísla, která ještě potřebujeme znát</h2>
<p>Pro úplné posouzení projektu nyní chybějí především <strong>aktuální počet bytů, celkový rozpočet rekonstrukce, požadovaná výše podpory ze SFPI a harmonogram stavby</strong>. Stejně důležité bude přesné dispoziční rozdělení mezi bydlení, knihovnu a technické či společné prostory.</p>
<p>Naše Kadaň bude proto dál hledat přílohy srpnové objednávky, aktuální projektovou dokumentaci a podklady rady či zastupitelstva. Pokud se v nich objeví nové konkrétní parametry, tento článek aktualizujeme.</p>

<div class="sources"><h2>Zdroje a ověření</h2><p>Aktuální smluvní údaje vycházejí z Registru smluv. Současnou kombinaci bytů a knihovny potvrzuje zápis z jednání kadaňského zastupitelstva 25. června 2026. Starší vývoj projektu a kupní cenu jsme porovnali s veřejnými informacemi Českého rozhlasu Sever. Obecný rámec dostupného nájemního bydlení ověřujeme na MMR a SFPI.</p><ul>{sources}</ul></div>
</article><aside class="sticky"><div class="sidebox"><h3>Co je nové</h3><ul><li>7. srpna přibyla příprava žádosti na dostupné bydlení</li><li>stojí 130 tisíc Kč bez DPH</li><li>v červnu se samostatně připravovala žádost na knihovnu</li><li>vedení města letos potvrdilo kombinaci obou funkcí</li></ul></div><div class="sidebox"><h3>Co stále nevíme</h3><ul><li>současný počet bytů</li><li>celkovou cenu rekonstrukce</li><li>výši žádané podpory</li><li>přesný harmonogram</li></ul></div><div data-promos data-context="sidebar"></div></aside></main>
{footer()}<script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script></body></html>'''


def ensure_article_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        write(path, text.replace("</urlset>", f"  <url><loc>{URL}</loc><lastmod>2026-08-09</lastmod></url>\n</urlset>"))


def strip_trailing_whitespace(path: Path) -> None:
    if not path.is_file(): return
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip(" \t") for line in text.splitlines()) + "\n"
    if cleaned != text: write(path, cleaned)


def normalize_generated_whitespace() -> None:
    paths = [ROOT/"index.html",ROOT/"rss.xml",ROOT/"sitemap.xml",ROOT/"news-sitemap.xml",ROOT/"llms.txt",ROOT/"clanky/index.html",ARTICLE]
    paths.extend(sorted((ROOT/"clanky").glob("strana-*.html")))
    for path in paths: strip_trailing_whitespace(path)


def upsert_registry() -> None:
    path = ROOT / "data/published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8")); articles=data.setdefault("articles",[])
    entry={"title":TITLE,"h1":TITLE,"url":URL,"published_at":PUBLISHED,"modified_at":PUBLISHED,
        "persons":["Jan Losenický","Jan Vaic","Jindra Zalabáková"],
        "organizations":["Město Kadaň","Regionální rozvojová agentura Ústeckého kraje, a.s.","Státní fond podpory investic","Městská knihovna Kadaň","Naše Kadaň"],
        "places":["Kadaň","Mírové náměstí","Hotel Svoboda"],
        "cases":["Rekonstrukce bývalého hotelu Svoboda"],
        "topics":["Dostupné bydlení","Nájemní bydlení","Městská knihovna","Městské investice","SFPI"],
        "fingerprint":sha256("kadan|hotel-svoboda|dostupne-bydleni-2|knihovna|20260807".encode()).hexdigest()[:24],
        "status":{"homepage":True,"archive":True,"rss":True,"sitemap":True,"news_sitemap":True},"source_path":ARTICLE_REL,"publication_status":"published","source_commit":ARTICLE_SOURCE_COMMIT}
    existing=next((i for i in articles if i.get("url")==URL),None)
    if existing is None: articles.append(entry)
    else: existing.clear(); existing.update(entry)
    articles.sort(key=lambda i:i.get("published_at",""), reverse=True)
    urls=[i.get("url") for i in articles if i.get("url")]; fps=[i.get("fingerprint") for i in articles if i.get("fingerprint")]
    dup_urls=sorted({x for x in urls if urls.count(x)>1}); dup_fps=sorted({x for x in fps if fps.count(x)>1})
    if dup_urls or dup_fps: raise RuntimeError(f"Duplicita registru: URL={dup_urls}, fingerprinty={dup_fps}")
    now=datetime.now(timezone.utc).isoformat(); data["generated_at"]=now; data["article_count"]=len(articles)
    data.setdefault("validation",{})["last_publication"]={"status":"prepared_for_publication","checked_at":now,"article_url":URL,"classification":"municipal_housing_library_investment","source_commit":ARTICLE_SOURCE_COMMIT,"public_verified_at":None}
    write(path,json.dumps(data,ensure_ascii=False,indent=2)+"\n")


def validate() -> None:
    text=ARTICLE.read_text(encoding="utf-8")
    surfaces={name:path.read_text(encoding="utf-8") for name,path in {
        "home":ROOT/"index.html","archive":ROOT/"clanky/index.html","rss":ROOT/"rss.xml","sitemap":ROOT/"sitemap.xml","news":ROOT/"news-sitemap.xml","llms":ROOT/"llms.txt","registry":ROOT/"data/published-content-index.json","manifest":ROOT/"data/article-integrity-manifest.json"}.items()}
    checks={"h1":f"<h1>{TITLE}</h1>" in text,"canonical":f'<link rel="canonical" href="{URL}">' in text,"indexable":"noindex" not in text.lower(),"social":SOCIAL.is_file(),"home":ARTICLE_REL in surfaces["home"],"archive":ARTICLE_REL in surfaces["archive"],"rss":URL in surfaces["rss"],"sitemap":URL in surfaces["sitemap"],"news":URL in surfaces["news"],"llms":ARTICLE_REL in surfaces["llms"],"registry":URL in surfaces["registry"],"manifest":URL in surfaces["manifest"]}
    from PIL import Image
    with Image.open(SOCIAL) as im: checks["social_dimensions"]=im.size==(1200,630)
    failed=[k for k,v in checks.items() if not v]
    if failed: raise RuntimeError("Neúplná publikace Svobody: "+", ".join(failed))
    ET.parse(ROOT/"rss.xml"); ET.parse(ROOT/"sitemap.xml"); ET.parse(ROOT/"news-sitemap.xml")
    print(json.dumps({"status":"prepared","url":URL,"checks":checks},ensure_ascii=False,indent=2))


def main() -> int:
    make_social(); write(ARTICLE,article_html())
    sys.path.insert(0,str(ROOT/"scripts")); import publish_gymnastika_kadan_20260806 as helper
    helper.rebuild_surfaces(); ensure_article_sitemap(); helper.rebuild_integrity_manifest(); upsert_registry()
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_footers.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_articles.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/sort_articles_chronologically.py")],cwd=ROOT,check=True)
    normalize_generated_whitespace(); validate(); return 0

if __name__ == "__main__": raise SystemExit(main())
