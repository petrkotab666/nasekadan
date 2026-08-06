#!/usr/bin/env python3
"""Odstraní případné duplicitní karty článku AVIES.

AVIES je historický článek a nemusí už být na titulní stránce ani na první
straně archivu. Kontrola proto připouští jeho nepřítomnost na titulce a hledá ho
v celém stránkovaném archivu. V archivu musí zůstat právě jedna karta.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HREF = "/clanky/avies-nemocnice-kadan.html"
ARTICLE_RE = re.compile(r"\s*<article\b[^>]*>.*?</article>\s*", re.I | re.S)


def is_card(block: str, class_tokens: tuple[str, ...]) -> bool:
    opening = block.split(">", 1)[0]
    return any(token in opening for token in class_tokens)


def dedupe_group(
    paths: list[Path],
    class_tokens: tuple[str, ...],
    *,
    require_one: bool,
    label: str,
) -> bool:
    texts = {path: path.read_text(encoding="utf-8") for path in paths}
    matches: list[tuple[Path, re.Match[str]]] = []
    for path, text in texts.items():
        matches.extend(
            (path, match)
            for match in ARTICLE_RE.finditer(text)
            if is_card(match.group(0), class_tokens) and HREF in match.group(0)
        )

    if not matches:
        if require_one:
            raise RuntimeError(f"V {label} chybí karta článku AVIES.")
        return False
    if len(matches) == 1:
        return False

    preferred = next(
        (
            item
            for item in matches
            if 'data-auto-article="avies-nemocnice-kadan"' in item[1].group(0)
        ),
        matches[0],
    )

    changed = False
    for path in paths:
        path_matches = [match for candidate, match in matches if candidate == path]
        if not path_matches:
            continue
        text = texts[path]
        for match in reversed(path_matches):
            if path == preferred[0] and match.start() == preferred[1].start() and match.end() == preferred[1].end():
                continue
            text = text[: match.start()] + "\n" + text[match.end() :]
            changed = True
        if text != texts[path]:
            path.write_text(text, encoding="utf-8", newline="\n")

    remaining = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        remaining += sum(
            1
            for block in ARTICLE_RE.findall(text)
            if is_card(block, class_tokens) and HREF in block
        )
    if remaining != 1:
        raise RuntimeError(f"Duplicitní AVIES karta v {label} nebyla odstraněna.")
    print(f"Opraveno: {label} – AVIES je právě jednou.")
    return changed


def main() -> int:
    changed = False
    changed |= dedupe_group(
        [ROOT / "index.html"],
        ("article-card",),
        require_one=False,
        label="titulní stránce",
    )
    archive_pages = [
        ROOT / "clanky" / "index.html",
        *sorted((ROOT / "clanky").glob("strana-*.html")),
    ]
    changed |= dedupe_group(
        archive_pages,
        ("archive-item", "article-card"),
        require_one=True,
        label="úplném stránkovaném archivu",
    )
    print("Duplicitní karta AVIES odstraněna." if changed else "Karta AVIES už je bez duplicity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
