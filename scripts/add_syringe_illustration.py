#!/usr/bin/env python3
"""Vloží ilustrační fotografii do článku o stříkačkách a zachová ji i v návrhu."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    ROOT / "clanky" / "strikacky-vchody-drogy-kadan.html",
    ROOT / ".github" / "drafts" / "strikacky-vchody-drogy-kadan.html",
)
MODIFIED = "2026-07-30T06:32:00+02:00"
IMAGE = "/assets/clanky/strikacky-vchody-drogy-kadan-ilustrace.webp"
FIGURE = (
    '<figure class="article-photo" data-syringe-illustration="1">'
    f'<img src="{IMAGE}" width="1280" height="720" '
    'alt="Ilustrační fotografie odhozené injekční stříkačky ve vchodu domu" '
    'loading="eager" decoding="async">'
    '<figcaption>Ilustrační foto: odhozená injekční stříkačka ve společných prostorách domu.</figcaption>'
    '</figure>'
)
CSS = (
    '.article-photo{margin:28px 0 34px}'
    '.article-photo img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;'
    'border-radius:20px;box-shadow:0 14px 34px #132b3624}'
    '.article-photo figcaption{margin-top:9px;color:#68767f;font-size:14px;line-height:1.45}'
)


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if "data-syringe-illustration" not in text:
        lead = re.search(r'(<p\b[^>]*class=["\'][^"\']*\bleadtext\b[^"\']*["\'][^>]*>.*?</p>)', text, re.I | re.S)
        if not lead:
            raise RuntimeError(f"V {path.relative_to(ROOT)} chybí perex článku.")
        text = text[: lead.end()] + "\n" + FIGURE + text[lead.end() :]

    if ".article-photo{" not in text:
        text, count = re.subn(r'</style>', CSS + '</style>', text, count=1, flags=re.I)
        if count != 1:
            raise RuntimeError(f"V {path.relative_to(ROOT)} chybí blok style.")

    text = re.sub(
        r'(<meta\b[^>]*property=["\']article:modified_time["\'][^>]*content=["\'])[^"\']+',
        rf'\g<1>{MODIFIED}',
        text,
        flags=re.I,
    )
    text = re.sub(
        r'(<meta\b[^>]*content=["\'])[^"\']+(["\'][^>]*property=["\']article:modified_time["\'])',
        rf'\g<1>{MODIFIED}\g<2>',
        text,
        flags=re.I,
    )
    text = re.sub(r'("dateModified"\s*:\s*")[^"]+', rf'\g<1>{MODIFIED}', text)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"Upraveno: {path.relative_to(ROOT)}")
        return True
    print(f"Beze změny: {path.relative_to(ROOT)}")
    return False


def main() -> int:
    for path in PATHS:
        if not path.is_file():
            raise RuntimeError(f"Chybí soubor {path.relative_to(ROOT)}")
        patch(path)

    public = PATHS[0].read_text(encoding="utf-8")
    if public.count('data-syringe-illustration="1"') != 1:
        raise RuntimeError("Ilustrační fotografie není v článku právě jednou.")
    if IMAGE not in public:
        raise RuntimeError("Článek neodkazuje na ilustrační soubor.")
    print("Ilustrační fotografie je vložena a článek je připraven k nasazení.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
