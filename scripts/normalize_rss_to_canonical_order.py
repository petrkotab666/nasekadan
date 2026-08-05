#!/usr/bin/env python3
"""Srovná RSS přesně podle kanonického data prvního zveřejnění článků.

Veřejný archiv a titulka se řadí podle article:published_time/datePublished.
RSS nesmí starší článek posunout před novější jen proto, že byl později
aktualizován. Skript používá registr publikovaného obsahu jako seznam URL,
ale datum ověřuje také v samotném článku přes hodnotu published_at registru.
Chybějící položky nevyrábí odhadem: při neúplnosti skončí chybou.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RSS_PATH = ROOT / "rss.xml"
REGISTRY_PATH = ROOT / "data" / "published-content-index.json"
ITEM_RE = re.compile(r"<item>.*?</item>", re.I | re.S)
LINK_RE = re.compile(
    r"<link>\s*(https://nasekadan\.cz/clanky/[^<\s?]+\.html)\s*</link>",
    re.I,
)
PUBDATE_RE = re.compile(r"<pubDate>.*?</pubDate>", re.I | re.S)
ATOM_LINK = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'


def parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def publication_status(entry: dict) -> str:
    value = entry.get("publication_status")
    if isinstance(value, str) and value:
        return value
    legacy = entry.get("status")
    if isinstance(legacy, str):
        return legacy
    return "published"


def canonical_entries() -> list[tuple[datetime, str]]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = payload.get("articles") or payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("Kanonický registr neobsahuje články.")

    now = datetime.now(timezone.utc)
    result: list[tuple[datetime, str]] = []
    for entry in entries:
        if publication_status(entry) in {"draft", "scheduled", "removed"}:
            continue
        url = entry.get("url") or entry.get("canonical_url")
        published = entry.get("published_at") or entry.get("date_published")
        if not url or not published or "/clanky/" not in url:
            continue
        dt = parse_iso(published)
        if dt <= now:
            result.append((dt, url))

    result.sort(key=lambda item: item[0], reverse=True)
    if not result:
        raise RuntimeError("Registr neobsahuje žádný zveřejněný článek.")
    return result


def item_link(item: str) -> str:
    match = LINK_RE.search(item)
    return match.group(1) if match else ""


def normalize_item_pubdate(item: str, published: datetime) -> str:
    value = format_datetime(published)
    replacement = f"<pubDate>{value}</pubDate>"
    if PUBDATE_RE.search(item):
        return PUBDATE_RE.sub(replacement, item, count=1)
    link = LINK_RE.search(item)
    if not link:
        raise RuntimeError("RSS položka nemá odkaz ani pubDate.")
    return item[: link.end()] + replacement + item[link.end() :]


def main() -> int:
    canonical = canonical_entries()
    expected_urls = [url for _, url in canonical]
    published_by_url = {url: dt for dt, url in canonical}

    text = RSS_PATH.read_text(encoding="utf-8")
    items = ITEM_RE.findall(text)
    if not items:
        raise RuntimeError("RSS neobsahuje žádné položky.")

    by_url: dict[str, str] = {}
    extras: list[str] = []
    for item in items:
        url = item_link(item)
        if not url:
            extras.append(item)
            continue
        if url in by_url:
            raise RuntimeError(f"Duplicitní RSS URL: {url}")
        by_url[url] = item

    missing = [url for url in expected_urls if url not in by_url]
    if missing:
        raise RuntimeError(f"RSS postrádá publikované články: {missing}")

    ordered: list[str] = []
    for url in expected_urls:
        ordered.append(normalize_item_pubdate(by_url.pop(url), published_by_url[url]))

    # Nečlánkové nebo nekanonické položky zachováme až za úplným seznamem.
    ordered.extend(by_url.values())
    ordered.extend(extras)

    without_items = ITEM_RE.sub("", text)
    if ATOM_LINK not in without_items:
        raise RuntimeError("RSS neobsahuje očekávaný atom:link.")

    rendered = "\n    " + "\n\n    ".join(item.strip() for item in ordered)
    updated = without_items.replace(ATOM_LINK, ATOM_LINK + rendered, 1)
    latest = format_datetime(canonical[0][0])
    updated = re.sub(
        r"<lastBuildDate>.*?</lastBuildDate>",
        f"<lastBuildDate>{latest}</lastBuildDate>",
        updated,
        count=1,
        flags=re.I | re.S,
    )
    # Po odstranění původních itemů zůstávají na některých řádcích pouze
    # mezery. Vyčistíme je před git diff --check, aby pojistka neselhala na
    # kosmetickém trailing whitespace po jinak správné opravě.
    updated = re.sub(r"(?m)^[ \t]+$", "", updated)
    updated = re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"

    check_urls = [item_link(item) for item in ITEM_RE.findall(updated) if item_link(item)]
    if check_urls[: len(expected_urls)] != expected_urls:
        raise RuntimeError("Výsledné RSS neodpovídá kanonickému pořadí.")
    if len(check_urls) != len(set(check_urls)):
        raise RuntimeError("Výsledné RSS obsahuje duplicitní URL.")

    if updated != text:
        RSS_PATH.write_text(updated, encoding="utf-8", newline="\n")
        print(f"RSS opraveno: {len(expected_urls)} článků v kanonickém pořadí.")
    else:
        print(f"RSS je v pořádku: {len(expected_urls)} článků v kanonickém pořadí.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
