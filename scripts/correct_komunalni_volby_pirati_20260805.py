#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RSS = ROOT / "rss.xml"

ELECTION_URL = "https://nasekadan.cz/clanky/komunalni-volby-kadan-kandidaty-lhuta-2026.html"
ELECTION_DESC = (
    "Podávání kandidátek do komunálních voleb skončilo. ODS a Dáme Kadani novou šanci "
    "zveřejnily sestavy, ANO oznámilo podání a další kandidátku tvoří nezávislí s podporou Pirátů."
)
JEZERO_URL = "https://nasekadan.cz/clanky/jezero-most-patrani-dva-lide-bourka-2026.html"
JEZERO_DESC = (
    "Policie podle CNN Prima NEWS a Mosteckého deníku pátrá po dvou lidech na jezeře Most. "
    "Silná bouřka jim měla zabránit v návratu na břeh. K jezeru jezdí také lidé z Kadaně."
)


def item_link(block: str) -> str:
    match = re.search(r"<link>(.*?)</link>", block, flags=re.S)
    return match.group(1).strip() if match else ""


def set_description(block: str, description: str) -> str:
    replacement = f"<description><![CDATA[{description}]]></description>"
    patterns = (
        r"<description><!\[CDATA\[.*?\]\]></description>",
        r"<description>.*?</description>",
    )
    for pattern in patterns:
        if re.search(pattern, block, flags=re.S):
            return re.sub(pattern, replacement, block, count=1, flags=re.S)
    raise RuntimeError(f"Položka RSS nemá popis: {item_link(block)}")


def set_correction_category(block: str, enabled: bool) -> str:
    block = re.sub(r"\s*<category>Oprava</category>", "", block)
    if enabled:
        block = re.sub(r"\s*</item>\s*$", "\n      <category>Oprava</category>\n    </item>", block, count=1)
    return block


def main() -> int:
    text = RSS.read_text(encoding="utf-8")
    matches = list(re.finditer(r"<item>.*?</item>", text, flags=re.S))
    if not matches:
        raise RuntimeError("RSS neobsahuje žádné položky.")

    counts = {ELECTION_URL: 0, JEZERO_URL: 0}
    parts: list[str] = []
    cursor = 0
    for match in matches:
        parts.append(text[cursor:match.start()])
        block = match.group(0)
        link = item_link(block)
        if link == ELECTION_URL:
            counts[ELECTION_URL] += 1
            block = set_description(block, ELECTION_DESC)
            block = set_correction_category(block, True)
        elif link == JEZERO_URL:
            counts[JEZERO_URL] += 1
            block = set_description(block, JEZERO_DESC)
            block = set_correction_category(block, False)
        parts.append(block)
        cursor = match.end()
    parts.append(text[cursor:])

    if counts != {ELECTION_URL: 1, JEZERO_URL: 1}:
        raise RuntimeError(f"Neočekávaný počet cílových položek RSS: {counts}")

    repaired = "".join(parts)
    RSS.write_text(repaired, encoding="utf-8", newline="\n")

    root = ET.parse(RSS).getroot()
    items = root.findall("./channel/item")
    links = [node.findtext("link") or "" for node in items]
    if len(items) != 50 or len(links) != len(set(links)):
        raise RuntimeError("RSS nemá přesně 50 unikátních položek.")
    if not links or links[0] != JEZERO_URL:
        raise RuntimeError("Nejnovější článek není první položkou RSS.")

    by_link = {node.findtext("link") or "": node for node in items}
    election = by_link[ELECTION_URL]
    jezero = by_link[JEZERO_URL]
    if (election.findtext("description") or "").strip() != ELECTION_DESC:
        raise RuntimeError("Volební článek má v RSS chybný popis.")
    if (jezero.findtext("description") or "").strip() != JEZERO_DESC:
        raise RuntimeError("Článek o jezeře Most má v RSS chybný popis.")
    election_categories = [node.text or "" for node in election.findall("category")]
    jezero_categories = [node.text or "" for node in jezero.findall("category")]
    if "Oprava" not in election_categories or "Oprava" in jezero_categories:
        raise RuntimeError("Kategorie Oprava je přiřazena nesprávné položce RSS.")

    print("RSS opraveno: popisy a kategorie jsou přiřazené ke správným článkům.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
