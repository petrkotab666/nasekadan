#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "clanky"
HOME = ROOT / "index.html"
ARCHIVE = ARTICLES_DIR / "index.html"
SITEMAP = ROOT / "sitemap.xml"
MANIFEST = ROOT / "data" / "article-integrity-manifest.json"
HOME_TOTAL = 14
BASE_URL = "https://nasekadan.cz"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first(patterns: list[str], text: str, default: str = "") -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return clean(match.group(1))
    return default


def is_public_article(path: Path) -> bool:
    if path.name == "index.html" or re.fullmatch(r"strana-\d+\.html", path.name):
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
        return False
    return bool(re.search(r'article:published_time|"datePublished"', text, re.I))


def article_info(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    published_raw = first([
        r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:published_time["\']',
        r'"datePublished"\s*:\s*"([^"]+)"',
    ], text)
    if not published_raw:
        raise RuntimeError(f"Publikovaný článek nemá datum: {path.relative_to(ROOT)}")
    published = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    title = first([r"<h1[^>]*>(.*?)</h1>", r"<title>(.*?)</title>"], text, path.stem)
    title = re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", title)
    rel = f"/clanky/{path.name}"
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "href": rel,
        "url": BASE_URL + rel,
        "title": title,
        "published_at": published.isoformat(),
        "timestamp": published.timestamp(),
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }


def load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"schema_version": 1, "articles": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def restore_missing_from_git(previous: dict) -> list[str]:
    restored: list[str] = []
    for item in previous.get("articles", []):
        rel = item.get("path")
        if not rel:
            continue
        target = ROOT / rel
        if target.exists():
            continue
        commit = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--all", "--", rel],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        if not commit:
            raise RuntimeError(f"Publikovaný článek zmizel a v historii není záloha: {rel}")
        blob = subprocess.run(
            ["git", "show", f"{commit}:{rel}"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        restored.append(rel)
    return restored


def published_articles() -> list[dict]:
    items = [article_info(path) for path in sorted(ARTICLES_DIR.glob("*.html")) if is_public_article(path)]
    items.sort(key=lambda item: item["timestamp"], reverse=True)
    if not items:
        raise RuntimeError("Nebyl nalezen žádný publikovaný článek.")
    urls = [item["url"] for item in items]
    if len(urls) != len(set(urls)):
        raise RuntimeError("Publikované články obsahují duplicitní URL.")
    return items


def write_manifest(articles: list[dict], previous: dict, restored: list[str]) -> None:
    previous_paths = {item.get("path") for item in previous.get("articles", []) if item.get("path")}
    current_paths = {item["path"] for item in articles}
    missing = sorted(previous_paths - current_paths)
    if missing:
        raise RuntimeError(f"Z manifestu zmizely publikované články: {missing}")
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(articles),
        "restored_in_this_run": restored,
        "policy": "published_article_paths_are_append_only_and_missing_files_are_restored_from_git_history",
        "articles": [{k: v for k, v in item.items() if k != "timestamp"} for item in articles],
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def archive_texts() -> list[str]:
    pages = [ARCHIVE] + sorted(ARTICLES_DIR.glob("strana-*.html"), key=lambda p: int(re.search(r"\d+", p.stem).group()))
    return [p.read_text(encoding="utf-8", errors="replace") for p in pages if p.exists()]


def audit_repo(articles: list[dict]) -> None:
    home = HOME.read_text(encoding="utf-8", errors="replace")
    sitemap = SITEMAP.read_text(encoding="utf-8", errors="replace")
    archives = archive_texts()
    joined_archive = "\n".join(archives)

    expected_home = {item["href"] for item in articles[: min(HOME_TOTAL, len(articles))]}
    missing_home = sorted(href for href in expected_home if href not in home)
    if missing_home:
        raise RuntimeError(f"Na titulce chybějí nejnovější články: {missing_home}")

    archive_missing: list[str] = []
    archive_duplicates: list[str] = []
    sitemap_missing: list[str] = []
    for item in articles:
        count = joined_archive.count(f'href="{item["href"]}"')
        if count == 0:
            archive_missing.append(item["href"])
        elif count > 1:
            archive_duplicates.append(item["href"])
        if item["url"] not in sitemap:
            sitemap_missing.append(item["url"])
    if archive_missing:
        raise RuntimeError(f"V archivu chybějí články: {archive_missing}")
    if archive_duplicates:
        raise RuntimeError(f"Archiv obsahuje duplicitní články: {archive_duplicates}")
    if sitemap_missing:
        raise RuntimeError(f"V sitemapě chybějí články: {sitemap_missing}")


def fetch(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": "NaseKadan-Article-Visibility-Guard/1.0"})
    try:
        with urlopen(request, timeout=35) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, ""
    except URLError as exc:
        raise RuntimeError(f"Nelze načíst {url}: {exc}") from exc


def audit_live(articles: list[dict], base: str) -> None:
    stamp = int(datetime.now(timezone.utc).timestamp())
    home_code, home = fetch(f"{base}/?visibility_guard={stamp}")
    archive_code, archive = fetch(f"{base}/clanky/?visibility_guard={stamp}")
    sitemap_code, sitemap = fetch(f"{base}/sitemap.xml?visibility_guard={stamp}")
    if (home_code, archive_code, sitemap_code) != (200, 200, 200):
        raise RuntimeError(f"Veřejné plochy nemají HTTP 200: domů={home_code}, archiv={archive_code}, sitemap={sitemap_code}")

    expected_home = articles[: min(HOME_TOTAL, len(articles))]
    missing_home = [item["href"] for item in expected_home if item["href"] not in home]
    if missing_home:
        raise RuntimeError(f"Na živé titulce chybějí nejnovější články: {missing_home}")

    for item in articles:
        if item["url"] not in sitemap:
            raise RuntimeError(f"Živá sitemap neobsahuje {item['url']}")
        code, page = fetch(f"{item['url']}?visibility_guard={stamp}")
        if code != 200 or f"<h1>{item['title']}</h1>" not in page or "noindex" in page.lower():
            raise RuntimeError(f"Veřejný článek není bezpečně dostupný: {item['url']} (HTTP {code})")


def normalize_generated_whitespace() -> None:
    paths = [HOME, ARCHIVE] + sorted(ARTICLES_DIR.glob("strana-*.html"))
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
        path.write_text(normalized, encoding="utf-8", newline="\n")


def run_generator() -> None:
    subprocess.run([sys.executable, "scripts/enforce_article_visibility.py"], cwd=ROOT, check=True)
    normalize_generated_whitespace()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--live-base")
    args = parser.parse_args()

    previous = load_manifest()
    restored = restore_missing_from_git(previous) if args.repair else []
    if args.repair:
        run_generator()
    articles = published_articles()
    write_manifest(articles, previous, restored)
    audit_repo(articles)
    if args.live_base:
        audit_live(articles, args.live_base.rstrip("/"))
    print(f"OK: {len(articles)} publikovaných článků; obnovené soubory: {len(restored)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
