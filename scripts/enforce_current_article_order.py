#!/usr/bin/env python3
"""Zajistí úplnou a chronologickou viditelnost publikovaných článků.

Přehledy se vždy znovu vytvoří ze skutečných článkových souborů. Kontrola není
vázána na konkrétní historický článek: ověřuje aktuální nejnovější text na
titulce a všechny dosud publikované články v celém stránkovaném archivu a RSS.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from enforce_article_visibility import article_info, main as enforce_visibility
from ensure_all_published_articles_in_rss import main as ensure_rss
from sort_articles_chronologically import main as sort_all
from enforce_latest_homepage_hero import main as enforce_latest_hero

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE_DIR = ROOT / "clanky"
ARCHIVE = ARCHIVE_DIR / "index.html"
RSS = ROOT / "rss.xml"


def published_articles() -> list[dict]:
    now = datetime.now(timezone.utc)
    articles: list[dict] = []
    for path in ARCHIVE_DIR.glob("*.html"):
        if path.name == "index.html" or path.name.startswith("strana-"):
            continue
        info = article_info(path)
        if info is None:
            continue
        published = info["dt"]
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        if published.astimezone(timezone.utc) <= now:
            articles.append(info)
    articles.sort(key=lambda item: item["dt"], reverse=True)
    return articles


def archive_text() -> str:
    pages = [ARCHIVE, *sorted(ARCHIVE_DIR.glob("strana-*.html"))]
    missing = [str(path.relative_to(ROOT)) for path in pages if not path.is_file()]
    if missing:
        raise RuntimeError(f"Chybí stránky archivu: {', '.join(missing)}")
    return "\n".join(path.read_text(encoding="utf-8") for path in pages)


def main() -> int:
    if not HOME.is_file() or not ARCHIVE.is_file() or not RSS.is_file():
        raise RuntimeError("Chybí titulní stránka, archiv článků nebo RSS.")

    enforce_visibility()
    ensure_rss()
    sort_all()
    enforce_latest_hero()

    articles = published_articles()
    if not articles:
        raise RuntimeError("Nebyl nalezen žádný publikovaný článek.")

    home = HOME.read_text(encoding="utf-8")
    archive = archive_text()
    rss = RSS.read_text(encoding="utf-8")

    newest = articles[0]
    if newest["href"] not in home:
        raise RuntimeError(
            f"Nejnovější článek {newest['href']} chybí na titulní stránce."
        )

    missing_archive: list[str] = []
    missing_rss: list[str] = []
    for article in articles:
        href = article["href"]
        url = "https://nasekadan.cz" + href
        if href not in archive:
            missing_archive.append(href)
        if url not in rss:
            missing_rss.append(href)

    if missing_archive:
        raise RuntimeError(
            "Ve stránkovaném archivu chybějí publikované články: "
            + ", ".join(missing_archive)
        )
    if missing_rss:
        raise RuntimeError(
            "V RSS chybějí publikované články: " + ", ".join(missing_rss)
        )

    print(
        f"Ověřeno {len(articles)} publikovaných článků: nejnovější je na titulce, "
        "všechny jsou v celém archivu i RSS a přehledy jsou chronologicky seřazené."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
