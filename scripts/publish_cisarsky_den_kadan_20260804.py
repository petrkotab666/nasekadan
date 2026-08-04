#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape, unescape
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = "cisarsky-den-kadan-historie-2026"
DRAFT = ROOT / ".github" / "drafts" / f"{SLUG}.html"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Císařský den v Kadani: od návštěvy Karla IV. k největší městské slavnosti"
DESC = (
    "Jak vznikl Císařský den, co se skutečně stalo při návštěvách Karla IV. "
    "a proč oficiální 34. ročník nebude čtyřiatřicátou uskutečněnou slavností."
)
PUBLISHED = "2026-08-04T05:50:00+02:00"
PUBLISHED_HUMAN = "4. SRPNA 2026 · 05:50"
DATE_SHORT = "4. 8. 2026"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def clean_html(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", value)).replace("\n", " ").strip()


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#102733")
    draw = ImageDraw.Draw(image)
    for y in range(630):
        ratio = y / 629
        r = int(16 + (112 - 16) * ratio)
        g = int(39 + (42 - 39) * ratio)
        b = int(51 + (42 - 51) * ratio)
        draw.line((0, y, 1200, y), fill=(r, g, b))

    # Záře, hradby a věže připomínající historickou Kadaň.
    draw.ellipse((765, 30, 1270, 535), fill="#d79e4525")
    draw.rectangle((690, 335, 1200, 630), fill="#111f27")
    draw.rectangle((735, 235, 830, 540), fill="#172a34")
    draw.polygon([(720, 235), (782, 150), (845, 235)], fill="#172a34")
    draw.rectangle((910, 270, 1010, 550), fill="#172a34")
    draw.polygon([(895, 270), (960, 175), (1025, 270)], fill="#172a34")
    draw.rectangle((1060, 315, 1160, 565), fill="#172a34")
    draw.polygon([(1045, 315), (1110, 225), (1175, 315)], fill="#172a34")
    for x in (750, 785, 925, 965, 1075, 1115):
        draw.rounded_rectangle((x, 350, x + 18, 395), radius=8, fill="#e6b85b")
    draw.arc((700, 450, 1180, 720), 180, 360, fill="#aa2630", width=16)

    # Císařská koruna jako výrazný motiv.
    crown = [(760, 125), (805, 70), (850, 130), (900, 55), (950, 130), (1000, 72), (1042, 125), (1020, 195), (785, 195)]
    draw.polygon(crown, fill="#d8a94d", outline="#fff2bf")
    draw.rectangle((790, 178, 1018, 218), fill="#b32632", outline="#fff2bf", width=4)
    for x in (820, 900, 980):
        draw.ellipse((x, 184, x + 18, 202), fill="#fff2bf")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 58)
    medium = ImageFont.truetype(bold_path, 31)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 21)

    draw.rounded_rectangle((58, 52, 390, 104), radius=25, fill="#a9232b")
    draw.text((82, 68), "NAŠE KADAŇ · HISTORIE", font=tiny, fill="white")
    lines = ["Císařský den", "od Karla IV.", "k dnešní slavnosti"]
    y = 145
    for line in lines:
        draw.text((62, y), line, font=bold, fill="white")
        y += 74
    draw.text((66, 390), "34. ročník, ale kolik slavností", font=medium, fill="#ffe0a1")
    draw.text((66, 432), "se ve skutečnosti uskutečnilo?", font=medium, fill="#ffe0a1")
    draw.text((66, 493), "22. srpna 2026 · Kadaň", font=small, fill="#edf4f6")
    draw.text((66, 570), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def article_page() -> str:
    if not DRAFT.exists():
        raise RuntimeError(f"Chybí návrh článku: {DRAFT}")
    text = DRAFT.read_text(encoding="utf-8")

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
            {"@type": "Person", "name": "Karel IV."},
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Event", "name": "Císařský den 2026", "startDate": "2026-08-22", "location": {"@type": "Place", "name": "Historické centrum Kadaně"}},
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

    text = re.sub(
        r'<meta name="robots" content="[^"]*">',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">',
        text,
        count=1,
    )
    text = text.replace('PŘIPRAVOVANÝ ČLÁNEK', PUBLISHED_HUMAN)
    text = text.replace('<span class="logo-mark"></span>', '<span class="logo-mark">NK</span>')
    text = text.replace('<main class="wrap article-shell">', '<main class="wrap article-shell" data-article-template="unified-v1">')

    hero = (
        f'<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" '
        'alt="Redakční grafika Císařského dne s korunou a siluetou historické Kadaně">\n'
    )
    text, count = re.subn(r'\s*<div class="hero">.*?</div>\s*', '\n  ' + hero + '\n', text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("V návrhu nebyl nalezen úvodní obrazový blok.")

    text = text.replace(
        '</style>',
        '.hero-image{display:block;width:100%;height:auto;margin:30px 0;border-radius:24px;box-shadow:var(--shadow)}\n'
        '@media(max-width:700px){.hero-image{border-radius:16px}}\n</style>',
        1,
    )
    text = re.sub(r'\s*<div class="sidebox editor">.*?</div>\s*', '\n', text, count=1, flags=re.S)
    text = text.replace(
        '<small>Před vydáním aktualizovat kompletní program, dopravní omezení, případné historické vlaky, vstupné a praktické informace pro návštěvníky.</small>',
        '<small>Pořadatel zatím zveřejnil hlavní body programu. Podrobný rozpis, dopravu a případná omezení doplníme po jejich oficiálním zveřejnění.</small>',
    )
    if 'data-promos data-context="sidebar"' not in text:
        text = text.replace('</aside>\n</main>', '  <div data-promos data-context="sidebar"></div>\n</aside>\n</main>', 1)

    meta = f'''\n<link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE)}"><meta property="og:description" content="{escape(DESC)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE)}"><meta name="twitter:description" content="{escape(DESC)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626"><link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script>\n'''
    text = text.replace('</head>', meta + '</head>', 1)

    footer = '''<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/long-article-ads.js?v=20260731-long-article-ads-2"></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body>'''
    text = re.sub(r'<footer>.*?</footer>\s*</body>', footer, text, count=1, flags=re.S)
    return text


def update_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<section class="wrap hero"[^>]*>.*?</section>', text, flags=re.S)
    if not match:
        raise RuntimeError("Na titulce nebyla nalezena hlavní sekce hero.")
    old = match.group(0)
    href_match = re.search(r'data-latest-article-href="([^"]+)"', old)
    h1_match = re.search(r'<h1>(.*?)</h1>', old, flags=re.S)
    desc_match = re.search(r'<div class="copy">.*?<p>(.*?)</p>', old, flags=re.S)
    old_href = href_match.group(1) if href_match else "/clanky/"
    old_title = clean_html(h1_match.group(1)) if h1_match else "Další aktuální články"
    old_desc = clean_html(desc_match.group(1)) if desc_match else "Přečtěte si další zprávy a ověřené informace z Kadaně a okolí."
    if old_href == REL:
        old_href = "/clanky/"
        old_title = "Další aktuální články"
    hero = f'''<section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{REL}">
    <article class="lead"><div class="photo" style="background-image:linear-gradient(180deg,transparent,#08263dbb),url('{SOCIAL_REL}');background-size:cover;background-position:center"><span>HISTORIE · KULTURA · KADAŇ · {PUBLISHED_HUMAN}</span><strong>{DATE_SHORT}</strong></div><div class="copy"><small>HISTORIE · KULTURA · KADAŇ · {PUBLISHED_HUMAN}</small><h1>{escape(TITLE)}</h1><p>{escape(DESC)}</p><a class="btn" href="{REL}">Přečíst nejnovější článek →</a></div></article>
    <aside class="current-aside"><p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p><h2>{escape(old_title)}</h2><p>{escape(old_desc)}</p><a class="aside-button" href="{escape(old_href)}">Přečíst článek →</a><div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div></aside>
  </section>'''
    text = text[:match.start()] + hero + text[match.end():]
    write(path, text)


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    if f'data-auto-article="{SLUG}"' not in text:
        card = f'''\n    <article class="article-card culture" data-auto-article="{SLUG}"><div class="visual" style="background-image:linear-gradient(180deg,transparent,#08263dcc),url('{SOCIAL_REL}');background-size:cover;background-position:center"><strong>{escape(TITLE)}</strong></div><div class="article-body"><span class="meta">{DATE_SHORT} · 05:50 · HISTORIE · KULTURA · KADAŇ</span><h3>{escape(TITLE)}</h3><p>{escape(DESC)}</p><a class="read-more" href="{REL}">Přečíst článek →</a></div></article>\n'''
        text = text.replace('<div class="archive-list">', '<div class="archive-list">' + card, 1)

    pattern = re.compile(r'(<script type="application/ld\+json">\s*)(\{.*?\})(\s*</script>)', re.S)
    for match in list(pattern.finditer(text)):
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph") if isinstance(data, dict) else None
        if not isinstance(graph, list):
            continue
        itemlist = next((node for node in graph if isinstance(node, dict) and node.get("@type") == "ItemList"), None)
        if not itemlist:
            continue
        items = itemlist.setdefault("itemListElement", [])
        if not any(isinstance(item, dict) and item.get("url") == URL for item in items):
            items.insert(0, {"@type": "ListItem", "position": 1, "url": URL, "name": TITLE})
        for pos, item in enumerate(items, 1):
            if isinstance(item, dict):
                item["position"] = pos
        itemlist["numberOfItems"] = len(items)
        replacement = match.group(1) + json.dumps(data, ensure_ascii=False, indent=2) + match.group(3)
        text = text[:match.start()] + replacement + text[match.end():]
        break
    write(path, text)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    rss_date = format_datetime(datetime.fromisoformat(PUBLISHED))
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{rss_date}</lastBuildDate>', text, count=1)
    if URL not in text:
        item = f'''<item><title>{escape(TITLE)}</title><description><![CDATA[{DESC}]]></description><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{rss_date}</pubDate><category>Kadaň</category><category>Historie</category><category>Kultura</category><category>Císařský den</category><szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>\n    '''
        text = text.replace('<item>', item + '<item>', 1)
    write(path, text)


def update_sitemaps() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    if URL not in text:
        text = text.replace('</urlset>', f'  <url><loc>{URL}</loc></url>\n</urlset>', 1)
    write(sitemap, text)

    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    if URL not in text:
        node = f'''  <url>\n    <loc>{URL}</loc>\n    <news:news>\n      <news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication>\n      <news:publication_date>{PUBLISHED}</news:publication_date>\n      <news:title>{escape(TITLE)}</news:title>\n    </news:news>\n  </url>\n'''
        if '<url>' in text:
            text = text.replace('  <url>', node + '  <url>', 1)
        else:
            text = text.replace('</urlset>', node + '</urlset>', 1)
    write(news, text)


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
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    if not any(isinstance(item, dict) and item.get("url") == URL for item in articles):
        try:
            source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        except Exception:
            source_commit = ""
        articles.insert(0, {
            "title": TITLE,
            "h1": TITLE,
            "url": URL,
            "published_at": PUBLISHED,
            "modified_at": PUBLISHED,
            "persons": ["Karel IV.", "Kateřina Mertová", "Jan Gaža"],
            "organizations": ["Město Kadaň", "Kulturní zařízení Kadaň"],
            "places": ["Kadaň", "Mírové náměstí", "Františkánský klášter", "Smetanovy sady"],
            "cases": ["Historie, tradice a číslování Císařského dne"],
            "topics": ["Císařský den", "Karel IV.", "Historie Kadaně", "Kultura"],
            "fingerprint": sha256(URL.encode()).hexdigest()[:24],
            "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
            "source_path": f"clanky/{SLUG}.html",
            "publication_status": "published",
            "source_commit": source_commit,
        })
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation["homepage_count"] = sum(1 for item in articles if isinstance(item, dict) and item.get("status", {}).get("homepage"))
    validation["archive_count"] = sum(1 for item in articles if isinstance(item, dict) and item.get("status", {}).get("archive"))
    validation["rss_count"] = sum(1 for item in articles if isinstance(item, dict) and item.get("status", {}).get("rss"))
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    make_social()
    write(ARTICLE, article_page())
    update_home()
    update_archive()
    update_rss()
    update_sitemaps()
    update_llms()
    update_registry()
    weather_script = ROOT / "scripts" / "ensure_weather_loader.py"
    if weather_script.exists():
        subprocess.run(["python3", str(weather_script)], cwd=ROOT, check=True)

    required = [ARTICLE, SOCIAL, ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "llms.txt"]
    for path in required:
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Chybí výstup {path}.")
    article = ARTICLE.read_text(encoding="utf-8")
    if f'<h1>{TITLE}</h1>' not in article or 'index,follow' not in article:
        raise RuntimeError("Článek nemá správný nadpis nebo indexaci.")
    if 'PŘIPRAVOVANÝ ČLÁNEK' in article or 'Neveřejný rozpracovaný článek' in article:
        raise RuntimeError("Ve veřejném článku zůstalo označení návrhu.")
    for path in [ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml"]:
        content = path.read_text(encoding="utf-8", errors="replace")
        if REL not in content and URL not in content:
            raise RuntimeError(f"V souboru {path} chybí článek.")
    if '/pocasi.js' not in (ROOT / "index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Publikace by odstranila loader počasí.")
    print(f"Připraveno k publikaci: {URL}")


if __name__ == "__main__":
    main()
