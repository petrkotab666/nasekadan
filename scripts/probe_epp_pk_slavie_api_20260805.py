#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import html
import json
import re
import unicodedata

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "epp-pk-slavie-20260805" / "api-target-result.json"
OUT_MD = ROOT / "research" / "epp-pk-slavie-20260805" / "api-target-result.md"
URLS = [
    "https://www.pomahejpohybem.cz/api/v1/projects",
    "https://pomahejpohybem.cz/api/frontend",
    "https://pomahejpohybem.cz/api/frontend/",
]
STRICT = ("pk slavie", "slavie kadan", "plavecky klub slavie", "pk slávie", "slávie kadaň")
CLUB = ("slavie", "slávie")
CITY = ("kadan", "kadaň")
SWIM = ("plav", "swim")
PARAM_KEYS = (
    "id", "project", "title", "subtitle", "name", "organisation", "organization", "city",
    "description", "purpose", "amount", "price", "sum", "grant", "finance", "money",
    "epoint", "point", "bod", "target", "goal", "actual", "progress", "status", "published",
    "realized", "date", "start", "end", "deadline", "created", "updated", "image", "url",
)


def fold(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).casefold()


def decode_unicode_escapes(text: str) -> str:
    text = html.unescape(text)
    def repl(match: re.Match[str]) -> str:
        try:
            return chr(int(match.group(1), 16))
        except Exception:
            return match.group(0)
    text = re.sub(r"\\u([0-9a-fA-F]{4})", repl, text)
    text = text.replace("\\/", "/")
    return text


def classify(text: str) -> dict[str, bool]:
    f = fold(text)
    return {
        "strict": any(term in f for term in tuple(fold(x) for x in STRICT)),
        "club": any(term in f for term in tuple(fold(x) for x in CLUB)),
        "city": any(term in f for term in tuple(fold(x) for x in CITY)),
        "swim": any(term in f for term in tuple(fold(x) for x in SWIM)),
    }


def scalar_fields(value: object, prefix: str = "$", out: dict[str, object] | None = None) -> dict[str, object]:
    if out is None:
        out = {}
    if len(out) >= 300:
        return out
    if isinstance(value, dict):
        for key, child in value.items():
            scalar_fields(child, f"{prefix}.{key}", out)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            scalar_fields(child, f"{prefix}[{i}]", out)
    elif isinstance(value, (str, int, float, bool)) or value is None:
        out[prefix] = value if not isinstance(value, str) or len(value) <= 5000 else value[:5000] + " …"
    return out


def compact_fields(value: dict) -> dict[str, object]:
    fields = scalar_fields(value)
    result: dict[str, object] = {}
    for path, child in fields.items():
        key = fold(path.rsplit(".", 1)[-1])
        if any(part in key for part in PARAM_KEYS):
            result[path] = child
        elif classify(str(child))["strict"]:
            result[path] = child
        elif classify(str(child))["city"] and classify(json.dumps(value, ensure_ascii=False))["swim"]:
            result[path] = child
    return result


def walk_dicts(value: object, path: str = "$", output: list[dict] | None = None) -> list[dict]:
    if output is None:
        output = []
    if len(output) >= 100:
        return output
    if isinstance(value, dict):
        rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        cls = classify(rendered)
        if cls["strict"] or (cls["club"] and cls["city"]) or (cls["city"] and cls["swim"]):
            output.append({
                "path": path,
                "classification": cls,
                "fields": compact_fields(value),
                "object": value,
            })
        for key, child in value.items():
            walk_dicts(child, f"{path}.{key}", output)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_dicts(child, f"{path}[{index}]", output)
    return output


def windows(text: str, term_groups: list[tuple[str, ...]], radius: int = 2500) -> list[dict]:
    folded = fold(text)
    hits: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for group in term_groups:
        for term in group:
            fterm = fold(term)
            start = 0
            while True:
                pos = folded.find(fterm, start)
                if pos < 0:
                    break
                left = max(0, pos - radius)
                right = min(len(text), pos + len(term) + radius)
                key = (left, right)
                if key not in seen:
                    seen.add(key)
                    excerpt = text[left:right]
                    cls = classify(excerpt)
                    if cls["strict"] or (cls["club"] and cls["city"]) or (cls["city"] and cls["swim"]):
                        hits.append({"term": term, "position": pos, "classification": cls, "excerpt": excerpt})
                start = pos + max(1, len(fterm))
                if len(hits) >= 100:
                    return hits
    return hits


def extract_balanced_objects(text: str, positions: list[int]) -> list[str]:
    objects: list[str] = []
    seen: set[str] = set()
    for pos in positions:
        search_start = max(0, pos - 200000)
        left_candidates = [i for i in range(pos, search_start - 1, -1) if text[i:i+1] == "{"]
        for left in left_candidates[:200]:
            depth = 0
            in_string = False
            escape = False
            for right in range(left, min(len(text), left + 500000)):
                ch = text[right]
                if in_string:
                    if escape:
                        escape = False
                    elif ch == "\\":
                        escape = True
                    elif ch == '"':
                        in_string = False
                    continue
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        if right >= pos:
                            candidate = text[left:right+1]
                            cls = classify(candidate)
                            if cls["strict"] or (cls["club"] and cls["city"]) or (cls["city"] and cls["swim"]):
                                signature = sha256(candidate.encode("utf-8", "replace")).hexdigest()
                                if signature not in seen:
                                    seen.add(signature)
                                    objects.append(candidate)
                            break
                        break
            if objects and len(objects) >= 50:
                return objects
    return objects


def parse_json_forgiving(text: str) -> tuple[object | None, list[str]]:
    errors: list[str] = []
    candidates = [text, text.lstrip("\ufeff\n\r\t ")]
    for candidate in candidates:
        try:
            return json.loads(candidate), errors
        except Exception as exc:
            errors.append(str(exc))
    return None, errors


def probe(url: str) -> dict:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151.0 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
        "Cache-Control": "no-cache",
    })
    response = session.get(url, timeout=120, allow_redirects=True)
    raw = response.text
    decoded = decode_unicode_escapes(raw)
    parsed, parse_errors = parse_json_forgiving(raw)
    if parsed is None and decoded != raw:
        parsed, extra_errors = parse_json_forgiving(decoded)
        parse_errors.extend(extra_errors)
    parsed_hits = walk_dicts(parsed) if parsed is not None else []
    term_groups = [STRICT, CLUB, CITY, SWIM]
    text_hits = windows(decoded, term_groups)
    positions: list[int] = []
    folded = fold(decoded)
    for term in STRICT + CLUB + CITY:
        fterm = fold(term)
        start = 0
        while True:
            pos = folded.find(fterm, start)
            if pos < 0:
                break
            positions.append(pos)
            start = pos + max(1, len(fterm))
    balanced_raw = extract_balanced_objects(decoded, sorted(set(positions))) if not parsed_hits else []
    balanced: list[dict] = []
    for candidate in balanced_raw:
        obj, errs = parse_json_forgiving(candidate)
        if isinstance(obj, dict):
            balanced.append({"fields": compact_fields(obj), "object": obj})
        else:
            balanced.append({"raw": candidate[:30000], "parse_errors": errs[:3]})
    return {
        "requested_url": url,
        "final_url": response.url,
        "status": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "bytes": len(response.content),
        "sha256": sha256(response.content).hexdigest(),
        "json_parsed": parsed is not None,
        "json_parse_errors": parse_errors[:6],
        "parsed_hits": parsed_hits,
        "text_hits": text_hits,
        "balanced_hits": balanced,
        "global_classification": classify(decoded),
        "counts": {
            "slavie": fold(decoded).count("slavie"),
            "kadan": fold(decoded).count("kadan"),
            "plav": fold(decoded).count("plav"),
            "swim": fold(decoded).count("swim"),
        },
    }


def dedupe_hits(results: list[dict]) -> list[dict]:
    output: list[dict] = []
    seen: set[str] = set()
    for result in results:
        for category in ("parsed_hits", "balanced_hits"):
            for hit in result.get(category, []):
                fields = hit.get("fields", {})
                signature = json.dumps(fields or hit, ensure_ascii=False, sort_keys=True, default=str)
                if signature in seen:
                    continue
                seen.add(signature)
                output.append({"source": result["final_url"], "category": category, **hit})
    return output


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    errors: list[dict] = []
    for url in URLS:
        try:
            results.append(probe(url))
        except Exception as exc:
            errors.append({"url": url, "error": repr(exc)})
    project_hits = dedupe_hits(results)
    exact_hits = [hit for hit in project_hits if classify(json.dumps(hit, ensure_ascii=False))["strict"]]
    city_swim_hits = [hit for hit in project_hits if classify(json.dumps(hit, ensure_ascii=False))["city"] and classify(json.dumps(hit, ensure_ascii=False))["swim"]]
    conclusion = "exact_project_found" if exact_hits else "city_swimming_trace_only" if city_swim_hits else "no_target_project_found"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "conclusion": conclusion,
        "exact_hits": exact_hits,
        "city_swim_hits": city_swim_hits,
        "all_project_hits": project_hits,
        "endpoints": results,
        "errors": errors,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Cílená kontrola veřejného API EPP – PK Slávie Kadaň",
        "",
        f"Vygenerováno: `{payload['generated_at']}`",
        f"Závěr: `{conclusion}`",
        f"Přímé projektové shody: `{len(exact_hits)}`",
        f"Shody Kadaň + plavání: `{len(city_swim_hits)}`",
        "",
        "## Nalezené projektové objekty",
        "",
    ]
    selected = exact_hits or city_swim_hits
    if not selected:
        lines.append("- V úplném veřejném seznamu ani v aktuálním API nebyl nalezen projekt odpovídající PK Slávii Kadaň.")
    for index, hit in enumerate(selected[:30], 1):
        lines.append(f"### Objekt {index} – {hit.get('source')}")
        fields = hit.get("fields", {})
        if fields:
            for path, value in fields.items():
                rendered = str(value).replace("\n", " ")
                lines.append(f"- `{path}` = `{rendered[:1500]}`")
        elif hit.get("raw"):
            lines.append(f"- `{str(hit['raw'])[:5000]}`")
        lines.append("")
    lines += ["## Stav jednotlivých rozhraní", ""]
    for result in results:
        lines.append(
            f"- `{result['status']}` {result['final_url']} – {result['bytes']} B, "
            f"JSON: `{result['json_parsed']}`, výskyty Slavie/Kadaň/plavání: "
            f"`{result['counts']['slavie']}/{result['counts']['kadan']}/{result['counts']['plav']}`"
        )
    if errors:
        lines += ["", "## Chyby", ""]
        lines.extend(f"- {item['url']}: {item['error']}" for item in errors)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "conclusion": conclusion,
        "exact_hits": len(exact_hits),
        "city_swim_hits": len(city_swim_hits),
        "json": str(OUT.relative_to(ROOT)),
        "markdown": str(OUT_MD.relative_to(ROOT)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
