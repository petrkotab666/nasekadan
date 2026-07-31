#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from monitor_national_kadan import (
    collect,
    fold,
    normalize_url,
    parse_datetime,
    read_json,
    write_json,
)

MAX_SEEN = 3000
GENERIC_TITLES = {
    "cist vice",
    "vice",
    "detail",
    "zobrazit vice",
    "pokracovat",
    "dalsi aktuality",
}
SOURCE_PRIORITY = {
    "emergency": 5,
    "police": 5,
    "regional_authority": 4,
    "regional_media": 3,
    "aggregator": 1,
}


def semantic_fingerprint(title: object) -> str:
    value = str(title or "").strip()
    value = re.sub(
        r"\s+-\s+(?:Chomutovský deník|Ústecký deník|Mostecký deník|e-Chomutovsko\.cz|Chomutovky\.cz)$",
        "",
        value,
        flags=re.I,
    )
    normalized = fold(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:20]


def term_matches(text: str, terms: list[str]) -> list[str]:
    return sorted({term for term in terms if term and term in text})


def title_score(value: object) -> int:
    title = str(value or "").strip()
    normalized = fold(title)
    if normalized in GENERIC_TITLES or len(title) < 8 or len(title) > 220:
        return -10_000
    score = 220 - abs(len(title) - 75)
    if len(title) > 140 and title.endswith((".", "!", "?")):
        score -= 120
    if len(title.split()) < 3:
        score -= 40
    return score


def candidate_quality(item: dict[str, Any]) -> tuple[int, int, int]:
    return (
        SOURCE_PRIORITY.get(str(item.get("tier") or ""), 0),
        title_score(item.get("title")),
        len(str(item.get("description") or "")),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="data/urgent-kadan-sources.json")
    parser.add_argument("--state", default="data/urgent-kadan-monitoring-state.json")
    parser.add_argument("--status", default="data/urgent-kadan-monitoring-status.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = read_json(Path(args.config))
    sources = [item for item in config.get("sources", []) if isinstance(item, dict)]
    if len(sources) < 6:
        raise SystemExit(f"Rychlý monitoring obsahuje jen {len(sources)} zdrojů.")

    local_terms = sorted(
        {fold(term) for term in config.get("localTerms", []) if fold(term)},
        key=len,
        reverse=True,
    )
    incident_terms = sorted(
        {fold(term) for term in config.get("incidentTerms", []) if fold(term)},
        key=len,
        reverse=True,
    )
    if "kadan" not in local_terms or "prunerov" not in local_terms:
        raise SystemExit("Chybí základní místní výrazy Kadaň nebo Prunéřov.")

    now = datetime.now(timezone.utc)
    bootstrap_hours = max(1, int(config.get("bootstrapHours") or 12))
    max_age_hours = max(6, int(config.get("maxAlertAgeHours") or 72))
    state_path = Path(args.state)
    state = read_json(state_path)
    seen = state.get("seen") if isinstance(state.get("seen"), dict) else {}
    bootstrap = not bool(seen)

    with ThreadPoolExecutor(max_workers=min(8, len(sources))) as executor:
        collected = list(executor.map(collect, sources))

    source_status: list[dict[str, Any]] = []
    by_url: dict[str, dict[str, Any]] = {}
    parsed_total = 0

    for source, items, error in collected:
        parsed_total += len(items)
        source_status.append({
            "name": source.get("name"),
            "url": source.get("url"),
            "tier": source.get("tier"),
            "category": source.get("category"),
            "status": "failed" if error else "checked",
            "itemsParsed": len(items),
            **({"error": error} if error else {}),
        })
        for item in items:
            if title_score(item.get("title")) < 0:
                continue
            haystack = fold(" ".join([
                str(item.get("title") or ""),
                str(item.get("description") or ""),
                str(item.get("url") or ""),
            ]))
            matched_local = term_matches(haystack, local_terms)
            if not matched_local:
                continue
            matched_incident = term_matches(haystack, incident_terms)
            if not bool(source.get("alertAllLocal")) and not matched_incident:
                continue

            candidate = dict(item)
            candidate.update({
                "sourceName": source.get("name"),
                "sourceUrl": source.get("url"),
                "tier": source.get("tier"),
                "category": source.get("category"),
                "matchedLocalTerms": matched_local,
                "matchedIncidentTerms": matched_incident,
                "severity": "urgent" if matched_incident or source.get("tier") in {"emergency", "police"} else "high",
            })
            url_key = normalize_url(candidate.get("url")) or f"{source.get('name')}|{fold(candidate.get('title'))}"
            previous = by_url.get(url_key)
            if not previous or candidate_quality(candidate) > candidate_quality(previous):
                by_url[url_key] = candidate

    unique: dict[str, dict[str, Any]] = {}
    for candidate in by_url.values():
        fingerprint = semantic_fingerprint(candidate.get("title"))
        candidate["fingerprint"] = fingerprint
        previous = unique.get(fingerprint)
        if not previous or candidate_quality(candidate) > candidate_quality(previous):
            unique[fingerprint] = candidate

    candidates = sorted(
        unique.values(),
        key=lambda item: (str(item.get("published") or ""), str(item.get("title") or "")),
        reverse=True,
    )

    alerts: list[dict[str, Any]] = []
    stale_suppressed = 0
    for item in candidates:
        fingerprint = str(item["fingerprint"])
        is_new = fingerprint not in seen
        published = parse_datetime(item.get("published"))
        should_alert = is_new and not bootstrap
        if is_new and bootstrap and published and published >= now - timedelta(hours=bootstrap_hours):
            should_alert = True
        if should_alert and published and published < now - timedelta(hours=max_age_hours):
            should_alert = False
            stale_suppressed += 1
        if should_alert:
            alerts.append(item)

        previous = seen.get(fingerprint) if isinstance(seen.get(fingerprint), dict) else {}
        seen[fingerprint] = {
            "title": item.get("title"),
            "url": item.get("url"),
            "sourceName": item.get("sourceName"),
            "firstSeen": previous.get("firstSeen") or now.isoformat(),
            "lastSeen": now.isoformat(),
            "published": item.get("published") or "",
        }

    if len(seen) > MAX_SEEN:
        seen = dict(sorted(
            seen.items(),
            key=lambda pair: str((pair[1] or {}).get("lastSeen") or ""),
            reverse=True,
        )[:MAX_SEEN])

    failed = [item for item in source_status if item.get("status") == "failed"]
    status = {
        "version": 1,
        "checkedAt": now.isoformat(),
        "bootstrap": bootstrap,
        "sourceCount": len(sources),
        "checkedSources": len(sources) - len(failed),
        "failedSources": len(failed),
        "itemsParsed": parsed_total,
        "relevantItems": len(candidates),
        "staleAlertsSuppressed": stale_suppressed,
        "newAlerts": len(alerts),
        "sourceStatus": source_status,
    }
    write_json(state_path, {"version": 1, "lastRunAt": now.isoformat(), "seen": seen})
    write_json(Path(args.status), status)
    write_json(Path(args.output), {"alerts": alerts, "status": status})

    print(json.dumps({
        "ok": True,
        "sources": f"{status['checkedSources']}/{status['sourceCount']}",
        "parsed": parsed_total,
        "relevant": len(candidates),
        "alerts": len(alerts),
        "bootstrap": bootstrap,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
