#!/usr/bin/env python3
"""Odstraní duplicitní karty jediného článku AVIES z titulky a archivu.

Starší publikační skript vkládal ručně psanou kartu i v situaci, kdy už obecná
pojistka vytvořila automatickou kartu stejného článku. Tento krok je idempotentní
a preferuje automaticky vytvořenou kartu, protože vychází přímo z metadat článku.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HREF = "/clanky/avies-nemocnice-kadan.html"
ARTICLE_RE = re.compile(r"\s*<article\b[^>]*>.*?</article>\s*", re.I | re.S)


def dedupe(path: Path, class_token: str) -> bool:
    text = path.read_text(encoding="utf-8")
    matches = []
    for match in ARTICLE_RE.finditer(text):
        block = match.group(0)
        opening = block.split(">", 1)[0]
        if class_token in opening and HREF in block:
            matches.append(match)

    if not matches:
        raise RuntimeError(f"V {path.relative_to(ROOT)} chybí karta článku AVIES.")
    if len(matches) == 1:
        return False

    preferred = next(
        (match for match in matches if 'data-auto-article="avies-nemocnice-kadan"' in match.group(0)),
        matches[0],
    )
    for match in reversed(matches):
        if match.start() == preferred.start() and match.end() == preferred.end():
            continue
        text = text[: match.start()] + "\n" + text[match.end() :]

    path.write_text(text, encoding="utf-8", newline="\n")

    check = [
        block
        for block in ARTICLE_RE.findall(text)
        if class_token in block.split(">", 1)[0] and HREF in block
    ]
    if len(check) != 1:
        raise RuntimeError(f"Duplicitní AVIES karta v {path.relative_to(ROOT)} nebyla odstraněna.")
    print(f"Opraveno: {path.relative_to(ROOT)} – AVIES je právě jednou.")
    return True


def main() -> int:
    changed = False
    changed |= dedupe(ROOT / "index.html", "article-card")
    changed |= dedupe(ROOT / "clanky" / "index.html", "archive-item")
    print("Duplicitní karta AVIES odstraněna." if changed else "Karta AVIES už je bez duplicity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
