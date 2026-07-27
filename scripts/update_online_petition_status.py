#!/usr/bin/env python3
"""Historický jednorázový aktualizační skript.

Článek clanky/epetice-nemocnice-kadan.html byl následně ručně rozšířen
o právní rozdíl mezi peticí a referendem, politickou debatu a upřesnění
částek 53 mil. / 25,9 mil. Kč. Skript proto záměrně nic nemění, aby
novější redakční verzi při případném opakovaném spuštění nepřepsal.
"""

from __future__ import annotations


def main() -> None:
    print("update_online_petition_status.py: no-op; článek obsahuje novější ruční aktualizaci")


if __name__ == "__main__":
    main()
