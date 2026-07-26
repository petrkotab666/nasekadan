#!/usr/bin/env python3
"""Odstraní z veřejného sestavení články, které editor výslovně neschválil.

Neveřejné pracovní verze patří do .github/drafts/. Soubor ve složce clanky/
se jinak automaticky stává veřejnou stránkou, proto se zde drží explicitní
seznam stažených nebo dosud neschválených textů.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNPUBLISHED = {
    "pozemky-koupaliste-kadan.html",
}


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def remove_public_files() -> None:
    for filename in UNPUBLISHED:
        path = ROOT / "clanky" / filename
        if path.exists():
            path.unlink()
            print(f"Odstraněn veřejný soubor: {path.relative_to(ROOT)}")


def remove_archive_references() -> None:
    path = ROOT / "clanky" / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for filename in UNPUBLISHED:
        url = f"https://nasekadan.cz/clanky/{filename}"
        href = f"/clanky/{filename}"

        # HTML karta v archivu.
        text = re.sub(
            rf"\s*<article\b[^>]*(?:data-pool-land-card|class=[\"'][^\"']*archive-item[^\"']*[\"'])[^>]*>"
            rf"(?:(?!</article>).)*?{re.escape(href)}(?:(?!</article>).)*?</article>",
            "",
            text,
            flags=re.I | re.S,
        )

        # JSON-LD položka seznamu. Odstraní položku i sousední čárku.
        text = re.sub(
            rf",?\s*\{{\s*\"@type\"\s*:\s*\"ListItem\"(?:(?!\}}).)*?"
            rf"{re.escape(url)}(?:(?!\}}).)*?\}}\s*,?",
            lambda m: "" if m.group(0).lstrip().startswith(",") else "",
            text,
            flags=re.S,
        )

    # Oprava čárek v poli JSON-LD po odebrání položky.
    text = re.sub(r"}\s*{", "},\n        {", text)
    text = re.sub(r",\s*]", "\n      ]", text)
    item_count = len(re.findall(r'\"@type\"\s*:\s*\"ListItem\"', text))
    text = re.sub(r'\"numberOfItems\"\s*:\s*\d+', f'\"numberOfItems\": {item_count}', text, count=1)
    write(path, text)


def remove_home_references() -> None:
    path = ROOT / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for filename in UNPUBLISHED:
        href = f"/clanky/{filename}"
        text = re.sub(
            rf"\s*<article\b[^>]*>\s*(?:(?!</article>).)*?{re.escape(href)}(?:(?!</article>).)*?</article>",
            "",
            text,
            flags=re.I | re.S,
        )
        text = re.sub(
            rf"\s*<a\b[^>]*href=[\"']{re.escape(href)}[\"'][^>]*>.*?</a>",
            "",
            text,
            flags=re.I | re.S,
        )
    write(path, text)


def remove_sitemap_references() -> None:
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for filename in UNPUBLISHED:
        url = f"https://nasekadan.cz/clanky/{filename}"
        text = re.sub(
            rf"\s*<url>\s*<loc>{re.escape(url)}</loc>.*?</url>",
            "",
            text,
            flags=re.I | re.S,
        )
    write(path, text)


def remove_rss_references() -> None:
    path = ROOT / "rss.xml"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for filename in UNPUBLISHED:
        url = f"https://nasekadan.cz/clanky/{filename}"
        text = re.sub(
            rf"\s*<item>(?:(?!</item>).)*?{re.escape(url)}(?:(?!</item>).)*?</item>",
            "",
            text,
            flags=re.I | re.S,
        )
    write(path, text)


def main() -> int:
    remove_public_files()
    remove_home_references()
    remove_archive_references()
    remove_sitemap_references()
    remove_rss_references()
    print("Neschválené články byly odstraněny z veřejného sestavení.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
