#!/usr/bin/env python3
"""Kompatibilní vstup pro starší workflow.

Původní verze měla pevně zapsaný konkrétní článek a při každém spuštění mohla
vracet titulní stránku do minulosti. Všechny starší workflow nyní používají
stejnou dynamickou pojistku skutečně nejnovějšího článku.
"""
from enforce_latest_homepage_hero import main

if __name__ == "__main__":
    raise SystemExit(main())
