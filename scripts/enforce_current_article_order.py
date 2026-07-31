#!/usr/bin/env python3
"""Zajistí úplnou viditelnost všech publikovaných článků.

Z článkových souborů znovu vytvoří titulní blok a archiv, doplní do RSS
každý chybějící veřejný článek, poté všechny přehledy chronologicky seřadí
a ověří nejnovější článek. Nový text tak nemůže zůstat mimo titulku,
archiv ani RSS.
"""
from __future__ import annotations

from pathlib import Path

from enforce_article_visibility import main as enforce_visibility
from ensure_all_published_articles_in_rss import main as ensure_rss
from sort_articles_chronologically import main as sort_all
from enforce_latest_homepage_hero import main as enforce_latest_hero

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"


def main() -> int:
    if not HOME.is_file() or not ARCHIVE.is_file() or not RSS.is_file():
        raise RuntimeError("Chybí titulní stránka, archiv článků nebo RSS.")

    enforce_visibility()
    ensure_rss()
    sort_all()
    enforce_latest_hero()

    home = HOME.read_text(encoding="utf-8")
    archive = ARCHIVE.read_text(encoding="utf-8")
    rss = RSS.read_text(encoding="utf-8")

    required = "/clanky/nemocnice-kadan-profil-sluzby-budoucnost.html"
    article = ROOT / required.lstrip("/")
    if article.is_file() and (required not in home or required not in archive):
        raise RuntimeError("Kontrolní článek o nemocnici chybí na titulní stránce nebo v archivu.")

    newest = "/clanky/koupaliste-kadan-pozemky-skluzavka-provoz-2026.html"
    newest_url = "https://nasekadan.cz" + newest
    if (ROOT / newest.lstrip("/")).is_file():
        if newest not in home or newest not in archive:
            raise RuntimeError("Nový článek o koupališti chybí na titulní stránce nebo v archivu.")
        if newest_url not in rss:
            raise RuntimeError("Nový článek o koupališti chybí v RSS.")

    print("Všechny publikované články jsou viditelné na titulce, v archivu i RSS a jsou chronologicky seřazené.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
