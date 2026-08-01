#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "clanky"

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("neindexované přílohy", re.compile(r"neindexovan(?:é|ých)\s+příloh", re.I)),
    ("fulltextová metoda", re.compile(r"(?:ne|nelze\s+)?č(?:í|i)st\s+fulltextem|fulltextově\s+nečiteln", re.I)),
    ("OCR jako součást veřejného textu", re.compile(r"\bOCR\b", re.I)),
    ("popis obcházení omezení", re.compile(r"obcház(?:en|eli|íme)|obej(?:ít|deme)\s+omezen", re.I)),
    ("sebepropagační popis rešerše", re.compile(r"(?:Naše\s+Kadaň|redakce|my)\s+(?:prošla|prošli|dohledala|dohledali|získala|získali)", re.I)),
    ("technická cesta přes kopii nebo archiv", re.compile(r"podařilo\s+se\s+(?:nám\s+)?dohledat\s+(?:přes|v)|přes\s+zahraniční\s+kopii", re.I)),
)


def iter_public_articles() -> list[Path]:
    if not ARTICLES.exists():
        return []
    return sorted(path for path in ARTICLES.rglob("*.html") if path.is_file())


def main() -> int:
    failures: list[str] = []
    for path in iter_public_articles():
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            line = text.count("\n", 0, match.start()) + 1
            failures.append(f"{path.relative_to(ROOT)}:{line}: {label}: {match.group(0)!r}")
    if failures:
        print("Ve veřejných článcích byl nalezen zakázaný popis interní rešeršní metody:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("Veřejné články neobsahují zakázaný popis interních rešeršních metod.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
