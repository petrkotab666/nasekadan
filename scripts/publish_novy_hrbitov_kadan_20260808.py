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
SLUG = "novy-hrbitov-kadan-architektonicka-studie-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
URL = f"https://nasekadan.cz/{ARTICLE_REL}"
SOCIAL_REL = f"social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL
SOCIAL_URL = f"https://nasekadan.cz/{SOCIAL_REL}"
TITLE = "Kadaň posouvá plán nového hřbitova. Architektonická studie bude stát 580 tisíc korun"
DESC = "Město vybralo architekta pro studii nového hřbitova. Poslední veřejný odhad počítal s kapacitou současného pohřebiště pro pohřbívání do země zhruba do roku 2028."
PUBLISHED = "2026-08-08T11:21:00+02:00"
ARTICLE_SOURCE_COMMIT = os.environ.get("ARTICLE_SOURCE_COMMIT", "pending-publication-commit")

SOURCES = [
    ("https://smlouvy.gov.cz/smlouva/38990118", "Registr smluv: Zpracování architektonické studie „Nový hřbitov“"),
    ("https://sever.rozhlas.cz/kadan-hleda-pozemky-pro-novy-hrbitov-klasterec-nad-ohri-uz-na-rozsireni-sveho-9114061", "Český rozhlas Sever: Kadaň hledá pozemky pro nový hřbitov, 15. listopadu 2023"),
    ("https://sever.rozhlas.cz/kadansky-hrbitov-je-na-hrane-kapacity-mesto-musi-hledat-pozemky-pro-zalozeni-9110149", "Český rozhlas Sever: Kadaňský hřbitov je na hraně kapacity, 9. listopadu 2023"),
    ("https://gis.mesto-kadan.cz/portal/upd-kadan", "Městský GIS Kadaň: aktuální územní plánování"),
]

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    image = Image.new("RGB", (W, H), "#13252d")
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(H):
        t = y / H
        c = (int(19 + 34*t), int(37 + 34*t), int(45 + 29*t))
        draw.line((0, y, W, y), fill=(*c, 255))
    draw.rectangle((0, 500, 1200, 630), fill=(13, 24, 29, 190))
    draw.polygon([(820, 500), (1010, 500), (1120, 630), (700, 630)], fill=(216, 207, 183, 70))
    draw.rectangle((790, 145, 820, 500), fill=(233, 234, 228, 210))
    draw.rectangle((1030, 145, 1060, 500), fill=(233, 234, 228, 210))
    draw.arc((790, 105, 1060, 330), start=180, end=360, fill=(233,234,228,230), width=26)
    draw.line((925, 150, 925, 285), fill=(233,234,228,215), width=18)
    draw.line((870, 205, 980, 205), fill=(233,234,228,215), width=18)
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fbrand = ImageFont.truetype(bold, 23)
    fbig = ImageFont.truetype(bold, 57)
    fmid = ImageFont.truetype(bold, 30)
    fsmall = ImageFont.truetype(regular, 24)
    draw.rounded_rectangle((62, 54, 380, 105), radius=24, fill=(159,38,38,255))
    draw.text((85, 68), "NAŠE KADAŇ · INVESTICE", font=fbrand, fill="white")
    draw.text((62, 154), "KADAŇ PŘIPRAVUJE", font=fbig, fill="white")
    draw.text((62, 222), "NOVÝ HŘBITOV", font=fbig, fill="white")
    draw.text((65, 326), "Architektonická studie: 580 tisíc Kč bez DPH", font=fmid, fill=(248,220,156,255))
    draw.text((65, 382), "Kde vznikne, zatím veřejné podklady neříkají", font=fsmall, fill=(239,243,244,255))
    draw.text((65, 553), "NASEKADAN.CZ", font=fbrand, fill="white")
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
        "mainEntityOfPage":{"@type":"WebPage","@id":URL},
        "image":[SOCIAL_URL],"inLanguage":"cs-CZ","isAccessibleForFree":True,
        "about":[{"@type":"Place","name":"Kadaň"},{"@type":"Thing","name":"Nový hřbitov"},{"@type":"Person","name":"Vojtěch Hajný"}],
    }
    breadcrumbs = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Naše Kadaň","item":"https://nasekadan.cz/"},
        {"@type":"ListItem","position":2,"name":"Články","item":"https://nasekadan.cz/clanky/"},
        {"@type":"ListItem","position":3,"name":TITLE,"item":URL},
    ]}
    sources = "".join(f'<li><a href="{u}" rel="noopener">{escape(label)}</a></li>' for u,label in SOURCES)
    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title>
<meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260805-event-hotfix-3">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}">
<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',',':'))}</script>
<script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumbs, ensure_ascii=False, separators=(',',':'))}</script>
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,840px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,64px)/1.03 Georgia,serif;letter-spacing:-.038em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #16242d22}}.fact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:28px 0}}.fact{{background:#f5f0e8;border:1px solid #dfd3bf;border-radius:17px;padding:18px}}.fact strong{{display:block;color:#9f2626;font:900 25px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.callout{{border-left:7px solid #9f2626;background:#f7f1e7;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.neutral{{background:#eef3f5;border:1px solid #d5e0e4;border-radius:18px;padding:23px 25px;margin:30px 0}}.timeline{{border-left:4px solid #d7dde0;margin:30px 0;padding-left:24px}}.timeline div{{position:relative;padding:0 0 25px}}.timeline div:before{{content:'';position:absolute;left:-33px;top:7px;width:14px;height:14px;border-radius:50%;background:#9f2626;border:4px solid #fff}}.timeline b{{display:block;font:800 21px Georgia,serif}}.timeline p{{margin:5px 0}}.sources{{background:#eef3f5;padding:24px;border-radius:18px;margin-top:42px}}.sources h2{{margin-top:0}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dde3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:800 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:680px){{.article{{padding:26px 20px}}.fact-grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article">
<p class="tag">MĚSTO · INVESTICE · VEŘEJNÝ PROSTOR · 8. SRPNA 2026 · 11:21</p>
<h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>Kadaň udělala další konkrétní krok k novému hřbitovu. Rada města v červenci vybrala architekta Vojtěcha Hajného a v Registru smluv byla začátkem srpna zveřejněna smlouva na architektonickou studii za 580 tisíc korun bez DPH. Kde má nové pohřebiště vzniknout, ale z nyní dostupných veřejných podkladů stále není zřejmé.</strong></p>
<img class="hero-image" src="/{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k přípravě nového hřbitova v Kadani">
<div class="fact-grid"><div class="fact"><strong>580 000 Kč</strong><span>cena architektonické studie bez DPH</span></div><div class="fact"><strong>15. 7. 2026</strong><span>rada schválila výběr architekta</span></div><div class="fact"><strong>2028</strong><span>poslední veřejně uváděný horizont kapacity pro pohřbívání do země</span></div></div>

<h2>Rada vybrala architekta, smlouva už je zveřejněná</h2>
<p>Výpis z mimořádné schůze rady města z 15. července 2026 obsahuje usnesení č. 562/2026. Rada jím schválila rozhodnutí hodnotící komise pro akci <strong>„Zpracování architektonické studie Nový hřbitov“</strong> a uzavření smlouvy s Ing. arch. Vojtěchem Hajným.</p>
<p>V Registru smluv se následně 4. srpna objevil záznam smlouvy na stejnou studii. Uvedená hodnota je <strong>580 tisíc korun bez DPH</strong>. Nejde tedy už jen o obecnou úvahu, že Kadaň bude někdy potřebovat další pohřebiště: město přešlo k placené architektonické přípravě.</p>

<div class="neutral"><strong>Co zatím veřejné dokumenty neříkají:</strong><p>Samotné usnesení rady ani základní údaje smluvního záznamu neuvádějí konkrétní parcelu, požadovanou kapacitu, předpokládanou cenu budoucí stavby ani harmonogram její realizace. Naše Kadaň proto tyto údaje nebude domýšlet.</p></div>

<h2>Proč se nový hřbitov řeší</h2>
<p>Problém je známý nejméně od roku 2023. Český rozhlas Sever tehdy přímo na kadaňském hřbitově citoval starostu Jana Losenického, podle něhož měla volná místa pro klasické pohřbívání do země vystačit přibližně <strong>do roku 2028</strong>. Poté měla zůstávat kapacita především v kolumbáriích.</p>
<p>Čtyři až pět let přitom podle tehdejšího vyjádření nebyla velká rezerva. Před založením nového pohřebiště může být nutná změna územního plánu, získání povolení a následně také vybudování parkování, příjezdových cest a inženýrských sítí.</p>

<h2>Ve hře byly pozemky u současného hřbitova, směr Tušimice i Úhošťany</h2>
<p>V listopadu 2023 město nejprve prověřovalo možnost navázat na současný hřbitov. Problémem bylo vlastnictví okolních pozemků. Podle tehdejšího vyjádření vedení města požadoval jeden ze soukromých vlastníků přibližně desetinásobek odhadní ceny, a dohoda proto nevypadala reálně.</p>
<p>Jako další možnosti tehdy zazněla lokalita <strong>na opačné straně Kadaně, spíše při výjezdu směrem na Tušimice</strong>, a také <strong>Úhošťany</strong>. Město si tehdy nechávalo zpracovat studii, která měla hledat vhodné pozemky v jeho vlastnictví.</p>
<div class="callout"><strong>To ale neznamená, že už je rozhodnuto.</strong><p>Nová smlouva z roku 2026 sama o sobě nepotvrzuje, že se nynější architektonická studie týká právě jedné z těchto dříve zmiňovaných lokalit. Dokud nebude zveřejněné zadání studie nebo její výstup, jsou Tušimice a Úhošťany jen historicky doložené varianty.</p></div>

<h2>Od hledání pozemku k architektonické studii</h2>
<div class="timeline">
<div><b>Listopad 2023</b><p>Město veřejně upozorňuje na omezenou kapacitu současného hřbitova a hledá městské pozemky pro případné nové pohřebiště.</p></div>
<div><b>15. července 2026</b><p>Rada města vybírá Vojtěcha Hajného pro zpracování architektonické studie „Nový hřbitov“.</p></div>
<div><b>4. srpna 2026</b><p>V Registru smluv je zveřejněna smlouva na studii za 580 tisíc korun bez DPH.</p></div>
</div>

<h2>Co bude rozhodující dál</h2>
<p>Nejdůležitějším dokumentem bude samotné <strong>zadání architektonické studie</strong>. Z něj by mělo být patrné, jaké území má architekt řešit, jakou kapacitu město požaduje a co všechno má být součástí návrhu. Teprve poté půjde poctivě hodnotit také dopravní napojení, majetkové vztahy, soulad s územním plánem a budoucí investiční náklady.</p>
<p>Naše Kadaň bude proto dál hledat přílohu smlouvy, zadávací dokumentaci a podkladový materiál rady. Pokud z nich vyplyne konkrétní lokalita nebo rozsah projektu, tento článek aktualizujeme.</p>

<div class="sources"><h2>Zdroje a ověření</h2><p>Potvrzené údaje oddělujeme od starších veřejně zvažovaných variant. Cena a předmět nové studie vycházejí z Registru smluv; výběr dodavatele z usnesení rady města. Historické informace o kapacitě a variantách umístění byly veřejně popsány Českým rozhlasem Sever v listopadu 2023.</p><ul>{sources}</ul></div>
</article>
<aside class="sticky"><div class="sidebox"><h3>Co je potvrzené</h3><ul><li>rada vybrala architekta 15. července</li><li>smlouva byla zveřejněna 4. srpna</li><li>studie stojí 580 tisíc Kč bez DPH</li><li>konkrétní lokalita zatím není veřejně potvrzená</li></ul></div><div class="sidebox"><h3>Co budeme hlídat</h3><ul><li>zadání a výstup studie</li><li>konkrétní pozemky</li><li>kapacitu hrobových míst</li><li>parkování, příjezd a sítě</li><li>odhad ceny a harmonogram</li></ul></div><div data-promos data-context="sidebar"></div></aside></main>
{footer()}<script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script></body></html>'''

def upsert_registry() -> None:
    path = ROOT / "data/published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    entry = {
        "title":TITLE,"h1":TITLE,"url":URL,"published_at":PUBLISHED,"modified_at":PUBLISHED,
        "persons":["Vojtěch Hajný","Jan Losenický"],
        "organizations":["Město Kadaň","Naše Kadaň"],
        "places":["Kadaň","Tušimice","Úhošťany"],
        "cases":["Příprava nového hřbitova v Kadani"],
        "topics":["Hřbitov","Městské investice","Územní plánování","Veřejný prostor","Pohřebnictví"],
        "fingerprint":sha256("kadan|novy-hrbitov|architektonicka-studie|2026|vojtech-hajny".encode()).hexdigest()[:24],
        "status":{"homepage":True,"archive":True,"rss":True,"sitemap":True,"news_sitemap":True},
        "source_path":ARTICLE_REL,"publication_status":"published","source_commit":ARTICLE_SOURCE_COMMIT,
    }
    existing = next((i for i in articles if i.get("url") == URL), None)
    if existing is None: articles.append(entry)
    else: existing.clear(); existing.update(entry)
    articles.sort(key=lambda i:i.get("published_at",""), reverse=True)
    urls=[i.get("url") for i in articles if i.get("url")]
    fps=[i.get("fingerprint") for i in articles if i.get("fingerprint")]
    dup_urls=sorted({x for x in urls if urls.count(x)>1})
    dup_fps=sorted({x for x in fps if fps.count(x)>1})
    if dup_urls or dup_fps: raise RuntimeError(f"Duplicita registru: URL={dup_urls}, fingerprinty={dup_fps}")
    now=datetime.now(timezone.utc).isoformat()
    data["generated_at"]=now
    data["article_count"]=len(articles)
    validation=data.setdefault("validation",{})
    validation["last_publication"]={"status":"prepared_for_publication","checked_at":now,"article_url":URL,"classification":"municipal_investment_cemetery","source_commit":ARTICLE_SOURCE_COMMIT,"public_verified_at":None}
    write(path, json.dumps(data, ensure_ascii=False, indent=2)+"\n")

def validate() -> None:
    text=ARTICLE.read_text(encoding="utf-8")
    checks={
        "h1":text.count(f"<h1>{TITLE}</h1>")==1,
        "indexable":"noindex" not in text.lower(),
        "canonical":f'<link rel="canonical" href="{URL}">' in text,
        "social":SOCIAL.is_file(),
        "homepage":ARTICLE_REL in (ROOT/"index.html").read_text(encoding="utf-8"),
        "archive":ARTICLE_REL in (ROOT/"clanky/index.html").read_text(encoding="utf-8"),
        "rss":(ROOT/"rss.xml").read_text(encoding="utf-8").count(ARTICLE_REL)==1,
        "sitemap":(ROOT/"sitemap.xml").read_text(encoding="utf-8").count(ARTICLE_REL)==1,
        "news":(ROOT/"news-sitemap.xml").read_text(encoding="utf-8").count(ARTICLE_REL)==1,
        "llms":ARTICLE_REL in (ROOT/"llms.txt").read_text(encoding="utf-8"),
        "registry":URL in (ROOT/"data/published-content-index.json").read_text(encoding="utf-8"),
        "manifest":URL in (ROOT/"data/article-integrity-manifest.json").read_text(encoding="utf-8"),
    }
    from PIL import Image
    with Image.open(SOCIAL) as im: checks["social_dimensions"] = im.size == (1200,630)
    failed=[k for k,v in checks.items() if not v]
    if failed: raise RuntimeError("Neúplná zdrojová publikace: "+", ".join(failed))
    ET.parse(ROOT/"rss.xml"); ET.parse(ROOT/"sitemap.xml"); ET.parse(ROOT/"news-sitemap.xml")
    print(json.dumps({"status":"prepared","url":URL,"checks":checks},ensure_ascii=False,indent=2))

def main() -> int:
    make_social()
    write(ARTICLE, article_html())
    sys.path.insert(0, str(ROOT/"scripts"))
    import publish_gymnastika_kadan_20260806 as helper
    helper.rebuild_surfaces()
    helper.rebuild_integrity_manifest()
    upsert_registry()
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_footers.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_articles.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/sort_articles_chronologically.py")],cwd=ROOT,check=True)
    validate()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
