#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import textwrap
from html import unescape
from xml.sax.saxutils import escape as xml_escape

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / ".github/drafts/alzbetinsky-klaster-kadan-20260803.html"
ARTICLE = ROOT / "clanky/alzbetinsky-klaster-kadan-pacienti-lecebna-1966.html"
SOCIAL = ROOT / "social/alzbetinsky-klaster-kadan-pacienti-20260803.png"

URL = "https://nasekadan.cz/clanky/alzbetinsky-klaster-kadan-pacienti-lecebna-1966.html"
REL = "/clanky/alzbetinsky-klaster-kadan-pacienti-lecebna-1966.html"
TITLE = "Kam odešli poslední pacienti? Skrytý příběh kadaňského kláštera"
DESC = "Staré prameny odhalují nemocnici, lékárnu, sirotčinec i plicní léčebnu v kadaňském klášteře. Proč skončila a kam odešli poslední pacienti?"
IMAGE_URL = "https://nasekadan.cz/social/alzbetinsky-klaster-kadan-pacienti-20260803.png"
PUBLISHED = "2026-08-03T04:00:00+02:00"
RSS_DATE = "Mon, 03 Aug 2026 04:00:00 +0200"
DATE_ISO = "2026-08-03"
ARTICLE_KEY = "alzbetinsky-klaster-kadan-pacienti-20260803"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def first_group(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.S | re.I)
    return strip_tags(match.group(1)) if match else default


def first_attr(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.S | re.I)
    return unescape(match.group(1)).strip() if match else default


def build_article() -> str:
    if not DRAFT.is_file():
        raise SystemExit(f"Chybí návrh článku: {DRAFT}")
    text = DRAFT.read_text(encoding="utf-8")
    required = [
        TITLE,
        'data-poll-id="alzbetinsky-klaster-kadan-2026"',
        'data-promos data-context="sidebar"',
        "Léčebna tbc a respiračních nemocí v Kadani",
        "142 léčených osob",
        "672 předmětů",
        URL,
        IMAGE_URL,
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"Návrh článku postrádá povinné části: {missing}")
    if "Náhled není k dispozici" in text or "pracovní náhled" in text.lower():
        raise SystemExit("Návrh obsahuje pracovní text.")
    return text


def social_image() -> None:
    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1200, 630
    img = Image.new("RGB", (width, height), (28, 19, 23))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        t = y / max(1, height - 1)
        r = int(33 * (1 - t) + 95 * t)
        g = int(24 * (1 - t) + 23 * t)
        b = int(28 * (1 - t) + 35 * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    gold = (198, 162, 92)
    wine = (140, 31, 52)
    cream = (245, 236, 219)
    draw.rectangle([0, 0, 18, height], fill=wine)
    draw.rectangle([0, height - 18, width, height], fill=gold)
    draw.ellipse([820, 15, 1260, 455], outline=gold, width=12)
    draw.rectangle([875, 235, 1200, 630], outline=gold, width=12)
    draw.ellipse([900, 112, 1175, 387], outline=cream, width=7)
    draw.rectangle([938, 248, 1137, 630], outline=cream, width=7)
    draw.line([(1038, 248), (1038, 630)], fill=cream, width=5)
    draw.line([(938, 390), (1137, 390)], fill=cream, width=5)

    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    f_brand = ImageFont.truetype(bold, 38)
    f_badge = ImageFont.truetype(bold, 23)
    f_title = ImageFont.truetype(bold, 55)
    f_sub = ImageFont.truetype(regular, 27)
    f_small = ImageFont.truetype(bold, 21)

    draw.text((58, 42), "NAŠE KADAŇ", font=f_brand, fill="white")
    draw.rounded_rectangle([58, 105, 340, 151], radius=20, fill=wine)
    draw.text((78, 114), "VELKÁ HISTORICKÁ REŠERŠE", font=f_badge, fill="white")

    y = 188
    for line in textwrap.wrap("Kam odešli poslední pacienti?", width=25):
        draw.text((58, y), line, font=f_title, fill="white")
        y += 66
    y += 2
    for line in textwrap.wrap("Skrytý příběh kadaňského kláštera", width=39):
        draw.text((60, y), line, font=f_sub, fill=cream)
        y += 38

    draw.rounded_rectangle([58, 520, 760, 582], radius=20, fill=cream)
    draw.text((82, 536), "142 pacientů • léčebna do roku 1966 • 672 předmětů", font=f_small, fill=(56, 30, 34))
    img.save(SOCIAL, format="PNG", optimize=True)


def update_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")

    section_match = re.search(
        r'(<section\b[^>]*class="wrap hero"[^>]*>)(.*?)(</section>)',
        text,
        re.S | re.I,
    )
    if not section_match:
        raise SystemExit("Na titulní straně chybí sekce hero.")

    section_open, section_body, section_close = section_match.groups()
    current_lead_match = re.search(r'<article class="lead">(.*?)</article>', section_body, re.S | re.I)
    current_aside_match = re.search(r'<aside class="current-aside">.*?</aside>', section_body, re.S | re.I)
    if not current_lead_match or not current_aside_match:
        raise SystemExit("Titulní strana nemá očekávaný hlavní článek a boční kartu.")

    current_lead_full = current_lead_match.group(0)
    current_href = first_attr(r'<a\b[^>]*href="([^"]+)"[^>]*>', current_lead_full)
    current_title = first_group(r'<h1>(.*?)</h1>', current_lead_full, "Další aktuální článek")
    current_desc = first_group(r'<div class="copy">.*?<p>(.*?)</p>', current_lead_full, "")
    current_date = first_group(r'<div class="copy">.*?<small>(.*?)</small>', current_lead_full, "")

    hero = f'''<article class="lead">
      <div class="photo" style="background:radial-gradient(circle at 82% 17%,rgba(255,255,255,.16),transparent 26%),linear-gradient(135deg,#23171b,#64202d 58%,#b78a3f)"><span>NEJNOVĚJŠÍ ČLÁNEK</span><strong>3. 8. 2026</strong></div>
      <div class="copy">
        <small>HISTORIE · VELKÁ REŠERŠE · 3. SRPNA 2026 · 04:00</small>
        <h1>{TITLE}</h1>
        <p>{DESC}</p>
        <a class="btn" href="{REL}">Přečíst článek →</a>
      </div>
    </article>'''

    if current_href and current_href != REL:
        aside = f'''<aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">{current_date}</p>
      <h2>{current_title}</h2>
      <p>{current_desc}</p>
      <a class="aside-button" href="{current_href}">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div>
    </aside>'''
    else:
        aside = current_aside_match.group(0)

    new_body = re.sub(r'<article class="lead">.*?</article>', hero, section_body, count=1, flags=re.S | re.I)
    new_body = re.sub(r'<aside class="current-aside">.*?</aside>', aside, new_body, count=1, flags=re.S | re.I)

    if "data-latest-article-href=" in section_open:
        section_open = re.sub(
            r'data-latest-article-href="[^"]*"',
            f'data-latest-article-href="{REL}"',
            section_open,
            count=1,
        )
    else:
        section_open = section_open[:-1] + f' data-latest-article-href="{REL}">'

    replacement = section_open + new_body + section_close
    text = text[:section_match.start()] + replacement + text[section_match.end():]

    text = re.sub(
        rf'\s*<article\b[^>]*data-auto-article="{re.escape(ARTICLE_KEY)}"[^>]*>.*?</article>\s*',
        "\n",
        text,
        flags=re.S | re.I,
    )
    card = f'''
      <article class="article-card service" data-auto-article="{ARTICLE_KEY}">
        <div class="visual" style="background:linear-gradient(135deg,#2b1820,#742239 58%,#b28b47)"><strong>{TITLE}</strong></div>
        <div class="article-body">
          <span class="meta">3. 8. 2026 · 04:00 · Historie · Velká rešerše</span>
          <h3>{TITLE}</h3>
          <p>142 pacientů, plicní léčebna do roku 1966 a otázka, kam odešli poslední nemocní.</p>
          <a class="read-more" href="{REL}">Přečíst článek →</a>
        </div>
      </article>
'''
    marker = '<div class="article-list">'
    if marker not in text:
        raise SystemExit("Titulní strana nemá seznam článků.")
    text = text.replace(marker, marker + card, 1)
    write(path, text)



def update_archive() -> None:
    path = ROOT / "clanky/index.html"
    text = path.read_text(encoding="utf-8")

    match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)
    if not match:
        raise SystemExit("Archiv nemá JSON-LD seznam.")
    data = json.loads(match.group(1))
    graph = data.get("@graph", [])
    itemlist = next((item for item in graph if item.get("@type") == "ItemList"), None)
    if not itemlist:
        raise SystemExit("Archiv nemá ItemList.")
    existing = [item for item in itemlist.get("itemListElement", []) if item.get("url") != URL]
    items = [{"@type": "ListItem", "position": 1, "url": URL, "name": TITLE}]
    for pos, item in enumerate(existing, 2):
        item["position"] = pos
        items.append(item)
    itemlist["itemListElement"] = items
    itemlist["numberOfItems"] = len(items)
    replacement = '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n  </script>"
    text = text[:match.start()] + replacement + text[match.end():]

    text = re.sub(
        rf'\s*<article\b[^>]*data-auto-article="{re.escape(ARTICLE_KEY)}"[^>]*>.*?</article>\s*',
        "\n",
        text,
        flags=re.S | re.I,
    )
    item = f'''
    <article class="article-card service" data-auto-article="{ARTICLE_KEY}">
      <div class="visual" style="background:linear-gradient(135deg,#2b1820,#742239 58%,#b28b47)"><strong>{TITLE}</strong></div>
      <div class="article-body"><span class="meta">3. 8. 2026 · 04:00 · Historie · Velká rešerše</span><h3>{TITLE}</h3><p>142 pacientů, léčebna do roku 1966 a nezodpovězená otázka posledního přesunu.</p><a class="read-more" href="{REL}">Přečíst článek →</a></div>
    </article>
'''
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if marker not in text:
        raise SystemExit("Archiv nemá očekávaný seznam článků.")
    text = text.replace(marker, marker + item, 1)
    write(path, text)


def update_feeds() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{RSS_DATE}</lastBuildDate>", text, count=1)
    if URL not in text:
        item = (
            "    <item>"
            f"<title>{xml_escape(TITLE)}</title>"
            f"<description><![CDATA[{DESC}]]></description>"
            f"<link>{URL}</link>"
            f"<guid isPermaLink=\"true\">{URL}</guid>"
            f"<pubDate>{RSS_DATE}</pubDate>"
            "<category>Historie</category><category>Kadaň</category>"
            f"<szn:image><szn:url>{IMAGE_URL}</szn:url></szn:image>"
            "<geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>"
            "</item>\n\n"
        )
        text = text.replace("    <item>", item + "    <item>", 1)
    write(path, text)

    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+", rf"\g<1>{DATE_ISO}", text, count=1)
    text = re.sub(r"(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+", rf"\g<1>{DATE_ISO}", text, count=1)
    if URL not in text:
        text = text.replace("</urlset>", f"  <url><loc>{URL}</loc><lastmod>{DATE_ISO}</lastmod></url>\n</urlset>")
    write(path, text)

    path = ROOT / "news-sitemap.xml"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if URL not in text:
            entry = (
                f"  <url><loc>{URL}</loc><news:news><news:publication>"
                "<news:name>Naše Kadaň</news:name><news:language>cs</news:language>"
                f"</news:publication><news:publication_date>{PUBLISHED}</news:publication_date>"
                f"<news:title>{xml_escape(TITLE)}</news:title></news:news></url>\n"
            )
            text = text.replace("</urlset>", entry + "</urlset>")
        write(path, text)


def validate() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    required = [
        TITLE,
        'data-poll-id="alzbetinsky-klaster-kadan-2026"',
        'data-promos data-context="sidebar"',
        "Léčebna tbc a respiračních nemocí v Kadani",
        "142 léčených osob",
        "672 předmětů",
        "/site.js",
        "/reklamy.js",
    ]
    missing = [item for item in required if item not in article]
    if missing:
        raise SystemExit(f"Článek postrádá: {missing}")

    checks = {
        "index.html": REL,
        "clanky/index.html": REL,
        "rss.xml": URL,
        "sitemap.xml": URL,
        "news-sitemap.xml": URL,
    }
    for rel, marker in checks.items():
        path = ROOT / rel
        if not path.is_file() or marker not in path.read_text(encoding="utf-8"):
            raise SystemExit(f"{rel} neobsahuje článek.")

    if not SOCIAL.is_file() or SOCIAL.stat().st_size < 10000:
        raise SystemExit("Sociální obrázek nebyl vytvořen nebo je příliš malý.")
    with Image.open(SOCIAL) as image:
        if image.size != (1200, 630):
            raise SystemExit(f"Sociální obrázek má nesprávné rozměry: {image.size}")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if f'data-latest-article-href="{REL}"' not in home:
        raise SystemExit("Článek není nastaven jako nejnovější na titulní straně.")
    if home.count(f'data-auto-article="{ARTICLE_KEY}"') != 1:
        raise SystemExit("Karta článku na titulní straně není právě jednou.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-source-only", action="store_true")
    args = parser.parse_args()

    if args.validate_source_only:
        text = build_article()
        if len(text) < 15000:
            raise SystemExit("Návrh článku je podezřele krátký.")
        compile(Path(__file__).read_text(encoding="utf-8"), str(__file__), "exec")
        print("Zdroj článku a publikační skript jsou připravené.")
        return

    write(ARTICLE, build_article())
    social_image()
    update_home()
    update_archive()
    update_feeds()
    validate()
    print("Článek o alžbětinském klášteře je připraven k veřejnému nasazení.")


if __name__ == "__main__":
    main()
