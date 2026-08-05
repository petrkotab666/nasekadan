#!/usr/bin/env python3
from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "epp-pk-slavie-20260805"
RAW = BASE / "raw-findings.json"
SUMMARY_JSON = BASE / "summary.json"
SUMMARY_MD = BASE / "summary.md"

STRICT_TERMS = (
    "pk slavie", "plavecky klub slavie", "slavie kadan", "slavie",
)
LOCATION_TERMS = ("kadan",)
SWIM_TERMS = ("plav", "swim")
PARAM_KEY_PARTS = (
    "name", "title", "nazev", "project", "amount", "price", "sum", "grant", "donation",
    "finance", "money", "castk", "kc", "target", "goal", "point", "bod", "purpose",
    "description", "popis", "ucel", "end", "deadline", "date", "datum", "term", "status",
    "progress", "current", "limit", "required", "need", "requested", "value", "url", "id",
)


def fold(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).casefold()


def scalar_map(value: object, path: str = "$", out: dict[str, object] | None = None, limit: int = 5000) -> dict[str, object]:
    if out is None:
        out = {}
    if len(out) >= limit:
        return out
    if isinstance(value, dict):
        for key, child in value.items():
            scalar_map(child, f"{path}.{key}", out, limit)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scalar_map(child, f"{path}[{index}]", out, limit)
    elif isinstance(value, (str, int, float, bool)) or value is None:
        rendered = value
        if isinstance(rendered, str) and len(rendered) > 4000:
            rendered = rendered[:4000] + " …"
        out[path] = rendered
    return out


def object_text(value: object, limit: int = 300000) -> str:
    try:
        rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        rendered = str(value)
    return rendered[:limit]


def classify(text: str) -> dict[str, bool]:
    folded = fold(text)
    strict = any(term in folded for term in STRICT_TERMS)
    location = any(term in folded for term in LOCATION_TERMS)
    swim = any(term in folded for term in SWIM_TERMS)
    return {
        "strict": strict,
        "location_and_swim": location and swim,
        "location": location,
        "swim": swim,
    }


def param_fields(value: object) -> dict[str, object]:
    flat = scalar_map(value)
    chosen: dict[str, object] = {}
    for path, child in flat.items():
        key = fold(path.rsplit(".", 1)[-1])
        rendered = str(child)
        if any(part in key for part in PARAM_KEY_PARTS):
            chosen[path] = child
        elif classify(rendered)["strict"] or classify(rendered)["location_and_swim"]:
            chosen[path] = child
        if len(chosen) >= 120:
            break
    return chosen


def collect_matching_nodes(root: object) -> list[dict]:
    queue: deque[tuple[str, object, int]] = deque([("$", root, 0)])
    hits: list[dict] = []
    seen_signatures: set[str] = set()
    while queue:
        path, value, depth = queue.popleft()
        if depth > 14:
            continue
        if isinstance(value, dict):
            text = object_text(value)
            cls = classify(text)
            if cls["strict"] or cls["location_and_swim"]:
                fields = param_fields(value)
                signature = json.dumps(fields, ensure_ascii=False, sort_keys=True, default=str)
                if signature not in seen_signatures:
                    seen_signatures.add(signature)
                    hits.append({
                        "path": path,
                        "classification": cls,
                        "fields": fields,
                        "preview": text[:8000],
                    })
                    if len(hits) >= 80:
                        break
            for key, child in value.items():
                queue.append((f"{path}.{key}", child, depth + 1))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                queue.append((f"{path}[{index}]", child, depth + 1))
        elif isinstance(value, str):
            cls = classify(value)
            if cls["strict"] or cls["location_and_swim"]:
                signature = f"{path}:{value[:1000]}"
                if signature not in seen_signatures:
                    seen_signatures.add(signature)
                    hits.append({
                        "path": path,
                        "classification": cls,
                        "fields": {path: value[:8000]},
                        "preview": value[:8000],
                    })
                    if len(hits) >= 80:
                        break
    return hits


def extract_urls(value: object) -> list[str]:
    pattern = re.compile(r"https?://[^\s\"'<>|\\]+", re.I)
    rendered = object_text(value, 10_000_000)
    urls: set[str] = set()
    for url in pattern.findall(rendered):
        cleaned = url.rstrip(".,);]}\\")
        folded = fold(cleaned)
        if any(token in folded for token in ("pomahejpohybem", "nadacecez", "api", "project")):
            urls.add(cleaned)
    return sorted(urls)


def network_summary(raw: dict) -> list[dict]:
    output: list[dict] = []
    for entry in raw.get("web", {}).get("network", []):
        text = object_text(entry)
        cls = classify(text)
        has_body = bool(entry.get("body"))
        interesting_url = any(x in fold(entry.get("url", "")) for x in ("api", "project", "graphql", "pomahejpohybem"))
        if cls["strict"] or cls["location_and_swim"] or (has_body and interesting_url):
            compact = {
                "url": entry.get("url"),
                "status": entry.get("status"),
                "resource_type": entry.get("resource_type"),
                "content_type": entry.get("content_type"),
                "classification": cls,
            }
            body = entry.get("body")
            if isinstance(body, str):
                compact["body_excerpt"] = body[:12000]
                try:
                    parsed = json.loads(body)
                    compact["matching_nodes"] = collect_matching_nodes(parsed)[:20]
                except Exception:
                    pass
            if entry.get("keyword_matches"):
                compact["keyword_matches"] = entry.get("keyword_matches")[:40]
            if entry.get("keyword_windows"):
                compact["keyword_windows"] = entry.get("keyword_windows")[:20]
            output.append(compact)
            if len(output) >= 80:
                break
    return output


def candidate_summary(raw: dict) -> list[dict]:
    output: list[dict] = []
    for entry in raw.get("candidate_responses", []):
        text = object_text(entry)
        cls = classify(text)
        if cls["strict"] or cls["location_and_swim"] or entry.get("json_keyword_matches"):
            output.append({
                "url": entry.get("url"),
                "status": entry.get("status"),
                "content_type": entry.get("content_type"),
                "classification": cls,
                "json_keyword_matches": entry.get("json_keyword_matches", [])[:50],
                "text_windows": entry.get("text_windows", [])[:20],
                "json_preview": entry.get("json_preview") if isinstance(entry.get("json_preview"), (dict, list)) else str(entry.get("json_preview", ""))[:12000],
            })
    return output[:60]


def apk_summary(raw: dict) -> list[dict]:
    output: list[dict] = []
    for item in raw.get("apk", {}).get("matches", []):
        snippet = item.get("snippet", "")
        folded = fold(snippet)
        cls = classify(snippet)
        if cls["strict"] or cls["location_and_swim"] or any(token in folded for token in ("http", "api", "project", "graphql", "pomahejpohybem", "nadacecez")):
            output.append({"file": item.get("file"), "snippet": snippet[:3000], "classification": cls})
        if len(output) >= 120:
            break
    return output


def infer_fields(hits: list[dict]) -> dict:
    extracted: dict[str, list[dict]] = {k: [] for k in ("names", "amounts", "purposes", "points", "dates", "statuses", "ids_urls")}
    for hit in hits:
        for path, value in hit.get("fields", {}).items():
            key = fold(path.rsplit(".", 1)[-1])
            record = {"path": path, "value": value, "source_node": hit.get("path")}
            if any(x in key for x in ("name", "title", "nazev")):
                extracted["names"].append(record)
            if any(x in key for x in ("amount", "price", "sum", "grant", "donation", "finance", "money", "castk", "kc")):
                extracted["amounts"].append(record)
            if any(x in key for x in ("purpose", "description", "popis", "ucel")):
                extracted["purposes"].append(record)
            if any(x in key for x in ("point", "bod", "target", "goal", "required", "need")):
                extracted["points"].append(record)
            if any(x in key for x in ("end", "deadline", "date", "datum", "term")):
                extracted["dates"].append(record)
            if any(x in key for x in ("status", "progress", "current")):
                extracted["statuses"].append(record)
            if key.endswith("id") or "url" in key:
                extracted["ids_urls"].append(record)
    for key in extracted:
        unique: list[dict] = []
        seen: set[str] = set()
        for item in extracted[key]:
            sig = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
            if sig not in seen:
                seen.add(sig)
                unique.append(item)
        extracted[key] = unique[:60]
    return extracted


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Chybí {RAW}")
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    all_hits = collect_matching_nodes(raw)
    strict_hits = [h for h in all_hits if h["classification"]["strict"]]
    contextual_hits = [h for h in all_hits if h["classification"]["location_and_swim"] and not h["classification"]["strict"]]
    inferred = infer_fields(strict_hits or contextual_hits)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_generated_at": raw.get("generated_at"),
        "strict_hit_count": len(strict_hits),
        "location_swim_hit_count": len(contextual_hits),
        "strict_hits": strict_hits[:40],
        "location_swim_hits": contextual_hits[:20],
        "inferred_project_fields": inferred,
        "network_entries": network_summary(raw),
        "candidate_responses": candidate_summary(raw),
        "candidate_urls": extract_urls(raw)[:200],
        "apk": {
            "downloaded": raw.get("apk", {}).get("downloaded"),
            "url": raw.get("apk", {}).get("url"),
            "size": raw.get("apk", {}).get("size"),
            "relevant_strings": apk_summary(raw),
            "errors": raw.get("apk", {}).get("errors", [])[:30],
        },
        "web_errors": raw.get("web", {}).get("errors", [])[:30],
        "conclusion": (
            "exact_project_trace_found" if strict_hits else
            "kadan_swimming_context_found" if contextual_hits else
            "no_project_parameters_found"
        ),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Kompaktní vyhodnocení EPP – PK Slávie Kadaň",
        "",
        f"Vygenerováno: `{summary['generated_at']}`",
        f"Závěr: `{summary['conclusion']}`",
        f"Přímé shody na Slávii: `{summary['strict_hit_count']}`",
        f"Kontextové shody Kadaň + plavání: `{summary['location_swim_hit_count']}`",
        "",
        "## Odvozená pole projektu",
        "",
    ]
    for category, items in inferred.items():
        lines.append(f"### {category}")
        if not items:
            lines.append("- nenalezeno")
        else:
            for item in items[:25]:
                value = str(item["value"]).replace("\n", " ")
                lines.append(f"- `{item['path']}` = `{value[:800]}`")
        lines.append("")

    lines += ["## Přímé relevantní objekty", ""]
    for hit in (strict_hits[:20] or contextual_hits[:10]):
        lines.append(f"### `{hit['path']}`")
        for path, value in list(hit.get("fields", {}).items())[:40]:
            rendered = str(value).replace("\n", " ")
            lines.append(f"- `{path}` = `{rendered[:1000]}`")
        lines.append("")

    lines += ["## Relevantní síťová volání", ""]
    for entry in summary["network_entries"][:30]:
        lines.append(f"- `{entry.get('status')}` {entry.get('url')}")
    if not summary["network_entries"]:
        lines.append("- žádné síťové volání neobsahovalo přímou shodu")

    lines += ["", "## Technická omezení", ""]
    errors = summary["web_errors"] + summary["apk"]["errors"]
    if errors:
        lines.extend(f"- {str(error)[:1000]}" for error in errors)
    else:
        lines.append("- bez zásadní technické chyby")

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary": str(SUMMARY_MD.relative_to(ROOT)),
        "json": str(SUMMARY_JSON.relative_to(ROOT)),
        "conclusion": summary["conclusion"],
        "strict_hit_count": summary["strict_hit_count"],
        "location_swim_hit_count": summary["location_swim_hit_count"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
