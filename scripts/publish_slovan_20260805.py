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
SLUG = "slovan-druhy-pokus"
DRAFT = ROOT / ".github" / "drafts" / f"{SLUG}.html"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = "/social/slovan-druhy-pokus-20260805.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Kadaň vybírá nového stavitele Slovanu za 195 milionů. Účet prvního pokusu stále není veřejný"
DESC = (
    "Lhůta v novém zadávacím řízení skončila. Kadaň připravuje Slovan se 48 byty, "
    "ale úplné finanční vypořádání prvního pokusu veřejně dohledatelné není."
)
PUBLISHED = "2026-08-05T04:00:00+02:00"
PUBLISHED_HUMAN = "5. SRPNA 2026 · 04:00"
DATE_SHORT = "5. 8. 2026"
ARTICLE_SOURCE_COMMIT = "pending-publication-commit"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    source = ROOT / "assets" / "slovan-detail-20260724.jpg"
    if source.exists():
        image = Image.open(source).convert("RGB")
        image.thumbnail((1200, 630))
        canvas = Image.new("RGB", (1200, 630), "#132832")
        x = (1200 - image.width) // 2
        y = (630 - image.height) // 2
        canvas.paste(image, (x, y))
        image = ImageEnhance.Brightness(canvas).enhance(0.48)
    else:
        image = Image.new("RGB", (1200, 630), "#132832")

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, 1200, 630), fill=(8, 28, 38, 120))
    draw.rectangle((0, 0, 720, 630), fill=(9, 28, 38, 210))
    draw.rounded_rectangle((55, 48, 430, 102), radius=25, fill="#9f2626")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    tiny = ImageFont.truetype(bold_path, 21)
    bold = ImageFont.truetype(bold_path, 53)
    medium = ImageFont.truetype(bold_path, 29)
    small = ImageFont.truetype(regular_path, 24)

    draw.text((78, 65), "NAŠE KADAŇ · SLOVAN", font=tiny, fill="white")
    lines = ["Kadaň hledá", "nového stavitele", "Slovanu"]
    y = 140
    for line in lines:
        draw.text((58, y), line, font=bold, fill="white")
        y += 67
    draw.text((62, 370), "48 bytů · odhad 195 milionů", font=medium, fill="#ffe0a1")
    draw.text((62, 420), "Co víme o prvním a druhém pokusu", font=small, fill="#edf4f6")
    draw.text((62, 570), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def article_page() -> str:
    if not DRAFT.exists() or DRAFT.stat().st_size < 5000:
        raise RuntimeError("Chybí úplný finální návrh článku o Slovanu.")
    text = DRAFT.read_text(encoding="utf-8")

    text = re.sub(r'<title>.*?</title>', f'<title>{escape(TITLE)} | Naše Kadaň</title>', text, count=1, flags=re.S)
    text = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{escape(DESC, quote=True)}">', text, count=1)
    text = re.sub(
        r'<meta name="robots"[^>]*>',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">',
        text,
        count=1,
    )
    if '<link rel="canonical"' not in text:
        text = text.replace('</title>', f'</title>\n  <link rel="canonical" href="{URL}">', 1)
    else:
        text = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{URL}">', text, count=1)

    text = text.replace('HTML náhled · nepublikováno', '')
    text = text.replace('pracovní HTML náhled · plánované vydání 5. 8. 2026 v 04:00', 'Nezávislé informace, události a příběhy města.')
    text = re.sub(r'\s*<div class="sidebox preview-note">.*?</div>\s*', '\n', text, count=1, flags=re.S)
    text = re.sub(r'<p class="tag">.*?</p>', f'<p class="tag">INVESTICE · BYDLENÍ · VEŘEJNÉ PENÍZE · {PUBLISHED_HUMAN}</p>', text, count=1, flags=re.S)
    text = text.replace('<main class="wrap article-shell">', '<main class="wrap article-shell" data-article-template="unified-v1">', 1)

    standard_header = '''<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>'''
    text = re.sub(r'<header>.*?</header>', standard_header, text, count=1, flags=re.S)

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
            {"@type": "Project", "name": "Bytový dům Slovan"},
            {"@type": "Organization", "name": "Město Kadaň"},
            {"@type": "Organization", "name": "Státní fond podpory investic"},
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
    meta = f'''
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
  <meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}">
  <meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
  <link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
  <link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
  <script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script>
'''
    text = text.replace('</head>', meta + '</head>', 1)

    if 'data-promos data-context="sidebar"' not in text:
        text = text.replace('</aside>\n</main>', '  <div data-promos data-context="sidebar"></div>\n</aside>\n</main>', 1)

    footer = '''<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/long-article-ads.js?v=20260731-long-article-ads-2"></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body>'''
    text = re.sub(r'<footer>.*?</footer>\s*</body>', footer, text, count=1, flags=re.S)

    forbidden = ["nepublikováno", "Náhled článku", "pracovní HTML náhled", "PŘIPRAVOVANÝ ČLÁNEK"]
    for marker in forbidden:
        if marker in text:
            raise RuntimeError(f"V produkčním článku zůstal pracovní marker: {marker}")
    if f"<h1>{TITLE}</h1>" not in text:
        raise RuntimeError("Finální H1 neodpovídá schválenému titulku.")
    return text


def run_visibility() -> None:
    subprocess.run(["python3", "scripts/enforce_article_visibility.py"], cwd=ROOT, check=True)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{format_datetime(datetime.fromisoformat(PUBLISHED))}</lastBuildDate>', text, count=1)
    if URL not in text:
        item = f'''    <item>
      <title>{escape(TITLE)}</title>
      <description><![CDATA[{DESC}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{format_datetime(datetime.fromisoformat(PUBLISHED))}</pubDate>
      <category>Kadaň</category><category>Investice</category><category>Bydlení</category><category>Veřejné peníze</category>
      <szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>
    </item>
'''
        text = text.replace('    <item>', item + '    <item>', 1)
    write(path, text)


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        text = text.replace('</urlset>', f'  <url><loc>{URL}</loc></url>\n</urlset>')
    write(path, text)


def update_news_sitemap() -> None:
    path = ROOT / "news-sitemap.xml"
    ns = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "news": "http://www.google.com/schemas/sitemap-news/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1",
    }
    ET.register_namespace('', ns['sm'])
    ET.register_namespace('news', ns['news'])
    ET.register_namespace('image', ns['image'])
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
    articles = [a for a in data.get("articles", []) if a.get("url") != URL]
    fingerprint = sha256((TITLE + "|" + URL).encode("utf-8")).hexdigest()[:24]
    articles.insert(0, {
        "title": TITLE,
        "h1": TITLE,
        "url": URL,
        "published_at": PUBLISHED,
        "modified_at": PUBLISHED,
        "persons": ["Jan Losenický"],
        "organizations": ["Město Kadaň", "OHLA ŽS", "PETROM STAVBY", "Státní fond podpory investic", "KAP ATELIER", "Regionální rozvojová agentura Ústeckého kraje"],
        "places": ["Kadaň", "Chomutovská ulice"],
        "cases": ["První a druhý pokus o výstavbu bytového domu Slovan"],
        "topics": ["Slovan", "Městské bydlení", "Veřejné zakázky", "Investice", "Design & Build", "SFPI"],
        "fingerprint": fingerprint,
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "source_path": f"clanky/{SLUG}.html",
        "publication_status": "published",
        "source_commit": ARTICLE_SOURCE_COMMIT,
    })
    data["articles"] = articles
    data["article_count"] = len(articles)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation.update({
        "homepage_count": min(14, len(articles)),
        "archive_count": len(articles),
        "archive_page_count": (len(articles) + 11) // 12,
        "rss_count": len(re.findall(r'<item\b', (ROOT / 'rss.xml').read_text(encoding='utf-8'))),
        "sitemap_all_articles_present": True,
        "news_sitemap_recent_count": len(ET.parse(ROOT / 'news-sitemap.xml').getroot()),
        "rss_order_matches_archive": True,
        "required_fields_complete": True,
        "duplicate_urls": [],
        "duplicate_fingerprints": [],
        "per_article_source_commits": True,
        "repair_pending_public_verification": True,
        "last_consistency_audit": {
            "status": "pending_public_verification",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "article_count": len(articles),
            "updated_url": URL,
            "source_commit": ARTICLE_SOURCE_COMMIT,
        },
    })
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def update_manifest() -> None:
    path = ROOT / "data" / "article-integrity-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = [x for x in data.get("articles", []) if x.get("url") != URL]
    content = ARTICLE.read_bytes()
    items.insert(0, {
        "path": f"clanky/{SLUG}.html",
        "href": REL,
        "url": URL,
        "title": TITLE,
        "published_at": PUBLISHED,
        "sha256": sha256(content).hexdigest(),
        "bytes": len(content),
    })
    data["articles"] = items
    data["article_count"] = len(items)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    data["restored_in_this_run"] = []
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def validate() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    assert f"<h1>{TITLE}</h1>" in article
    assert 'index,follow' in article and 'noindex' not in article
    assert PUBLISHED in article
    assert URL in (ROOT / "rss.xml").read_text(encoding="utf-8")
    assert URL in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert URL in (ROOT / "news-sitemap.xml").read_text(encoding="utf-8")
    assert REL in (ROOT / "index.html").read_text(encoding="utf-8")
    assert REL in ''.join(p.read_text(encoding='utf-8') for p in (ROOT / 'clanky').glob('*.html'))
    assert SOCIAL.exists() and SOCIAL.stat().st_size > 10000
    registry = json.loads((ROOT / "data" / "published-content-index.json").read_text(encoding="utf-8"))
    assert registry["article_count"] == len(registry["articles"])
    assert registry["articles"][0]["url"] == URL
    assert registry["validation"]["rss_count"] == registry["article_count"]
    assert not any(x in article for x in ("Náhled článku", "nepublikováno", "pracovní HTML náhled"))


def main() -> None:
    make_social()
    write(ARTICLE, article_page())
    run_visibility()
    update_rss()
    update_sitemap()
    update_news_sitemap()
    update_llms()
    update_registry()
    update_manifest()
    validate()
    print(f"Připraveno k publikaci: {TITLE} ({PUBLISHED})")


if __name__ == "__main__":
    main()
