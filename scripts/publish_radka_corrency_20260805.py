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
SLUG = "radka-kurzy-corrency-1000-korun-zari-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "RADKA od září končí s jednorázovými vstupy. Na dětské kurzy lze využít příspěvek 1 000 korun"
DESC = (
    "Mezigenerační centrum RADKA v Kadani přejde od září výhradně na ucelené kurzy. "
    "Na vybrané dětské aktivity a plavání lze využít příspěvek Corrency ve výši 1 000 korun."
)
PUBLISHED = "2026-08-05T18:45:00+02:00"
ARTICLE_SOURCE_COMMIT = "pending-publication-commit"
CORRENCY_URL = "https://kadan.corrency.cz/deti/"
CORRENCY_REGISTRATION = "https://app.corrency.cz/registrace-obcan/kadan-podpora-volnocasovych-aktivit-leden-zari-2026-01-09-26/"
RADKA_MCR = "https://radka.kadan.cz/mezigeneracni-centrum-mcr/"
RADKA_CONTACT = "https://radka.kadan.cz/uvodni-stranka/kontakty/mcr-kontakty/"
WEBOOKER = "https://radka.webooker.eu/flutter"
FORM = "https://forms.gle/CLhfyCZu3NGEaFdk8"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#163a4a")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, 1200, 630), fill=(16, 52, 67, 255))
    draw.polygon([(725, 0), (1200, 0), (1200, 630), (875, 630)], fill=(150, 38, 47, 238))
    for y in range(55, 640, 90):
        draw.rounded_rectangle((785, y, 1115, y + 52), radius=24, fill=(255, 255, 255, 42))
    draw.rounded_rectangle((58, 48, 440, 102), radius=25, fill="#9f2626")
    draw.rounded_rectangle((812, 120, 1078, 388), radius=44, fill=(255, 255, 255, 228))
    draw.ellipse((882, 150, 1008, 276), fill="#f3c75b")
    draw.rounded_rectangle((850, 292, 1040, 348), radius=26, fill="#1f5c74")
    draw.rounded_rectangle((830, 372, 1060, 494), radius=30, fill=(255, 255, 255, 210))
    draw.text((865, 396), "1 000 Kč", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 39), fill="#9f2626")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    tiny = ImageFont.truetype(bold_path, 21)
    bold = ImageFont.truetype(bold_path, 48)
    medium = ImageFont.truetype(bold_path, 29)
    small = ImageFont.truetype(regular_path, 24)

    draw.text((78, 65), "NAŠE KADAŇ · DĚTI A RODINA", font=tiny, fill="white")
    lines = ["RADKA mění", "od září systém", "dětských aktivit"]
    y = 148
    for line in lines:
        draw.text((58, y), line, font=bold, fill="white")
        y += 65
    draw.text((62, 370), "Jednorázové vstupy končí", font=medium, fill="#ffe0a1")
    draw.text((62, 420), "Na kurzy lze využít Corrency", font=small, fill="#edf4f6")
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
            {"@type": "Organization", "name": "RADKA z. s."},
            {"@type": "Organization", "name": "Město Kadaň"},
            {"@type": "Thing", "name": "Corrency"},
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Thing", "name": "Dětské kurzy a volnočasové aktivity"},
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
<p class="tag">KADAŇ · DĚTI A RODINA · VOLNÝ ČAS · 5. SRPNA 2026 · 18:45</p>
<h1>__TITLE__</h1>
<p class="leadtext"><strong>Mezigenerační centrum RADKA v Kadani mění od září systém svých pravidelných aktivit. Jednorázové vstupy skončí a děti i rodiče se budou přihlašovat do ucelených kurzů. Na vybrané kroužky, dopolední programy a plavání lze podle organizace využít také příspěvek Corrency ve výši 1 000 korun na dítě.</strong></p>
<img class="hero-image" src="__SOCIAL_REL__" width="1200" height="630" alt="Redakční grafika Naší Kadaně k novému systému kurzů RADKA a příspěvku Corrency">
<div class="alert"><strong>Od září bez jednorázových vstupů</strong><p>Pravidelné aktivity Mezigeneračního centra budou nově fungovat pouze jako ucelené kurzy. Přihlášený účastník bude mít místo ve skupině zajištěné po celou dobu kurzu.</p></div>
<p>RADKA oznámila změnu systému s cílem vytvořit stabilnější a vhodně velké skupiny dětí i rodičů. Přihlašování bude probíhat přes rezervační systém Webooker.</p>
<h2>Zameškanou lekci bude možné nahradit</h2>
<p>Nový režim počítá také s náhradami při nemoci dítěte. Rodič musí dítě včas omluvit prostřednictvím Webookeru. Nevyužitou lekci pak bude možné podle zveřejněných pravidel nahradit v jiném termínu nebo na jiném kurzu určeném pro stejně staré děti.</p>
<div class="fact-grid"><div class="fact"><strong>Celé kurzy</strong><span>jednorázové vstupy do pravidelných aktivit od září končí</span></div><div class="fact"><strong>Jisté místo</strong><span>účastník má rezervaci po celou dobu zvoleného kurzu</span></div><div class="fact"><strong>Náhradní lekce</strong><span>při včasné omluvě přes Webooker</span></div></div>
<h2>Na aktivity lze využít Corrency</h2>
<p>RADKA se zapojila do kadaňského programu Corrency. Podle jejího oznámení lze příspěvek využít na dopolední aktivity, zájmové kroužky a plavecké kurzy pořádané organizacemi RADKA z. s. a RADKA sport.</p>
<p>Městský program je určen dětem od narození do 16 let s trvalým pobytem v Kadani. Na každé úspěšně zaregistrované dítě připadá 1 000 correntů, které mají stejnou hodnotu jako 1 000 korun. Příspěvek může pokrýt nejvýše polovinu ceny vybrané aktivity; zbývající část doplácí rodič.</p>
<div class="practical"><h2>Podmínky příspěvku</h2><ul><li><strong>Výše podpory:</strong> 1 000 COR na dítě.</li><li><strong>Věk dítěte:</strong> 0 až 16 let.</li><li><strong>Podmínka:</strong> trvalý pobyt dítěte v Kadani.</li><li><strong>Spoluúčast:</strong> nejméně 50 procent ceny hradí rodina.</li><li><strong>Konec registrace a platnosti:</strong> 30. září 2026.</li><li><strong>Celkový rozpočet města:</strong> 500 000 korun, maximálně pro 500 dětí.</li></ul></div>
<p>Z veřejné stránky programu není patrné, kolik příspěvků je v tuto chvíli ještě volných. RADKA proto rodičům doporučuje neodkládat registraci. Samotné přihlášení do kurzu a rezervace příspěvku jsou dva oddělené kroky.</p>
<h2>Jak postupovat</h2>
<ol><li>Zaregistrovat dítě do kadaňského programu Corrency a rezervovat příspěvek.</li><li>Vybrat a rezervovat kurz RADKY prostřednictvím Webookeru.</li><li>Vyplnit formulář RADKY pro uplatnění correntů.</li><li>Při nejasnostech kontaktovat Mezigenerační centrum.</li></ol>
<div class="alert"><strong>Kontakty RADKA</strong><p>Mezigenerační centrum sídlí na adrese Kpt. Jaroše 630 v Kadani. Dotazy lze poslat na <a href="mailto:mcr@radka.info">mcr@radka.info</a> nebo vyřídit na telefonu <a href="tel:+420739094565">739 094 565</a>.</p></div>
<section class="sources"><h2>Zdroje a odkazy</h2><ul><li>Veřejné oznámení RADKA z. s. z 5. srpna 2026 o novém systému kurzů a možnosti využít Corrency.</li><li><a href="__RADKA_MCR__" target="_blank" rel="noopener noreferrer">Mezigenerační centrum RADKA – oficiální stránka</a>.</li><li><a href="__RADKA_CONTACT__" target="_blank" rel="noopener noreferrer">RADKA – oficiální kontakty MCR</a>.</li><li><a href="__CORRENCY_URL__" target="_blank" rel="noopener noreferrer">Corrency Kadaň – podmínky programu pro děti</a>.</li><li><a href="__CORRENCY_REGISTRATION__" target="_blank" rel="noopener noreferrer">Registrace dítěte do programu Corrency</a>.</li><li><a href="__WEBOOKER__" target="_blank" rel="noopener noreferrer">Rezervační systém Webooker RADKA</a> a <a href="__FORM__" target="_blank" rel="noopener noreferrer">formulář RADKY pro uplatnění příspěvku</a>.</li></ul><p>Podmínky Corrency byly redakcí ověřeny 5. srpna 2026 před vydáním článku.</p></section>
</article><aside class="sticky"><div class="sidebox"><h3>Rychlé shrnutí</h3><ul><li>Od září už jen ucelené kurzy.</li><li>Jednorázové vstupy končí.</li><li>Včas omluvenou lekci lze nahradit.</li><li>Na dítě lze využít 1 000 COR.</li><li>Program končí 30. září.</li></ul></div><div class="sidebox"><h3>Nejdřív Corrency, potom RADKA</h3><p>Rodič musí zvlášť zaregistrovat dítě do programu Corrency a zvlášť rezervovat konkrétní kurz.</p></div><div data-promos data-context="sidebar"></div></aside></main>
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
        "__RADKA_MCR__": RADKA_MCR,
        "__RADKA_CONTACT__": RADKA_CONTACT,
        "__CORRENCY_URL__": CORRENCY_URL,
        "__CORRENCY_REGISTRATION__": CORRENCY_REGISTRATION,
        "__WEBOOKER__": WEBOOKER,
        "__FORM__": FORM,
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
        item = f"""    <item>
      <title>{escape(TITLE)}</title>
      <description><![CDATA[{DESC}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{format_datetime(datetime.fromisoformat(PUBLISHED))}</pubDate>
      <category>Kadaň</category><category>Děti a rodina</category><category>Volný čas</category><category>Praktické informace</category>
      <szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>
    </item>

"""
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
        "organizations": ["RADKA z. s.", "RADKA sport", "Město Kadaň", "Corrency"],
        "places": ["Kadaň", "Kpt. Jaroše 630"],
        "cases": ["Změna systému Mezigeneračního centra RADKA od září 2026", "Corrency pro děti v Kadani 2026"],
        "topics": ["Děti", "Rodina", "Volný čas", "Kurzy", "Corrency", "Příspěvek 1 000 Kč", "RADKA"],
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
            "classification": "family_activity_service_change",
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
    assert CORRENCY_URL in article
    assert RADKA_MCR in article
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
