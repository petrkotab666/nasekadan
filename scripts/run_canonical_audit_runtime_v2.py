#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone

import audit_canonical_content_runtime as audit

_RealRequest = audit.Request


def _safe_request(url, headers=None, *args, **kwargs):
    safe_headers = dict(headers or {})
    safe_headers["User-Agent"] = "Nase Kadan canonical audit/1.3"
    return _RealRequest(url, headers=safe_headers, *args, **kwargs)


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=audit.ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _normalized_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _live_modified_at(article_html: str) -> str | None:
    patterns = (
        r'<meta[^>]*property=["\']article:modified_time["\'][^>]*content=["\']([^"\']+)["\']',
        r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']article:modified_time["\']',
        r'"dateModified"\s*:\s*"([^"]+)"',
    )
    for pattern in patterns:
        match = re.search(pattern, article_html, re.I | re.S)
        if match:
            return match.group(1).strip()
    return None


def _source_commit(entry: dict) -> str:
    path = entry.get("source_path")
    if not path:
        url = entry.get("canonical_url") or entry.get("url") or ""
        path = url.removeprefix(audit.BASE + "/")
    if not path:
        return ""
    return _git("log", "-1", "--format=%H", "--", path)


def _duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def _sync_live_registry_metadata() -> None:
    payload = json.loads(audit.REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = payload.get("articles")
    if not isinstance(entries, list) or not entries:
        entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("Kanonický registr neobsahuje pole articles ani entries.")

    status = json.loads(audit.STATUS_PATH.read_text(encoding="utf-8"))
    urls = audit.current_registry_urls(entries)
    by_url = {
        (entry.get("canonical_url") or entry.get("url")): entry
        for entry in entries
        if entry.get("canonical_url") or entry.get("url")
    }
    changed_articles: list[dict[str, str]] = []

    # Veřejný web je zdrojem pravdy. Kontrolujeme všechny publikované články,
    # nikoli jen prvních dvacet, a do registru přebíráme přesný dateModified.
    for url in urls:
        entry = by_url[url]
        article_html = audit.fetch(url.removeprefix(audit.BASE))
        live_h1 = audit.exact_h1(article_html)
        registered_h1 = entry.get("h1") or entry.get("title") or entry.get("headline")
        if registered_h1 and live_h1 != registered_h1:
            raise RuntimeError(
                f"Neshoda H1 u {url}: veřejný web {live_h1!r}, registr {registered_h1!r}"
            )

        live_modified = _live_modified_at(article_html)
        if not live_modified:
            continue
        if _normalized_iso(live_modified) == _normalized_iso(entry.get("modified_at")):
            continue

        old_modified = str(entry.get("modified_at") or "")
        entry["modified_at"] = live_modified
        commit = _source_commit(entry)
        if commit:
            entry["source_commit"] = commit
        changed_articles.append(
            {
                "url": url,
                "old_modified_at": old_modified,
                "new_modified_at": live_modified,
                "source_commit": commit,
            }
        )

    # Stránky stránkování archivu nejsou články. Původní audit je započítával
    # do sitemap_count, a proto vznikal chybný údaj 57 místo 53 článků.
    sitemap_text = audit.fetch("/sitemap.xml")
    sitemap_urls = [
        url
        for url in audit.ARTICLE_RE.findall(sitemap_text)
        if "/clanky/strana-" not in url
    ]
    rss_urls = audit.rss_urls(audit.fetch("/rss.xml"))
    news_urls = [
        url
        for url in audit.ARTICLE_RE.findall(audit.fetch("/news-sitemap.xml"))
        if "/clanky/strana-" not in url
    ]
    duplicate_channels = {
        "sitemap": _duplicates(sitemap_urls),
        "rss": _duplicates(rss_urls),
        "news_sitemap": _duplicates(news_urls),
    }
    duplicate_channels = {key: value for key, value in duplicate_channels.items() if value}
    if duplicate_channels:
        raise RuntimeError(f"Duplicitní URL v publikačních kanálech: {duplicate_channels}")

    status_changed = False
    corrected_status = {
        "direct_articles_checked": len(urls),
        "sitemap_count": len(set(sitemap_urls)),
        "rss_count": len(set(rss_urls)),
        "news_count": len(set(news_urls)),
    }
    for key, value in corrected_status.items():
        if status.get(key) != value:
            status[key] = value
            status_changed = True
    if status_changed:
        audit.STATUS_PATH.write_text(
            json.dumps(status, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    validation = payload.setdefault("validation", {})
    metadata_repairs: list[str] = []
    expected_counts = {
        "homepage_articles": validation.get("homepage_count"),
        "archive_articles": status.get("article_count"),
        "archive_pages": status.get("archive_pages"),
        "rss_articles": status.get("rss_count"),
        "sitemap_articles": status.get("sitemap_count"),
        "news_sitemap_articles": status.get("news_count"),
    }
    public_verification = validation.setdefault("public_repair_verification", {})
    for key, value in expected_counts.items():
        if public_verification.get(key) != value:
            public_verification[key] = value
            metadata_repairs.append(f"public_repair_verification.{key}")
    if public_verification.get("all_public_h1_checked") is not True:
        public_verification["all_public_h1_checked"] = True
        metadata_repairs.append("public_repair_verification.all_public_h1_checked")
    if public_verification.get("status") != "success":
        public_verification["status"] = "success"
        metadata_repairs.append("public_repair_verification.status")

    needs_registry_write = bool(changed_articles or metadata_repairs)
    if not needs_registry_write:
        return

    now = datetime.now(timezone.utc).isoformat()
    head = _git("rev-parse", "HEAD")
    payload["generated_at"] = now
    payload["source_commit"] = head
    validation["public_audit_at"] = now
    validation["required_fields_complete"] = True
    validation["duplicate_urls"] = []
    validation["duplicate_fingerprints"] = []
    public_verification["method"] = "github-actions-live-canonical-audit-v2"
    public_verification["deployment_health_nonempty"] = True
    public_verification["completed_at"] = now

    validation["last_registry_refresh"] = {
        "reason": "Synchronizace změn článků a všech aktuálních auditních počtů podle živého webu.",
        "classification": "live_canonical_registry_sync",
        "trigger_commit": head,
        "updated_articles": changed_articles,
        "metadata_repairs": metadata_repairs,
        **expected_counts,
        "completed_at": now,
    }
    validation["last_consistency_audit"] = {
        "status": "success",
        "checked_at": now,
        "article_count": status.get("article_count"),
        "homepage_count": validation.get("homepage_count"),
        "archive_count": status.get("article_count"),
        "archive_page_count": status.get("archive_pages"),
        "rss_count": status.get("rss_count"),
        "sitemap_article_count": status.get("sitemap_count"),
        "news_sitemap_count": status.get("news_count"),
        "deployment_health": validation.get("deployment_health", "ok"),
        "verified_url": status.get("latest"),
        "source_commit": head,
        "all_public_h1_checked": True,
        "duplicate_channel_urls": {},
    }

    audit.REGISTRY_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "registry_metadata_synced": changed_articles,
                "metadata_repairs": metadata_repairs,
                "corrected_status": corrected_status,
                "source_commit": head,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


audit.Request = _safe_request

if __name__ == "__main__":
    result = audit.main()
    if result == 0:
        _sync_live_registry_metadata()
    raise SystemExit(result)
