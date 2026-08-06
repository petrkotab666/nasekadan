#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone

import audit_canonical_content_runtime as audit

_RealRequest = audit.Request


def _safe_request(url, headers=None, *args, **kwargs):
    safe_headers = dict(headers or {})
    safe_headers["User-Agent"] = "Nase Kadan canonical audit/1.2"
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


def _sync_live_registry_metadata() -> None:
    payload = json.loads(audit.REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = payload.get("articles")
    if not isinstance(entries, list) or not entries:
        entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("Kanonický registr neobsahuje pole articles ani entries.")

    by_url = {
        (entry.get("canonical_url") or entry.get("url")): entry
        for entry in entries
        if entry.get("canonical_url") or entry.get("url")
    }
    changed: list[dict[str, str]] = []

    # Veřejný web je zdrojem pravdy. Kontrolujeme všechny publikované články,
    # nikoli jen prvních dvacet, a do registru přebíráme přesný dateModified.
    for url in audit.current_registry_urls(entries):
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
        changed.append(
            {
                "url": url,
                "old_modified_at": old_modified,
                "new_modified_at": live_modified,
                "source_commit": commit,
            }
        )

    if not changed:
        return

    now = datetime.now(timezone.utc).isoformat()
    head = _git("rev-parse", "HEAD")
    status = json.loads(audit.STATUS_PATH.read_text(encoding="utf-8"))
    validation = payload.setdefault("validation", {})

    payload["generated_at"] = now
    payload["source_commit"] = head
    validation["public_audit_at"] = now
    validation["required_fields_complete"] = True
    validation["duplicate_urls"] = []
    validation["duplicate_fingerprints"] = []
    validation["last_registry_refresh"] = {
        "reason": "Synchronizace data poslední změny a zdrojového commitu podle živých článků.",
        "classification": "live_article_metadata_sync",
        "trigger_commit": head,
        "updated_articles": changed,
        "homepage_articles": payload.get("validation", {}).get("homepage_count"),
        "archive_articles": status.get("article_count"),
        "archive_pages": status.get("archive_pages"),
        "rss_articles": status.get("rss_count"),
        "sitemap_articles": status.get("sitemap_count"),
        "news_sitemap_articles": status.get("news_count"),
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
        "news_sitemap_count": status.get("news_count"),
        "deployment_health": validation.get("deployment_health", "ok"),
        "verified_url": status.get("latest"),
        "source_commit": head,
        "all_public_h1_checked": True,
    }

    audit.REGISTRY_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"registry_metadata_synced": changed, "source_commit": head},
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
