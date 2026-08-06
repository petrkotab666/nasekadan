#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import ssl
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
REGISTRY_PATH = ROOT / "data" / "published-content-index.json"
STATUS_PATH = ROOT / ".github" / "canonical-content-audit-status.json"
ARTICLE_RE = re.compile(r"https://nasekadan\.cz/clanky/[^\"'<>\s?]+\.html")
REL_ARTICLE_RE = re.compile(r"(?:https://nasekadan\.cz)?(/clanky/[^\"'<>\s?]+\.html)")


def fetch(path: str) -> str:
    sep = "&" if "?" in path else "?"
    url = f"{BASE}{path}{sep}audit={int(time.time() * 1000)}"
    # HTTP hlavičky se v Pythonu serializují přes latin-1. User-Agent proto
    # musí zůat čistě ASCII; diakritika zde dříve shazovala celý audit až
    # po úspěšném nasazení webu a vytvářela falešný incident.
    req = Request(
        url,
        headers={
            "User-Agent": "NaseKadan-canonical-audit/1.1",
            "Cache-Control": "no-cache",
        },
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urlopen(req, timeout=40, context=ctx) as response:
        if response.status != 200:
            raise RuntimeError(f"{url} vrátil HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")


def abs_url(value: str) -> str:
    return value if value.startswith("http") else BASE + value


def article_urls(text: str) -> set[str]:
    return {abs_url(match) for match in REL_ARTICLE_RE.findall(text) if "/clanky/strana-" not in match}


def rss_urls(text: str) -> list[str]:
    return [u.strip() for u in re.findall(r"<link>\s*(https://nasekadan\.cz/clanky/[^<]+\.html)\s*</link>", text)]


def registry_entries() -> list[dict]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    # Aktuální kanonický registr používá pole "articles". Starší verze auditu
    # pracovaly s polem "entries", proto podporujeme obě schémata, aby změna
    # názvu klíče nemohla po úspěšném nasazení vyvolat falešný incident.
    entries = payload.get("articles")
    if not isinstance(entries, list) or not entries:
        entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError(
            "Kanonický registr je prázdný nebo neplatný; očekává se pole articles nebo entries."
        )
    return entries


def publication_status(entry: dict) -> str:
    """Return editorial publication state without confusing it with channel flags.

    In schema 1.5, ``status`` is a mapping such as homepage/archive/RSS flags,
    while the actual publication state is stored in ``publication_status``.
    Older registry schemas used a string directly in ``status``. Supporting
    both forms prevents a TypeError and keeps drafts/removed items excluded.
    """
    value = entry.get("publication_status")
    if isinstance(value, str) and value:
        return value
    legacy = entry.get("status")
    if isinstance(legacy, str) and legacy:
        return legacy
    return "published"


def parse_published(entry: dict) -> datetime:
    value = (
        entry.get("published_at")
        or entry.get("date_published")
        or entry.get("published")
    )
    if not value:
        raise RuntimeError(f"V registru chybí datum publikace: {entry}")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def current_registry_urls(entries: list[dict]) -> list[str]:
    now = datetime.now(timezone.utc)
    items = []
    for entry in entries:
        url = entry.get("canonical_url") or entry.get("url")
        if not url or "/clanky/" not in url:
            continue
        if publication_status(entry) in {"draft", "scheduled", "removed"}:
            continue
        published = parse_published(entry)
        if published <= now:
            items.append((published, url))
    items.sort(reverse=True)
    return [url for _, url in items]


def archive_pages(first_page: str) -> list[str]:
    pages = ["/clanky/"]
    # Generátor archivu používá podle šablony absolutní URL, kořenové odkazy
    # /clanky/strana-N.html nebo relativní strana-N.html. Audit musí umět
    # všechny tři varianty, jinak zkontroluje jen první stránku a falešně
    # označí všechny starší články za chybějící.
    for page in re.findall(
        r'href=["\']((?:https://nasekadan\.cz)?(?:/clanky/)?strana-\d+\.html)["\']',
        first_page,
    ):
        if page.startswith(BASE):
            normalized = page[len(BASE):]
        elif page.startswith("/"):
            normalized = page
        else:
            normalized = f"/clanky/{page}"
        if normalized not in pages:
            pages.append(normalized)
    return pages


def exact_h1(text: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
    if not match:
        raise RuntimeError("Stránka nemá H1.")
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-status", action="store_true")
    args = parser.parse_args()

    entries = registry_entries()
    expected = current_registry_urls(entries)
    expected_set = set(expected)
    if not expected:
        raise RuntimeError("Registr neobsahuje žádný aktuální článek.")

    home_text = fetch("/")
    archive_first = fetch("/clanky/")
    archive_texts = [archive_first]
    for page in archive_pages(archive_first)[1:]:
        archive_texts.append(fetch(page))
    rss_text = fetch("/rss.xml")
    sitemap_text = fetch("/sitemap.xml")
    news_text = fetch("/news-sitemap.xml")
    llms_text = fetch("/llms.txt")
    health_text = fetch("/deployment-health.txt")

    archive_found: set[str] = set()
    for text in archive_texts:
        archive_found |= article_urls(text)
    rss_found = set(rss_urls(rss_text))
    sitemap_found = set(ARTICLE_RE.findall(sitemap_text))
    llms_found = set(ARTICLE_RE.findall(llms_text))
    news_found = set(ARTICLE_RE.findall(news_text))

    missing_archive = sorted(expected_set - archive_found)
    missing_rss = sorted(expected_set - rss_found)
    missing_sitemap = sorted(expected_set - sitemap_found)

    # llms.txt je záměrně stručný výběr nejnovějších článků, nikoli úplný
    # kanonický archiv. Kontrolujeme proto jen jeho dostupnost a neprázdnost;
    # úplnost vyžadujeme u archivu, RSS a sitemap podle redakčních pravidel.
    if not llms_text.strip() or not llms_found:
        raise RuntimeError("llms.txt je prázdný nebo neobsahuje žádný článek.")

    # News sitemap má podle pravidel vyhledávačů obsahovat jen čerstvé články,
    # proto zde vyžadujeme aktuální dvoudenní okno, ne celou historii.
    now = datetime.now(timezone.utc)
    two_days_ago = now.timestamp() - 2 * 86400
    expected_news = {
        (entry.get("canonical_url") or entry.get("url"))
        for entry in entries
        if (entry.get("canonical_url") or entry.get("url"))
        and publication_status(entry) not in {"draft", "scheduled", "removed"}
        and parse_published(entry).timestamp() >= two_days_ago
        and parse_published(entry) <= now
    }
    missing_news = sorted(expected_news - news_found)

    if missing_archive or missing_rss or missing_sitemap or missing_news:
        raise RuntimeError(
            "Kanonické kanály nejsou úplné: "
            f"archiv={missing_archive}, rss={missing_rss}, sitemap={missing_sitemap}, "
            f"news={missing_news}"
        )

    # Ověření prvních článků přímo zabraňuje stavu, kdy jsou odkazy přítomné,
    # ale samotný HTML soubor na serveru chybí nebo byl přepsán.
    checked = 0
    for url in expected[: min(20, len(expected))]:
        path = url.removeprefix(BASE)
        article = fetch(path)
        h1 = exact_h1(article)
        entry = next(
            e
            for e in entries
            if (e.get("canonical_url") or e.get("url")) == url
        )
        expected_h1 = entry.get("h1") or entry.get("title") or entry.get("headline")
        if expected_h1 and h1 != expected_h1:
            raise RuntimeError(f"Neshoda H1 u {url}: {h1!r} != {expected_h1!r}")
        if "noindex" in article.lower():
            raise RuntimeError(f"Publikovaný článek má noindex: {url}")
        checked += 1

    home_urls = article_urls(home_text)
    if not home_urls:
        raise RuntimeError("Titulní stránka neobsahuje žádný článek.")
    if expected[0] not in home_urls:
        raise RuntimeError(f"Nejnovější článek není na titulce: {expected[0]}")

    if "status=ok" not in health_text:
        raise RuntimeError("deployment-health.txt nemá status=ok")

    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
        "article_count": len(expected),
        "direct_articles_checked": checked,
        "archive_pages": len(archive_texts),
        "rss_count": len(rss_found),
        "sitemap_count": len(sitemap_found),
        "news_count": len(news_found),
        "llms_count": len(llms_found),
        "latest": expected[0],
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))
    if args.write_status:
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATUS_PATH.write_text(
            json.dumps(status, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
