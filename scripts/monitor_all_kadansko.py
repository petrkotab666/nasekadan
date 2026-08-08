#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from monitor_national_kadan import collect, fold, normalize_url, parse_datetime, read_json, write_json
from update_city_news import load_sources

MAX_WORKERS = 12
MAX_SEEN = 16000
MAX_ALERTS_PER_RUN = 12

VOLATILE_QUERY_KEYS = {
    "tmstv", "timestamp", "tstamp", "cache", "nocache", "_", "rand",
    "ver", "version", "drawerurl", "cartdraweropened",
}
GENERIC_TITLES = {
    "číst více", "čtěte více", "zobrazit více", "více", "detail", "aktuality",
    "novinky", "program", "kalendář akcí", "úvod", "hlavní stránka", "domů",
    "kontakt", "kontakty", "menu", "facebook", "instagram", "přeskočit na obsah",
    "prezentace", "ústecký deník", "kolínský deník", "chomutovský deník",
}
GENERIC_PATTERNS = [
    re.compile(r"^(?:číst|čtěte|zobrazit|pokračovat)(?:\s+více)?$", re.I),
    re.compile(r"^(?:přeskočit na obsah|hlavní stránka|domů|úvod|menu|kontakt|kontakty)$", re.I),
    re.compile(r"^(?:prezentace|program|aktuality|novinky|kalendář akcí)$", re.I),
]
LOCAL_TERMS = {
    "kadan", "kadansko", "prunerov", "tusimice", "nechranice", "uhost",
    "uhostany", "pokutice", "bystrice u kadane", "mikulovice u kadane",
    "hradiste u kadane", "klasterec nad ohri", "elektrarna prunerov",
    "elektrarna tusimice", "doly nastup", "nemocnice kadan",
}
# Některé názvy obcí jsou zároveň běžná česká slova. U těchto názvů se
# nesmí použít prostá podřetězcová shoda, jinak vznikají falešné nálezy typu
# „na místo vyjeli hasiči“, „oprava mostu“ nebo „turistický ostrov“.
AMBIGUOUS_LOCAL_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "misto": (
        re.compile(r"\bobec\s+misto\b"),
        re.compile(r"\bmisto\s+u\s+chomutova\b"),
        re.compile(r"\bmisto\s+na\s+chomutovsku\b"),
        re.compile(r"\bv\s+obci\s+misto\b"),
    ),
    "most": (
        re.compile(r"\bmosteck\w*\b"),
        re.compile(r"\bmesto\s+most\b"),
        re.compile(r"\bokres\s+most\b"),
        re.compile(r"\bv\s+moste\b"),
        re.compile(r"\bz\s+mostu\b"),
        re.compile(r"\bdo\s+mostu\b"),
        re.compile(r"\bu\s+mostu\b"),
    ),
    "ostrov": (
        re.compile(r"\bostrovsk\w*\b"),
        re.compile(r"\bmesto\s+ostrov\b"),
        re.compile(r"\bostrov\s+nad\s+ohri\b"),
        re.compile(r"\bv\s+ostrove\b"),
        re.compile(r"\bz\s+ostrova\b"),
        re.compile(r"\bdo\s+ostrova\b"),
        re.compile(r"\bostrov\s+(?:opravi|otevre|postavi|vybuduje|schvalil|spusti|chysta|investuje|ziska|nabizi|vyhlasil|bude)\b"),
    ),
}
HIGH_SIGNAL_TERMS = {
    "pozar", "nehoda", "havarie", "evakuace", "vybuch", "zasah hasicu",
    "policie", "patrani", "pohresovan", "uzavirka", "neprujezd", "vyluka",
    "odstavka", "vypadek", "bez vody", "bez elektriny", "bez tepla",
    "omezeni provozu", "zmena provozu", "docasne uzavren", "zruseno",
    "zastupitelstv", "rada mesta", "usneseni", "uredni deska",
    "verejna vyhlaska", "verejna zakazka", "vyberove rizeni", "smlouva",
    "dodatek", "rozpocet", "ucetni zaverka", "vyrocni zprava", "dotace",
    "investice", "rekonstrukce", "stavebni povoleni", "uzemni plan", "eia",
    "konkurs", "reditel", "jednatel", "personalni zmena", "kontrola",
    "zapis ze zasedani", "zapis zastupitelstva", "zapis do skoly",
    "prijimaci rizeni", "prazdninovy provoz", "zmena ceny", "jideln",
    "druzina", "nemocnice", "ambulance",
}
URGENT_SIGNAL_TERMS = {
    "pozar", "nehoda", "havarie", "evakuace", "vybuch", "pohresovan",
    "uzavirka", "neprujezd", "odstavka", "vypadek", "bez vody",
    "bez elektriny", "bez tepla", "krizova", "vystraha",
}
BROAD_TIERS = {
    "regional_media", "national_media", "aggregator", "regional_authority",
    "transport", "utility", "emergency", "police",
}


def stable_url(value: object) -> str:
    url = normalize_url(value)
    if not url:
        return ""
    parsed = urlsplit(url)
    query = [
        (key, val) for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in VOLATILE_QUERY_KEYS
    ]
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parsed.scheme, parsed.netloc, path, urlencode(query, doseq=True), ""))


def infer_tier(source: dict[str, Any]) -> str:
    explicit = str(source.get("tier") or "").strip().lower()
    if explicit and explicit != "organization":
        return explicit
    text = fold(f"{source.get('name')} {source.get('category')}")
    if "google news" in text:
        return "aggregator"
    if "media" in text or "denik" in text or "rozhlas" in text or "noviny" in text:
        return "regional_media"
    if "policie" in text:
        return "police"
    if "hasic" in text or "zachranna sluzba" in text or "krizove" in text:
        return "emergency"
    if any(token in text for token in ("doprava", "zeleznic", "silnic", "jizdni rad")):
        return "transport"
    if any(token in text for token in ("elektrina", "voda", "teplo", "cez", "povodi")):
        return "utility"
    if "kraj" in text and "mesto" not in text:
        return "regional_authority"
    return "organization"


def title_quality(title: object, tier: str) -> int:
    raw = re.sub(r"\s+", " ", str(title or "")).strip(" \t\r\n-|•·")
    folded = fold(raw)
    if not folded or folded in GENERIC_TITLES:
        return -1000
    if len(raw) < 8 or len(raw) > 260:
        return -900
    if any(pattern.fullmatch(raw) for pattern in GENERIC_PATTERNS):
        return -800
    if re.search(r"\bstaženo\s+[\d\s.,]+[×x]\b", raw, re.I):
        raw = re.sub(r"\s*\(\s*staženo\s+[\d\s.,]+[×x]\s*\)\s*", " ", raw, flags=re.I).strip()
        folded = fold(raw)
    if tier in BROAD_TIERS and re.fullmatch(
        r"[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\wÁ-ž.-]+(?:\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\wÁ-ž.-]+){0,2}", raw
    ):
        return -700
    if any(token in folded for token in ("číst více", "zobrazit více", "pokračovat", "přeskočit na obsah")):
        return -600
    score = min(len(raw), 120)
    if len(raw.split()) >= 4:
        score += 20
    return score


def source_priority(source: dict[str, Any], tier: str) -> int:
    return {
        "municipality": 100,
        "organization": 90,
        "emergency": 100,
        "police": 100,
        "regional_authority": 88,
        "transport": 86,
        "utility": 86,
        "regional_media": 70,
        "national_media": 60,
        "aggregator": 30,
    }.get(tier, 60)


def local_matches(item: dict[str, Any]) -> list[str]:
    haystack = fold(" ".join([
        str(item.get("title") or ""),
        str(item.get("description") or ""),
        str(item.get("url") or ""),
    ]))
    matches: list[str] = []
    for term in sorted(LOCAL_TERMS):
        ambiguous_patterns = AMBIGUOUS_LOCAL_PATTERNS.get(term)
        if ambiguous_patterns is not None:
            if any(pattern.search(haystack) for pattern in ambiguous_patterns):
                matches.append(term)
            continue
        escaped = re.escape(term).replace(r"\ ", r"\s+")
        if re.search(rf"(?<!\w){escaped}\w*", haystack):
            matches.append(term)
    return matches


def signal_level(item: dict[str, Any], tier: str) -> str:
    # U běžných webů rozhoduje titulek. Okolní HTML často obsahuje názvy
    # sousedních položek a nesmí z očkování psů udělat požární poplach.
    title_text = fold(f"{item.get('title')} {item.get('category')}")
    if any(term in title_text for term in URGENT_SIGNAL_TERMS):
        return "urgent"
    if any(term in title_text for term in HIGH_SIGNAL_TERMS):
        return "high"
    # U specializovaných krizových, policejních, dopravních a síťových zdrojů
    # smí rozhodnout i popis, protože jejich titulky bývají krátké.
    if tier in {"emergency", "police", "transport", "utility"}:
        full_text = fold(f"{item.get('title')} {item.get('description')} {item.get('category')}")
        if any(term in full_text for term in URGENT_SIGNAL_TERMS):
            return "urgent"
        if any(term in full_text for term in HIGH_SIGNAL_TERMS):
            return "high"
    return "medium"


def fingerprint(item: dict[str, Any]) -> str:
    identity = stable_url(item.get("url")) or f"{item.get('sourceName')}|{fold(item.get('title'))}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]


def load_all_sources(extra_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_sources, coverage = load_sources()
    extra = read_json(extra_path)
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()

    for source in base_sources:
        source_url = str(source.get("url") or "").strip()
        dedup_key = stable_url(source_url)
        if not dedup_key or dedup_key in seen:
            continue
        seen.add(dedup_key)
        tier = infer_tier(source)
        # Deduplikace používá stabilní klíč, HTTP požadavek ale musí dostat
        # přesnou adresu z registru. Některé servery rozlišují /news a /news/.
        merged.append({**source, "url": source_url, "kind": source.get("kind") or "html", "tier": tier})

    for source in extra.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_url = str(source.get("url") or "").strip()
        dedup_key = stable_url(source_url)
        if not dedup_key or dedup_key in seen:
            continue
        seen.add(dedup_key)
        tier = infer_tier(source)
        merged.append({**source, "url": source_url, "tier": tier})

    coverage = {
        **coverage,
        "extraSources": max(0, len(merged) - int(coverage.get("totalUniqueSources") or 0)),
        "completeSourceCount": len(merged),
        "scopeMunicipalities": (extra.get("scope") or {}).get("municipalities", []),
    }
    return merged, coverage


def fresh_enough(item: dict[str, Any], tier: str, now: datetime) -> bool:
    published = parse_datetime(item.get("published"))
    if not published:
        return False
    max_age = timedelta(hours=72 if tier in {"emergency", "police", "transport", "utility"} else 24 * 14)
    return published >= now - max_age and published <= now + timedelta(hours=6)


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
    if coverage.get("monitoredDirectoryOrganizations") != coverage.get("directoryOrganizations"):
        raise SystemExit(f"Neúplné pokrytí kanonického adresáře: {coverage}")

    state = read_json(state_path)
    seen = state.get("seen") if isinstance(state.get("seen"), dict) else {}
    bootstrap = not bool(seen)
    now = datetime.now(timezone.utc)

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(sources))) as executor:
        collected = list(executor.map(collect, sources))

    # MONITOR_SECOND_PASS_V2
    # Po prvním paralelním průchodu ještě jednou pomalu zkusit pouze selhané
    # zdroje. Tím se jednorázový timeout/503 nestane falešným výpadkem celého
    # monitoringu a současně nezpomalujeme zdroje, které fungují napoprvé.
    initial_failed = sum(1 for _source, _items, error in collected if error)
    failed_indexes = [index for index, (_source, _items, error) in enumerate(collected) if error]
    if failed_indexes:
        time.sleep(2.0)
        for index in failed_indexes:
            source, old_items, old_error = collected[index]
            retried = collect(source)
            _source, new_items, new_error = retried
            if not new_error or len(new_items) > len(old_items):
                collected[index] = retried
            else:
                collected[index] = (source, old_items, f"{old_error}; retry: {new_error}")
    recovered_after_retry = initial_failed - sum(1 for _source, _items, error in collected if error)

    source_status: list[dict[str, Any]] = []
    parsed_total = 0
    by_url: dict[str, dict[str, Any]] = {}
    suppressed = {
        "genericTitle": 0,
        "missingUrl": 0,
        "broadWithoutLocalMatch": 0,
        "notEditoriallySignificant": 0,
        "notFreshOrUndated": 0,
        "duplicate": 0,
        "deferredByCap": 0,
    }

    for source, items, error in collected:
        tier = infer_tier(source)
        parsed_total += len(items)
        source_status.append({
            "name": source.get("name"),
            "url": source.get("url"),
            "category": source.get("category"),
            "tier": tier,
            "status": "failed" if error else "checked",
            "itemsParsed": len(items),
            **({"error": error} if error else {}),
        })
        for item in items:
            title = re.sub(r"\s+", " ", str(item.get("title") or "")).strip()
            quality = title_quality(title, tier)
            if quality < 0:
                suppressed["genericTitle"] += 1
                continue
            url = stable_url(item.get("url"))
            if not url:
                suppressed["missingUrl"] += 1
                continue
            candidate = dict(item)
            candidate.update({
                "title": re.sub(r"\s*\(\s*staženo\s+[\d\s.,]+[×x]\s*\)\s*", "", title, flags=re.I).strip(),
                "url": url,
                "sourceName": source.get("name"),
                "sourceUrl": source.get("url"),
                "category": source.get("category"),
                "tier": tier,
                "quality": quality,
                "sourcePriority": source_priority(source, tier),
            })
            candidate["localMatches"] = local_matches(candidate)
            candidate["severity"] = signal_level(candidate, tier)
            previous = by_url.get(url)
            if not previous or (
                candidate["sourcePriority"], candidate["quality"], len(str(candidate.get("description") or ""))
            ) > (
                previous["sourcePriority"], previous["quality"], len(str(previous.get("description") or ""))
            ):
                if previous:
                    suppressed["duplicate"] += 1
                by_url[url] = candidate
            else:
                suppressed["duplicate"] += 1

    candidates = sorted(
        by_url.values(),
        key=lambda item: (
            str(item.get("published") or ""),
            int(item.get("sourcePriority") or 0),
            str(item.get("title") or ""),
        ),
        reverse=True,
    )

    alerts: list[dict[str, Any]] = []
    for item in candidates:
        fp = fingerprint(item)
        item["fingerprint"] = fp
        is_new = fp not in seen
        tier = str(item.get("tier") or "")
        if is_new and not bootstrap:
            if tier in BROAD_TIERS and not item.get("localMatches"):
                suppressed["broadWithoutLocalMatch"] += 1
            elif str(item.get("severity")) not in {"urgent", "high"}:
                suppressed["notEditoriallySignificant"] += 1
            elif not fresh_enough(item, tier, now):
                suppressed["notFreshOrUndated"] += 1
            elif len(alerts) < MAX_ALERTS_PER_RUN:
                alerts.append(item)
            else:
                suppressed["deferredByCap"] += 1
                continue
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
        "version": 3,
        "checkedAt": now.isoformat(),
        "bootstrap": bootstrap,
        "sourceCount": len(sources),
        "checkedSources": len(sources) - len(failed),
        "failedSources": len(failed),
        "initialFailedSources": initial_failed,
        "recoveredSourcesAfterRetry": recovered_after_retry,
        "itemsParsed": parsed_total,
        "uniqueItems": len(candidates),
        "newAlerts": len(alerts),
        "alertsCapped": suppressed["deferredByCap"] > 0,
        "suppressed": suppressed,
        "coverage": coverage,
        "sourceStatus": source_status,
    }
    write_json(state_path, {"version": 3, "lastRunAt": now.isoformat(), "seen": seen})
    write_json(status_path, status)
    write_json(output_path, {"alerts": alerts, "status": status})
    print(json.dumps({
        "ok": True,
        "sources": f"{status['checkedSources']}/{status['sourceCount']}",
        "parsed": parsed_total,
        "unique": len(candidates),
        "alerts": len(alerts),
        "deferred": suppressed["deferredByCap"],
        "suppressed": suppressed,
        "bootstrap": bootstrap,
        "organizations": coverage.get("monitoredDirectoryOrganizations"),
        "municipalities": len(coverage.get("scopeMunicipalities") or []),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
