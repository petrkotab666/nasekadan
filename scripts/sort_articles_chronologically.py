#!/usr/bin/env python3
"""Seřadí články všude výhradně podle data a času zveřejnění.

Pořadí se načítá z article:published_time nebo datePublished v samotném článku,
nikoli z ručně zadané pozice karty. Týdenní kulturní přehled proto nemůže být
připnut před novější zprávy jen proto, že používá spravované značky.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, format_datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"
NEWS = ROOT / "news-sitemap.xml"
WEEKLY_TOKEN = "kam-v-kadani-a-okoli-"
START = "<!-- WEEKLY-EVENTS-START -->"
END = "<!-- WEEKLY-EVENTS-END -->"
ARTICLE_RE = re.compile(r"<article\b[^>]*>.*?</article>", re.I | re.S)
ITEM_RE = re.compile(r"<item>.*?</item>", re.I | re.S)
URL_RE = re.compile(r"<url>.*?</url>", re.I | re.S)
PAGINATION_RE = re.compile(r'<nav\b[^>]*class=["\'][^"\']*article-pagination[^"\']*["\'][^>]*>.*?</nav>', re.I | re.S)


def iso_datetime(value: str) -> datetime:
    value = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def article_href(block: str) -> str:
    found = re.search(r'href=["\'](/clanky/[^"\']+\.html)["\']', block, re.I)
    return found.group(1) if found else ""


def article_published(href: str) -> datetime:
    if not href:
        return datetime.min.replace(tzinfo=timezone.utc)
    path = ROOT / href.lstrip("/")
    if not path.is_file():
        return datetime.min.replace(tzinfo=timezone.utc)
    text = path.read_text(encoding="utf-8")
    patterns = (
        r'<meta\b[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
        r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']',
        r'"datePublished"\s*:\s*"([^"]+)"',
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            try:
                return iso_datetime(match.group(1))
            except ValueError:
                pass
    return datetime.min.replace(tzinfo=timezone.utc)


def wrap_weekly(block: str, indent: str = "    ") -> str:
    if WEEKLY_TOKEN in block:
        return f"{indent}{START}\n{block.strip()}\n{indent}{END}"
    return block.strip()


def sorted_article_blocks(body: str) -> list[str]:
    clean = re.sub(rf"\s*{re.escape(START)}.*?{re.escape(END)}\s*", lambda m: ARTICLE_RE.search(m.group(0)).group(0) if ARTICLE_RE.search(m.group(0)) else "", body, flags=re.S)
    blocks = ARTICLE_RE.findall(clean)
    decorated = []
    for index, block in enumerate(blocks):
        href = article_href(block)
        decorated.append((article_published(href), -index, block))
    decorated.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in decorated]


def replace_section(path: Path, start_marker: str, end_marker: str, *, archive: bool) -> list[str]:
    text = path.read_text(encoding="utf-8")
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f"V {path} chybí začátek seznamu")
    body_start = start + len(start_marker)
    end = text.find(end_marker, body_start)
    if end < 0:
        raise RuntimeError(f"V {path} chybí konec seznamu")
    body = text[body_start:end]
    blocks = sorted_article_blocks(body)
    indent = "    "

    # Generátor viditelnosti vkládá za karty stránkovací <nav>. Starší verze
    # tohoto třídicího kroku při přepsání sekce zachovala jen <article> bloky,
    # takže na první stránce archivu zmizel odkaz na stranu 2, přestože
    # strana-2.html až strana-N.html na serveru existovaly. Navigaci proto
    # výslovně zachovat. Na titulce je navíc potřeba obnovit uzavření .article-list.
    pagination_match = PAGINATION_RE.search(body)
    pagination = pagination_match.group(0).strip() if pagination_match else ""
    rendered = "\n".join(wrap_weekly(block, indent) for block in blocks)
    if archive:
        suffix = pagination
    else:
        suffix = "</div>"
        if pagination:
            suffix += "\n" + pagination
    replacement = "\n" + rendered
    if suffix:
        replacement += "\n" + indent + suffix
    replacement += "\n    "

    text = text[:body_start] + replacement + text[end:]
    path.write_text(text, encoding="utf-8", newline="\n")
    return blocks


def update_archive_jsonld(blocks: list[str]) -> None:
    text = ARCHIVE.read_text(encoding="utf-8")
    scripts = list(re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S))
    for match in scripts:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph", []) if isinstance(data, dict) else []
        itemlist = next((node for node in graph if isinstance(node, dict) and node.get("@type") == "ItemList"), None)
        if itemlist is None:
            continue
        elements = []
        for position, block in enumerate(blocks, 1):
            href = article_href(block)
            if not href:
                continue
            title_match = re.search(r"<h[23]\b[^>]*>(.*?)</h[23]>", block, re.I | re.S)
            title = strip_tags(title_match.group(1)) if title_match else href
            elements.append({
                "@type": "ListItem",
                "position": position,
                "url": "https://nasekadan.cz" + href,
                "name": title,
            })
        itemlist["itemListElement"] = elements
        itemlist["numberOfItems"] = len(elements)
        replacement = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + "</script>"
        text = text[:match.start()] + replacement + text[match.end():]
        ARCHIVE.write_text(text, encoding="utf-8", newline="\n")
        return


def rss_item_date(item: str) -> datetime:
    match = re.search(r"<pubDate>(.*?)</pubDate>", item, re.I | re.S)
    if not match:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = parsedate_to_datetime(strip_tags(match.group(1)))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)


def sort_rss() -> None:
    text = RSS.read_text(encoding="utf-8")
    text = re.sub(rf"\s*{re.escape(START)}\s*", "\n", text)
    text = re.sub(rf"\s*{re.escape(END)}\s*", "\n", text)
    items = ITEM_RE.findall(text)
    items.sort(key=rss_item_date, reverse=True)
    text = ITEM_RE.sub("", text)
    anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if anchor not in text:
        raise RuntimeError("RSS nemá atom:link")
    rendered = []
    for item in items:
        if WEEKLY_TOKEN in item:
            rendered.append(f"    {START}\n{item.strip()}\n    {END}")
        else:
            rendered.append(item.strip())
    text = text.replace(anchor, anchor + "\n    " + "\n\n    ".join(rendered), 1)
    if items:
        latest = rss_item_date(items[0])
        text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{format_datetime(latest)}</lastBuildDate>", text, count=1)
    RSS.write_text(text, encoding="utf-8", newline="\n")


def news_date(block: str) -> datetime:
    match = re.search(r"<news:publication_date>(.*?)</news:publication_date>", block, re.I | re.S)
    if not match:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        return iso_datetime(strip_tags(match.group(1)))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def sort_news_sitemap() -> None:
    text = NEWS.read_text(encoding="utf-8")
    blocks = URL_RE.findall(text)
    blocks.sort(key=news_date, reverse=True)
    text = URL_RE.sub("", text)
    text = text.replace("</urlset>", "\n" + "\n".join("  " + block.strip() for block in blocks) + "\n</urlset>")
    NEWS.write_text(text, encoding="utf-8", newline="\n")


def validate(blocks: list[str], label: str) -> None:
    dates = [article_published(article_href(block)) for block in blocks]
    if dates != sorted(dates, reverse=True):
        raise RuntimeError(f"{label} není chronologicky sestupně")


def main() -> int:
    home_blocks = replace_section(HOME, '<div class="article-list">', '<p class="archive-note">', archive=False)
    archive_blocks = replace_section(ARCHIVE, '<section class="archive-list" aria-label="Chronologický přehled článků">', '</section>', archive=True)
    validate(home_blocks, "Titulní stránka")
    validate(archive_blocks, "Archiv")
    update_archive_jsonld(archive_blocks)
    sort_rss()
    sort_news_sitemap()
    print("Články jsou seřazené sestupně podle article:published_time/datePublished; stránkování zůstalo zachované.")
    for block in home_blocks[:10]:
        href = article_href(block)
        print(article_published(href).isoformat(), href)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
