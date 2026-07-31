#!/usr/bin/env python3
"""Připraví kompletní veřejnou publikaci článku o sečení trávníků.

Skript je idempotentní. Neveřejný zdroj je uložen komprimovaně v .github/drafts,
proto se před plánovaným časem nemůže dostat na produkční web. Při spuštění jej
sestaví, přepne na indexovatelnou verzi, spustí společné publikační nástroje a
výslovně zajistí RSS i obě sitemapy.
"""

from __future__ import annotations

import base64
import gzip
import html
import json
import re
import subprocess
import sys
from email.utils import format_datetime
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SLUG = "sekani-travniku-kadan-spravci-vysky-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
SOURCE1 = ROOT / ".github" / "drafts" / f"{SLUG}.html.gz.b64"
SOURCE2 = ROOT / ".github" / "drafts" / f"{SLUG}.html.gz.b64.part2"
PUBLIC_URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
PUBLISHED = "2026-08-01T11:00:00+02:00"
PUBLISHED_DT = datetime.fromisoformat(PUBLISHED)
EXPECTED = "Sedm centimetrů je smluvní minimum jedné konkrétní lokality"


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def read_source() -> str:
    encoded = SOURCE1.read_text(encoding="utf-8") + SOURCE2.read_text(encoding="utf-8")
    packed = base64.b64decode("".join(encoded.split()), validate=True)
    return gzip.decompress(packed).decode("utf-8")


def attr(text: str, key: str, value: str) -> str:
    patterns = (
        rf'<meta\b(?=[^>]*\b{key}=["\']{re.escape(value)}["\'])[^>]*\bcontent=["\']([^"\']+)',
        rf'<meta\b(?=[^>]*\bcontent=["\']([^"\']+)["\'])[^>]*\b{key}=["\']{re.escape(value)}["\'][^>]*>',
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return html.unescape(match.group(1)).strip()
    return ""


def first_tag(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(match.group(1)))).strip()


def publish_article() -> None:
    text = read_source()
    old = '<meta name="robots" content="noindex,nofollow">'
    new = '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">'
    if old not in text:
        raise RuntimeError("Neveřejný zdroj neobsahuje očekávaný robots noindex.")
    text = text.replace(old, new, 1)
    if text.count(PUBLISHED) < 2:
        raise RuntimeError("Zdroj neobsahuje úplná publikační data.")
    ARTICLE.write_text(text, encoding="utf-8", newline="\n")


def run_common_pipeline() -> None:
    run("scripts/normalize_articles.py", "--write", "--check")
    run("scripts/generate_social_cards.py", "--write", "--check")
    run("scripts/finalize_launch.py")
    run("scripts/prepare_discovery.py")
    run("scripts/normalize_search_snippets.py")
    run("scripts/enforce_article_visibility.py")
    run("scripts/sort_articles_chronologically.py")


def remove_rss_item(text: str) -> str:
    pattern = re.compile(
        r"\s*<item>.*?" + re.escape(PUBLIC_URL) + r".*?</item>\s*",
        re.I | re.S,
    )
    return pattern.sub("\n", text)


def ensure_rss(title: str, description: str, image_url: str) -> None:
    path = ROOT / "rss.xml"
    text = remove_rss_item(path.read_text(encoding="utf-8"))
    safe_title = html.escape(title)
    cdata_description = description.replace("]]>", "]]]]><![CDATA[>")
    item = f'''    <item>
      <title>{safe_title}</title>
      <description><![CDATA[{cdata_description}]]></description>
      <link>{PUBLIC_URL}</link>
      <guid isPermaLink="true">{PUBLIC_URL}</guid>
      <pubDate>{format_datetime(PUBLISHED_DT)}</pubDate>
      <category>Město</category>
      <category>Životní prostředí</category>
      <category>Veřejná zeleň</category>
      <szn:image><szn:url>{html.escape(image_url)}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>'''
    anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if anchor not in text:
        raise RuntimeError("V RSS chybí vkládací marker.")
    text = text.replace(anchor, anchor + "\n" + item, 1)
    if re.search(r"<lastBuildDate>.*?</lastBuildDate>", text, re.S):
        text = re.sub(
            r"<lastBuildDate>.*?</lastBuildDate>",
            f"<lastBuildDate>{format_datetime(PUBLISHED_DT)}</lastBuildDate>",
            text,
            count=1,
            flags=re.S,
        )
    path.write_text(text, encoding="utf-8", newline="\n")


def ensure_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if PUBLIC_URL not in text:
        entry = f"  <url><loc>{PUBLIC_URL}</loc><lastmod>2026-08-01</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n"
        if "</urlset>" not in text:
            raise RuntimeError("Sitemap nemá uzavírací element urlset.")
        text = text.replace("</urlset>", entry + "</urlset>", 1)
        path.write_text(text, encoding="utf-8", newline="\n")


def ensure_news_sitemap(title: str) -> None:
    path = ROOT / "news-sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if PUBLIC_URL not in text:
        entry = (
            "  <url>"
            f"<loc>{PUBLIC_URL}</loc>"
            "<news:news><news:publication>"
            "<news:name>Naše Kadaň</news:name><news:language>cs</news:language>"
            "</news:publication>"
            f"<news:publication_date>{PUBLISHED}</news:publication_date>"
            f"<news:title>{html.escape(title)}</news:title>"
            "</news:news></url>\n"
        )
        if "</urlset>" not in text:
            raise RuntimeError("News sitemap nemá uzavírací element urlset.")
        text = text.replace("</urlset>", entry + "</urlset>", 1)
        path.write_text(text, encoding="utf-8", newline="\n")


def ensure_facebook_trigger() -> None:
    path = ROOT / ".github" / "facebook-publish-trigger.txt"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    article_path = f"clanky/{SLUG}.html"
    lines = [line.strip() for line in existing.splitlines() if line.strip()]
    if article_path not in lines:
        lines.append(article_path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate() -> dict[str, str]:
    text = ARTICLE.read_text(encoding="utf-8")
    title = first_tag(text, "h1")
    description = attr(text, "name", "description")
    image_url = attr(text, "property", "og:image")
    if not all((title, description, image_url)):
        raise RuntimeError("Článek nemá úplná metadata.")
    if EXPECTED not in text:
        raise RuntimeError("V článku chybí kontrolní věta.")
    required = (
        'data-poll-id="sekani-travniku-kadan-2026"',
        "/api/analytics/pageview",
        "index,follow",
        "105,2 ha",
        "282",
        "7–25 cm",
    )
    for marker in required:
        if marker not in text:
            raise RuntimeError(f"V článku chybí marker {marker!r}.")
    if "noindex,nofollow" in text:
        raise RuntimeError("Veřejný článek zůstal noindex.")

    image_path = ROOT / "social" / image_url.rsplit("/", 1)[-1]
    if not image_path.exists() or image_path.stat().st_size < 10_000:
        raise RuntimeError("Sociální obrázek chybí nebo je příliš malý.")

    ensure_rss(title, description, image_url)
    ensure_sitemap()
    ensure_news_sitemap(title)
    ensure_facebook_trigger()

    checks = {
        ROOT / "index.html": f"/clanky/{SLUG}.html",
        ROOT / "clanky" / "index.html": f"/clanky/{SLUG}.html",
        ROOT / "rss.xml": PUBLIC_URL,
        ROOT / "sitemap.xml": PUBLIC_URL,
        ROOT / "news-sitemap.xml": PUBLIC_URL,
    }
    for path, marker in checks.items():
        if marker not in path.read_text(encoding="utf-8"):
            raise RuntimeError(f"Soubor {path.relative_to(ROOT)} neobsahuje {marker}.")

    payload = {
        "article": str(ARTICLE.relative_to(ROOT)),
        "publicUrl": PUBLIC_URL,
        "socialUrl": image_url,
        "socialFile": str(image_path.relative_to(ROOT)),
        "published": PUBLISHED,
        "title": title,
    }
    status_path = ROOT / ".github" / "greenery-publication-bundle.json"
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    publish_article()
    run_common_pipeline()
    payload = validate()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
