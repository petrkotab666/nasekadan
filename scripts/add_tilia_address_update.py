#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEWS_PATH = ROOT / "data" / "city-news.json"

ITEM = {
    "id": "tilia-kadan-postovni-953-20260730",
    "title": "TILIA Kadaň přesunula poradenská pracoviště na Poštovní 953",
    "date": "2026-07-30",
    "category": "Sociální a poradenské služby",
    "description": (
        "Sídlo organizace, Poradna pro rodinu a mezilidské vztahy a Sociální centrum – "
        "odborné sociální poradenství jsou na adrese Poštovní 953. Sociálně aktivizační "
        "služba pro rodiny s dětmi má v Kadani dál samostatné pracoviště v ulici Jana Švermy 5."
    ),
    "source": "https://tiliakadan.cz/kontakty/",
    "sourceName": "TILIA Kadaň, z. s.",
}


def main() -> None:
    data = json.loads(NEWS_PATH.read_text(encoding="utf-8"))
    items = data.get("items")
    if not isinstance(items, list):
        raise SystemExit("data/city-news.json neobsahuje platné pole items")

    items = [item for item in items if item.get("id") != ITEM["id"]]
    items.insert(0, ITEM)
    data["items"] = items[:100]

    sources = data.get("sources")
    if not isinstance(sources, list):
        sources = []
    for source in (
        "TILIA Kadaň, z. s. (praktická změna adresy)",
        "TILIA Kadaň – kontakty a pracoviště (ověřeno)",
    ):
        if source not in sources:
            sources.append(source)
    data["sources"] = sources
    data["generatedAt"] = datetime.now(timezone.utc).isoformat()

    NEWS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    check = json.loads(NEWS_PATH.read_text(encoding="utf-8"))
    first = check["items"][0]
    if first.get("id") != ITEM["id"] or "Poštovní 953" not in first.get("description", ""):
        raise SystemExit("Kontrola vloženého oznámení selhala")
    print("Oznámení TILIA Kadaň bylo vloženo do veřejného přehledu.")


if __name__ == "__main__":
    main()
