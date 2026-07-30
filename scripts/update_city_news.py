#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "city-news.json"
SOURCES_FILE = ROOT / "data" / "city-sources.json"
ORGANIZATIONS_FILE = ROOT / "data" / "organizations.json"
UA = "NaseKadanBot/1.3 (+https://nasekadan.cz; info@nasekadan.cz)"
MIN_SAFE_ITEMS = 3
MAX_WORKERS = 8


def fetch(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "cs,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=25) as response:
        return response.read().decode(
            response.headers.get_content_charset() or "utf-8", errors="replace"
        )


def clean(value: object) -> str:
    return re.sub(
        r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    ).strip()


def normalize_url(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return ""
    path = re.sub(r"/+$", "", parsed.path) or "/"
    return urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, "")
    )


def parse(page: str, source: dict[str, str]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for href, body in re.findall(
        r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.I | re.S
    ):
        title = clean(body)
        if len(title) < 10 or len(title) > 180:
            continue
        lower = title.lower()
        if any(
            token in lower
            for token in (
                "více",
                "menu",
                "kontakt",
                "facebook",
                "instagram",
                "cookies",
                "úvodní stránka",
                "přihlásit",
            )
        ):
            continue
        url = urljoin(source["url"], href)
        if not url.startswith("http") or normalize_url(url) == normalize_url(source["url"]):
            continue
        position = page.find(href)
        around = clean(page[max(0, position - 450) : position + 1100]) if position >= 0 else ""
        match = re.search(r"(\d{1,2})[./]\s*(\d{1,2})[./]\s*(20\d{2})", around)
        date = (
            f"{match.group(3)}-{int(match.group(2)):02d}-{int(match.group(1)):02d}"
            if match
            else ""
        )
        description = around.replace(title, "", 1)[:420].strip(" -|")
        key = hashlib.sha1(f"{title}|{url}".encode()).hexdigest()[:12]
        output.append(
            {
                "id": key,
                "title": title,
                "date": date,
                "category": source["category"],
                "description": description,
                "source": url,
                "sourceName": source["name"],
            }
        )
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for item in output:
        unique.setdefault((item["title"].lower(), item["source"]), item)
    return list(unique.values())[:15]


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_sources() -> tuple[list[dict[str, str]], dict[str, object]]:
    manual_config = read_json(SOURCES_FILE)
    organizations = read_json(ORGANIZATIONS_FILE)

    merged: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    manual_unique = 0
    directory_unique_added = 0

    def add_source(name: object, url: object, category: object, origin: str) -> bool:
        nonlocal manual_unique, directory_unique_added
        normalized = normalize_url(url)
        if not normalized or normalized in seen_urls:
            return False
        seen_urls.add(normalized)
        merged.append(
            {
                "name": clean(name) or normalized,
                "url": str(url).strip(),
                "category": clean(category) or "Organizace v Kadani",
                "origin": origin,
            }
        )
        if origin == "manual_registry":
            manual_unique += 1
        else:
            directory_unique_added += 1
        return True

    for source in manual_config.get("sources", []):
        if isinstance(source, dict):
            add_source(
                source.get("name"),
                source.get("url"),
                source.get("category"),
                "manual_registry",
            )

    directory_total = 0
    directory_with_url = 0
    directory_monitored = 0
    missing_directory_urls: list[str] = []

    for group in organizations.get("groups", []):
        if not isinstance(group, dict):
            continue
        category = clean(group.get("name")) or "Organizace v Kadani"
        for item in group.get("items", []):
            if not isinstance(item, dict):
                continue
            directory_total += 1
            name = clean(item.get("name")) or f"Organizace {directory_total}"
            raw_monitor_urls = item.get("monitorUrls")
            if isinstance(raw_monitor_urls, list):
                candidate_urls = raw_monitor_urls
            else:
                candidate_urls = [item.get("url")]
            valid_urls = [str(url).strip() for url in candidate_urls if normalize_url(url)]
            if not valid_urls:
                missing_directory_urls.append(name)
                continue
            directory_with_url += 1
            directory_monitored += 1
            for index, url in enumerate(valid_urls, start=1):
                source_name = name if index == 1 else f"{name} – zdroj {index}"
                add_source(source_name, url, category, "organization_directory")

    coverage_percent = round(
        (directory_monitored / directory_total * 100) if directory_total else 0, 2
    )
    coverage: dict[str, object] = {
        "directoryOrganizations": directory_total,
        "directoryOrganizationsWithUrl": directory_with_url,
        "monitoredDirectoryOrganizations": directory_monitored,
        "missingDirectoryOrganizations": missing_directory_urls,
        "coveragePercent": coverage_percent,
        "manualUniqueSources": manual_unique,
        "directoryUniqueSourcesAdded": directory_unique_added,
        "totalUniqueSources": len(merged),
        "directoryIsCanonicalRegistry": True,
    }
    return merged, coverage


def collect(source: dict[str, str]) -> tuple[dict[str, str], list[dict[str, str]], str]:
    try:
        return source, parse(fetch(source["url"]), source), ""
    except Exception as exc:  # jednotlivý výpadek nesmí shodit celý přehled
        return source, [], f"{type(exc).__name__}: {exc}"


def main() -> None:
    sources, coverage = load_sources()
    previous = read_json(OUT)
    items: list[dict[str, str]] = []
    errors: list[str] = []
    used: list[str] = []
    source_status: list[dict[str, object]] = []

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(sources)))) as executor:
        collected = list(executor.map(collect, sources))

    for source, parsed, error in collected:
        status: dict[str, object] = {
            "name": source["name"],
            "url": source["url"],
            "category": source["category"],
            "origin": source["origin"],
            "status": "failed" if error else "checked",
            "itemsFound": len(parsed),
        }
        if error:
            status["error"] = error
            errors.append(f"{source['name']}: {error}")
        else:
            items.extend(parsed)
        used.append(f"{source['name']} ({len(parsed)})")
        source_status.append(status)

    unique: dict[tuple[str, str], dict[str, str]] = {}
    for item in items:
        key = (item["title"].lower(), item["source"])
        if key not in unique or len(item["description"]) > len(unique[key]["description"]):
            unique[key] = item

    result = sorted(
        unique.values(),
        key=lambda item: (item.get("date") or "0000-00-00", item["title"]),
        reverse=True,
    )[:100]

    previous_items = previous.get("items") if isinstance(previous.get("items"), list) else []
    retained_previous_items = False
    if len(result) < MIN_SAFE_ITEMS and previous_items:
        retained_previous_items = True
        errors.append(
            f"Nový sběr vrátil jen {len(result)} položek; zachováno {len(previous_items)} předchozích položek."
        )
        result = previous_items
    elif len(result) < MIN_SAFE_ITEMS:
        raise SystemExit(
            f"Sběr vrátil jen {len(result)} položek a není dostupná bezpečná záloha."
        )

    comparable_previous = {
        "sources": previous.get("sources", []),
        "errors": previous.get("errors", []),
        "sourceStatus": previous.get("sourceStatus", []),
        "monitoringCoverage": previous.get("monitoringCoverage", {}),
        "retainedPreviousItems": previous.get("retainedPreviousItems", False),
        "items": previous_items,
    }
    comparable_new = {
        "sources": used,
        "errors": errors,
        "sourceStatus": source_status,
        "monitoringCoverage": coverage,
        "retainedPreviousItems": retained_previous_items,
        "items": result,
    }
    if comparable_previous == comparable_new:
        print(
            f"Beze změny: {len(result)} položek, {coverage['monitoredDirectoryOrganizations']} "
            f"z {coverage['directoryOrganizations']} organizací v monitoringu."
        )
        return

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        **comparable_new,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(OUT)
    failed = sum(1 for status in source_status if status["status"] == "failed")
    print(
        f"Uloženo {len(result)} položek; monitorováno "
        f"{coverage['monitoredDirectoryOrganizations']}/{coverage['directoryOrganizations']} organizací; "
        f"unikátních zdrojů {coverage['totalUniqueSources']}; přímých chyb zdrojů {failed}."
    )


if __name__ == "__main__":
    main()
