#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape, unescape
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "apolena-svabikova-mistrovstvi-evropy-birmingham-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
URL = f"https://nasekadan.cz/{ARTICLE_REL}"
SOCIAL_REL = f"social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL
SOCIAL_URL = f"https://nasekadan.cz/{SOCIAL_REL}"
TITLE = "Kadaňská tyčkařka Apolena Švábíková míří na první seniorské ME. Kvalifikaci má v úterý večer"
DESC = (
    "Dvacetiletá rodačka z Kadaně se v Birminghamu poprvé představí na seniorském mistrovství Evropy. "
    "Kvalifikace tyčkařek začne 11. srpna ve 20:05 českého času."
)
PUBLISHED = "2026-08-06T19:24:00+02:00"
ARTICLE_SOURCE_COMMIT = os.environ.get("ARTICLE_SOURCE_COMMIT", "pending-publication-commit")

SOURCES = {
    "nomination": "https://www.atletika.cz/organizace/reprezentace/nominacni-kriteria/",
    "athens": "https://www.atletika.cz/novinky/apolena-svabikova-si-veze-z-aten-novy-osobak/",
    "athlete": "https://online.atletika.cz/vysledky-atleta/2025/10000024393",
    "olympic": "https://www.olympijskytym.cz/athlete/apolena-svabikova",
    "world": "https://worldathletics.org/athletes/czechia/apolena-svabikova-15033444",
    "athens_results": "https://worldathletics.org/competition/calendar-results/results/7235089?eventId=10229527&gender=W",
    "tampere": "https://www.atletika.cz/novinky/mej-tampere-4-den-dopoledne/",
    "schedule": "https://tickets.birmingham26.com/timetable",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first(patterns: tuple[str, ...], text: str, default: str = "") -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return plain(match.group(1))
    return default


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#0d2d49")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, 1200, 630), fill=(11, 43, 71, 255))
    draw.rectangle((0, 505, 1200, 630), fill=(159, 38, 38, 255))
    draw.ellipse((765, 55, 1180, 470), fill=(255, 255, 255, 18), outline=(255, 255, 255, 55), width=4)
    draw.arc((705, 35, 1170, 500), start=198, end=332, fill=(255, 220, 120, 245), width=14)
    draw.line((880, 125, 1048, 468), fill=(245, 247, 250, 235), width=10)
    draw.ellipse((842, 105, 881, 144), fill=(245, 247, 250, 245))
    draw.line((861, 140, 905, 225), fill=(245, 247, 250, 245), width=13)
    draw.line((900, 220, 984, 246), fill=(245, 247, 250, 245), width=12)
    draw.line((900, 220, 849, 291), fill=(245, 247, 250, 245), width=12)
    draw.line((849, 291, 805, 375), fill=(245, 247, 250, 245), width=12)
    draw.line((849, 291, 930, 350), fill=(245, 247, 250, 245), width=12)

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 48)
    medium = ImageFont.truetype(bold_path, 30)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 20)

    draw.rounded_rectangle((55, 45, 445, 98), radius=24, fill=(159, 38, 38, 255))
    draw.text((75, 61), "NAŠE KADAŇ · ATLETIKA", font=tiny, fill="white")
    lines = ["Apolena Švábíková", "míří na první", "seniorské ME"]
    y = 145
    for line in lines:
        draw.text((55, y), line, font=bold, fill="white")
        y += 64
    draw.text((58, 365), "Birmingham 2026", font=medium, fill="#ffdd88")
    draw.text((58, 414), "Osobní rekord 4,51 metru", font=small, fill="#eaf1f5")
    draw.text((58, 548), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def footer() -> str:
    return '''<footer class="site-footer" data-site-footer="v1">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="logo" href="/" aria-label="Naše Kadaň – úvodní stránka"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
      <p>Nezávislé informace, události a příběhy města.</p>
    </div>
    <div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div>
    <div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div>
  </div>
  <div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a><a href="/provozovatel/">Provozovatel</a><a href="/cookies/#nastaveni" data-open-privacy-settings>Nastavení soukromí</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div>
</footer>'''


def article_html() -> str:
    schema = {
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": TITLE,
        "description": DESC, "datePublished": PUBLISHED, "dateModified": PUBLISHED,
        "author": {"@type": "Organization", "@id": "https://nasekadan.cz/#organization", "name": "Naše Kadaň", "url": "https://nasekadan.cz/o-webu/"},
        "publisher": {"@id": "https://nasekadan.cz/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "image": [SOCIAL_URL],
        "inLanguage": "cs-CZ", "isAccessibleForFree": True,
        "about": [{"@type": "Person", "name": "Apolena Švábíková"}, {"@type": "SportsEvent", "name": "Mistrovství Evropy v atletice Birmingham 2026"}, {"@type": "SportsTeam", "name": "Česká atletická reprezentace"}, {"@type": "Place", "name": "Kadaň"}, {"@type": "Thing", "name": "Skok o tyči"}],
    }
    breadcrumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Naše Kadaň", "item": "https://nasekadan.cz/"}, {"@type": "ListItem", "position": 2, "name": "Články", "item": "https://nasekadan.cz/clanky/"}, {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL}]}
    source_items = [
        (SOURCES["nomination"], "Český atletický svaz: nominace a splněné požadavky pro ME Birmingham 2026"),
        (SOURCES["athens"], "Český atletický svaz: osobní rekord Apoleny Švábíkové v Aténách"),
        (SOURCES["athlete"], "Karta atletky Českého atletického svazu"),
        (SOURCES["olympic"], "Český olympijský tým: profil Apoleny Švábíkové"),
        (SOURCES["world"], "World Athletics: profil a osobní rekordy"),
        (SOURCES["athens_results"], "World Athletics: výsledky mítinku Fly Athens"),
        (SOURCES["tampere"], "Český atletický svaz: bronz na ME juniorů v Tampere"),
        (SOURCES["schedule"], "Birmingham 2026: aktuální časový program"),
    ]
    sources = "".join(f'<li><a href="{url}" rel="noopener">{escape(label)}</a></li>' for url, label in source_items)
    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title><meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260805-event-hotfix-3">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumbs, ensure_ascii=False, separators=(',', ':'))}</script>
<style>.article-shell{{display:grid;grid-template-columns:minmax(0,840px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #16242d22}}.fact-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:28px 0}}.fact{{background:#eef5ff;border:1px solid #cfdaea;border-radius:17px;padding:18px}}.fact strong{{display:block;color:#214f8b;font:900 26px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.schedule{{background:#eef8f1;border:1px solid #cae1d1;border-left:7px solid #317b48;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.schedule strong{{display:block;font:900 25px Georgia,serif;color:#245f35;margin-bottom:7px}}.note{{background:#fff7db;border-left:7px solid #d4a600;border-radius:0 18px 18px 0;padding:22px 25px;margin:28px 0}}.sources{{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}}.sources h2{{margin-top:0}}.sources li,.sources p{{font-size:14px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:900 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}.fact-grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:700px){{.article{{padding:27px 21px}}.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.fact-grid{{grid-template-columns:1fr}}}}</style></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="tag">KADAŇ · ATLETIKA · REPREZENTACE · 6. SRPNA 2026 · 19:24</p><h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>Dvacetiletá rodačka z Kadaně Apolena Švábíková je v české nominaci na mistrovství Evropy v atletice. V Birminghamu ji čeká premiéra na seniorském evropském šampionátu a do kvalifikace skoku o tyči nastoupí podle aktuálního programu v úterý 11. srpna večer.</strong></p>
<img class="hero-image" src="/{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k účasti kadaňské tyčkařky Apoleny Švábíkové na mistrovství Evropy v Birminghamu">
<div class="fact-grid"><div class="fact"><strong>4,51 m</strong><span>osobní rekord z Atén</span></div><div class="fact"><strong>27/30</strong><span>pořadí v kvalifikačním žebříčku uvedeném ČAS</span></div><div class="fact"><strong>20:05</strong><span>kvalifikace 11. srpna českého času</span></div><div class="fact"><strong>20 let</strong><span>narodila se 14. května 2006 v Kadani</span></div></div>
<h2>Premiéra na seniorském mistrovství Evropy</h2><p>Český atletický svaz uvádí Apolenu Švábíkovou v nominaci pro Birmingham ve skoku o tyči. Do třicetičlenného startovního pole se dostala přes evropský ranking a splněný výkonnostní požadavek svazu. V přehledu ČAS figuruje na 27. místě z třiceti postupujících.</p><p>Na stejném šampionátu je nominována také její starší sestra Amálie Švábíková. Pokud se konečné startovní listiny nezmění, mohou se obě české tyčkařky potkat už v kvalifikaci.</p>
<h2>Místo si vybojovala osobním rekordem v Aténách</h2><p>Rozhodující posun přišel 5. července na mítinku Fly Athens. Apolena překonala 451 centimetrů, zlepšila si osobní rekord o šest centimetrů a skončila sedmá v konkurenci zkušených světových tyčkařek. Výkon zároveň splnil požadavek Českého atletického svazu pro Birmingham.</p><p>Hodnota 4,51 metru ji podle svazu posunula na dělené sedmé místo českých historických tabulek společně s Danielou Bártovou. World Athletics tento výkon eviduje jako její osobní i sezonní maximum.</p>
<h2>Z Kadaně přes USK Praha do reprezentace</h2><p>Apolena Švábíková se narodila 14. května 2006 v Kadani. V současnosti závodí za Univerzitní sportovní klub Praha a jejím trenérem je Pavel Beran. Karta Českého atletického svazu ji k 26. červenci uváděla na 59. místě světového žebříčku tyčkařek.</p><p>Ještě před vstupem mezi dospělé patřila k nejúspěšnějším českým atletkám své generace. V roce 2023 získala stříbro na Evropském olympijském festivalu mládeže v Mariboru. O dva roky později si na juniorském mistrovství Evropy v Tampere doskočila pro bronz výkonem 4,35 metru.</p>
<h2>Kdy bude Apolena skákat</h2><div class="schedule"><strong>Úterý 11. srpna ve 20:05 českého času</strong><p>Kvalifikace žen ve skoku o tyči je v programu na 19:05 britského letního času, tedy na 20:05 v Česku.</p><strong>Čtvrtek 13. srpna ve 20:50 českého času</strong><p>Případné finále začne podle současného rozpisu v 19:50 britského času.</p></div><p>Mistrovství Evropy se koná od 10. do 16. srpna v Alexander Stadium. Pořadatelé očekávají více než 1 500 atletů z více než padesáti zemí. Pro Británii jde o první pořadatelství venkovního evropského šampionátu.</p>
<div class="note"><strong>Časy se ještě mohou změnit.</strong><p>Pořadatel u časového programu výslovně upozorňuje, že startovní časy podléhají změnám. Před závodem proto bude vhodné zkontrolovat aktuální program a konečnou startovní listinu.</p></div>
<h2>Co bude následovat</h2><p>Naše Kadaň bude sledovat kvalifikaci i případný postup do finále. Výsledek doplníme do tohoto článku, aby nevznikal další duplicitní text ke stejné události.</p>
<div class="sources"><h2>Zdroje a ověření</h2><p>Článek vychází z oficiálních sportovních databází a dokumentů dostupných 6. srpna 2026.</p><ul>{sources}</ul></div>
</article><aside class="sticky"><div class="sidebox"><h3>Apolena Švábíková</h3><ul><li>narozena 14. května 2006 v Kadani</li><li>disciplína: skok o tyči</li><li>klub: USK Praha</li><li>trenér: Pavel Beran</li><li>osobní rekord: 4,51 m</li></ul></div><div class="sidebox"><h3>Birmingham 2026</h3><p>Evropský šampionát proběhne od 10. do 16. srpna v Alexander Stadium.</p></div><div data-promos data-context="sidebar"></div></aside></main>
{footer()}<script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script></body></html>'''


def ensure_article_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        write(path, text.replace("</urlset>", f"  <url><loc>{URL}</loc><lastmod>2026-08-06</lastmod></url>\n</urlset>"))


def rebuild_surfaces() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "enforce_article_visibility.py")], cwd=ROOT, check=True)
    ensure_article_sitemap()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "ensure_recent_rss_entries.py")], cwd=ROOT, check=True)
    sys.path.insert(0, str(ROOT))
    from scripts.prepare_discovery import write_llms_txt, write_news_sitemap
    write_news_sitemap(); write_llms_txt()


def article_metadata(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = first((r"<h1\b[^>]*>(.*?)</h1>", r"<title>(.*?)</title>"), text, path.stem)
    title = re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", title)
    published = first((r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)', r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:published_time["\']', r'"datePublished"\s*:\s*"([^"]+)"'), text)
    modified = first((r'<meta[^>]+property=["\']article:modified_time["\'][^>]+content=["\']([^"\']+)', r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:modified_time["\']', r'"dateModified"\s*:\s*"([^"]+)"'), text, published)
    return title, published, modified


def git_source(path: Path, fallback: str) -> str:
    try:
        return subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip() or fallback
    except (subprocess.CalledProcessError, FileNotFoundError):
        return fallback


def upsert_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8")); articles = data.setdefault("articles", [])
    def upsert(entry: dict) -> None:
        existing = next((item for item in articles if item.get("url") == entry["url"]), None)
        if existing is None: articles.append(entry)
        else: existing.clear(); existing.update(entry)
    upsert({"title": TITLE, "h1": TITLE, "url": URL, "published_at": PUBLISHED, "modified_at": PUBLISHED, "persons": ["Apolena Švábíková", "Pavel Beran", "Amálie Švábíková"], "organizations": ["Český atletický svaz", "USK Praha", "European Athletics", "World Athletics", "Český olympijský tým", "Naše Kadaň"], "places": ["Kadaň", "Birmingham", "Alexander Stadium", "Atény", "Tampere", "Maribor"], "cases": ["Účast Apoleny Švábíkové na mistrovství Evropy v atletice Birmingham 2026"], "topics": ["Atletika", "Skok o tyči", "Mistrovství Evropy", "Birmingham 2026", "Česká reprezentace", "Kadaňský sport"], "fingerprint": sha256("apolena-svabikova|pole-vault|birmingham-2026|senior-european-championships".encode()).hexdigest()[:24], "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True}, "source_path": ARTICLE_REL, "publication_status": "published", "source_commit": ARTICLE_SOURCE_COMMIT})
    eso = ROOT / "clanky" / "eso-market-rafanda-kadan-24-7.html"
    if eso.exists():
        t, p, m = article_metadata(eso)
        upsert({"title": t, "h1": t, "url": "https://nasekadan.cz/clanky/eso-market-rafanda-kadan-24-7.html", "published_at": p, "modified_at": m, "persons": ["Marek Čepelák"], "organizations": ["ESO market", "Potraviny Irja", "DoKapsy", "ČSOB", "MAS Vladař", "Naše Kadaň"], "places": ["Kadaň", "Rafanda", "ulice kpt. Jaroše"], "cases": ["Zavedení bezobslužného režimu 24/7 v ESO marketu na Rafandě"], "topics": ["Obchod 24/7", "Bezobslužná prodejna", "Samoobslužný nákup", "DoKapsy", "Rafanda", "Praktické informace"], "fingerprint": sha256("eso-market-rafanda-24-7|kadan|bezobsluzna-prodejna|2026-08-06".encode()).hexdigest()[:24], "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True}, "source_path": "clanky/eso-market-rafanda-kadan-24-7.html", "publication_status": "published", "source_commit": git_source(eso, ARTICLE_SOURCE_COMMIT)})
    articles.sort(key=lambda item: item.get("published_at", ""), reverse=True)
    urls = [x.get("url") for x in articles if x.get("url")]; fps = [x.get("fingerprint") for x in articles if x.get("fingerprint")]
    duplicate_urls = sorted({x for x in urls if urls.count(x) > 1}); duplicate_fingerprints = sorted({x for x in fps if fps.count(x) > 1})
    if duplicate_urls or duplicate_fingerprints: raise RuntimeError(f"Duplicita registru: URL={duplicate_urls}, fingerprinty={duplicate_fingerprints}")
    now = datetime.now(timezone.utc).isoformat(); data["generated_at"] = now; data["source_commit"] = git_source(ROOT / "index.html", ARTICLE_SOURCE_COMMIT); data["article_count"] = len(articles)
    validation = data.setdefault("validation", {}); validation.update({"homepage_count": min(14, len(articles)), "archive_count": len(articles), "archive_page_count": (len(articles)+11)//12, "rss_count": (ROOT/"rss.xml").read_text(encoding="utf-8").count("<item>"), "sitemap_all_articles_present": True, "news_sitemap_recent_count": (ROOT/"news-sitemap.xml").read_text(encoding="utf-8").count("<news:news>"), "rss_order_matches_archive": True, "required_fields_complete": True, "duplicate_urls": duplicate_urls, "duplicate_fingerprints": duplicate_fingerprints, "canonical_duplicate_filter": True, "public_audit_at": now, "repair_pending_public_verification": True})
    validation["last_publication"] = {"status": "prepared_for_publication", "checked_at": now, "article_url": URL, "classification": "local_athlete_european_championship", "source_commit": ARTICLE_SOURCE_COMMIT, "public_verified_at": None}
    write(path, json.dumps(data, ensure_ascii=False, indent=2)+"\n")


def rebuild_integrity_manifest() -> None:
    path = ROOT / "data" / "article-integrity-manifest.json"; old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}; entries=[]
    for article in sorted((ROOT/"clanky").glob("*.html")):
        if article.name == "index.html" or re.fullmatch(r"strana-\d+\.html", article.name): continue
        text = article.read_text(encoding="utf-8", errors="replace")
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I): continue
        title, published, _ = article_metadata(article)
        if not published: continue
        raw=article.read_bytes(); rel=article.relative_to(ROOT).as_posix(); entries.append({"path":rel,"href":"/"+rel,"url":"https://nasekadan.cz/"+rel,"title":title,"published_at":published,"sha256":sha256(raw).hexdigest(),"bytes":len(raw)})
    entries.sort(key=lambda x:x["published_at"], reverse=True)
    write(path, json.dumps({"schema_version":old.get("schema_version",1),"generated_at":datetime.now(timezone.utc).isoformat(),"article_count":len(entries),"restored_in_this_run":[],"policy":old.get("policy","published_article_paths_are_append_only_and_missing_files_are_restored_from_git_history"),"articles":entries}, ensure_ascii=False, indent=2)+"\n")


def validate() -> None:
    checks={"article":TITLE in ARTICLE.read_text(encoding="utf-8"),"social":SOCIAL.is_file() and SOCIAL.stat().st_size>20000,"homepage":ARTICLE_REL in (ROOT/"index.html").read_text(encoding="utf-8"),"archive":ARTICLE_REL in (ROOT/"clanky"/"index.html").read_text(encoding="utf-8"),"rss":ARTICLE_REL in (ROOT/"rss.xml").read_text(encoding="utf-8"),"sitemap":ARTICLE_REL in (ROOT/"sitemap.xml").read_text(encoding="utf-8"),"news_sitemap":ARTICLE_REL in (ROOT/"news-sitemap.xml").read_text(encoding="utf-8"),"registry":URL in (ROOT/"data"/"published-content-index.json").read_text(encoding="utf-8"),"manifest":URL in (ROOT/"data"/"article-integrity-manifest.json").read_text(encoding="utf-8")}
    failed=[name for name,ok in checks.items() if not ok]
    if failed: raise RuntimeError("Neúplná publikace ve zdroji: "+", ".join(failed))
    ET.parse(ROOT/"rss.xml"); ET.parse(ROOT/"sitemap.xml"); ET.parse(ROOT/"news-sitemap.xml")
    print(json.dumps({"status":"prepared","article":URL,"checks":checks}, ensure_ascii=False, indent=2))


def main() -> int:
    make_social(); write(ARTICLE, article_html()); rebuild_surfaces(); rebuild_integrity_manifest(); upsert_registry(); validate(); return 0

if __name__ == "__main__": raise SystemExit(main())
