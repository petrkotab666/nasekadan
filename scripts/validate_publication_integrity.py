#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_DIR = ROOT / "clanky"
HOME = ROOT / "index.html"
ARCHIVE = ARTICLE_DIR / "index.html"
SITEMAP = ROOT / "sitemap.xml"
RSS = ROOT / "rss.xml"
SITE_HOST = "nasekadan.cz"
HOME_RECENT_LIMIT = 6
RSS_MAX_AGE_DAYS = 120

TRAIN_PATH = "/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html"
TRAIN_URL = f"https://{SITE_HOST}{TRAIN_PATH}"


@dataclass(frozen=True)
class Article:
    path: Path
    canonical: str
    relative_url: str
    published: datetime | None


def read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Chybí povinný soubor: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def parse_datetime(value: str) -> datetime | None:
    value = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def extract_published(html: str) -> datetime | None:
    patterns = (
        r'<meta\s+property=["\']article:published_time["\']\s+content=["\']([^"\']+)',
        r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']article:published_time["\']',
        r'["\']datePublished["\']\s*:\s*["\']([^"\']+)',
    )
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            parsed = parse_datetime(match.group(1))
            if parsed:
                return parsed
    return None


def extract_canonical(html: str) -> str | None:
    patterns = (
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)',
        r'<link\s+href=["\']([^"\']+)["\']\s+rel=["\']canonical["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            return match.group(1).strip()
    return None


def is_private_or_unpublished(html: str, published: datetime | None, now: datetime) -> bool:
    robots = re.findall(r'<meta\s+[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)', html, flags=re.I)
    if any("noindex" in value.lower() for value in robots):
        return True
    if published and published > now + timedelta(minutes=10):
        return True
    return False


def collect_articles(now: datetime) -> list[Article]:
    articles: list[Article] = []
    for path in sorted(ARTICLE_DIR.glob("*.html")):
        if path.name == "index.html":
            continue
        html = read(path)
        published = extract_published(html)
        if is_private_or_unpublished(html, published, now):
            continue
        canonical = extract_canonical(html)
        if not canonical:
            continue
        parsed = urlsplit(canonical)
        if parsed.scheme != "https" or parsed.netloc not in {SITE_HOST, f"www.{SITE_HOST}"}:
            continue
        articles.append(
            Article(
                path=path,
                canonical=canonical.replace(f"https://www.{SITE_HOST}", f"https://{SITE_HOST}"),
                relative_url=parsed.path,
                published=published,
            )
        )
    return articles


def present(text: str, article: Article) -> bool:
    return article.relative_url in text or article.canonical in text


def main() -> int:
    now = datetime.now(timezone.utc)
    home = read(HOME)
    archive = read(ARCHIVE)
    sitemap = read(SITEMAP)
    rss = read(RSS)
    articles = collect_articles(now)
    errors: list[str] = []

    if not articles:
        errors.append("Nebyl nalezen žádný veřejně publikovaný článek.")

    for article in articles:
        label = article.path.relative_to(ROOT)
        if not present(archive, article):
            errors.append(f"{label}: článek chybí v archivu /clanky/.")
        if article.canonical not in sitemap:
            errors.append(f"{label}: článek chybí v sitemap.xml.")
        if article.published and article.published >= now - timedelta(days=RSS_MAX_AGE_DAYS):
            if article.canonical not in rss:
                errors.append(f"{label}: čerstvý článek chybí v rss.xml.")

    dated = sorted(
        (article for article in articles if article.published and article.published <= now),
        key=lambda article: article.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    for article in dated[:HOME_RECENT_LIMIT]:
        if not present(home, article):
            errors.append(
                f"{article.path.relative_to(ROOT)}: jeden z {HOME_RECENT_LIMIT} nejnovějších článků chybí na titulní stránce."
            )

    train_file = ARTICLE_DIR / TRAIN_PATH.rsplit("/", 1)[-1]
    if not train_file.is_file():
        errors.append("Zdrojový článek o nočních výlukách byl odstraněn.")
    for location, text in (
        ("titulní stránce", home),
        ("archivu", archive),
        ("sitemapě", sitemap),
        ("RSS", rss),
    ):
        if TRAIN_PATH not in text and TRAIN_URL not in text:
            errors.append(f"Článek o nočních výlukách chybí v {location}.")

    if errors:
        print("KONTROLA PUBLIKOVANÝCH ČLÁNKŮ SELHALA", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Kontrola publikace je v pořádku: {len(articles)} veřejných článků, "
        f"{min(HOME_RECENT_LIMIT, len(dated))} nejnovějších ověřeno na titulní stránce."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
