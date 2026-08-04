#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

DEFAULT_TARGETS = (
    Path("scripts/publish_festpout_polaky_20260805.py"),
    Path("scripts/deploy_festpout_polaky_20260805.sh"),
)

REPLACEMENTS = (
    ("2026-08-05T07:30:00+02:00", "2026-08-09T08:00:00+02:00"),
    ("2026-08-05T05:30:00Z", "2026-08-09T06:00:00Z"),
    ("2026-08-05 05:30:00", "2026-08-09 06:00:00"),
    ("datetime(2026, 8, 5, 7, 30", "datetime(2026, 8, 9, 8, 0"),
    ("2026, 8, 5, 7, 30", "2026, 8, 9, 8, 0"),
    ("5. srpna 2026 v 7:30", "9. srpna 2026 v 8:00"),
    ("5. srpna 2026", "9. srpna 2026"),
    ("5. 8. 2026", "9. 8. 2026"),
    ("05.08.2026", "09.08.2026"),
    ("20260805", "20260809"),
    ("2026-08-05", "2026-08-09"),
)

FORBIDDEN = (
    "2026-08-05T07:30",
    "2026-08-05T05:30",
    "2026-08-05 05:30",
    "2026, 8, 5, 7, 30",
    "20260805",
)


def retime(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"Chybí soubor k přečasování: {path}")
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if text == original:
        raise SystemExit(f"V souboru {path} nebyl nalezen žádný původní časový údaj.")
    remaining = [token for token in FORBIDDEN if token in text]
    if remaining:
        raise SystemExit(f"V souboru {path} zůstaly staré časové údaje: {remaining}")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    targets = tuple(Path(item) for item in sys.argv[1:]) or DEFAULT_TARGETS
    for target in targets:
        retime(target)
    combined = "\n".join(path.read_text(encoding="utf-8") for path in targets)
    required = (
        "2026-08-09",
        "20260809",
        "2026, 8, 9, 8, 0",
    )
    missing = [token for token in required if token not in combined]
    if missing:
        raise SystemExit(f"Po přečasování chybí nové údaje: {missing}")
    print("Publikační balíček Festpouti je přečasovaný na 9. srpna 2026 v 8:00 Europe/Prague.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
