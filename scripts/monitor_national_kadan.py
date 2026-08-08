#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import http.client
import json
import random
import re
import socket
import subprocess
import threading
import time
import unicodedata
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

UA = "NaseKadanNationalMonitor/1.2 (+https://nasekadan.cz; info@nasekadan.cz)"
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
MAX_WORKERS = 8
MAX_ITEMS_PER_SOURCE = 120
MAX_SEEN = 5000
TRACKING_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "yclid", "mc_cid", "mc_eid",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean(value: object) -> str:
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", str(value or ""), flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def fold(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value).lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text).strip()


def normalize_url(value: object, base: str = "") -> str:
    raw = str(value or "").strip()
    if base:
        raw = urljoin(base, raw)
    parsed = urlsplit(raw)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return ""
    query = [(key, val) for key, val in parse_qsl(parsed.query, keep_blank_values=True) if key.lower() not in TRACKING_KEYS]
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, urlencode(query, doseq=True), ""))


# MONITOR_RELIABLE_FETCH_V2
_TRANSIENT_HTTP_CODES = {403, 406, 408, 425, 429, 500, 502, 503, 504}
_HOST_SEMAPHORES: dict[str, threading.Semaphore] = {
    # Google News při desítkách RSS dotazů vrací dočasné 503. Dva souběžné
    # požadavky udrží průchod rychlý, ale neodpálí throttling.
    "news.google.com": threading.Semaphore(2),
}


def _request(url: str, user_agent: str, timeout: int = 45) -> tuple[str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, text/html, application/xhtml+xml",
            "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.6",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get_content_type() or ""
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace"), content_type


def fetch(url: str) -> tuple[str, str]:
    host = urlsplit(url).netloc.lower().split(':', 1)[0]
    attempts = 5 if host == "news.google.com" else 3
    semaphore = _HOST_SEMAPHORES.get(host)
    last_exc: Exception | None = None

    for attempt in range(attempts):
        acquired = False
        try:
            if semaphore is not None:
                semaphore.acquire()
                acquired = True
                # Rozprostřít RSS dotazy i v rámci dvojice workerů.
                time.sleep(0.25 + random.random() * 0.35)
            ua = UA if attempt == 0 else BROWSER_UA
            timeout = 45 if attempt < 2 else 60
            return _request(url, ua, timeout=timeout)
        except HTTPError as exc:
            last_exc = exc
            if exc.code not in _TRANSIENT_HTTP_CODES:
                raise
            retry_after = 0.0
            try:
                retry_after = float(exc.headers.get('Retry-After') or 0)
            except (TypeError, ValueError):
                retry_after = 0.0
        except (URLError, TimeoutError, socket.timeout, ConnectionError,
                ConnectionResetError, http.client.IncompleteRead, OSError) as exc:
            last_exc = exc
            retry_after = 0.0
        finally:
            if acquired and semaphore is not None:
                semaphore.release()

        if attempt + 1 < attempts:
            backoff = max(retry_after, min(12.0, 1.2 * (2 ** attempt)))
            time.sleep(backoff + random.random() * 0.6)

    # MONITOR_CURL_FALLBACK_V1
    # Některé veřejné weby odmítají urllib, ale běžný HTTP klient obslouží.
    # Curl je až poslední možnost a nepoužívá se pro trvalé 404.
    if not (isinstance(last_exc, HTTPError) and last_exc.code == 404):
        try:
            proc = subprocess.run([
                "curl", "-fsSL", "--compressed", "--max-time", "70",
                "--retry", "2", "--retry-delay", "2", "--retry-all-errors",
                "-A", BROWSER_UA,
                "-H", "Accept-Language: cs-CZ,cs;q=0.9,en;q=0.6",
                "-H", "Accept: application/rss+xml,application/atom+xml,application/xml,text/xml,text/html,application/xhtml+xml,*/*;q=0.8",
                url,
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            body = proc.stdout.decode("utf-8", errors="replace")
            if body.strip():
                stripped=body.lstrip().lower()
                content_type = "application/xml" if stripped.startswith("<?xml") or stripped.startswith("<rss") or stripped.startswith("<feed") else "text/html"
                return body, content_type
        except Exception:
            pass
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"Nepodařilo se načíst {url}")


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
    first = re.search(r"\b(20\d{2})[-./](\d{1,2})[-./](\d{1,2})(?:[ T](\d{1,2}):(\d{2}))?\b", raw)
    if first:
        year, month, day = map(int, first.group(1, 2, 3))
        hour = int(first.group(4) or 0)
        minute = int(first.group(5) or 0)
        try:
            return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
        except ValueError:
            return None
    second = re.search(r"\b(\d{1,2})[. /](\d{1,2})[. /](20\d{2})(?:\s+(\d{1,2}):(\d{2}))?\b", raw)
    if second:
        day, month, year = map(int, second.group(1, 2, 3))
        hour = int(second.group(4) or 0)
        minute = int(second.group(5) or 0)
        try:
            return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def node_text(node: ET.Element, names: set[str]) -> str:
    for child in node.iter():
        if local_name(child.tag) in names and clean(child.text):
            return clean("".join(child.itertext()))
    return ""


def rss_link(node: ET.Element) -> str:
    for child in node.iter():
        if local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        if href:
            return href
        if clean(child.text):
            return clean(child.text)
    return ""


def parse_rss(page: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    root = ET.fromstring(page)
    nodes = [node for node in root.iter() if local_name(node.tag) in {"item", "entry"}]
    output: list[dict[str, Any]] = []
    for node in nodes[:MAX_ITEMS_PER_SOURCE]:
        title = node_text(node, {"title"})
        url = normalize_url(rss_link(node), str(source["url"]))
        description = node_text(node, {"description", "summary", "content", "encoded"})
        published_raw = node_text(node, {"pubdate", "published", "updated", "date"})
        published = parse_datetime(published_raw)
        if title and url:
            output.append({
                "title": title[:300],
                "url": url,
                "description": description[:1000],
                "published": published.isoformat() if published else "",
            })
    return output


def parse_html(page: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    matches = list(re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.I | re.S))
    for match in matches[:1000]:
        title = clean(match.group(2))
        if len(title) < 8 or len(title) > 300:
            continue
        url = normalize_url(match.group(1), str(source["url"]))
        if not url or url == normalize_url(source["url"]):
            continue
        # Bereme jen text od odkazu směrem dopředu. Text před odkazem často patří
        # sousední zprávě a vytvářel falešné shody na slovo Kadaň.
        around_raw = page[match.start(): min(len(page), match.end() + 650)]
        around = clean(around_raw)
        published = None
        datetime_match = re.search(r'<time\b[^>]*datetime=["\']([^"\']+)', around_raw, re.I)
        if datetime_match:
            published = parse_datetime(datetime_match.group(1))
        if not published:
            published = parse_datetime(around)
        description = around.replace(title, "", 1).strip(" -|·")[:1000]
        output.append({
            "title": title,
            "url": url,
            "description": description,
            "published": published.isoformat() if published else "",
        })
    return output


def collect(source: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    try:
        page, content_type = fetch(str(source["url"]))
        kind = str(source.get("kind") or "html").lower()
        if kind == "rss" or "xml" in content_type or page.lstrip().startswith("<?xml"):
            parsed = parse_rss(page, source)
        else:
            parsed = parse_html(page, source)
        return source, parsed, ""
    except Exception as exc:
        return source, [], f"{type(exc).__name__}: {exc}"


def item_fingerprint(item: dict[str, Any]) -> str:
    identity = normalize_url(item.get("url")) or f"{item.get('sourceName')}|{item.get('title')}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]


def relevance(item: dict[str, Any], terms: list[str]) -> list[str]:
    haystack = fold(" ".join([
        str(item.get("title") or ""),
        str(item.get("description") or ""),
        str(item.get("url") or ""),
    ]))
    return sorted({term for term in terms if term and term in haystack})


def ignored_by_policy(item: dict[str, Any], patterns: list[re.Pattern[str]], current_year: int) -> bool:
    if str(item.get("tier") or "") != "national_media":
        return False
    title = fold(item.get("title"))
    if any(pattern.search(title) for pattern in patterns):
        return True
    years = {int(value) for value in re.findall(r"\b20\d{2}\b", title)}
    if years and max(years) < current_year - 1:
        return True
    return False


def severity_for(tier: str) -> str:
    if tier in {"government", "ministry", "parliament", "regulator", "fund"}:
        return "high"
    return "medium"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="data/national-kadan-sources.json")
    parser.add_argument("--state", default="data/national-kadan-monitoring-state.json")
    parser.add_argument("--status", default="data/national-kadan-monitoring-status.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config_path = Path(args.config)
    state_path = Path(args.state)
    status_path = Path(args.status)
    output_path = Path(args.output)

    config = read_json(config_path)
    sources = [source for source in config.get("sources", []) if isinstance(source, dict)]
    if len(sources) < 20:
        raise SystemExit(f"Konfigurace obsahuje jen {len(sources)} zdrojů; očekáváno nejméně 20.")
    normalized_terms = sorted({fold(term) for term in config.get("relevanceTerms", []) if fold(term)}, key=len, reverse=True)
    if not any(term == "kadan" for term in normalized_terms):
        raise SystemExit("Konfigurace neobsahuje základní relevanční výraz Kadaň.")
    exclude_patterns = [
        re.compile(str(pattern), re.I)
        for pattern in config.get("nationalMediaExcludePatterns", [])
        if str(pattern).strip()
    ]

    now = datetime.now(timezone.utc)
    bootstrap_hours = max(1, int(config.get("bootstrapHours") or 72))
    national_media_max_alert_age_days = max(1, int(config.get("nationalMediaMaxAlertAgeDays") or 14))
    state = read_json(state_path)
    seen = state.get("seen") if isinstance(state.get("seen"), dict) else {}
    bootstrap = not bool(seen)

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(sources))) as executor:
        collected = list(executor.map(collect, sources))

    source_status: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    ignored_items = 0
    for source, parsed, error in collected:
        status = {
            "name": source.get("name"),
            "url": source.get("url"),
            "tier": source.get("tier"),
            "category": source.get("category"),
            "status": "failed" if error else "checked",
            "itemsParsed": len(parsed),
        }
        if error:
            status["error"] = error
        source_status.append(status)
        for item in parsed:
            item.update({
                "sourceName": source.get("name"),
                "sourceUrl": source.get("url"),
                "tier": source.get("tier"),
                "category": source.get("category"),
            })
            if ignored_by_policy(item, exclude_patterns, now.year):
                ignored_items += 1
                continue
            matched = relevance(item, normalized_terms)
            if not matched:
                continue
            item["matchedTerms"] = matched
            item["fingerprint"] = item_fingerprint(item)
            item["severity"] = severity_for(str(source.get("tier") or ""))
            candidates.append(item)

    unique: dict[str, dict[str, Any]] = {}
    for item in candidates:
        fingerprint = str(item["fingerprint"])
        previous = unique.get(fingerprint)
        if not previous or len(str(item.get("description") or "")) > len(str(previous.get("description") or "")):
            unique[fingerprint] = item

    relevant_items = sorted(
        unique.values(),
        key=lambda item: (str(item.get("published") or ""), str(item.get("title") or "")),
        reverse=True,
    )
    alerts: list[dict[str, Any]] = []
    stale_alerts_suppressed = 0
    for item in relevant_items:
        fingerprint = str(item["fingerprint"])
        is_new = fingerprint not in seen
        should_alert = is_new and not bootstrap
        published = parse_datetime(item.get("published"))
        if is_new and bootstrap and published and published >= now - timedelta(hours=bootstrap_hours):
            should_alert = True
        if (
            should_alert
            and str(item.get("tier") or "") == "national_media"
            and (not published or published < now - timedelta(days=national_media_max_alert_age_days))
        ):
            should_alert = False
            stale_alerts_suppressed += 1
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
        ordered_seen = sorted(
            seen.items(),
            key=lambda pair: str((pair[1] or {}).get("lastSeen") or ""),
            reverse=True,
        )[:MAX_SEEN]
        seen = dict(ordered_seen)

    failed = [item for item in source_status if item["status"] == "failed"]
    state_out = {
        "version": 1,
        "lastRunAt": now.isoformat(),
        "seen": seen,
    }
    status_out = {
        "version": 1,
        "checkedAt": now.isoformat(),
        "bootstrap": bootstrap,
        "sourceCount": len(sources),
        "checkedSources": len(sources) - len(failed),
        "failedSources": len(failed),
        "relevantItems": len(relevant_items),
        "ignoredItems": ignored_items,
        "staleAlertsSuppressed": stale_alerts_suppressed,
        "newAlerts": len(alerts),
        "sourceStatus": source_status,
    }
    output = {
        "generatedAt": now.isoformat(),
        "bootstrap": bootstrap,
        "sourceCount": len(sources),
        "failedSources": len(failed),
        "ignoredItems": ignored_items,
        "staleAlertsSuppressed": stale_alerts_suppressed,
        "alerts": alerts,
        "matches": relevant_items[:100],
    }
    write_json(state_path, state_out)
    write_json(status_path, status_out)
    write_json(output_path, output)
    print(json.dumps({
        "ok": True,
        "bootstrap": bootstrap,
        "sources": len(sources),
        "failed": len(failed),
        "matches": len(relevant_items),
        "ignored": ignored_items,
        "staleSuppressed": stale_alerts_suppressed,
        "alerts": len(alerts),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
