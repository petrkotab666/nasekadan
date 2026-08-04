#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import ssl
import unicodedata
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from build_monitoring_registry import ROOT, canonical_url, clean, fold, read_json, write_json

UA = "NaseKadanUnifiedMonitor/2.0 (+https://nasekadan.cz; info@nasekadan.cz)"
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/150 Safari/537.36"
MAX_WORKERS = 14
MAX_STATE_ITEMS = 30000
MODE_MAX_ALERTS = {"urgent": 30, "hourly": 60, "daily": 120}
MODE_MAX_AGE = {"urgent": 36, "hourly": 168, "daily": 720}
MODE_BOOTSTRAP_AGE = {"urgent": 12, "hourly": 2, "daily": 0}
GENERIC_TITLES = {
    "číst více", "čtěte více", "zobrazit více", "více", "detail", "pokračovat",
    "přeskočit na obsah", "hlavní stránka", "domů", "úvod", "menu", "kontakt",
    "kontakty", "všechny akce", "rozšířené vyhledávání", "přidat novou akci",
    "aktuality", "novinky", "program", "kalendář akcí", "facebook", "instagram",
}
LOCAL_CORE_TERMS = {
    "kadan", "kadansko", "prunerov", "tusimice", "nechranice", "uhost", "uhostany",
    "pokutice", "bystrice u kadane", "mikulovice u kadane", "hradiste u kadane",
    "nemocnice kadan", "elektrarna prunerov", "elektrarna tusimice",
}
URGENT_TERMS = {
    "pozar", "hori", "horel", "horela", "hasici", "nehoda", "havarie", "zraneni",
    "evakuace", "vybuch", "kour", "patrani", "pohresovan", "policie", "kriminaliste",
    "uzavirka", "neprujezdna", "vypadek", "odstavka", "bez elektriny", "bez vody",
    "unik", "nebezpeci", "vystraha", "zasah", "mimoradna udalost",
}
HIGH_TERMS = {
    "uredni deska", "verejna vyhlaska", "zastupitelstvo", "rada mesta", "usneseni",
    "smlouva", "verejna zakazka", "tendr", "dotace", "rozpocet", "nemocnice",
    "skola", "skolka", "ordinace", "ambulance", "odstavka", "vyluka", "uzavirka",
    "voda", "elektrina", "teplo", "doprava", "eia", "stavebni povoleni",
}
VOLATILE_TEXT_PATTERNS = [
    r"\bstaženo\s+[\d\s.,]+\s*[×x]\b",
    r"\bzůstává\s+\d+\b",
    r"\bcelkem hlasů:\s*\d+\b",
    r"\bposlední aktualizace:\s*[^<\n]+",
    r"\bčas poslední aktualizace:\s*[^<\n]+",
    r"\b\d{1,2}:\d{2}:\d{2}\b",
    r"\b(?:dnes|zítra),?\s+(?:pondělí|úterý|středa|čtvrtek|pátek|sobota|neděle)?\b",
    r"\b(?:tlak|vlhkost|vítr|srážky)\s+\d+(?:[.,]\d+)?\b",
]


def write_stable_status(path: Path, value: dict[str, Any]) -> bool:
    """Persist status only when its structural health changes.

    Freshness is checked from GitHub Actions run metadata, so a quiet monitor does
    not create a commit every fifteen minutes merely because checkedAt changed.
    """
    previous = read_json(path)
    comparable_previous = dict(previous)
    comparable_current = dict(value)
    for payload in (comparable_previous, comparable_current):
        payload.pop("checkedAt", None)
        payload.pop("generatedAt", None)
    if previous and comparable_previous == comparable_current:
        return False
    value = dict(value)
    value["generatedAt"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def strip_accents(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def normalized_title(value: object) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\(\s*staženo\s+[\d\s.,]+\s*[×x]\s*\)", " ", text, flags=re.I)
    text = re.sub(r"\b(?:číst|čtěte|zobrazit)\s+více\s*(?:->|→)?", " ", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" \t\r\n-|•·")
    return text


def clean_html_text(page: str, ignore_patterns: list[str] | None = None) -> str:
    text = re.sub(r"<(?:script|style|noscript|svg)\b.*?</(?:script|style|noscript|svg)>", " ", page, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    patterns = VOLATILE_TEXT_PATTERNS + list(ignore_patterns or [])
    for pattern in patterns:
        try:
            text = re.sub(pattern, " ", text, flags=re.I)
        except re.error:
            continue
    return re.sub(r"\s+", " ", text).strip()


def parse_datetime(value: object) -> datetime | None:
    raw = clean(value)
    if not raw:
        return None
    try:
        parsed = parsedate_to_datetime(raw)
        if parsed:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        pass
    for pattern, order in (
        (r"\b(20\d{2})[-./](\d{1,2})[-./](\d{1,2})(?:[ T](\d{1,2}):(\d{2}))?", "ymd"),
        (r"\b(\d{1,2})[. /](\d{1,2})[. /](20\d{2})(?:\s+(\d{1,2}):(\d{2}))?", "dmy"),
    ):
        match = re.search(pattern, raw)
        if not match:
            continue
        try:
            if order == "ymd":
                year, month, day = map(int, match.group(1, 2, 3))
            else:
                day, month, year = map(int, match.group(1, 2, 3))
            hour = int(match.group(4) or 0)
            minute = int(match.group(5) or 0)
            return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def request_once(url: str, user_agent: str) -> tuple[str, str, str]:
    request = Request(url, headers={
        "User-Agent": user_agent,
        "Accept": "application/rss+xml,application/atom+xml,application/xml,text/xml,text/html,application/xhtml+xml,application/json",
        "Accept-Language": "cs,en;q=0.7",
        "Cache-Control": "no-cache",
    })
    context = ssl.create_default_context()
    with urlopen(request, timeout=35, context=context) as response:
        content_type = response.headers.get_content_type() or ""
        charset = response.headers.get_content_charset() or "utf-8"
        final_url = response.geturl()
        return response.read().decode(charset, errors="replace"), content_type, final_url


def fetch_source(source: dict[str, Any]) -> tuple[str, str, str, str]:
    urls = [source.get("url")] + list(source.get("fallbackUrls") or [])
    errors = []
    for url in urls:
        if not canonical_url(url):
            continue
        for ua in (UA, BROWSER_UA):
            try:
                page, content_type, final_url = request_once(str(url), ua)
                return page, content_type, final_url, ""
            except HTTPError as exc:
                errors.append(f"{url}: HTTP {exc.code}")
                if exc.code not in {403, 406, 429, 503}:
                    break
            except (URLError, TimeoutError, ssl.SSLError, OSError) as exc:
                errors.append(f"{url}: {type(exc).__name__}: {exc}")
                break
    return "", "", "", "; ".join(errors[-6:]) or "zdroj se nepodařilo načíst"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def node_text(node: ET.Element, names: set[str]) -> str:
    for child in node.iter():
        if local_name(child.tag) in names:
            value = normalized_title("".join(child.itertext()))
            if value:
                return value
    return ""


def rss_link(node: ET.Element) -> str:
    for child in node.iter():
        if local_name(child.tag) != "link":
            continue
        href = clean(child.attrib.get("href"))
        if href:
            return href
        value = clean(child.text)
        if value:
            return value
    return ""


def parse_rss(page: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    root = ET.fromstring(page)
    output = []
    for node in [n for n in root.iter() if local_name(n.tag) in {"item", "entry"}][:250]:
        title = node_text(node, {"title"})
        url = canonical_url(urljoin(str(source.get("url")), rss_link(node)))
        description = node_text(node, {"description", "summary", "content", "encoded"})
        published_raw = node_text(node, {"pubdate", "published", "updated", "date"})
        if title and url:
            output.append({
                "title": title[:300],
                "url": url,
                "description": description[:2000],
                "published": parse_datetime(published_raw).isoformat() if parse_datetime(published_raw) else "",
            })
    return output


def global_page_date(page: str) -> datetime | None:
    patterns = [
        r'<meta\b[^>]*(?:property|name)=["\'](?:article:published_time|date|datePublished|publishdate)["\'][^>]*content=["\']([^"\']+)',
        r'<time\b[^>]*datetime=["\']([^"\']+)',
        r'"datePublished"\s*:\s*"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, re.I)
        if match:
            parsed = parse_datetime(match.group(1))
            if parsed:
                return parsed
    return None


def parse_html(page: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    page_date = global_page_date(page)
    for match in list(re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.I | re.S))[:3000]:
        title = normalized_title(match.group(2))
        if not title:
            continue
        raw_url = urljoin(str(source.get("url")), html.unescape(match.group(1)))
        url = canonical_url(raw_url)
        if not url:
            continue
        around_raw = page[max(0, match.start() - 250): min(len(page), match.end() + 900)]
        around = clean_html_text(around_raw, (source.get("rules") or {}).get("ignoreTextPatterns"))
        description = around.replace(title, " ", 1).strip(" -|•·")[:1800]
        date = None
        date_match = re.search(r'<time\b[^>]*datetime=["\']([^"\']+)', around_raw, re.I)
        if date_match:
            date = parse_datetime(date_match.group(1))
        if not date:
            date = parse_datetime(around)
        if not date:
            date = page_date
        output.append({
            "title": title[:300],
            "url": url,
            "description": description,
            "published": date.isoformat() if date else "",
        })
    return output


def compile_patterns(values: list[str]) -> list[re.Pattern[str]]:
    output = []
    for value in values:
        try:
            output.append(re.compile(str(value), re.I))
        except re.error:
            continue
    return output


def source_terms(registry: dict[str, Any]) -> set[str]:
    terms = set(LOCAL_CORE_TERMS)
    coverage = registry.get("coverage") or {}
    for value in coverage.get("scopeMunicipalities") or []:
        folded = fold(value)
        if folded:
            terms.add(folded)
    terms.update({
        "klasterec nad ohri", "brezno", "chomutov", "ohre", "nechranicka prehrada",
        "doupovske hory", "krusne hory",
    })
    return terms


def meaningful_title(title: str, source: dict[str, Any]) -> bool:
    folded = fold(title)
    if not folded or folded in {fold(x) for x in GENERIC_TITLES}:
        return False
    if len(title) < 8 or len(title) > 280:
        return False
    rules = source.get("rules") or {}
    if any(pattern.search(title) for pattern in compile_patterns(rules.get("ignoreTitlePatterns") or [])):
        return False
    # Regionální média občas nabízejí jen jména moderátorů nebo autorů.
    if source.get("requiresLocalMatch") and re.fullmatch(r"[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\wÁ-ž.-]+(?:\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\wÁ-ž.-]+){0,2}", title):
        return False
    return True


def url_allowed(url: str, source: dict[str, Any]) -> bool:
    if canonical_url(url) == canonical_url(source.get("url")):
        return False
    rules = source.get("rules") or {}
    excludes = compile_patterns(rules.get("excludeUrlPatterns") or [])
    if any(pattern.search(url) for pattern in excludes):
        return False
    includes = compile_patterns(rules.get("includeUrlPatterns") or [])
    if includes and not any(pattern.search(url) for pattern in includes):
        return False
    parsed = urlsplit(url)
    path = parsed.path.lower()
    if re.search(r"/(?:kontakt|kontakty|mapa-webu|sitemap|search|hledej|author|tag)/?$", path):
        return False
    return True


def local_matches(item: dict[str, Any], terms: set[str]) -> list[str]:
    haystack = fold(" ".join([
        str(item.get("title") or ""),
        str(item.get("description") or ""),
        str(item.get("url") or ""),
    ]))
    return sorted(term for term in terms if term and term in haystack)


def severity(item: dict[str, Any], source: dict[str, Any]) -> str:
    text = fold(f"{item.get('title')} {item.get('description')} {source.get('category')}")
    if any(term in text for term in URGENT_TERMS):
        return "urgent"
    if any(term in text for term in HIGH_TERMS) or int(source.get("priority") or 0) >= 95:
        return "high"
    return "medium"


def content_hash(item: dict[str, Any]) -> str:
    raw = fold(f"{item.get('title')}|{item.get('description')}")
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def semantic_title_key(title: object) -> str:
    text = fold(title)
    text = re.sub(r"\s+-\s+(?:chomutovsky denik|ustecky denik|mostecky denik|e-chomutovsko(?:\.cz)?|chomutovky(?:\.cz)?)$", "", text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def source_rank(source: dict[str, Any]) -> tuple[int, int]:
    direct = 0 if source.get("tier") == "aggregator" else 1
    return direct, int(source.get("priority") or 0)


def select_sources(registry: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    output = []
    for source in registry.get("sources") or []:
        if not isinstance(source, dict):
            continue
        if mode not in (source.get("cadences") or []):
            continue
        if not source.get("monitorable") and source.get("alertPolicy") != "health_only":
            continue
        output.append(source)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["urgent", "hourly", "daily"])
    parser.add_argument("--registry", default="data/monitoring-registry.json")
    parser.add_argument("--state")
    parser.add_argument("--status")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    mode = args.mode
    registry = read_json(ROOT / args.registry)
    if not registry.get("sources"):
        raise SystemExit("Jednotný registr monitoringu neexistuje nebo je prázdný.")
    state_path = ROOT / (args.state or f"data/monitoring-state-{mode}.json")
    status_path = ROOT / (args.status or f"data/monitoring-status-{mode}.json")
    output_path = Path(args.output)

    sources = select_sources(registry, mode)
    minimums = {"urgent": 8, "hourly": 70, "daily": 100}
    if len(sources) < minimums[mode]:
        raise SystemExit(f"Vrstva {mode} obsahuje jen {len(sources)} zdrojů; minimum je {minimums[mode]}.")

    state = read_json(state_path)
    item_state = state.get("items") if isinstance(state.get("items"), dict) else {}
    source_state = state.get("sources") if isinstance(state.get("sources"), dict) else {}
    bootstrap = not bool(item_state)
    now = datetime.now(timezone.utc)
    terms = source_terms(registry)

    def collect(source: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], str]:
        page, content_type, final_url, error = fetch_source(source)
        if error:
            return source, [], {}, error
        policy = source.get("alertPolicy")
        if policy in {"snapshot", "health_only"}:
            snapshot = clean_html_text(page, (source.get("rules") or {}).get("ignoreTextPatterns"))
            return source, [], {
                "hash": hashlib.sha256(fold(snapshot).encode("utf-8")).hexdigest()[:24],
                "text": snapshot[:4000],
                "finalUrl": final_url,
                "contentType": content_type,
            }, ""
        try:
            kind = str(source.get("kind") or "html").lower()
            if kind in {"rss", "atom", "xml"} or "xml" in content_type or page.lstrip().startswith("<?xml"):
                items = parse_rss(page, source)
            else:
                items = parse_html(page, source)
            return source, items, {
                "finalUrl": final_url,
                "contentType": content_type,
                "pageHash": hashlib.sha256(fold(clean_html_text(page)).encode("utf-8")).hexdigest()[:24],
            }, ""
        except Exception as exc:
            return source, [], {}, f"{type(exc).__name__}: {exc}"

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(sources))) as executor:
        collected = list(executor.map(collect, sources))

    statuses = []
    candidates_by_url: dict[str, dict[str, Any]] = {}
    candidates_by_title: dict[str, dict[str, Any]] = {}
    snapshot_alerts: list[dict[str, Any]] = []
    parsed_total = 0
    suppressed = {
        "genericTitle": 0,
        "excludedUrl": 0,
        "missingLocalMatch": 0,
        "discoveryNotImportant": 0,
        "stale": 0,
        "duplicate": 0,
    }

    for source, items, metadata, error in collected:
        source_id = str(source.get("id"))
        previous_source = source_state.get(source_id) if isinstance(source_state.get(source_id), dict) else {}
        status = {
            "id": source_id,
            "name": source.get("name"),
            "url": source.get("url"),
            "category": source.get("category"),
            "tier": source.get("tier"),
            "policy": source.get("alertPolicy"),
            "status": "failed" if error else "checked",
            "itemsParsed": len(items),
            **({"error": error} if error else {}),
        }
        statuses.append(status)
        if error:
            # Repeated identical failure does not rewrite state every cycle. A
            # transition or a changed error is persisted and surfaced by health.
            if previous_source.get("lastError") != error:
                source_state[source_id] = {
                    **previous_source,
                    "lastFailureAt": now.isoformat(),
                    "consecutiveFailures": int(previous_source.get("consecutiveFailures") or 0) + 1,
                    "lastError": error,
                }
            continue

        final_url = metadata.get("finalUrl") or source.get("url")
        if not previous_source or previous_source.get("lastError") or previous_source.get("finalUrl") != final_url:
            source_state[source_id] = {
                **previous_source,
                "lastSuccess": now.isoformat(),
                "consecutiveFailures": 0,
                "lastError": "",
                "finalUrl": final_url,
            }

        if source.get("alertPolicy") == "snapshot":
            current_hash = metadata.get("hash") or ""
            previous_hash = previous_source.get("snapshotHash") or ""
            source_state[source_id]["snapshotHash"] = current_hash
            if previous_hash and current_hash and previous_hash != current_hash:
                text = str(metadata.get("text") or "")
                local = local_matches({"title": source.get("name"), "description": text, "url": source.get("url")}, terms)
                if local or not source.get("requiresLocalMatch"):
                    snapshot_alerts.append({
                        "title": f"Změna na zdroji: {source.get('name')}",
                        "url": source.get("url"),
                        "description": text[:1800],
                        "published": now.isoformat(),
                        "sourceName": source.get("name"),
                        "sourceId": source_id,
                        "category": source.get("category"),
                        "tier": source.get("tier"),
                        "priority": source.get("priority"),
                        "severity": "high" if int(source.get("priority") or 0) >= 90 else "medium",
                        "reason": "source_changed",
                        "localMatches": local,
                        "fingerprint": hashlib.sha256(f"snapshot|{source_id}|{current_hash}".encode()).hexdigest()[:20],
                    })
            continue

        parsed_total += len(items)
        for item in items:
            title = normalized_title(item.get("title"))
            if not meaningful_title(title, source):
                suppressed["genericTitle"] += 1
                continue
            url = canonical_url(item.get("url"))
            if not url_allowed(url, source):
                suppressed["excludedUrl"] += 1
                continue
            item = dict(item)
            item["title"] = title
            item["url"] = url
            local = local_matches(item, terms)
            if source.get("requiresLocalMatch") and not local:
                suppressed["missingLocalMatch"] += 1
                continue
            sev = severity(item, source)
            if source.get("alertPolicy") == "discovery" and mode != "daily":
                continue
            if source.get("alertPolicy") == "discovery" and sev == "medium":
                suppressed["discoveryNotImportant"] += 1
                continue
            candidate = {
                **item,
                "sourceName": source.get("name"),
                "sourceId": source_id,
                "category": source.get("category"),
                "tier": source.get("tier"),
                "priority": int(source.get("priority") or 0),
                "severity": sev,
                "reason": "new_item",
                "localMatches": local,
            }
            previous = candidates_by_url.get(url)
            if not previous or source_rank(source) > (
                0 if previous.get("tier") == "aggregator" else 1,
                int(previous.get("priority") or 0),
            ):
                if previous:
                    suppressed["duplicate"] += 1
                candidates_by_url[url] = candidate
            else:
                suppressed["duplicate"] += 1

    # Deduplikace stejného titulku mezi přímým zdrojem a agregátorem.
    for candidate in candidates_by_url.values():
        key = semantic_title_key(candidate.get("title"))
        previous = candidates_by_title.get(key)
        rank = (0 if candidate.get("tier") == "aggregator" else 1, int(candidate.get("priority") or 0))
        previous_rank = (
            0 if previous and previous.get("tier") == "aggregator" else 1,
            int(previous.get("priority") or 0) if previous else -1,
        )
        if previous is None or rank > previous_rank:
            candidates_by_title[key] = candidate
        else:
            suppressed["duplicate"] += 1

    candidates = sorted(
        candidates_by_title.values(),
        key=lambda x: (
            str(x.get("published") or ""),
            {"urgent": 3, "high": 2, "medium": 1}.get(str(x.get("severity")), 0),
            int(x.get("priority") or 0),
            str(x.get("title")),
        ),
        reverse=True,
    )

    alerts = list(snapshot_alerts)
    max_age = timedelta(hours=MODE_MAX_AGE[mode])
    bootstrap_age = timedelta(hours=MODE_BOOTSTRAP_AGE[mode])
    seen_this_run = set()

    for item in candidates:
        item_id = hashlib.sha256(f"url|{item.get('url')}".encode()).hexdigest()[:20]
        seen_this_run.add(item_id)
        previous = item_state.get(item_id) if isinstance(item_state.get(item_id), dict) else {}
        current_hash = content_hash(item)
        published = parse_datetime(item.get("published"))
        is_new = not bool(previous)
        changed = bool(previous) and previous.get("contentHash") != current_hash
        should_alert = False
        reason = "new_item"

        if is_new and not bootstrap:
            should_alert = True
        elif is_new and bootstrap and mode == "urgent" and published and published >= now - bootstrap_age:
            should_alert = True
        elif changed and previous.get("lastAlertedHash") != current_hash:
            # Aktualizace se hlásí jen u důležitých oficiálních či provozních zdrojů.
            if item.get("severity") in {"urgent", "high"} and item.get("tier") != "aggregator":
                should_alert = True
                reason = "updated_item"

        if should_alert and published and published < now - max_age:
            should_alert = False
            suppressed["stale"] += 1

        record = {
            "title": item.get("title"),
            "url": item.get("url"),
            "sourceName": item.get("sourceName"),
            "sourceId": item.get("sourceId"),
            "category": item.get("category"),
            "firstSeen": previous.get("firstSeen") or now.isoformat(),
            "lastSeen": (now.isoformat() if (is_new or changed) else previous.get("lastSeen") or previous.get("firstSeen") or now.isoformat()),
            "published": item.get("published") or "",
            "contentHash": current_hash,
            "lastAlertedHash": previous.get("lastAlertedHash") or "",
        }
        if should_alert:
            item["reason"] = reason
            item["fingerprint"] = hashlib.sha256(
                f"{reason}|{item_id}|{current_hash}".encode()
            ).hexdigest()[:20]
            alerts.append(item)
            record["lastAlertedHash"] = current_hash
            record["lastAlertedAt"] = now.isoformat()
        item_state[item_id] = record

    # Záznamy mimo aktuální výřez ponecháme, ale omezíme jejich počet.
    if len(item_state) > MAX_STATE_ITEMS:
        item_state = dict(sorted(
            item_state.items(),
            key=lambda pair: str((pair[1] or {}).get("lastSeen") or ""),
            reverse=True,
        )[:MAX_STATE_ITEMS])

    severity_rank = {"urgent": 3, "high": 2, "medium": 1}
    alerts = sorted(
        alerts,
        key=lambda x: (
            severity_rank.get(str(x.get("severity")), 0),
            int(x.get("priority") or 0),
            str(x.get("published") or ""),
        ),
        reverse=True,
    )
    max_alerts = MODE_MAX_ALERTS[mode]
    alerts_capped = len(alerts) > max_alerts
    alerts = alerts[:max_alerts]

    failures = [x for x in statuses if x.get("status") == "failed"]
    required_failures = [
        x for x in failures
        if next((s for s in sources if s.get("id") == x.get("id") and s.get("required")), None)
    ]
    status = {
        "version": 2,
        "mode": mode,
        "checkedAt": now.isoformat(),
        "bootstrap": bootstrap,
        "sourceCount": len(sources),
        "checkedSources": len(sources) - len(failures),
        "failedSources": len(failures),
        "requiredFailedSources": len(required_failures),
        "itemsParsed": parsed_total,
        "relevantItems": len(candidates),
        "newAlerts": len(alerts),
        "alertsCapped": alerts_capped,
        "suppressed": suppressed,
        "coverage": registry.get("coverage") or {},
        "sourceStatus": statuses,
    }
    state_payload = {
        "version": 2,
        "mode": mode,
        "items": item_state,
        "sources": source_state,
    }
    write_json(state_path, state_payload)
    write_stable_status(status_path, status)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"alerts": alerts, "status": status}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "sources": f"{status['checkedSources']}/{status['sourceCount']}",
        "requiredFailures": status["requiredFailedSources"],
        "parsed": parsed_total,
        "relevant": len(candidates),
        "alerts": len(alerts),
        "suppressed": suppressed,
        "bootstrap": bootstrap,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
