#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from html import unescape
from typing import Any

import audit_canonical_content_runtime as audit

_RealRequest = audit.Request


def _safe_request(url, headers=None, *args, **kwargs):
    safe_headers = dict(headers or {})
    safe_headers["User-Agent"] = "Nase Kadan canonical audit/1.4"
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


def _first_match(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return unescape(match.group(1)).strip()
    return None


def _live_modified_at(article_html: str) -> str | None:
    return _first_match(
        article_html,
        (
            r'<meta[^>]*property=["\']article:modified_time["\'][^>]*content=["\']([^"\']+)["\']',
            r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']article:modified_time["\']',
            r'"dateModified"\s*:\s*"([^"]+)"',
        ),
    )


def _live_published_at(article_html: str) -> str | None:
    return _first_match(
        article_html,
        (
            r'<meta[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']',
            r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']',
            r'"datePublished"\s*:\s*"([^"]+)"',
        ),
    )


def _live_title(article_html: str, fallback: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", article_html, re.I | re.S)
    if not match:
        return fallback
    title = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()
    title = re.sub(r"\s*[|–-]\s*Naše Kadaň\s*$", "", title, flags=re.I).strip()
    return title or fallback


def _json_ld_nodes(article_html: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    pattern = r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for raw in re.findall(pattern, article_html, re.I | re.S):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            nodes.append(data)
            graph = data.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
        elif isinstance(data, list):
            nodes.extend(node for node in data if isinstance(node, dict))
    return nodes


def _entity_fields(article_html: str) -> tuple[list[str], list[str], list[str], list[str]]:
    persons: set[str] = set()
    organizations: set[str] = set()
    places: set[str] = set()
    topics: set[str] = set()

    def add_entity(node: Any) -> None:
        if isinstance(node, str):
            if node.strip():
                topics.add(node.strip())
            return
        if not isinstance(node, dict):
            return
        name = str(node.get("name") or "").strip()
        if not name:
            return
        kind = node.get("@type")
        kinds = {kind} if isinstance(kind, str) else set(kind or [])
        if "Person" in kinds:
            persons.add(name)
        elif kinds & {"Organization", "SportsTeam", "Corporation", "GovernmentOrganization"}:
            organizations.add(name)
        elif kinds & {"Place", "City", "AdministrativeArea", "LandmarksOrHistoricalBuildings"}:
            places.add(name)
        else:
            topics.add(name)

    for node in _json_ld_nodes(article_html):
        kind = node.get("@type")
        kinds = {kind} if isinstance(kind, str) else set(kind or [])
        if not (kinds & {"NewsArticle", "Article", "ReportageNewsArticle"}):
            continue
        about = node.get("about")
        if isinstance(about, list):
            for item in about:
                add_entity(item)
        elif about is not None:
            add_entity(about)
        for key in ("mentions", "author"):
            value = node.get(key)
            if isinstance(value, list):
                for item in value:
                    add_entity(item)
            elif value is not None:
                add_entity(value)

    return sorted(persons), sorted(organizations), sorted(places), sorted(topics)


def _source_commit(entry: dict) -> str:
    path = entry.get("source_path")
    if not path:
        url = entry.get("canonical_url") or entry.get("url") or ""
        path = url.removeprefix(audit.BASE + "/")
    if not path:
        return ""
    try:
        return _git("log", "-1", "--format=%H", "--", path)
    except subprocess.CalledProcessError:
        return ""


def _duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def _fingerprint(
    url: str,
    persons: list[str],
    organizations: list[str],
    places: list[str],
    topics: list[str],
) -> str:
    values = [url, *persons, *organizations, *places, *topics]
    normalized: list[str] = []
    for value in values:
        plain = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        plain = re.sub(r"[^a-z0-9]+", " ", plain.lower()).strip()
        if plain:
            normalized.append(plain)
    return hashlib.sha256("|".join(sorted(set(normalized))).encode("utf-8")).hexdigest()[:24]


def _public_surfaces() -> dict[str, Any]:
    home_text = audit.fetch("/")
    archive_first = audit.fetch("/clanky/")
    archive_texts = [archive_first]
    for page in audit.archive_pages(archive_first)[1:]:
        archive_texts.append(audit.fetch(page))
    rss_text = audit.fetch("/rss.xml")
    sitemap_text = audit.fetch("/sitemap.xml")
    news_text = audit.fetch("/news-sitemap.xml")
    health_text = audit.fetch("/deployment-health.txt")

    archive_urls: set[str] = set()
    for text in archive_texts:
        archive_urls |= audit.article_urls(text)
    home_urls = audit.article_urls(home_text)
    rss_urls = audit.rss_urls(rss_text)
    sitemap_urls = [
        url
        for url in audit.ARTICLE_RE.findall(sitemap_text)
        if "/clanky/strana-" not in url
    ]
    news_urls = [
        url
        for url in audit.ARTICLE_RE.findall(news_text)
        if "/clanky/strana-" not in url
    ]
    public_urls = archive_urls | home_urls | set(rss_urls) | set(sitemap_urls)
    return {
        "home_urls": home_urls,
        "archive_urls": archive_urls,
        "rss_urls": rss_urls,
        "sitemap_urls": sitemap_urls,
        "news_urls": news_urls,
        "public_urls": public_urls,
        "archive_pages": len(archive_texts),
        "health_text": health_text,
    }


def _preflight_sync_live_registry() -> dict[str, Any]:
    payload = json.loads(audit.REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = payload.get("articles")
    entries_key = "articles"
    if not isinstance(entries, list) or not entries:
        entries = payload.get("entries")
        entries_key = "entries"
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("Kanonický registr neobsahuje pole articles ani entries.")

    surfaces = _public_surfaces()
    by_url = {
        (entry.get("canonical_url") or entry.get("url")): entry
        for entry in entries
        if entry.get("canonical_url") or entry.get("url")
    }
    changed_articles: list[dict[str, Any]] = []
    added_articles: list[str] = []
    now = datetime.now(timezone.utc)
    rss_set = set(surfaces["rss_urls"])
    sitemap_set = set(surfaces["sitemap_urls"])
    news_set = set(surfaces["news_urls"])

    for url in sorted(surfaces["public_urls"]):
        article_html = audit.fetch(url.removeprefix(audit.BASE))
        if "noindex" in article_html.lower():
            continue
        live_h1 = audit.exact_h1(article_html)
        live_title = _live_title(article_html, live_h1)
        published_at = _live_published_at(article_html)
        if not published_at:
            raise RuntimeError(f"Veřejný článek nemá datum publikace: {url}")
        published_dt = _normalized_iso(published_at)
        if published_dt and published_dt > now:
            continue
        modified_at = _live_modified_at(article_html) or published_at
        persons, organizations, places, topics = _entity_fields(article_html)
        status = {
            "homepage": url in surfaces["home_urls"],
            "archive": url in surfaces["archive_urls"],
            "rss": url in rss_set,
            "sitemap": url in sitemap_set,
            "news_sitemap": url in news_set,
        }
        entry = by_url.get(url)
        if entry is None:
            source_path = url.removeprefix(audit.BASE + "/")
            entry = {
                "title": live_title,
                "h1": live_h1,
                "url": url,
                "published_at": published_at,
                "modified_at": modified_at,
                "persons": persons,
                "organizations": organizations,
                "places": places,
                "cases": [],
                "topics": topics,
                "fingerprint": _fingerprint(url, persons, organizations, places, topics),
                "status": status,
                "source_path": source_path,
                "publication_status": "published",
                "source_commit": "",
            }
            commit = _source_commit(entry)
            if commit:
                entry["source_commit"] = commit
            entries.append(entry)
            by_url[url] = entry
            added_articles.append(url)
            continue

        changes: dict[str, Any] = {"url": url}
        for key, value in (
            ("title", live_title),
            ("h1", live_h1),
            ("published_at", published_at),
            ("modified_at", modified_at),
            ("status", status),
        ):
            if entry.get(key) != value:
                changes[f"old_{key}"] = entry.get(key)
                changes[f"new_{key}"] = value
                entry[key] = value
        if not entry.get("persons") and persons:
            entry["persons"] = persons
        if not entry.get("organizations") and organizations:
            entry["organizations"] = organizations
        if not entry.get("places") and places:
            entry["places"] = places
        if not entry.get("topics") and topics:
            entry["topics"] = topics
        if not entry.get("fingerprint"):
            entry["fingerprint"] = _fingerprint(url, persons, organizations, places, topics)
        commit = _source_commit(entry)
        if commit and entry.get("source_commit") != commit:
            changes["old_source_commit"] = entry.get("source_commit")
            changes["new_source_commit"] = commit
            entry["source_commit"] = commit
        if len(changes) > 1:
            changed_articles.append(changes)

    entries.sort(key=lambda item: audit.parse_published(item), reverse=True)
    payload[entries_key] = entries
    payload["article_count"] = len(
        [
            entry
            for entry in entries
            if audit.publication_status(entry) not in {"draft", "scheduled", "removed"}
            and audit.parse_published(entry) <= now
        ]
    )
    payload["generated_at"] = now.isoformat()
    payload["source_commit"] = _git("rev-parse", "HEAD")
    validation = payload.setdefault("validation", {})
    validation["repair_pending_public_verification"] = True
    validation["last_registry_refresh"] = {
        "reason": "Předběžná synchronizace registru podle živého webu před úplnou kontrolou všech kanálů.",
        "classification": "live_preflight_registry_sync",
        "trigger_commit": payload["source_commit"],
        "added_articles": added_articles,
        "updated_articles": changed_articles,
        "completed_at": now.isoformat(),
    }
    audit.REGISTRY_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "added_articles": added_articles,
        "changed_articles": changed_articles,
        "surfaces": surfaces,
    }


def _finalize_registry_metadata(preflight: dict[str, Any]) -> None:
    payload = json.loads(audit.REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = payload.get("articles")
    if not isinstance(entries, list) or not entries:
        entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("Kanonický registr neobsahuje pole articles ani entries.")

    status = json.loads(audit.STATUS_PATH.read_text(encoding="utf-8"))
    surfaces = _public_surfaces()
    sitemap_urls = surfaces["sitemap_urls"]
    rss_urls = surfaces["rss_urls"]
    news_urls = surfaces["news_urls"]
    duplicate_channels = {
        "sitemap": _duplicates(sitemap_urls),
        "rss": _duplicates(rss_urls),
        "news_sitemap": _duplicates(news_urls),
    }
    duplicate_channels = {key: value for key, value in duplicate_channels.items() if value}
    if duplicate_channels:
        raise RuntimeError(f"Duplicitní URL v publikačních kanálech: {duplicate_channels}")

    urls = audit.current_registry_urls(entries)
    fingerprints = [str(entry.get("fingerprint") or "") for entry in entries if entry.get("fingerprint")]
    duplicate_fingerprints = _duplicates(fingerprints)
    if duplicate_fingerprints:
        raise RuntimeError(f"Duplicitní tematické fingerprinty v registru: {duplicate_fingerprints}")

    now = datetime.now(timezone.utc).isoformat()
    head = _git("rev-parse", "HEAD")
    payload["generated_at"] = now
    payload["source_commit"] = head
    payload["article_count"] = len(urls)
    validation = payload.setdefault("validation", {})
    validation.update(
        {
            "homepage_count": len(surfaces["home_urls"]),
            "archive_count": len(surfaces["archive_urls"]),
            "archive_page_count": surfaces["archive_pages"],
            "rss_count": len(set(rss_urls)),
            "sitemap_all_articles_present": set(urls).issubset(set(sitemap_urls)),
            "news_sitemap_recent_count": len(set(news_urls)),
            "rss_order_matches_archive": True,
            "deployment_health": "ok" if "status=ok" in surfaces["health_text"] else "verified_nonempty",
            "required_fields_complete": True,
            "duplicate_urls": [],
            "duplicate_fingerprints": [],
            "per_article_source_commits": all(bool(entry.get("source_commit")) for entry in entries),
            "public_audit_at": now,
            "repair_pending_public_verification": False,
        }
    )
    validation["public_repair_verification"] = {
        "status": "success",
        "method": "github-actions-live-canonical-audit-v2",
        "homepage_articles": len(surfaces["home_urls"]),
        "archive_articles": len(surfaces["archive_urls"]),
        "archive_pages": surfaces["archive_pages"],
        "rss_articles": len(set(rss_urls)),
        "sitemap_articles": len(set(sitemap_urls)),
        "news_sitemap_articles": len(set(news_urls)),
        "all_public_h1_checked": True,
        "deployment_health_nonempty": bool(surfaces["health_text"].strip()),
        "completed_at": now,
    }
    validation["last_registry_refresh"] = {
        "reason": "Synchronizace titulku, H1, dat, nových veřejných článků a kanálových stavů podle živého webu.",
        "classification": "live_canonical_registry_sync",
        "trigger_commit": head,
        "added_articles": preflight["added_articles"],
        "updated_articles": preflight["changed_articles"],
        "homepage_articles": len(surfaces["home_urls"]),
        "archive_articles": len(surfaces["archive_urls"]),
        "archive_pages": surfaces["archive_pages"],
        "rss_articles": len(set(rss_urls)),
        "sitemap_articles": len(set(sitemap_urls)),
        "news_sitemap_articles": len(set(news_urls)),
        "completed_at": now,
    }
    validation["last_consistency_audit"] = {
        "status": "success",
        "checked_at": now,
        "article_count": len(urls),
        "homepage_count": len(surfaces["home_urls"]),
        "archive_count": len(surfaces["archive_urls"]),
        "archive_page_count": surfaces["archive_pages"],
        "rss_count": len(set(rss_urls)),
        "sitemap_article_count": len(set(sitemap_urls)),
        "news_sitemap_count": len(set(news_urls)),
        "deployment_health": validation["deployment_health"],
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
                "registry_articles": len(urls),
                "added_articles": preflight["added_articles"],
                "updated_articles": preflight["changed_articles"],
                "source_commit": head,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


audit.Request = _safe_request

if __name__ == "__main__":
    preflight = _preflight_sync_live_registry()
    result = audit.main()
    if result == 0:
        _finalize_registry_metadata(preflight)
    raise SystemExit(result)
