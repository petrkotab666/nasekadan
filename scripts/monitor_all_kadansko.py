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

from monitor_national_kadan import collect, fold, normalize_url, parse_datetime, read_json, write_json
from update_city_news import load_sources

MAX_WORKERS = 12
MAX_SEEN = 12000
MAX_ALERTS_PER_RUN = 80
GENERIC_TITLES = {
    "číst více", "více", "detail", "aktuality", "novinky", "program", "kalendář akcí",
    "úvod", "hlavní stránka", "domů", "kontakt", "kontakty", "menu", "facebook", "instagram",
}


def title_quality(title: object) -> int:
    raw = str(title or "").strip()
    folded = fold(raw)
    if not folded or folded in GENERIC_TITLES:
        return -1000
    if len(raw) < 8 or len(raw) > 260:
        return -500
    score = min(len(raw), 120)
    if any(token in folded for token in ("číst více", "zobrazit více", "pokračovat", "menu")):
        score -= 200
    if len(raw.split()) >= 4:
        score += 20
    return score


def source_priority(source: dict[str, Any]) -> int:
    tier = str(source.get("tier") or "")
    return {
        "municipality": 100,
        "organization": 90,
        "directory": 85,
        "emergency": 100,
        "police": 100,
        "regional_authority": 90,
        "regional_media": 70,
        "aggregator": 30,
    }.get(tier, 60)


def severity_for(category: object, tier: object, title: object) -> str:
    text = fold(f"{category} {tier} {title}")
    urgent_terms = (
        "požár", "nehoda", "havárie", "policie", "hasiči", "záchranná", "nemocnice",
        "uzavírka", "výpadek", "odstávka", "voda", "elektřina", "teplo", "krizové",
        "úřední deska", "rozhodnutí", "zastupitelstvo", "rada města", "školy", "školka",
    )
    if any(term in text for term in urgent_terms):
        return "high"
    return "medium"


def fingerprint(item: dict[str, Any]) -> str:
    url = normalize_url(item.get("url"))
    title = fold(item.get("title"))
    identity = url or f"{item.get('sourceName')}|{title}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]


def load_all_sources(extra_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_sources, coverage = load_sources()
    extra = read_json(extra_path)
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()

    for source in base_sources:
        url = normalize_url(source.get("url"))
        if not url or url in seen:
            continue
        seen.add(url)
        merged.append({
            **source,
            "kind": "html",
            "tier": "organization",
        })

    for source in extra.get("sources", []):
        if not isinstance(source, dict):
            continue
        url = normalize_url(source.get("url"))
        if not url or url in seen:
            continue
        seen.add(url)
        merged.append(dict(source))

    coverage = {
        **coverage,
        "extraSources": max(0, len(merged) - int(coverage.get("totalUniqueSources") or 0)),
        "completeSourceCount": len(merged),
        "scopeMunicipalities": (extra.get("scope") or {}).get("municipalities", []),
    }
    return merged, coverage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra-config", default="data/kadansko-extra-sources.json")
    parser.add_argument("--state", default="data/all-kadansko-monitoring-state.json")
    parser.add_argument("--status", default="data/all-kadansko-monitoring-status.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    state_path = Path(args.state)
    status_path = Path(args.status)
    output_path = Path(args.output)
    sources, coverage = load_all_sources(Path(args.extra_config))
    if len(sources) < 90:
        raise SystemExit(f"Úplný monitoring obsahuje jen {len(sources)} zdrojů; očekáváno nejméně 90.")

    state = read_json(state_path)
    seen = state.get("seen") if isinstance(state.get("seen"), dict) else {}
    bootstrap = not bool(seen)
    now = datetime.now(timezone.utc)

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(sources))) as executor:
        collected = list(executor.map(collect, sources))

    source_status: list[dict[str, Any]] = []
    parsed_total = 0
    by_url: dict[str, dict[str, Any]] = {}

    for source, items, error in collected:
        parsed_total += len(items)
        source_status.append({
            "name": source.get("name"),
            "url": source.get("url"),
            "category": source.get("category"),
            "tier": source.get("tier"),
            "status": "failed" if error else "checked",
            "itemsParsed": len(items),
            **({"error": error} if error else {}),
        })
        for item in items:
            title = str(item.get("title") or "").strip()
            quality = title_quality(title)
            if quality < 0:
                continue
            url = normalize_url(item.get("url"))
            if not url:
                continue
            candidate = dict(item)
            candidate.update({
                "title": title,
                "url": url,
                "sourceName": source.get("name"),
                "sourceUrl": source.get("url"),
                "category": source.get("category"),
                "tier": source.get("tier"),
                "severity": severity_for(source.get("category"), source.get("tier"), title),
                "quality": quality,
                "sourcePriority": source_priority(source),
            })
            previous = by_url.get(url)
            if not previous or (
                candidate["sourcePriority"], candidate["quality"], len(str(candidate.get("description") or ""))
            ) > (
                previous["sourcePriority"], previous["quality"], len(str(previous.get("description") or ""))
            ):
                by_url[url] = candidate

    candidates = sorted(
        by_url.values(),
        key=lambda item: (str(item.get("published") or ""), int(item.get("sourcePriority") or 0), str(item.get("title") or "")),
        reverse=True,
    )

    alerts: list[dict[str, Any]] = []
    for item in candidates:
        fp = fingerprint(item)
        item["fingerprint"] = fp
        is_new = fp not in seen
        published = parse_datetime(item.get("published"))
        should_alert = is_new and not bootstrap
        # Při prvním nasazení nezahlcujeme historii. Upozorníme pouze na položky
        # s prokazatelným datem z posledních dvou hodin.
        if is_new and bootstrap and published and published >= now - timedelta(hours=2):
            should_alert = True
        if should_alert and len(alerts) < MAX_ALERTS_PER_RUN:
            alerts.append(item)
        previous = seen.get(fp) if isinstance(seen.get(fp), dict) else {}
        seen[fp] = {
            "title": item.get("title"),
            "url": item.get("url"),
            "sourceName": item.get("sourceName"),
            "category": item.get("category"),
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
        "uniqueItems": len(candidates),
        "newAlerts": len(alerts),
        "alertsCapped": len(alerts) >= MAX_ALERTS_PER_RUN,
        "coverage": coverage,
        "sourceStatus": source_status,
    }
    write_json(state_path, {"version": 1, "lastRunAt": now.isoformat(), "seen": seen})
    write_json(status_path, status)
    write_json(output_path, {"alerts": alerts, "status": status})
    print(json.dumps({
        "ok": True,
        "sources": f"{status['checkedSources']}/{status['sourceCount']}",
        "parsed": parsed_total,
        "unique": len(candidates),
        "alerts": len(alerts),
        "bootstrap": bootstrap,
        "organizations": coverage.get("monitoredDirectoryOrganizations"),
        "municipalities": len(coverage.get("scopeMunicipalities") or []),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
