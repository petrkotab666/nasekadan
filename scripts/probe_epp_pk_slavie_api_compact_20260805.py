#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import unicodedata

import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "epp-pk-slavie-20260805"
OUT_JSON = BASE / "api-target-result.json"
OUT_MD = BASE / "api-target-result.md"
URLS = [
    "https://www.pomahejpohybem.cz/api/v1/projects",
    "https://pomahejpohybem.cz/api/frontend",
    "https://pomahejpohybem.cz/api/frontend/",
]
STRICT = ("pk slavie", "slavie kadan", "plavecky klub slavie")
CLUB = ("slavie",)
CITY = ("kadan",)
SWIM = ("plav", "swim")
PROJECT_KEYS = {
    "id", "project_id", "title", "subtitle", "name", "city", "description", "epoints",
    "actual_epoints", "published", "realized", "organisation_id", "organization_id", "image",
}


def safe_text(value: object, limit: int = 12000) -> str:
    text = str(value).encode("utf-8", "replace").decode("utf-8", "replace")
    return text[:limit]


def fold(value: object) -> str:
    text = unicodedata.normalize("NFKD", safe_text(value, 2_000_000))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).casefold()


def decode_non_surrogate_escapes(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        code = int(match.group(1), 16)
        if 0xD800 <= code <= 0xDFFF:
            return match.group(0)
        return chr(code)
    return re.sub(r"\\u([0-9a-fA-F]{4})", repl, text).replace("\\/", "/")


def classify(value: object) -> dict[str, bool]:
    f = fold(value)
    return {
        "strict": any(term in f for term in STRICT),
        "club": any(term in f for term in CLUB),
        "city": any(term in f for term in CITY),
        "swim": any(term in f for term in SWIM),
    }


def looks_like_project(value: dict) -> bool:
    keys = {fold(key) for key in value}
    return len(keys & PROJECT_KEYS) >= 2 and bool(keys & {"title", "subtitle", "name", "description", "project_id", "epoints"})


def compact(value: object, prefix: str = "$", out: dict[str, object] | None = None) -> dict[str, object]:
    if out is None:
        out = {}
    if len(out) >= 100:
        return out
    if isinstance(value, dict):
        for key, child in value.items():
            compact(child, f"{prefix}.{key}", out)
    elif isinstance(value, list):
        if len(value) <= 12:
            for index, child in enumerate(value):
                compact(child, f"{prefix}[{index}]", out)
    elif isinstance(value, (str, int, float, bool)) or value is None:
        out[prefix] = safe_text(value, 5000) if isinstance(value, str) else value
    return out


def find_projects(value: object, path: str = "$", out: list[dict] | None = None) -> list[dict]:
    if out is None:
        out = []
    if isinstance(value, dict):
        if looks_like_project(value):
            rendered = json.dumps(value, ensure_ascii=True, separators=(",", ":"), default=str)
            cls = classify(decode_non_surrogate_escapes(rendered))
            if cls["strict"] or (cls["club"] and cls["city"]) or (cls["city"] and cls["swim"]):
                out.append({
                    "path": path,
                    "classification": cls,
                    "fields": compact(value),
                })
        for key, child in value.items():
            find_projects(child, f"{path}.{key}", out)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            find_projects(child, f"{path}[{index}]", out)
    return out


def raw_windows(text: str, radius: int = 1800) -> list[dict]:
    decoded = decode_non_surrogate_escapes(text)
    f = fold(decoded)
    positions: set[int] = set()
    for term in STRICT + CLUB + CITY:
        start = 0
        while True:
            pos = f.find(term, start)
            if pos < 0:
                break
            positions.add(pos)
            start = pos + max(1, len(term))
    windows: list[dict] = []
    seen: set[str] = set()
    for pos in sorted(positions):
        excerpt = safe_text(decoded[max(0, pos-radius): min(len(decoded), pos+radius)], radius * 2)
        cls = classify(excerpt)
        if not (cls["strict"] or (cls["club"] and cls["city"]) or (cls["city"] and cls["swim"])):
            continue
        digest = sha256(excerpt.encode("utf-8", "replace")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        windows.append({"classification": cls, "excerpt": excerpt})
        if len(windows) >= 30:
            break
    return windows


def parse_response(text: str) -> tuple[object | None, list[str]]:
    errors: list[str] = []
    cleaned = text.encode("utf-8", "replace").decode("utf-8", "replace").lstrip("\ufeff\r\n\t ")
    try:
        return json.loads(cleaned), errors
    except Exception as exc:
        errors.append(f"standard: {exc}")
    try:
        from json_repair import repair_json
        repaired = repair_json(cleaned)
        return json.loads(repaired), errors
    except Exception as exc:
        errors.append(f"repair: {exc}")
    return None, errors


def probe(url: str) -> dict:
    response = requests.get(
        url,
        timeout=150,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/151.0 Safari/537.36",
            "Accept": "application/json,text/plain,*/*",
            "Cache-Control": "no-cache",
        },
        allow_redirects=True,
    )
    text = response.content.decode("utf-8", "replace")
    parsed, parse_errors = parse_response(text)
    projects = find_projects(parsed) if parsed is not None else []
    decoded = decode_non_surrogate_escapes(text)
    return {
        "requested_url": url,
        "final_url": response.url,
        "status": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "bytes": len(response.content),
        "sha256": sha256(response.content).hexdigest(),
        "json_parsed": parsed is not None,
        "parse_errors": parse_errors,
        "counts": {
            "slavie": fold(decoded).count("slavie"),
            "kadan": fold(decoded).count("kadan"),
            "plav": fold(decoded).count("plav"),
            "swim": fold(decoded).count("swim"),
        },
        "project_hits": projects[:50],
        "raw_windows": raw_windows(text),
    }


def unique_hits(endpoints: list[dict]) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for endpoint in endpoints:
        for hit in endpoint["project_hits"]:
            sig = json.dumps(hit["fields"], ensure_ascii=True, sort_keys=True, default=str)
            if sig in seen:
                continue
            seen.add(sig)
            out.append({"source": endpoint["final_url"], **hit})
    return out


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    endpoints: list[dict] = []
    errors: list[dict] = []
    for url in URLS:
        try:
            endpoints.append(probe(url))
        except Exception as exc:
            errors.append({"url": url, "error": safe_text(repr(exc), 2000)})
    hits = unique_hits(endpoints)
    exact = [hit for hit in hits if hit["classification"]["strict"]]
    club_city = [hit for hit in hits if hit["classification"]["club"] and hit["classification"]["city"]]
    city_swim = [hit for hit in hits if hit["classification"]["city"] and hit["classification"]["swim"]]
    conclusion = "exact_project_found" if exact else "club_city_project_found" if club_city else "city_swimming_projects_found" if city_swim else "target_not_found"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "conclusion": conclusion,
        "exact_hits": exact,
        "club_city_hits": club_city,
        "city_swim_hits": city_swim,
        "endpoints": endpoints,
        "errors": errors,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Cílená kontrola veřejných dat EPP – PK Slávie Kadaň",
        "",
        f"Vygenerováno: `{payload['generated_at']}`",
        f"Závěr: `{conclusion}`",
        f"Přímé shody: `{len(exact)}`",
        f"Shody Slávie + Kadaň: `{len(club_city)}`",
        f"Shody Kadaň + plavání: `{len(city_swim)}`",
        "",
        "## Projektové karty",
        "",
    ]
    selected = exact or club_city or city_swim
    if not selected:
        lines.append("- V úplném veřejném seznamu ani v aktuálních datech nebyla nalezena karta PK Slávie Kadaň.")
    for index, hit in enumerate(selected[:30], 1):
        lines.append(f"### {index}. {hit['source']}")
        for path, value in hit["fields"].items():
            lines.append(f"- `{path}` = `{safe_text(value, 1200).replace(chr(10), ' ')}`")
        lines.append("")
    lines += ["## Rozhraní", ""]
    for endpoint in endpoints:
        counts = endpoint["counts"]
        lines.append(
            f"- `{endpoint['status']}` {endpoint['final_url']} – {endpoint['bytes']} B, JSON `{endpoint['json_parsed']}`, "
            f"Slavie/Kadaň/plav: `{counts['slavie']}/{counts['kadan']}/{counts['plav']}`"
        )
        for window in endpoint["raw_windows"][:8]:
            excerpt = window["excerpt"].replace("\n", " ")
            lines.append(f"  - kontext: `{safe_text(excerpt, 1800)}`")
    if errors:
        lines += ["", "## Chyby", ""]
        lines.extend(f"- {item['url']}: {item['error']}" for item in errors)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "conclusion": conclusion,
        "exact": len(exact),
        "club_city": len(club_city),
        "city_swim": len(city_swim),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
