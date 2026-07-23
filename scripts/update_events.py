#!/usr/bin/env python3
"""Aktualizuje veřejný kalendář akcí Naše Kadaň.

Používá jen veřejně dostupné stránky. Zachovává odkaz na zdroj, slučuje duplicity
podle názvu/data/místa a při chybě zdroje ponechá poslední ověřená data.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "events-seed.json"
OUTPUT = ROOT / "data" / "events.json"
USER_AGENT = "NaseKadanBot/1.0 (+https://nasekadan.cz; info@nasekadan.cz)"

SOURCES = [
    {"name": "Kino Hvězda Kadaň", "url": "https://www.kinokadan.cz/cely-program", "kind": "jsonld", "category": "Kino"},
    {"name": "Městská knihovna Kadaň", "url": "https://www.knihovnakadan.cz/", "kind": "library", "category": "Knihovna"},
    {"name": "e-region – Kadaň", "url": "https://www.e-region.cz/akce/mesto-kadan", "kind": "eregion", "category": "Akce"},
    {"name": "RADKA Kadaň", "url": "https://radka.kadan.cz/uvodni-stranka/pripravujeme/", "kind": "radka", "category": "Komunitní"},
]


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "cs,en;q=0.7"})
    with urlopen(req, timeout=25) as response:
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")[:80]


def normalize_event(event: dict, source: dict) -> dict | None:
    title = clean(str(event.get("title") or event.get("name") or ""))
    start = str(event.get("start") or event.get("startDate") or "").strip()
    if not title or not start:
        return None
    place = clean(str(event.get("place") or event.get("location") or "Kadaň"))
    description = clean(str(event.get("description") or ""))[:900]
    date_key = start[:10]
    raw_key = f"{title}|{date_key}|{place}".lower()
    identifier = event.get("id") or f"{slug(title)}-{date_key}-{hashlib.sha1(raw_key.encode()).hexdigest()[:7]}"
    return {
        "id": identifier,
        "title": title,
        "start": start,
        **({"end": event["end"]} if event.get("end") else {}),
        "time": clean(str(event.get("time") or "")),
        "place": place,
        "category": clean(str(event.get("category") or source["category"])),
        "description": description,
        "price": clean(str(event.get("price") or "")),
        "image": str(event.get("image") or ""),
        "source": str(event.get("source") or source["url"]),
        "sourceName": str(event.get("sourceName") or source["name"]),
        "verified": bool(event.get("verified", True)),
    }


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def parse_jsonld(page: str, source: dict) -> list[dict]:
    found: list[dict] = []
    for raw in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', page, re.I | re.S):
        try:
            data = json.loads(html.unescape(raw).strip())
        except Exception:
            continue
        for item in walk_json(data):
            item_type = item.get("@type")
            types = item_type if isinstance(item_type, list) else [item_type]
            if not any(t in {"Event", "Movie", "ScreeningEvent", "Festival"} for t in types):
                continue
            location = item.get("location") or {}
            if isinstance(location, dict):
                address = location.get("address") or {}
                place = location.get("name") or (address.get("streetAddress") if isinstance(address, dict) else "")
            else:
                place = str(location)
            image = item.get("image")
            if isinstance(image, list):
                image = image[0] if image else ""
            found.append({
                "name": item.get("name"),
                "startDate": item.get("startDate") or item.get("datePublished"),
                "end": item.get("endDate"),
                "location": place or "Kino Hvězda Kadaň",
                "description": item.get("description", ""),
                "image": image or "",
                "source": item.get("url") or source["url"],
                "category": source["category"],
            })
    return found


def parse_library(page: str, source: dict) -> list[dict]:
    # Knihovna často publikuje karty bez jednotného JSON-LD. Přebíráme jen karty,
    # u kterých je v okolním HTML nalezen datum; jinak je nezveřejníme automaticky.
    events = []
    pattern = re.compile(r'href=["\']([^"\']+)["\'][^>]*>.*?<h[2-6][^>]*>(.*?)</h[2-6]>(.{0,1200})', re.I | re.S)
    for href, title, tail in pattern.findall(page):
        date_match = re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(20\d{2})', clean(tail))
        if not date_match:
            continue
        day, month, year = map(int, date_match.groups())
        events.append({
            "title": clean(title),
            "start": f"{year:04d}-{month:02d}-{day:02d}",
            "place": "Městská knihovna Kadaň",
            "description": clean(tail)[:420],
            "source": href if href.startswith("http") else "https://www.knihovnakadan.cz" + href,
            "category": "Knihovna",
        })
    return events


def parse_eregion(page: str, source: dict) -> list[dict]:
    text = clean(page)
    events = []
    # Konzervativní parser: vyžaduje rok, název a zmínku Kadaně v bloku.
    for match in re.finditer(r'od\s+(\d{1,2})\.(\d{1,2})\.(20\d{2}).{0,120}?do\s+(\d{1,2})\.(\d{1,2})\.(20\d{2}).{0,30}?([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][^|]{3,100})', text, re.I):
        d1, m1, y1, d2, m2, y2, title = match.groups()
        events.append({"title": clean(title), "start": f"{y1}-{int(m1):02d}-{int(d1):02d}", "end": f"{y2}-{int(m2):02d}-{int(d2):02d}", "place": "Kadaň", "category": "Akce", "source": source["url"]})
    return events


def parse_radka(page: str, source: dict) -> list[dict]:
    # Publikujeme pouze jasně datované jednotlivé akce, nikoli aktivity „dle domluvy“.
    text = clean(page)
    events = []
    for title, d1, m1, d2, m2, year in re.findall(r'([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][^\.]{4,100}?)\s+(\d{1,2})\.\s*-\s*(\d{1,2})\.(\d{1,2})\.\s*(20\d{2})', text):
        # Starší varianta regexu; ponecháno pro kompatibilitu, pokud zdroj změní zápis.
        pass
    # Jednodenní i rozsah DD.MM. - DD.MM. YYYY
    for match in re.finditer(r'([^.!?]{5,100}?)\s+(\d{1,2})\.(\d{1,2})\.\s*-\s*(\d{1,2})\.(\d{1,2})\.\s*(20\d{2})', text):
        title, d1, m1, d2, m2, year = match.groups()
        events.append({"title": clean(title)[-90:], "start": f"{year}-{int(m1):02d}-{int(d1):02d}", "end": f"{year}-{int(m2):02d}-{int(d2):02d}", "place": "RADKA / dle pořadatele", "category": "Komunitní", "source": source["url"]})
    return events


def load_seed() -> list[dict]:
    try:
        return json.loads(SEED.read_text(encoding="utf-8")).get("events", [])
    except Exception:
        return []


def main() -> int:
    events = []
    used_sources = ["seed"]
    for item in load_seed():
        normalized = normalize_event(item, {"name": item.get("sourceName", "Ověřený zdroj"), "url": item.get("source", ""), "category": item.get("category", "Akce")})
        if normalized:
            events.append(normalized)

    parsers = {"jsonld": parse_jsonld, "library": parse_library, "eregion": parse_eregion, "radka": parse_radka}
    errors = []
    for source in SOURCES:
        try:
            page = fetch(source["url"])
            parsed = parsers[source["kind"]](page, source)
            count = 0
            for item in parsed:
                normalized = normalize_event(item, source)
                if normalized:
                    events.append(normalized)
                    count += 1
            used_sources.append(f"{source['name']} ({count})")
        except Exception as exc:
            errors.append(f"{source['name']}: {exc}")

    unique = {}
    for event in events:
        key = (slug(event["title"]), event["start"][:10], slug(event.get("place", "")))
        current = unique.get(key)
        # Ručně ověřený seed má přednost, jinak delší popis.
        if current is None or (event.get("verified") and not current.get("verified")) or len(event.get("description", "")) > len(current.get("description", "")):
            unique[key] = event

    result = sorted(unique.values(), key=lambda e: e["start"])
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": used_sources,
        "errors": errors,
        "events": result,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(OUTPUT)
    print(f"Uloženo {len(result)} akcí do {OUTPUT}")
    if errors:
        print("Některé zdroje selhaly:", *errors, sep="\n- ", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
