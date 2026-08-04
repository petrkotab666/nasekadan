#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'scripts' / 'run_article_integrity_guard.sh'
PIN_HREF = '/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html'
PIN_UNTIL = '2026-08-05T16:00:00+00:00'
START = '  # Každý běh znovu ruší historické připnutí titulky.'
END = '  # Odstraň pouze známé jednorázové nástroje'
NEW_START = '  # NK-STADIUM-PIN-GUARD-20260804'


def main() -> None:
    text = PATH.read_text(encoding='utf-8')
    block = f'''  # NK-STADIUM-PIN-GUARD-20260804
  # Do 5. srpna 2026 18:00 SELČ respektuj redakční připnutí pouze na titulce.
  # Poté se zdrojová konfigurace sama vrátí k běžnému pořadí.
  python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import re

path = Path('scripts/enforce_article_visibility.py')
text = path.read_text(encoding='utf-8')
pin_href = {PIN_HREF!r}
pin_until = datetime.fromisoformat({PIN_UNTIL!r})
active = datetime.now(timezone.utc) <= pin_until
href_value = f'HOMEPAGE_PIN_HREF = {{pin_href!r}}' if active else "HOMEPAGE_PIN_HREF = ''"
until_value = (
    f'HOMEPAGE_PIN_UNTIL = datetime.fromisoformat({PIN_UNTIL!r})'
    if active else
    'HOMEPAGE_PIN_UNTIL = datetime.fromtimestamp(0, tz=timezone.utc)'
)
text, href_count = re.subn(r'^HOMEPAGE_PIN_HREF\\s*=.*$', href_value, text, count=1, flags=re.M)
text, until_count = re.subn(r'^HOMEPAGE_PIN_UNTIL\\s*=.*$', until_value, text, count=1, flags=re.M)
if href_count != 1 or until_count != 1:
    raise SystemExit(f'Chybí jednoznačná konfigurace titulky: href={{href_count}}, until={{until_count}}')
compile(text, str(path), 'exec')
path.write_text(text, encoding='utf-8', newline='\\n')
PY

'''
    if NEW_START in text:
        pattern = re.compile(
            re.escape(NEW_START) + r'.*?(?=' + re.escape(END) + r')',
            re.S,
        )
    else:
        pattern = re.compile(
            re.escape(START) + r'.*?(?=' + re.escape(END) + r')',
            re.S,
        )
    text, count = pattern.subn(lambda _match: block, text, count=1)
    if count != 1:
        raise RuntimeError(f'Blok kanonické pojistky nebyl jednoznačně nalezen: {count}')
    PATH.write_text(text, encoding='utf-8', newline='\n')
    print('Kanonická pojistka má platné časově omezené pravidlo připnutí.')


if __name__ == '__main__':
    main()
