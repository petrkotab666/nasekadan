#!/usr/bin/env python3
"""Doplní do RSS chybějící nedávno publikované články.

Zdroj pravdy je samotný článek: URL, H1, meta description, datum publikace a
OG obrázek. Skript je idempotentní a nepřepisuje již existující RSS položky.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "clanky"
RSS = ROOT / "rss.xml"
BASE = "https://nasekadan.cz"
RECENT_DAYS = 14
ATOM_ANCHOR = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'


def clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first(patterns: tuple[str, ...], text: str, default: str = "") -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return clean_html(match.group(1))
    return default


def published_at(text: str) -> datetime | None:
    raw = first((
        r'<meta\b[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
        r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']',
        r'"datePublished"\s*:\s*"([^"]+)"',
    ), text)
    if not raw:
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def cdata(value: str) -> str:
    return value.replace("]]>", "]]]]><![CDATA[>")


def item_for(path: Path, text: str, published: datetime) -> str:
    href = f"/clanky/{path.name}"
    url = BASE + href
    title = first((r'<h1\b[^>]*>(.*?)</h1>', r'<title>(.*?)</title>'), text, path.stem)
    title = re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", title)
    description = first((
        r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)',
        r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']',
        r'<p\b[^>]*class=["\'][^"\']*leadtext[^"\']*["\'][^>]*>(.*?)</p>',
    ), text, title)
    image = first((
        r'<meta\b[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)',
        r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
    ), text, BASE + "/social-card.png")
    tag = first((r'<p\b[^>]*class=["\'][^"\']*tag[^"\']*["\'][^>]*>(.*?)</p>',), text, "Kadaň")
    categories = []
    for part in re.split(r"\s*[·|]\s*", tag):
        part = re.sub(r"\b\d{1,2}\.\s*[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž]+\s+\d{4}\b", "", part).strip(" ·|")
        if part and not re.fullmatch(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}", part):
            categories.append(part.title())
    if not categories:
        categories = ["Kadaň"]
    category_xml = "".join(f"\n      <category>{escape(value)}</category>" for value in categories[:4])
    return f'''    <item>
      <title>{escape(title)}</title>
      <description><![CDATA[{cdata(description)}]]></description>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{format_datetime(published)}</pubDate>{category_xml}
      <szn:image><szn:url>{escape(image)}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>'''


def main() -> int:
    if not RSS.is_file():
        raise RuntimeError("Chybí rss.xml")
    xml = RSS.read_text(encoding="utf-8")
    if ATOM_ANCHOR not in xml:
        raise RuntimeError("V rss.xml chybí atom:link kotva")

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=RECENT_DAYS)
    missing: list[tuple[datetime, str, str]] = []
    for path in sorted(ARTICLES.glob("*.html")):
        if path.name == "index.html":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', text, re.I):
            continue
        published = published_at(text)
        if published is None:
            continue
        utc = published.astimezone(timezone.utc)
        if utc < cutoff or utc > now + timedelta(minutes=2):
            continue
        url = f"{BASE}/clanky/{path.name}"
        if url in xml:
            continue
        missing.append((published, url, item_for(path, text, published)))

    if not missing:
        print("RSS již obsahuje všechny nedávné články.")
        return 0

    missing.sort(key=lambda row: row[0], reverse=True)
    rendered = "\n" + "\n".join(row[2] for row in missing)
    xml = xml.replace(ATOM_ANCHOR, ATOM_ANCHOR + rendered, 1)
    newest = max(row[0] for row in missing)
    current_items = re.findall(r"<pubDate>(.*?)</pubDate>", xml, re.I | re.S)
    dates = [newest]
    for raw in current_items:
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(clean_html(raw))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dates.append(dt)
        except (TypeError, ValueError):
            pass
    latest = max(dates)
    xml = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{format_datetime(latest)}</lastBuildDate>", xml, count=1)
    RSS.write_text(xml, encoding="utf-8", newline="\n")
    print("Do RSS doplněno:")
    for _, url, _ in missing:
        print("-", url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
