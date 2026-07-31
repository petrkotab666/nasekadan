#!/usr/bin/env python3
"""Remove non-page technical and private research files from the public sitemap."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
TECHNICAL_PATTERNS = (
    re.compile(r"^https://nasekadan\.cz/clanky/parts/", re.IGNORECASE),
    re.compile(r"^https://nasekadan\.cz/research/", re.IGNORECASE),
    re.compile(r"^https://nasekadan\.cz/google[a-z0-9_-]+\.html$", re.IGNORECASE),
)


def is_technical(url: str) -> bool:
    return any(pattern.search(url) for pattern in TECHNICAL_PATTERNS)


def main() -> int:
    if not SITEMAP.exists():
        raise FileNotFoundError(SITEMAP)

    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.parse(SITEMAP)
    root = tree.getroot()
    removed: list[str] = []

    for url_node in list(root):
        loc = next((child for child in url_node if child.tag.endswith("loc")), None)
        value = (loc.text or "").strip() if loc is not None else ""
        if value and is_technical(value):
            root.remove(url_node)
            removed.append(value)

    tree.write(SITEMAP, encoding="utf-8", xml_declaration=True)
    with SITEMAP.open("a", encoding="utf-8") as handle:
        handle.write("\n")

    if removed:
        print("Ze sitemapy odstraněny technické a neveřejné soubory:")
        for url in removed:
            print(f"- {url}")
    else:
        print("Sitemap neobsahovala žádné technické ani neveřejné soubory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
