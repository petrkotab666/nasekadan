#!/usr/bin/env python3
"""Zajistí novou letní reklamní rotaci na všech veřejných HTML stránkách.

Skript sjednotí cache-busting verzi opravného reklamního balíku a doplní jej na
stránky, které načítají hlavní `reklamy.js`, ale opravu dosud nemají. Náhledy a
neveřejné pracovní soubory se záměrně nemění.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260730-pojistime-rotation-4"
SCRIPT_SRC = f"/reklamy-oprava-obrazku.js?v={VERSION}"

EXCLUDED_PARTS = {".git", ".github", "nahled", "node_modules"}
MAIN_AD_RE = re.compile(
    r"<script\b[^>]*\bsrc=[\"'][^\"']*(?:^|/)reklamy\.js(?:\?[^\"']*)?[\"'][^>]*>\s*</script>",
    re.IGNORECASE,
)
ROTATION_RE = re.compile(
    r"(<script\b[^>]*\bsrc=[\"'])([^\"']*?reklamy-oprava-obrazku\.js)(?:\?[^\"']*)?([\"'][^>]*>\s*</script>)",
    re.IGNORECASE,
)


def public_html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        files.append(path)
    return sorted(files)


def normalize(text: str) -> tuple[str, bool]:
    changed = False

    def replace_rotation(match: re.Match[str]) -> str:
        nonlocal changed
        replacement = f"{match.group(1)}{match.group(2)}?v={VERSION}{match.group(3)}"
        if replacement != match.group(0):
            changed = True
        return replacement

    updated = ROTATION_RE.sub(replace_rotation, text)

    if MAIN_AD_RE.search(updated) and not ROTATION_RE.search(updated):
        tag = f'<script src="{SCRIPT_SRC}"></script>'
        if re.search(r"</body\s*>", updated, re.IGNORECASE):
            updated = re.sub(r"</body\s*>", f"{tag}\n</body>", updated, count=1, flags=re.IGNORECASE)
        else:
            updated = updated.rstrip() + f"\n{tag}\n"
        changed = True

    return updated, changed


def audit(files: list[Path]) -> list[str]:
    problems: list[str] = []
    expected_fragment = f"reklamy-oprava-obrazku.js?v={VERSION}"

    for path in files:
        text = path.read_text(encoding="utf-8")
        has_main = MAIN_AD_RE.search(text) is not None
        rotations = ROTATION_RE.findall(text)

        if has_main and not rotations:
            problems.append(f"{path.relative_to(ROOT)}: chybí opravný reklamní balík")
            continue

        if rotations and expected_fragment not in text:
            problems.append(f"{path.relative_to(ROOT)}: používá starou verzi letní rotace")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Zapsat opravy do HTML souborů")
    parser.add_argument("--check", action="store_true", help="Po úpravě provést blokující kontrolu")
    args = parser.parse_args()

    files = public_html_files()
    changed_paths: list[Path] = []

    if args.write:
        for path in files:
            text = path.read_text(encoding="utf-8")
            updated, changed = normalize(text)
            if not changed:
                continue
            path.write_text(updated, encoding="utf-8")
            changed_paths.append(path)

    problems = audit(files)
    print(
        f"Letní reklamní rotace: zkontrolováno {len(files)} HTML, "
        f"upraveno {len(changed_paths)}, problémů {len(problems)}."
    )
    for path in changed_paths[:30]:
        print(f"UPRAVENO: {path.relative_to(ROOT)}")
    if len(changed_paths) > 30:
        print(f"… a dalších {len(changed_paths) - 30} souborů")

    if problems:
        for problem in problems[:50]:
            print(f"CHYBA: {problem}", file=sys.stderr)
        if len(problems) > 50:
            print(f"… a dalších {len(problems) - 50} problémů", file=sys.stderr)
        return 1

    if args.check or not args.write:
        print(f"Všechny reklamní stránky používají {SCRIPT_SRC}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
