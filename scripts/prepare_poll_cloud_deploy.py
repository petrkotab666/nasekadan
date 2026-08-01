#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_GREENERY = ROOT / '.github/workflows/publish-greenery-2026-08-01-1100-v2.yml'


def disable_old_greenery_schedule() -> None:
    text = OLD_GREENERY.read_text(encoding='utf-8')
    marker = '# POLL_V2_SUPERSEDED'
    if marker in text:
        return
    start = text.find('  schedule:\n')
    end = text.find('  workflow_dispatch:', start)
    if start < 0 or end < 0:
        raise RuntimeError('Nelze najít harmonogram starého workflow článku o sečení.')
    replacement = f'  # {marker}: harmonogram převzal publish-greenery-2026-08-01-1100-v3.yml\n'
    text = text[:start] + replacement + text[end:]
    OLD_GREENERY.write_text(text, encoding='utf-8')


def main() -> None:
    disable_old_greenery_schedule()
    print('Starý publikační harmonogram byl bezpečně vypnut; ruční spuštění zůstává dostupné.')


if __name__ == '__main__':
    main()
