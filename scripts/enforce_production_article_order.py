#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = [
    "/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html",
    "/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html",
    "/clanky/kolobezky-hriste-detektor-kovu-kadan.html",
    "/clanky/avies-nemocnice-kadan.html",
    "/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html",
]


def reorder(path: Path, start_marker: str, end_marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker, start)
    section = text[start:end]
    blocks = re.findall(r"<article\b[^>]*>.*?</article>", section, flags=re.S | re.I)

    ordered: list[str] = []
    used: set[int] = set()
    for href in ORDER:
        match_index = next((i for i, block in enumerate(blocks) if i not in used and f'href="{href}"' in block), None)
        if match_index is None:
            raise RuntimeError(f"V {path} chybí karta {href}")
        ordered.append(blocks[match_index])
        used.add(match_index)

    ordered.extend(block for i, block in enumerate(blocks) if i not in used)
    replacement = "\n" + "\n".join(block.strip() for block in ordered) + "\n    "
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")


def verify(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    positions = [text.find(f'href="{href}"', text.find(marker)) for href in ORDER]
    if any(position < 0 for position in positions):
        raise RuntimeError(f"V {path} chybí některý povinný odkaz")
    if positions != sorted(positions):
        raise RuntimeError(f"V {path} je špatné pořadí: {positions}")


def main() -> int:
    home = ROOT / "index.html"
    archive = ROOT / "clanky" / "index.html"
    reorder(home, '<div class="article-list">', '<p class="archive-note">')
    reorder(archive, '<section class="archive-list" aria-label="Chronologický přehled článků">', '</section>')
    verify(home, '<div class="article-list">')
    verify(archive, '<section class="archive-list"')
    print("Pořadí potvrzeno: Nechranice, 82 lůžek, koloběžky, AVIES, kultura.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Chyba pořadí článků: {exc}", file=sys.stderr)
        raise
