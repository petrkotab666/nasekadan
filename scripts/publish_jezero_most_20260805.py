#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
from math import ceil
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "jezero-most-patrani-dva-lide-bourka-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Na jezeře Most pátrají po dvou lidech. Kvůli bouřce se neměli dostat na břeh"
DESC = (
    "Policie podle CNN Prima NEWS a Mosteckého deníku pátrá po dvou lidech na jezeře Most. "
    "Silná bouřka jim měla zabránit v návratu na břeh. K jezeru jezdí také lidé z Kadaně."
)
PUBLISHED = "2026-08-05T10:50:00+02:00"
MODIFIED = PUBLISHED
RSS_DATE = "Wed, 05 Aug 2026 10:50:00 +0200"
FINGERPRINT = sha256(
    "jezero-most|patrani-dva-lide|silna-bourka|bezpecnost-u-vody|vazba-kadan".encode("utf-8")
).hexdigest()[:24]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#071a2b")
    draw = ImageDraw.Draw(image)
    for y in range(630):
        ratio = y / 629
        draw.line((0, y, 1200, y), fill=(7 + int(12 * ratio), 26 + int(18 * ratio), 43 + int(30 * ratio)))
    draw.rectangle((0, 425, 1200, 630), fill="#0b3550")
    for y in range(440, 630, 24):
        offset = (y // 24) % 2 * 30
        for x in range(-60 + offset, 1200, 120):
            draw.arc((x, y, x + 150, y + 48), 195, 345, fill="#4f89a5", width=4)
    draw.polygon([(935, 55), (820, 260), (890, 250), (790, 425), (1010, 190), (925, 205)], fill="#f7d56f")
    draw.polygon([(0, 470), (180, 438), (340, 455), (505, 420), (700, 465), (1200, 405), (1200, 630), (0, 630)], fill="#08151d")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 55)
    medium = ImageFont.truetype(bold_path, 30)
    small = ImageFont.truetype(regular_path, 24)
    tiny = ImageFont.truetype(bold_path, 21)
    draw.rounded_rectangle((58, 48, 420, 102), radius=27, fill="#a9232b")
    draw.text((82, 65), "NAŠE KADAŇ · AKTUÁLNĚ", font=tiny, fill="white")
    y = 142
    for line in ["Na jezeře Most", "pátrají po", "dvou lidech"]:
        draw.text((60, y), line, font=bold, fill="white")
        y += 72
    draw.text((64, 378), "Silná bouřka jim měla zabránit", font=medium, fill="#ffe5a3")
    draw.text((64, 420), "v návratu na břeh", font=medium, fill="#ffe5a3")
    draw.text((64, 548), "ZPRÁVU SLEDUJEME I PRO ČTENÁŘE Z KADANĚ", font=small, fill="#dceaf0")
    draw.text((64, 588), "NASEKADAN.CZ", font=tiny, fill="white")
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
            {"@type": "Place", "name": "Jezero Most"},
            {"@type": "Place", "name": "Most"},
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Thing", "name": "Pátrání po dvou pohřešovaných lidech"},
            {"@type": "Thing", "name": "Silná bouřka"},
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
<meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}">
<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{MODIFIED}">
<link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626"><link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
<script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script>
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #0b385544}}.status-box{{background:#fff4cf;border:1px solid #e0c36f;border-left:7px solid #a9232b;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.status-box strong{{display:block;font:900 25px Georgia,serif;color:#752026;margin-bottom:6px}}.fact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:28px 0}}.fact{{background:#edf7fb;border:1px solid #cce1ea;border-radius:17px;padding:20px}}.fact strong{{display:block;color:#145a7a;font:900 25px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.neighbor-note{{background:#fff3f3;border:1px solid #e8c7ca;border-left:7px solid #a9232b;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.neighbor-note strong{{display:block;font:900 25px Georgia,serif;color:#85202a;margin-bottom:6px}}.known{{background:#eef6f8;border-radius:20px;padding:25px;margin:30px 0}}.known h2{{margin-top:0}}.known-grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}.known-card{{background:#fff;border:1px solid #d7e2e6;border-radius:15px;padding:18px}}.known-card h3{{font:900 22px Georgia,serif;margin:0 0 8px}}.sources{{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}}.sources h2{{margin-top:0}}.sources li,.sources p{{font-size:14px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:900 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:700px){{.article{{padding:27px 21px}}.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.fact-grid,.known-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article">
<p class="tag">OD SOUSEDŮ · MOST · AKTUÁLNĚ · 5. SRPNA 2026 · 10:50</p>
<h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>Policisté podle CNN Prima NEWS a Mosteckého deníku pátrají po dvou lidech na jezeře Most. Silná bouřka jim měla zabránit v návratu na břeh. Noční pátrání bylo podle zveřejněných informací přerušeno kvůli tmě. Výsledek pátrání nebyl v době vydání veřejně potvrzen.</strong></p>
<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika Naší Kadaně k pátrání po dvou lidech na jezeře Most během silné bouřky">
<div class="status-box"><strong>Aktuální stav k 10:50</strong><p>Dva nezávislé mediální zdroje popisují stejnou událost. Policie ani hasiči však zatím nezveřejnili samostatnou veřejnou zprávu s totožností pohřešovaných, přesným průběhem nebo výsledkem pátrání. Článek proto uvádí pouze potvrzené mediální informace a jasně odděluje to, co zatím známé není.</p></div>
<p>Na ověřené facebookové stránce CNN Prima NEWS se v úterý dopoledne objevila informace, že policisté pátrají po dvou pohřešovaných lidech. Podle grafiky televize se dvojice kvůli silné bouřce nemohla dostat na břeh jezera Most.</p>
<p>Mostecký deník současně uvedl, že se na jezeře pohřešují dva lidé a že pátrání bylo během noci přerušeno kvůli tmě. Veřejně zatím není potvrzeno, zda byli pohřešovaní ve vodě, na paddleboardu, kajaku, šlapadle nebo jiném plavidle.</p>
<div class="fact-grid"><div class="fact"><strong>2 lidé</strong><span>počet pohřešovaných uváděný oběma médii</span></div><div class="fact"><strong>Silná bouřka</strong><span>podle CNN Prima NEWS měla zabránit návratu na břeh</span></div><div class="fact"><strong>Výsledek neznámý</strong><span>k 10:50 nebylo nalezení dvojice veřejně potvrzeno</span></div></div>
<div class="neighbor-note"><strong>Proč zprávu přinášíme i v Kadani</strong><p>Jezero Most je oblíbeným místem pro koupání, výlety a vodní sporty v celém severozápadním regionu. K vodě pravidelně míří také návštěvníci z Kadaně a Chomutovska. Událost proto není jen vzdálenou mosteckou zprávou, ale týká se místa, které zná a navštěvuje řada našich čtenářů.</p></div>
<h2>Co je potvrzené a co zatím chybí</h2>
<div class="known"><div class="known-grid"><div class="known-card"><h3>Potvrzují média</h3><ul><li>policie pátrá po dvou lidech,</li><li>událost se odehrála na jezeře Most,</li><li>dvojici měla návrat komplikovat silná bouřka,</li><li>noční pátrání podle Deníku přerušila tma.</li></ul></div><div class="known-card"><h3>Zatím není veřejně potvrzeno</h3><ul><li>totožnost, věk ani fotografie pohřešovaných,</li><li>na jakém prostředku nebo v jaké části jezera byli,</li><li>přesný čas oznámení,</li><li>zda byli nalezeni a v jakém stavu.</li></ul></div></div></div>
<h2>Otevřená vodní plocha se při bouřce rychle mění</h2>
<p>Jezero Most využívají plavci, paddleboardisté, kajakáři i návštěvníci půjčoven šlapadel. Na otevřené hladině se při bouřce mohou během krátké doby zhoršit dohlednost, vítr i vlnění. Při rychlém příchodu bouřky je bezpečnější vodu okamžitě opustit a nečekat, zda se počasí uklidní.</p>
<p><strong>Naše Kadaň bude zprávu průběžně aktualizovat. Jakmile policie, hasiči nebo další důvěryhodný zdroj zveřejní výsledek pátrání, doplníme jej do tohoto článku, nikoli do nové duplicitní zprávy.</strong></p>
<section class="sources"><h2>Zdroje a ověření</h2><ul><li><a href="https://www.facebook.com/CNNPrimaNEWS/" rel="nofollow noopener">CNN Prima NEWS – ověřená facebooková stránka, příspěvek k pátrání na jezeře Most</a></li><li><a href="https://mostecky.denik.cz/" rel="nofollow noopener">Mostecký deník – „Po bouřce na jezeře Most se pohřešují dva lidé. Pátrání přes noc přerušila tma“</a></li><li><a href="https://mostecky.denik.cz/zpravy_region/most-jezero-obcerstveni-koupani-ceny-20260523.html" rel="nofollow noopener">Mostecký deník – jezero jako regionální cíl pro koupání a vodní sporty</a></li><li><a href="https://mosteckejezero.com/poznej-jezero-most/" rel="nofollow noopener">Jezero Most – informace pro návštěvníky</a></li></ul><p>Redakce stav ověřila 5. srpna 2026 v 10:50. V době vydání nebyl veřejně známý výsledek pátrání.</p></section>
<div data-promos data-context="article-end"></div></article>
<aside class="sticky"><div class="sidebox"><h3>Jezero Most</h3><ul><li>rekreační vodní plocha u Mostu</li><li>koupání a vodní sporty</li><li>cíl návštěvníků z celého regionu</li></ul></div><div class="sidebox"><h3>Praktická zásada</h3><p>Při příchodu bouřky opusťte vodu co nejdříve. Na návrat nečekejte až do chvíle, kdy vítr a vlny znemožní bezpečný pohyb.</p></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/" aria-label="Naše Kadaň – úvodní stránka"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a><a href="/provozovatel/">Provozovatel</a><a href="/cookies/#nastaveni" data-open-privacy-settings>Nastavení soukromí</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/long-article-ads.js?v=20260731-long-article-ads-2"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script>
</body></html>'''


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{RSS_DATE}</lastBuildDate>", text, count=1)
    if URL in text:
        path.write_text(text, encoding="utf-8", newline="\n")
        return
    item = f'''    <item>
      <title>{escape(TITLE)}</title>
      <description><![CDATA[{DESC}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{RSS_DATE}</pubDate>
      <category>Od sousedů</category><category>Most</category><category>Bezpečnost</category><category>Aktuálně</category>
      <szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image>
    </item>

'''
    marker = "    <item>"
    if marker not in text:
        raise RuntimeError("RSS neobsahuje první položku.")
    path.write_text(text.replace(marker, item + marker, 1), encoding="utf-8", newline="\n")


def update_news_sitemap() -> None:
    path = ROOT / "news-sitemap.xml"
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.register_namespace("image", "http://www.google.com/schemas/sitemap-image/1.1")
    ET.register_namespace("news", "http://www.google.com/schemas/sitemap-news/0.9")
    tree = ET.parse(path)
    root = tree.getroot()
    sm = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ns_news = "http://www.google.com/schemas/sitemap-news/0.9"
    ns_image = "http://www.google.com/schemas/sitemap-image/1.1"
    for old in list(root):
        loc = old.find(f"{{{sm}}}loc")
        if loc is not None and loc.text == URL:
            root.remove(old)
    node = ET.Element(f"{{{sm}}}url")
    ET.SubElement(node, f"{{{sm}}}loc").text = URL
    news = ET.SubElement(node, f"{{{ns_news}}}news")
    publication = ET.SubElement(news, f"{{{ns_news}}}publication")
    ET.SubElement(publication, f"{{{ns_news}}}name").text = "Naše Kadaň"
    ET.SubElement(publication, f"{{{ns_news}}}language").text = "cs"
    ET.SubElement(news, f"{{{ns_news}}}publication_date").text = PUBLISHED
    ET.SubElement(news, f"{{{ns_news}}}title").text = TITLE
    image = ET.SubElement(node, f"{{{ns_image}}}image")
    ET.SubElement(image, f"{{{ns_image}}}loc").text = SOCIAL_URL
    ET.SubElement(image, f"{{{ns_image}}}title").text = TITLE
    root.insert(0, node)
    while len(root) > 10:
        root.remove(root[-1])
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    if URL in text:
        return
    marker = "## Nejnovější vlastní články\n\n"
    if marker not in text:
        raise RuntimeError("llms.txt neobsahuje sekci nejnovějších článků.")
    entry = f"- [{TITLE}]({URL})\n  {DESC}\n"
    path.write_text(text.replace(marker, marker + entry, 1), encoding="utf-8", newline="\n")


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = [x for x in data.get("articles", []) if isinstance(x, dict) and x.get("url") != URL]
    articles.append({
        "title": TITLE,
        "h1": TITLE,
        "url": URL,
        "published_at": PUBLISHED,
        "modified_at": MODIFIED,
        "persons": [],
        "organizations": ["Policie České republiky", "CNN Prima NEWS", "Mostecký deník"],
        "places": ["Jezero Most", "Most", "Kadaň", "Chomutovsko"],
        "cases": ["Pátrání po dvou lidech na jezeře Most po silné bouřce"],
        "topics": ["Jezero Most", "Pátrání", "Bouřka", "Bezpečnost u vody", "Od sousedů"],
        "fingerprint": FINGERPRINT,
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "source_path": f"clanky/{SLUG}.html",
        "publication_status": "published",
        "source_commit": "pending-publication-commit",
    })
    articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    data["articles"] = articles
    data["article_count"] = len(articles)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["homepage_count"] = min(14, len(articles))
    validation["archive_count"] = len(articles)
    validation["archive_page_count"] = ceil(len(articles) / 12)
    validation["rss_count"] = len(articles)
    validation["sitemap_all_articles_present"] = True
    validation["news_sitemap_recent_count"] = min(10, len(articles))
    urls = [x.get("url") for x in articles]
    fps = [x.get("fingerprint") for x in articles]
    validation["duplicate_urls"] = sorted({x for x in urls if x and urls.count(x) > 1})
    validation["duplicate_fingerprints"] = sorted({x for x in fps if x and fps.count(x) > 1})
    validation["repair_pending_public_verification"] = True
    validation["last_consistency_audit"] = {"status": "pending_public_verification", "checked_at": datetime.now(timezone.utc).isoformat(), "article_count": len(articles), "updated_url": URL, "source_commit": "pending-publication-commit"}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    write(ARTICLE, article_page())
    make_social()
    subprocess.run(["python3", str(ROOT / "scripts" / "enforce_all_article_visibility.py")], check=True)
    update_rss()
    update_news_sitemap()
    update_llms()
    update_registry()
    print(f"Hotovo: {URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
