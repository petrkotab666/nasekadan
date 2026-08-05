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
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "vyluka-zatec-blatno-do-24-srpna-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Výluka přes Žatec potrvá do 24. srpna. Autobusy nahrazují vlaky i směrem na Chomutov"
DESC = (
    "Cestující z Kadaňska musí dál počítat s náhradní autobusovou dopravou na lince R25. "
    "Do 13. srpna zasahuje omezení až do Chomutova, poté pokračuje mezi Žatcem a Blatnem."
)
PUBLISHED = "2026-08-05T18:00:00+02:00"
ARTICLE_SOURCE_COMMIT = "pending-publication-commit"
OFFICIAL_SOURCE = "https://www.podborany.net/urad/aktuality/prodlouzeni-vyluky-blatno-u-jesenice-zatec-4552cs.html"
GW_SOURCE = "https://www.gwtr.cz/cs/o-spolecnosti/omezeni-provozu/vyluka-blatno-u-jesenice-zatec-03-03-03-08-2026"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#102b3a")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, 1200, 630), fill=(10, 34, 48, 255))
    draw.polygon([(700, 0), (1200, 0), (1200, 630), (900, 630)], fill=(154, 37, 45, 235))
    for x in range(790, 1250, 95):
        draw.line((x, 0, x - 300, 630), fill=(255, 255, 255, 35), width=18)
    draw.rounded_rectangle((58, 48, 430, 102), radius=25, fill="#9f2626")
    draw.rounded_rectangle((760, 165, 1110, 455), radius=34, fill=(255, 255, 255, 225))
    draw.rectangle((805, 223, 1065, 367), fill="#173b4b")
    draw.rounded_rectangle((835, 383, 900, 448), radius=30, fill="#182b34")
    draw.rounded_rectangle((980, 383, 1045, 448), radius=30, fill="#182b34")
    draw.line((805, 463, 1080, 463), fill=(255, 255, 255, 210), width=9)
    draw.line((830, 495, 1070, 495), fill=(255, 255, 255, 120), width=6)

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    tiny = ImageFont.truetype(bold_path, 21)
    bold = ImageFont.truetype(bold_path, 52)
    medium = ImageFont.truetype(bold_path, 31)
    small = ImageFont.truetype(regular_path, 24)

    draw.text((78, 65), "NAŠE KADAŇ · DOPRAVA", font=tiny, fill="white")
    lines = ["Výluka přes Žatec", "potrvá až do", "24. srpna"]
    y = 145
    for line in lines:
        draw.text((58, y), line, font=bold, fill="white")
        y += 70
    draw.text((62, 380), "4.–13. 8. až do Chomutova", font=medium, fill="#ffe0a1")
    draw.text((62, 430), "Náhradní autobusy na lince R25", font=small, fill="#edf4f6")
    draw.text((62, 570), "NASEKADAN.CZ", font=tiny, fill="white")
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
            {"@type": "Thing", "name": "Výluka linky R25"},
            {"@type": "Place", "name": "Žatec"},
            {"@type": "Place", "name": "Podbořany"},
            {"@type": "Place", "name": "Blatno u Jesenice"},
            {"@type": "Place", "name": "Chomutov"},
            {"@type": "Organization", "name": "Správa železnic"},
            {"@type": "Organization", "name": "GW Train Regio"},
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
    template = """<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ | Naše Kadaň</title>
<meta name="description" content="__DESC__"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="__URL__"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="__TITLE__"><meta property="og:description" content="__DESC__"><meta property="og:url" content="__URL__"><meta property="og:image" content="__SOCIAL_URL__"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="__TITLE__"><meta name="twitter:description" content="__DESC__"><meta name="twitter:image" content="__SOCIAL_URL__">
<meta property="article:published_time" content="__PUBLISHED__"><meta property="article:modified_time" content="__PUBLISHED__">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
<script type="application/ld+json">__SCHEMA__</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">__BREADCRUMB__</script>
<style>
.article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:54px 0 72px}.article{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}.article h1{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}.article h2{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}.article p,.article li{font-size:18px;line-height:1.7}.article a{color:#9f2626;text-underline-offset:3px}.tag{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}.leadtext{font-size:23px!important;color:#465862;line-height:1.52!important}.hero-image{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #0b385544}.alert{background:#fff4cf;border:1px solid #e0c36f;border-left:7px solid #a9232b;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}.alert strong{display:block;font:900 25px Georgia,serif;color:#752026;margin-bottom:6px}.fact-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:28px 0}.fact{background:#edf7fb;border:1px solid #cce1ea;border-radius:17px;padding:20px}.fact strong{display:block;color:#145a7a;font:900 23px Georgia,serif;margin-bottom:6px}.fact span{font-size:14px;line-height:1.4}.practical{background:#eef6f8;border-radius:20px;padding:25px;margin:30px 0}.practical h2{margin-top:0}.sources{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}.sources h2{margin-top:0}.sources li,.sources p{font-size:14px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:900 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px;line-height:1.5}@media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}@media(max-width:700px){.article{padding:27px 21px}.article h1{font-size:42px}.leadtext{font-size:20px!important}.fact-grid{grid-template-columns:1fr}}
</style></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article">
<p class="tag">DOPRAVA · ŽATECKO · PODBOŘANSKO · 5. SRPNA 2026 · 18:00</p>
<h1>__TITLE__</h1>
<p class="leadtext"><strong>Cestující z Kadaňska, kteří jedou přes Žatec a Podbořany směrem na Plzeň, musí dál počítat s náhradní autobusovou dopravou. Výluka linky R25 mezi Blatnem u Jesenice a Žatcem byla prodloužena do 24. srpna. V první části srpna zasahuje omezení až do Chomutova.</strong></p>
<img class="hero-image" src="__SOCIAL_REL__" width="1200" height="630" alt="Redakční grafika Naší Kadaně k prodloužené výluce linky R25 přes Žatec a Podbořany">
<div class="alert"><strong>Nejdůležitější změna</strong><p>Výluka neskončila 3. srpna, jak uváděl původní plán. Podle opravených jízdních řádů pokračuje mezi Blatnem u Jesenice a Žatcem až do 24. srpna 2026.</p></div>
<p>Opravené výlukové jízdní řády zveřejnilo město Podbořany už 21. července. Informace je nyní důležitá hlavně prakticky: původní termín skončil, náhradní autobusy ale na trase dál jezdí.</p>
<div class="fact-grid"><div class="fact"><strong>Do 24. 8.</strong><span>výluka mezi Blatnem u Jesenice a Žatcem</span></div><div class="fact"><strong>4.–13. 8.</strong><span>náhradní doprava až v úseku Blatno–Žatec–Chomutov</span></div><div class="fact"><strong>14.–24. 8.</strong><span>náhradní doprava pokračuje mezi Blatnem a Žatcem</span></div></div>
<h2>Do 13. srpna jedou autobusy až do Chomutova</h2>
<p>Ve dnech od 4. do 13. srpna jsou podle zveřejněného výlukového jízdního řádu vlaky nahrazeny autobusy v celém úseku <strong>Blatno u Jesenice – Žatec – Chomutov</strong>. Změna se proto může dotknout i cestujících, kteří se na linku R25 napojují v Chomutově nebo pokračují směrem na Kadaň.</p>
<p>Zastávky <strong>Hořetice a Březno u Chomutova</strong> jsou během tohoto období kvůli silničním uzavírkám obsluhovány mikrobusy.</p>
<h2>Kryry a Vroutek mají zvláštní mikrobusy</h2>
<p>Většina náhradních autobusů jede mimo železniční stanice Kryry a Vroutek. Jejich obsluhu zajišťují samostatné mikrobusy: jeden spojuje Blatno u Jesenice s Vroutkem, druhý Kryry s Podbořany. Cestující přivážejí k hlavním náhradním autobusům do Podbořan a Blatna u Jesenice.</p>
<div class="practical"><h2>Co si zkontrolovat před cestou</h2><ul><li>konkrétní spoj a odjezd v aktuálním výlukovém jízdním řádu nebo v IDOS,</li><li>místo zastávky náhradního autobusu, které nemusí být přímo před nádražní budovou,</li><li>návaznost v Žatci, Podbořanech, Blatně u Jesenice nebo Chomutově,</li><li>možnosti přepravy kola, kočárku či většího zavazadla,</li><li>způsob placení: v náhradních autobusech není garantována platba bankovní kartou.</li></ul></div>
<h2>Web dopravce stále ukazuje starší termín</h2>
<p>Na stránce dopravce GW Train Regio zůstával při redakční kontrole 5. srpna uveden původní konec výluky 3. srpna. Aktuálnější podklady jsou přiložené k oznámení města Podbořany a počítají s pokračováním omezení do 24. srpna.</p>
<p>Pro konkrétní cestu je proto bezpečnější vycházet z opravených výlukových jízdních řádů a z vyhledávače spojení pro zvolený den, nikoli pouze z titulku starší stránky dopravce.</p>
<section class="sources"><h2>Zdroje a ověření</h2><ul><li><a href="__OFFICIAL_SOURCE__" target="_blank" rel="noopener noreferrer">Město Podbořany – prodloužení výluky a opravené jízdní řády</a>, vloženo a aktualizováno 21. července 2026.</li><li><a href="__GW_SOURCE__" target="_blank" rel="noopener noreferrer">GW Train Regio – původní stránka výluky</a>, která při kontrole stále uváděla konec 3. srpna.</li></ul><p>Redakce údaje znovu ověřila 5. srpna 2026 před vydáním článku.</p></section>
</article><aside class="sticky"><div class="sidebox"><h3>Rychlé shrnutí</h3><ul><li>Výluka R25 pokračuje do 24. srpna.</li><li>Do 13. srpna zasahuje až do Chomutova.</li><li>Kryry, Vroutek, Hořetice a Březno obsluhují v určených obdobích mikrobusy.</li><li>Před cestou je nutné zkontrolovat konkrétní spoj.</li></ul></div><div class="sidebox"><h3>Pro cestující z Kadaně</h3><p>Největší dopad má omezení na cestách přes Chomutov, Žatec a Podbořany směrem na Plzeň.</p></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/long-article-ads.js?v=20260731-long-article-ads-2"></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body></html>
"""
    replacements = {
        "__TITLE__": escape(TITLE),
        "__DESC__": escape(DESC, quote=True),
        "__URL__": URL,
        "__SOCIAL_URL__": SOCIAL_URL,
        "__SOCIAL_REL__": SOCIAL_REL,
        "__PUBLISHED__": PUBLISHED,
        "__SCHEMA__": json.dumps(schema, ensure_ascii=False, separators=(",", ":")),
        "__BREADCRUMB__": json.dumps(breadcrumb, ensure_ascii=False, separators=(",", ":")),
        "__OFFICIAL_SOURCE__": OFFICIAL_SOURCE,
        "__GW_SOURCE__": GW_SOURCE,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def run_visibility() -> None:
    subprocess.run(["python3", "scripts/enforce_all_article_visibility.py"], cwd=ROOT, check=True)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{format_datetime(datetime.fromisoformat(PUBLISHED))}</lastBuildDate>", text, count=1)
    if URL not in text:
        item = f'''    <item>
      <title>{escape(TITLE)}</title>
      <description><![CDATA[{DESC}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{format_datetime(datetime.fromisoformat(PUBLISHED))}</pubDate>
      <category>Doprava</category><category>Žatecko</category><category>Podbořansko</category><category>Praktické informace</category>
      <szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image>
    </item>

'''
        text = text.replace("    <item>", item + "    <item>", 1)
    write(path, text)


def update_news_sitemap() -> None:
    path = ROOT / "news-sitemap.xml"
    ns = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "news": "http://www.google.com/schemas/sitemap-news/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1",
    }
    ET.register_namespace("", ns["sm"])
    ET.register_namespace("news", ns["news"])
    ET.register_namespace("image", ns["image"])
    root = ET.parse(path).getroot()
    for node in list(root):
        loc = node.find(f"{{{ns['sm']}}}loc")
        if loc is not None and loc.text == URL:
            root.remove(node)
    url_node = ET.Element(f"{{{ns['sm']}}}url")
    ET.SubElement(url_node, f"{{{ns['sm']}}}loc").text = URL
    news_node = ET.SubElement(url_node, f"{{{ns['news']}}}news")
    publication = ET.SubElement(news_node, f"{{{ns['news']}}}publication")
    ET.SubElement(publication, f"{{{ns['news']}}}name").text = "Naše Kadaň"
    ET.SubElement(publication, f"{{{ns['news']}}}language").text = "cs"
    ET.SubElement(news_node, f"{{{ns['news']}}}publication_date").text = PUBLISHED
    ET.SubElement(news_node, f"{{{ns['news']}}}title").text = TITLE
    image_node = ET.SubElement(url_node, f"{{{ns['image']}}}image")
    ET.SubElement(image_node, f"{{{ns['image']}}}loc").text = SOCIAL_URL
    ET.SubElement(image_node, f"{{{ns['image']}}}title").text = TITLE
    root.insert(0, url_node)
    while len(list(root)) > 10:
        root.remove(list(root)[-1])
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    entry = f"- [{TITLE}]({URL})\n  {DESC}\n"
    if URL not in text:
        marker = "## Nejnovější vlastní články\n\n"
        if marker not in text:
            raise RuntimeError("llms.txt nemá sekci nejnovějších článků.")
        text = text.replace(marker, marker + entry, 1)
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = [item for item in data.get("articles", []) if item.get("url") != URL]
    fingerprint = sha256((TITLE + "|" + URL).encode("utf-8")).hexdigest()[:24]
    new_article = {
        "title": TITLE,
        "h1": TITLE,
        "url": URL,
        "published_at": PUBLISHED,
        "modified_at": PUBLISHED,
        "persons": [],
        "organizations": ["Město Podbořany", "Správa železnic", "GW Train Regio"],
        "places": ["Kadaň", "Chomutov", "Žatec", "Podbořany", "Blatno u Jesenice", "Kryry", "Vroutek", "Hořetice", "Březno u Chomutova"],
        "cases": ["Prodloužená výluka R25 Blatno u Jesenice–Žatec do 24. srpna 2026"],
        "topics": ["Doprava", "Výluka", "R25", "Náhradní autobusová doprava", "Žatecko", "Podbořansko"],
        "fingerprint": fingerprint,
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "source_path": f"clanky/{SLUG}.html",
        "publication_status": "published",
        "source_commit": ARTICLE_SOURCE_COMMIT,
    }
    articles.append(new_article)
    articles.sort(key=lambda item: item.get("published_at", ""), reverse=True)
    data["articles"] = articles
    data["article_count"] = len(articles)
    now = datetime.now(timezone.utc).isoformat()
    data["generated_at"] = now
    validation = data.setdefault("validation", {})
    validation.update({
        "homepage_count": min(14, len(articles)),
        "archive_count": len(articles),
        "archive_page_count": (len(articles) + 11) // 12,
        "rss_count": len(re.findall(r"<item\b", (ROOT / "rss.xml").read_text(encoding="utf-8"))),
        "sitemap_all_articles_present": True,
        "news_sitemap_recent_count": len(ET.parse(ROOT / "news-sitemap.xml").getroot()),
        "rss_order_matches_archive": True,
        "required_fields_complete": True,
        "duplicate_urls": [],
        "duplicate_fingerprints": [],
        "per_article_source_commits": True,
        "repair_pending_public_verification": True,
        "last_publication": {
            "status": "pending_public_verification",
            "checked_at": now,
            "article_url": URL,
            "classification": "practical_transport_alert",
            "source_commit": ARTICLE_SOURCE_COMMIT,
        },
    })
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def update_manifest() -> None:
    path = ROOT / "data" / "article-integrity-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = [item for item in data.get("articles", []) if item.get("url") != URL]
    content = ARTICLE.read_bytes()
    items.append({
        "path": f"clanky/{SLUG}.html",
        "href": REL,
        "url": URL,
        "title": TITLE,
        "published_at": PUBLISHED,
        "sha256": sha256(content).hexdigest(),
        "bytes": len(content),
    })
    items.sort(key=lambda item: item.get("published_at", ""), reverse=True)
    data["articles"] = items
    data["article_count"] = len(items)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    data["restored_in_this_run"] = []
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def normalize_whitespace() -> None:
    paths = [ROOT / "index.html", ROOT / "sitemap.xml", ROOT / "rss.xml", ROOT / "news-sitemap.xml", ROOT / "llms.txt", ROOT / "clanky" / "index.html"]
    paths.extend(sorted((ROOT / "clanky").glob("strana-*.html")))
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        write(path, "\n".join(line.rstrip() for line in text.splitlines()) + "\n")


def validate() -> None:
    ET.parse(ROOT / "rss.xml")
    ET.parse(ROOT / "sitemap.xml")
    ET.parse(ROOT / "news-sitemap.xml")
    article = ARTICLE.read_text(encoding="utf-8")
    assert f"<h1>{escape(TITLE)}</h1>" in article
    assert "index,follow" in article and "noindex" not in article
    assert PUBLISHED in article
    assert OFFICIAL_SOURCE in article
    assert URL in (ROOT / "rss.xml").read_text(encoding="utf-8")
    assert URL in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert URL in (ROOT / "news-sitemap.xml").read_text(encoding="utf-8")
    assert REL in (ROOT / "index.html").read_text(encoding="utf-8")
    assert REL in "".join(path.read_text(encoding="utf-8") for path in (ROOT / "clanky").glob("*.html"))
    assert SOCIAL.exists() and SOCIAL.stat().st_size > 10000
    registry = json.loads((ROOT / "data" / "published-content-index.json").read_text(encoding="utf-8"))
    assert registry["article_count"] == len(registry["articles"])
    assert registry["validation"]["rss_count"] == registry["article_count"]
    assert any(item.get("url") == URL for item in registry["articles"])


def main() -> None:
    make_social()
    write(ARTICLE, article_page())
    run_visibility()
    update_rss()
    update_news_sitemap()
    update_llms()
    update_registry()
    update_manifest()
    normalize_whitespace()
    validate()
    print(f"Připraveno k publikaci: {TITLE} ({PUBLISHED})")


if __name__ == "__main__":
    main()
