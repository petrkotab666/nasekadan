#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / ".github/drafts/kadan-komunalni-volby-historie-20260808.html"
SLUG = "komunalni-volby-kadan-historie-1990-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
URL = f"https://nasekadan.cz/{ARTICLE_REL}"
SOCIAL_REL = f"social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL
SOCIAL_URL = f"https://nasekadan.cz/{SOCIAL_REL}"
TITLE = "36 let komunálních voleb v Kadani: vítězové, čtyři starostové, kupování hlasů i boj o rok 2026"
DESC = "Devět komunálních voleb, čtyři starostové, téměř nepřetržitá dominance ODS, soudní spor z roku 2010, další podezření z roku 2014 a politický souboj před volbami 2026 v Kadani."
PUBLISHED = "2026-08-08T04:00:00+02:00"
ARTICLE_SOURCE_COMMIT = os.environ.get("ARTICLE_SOURCE_COMMIT", "pending-publication-commit")
REQUIRED_HEADINGS = [
    "Výsledky voleb od roku 1990",
    "1990: první svobodné komunální volby",
    "1994: nastupuje ODS",
    "1998: jediná novodobá porážka ODS",
    "2002: návrat ODS a začátek Kulhánkovy éry",
    "2006: ODS prudce posiluje",
    "2010: téměř polovina hlasů — a největší volební aféra",
    "Právní paradox roku 2010",
    "Krupka změnila právní pohled",
    "Trestní zákon tehdy na kupování hlasů nestačil",
    "2014: ODS drží Kadaň, podezření se vrací",
    "2018: vrchol dominance ODS",
    "2022: konec dvacetileté Kulhánkovy éry",
    "Čtyři starostové po revoluci",
    "Co ukazuje více než třicet let voleb",
    "A co rok 2026? Kadaň jde do voleb po změně politické mapy",
    "Zdroje a ověření",
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    image = Image.new("RGB", (W, H), "#13232d")
    px = image.load()
    for y in range(H):
        for x in range(W):
            t = x / W
            px[x, y] = (int(19 * (1-t) + 127 * t), int(35 * (1-t) + 23 * t), int(45 * (1-t) + 32 * t))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((720, -180, 1350, 450), fill=(255,255,255,18))
    draw.rectangle((0,500,1200,630), fill=(0,0,0,50))
    draw.line((88,442,1112,442), fill=(255,255,255,95), width=3)
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fbig = ImageFont.truetype(bold, 76)
    fmid = ImageFont.truetype(bold, 28)
    fsmall = ImageFont.truetype(regular, 24)
    fyear = ImageFont.truetype(bold, 28)
    draw.rounded_rectangle((82,62,143,123), radius=16, fill=(169,35,43,255))
    draw.text((93,76), "NK", font=fmid, fill="white")
    draw.text((162,73), "NAŠE KADAŇ", font=fmid, fill="white")
    draw.text((86,165), "36 LET KOMUNÁLNÍCH", font=fbig, fill="white")
    draw.text((86,248), "VOLEB V KADANI", font=fbig, fill="white")
    draw.text((88,350), "Vítězové, čtyři starostové, soudní spor", font=fsmall, fill=(238,241,242,255))
    draw.text((88,384), "o hlasy a boj o rok 2026", font=fsmall, fill=(238,241,242,255))
    years = ["1990","1994","1998","2002","2006","2010","2014","2018","2022","2026"]
    x0, x1 = 92, 1108
    for i, year in enumerate(years):
        x = x0 + i * (x1-x0) / (len(years)-1)
        draw.ellipse((x-7,435,x+7,449), fill=(255,255,255,240))
        if year in {"1990","2010","2022","2026"}:
            draw.text((x-31,467), year, font=fyear, fill="white")
    for idx in (5,9):
        x = x0 + idx * (x1-x0) / (len(years)-1)
        draw.ellipse((x-13,429,x+13,455), outline=(201,164,90,255), width=4)
    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image.save(SOCIAL, format="PNG", optimize=True)


def schemas() -> str:
    news = {
        "@context":"https://schema.org","@type":"NewsArticle","headline":TITLE,"description":DESC,
        "datePublished":PUBLISHED,"dateModified":PUBLISHED,
        "author":{"@type":"Organization","@id":"https://nasekadan.cz/#organization","name":"Naše Kadaň","url":"https://nasekadan.cz/o-webu/"},
        "publisher":{"@id":"https://nasekadan.cz/#organization"},
        "mainEntityOfPage":{"@type":"WebPage","@id":URL},"image":[SOCIAL_URL],"inLanguage":"cs-CZ","isAccessibleForFree":True,
        "about":[{"@type":"Place","name":"Kadaň"},{"@type":"Thing","name":"Komunální volby"},{"@type":"Organization","name":"ODS"},{"@type":"Organization","name":"ANO 2011"},{"@type":"Person","name":"Jiří Kulhánek"},{"@type":"Person","name":"Jan Losenický"}]
    }
    crumbs = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Naše Kadaň","item":"https://nasekadan.cz/"},
        {"@type":"ListItem","position":2,"name":"Články","item":"https://nasekadan.cz/clanky/"},
        {"@type":"ListItem","position":3,"name":TITLE,"item":URL}]}
    return '<script data-nk-newsarticle="1" type="application/ld+json">'+json.dumps(news,ensure_ascii=False,separators=(",",":"))+'</script>\n<script data-nasekadan-breadcrumbs="1" type="application/ld+json">'+json.dumps(crumbs,ensure_ascii=False,separators=(",",":"))+'</script>'


def make_article() -> None:
    draft = DRAFT.read_text(encoding="utf-8")
    if 'data-do-not-shorten="true"' not in draft or TITLE not in draft:
        raise RuntimeError("Závazný draft není označen jako plný nebo nemá přesný H1.")
    for heading in REQUIRED_HEADINGS:
        if f">{heading}</h2>" not in draft:
            raise RuntimeError(f"V závazném draftu chybí kapitola: {heading}")
    m = re.search(r'<article\b[^>]*>(.*?)</article>', draft, re.I|re.S)
    if not m:
        raise RuntimeError("V draftu chybí článek.")
    inner = m.group(1).strip()
    original_text_bytes = len(inner.encode("utf-8"))
    hero = f'<img class="hero-image" src="/{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k 36 letům komunálních voleb v Kadani od roku 1990 do roku 2026">'
    inner, count = re.subn(r'(<p class="leadtext">.*?</p>)', r'\1\n'+hero, inner, count=1, flags=re.I|re.S)
    if count != 1:
        raise RuntimeError("Nepodařilo se vložit titulní grafiku bez zásahu do textu.")
    # Přidat přímé odkazy až za původní zdrojový seznam; původní text zůstává celý.
    source_links = '''<div class="source-links"><h3>Přímé odkazy na klíčové podklady</h3><ul>
<li><a href="https://www.zakonyprolidi.cz/judikat/ksul/15-a-91-2010-33" rel="noopener">Krajský soud v Ústí nad Labem: 15 A 91/2010-33 — Kadaň</a></li>
<li><a href="https://nalus.usoud.cz/Search/GetText.aspx?sz=Pl-57-10_2" rel="noopener">Ústavní soud: Pl. ÚS 57/10 — Krupka</a></li>
<li><a href="https://www.zakonyprolidi.cz/judikat/ksul/15-a-92-2010-118" rel="noopener">Krajský soud v Ústí nad Labem: 15 A 92/2010-118 — Krupka po nálezu ÚS</a></li>
<li><a href="https://policie.gov.cz/clanek/obvinen-za-kupceni-s-hlasy.aspx" rel="noopener">Policie ČR: prověřování komunálních voleb 2014 v Ústeckém kraji</a></li>
<li><a href="https://mv.gov.cz/npo/clanek/informace-o-podminkach-kandidatury-ve-volbach-do-zastupitelstev-obci-v-roce-2026.aspx" rel="noopener">Ministerstvo vnitra: kandidatura a termíny komunálních voleb 2026</a></li>
</ul></div>'''
    inner += "\n" + source_links
    if len(inner.encode("utf-8")) <= original_text_bytes:
        raise RuntimeError("Publikační transformace neočekávaně zkrátila plný text.")
    style = '''<style>
.article-shell{display:grid;grid-template-columns:minmax(0,840px) 300px;gap:36px;align-items:start;padding:54px 0 72px}.article{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}.article h1{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}.article h2{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}.article h3{font:800 24px/1.2 Georgia,serif}.article p,.article li{font-size:18px;line-height:1.7}.article a{color:#9f2626;text-underline-offset:3px}.tag{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}.leadtext{font-size:23px!important;color:#465862;line-height:1.52!important}.hero-image{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #16242d22}.fact-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:28px 0}.fact-card{background:#fff;border:1px solid #dde3e6;border-radius:18px;padding:22px;box-shadow:0 8px 25px #16242d0a}.fact-card span{display:block;color:#a9232b;font-weight:900;font-size:13px;letter-spacing:.06em;text-transform:uppercase}.fact-card strong{display:block;font:800 26px Georgia,serif;margin:7px 0}.fact-card p{margin:0;color:#52616a}.data-table{width:100%;border-collapse:collapse;margin:26px 0;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 10px 28px #16242d0d}.data-table th,.data-table td{padding:14px;border-bottom:1px solid #dde3e6;text-align:left;vertical-align:top}.data-table th{background:#14232d;color:#fff}.callout{border-left:6px solid #a9232b;background:#f3efe7;margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}.callout strong{font:800 24px Georgia,serif;display:block;margin-bottom:6px}.callout.final p{font:800 25px/1.4 Georgia,serif;margin:0}.timeline{margin:30px 0}.tl-row{display:grid;grid-template-columns:86px 1fr;gap:14px;border-top:1px solid #dde3e6;padding:15px 0}.tl-year{font-weight:900;color:#a9232b}.tl-row strong{font-family:Georgia,serif;font-size:20px}.source-list,.source-links{background:#eef3f5;padding:24px;border-radius:18px}.source-links{margin-top:18px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid #dde3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px}@media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}@media(max-width:680px){.article{padding:26px 20px}.fact-grid{grid-template-columns:1fr}.data-table{display:block;overflow-x:auto}.hero-image{border-radius:16px}}
</style>'''
    head = f'''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(TITLE)} | Naše Kadaň</title><meta name="description" content="{escape(DESC,quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260805-event-hotfix-3"><meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE,quote=True)}"><meta property="og:description" content="{escape(DESC,quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE,quote=True)}"><meta name="twitter:description" content="{escape(DESC,quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}"><link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">{schemas()}{style}</head><body>'''
    header = '''<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>'''
    aside = '''<aside class="sticky"><div class="sidebox"><h3>V kostce</h3><p><strong>1990–2022:</strong> devět komunálních voleb.</p><p><strong>ODS:</strong> vítěz všech voleb od roku 1994 kromě roku 1998.</p><p><strong>2010:</strong> soudní spor o tvrzené placení za hlasy.</p><p><strong>2026:</strong> někdejší společný politický okruh jde do voleb rozdělený.</p></div><div class="sidebox"><h3>Sledujeme dál</h3><ul><li>registraci kandidátek do 22. srpna</li><li>úplná jména a pořadí kandidátů</li><li>programy stran a uskupení</li><li>říjnový výsledek a novou povolební většinu</li></ul></div><div data-promos data-context="sidebar"></div></aside>'''
    sys.path.insert(0, str(ROOT / "scripts"))
    import publish_gymnastika_kadan_20260806 as helper
    output = head + header + '<main class="wrap article-shell" data-article-template="unified-v1"><article class="article">' + inner + '</article>' + aside + '</main>' + helper.footer() + '<script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script></body></html>'
    write(ARTICLE, output)


def upsert_registry() -> None:
    path = ROOT / "data/published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    entry = {
        "title":TITLE,"h1":TITLE,"url":URL,"published_at":PUBLISHED,"modified_at":PUBLISHED,
        "persons":["Václav Vaňas","Miloslav Müller","Jiří Kulhánek","Jan Losenický","Radek Oswald"],
        "organizations":["Město Kadaň","ODS","ČSSD","ANO 2011","Dáme Kadani novou šanci","Ústavní soud","Krajský soud v Ústí nad Labem","Policie České republiky","Naše Kadaň"],
        "places":["Kadaň","Krupka","Prunéřov"],
        "cases":["Komunální volby Kadaň 1990–2026","Soudní přezkum komunálních voleb Kadaň 2010","Podezření na ovlivňování voleb Kadaň 2014"],
        "topics":["Komunální volby","Historie komunální politiky","Kupování hlasů","Volební právo","Starostové Kadaně","Komunální volby 2026"],
        "fingerprint":sha256("kadan|komunalni-volby|historie|1990-2026|15-a-91-2010".encode()).hexdigest()[:24],
        "status":{"homepage":True,"archive":True,"rss":True,"sitemap":True,"news_sitemap":True},
        "source_path":ARTICLE_REL,"publication_status":"published","source_commit":ARTICLE_SOURCE_COMMIT,
    }
    existing = next((i for i in articles if i.get("url") == URL), None)
    if existing is None: articles.append(entry)
    else: existing.clear(); existing.update(entry)
    articles.sort(key=lambda i:i.get("published_at",""), reverse=True)
    urls=[i.get("url") for i in articles if i.get("url")]; fps=[i.get("fingerprint") for i in articles if i.get("fingerprint")]
    dup_urls=sorted({x for x in urls if urls.count(x)>1}); dup_fps=sorted({x for x in fps if fps.count(x)>1})
    if dup_urls or dup_fps: raise RuntimeError(f"Duplicita registru: URL={dup_urls}, fingerprinty={dup_fps}")
    now=datetime.now(timezone.utc).isoformat(); data["generated_at"]=now; data["article_count"]=len(articles)
    validation=data.setdefault("validation",{}); validation.update({"homepage_count":min(14,len(articles)),"archive_count":len(articles),"archive_page_count":(len(articles)+11)//12,"rss_count":(ROOT/"rss.xml").read_text(encoding="utf-8").count("<item>"),"sitemap_all_articles_present":True,"news_sitemap_recent_count":(ROOT/"news-sitemap.xml").read_text(encoding="utf-8").count("<news:news>"),"rss_order_matches_archive":True,"required_fields_complete":True,"duplicate_urls":dup_urls,"duplicate_fingerprints":dup_fps,"repair_pending_public_verification":True})
    validation["last_publication"]={"status":"prepared_for_publication","checked_at":now,"article_url":URL,"classification":"kadan_municipal_election_history","source_commit":ARTICLE_SOURCE_COMMIT,"public_verified_at":None}
    write(path,json.dumps(data,ensure_ascii=False,indent=2)+"\n")


def validate() -> None:
    text=ARTICLE.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if f">{heading}</h2>" not in text: raise RuntimeError(f"Po transformaci chybí kapitola: {heading}")
    checks={
        "h1": text.count(f"<h1>{TITLE}</h1>")==1,
        "indexable":"noindex" not in text.lower(),
        "canonical":f'<link rel="canonical" href="{URL}">' in text,
        "published":PUBLISHED in text,
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
    print(json.dumps({"status":"prepared","url":URL,"checks":checks,"required_headings":len(REQUIRED_HEADINGS)},ensure_ascii=False,indent=2))


def main() -> int:
    if ARTICLE.exists():
        current=ARTICLE.read_text(encoding="utf-8")
        if TITLE in current and all(f">{h}</h2>" in current for h in REQUIRED_HEADINGS):
            print("Cílový článek už existuje v plné podobě; povrchy budou jen idempotentně srovnány.")
    make_social(); make_article()
    sys.path.insert(0,str(ROOT/"scripts")); import publish_gymnastika_kadan_20260806 as helper
    helper.rebuild_surfaces(); helper.rebuild_integrity_manifest(); upsert_registry()
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_footers.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/normalize_articles.py"),"--write","--check"],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/sort_articles_chronologically.py")],cwd=ROOT,check=True)
    validate(); return 0

if __name__ == "__main__": raise SystemExit(main())
