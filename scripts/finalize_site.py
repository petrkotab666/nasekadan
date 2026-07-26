#!/usr/bin/env python3
"""Bezpečný závěrečný krok lokální aktualizace webu Naše Kadaň.

Historická verze tohoto skriptu znovu přepisovala hlavičky, metadata, sitemapu
a části konstrukce stránek podle staré šablony. Proto mohla pravidelná serverová
aktualizace po správném nasazení vrátit web do staršího stavu. Tento kompatibilní
vstupní bod už obsah nepřestavuje. Pouze spustí současné idempotentní ochrany.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*parts: str) -> None:
    command = [PYTHON, *parts]
    print("Spouštím:", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    # Obnovit známé vazby článku o nočních výlukách.
    run("scripts/ensure_publication_integrity.py")

    # Doplnit také všechny novější články, které vznikly až po původní
    # ochraně publikace, zejména ePetici a článek o pozemcích koupaliště.
    run("scripts/ensure_newest_article_indexes.py")

    # Série o nemocnici se udržuje z jednoho zdroje a nesmí se rozpadnout při
    # serverové aktualizaci.
    run("scripts/link_hospital_series.py")

    # Všechny veřejné stránky dostanou identickou statickou patičku a jeden
    # společný stylesheet. Staré varianty se odstraní.
    run("scripts/normalize_footers.py", "--write", "--check")

    # Závěrečná kontrola je blokující: neúplný web se nesmí překopírovat do
    # veřejného document rootu.
    run("scripts/validate_publication_integrity.py")

    print("Finální kontrola webu je v pořádku; žádná stará šablona nebyla použita.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
