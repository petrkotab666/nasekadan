#!/usr/bin/env python3
"""Zajistí viditelnost všech publikovaných článků a následně je seřadí.

Nejprve z článkových souborů znovu vytvoří titulní blok, karty na titulce
a úplný archiv. Teprve potom provede chronologické řazení a kontrolu hero
bloku. Díky tomu nově zveřejněný článek nemůže zůstat mimo přehledy.
"""
from __future__ import annotations

from pathlib import Path

from enforce_article_visibility import main as enforce_visibility
from sort_articles_chronologically import main as sort_all
from enforce_latest_homepage_hero import main as enforce_latest_hero

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"


def main() -> int:
    if not HOME.is_file() or not ARCHIVE.is_file():
        raise RuntimeError("Chybí titulní stránka nebo archiv článků.")

    enforce_visibility()
    sort_all()
    enforce_latest_hero()

    home = HOME.read_text(encoding="utf-8")
    archive = ARCHIVE.read_text(encoding="utf-8")
    required = "/clanky/nemocnice-kadan-profil-sluzby-budoucnost.html"
    article = ROOT / required.lstrip("/")
    if article.is_file() and (required not in home or required not in archive):
        raise RuntimeError("Kontrolní článek o nemocnici chybí na titulní stránce nebo v archivu.")

    newest = "/clanky/koupaliste-kadan-pozemky-skluzavka-provoz-2026.html"
    if (ROOT / newest.lstrip("/")).is_file() and (newest not in home or newest not in archive):
        raise RuntimeError("Nový článek o koupališti chybí na titulní stránce nebo v archivu.")

    print("Všechny publikované články jsou viditelné a chronologicky seřazené.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
