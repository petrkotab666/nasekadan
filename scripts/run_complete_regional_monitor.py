#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import monitor_all_kadansko as monitor


MANDATORY_REGIONAL_SUPPLEMENTS = {
    "Pětipsy": "https://www.petipsy.cz/",
    "Loučná pod Klínovcem": "https://www.loucna.eu/",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Nelze načíst {path}: {type(exc).__name__}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Soubor {path} neobsahuje JSON objekt.")
    return value


def normalize_url(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return ""
    query = [
        (key, val)
        for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in monitor.VOLATILE_QUERY_KEYS
    ]
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, urlencode(query, doseq=True), "")
    )


def build_complete_config(
    legacy_path: Path, regional_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    legacy = read_json(legacy_path)
    regional = read_json(regional_path)

    municipalities = [
        dict(item) for item in regional.get("municipalities", []) if isinstance(item, dict)
    ]
    institutions = [
        item
        for item in regional.get("namedInstitutionsAndEventSources", [])
        if isinstance(item, dict)
    ]
    unresolved = (
        (regional.get("discoveryStatus") or {}).get(
            "unresolvedDiscoverOfficialUrlEntries", []
        )
        or []
    )

    # Kritická pojistka: původní ORP registr nesmí při rozšiřování regionu ztratit
    # žádnou dříve sledovanou obec. Tyto dvě položky v širokém registru chyběly.
    existing_names = {
        str(item.get("name") or "").strip().casefold() for item in municipalities
    }
    supplemented_municipalities: list[str] = []
    for name, official_url in MANDATORY_REGIONAL_SUPPLEMENTS.items():
        if name.casefold() in existing_names:
            continue
        municipalities.append(
            {
                "name": name,
                "priority": "core",
                "officialUrl": official_url,
                "monitoringSource": "mandatory-orp-supplement",
                "officialUrlVerifiedAt": "2026-08-04",
            }
        )
        existing_names.add(name.casefold())
        supplemented_municipalities.append(name)

    if len(municipalities) < 57:
        raise SystemExit(
            f"Regionální registr obsahuje jen {len(municipalities)} obcí a měst; očekáváno nejméně 57."
        )
    if unresolved:
        raise SystemExit(
            "Regionální registr obsahuje nevyřešené oficiální zdroje: "
            + ", ".join(map(str, unresolved))
        )

    sources: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_source(
        name: object,
        url: object,
        category: object,
        tier: str,
        *,
        kind: str = "html",
    ) -> None:
        normalized = normalize_url(url)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        sources.append(
            {
                "name": str(name or normalized).strip(),
                "url": str(url).strip(),
                "category": str(category or "Široký region").strip(),
                "tier": tier,
                "kind": kind,
            }
        )

    for item in legacy.get("sources", []):
        if not isinstance(item, dict):
            continue
        add_source(
            item.get("name"),
            item.get("url"),
            item.get("category"),
            str(item.get("tier") or "organization"),
            kind=str(item.get("kind") or "html"),
        )

    local_terms: set[str] = set()
    municipality_names: list[str] = []
    for municipality in municipalities:
        name = str(municipality.get("name") or "").strip()
        official_url = municipality.get("officialUrl")
        if not name or not normalize_url(official_url):
            raise SystemExit(f"Obec nebo město bez platného oficiálního webu: {municipality}")
        municipality_names.append(name)
        local_terms.add(name)
        for locality in municipality.get("includedLocalities", []) or []:
            if str(locality).strip():
                local_terms.add(str(locality).strip())
        add_source(
            f"{name} – oficiální web",
            official_url,
            "Města a obce širokého regionu",
            "municipality",
        )
        for index, url in enumerate(municipality.get("monitorUrls", []) or [], start=1):
            add_source(
                f"{name} – doplňkový zdroj {index}",
                url,
                "Města a obce širokého regionu",
                "municipality",
            )

    for institution in institutions:
        name = str(institution.get("name") or "").strip()
        category = str(institution.get("category") or "regionální instituce")
        if not name:
            continue
        local_terms.add(name)
        add_source(name, institution.get("url"), category, "organization")
        for index, url in enumerate(institution.get("monitorUrls", []) or [], start=1):
            add_source(
                f"{name} – doplňkový zdroj {index}",
                url,
                category,
                "organization",
            )

    # Širší mediální pojistka: samostatné dotazy po menších skupinách názvů.
    # Dynamické místní termíny se před spuštěním přidají do monitor.LOCAL_TERMS.
    search_terms = sorted(local_terms, key=str.casefold)
    for index in range(0, len(search_terms), 8):
        group = search_terms[index : index + 8]
        query = "(" + " OR ".join(f'\"{term}\"' for term in group) + ") when:7d"
        url = "https://news.google.com/rss/search?" + urlencode(
            {"q": query, "hl": "cs", "gl": "CZ", "ceid": "CZ:cs"}
        )
        add_source(
            f"Google News – široký region {index // 8 + 1}",
            url,
            "Média – široký region",
            "aggregator",
            kind="rss",
        )

    metadata = {
        "regionalMunicipalities": len(municipalities),
        "regionalNamedInstitutions": len(institutions),
        "regionalRegistryUpdatedAt": regional.get("updatedAt"),
        "regionalRegistryComplete": not unresolved,
        "regionalSourceEntries": len(sources),
        "regionalLocalTerms": len(local_terms),
        "supplementedMunicipalities": supplemented_municipalities,
        "mandatoryRegionalSupplements": sorted(MANDATORY_REGIONAL_SUPPLEMENTS),
    }
    config = {
        "version": 3,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "name": "Kadaň, Kadaňsko a široký regionální dojezd",
            "municipalities": municipality_names,
        },
        "sources": sources,
        "coverageMetadata": metadata,
    }
    return config, {"metadata": metadata, "localTerms": sorted(local_terms)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", default="data/kadansko-extra-sources.json")
    parser.add_argument("--regional", default="data/regional-sources.json")
    parser.add_argument("--state", default="data/all-kadansko-monitoring-state.json")
    parser.add_argument("--status", default="data/all-kadansko-monitoring-status.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config, details = build_complete_config(Path(args.legacy), Path(args.regional))
    for term in details["localTerms"]:
        folded = monitor.fold(term)
        if folded:
            monitor.LOCAL_TERMS.add(folded)

    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".json", delete=False
    ) as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        config_path = Path(handle.name)

    original_argv = sys.argv[:]
    try:
        sys.argv = [
            "monitor_all_kadansko.py",
            "--extra-config",
            str(config_path),
            "--state",
            args.state,
            "--status",
            args.status,
            "--output",
            args.output,
        ]
        result = monitor.main()
    finally:
        sys.argv = original_argv
        config_path.unlink(missing_ok=True)

    status_path = Path(args.status)
    output_path = Path(args.output)
    status = read_json(status_path)
    coverage = status.setdefault("coverage", {})
    coverage.update(details["metadata"])
    coverage["completeHourlyMonitoring"] = True
    coverage["monitoringPolicy"] = {
        "primarySchedule": "hourly",
        "selfHealingWatchdog": True,
        "automaticFailedRunRetry": True,
        "emergencyIssueTrigger": True,
    }

    source_count = int(status.get("sourceCount") or 0)
    checked_sources = int(status.get("checkedSources") or 0)
    minimum_checked = max(75, int(source_count * 0.65))
    if source_count < 140:
        raise SystemExit(
            f"Kompletní monitoring obsahuje jen {source_count} zdrojů; očekáváno nejméně 140."
        )
    if checked_sources < minimum_checked:
        raise SystemExit(
            f"Dostupných bylo jen {checked_sources}/{source_count} zdrojů; minimum je {minimum_checked}."
        )
    if int(coverage.get("regionalMunicipalities") or 0) < 57:
        raise SystemExit("Výstup nepotvrzuje všech 57 obcí a měst širokého registru.")

    status_path.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    output = read_json(output_path)
    output["status"] = status
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "ok": True,
                "sources": f"{checked_sources}/{source_count}",
                "municipalities": coverage.get("regionalMunicipalities"),
                "institutions": coverage.get("regionalNamedInstitutions"),
                "alerts": status.get("newAlerts"),
                "supplements": coverage.get("supplementedMunicipalities"),
            },
            ensure_ascii=False,
        )
    )
    return int(result or 0)


if __name__ == "__main__":
    raise SystemExit(main())
