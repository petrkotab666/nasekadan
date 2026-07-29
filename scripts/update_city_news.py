#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "city-news.json"
SOURCES_FILE = ROOT / "data" / "city-sources.json"
UA = "NaseKadanBot/1.2 (+https://nasekadan.cz; info@nasekadan.cz)"
MIN_SAFE_ITEMS = 3


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
        if not url.startswith("http") or url == source["url"]:
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


def read_previous() -> dict:
    if not OUT.exists():
        return {}
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> None:
    config = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    previous = read_previous()
    items: list[dict[str, str]] = []
    errors: list[str] = []
    used: list[str] = []

    for source in config.get("sources", []):
        try:
            parsed = parse(fetch(source["url"]), source)
            items.extend(parsed)
            used.append(f"{source['name']} ({len(parsed)})")
        except Exception as exc:  # jednotlivý výpadek zdroje nesmí shodit celý přehled
            errors.append(f"{source['name']}: {type(exc).__name__}: {exc}")

    unique: dict[tuple[str, str], dict[str, str]] = {}
    for item in items:
        key = (item["title"].lower(), item["source"])
        if key not in unique or len(item["description"]) > len(unique[key]["description"]):
            unique[key] = item

    result = sorted(
        unique.values(), key=lambda item: (item.get("date") or "0000-00-00", item["title"]), reverse=True
    )[:100]

    previous_items = previous.get("items") if isinstance(previous.get("items"), list) else []
    if len(result) < MIN_SAFE_ITEMS and previous_items:
        print(
            f"Nový sběr vrátil jen {len(result)} položek; zachovávám posledních "
            f"{len(previous_items)} bezpečně uložených položek."
        )
        return
    if len(result) < MIN_SAFE_ITEMS:
        raise SystemExit(f"Sběr vrátil jen {len(result)} položek a není dostupná bezpečná záloha.")

    comparable_previous = {
        "sources": previous.get("sources", []),
        "errors": previous.get("errors", []),
        "items": previous_items,
    }
    comparable_new = {"sources": used, "errors": errors, "items": result}
    if comparable_previous == comparable_new:
        print(f"Beze změny: zůstává {len(result)} položek.")
        return

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": used,
        "errors": errors,
        "items": result,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(OUT)
    print(f"Uloženo {len(result)} městských novinek a odkazů; chyb zdrojů: {len(errors)}.")


if __name__ == "__main__":
    main()
