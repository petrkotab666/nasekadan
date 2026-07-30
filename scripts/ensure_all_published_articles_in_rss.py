#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RSS = ROOT / "rss.xml"
ARTICLES = ROOT / "clanky"
BASE = "https://nasekadan.cz"
ITEM_RE = re.compile(r"\s*<item>.*?</item>\s*", re.I | re.S)


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first(patterns: tuple[str, ...], text: str, default: str = "") -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return plain(match.group(1))
    return default


def parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def item_link(item: str) -> str:
    match = re.search(r"<link>(.*?)</link>", item, re.I | re.S)
    return plain(match.group(1)) if match else ""


def item_date(item: str) -> datetime:
    match = re.search(r"<pubDate>(.*?)</pubDate>", item, re.I | re.S)
    if not match:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = parsedate_to_datetime(plain(match.group(1)))
    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def article_item(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
        return None

    published = first((
        r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:published_time["\']',
        r'"datePublished"\s*:\s*"([^"]+)"',
    ), text)
    dt = parse_iso(published)
    if dt is None:
        return None

    title = first((r"<h1\b[^>]*>(.*?)</h1>", r"<title>(.*?)</title>"), text, path.stem)
    title = re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", title).strip()
    description = first((
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
        r'<p[^>]+class=["\'][^"\']*leadtext[^"\']*["\'][^>]*>(.*?)</p>',
    ), text, title)
    canonical = first((r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',), text)
    if not canonical:
        canonical = f"{BASE}/clanky/{path.name}"
    image = first((r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',), text)
    if not image:
        image = f"{BASE}/social-card.png"
    tag = first((r'<p[^>]+class=["\'][^"\']*tag[^"\']*["\'][^>]*>(.*?)</p>',), text, "Aktuálně")
    categories = [part.strip() for part in tag.split("·") if part.strip()][:3]
    if not categories:
        categories = ["Aktuálně"]

    safe_desc = description.replace("]]>", "] ]>")
    category_xml = "\n".join(f"      <category>{escape(category)}</category>" for category in categories)
    item = f'''    <item>
      <title>{escape(title)}</title>
      <description><![CDATA[{safe_desc}]]></description>
      <link>{escape(canonical)}</link>
      <guid isPermaLink="true">{escape(canonical)}</guid>
      <pubDate>{format_datetime(dt)}</pubDate>
{category_xml}
      <szn:image><szn:url>{escape(image)}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>'''
    return canonical, item


def main() -> int:
    text = RSS.read_text(encoding="utf-8")
    anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if anchor not in text:
        raise RuntimeError("RSS nemá atom:link vkládací bod.")

    items_by_url: dict[str, str] = {}
    for item in ITEM_RE.findall(text):
        url = item_link(item)
        if url and url not in items_by_url:
            items_by_url[url] = item.strip()

    added: list[str] = []
    for path in sorted(ARTICLES.glob("*.html")):
        if path.name == "index.html":
            continue
        result = article_item(path)
        if result is None:
            continue
        url, item = result
        if url not in items_by_url:
            items_by_url[url] = item
            added.append(url)

    items = list(items_by_url.values())
    items.sort(key=item_date, reverse=True)
    text = ITEM_RE.sub("\n", text)
    rendered = "\n\n".join(items)
    text = text.replace(anchor, anchor + "\n" + rendered, 1)
    if items:
        text = re.sub(
            r"<lastBuildDate>.*?</lastBuildDate>",
            f"<lastBuildDate>{format_datetime(item_date(items[0]))}</lastBuildDate>",
            text,
            count=1,
            flags=re.S,
        )
    RSS.write_text(text, encoding="utf-8", newline="\n")
    print(f"RSS obsahuje {len(items)} jedinečných článků; nově doplněno {len(added)}.")
    for url in added:
        print("Doplněno:", url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
