#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
TRACKING_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "yclid", "mc_cid", "mc_eid",
}
VOLATILE_KEYS = {
    "tmstv", "timestamp", "tstamp", "cache", "nocache", "_", "rand",
    "ver", "version", "drawerurl", "cartdraweropened",
}
SOCIAL_HOSTS = {
    "facebook.com", "www.facebook.com", "instagram.com", "www.instagram.com",
}
MANDATORY_CATEGORY_PATTERNS = {
    "město a samospráva": [r"\bmesto\b", r"\bobec\b", r"samosprav"],
    "úřední desky a rozhodnutí": [r"uredni desk", r"rozhodnuti", r"verejn[ae] vyhlask"],
    "smlouvy a hospodaření": [r"smlouv", r"hospodar", r"rozpocet"],
    "veřejné zakázky": [r"verejn[ae] zakaz", r"\bnen\b", r"vestnik veřejnych zakazek", r"zakazky gov"],
    "hasiči a mimořádné události": [r"hasic", r"mimoradn", r"krizov"],
    "policie a bezpečnost": [r"policie", r"bezpecnost", r"kriminal"],
    "zdravotnictví": [r"zdravot", r"nemocnic", r"ambulanc", r"ordinac"],
    "základní školy": [r"zakladni skol", r"\bzs\b"],
    "mateřské školy": [r"matersk[ae] skol", r"\bms\b"],
    "sociální služby": [r"socialni"],
    "městské služby": [r"mestske sluz", r"technicke sluz", r"tepelne hospodar", r"kabelova televize"],
    "doprava": [r"doprav", r"zeleznic", r"silnic", r"vyluk"],
    "regionální média": [r"regionalni media", r"denik", r"rozhlas", r"noviny"],
}
MANDATORY_CATEGORIES = set(MANDATORY_CATEGORY_PATTERNS)
DEFAULT_EXCLUDE_URL_PATTERNS = [
    r"(?:[?&](?:lang|zmena-vzhledu|design|print|mapa-webu)=)",
    r"/(?:kontakt|kontakty|mapa-webu|sitemap|search|hledej|author|tag|category)/?$",
    r"(?:[?&]subakce=(?:eventsearch|addevents|events_type))",
    r"(?:[?&]events_type=\d+)",
]
DEFAULT_IGNORE_TITLE_PATTERNS = [
    r"^(?:číst|čtěte|zobrazit|více|detail|pokračovat)(?:\s+více)?$",
    r"^(?:přeskočit na obsah|hlavní stránka|domů|úvod|menu|kontakt|kontakty)$",
    r"^(?:všechny akce|rozšířené vyhledávání|přidat novou akci)$",
    r"^(?:prezentace|pro děti|psychologický|punk-rock|rock and roll|talkshow|tragédie|tragikomedie|tvůrčí dílny|tématická akce|vernisáž|vzdělávání|vážná hudba|slavnostní program|přednáška, kurz)$",
]


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, value: dict[str, Any]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    comparable = dict(value)
    comparable.pop("generatedAt", None)
    previous = read_json(path)
    previous_comparable = dict(previous)
    previous_comparable.pop("generatedAt", None)
    if previous and comparable == previous_comparable:
        return False
    value = dict(value)
    value["generatedAt"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def fold(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value).lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def canonical_url(value: object) -> str:
    raw = clean(value)
    if not raw:
        return ""
    parsed = urlsplit(raw)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return ""
    query = []
    for key, val in parse_qsl(parsed.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered in TRACKING_KEYS or lowered in VOLATILE_KEYS:
            continue
        query.append((key, val))
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        path,
        urlencode(query, doseq=True),
        "",
    ))


def host(value: object) -> str:
    return urlsplit(canonical_url(value)).netloc


def infer_kind(source: dict[str, Any]) -> str:
    explicit = clean(source.get("kind")).lower()
    if explicit in {"rss", "atom", "html", "json", "xml"}:
        return explicit
    url = canonical_url(source.get("url"))
    if re.search(r"(?:rss|feed|atom)(?:\.|/|$)", url, re.I):
        return "rss"
    if url.endswith(".xml"):
        return "xml"
    return "html"


def infer_tier(source: dict[str, Any]) -> str:
    explicit = clean(source.get("tier")).lower()
    if explicit:
        return explicit
    category = fold(source.get("category"))
    name = fold(source.get("name"))
    text = f"{category} {name}"
    if "uredni deska" in text or "mesto " in name or "obec " in name:
        return "municipality"
    if "registr" in text or "zakazk" in text or "eia" in text:
        return "public_registry"
    if "policie" in text:
        return "police"
    if "hasic" in text or "kriz" in text:
        return "emergency"
    if "media" in text or "denik" in text or "rozhlas" in text or "noviny" in text:
        return "regional_media"
    if "doprava" in text or "zeleznic" in text or "silnic" in text:
        return "transport"
    if "voda" in text or "teplo" in text or "elektr" in text or "odstavk" in text:
        return "utility"
    return "organization"


def infer_cadences(source: dict[str, Any]) -> list[str]:
    explicit = source.get("cadences")
    if isinstance(explicit, list):
        values = [clean(x).lower() for x in explicit if clean(x).lower() in {"urgent", "hourly", "daily"}]
        if values:
            return sorted(set(values), key=("urgent", "hourly", "daily").index)
    tier = infer_tier(source)
    text = fold(f"{source.get('name')} {source.get('category')}")
    values: set[str] = {"daily"}
    if tier in {
        "municipality", "organization", "directory", "regional_media", "national_media",
        "regional_authority", "transport", "utility", "police", "emergency",
    }:
        values.add("hourly")
    if tier in {"police", "emergency"} or any(token in text for token in (
        "odstavk", "vypadek", "kriz", "hasic", "policie", "dopravni", "nehod",
    )):
        values.add("urgent")
    return [x for x in ("urgent", "hourly", "daily") if x in values]


def infer_priority(source: dict[str, Any]) -> int:
    if source.get("priority") is not None:
        try:
            return max(1, min(100, int(source["priority"])))
        except (TypeError, ValueError):
            pass
    return {
        "emergency": 100,
        "police": 100,
        "municipality": 95,
        "regional_authority": 95,
        "public_registry": 92,
        "organization": 85,
        "utility": 90,
        "transport": 85,
        "regional_media": 75,
        "national_media": 75,
        "aggregator": 45,
        "directory": 60,
    }.get(infer_tier(source), 70)


def requires_local_match(source: dict[str, Any]) -> bool:
    if "requiresLocalMatch" in source:
        return bool(source.get("requiresLocalMatch"))
    tier = infer_tier(source)
    return tier in {
        "regional_media", "national_media", "aggregator", "regional_authority",
        "transport", "utility", "emergency", "police", "public_registry",
    }


def infer_alert_policy(source: dict[str, Any]) -> str:
    explicit = clean(source.get("alertPolicy")).lower()
    if explicit in {"items", "snapshot", "discovery", "health_only"}:
        return explicit
    if host(source.get("url")) in SOCIAL_HOSTS:
        return "health_only"
    text = fold(f"{source.get('name')} {source.get('category')} {source.get('url')}")
    if "gis" in text or "overeni-planovane-odstavky" in text:
        return "snapshot"
    if "vyhledavani" in text and infer_tier(source) == "public_registry":
        return "discovery"
    return "items"


def stable_id(name: object, url: object) -> str:
    raw = f"{fold(name)}|{canonical_url(url)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def add_source(
    registry: dict[str, dict[str, Any]],
    source: dict[str, Any],
    origin: str,
    *,
    default_category: str = "Kadaňsko",
) -> None:
    url = canonical_url(source.get("url"))
    if not url:
        return
    key = url
    name = clean(source.get("name")) or url
    category = clean(source.get("category")) or default_category
    current = registry.get(key)
    record = {
        "id": stable_id(name, url),
        "name": name,
        "url": url,
        "fallbackUrls": [
            canonical_url(x) for x in (source.get("fallbackUrls") or [])
            if canonical_url(x) and canonical_url(x) != url
        ],
        "kind": infer_kind(source),
        "tier": infer_tier(source),
        "category": category,
        "municipality": clean(source.get("municipality")),
        "cadences": infer_cadences(source),
        "priority": infer_priority(source),
        "alertPolicy": infer_alert_policy(source),
        "requiresLocalMatch": requires_local_match(source),
        "required": bool(source.get("required")),
        "monitorable": host(url) not in SOCIAL_HOSTS and infer_alert_policy(source) != "health_only",
        "rules": {
            "excludeUrlPatterns": list(dict.fromkeys(
                DEFAULT_EXCLUDE_URL_PATTERNS
                + list((source.get("rules") or {}).get("excludeUrlPatterns") or [])
            )),
            "ignoreTitlePatterns": list(dict.fromkeys(
                DEFAULT_IGNORE_TITLE_PATTERNS
                + list((source.get("rules") or {}).get("ignoreTitlePatterns") or [])
            )),
            "ignoreTextPatterns": list(dict.fromkeys(
                list((source.get("rules") or {}).get("ignoreTextPatterns") or [])
            )),
            "includeUrlPatterns": list(dict.fromkeys(
                list((source.get("rules") or {}).get("includeUrlPatterns") or [])
            )),
        },
        "origins": [origin],
        "aliases": [],
    }
    if current is None:
        registry[key] = record
        return
    current["origins"] = sorted(set(current.get("origins", [])) | {origin})
    current["aliases"] = sorted(set(current.get("aliases", [])) | {name} - {current["name"]})
    current["fallbackUrls"] = sorted(set(current.get("fallbackUrls", [])) | set(record["fallbackUrls"]))
    current["cadences"] = [x for x in ("urgent", "hourly", "daily") if x in set(current["cadences"]) | set(record["cadences"])]
    current["priority"] = max(int(current.get("priority") or 0), int(record["priority"]))
    current["required"] = bool(current.get("required")) or record["required"]
    current["monitorable"] = bool(current.get("monitorable")) or record["monitorable"]
    current["requiresLocalMatch"] = bool(current.get("requiresLocalMatch")) and record["requiresLocalMatch"]
    if record["alertPolicy"] == "items" or current.get("alertPolicy") in {"discovery", "health_only"}:
        current["alertPolicy"] = record["alertPolicy"]
    if not current.get("municipality") and record.get("municipality"):
        current["municipality"] = record["municipality"]
    if record["priority"] > current.get("priority", 0):
        current["name"] = record["name"]
        current["category"] = record["category"]
        current["tier"] = record["tier"]
    for key_name in ("excludeUrlPatterns", "ignoreTitlePatterns", "ignoreTextPatterns", "includeUrlPatterns"):
        current["rules"][key_name] = list(dict.fromkeys(current["rules"].get(key_name, []) + record["rules"].get(key_name, [])))


def load_sources() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    organizations = read_json(ROOT / "data" / "organizations.json")
    city = read_json(ROOT / "data" / "city-sources.json")
    extra = read_json(ROOT / "data" / "kadansko-extra-sources.json")
    urgent = read_json(ROOT / "data" / "urgent-kadan-sources.json")
    national = read_json(ROOT / "data" / "national-kadan-sources.json")
    supplemental = read_json(ROOT / "data" / "monitoring-supplemental-sources.json")

    organization_names: list[str] = []
    organization_missing_urls: list[str] = []
    for group in organizations.get("groups", []):
        if not isinstance(group, dict):
            continue
        category = clean(group.get("name")) or "Kadaňské organizace"
        for item in group.get("items", []):
            if not isinstance(item, dict):
                continue
            name = clean(item.get("name"))
            if name:
                organization_names.append(name)
            urls = item.get("monitorUrls") if isinstance(item.get("monitorUrls"), list) else [item.get("url")]
            valid = False
            for index, url in enumerate(urls, 1):
                if canonical_url(url):
                    valid = True
                    add_source(registry, {
                        "name": name if index == 1 else f"{name} – zdroj {index}",
                        "url": url,
                        "category": category,
                        "tier": "organization",
                        "required": True,
                        "requiresLocalMatch": False,
                    }, "organizations.json", default_category=category)
            if name and not valid:
                organization_missing_urls.append(name)

    for source in city.get("sources", []):
        if isinstance(source, dict):
            add_source(registry, source, "city-sources.json")
    for source in extra.get("sources", []):
        if isinstance(source, dict):
            add_source(registry, source, "kadansko-extra-sources.json")
    for source in urgent.get("sources", []):
        if isinstance(source, dict):
            enriched = dict(source)
            enriched["cadences"] = ["urgent", "hourly", "daily"]
            add_source(registry, enriched, "urgent-kadan-sources.json")
    for source in national.get("sources", []):
        if isinstance(source, dict):
            add_source(registry, source, "national-kadan-sources.json")
    for source in supplemental.get("sources", []):
        if isinstance(source, dict):
            add_source(registry, source, "monitoring-supplemental-sources.json")

    sources = sorted(
        registry.values(),
        key=lambda x: (-int(x.get("priority") or 0), fold(x.get("category")), fold(x.get("name")), x.get("url")),
    )
    scope = supplemental.get("scope") or {}
    municipalities = scope.get("municipalities") or []
    municipality_names = [clean(x.get("name")) for x in municipalities if isinstance(x, dict) and clean(x.get("name"))]
    monitored_municipalities = sorted({
        clean(source.get("municipality"))
        for source in sources
        if clean(source.get("municipality"))
    })
    missing_municipalities = sorted(set(municipality_names) - set(monitored_municipalities))

    folded_categories = {fold(source.get("category")) for source in sources}
    folded_source_texts = {fold(f"{source.get('name')} {source.get('category')}") for source in sources}
    present_mandatory: set[str] = set()
    for mandatory, patterns in MANDATORY_CATEGORY_PATTERNS.items():
        if any(
            re.search(pattern, value, re.I)
            for pattern in patterns
            for value in (folded_categories | folded_source_texts)
        ):
            present_mandatory.add(mandatory)
    missing_categories = sorted(MANDATORY_CATEGORIES - present_mandatory)

    coverage = {
        "canonicalOrganizations": len(set(organization_names)),
        "organizationsWithoutUrl": sorted(set(organization_missing_urls)),
        "registeredSources": len(sources),
        "monitorableSources": sum(1 for x in sources if x.get("monitorable")),
        "healthOnlySources": sum(1 for x in sources if x.get("alertPolicy") == "health_only"),
        "urgentSources": sum(1 for x in sources if "urgent" in x.get("cadences", [])),
        "hourlySources": sum(1 for x in sources if "hourly" in x.get("cadences", [])),
        "dailySources": sum(1 for x in sources if "daily" in x.get("cadences", [])),
        "scopeMunicipalities": municipality_names,
        "monitoredMunicipalities": monitored_municipalities,
        "missingMunicipalities": missing_municipalities,
        "mandatoryCategories": sorted(MANDATORY_CATEGORIES),
        "missingMandatoryCategories": missing_categories,
        "origins": sorted({
            origin for source in sources for origin in source.get("origins", [])
        }),
    }
    return sources, coverage


def validate(coverage: dict[str, Any]) -> None:
    failures = []
    if coverage.get("organizationsWithoutUrl"):
        failures.append(f"organizace bez URL: {coverage['organizationsWithoutUrl']}")
    if coverage.get("missingMunicipalities"):
        failures.append(f"obce bez oficiálního zdroje: {coverage['missingMunicipalities']}")
    if coverage.get("missingMandatoryCategories"):
        failures.append(f"chybějící povinné oblasti: {coverage['missingMandatoryCategories']}")
    if int(coverage.get("registeredSources") or 0) < 110:
        failures.append(f"jen {coverage.get('registeredSources')} registrovaných zdrojů")
    if int(coverage.get("urgentSources") or 0) < 8:
        failures.append(f"jen {coverage.get('urgentSources')} akutních zdrojů")
    if failures:
        raise SystemExit("Neúplný registr monitoringu: " + "; ".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/monitoring-registry.json")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    sources, coverage = load_sources()
    if not args.no_strict:
        validate(coverage)
    payload = {
        "version": 2,
        "scope": "Kadaň, ORP Kadaň a bezprostředně související region",
        "coverage": coverage,
        "sources": sources,
    }
    changed = write_json(ROOT / args.output, payload)
    print(json.dumps({
        "ok": True,
        "changed": changed,
        "sources": len(sources),
        "monitorable": coverage.get("monitorableSources"),
        "urgent": coverage.get("urgentSources"),
        "hourly": coverage.get("hourlySources"),
        "daily": coverage.get("dailySources"),
        "municipalities": len(coverage.get("monitoredMunicipalities") or []),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
