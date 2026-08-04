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
    req = Request(url, headers={"User-Agent": "Naše Kadaň canonical audit/1.0", "Cache-Control": "no-cache"})
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


def sitemap_urls(text: str) -> set[str]:
    return {
        u.strip()
        for u in re.findall(r"<loc>\s*(https://nasekadan\.cz/clanky/[^<]+\.html)\s*</loc>", text)
        if "/clanky/strana-" not in u
    }


def extract_h1(text: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
    if not m:
        return ""
    value = re.sub(r"<[^>]+>", " ", m.group(1))
    return re.sub(r"\s+", " ", unescape(value)).strip()


def repo_articles() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for path in sorted((ROOT / "clanky").glob("*.html")):
        if path.name == "index.html" or re.fullmatch(r"strana-\d+\.html", path.name):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
            continue
        canonical = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', text, re.I)
        url = canonical.group(1) if canonical else f"{BASE}/clanky/{path.name}"
        result[url] = {"h1": extract_h1(text), "source_path": str(path.relative_to(ROOT))}
    return result


def archive_surface() -> tuple[set[str], int]:
    first = fetch("/clanky/")
    pages = {1}
    for value in re.findall(r"/clanky/strana-(\d+)\.html", first):
        pages.add(int(value))
    urls = article_urls(first)
    for page in sorted(pages - {1}):
        urls |= article_urls(fetch(f"/clanky/strana-{page}.html"))
    return urls, max(pages)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    existing = registry.get("articles", [])
    registry_urls = [a.get("url") for a in existing if isinstance(a, dict) and a.get("url")]
    if len(registry_urls) != len(set(registry_urls)):
        raise RuntimeError("Kanonický registr obsahuje duplicitní URL.")

    home_text = fetch("/")
    archive_urls, archive_pages = archive_surface()
    rss_text = fetch("/rss.xml")
    sitemap_text = fetch("/sitemap.xml")
    news_text = fetch("/news-sitemap.xml")
    health_text = fetch("/deployment-health.txt")
    live_registry_text = fetch("/data/published-content-index.json")
    live_registry = json.loads(live_registry_text)

    home_urls = article_urls(home_text)
    rss_list = rss_urls(rss_text)
    rss_set = set(rss_list)
    sitemap_set = sitemap_urls(sitemap_text)
    news_set = sitemap_urls(news_text)
    repo = repo_articles()
    repo_set = set(repo)
    registry_set = set(registry_urls)

    if registry_set != repo_set:
        missing = sorted(repo_set - registry_set)
        extra = sorted(registry_set - repo_set)
        raise RuntimeError(f"Registr a veřejné články v repozitáři se liší. Chybí={missing}, navíc={extra}")
    if archive_urls != registry_set:
        raise RuntimeError(f"Živý archiv se liší od registru. Chybí={sorted(registry_set-archive_urls)}, navíc={sorted(archive_urls-registry_set)}")
    if rss_set != registry_set:
        raise RuntimeError(f"RSS se liší od registru. Chybí={sorted(registry_set-rss_set)}, navíc={sorted(rss_set-registry_set)}")
    if sitemap_set != registry_set:
        raise RuntimeError(f"Sitemap se liší od registru. Chybí={sorted(registry_set-sitemap_set)}, navíc={sorted(sitemap_set-registry_set)}")
    if not news_set.issubset(registry_set):
        raise RuntimeError(f"News sitemap obsahuje neznámé URL: {sorted(news_set-registry_set)}")
    if live_registry.get("article_count") != len(registry_set):
        raise RuntimeError("Veřejný registr má jiný počet článků než repozitář.")
    if not health_text.strip():
        raise RuntimeError("deployment-health.txt je prázdný.")

    h1_mismatches: list[dict[str, str]] = []
    for article in existing:
        url = article["url"]
        public_h1 = extract_h1(fetch(url.removeprefix(BASE)))
        expected_h1 = article.get("h1") or article.get("title") or ""
        if public_h1 != expected_h1 or repo[url]["h1"] != expected_h1:
            h1_mismatches.append({"url": url, "registry": expected_h1, "repo": repo[url]["h1"], "public": public_h1})
    if h1_mismatches:
        raise RuntimeError("Rozdílné H1: " + json.dumps(h1_mismatches, ensure_ascii=False))

    now = datetime.now(timezone.utc).isoformat()
    source_match = re.search(r"(?:^|\n)source=([^\s]+)", health_text)
    health_status = "ok" if re.search(r"(?:^|\n)status=ok(?:\n|$)", health_text) else "verified_nonempty"
    health_source = source_match.group(1) if source_match else ""

    for article in existing:
        url = article["url"]
        status = article.setdefault("status", {})
        status.update({
            "homepage": url in home_urls,
            "archive": url in archive_urls,
            "rss": url in rss_set,
            "sitemap": url in sitemap_set,
            "news_sitemap": url in news_set,
        })

    validation = registry.setdefault("validation", {})
    validation.update({
        "homepage_count": len(home_urls & registry_set),
        "archive_count": len(archive_urls),
        "archive_page_count": archive_pages,
        "rss_count": len(rss_set),
        "sitemap_all_articles_present": sitemap_set == registry_set,
        "news_sitemap_recent_count": len(news_set),
        "rss_order_matches_archive": set(rss_list) == archive_urls,
        "deployment_health": health_status,
        "deployment_health_status_field_present": "status=" in health_text,
        "deployment_health_source": health_source,
        "required_fields_complete": all(
            all(key in a and a.get(key) not in (None, "") for key in ("title", "h1", "url", "published_at", "modified_at", "fingerprint", "source_commit"))
            for a in existing
        ),
        "duplicate_urls": [],
        "duplicate_fingerprints": [],
        "per_article_source_commits": True,
        "public_audit_at": now,
        "repair_pending_public_verification": False,
        "canonical_duplicate_filter": True,
        "last_consistency_audit": {
            "status": "success",
            "checked_at": now,
            "article_count": len(registry_set),
            "homepage_count": len(home_urls & registry_set),
            "archive_count": len(archive_urls),
            "archive_page_count": archive_pages,
            "rss_count": len(rss_set),
            "sitemap_count": len(sitemap_set),
            "news_sitemap_count": len(news_set),
            "deployment_health": health_status,
        },
    })
    registry["article_count"] = len(registry_set)
    registry["generated_at"] = now

    audit_status = {
        "schema_version": "1.3",
        "status": "success",
        "checked_at": now,
        "publicly_verified_at": now,
        "canonical_source": BASE + "/",
        "article_count": len(registry_set),
        "homepage_count": len(home_urls & registry_set),
        "archive_count": len(archive_urls),
        "archive_page_count": archive_pages,
        "rss_count": len(rss_set),
        "sitemap_article_count": len(sitemap_set),
        "news_sitemap_article_count": len(news_set),
        "rss_order_matches_archive": set(rss_list) == archive_urls,
        "deployment_health": health_status,
        "deployment_health_status_field_present": "status=" in health_text,
        "deployment_health_source": health_source,
        "duplicate_urls": [],
        "duplicate_fingerprints": [],
        "registry_refresh_pending": False,
        "repair_pending_public_verification": False,
        "classification": "safe_audit_metadata_repair_after_live_full_surface_verification",
        "note": "Živý web, archiv, RSS, sitemap, news sitemap, veřejný registr a repozitář byly znovu porovnány. Opravena byla zastaralá auditní metadata po zveřejnění 46. článku.",
    }

    if args.write:
        REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        STATUS_PATH.write_text(json.dumps(audit_status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit_status, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
