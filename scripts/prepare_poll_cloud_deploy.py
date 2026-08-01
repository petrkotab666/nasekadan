#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_GREENERY = ROOT / '.github/workflows/publish-greenery-2026-08-01-1100-v2.yml'


def disable_old_greenery_schedule() -> None:
    text = OLD_GREENERY.read_text(encoding='utf-8')
    if 'publish-greenery-2026-08-01-1100-v3.yml' in text and '  schedule:\n' not in text:
        return
    start = text.find('  schedule:\n')
    end = text.find('  workflow_dispatch:', start)
    if start < 0 or end < 0:
        raise RuntimeError('Starý workflow není ani vypnutý, ani ve známém původním formátu.')
    text = text[:start] + "  # Harmonogram převzal publish-greenery-2026-08-01-1100-v3.yml\n" + text[end:]
    OLD_GREENERY.write_text(text, encoding='utf-8')


def main() -> None:
    disable_old_greenery_schedule()
    print('Starý publikační harmonogram je vypnutý; publikaci zajišťuje v3.')


if __name__ == '__main__':
    main()
