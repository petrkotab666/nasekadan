#!/usr/bin/env python3
"""Přidá přímý, idempotentní loader počasí na titulku a stránku počasí."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (ROOT / "index.html", ROOT / "pocasi" / "index.html")
MARKER = 'data-nk-weather-direct="1"'
LOADER = (
    '<script data-nk-weather-direct="1" data-nk-weather="direct" '
    'src="/pocasi.js?v=20260803-weather-live-refresh-3" defer></script>'
)


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    closing = "</body>"
    if closing not in text:
        raise SystemExit(f"V {path} chybí </body>.")
    text = text.replace(closing, f"{LOADER}\n{closing}", 1)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for target in TARGETS:
        if not target.is_file():
            raise SystemExit(f"Chybí očekávaný soubor {target}.")
        if patch(target):
            changed.append(str(target.relative_to(ROOT)))
    if changed:
        print("Loader počasí doplněn: " + ", ".join(changed))
    else:
        print("Loader počasí je již přítomen.")


if __name__ == "__main__":
    main()
