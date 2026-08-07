#!/usr/bin/env python3
"""Blokující pojistka proti zmizení již publikovaných článků.

Kanonický seznam se odvozuje přímo z veřejných HTML článků, nikoli z titulky
nebo archivu, které jsou pouze generované pohledy. Umí také uložit vstupní
manifest před buildem a na konci sestavení proti němu ověřit, že žádný již
publikovaný článek nezmizel.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ARTICLE_RE = re.compile(r"^[^.].*\.html$")
PAGE_RE = re.compile(r"strana-\d+\.html$")


def parse_datetime(value: str) -> datetime | None:
    value = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def published_at(text: str) -> datetime | None:
    patterns = (
        r'<meta\s+property=["\']article:published_time["\']\s+content=["\']([^"\']+)',
        r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']article:published_time["\']',
        r'["\']datePublished["\']\s*:\s*["\']([^"\']+)',
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            dt = parse_datetime(match.group(1))
            if dt:
                return dt
    return None


def is_public_article(path: Path, *, now: datetime | None = None) -> bool:
    if path.name == "index.html" or PAGE_RE.fullmatch(path.name):
        return False
    if not ARTICLE_RE.fullmatch(path.name):
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"<html\b", text, re.I):
        return False
    if re.search(
        r'<meta\b(?=[^>]*\bname=["\']robots["\'])(?=[^>]*\bcontent=["\'][^"\']*\bnoindex\b)',
        text,
        re.I,
    ):
        return False
    dt = published_at(text)
    current = now or datetime.now(timezone.utc)
    if dt and dt > current + timedelta(minutes=10):
        return False
    return True


def canonical_articles(root: Path) -> list[str]:
    article_dir = root / "clanky"
    if not article_dir.is_dir():
        raise SystemExit(f"Chybí adresář článků: {article_dir}")
    now = datetime.now(timezone.utc)
    return sorted(
        f"clanky/{path.name}"
        for path in article_dir.glob("*.html")
        if is_public_article(path, now=now)
    )


def archive_text(target: Path) -> str:
    article_dir = target / "clanky"
    paths = [article_dir / "index.html"]
    paths.extend(sorted(article_dir.glob("strana-*.html")))
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in paths
        if path.is_file()
    )


def validate_article_file(path: Path, rel: str) -> list[str]:
    errors: list[str] = []
    if not path.is_file() or path.stat().st_size < 400:
        return [f"chybí nebo je prázdný článek {rel}"]
    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"<h1\b[^>]*>.*?</h1>", text, re.I | re.S):
        errors.append(f"článek nemá H1: {rel}")
    expected = f"https://nasekadan.cz/{rel}"
    if expected not in text:
        errors.append(f"článek nemá vlastní kanonickou URL: {rel}")
    return errors


def load_manifest(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.get("articles")
    if not isinstance(articles, list) or not all(isinstance(item, str) for item in articles):
        raise SystemExit(f"Neplatný manifest článků: {path}")
    return sorted(set(articles))


def verify(target: Path, articles: list[str]) -> list[str]:
    errors: list[str] = []
    archive = archive_text(target)
    rss = (target / "rss.xml").read_text(encoding="utf-8", errors="replace") if (target / "rss.xml").is_file() else ""
    sitemap = (target / "sitemap.xml").read_text(encoding="utf-8", errors="replace") if (target / "sitemap.xml").is_file() else ""

    if not archive:
        errors.append("chybí nebo je prázdný archiv článků")
    if not rss:
        errors.append("chybí nebo je prázdné RSS")
    if not sitemap:
        errors.append("chybí nebo je prázdná sitemap")

    for rel in articles:
        name = Path(rel).name
        errors.extend(validate_article_file(target / rel, rel))
        if name not in archive:
            errors.append(f"článek chybí v archivu: {rel}")
        if name not in rss:
            errors.append(f"článek chybí v RSS: {rel}")
        if name not in sitemap:
            errors.append(f"článek chybí v sitemapě: {rel}")

    target_articles = canonical_articles(target) if (target / "clanky").is_dir() else []
    if len(target_articles) < len(articles):
        errors.append(
            f"cílový web má méně článků než chráněný manifest: {len(target_articles)} < {len(articles)}"
        )
    return errors


def write_manifest(path: Path, articles: list[str]) -> None:
    payload = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(articles),
        "articles": articles,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=".")
    parser.add_argument("--target", default=".")
    parser.add_argument("--manifest", help="Použít již uložený chráněný seznam článků.")
    parser.add_argument("--write-manifest")
    parser.add_argument(
        "--write-manifest-only",
        action="store_true",
        help="Pouze uložit kanonický seznam článků a nekontrolovat publikační povrchy.",
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    target = Path(args.target).resolve()
    articles = load_manifest(Path(args.manifest)) if args.manifest else canonical_articles(source)

    if args.write_manifest:
        write_manifest(Path(args.write_manifest), articles)
    if args.write_manifest_only:
        print(f"Vstupní manifest uložen: {len(articles)} publikovaných článků.")
        return 0

    errors = verify(target, articles)
    print(f"Chráněných publikovaných článků: {len(articles)}")
    if errors:
        print("REGRESE PUBLIKOVANÉHO OBSAHU:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Úplnost publikovaných článků: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
