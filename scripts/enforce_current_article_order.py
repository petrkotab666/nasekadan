#!/usr/bin/env python3
"""Seřadí už publikované články a ochrání skutečně nejnovější titulku.

Jednorázové publikační skripty starších článků se zde nesmějí znovu spouštět.
Právě jejich opakované volání vracelo na hlavní stránku starší přehled ordinací
a odstraňovalo z titulky dnešní článek o Nemocnici Kadaň.
"""
from __future__ import annotations

from pathlib import Path

from sort_articles_chronologically import main as sort_all
from enforce_latest_homepage_hero import main as enforce_latest_hero

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"


def main() -> int:
    if not HOME.is_file() or not ARCHIVE.is_file():
        raise RuntimeError("Chybí titulní stránka nebo archiv článků.")

    sort_all()
    enforce_latest_hero()

    home = HOME.read_text(encoding="utf-8")
    archive = ARCHIVE.read_text(encoding="utf-8")
    required = "/clanky/nemocnice-kadan-profil-sluzby-budoucnost.html"
    article = ROOT / required.lstrip("/")
    if article.is_file() and (required not in home or required not in archive):
        raise RuntimeError("Dnešní článek o nemocnici chybí na titulní stránce nebo v archivu.")

    print("Články jsou chronologicky seřazené a nejnovější článek je chráněný na titulní straně.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
