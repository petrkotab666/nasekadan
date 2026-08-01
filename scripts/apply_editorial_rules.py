#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / "clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html",
)

REPLACEMENTS = (
    (
        " Naše Kadaň prošla české i zahraniční dokumenty, neindexované přílohy, smlouvy a územní podklady.",
        "",
    ),
    (
        "  <p>Český archiv oznámení nebyl běžně čitelný po jednotlivých přílohách. Úplnější text se však podařilo dohledat v německém přeshraničním řízení.</p>\n",
        "",
    ),
)

FORBIDDEN_PUBLIC_PHRASES = (
    "neindexované přílohy",
    "nebyl běžně čitelný",
    "podařilo dohledat v německém přeshraničním řízení",
)


def clean(path: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8")
    text = original
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    found = [phrase for phrase in FORBIDDEN_PUBLIC_PHRASES if phrase in text]
    if found:
        raise SystemExit(f"V článku zůstal popis rešeršní metody: {', '.join(found)}")
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = [str(path.relative_to(ROOT)) for path in TARGETS if clean(path)]
    if changed:
        print("Redakční pravidlo použito na: " + ", ".join(changed))
    else:
        print("Text už redakční pravidlo splňuje.")


if __name__ == "__main__":
    main()
