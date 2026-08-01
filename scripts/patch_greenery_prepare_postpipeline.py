#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'scripts/prepare_greenery_publication_20260801.py'
MARKER = 'POLL_POST_PIPELINE_V2'

HELPER = r'''

def enforce_poll_markup_after_pipeline() -> None:
    """Po společné normalizaci znovu vynutí aktuální externí obsluhu ankety."""
    text = ARTICLE.read_text(encoding="utf-8")
    legacy = re.compile(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', re.I | re.S)
    text = legacy.sub(
        lambda match: "" if "/api/analytics/pageview" in match.group(1) and "data-poll-vote" in match.group(1) else match.group(0),
        text,
    )
    text = text.replace(
        "Funkční hlasování se připojí při zveřejnění článku.",
        "Po hlasování se ihned zobrazí aktuální počty hlasů a procenta.",
    )
    site_tag = f'<script src="/site.js?v={POLL_VERSION}" defer></script>'
    pattern = re.compile(
        r'<script\b(?=[^>]*\bsrc=["\']/site\.js(?:\?v=[^"\']+)?["\'])[^>]*></script>',
        re.I,
    )
    matches = list(pattern.finditer(text))
    if matches:
        first = matches[0]
        text = text[:first.start()] + site_tag + text[first.end():]
        text = pattern.sub("", text, count=max(0, len(matches) - 1))
    elif "</body>" in text:
        text = text.replace("</body>", site_tag + "\n</body>", 1)
    else:
        raise RuntimeError("Po normalizaci nelze vložit site.js pro anketu.")
    ARTICLE.write_text(text, encoding="utf-8", newline="\n")
'''


def main() -> None:
    text = PATH.read_text(encoding='utf-8')
    if MARKER in text:
        print('Povinné vložení ankety po normalizaci už je nastavené.')
        return
    anchor = '\ndef run_common_pipeline() -> None:\n'
    if anchor not in text:
        raise RuntimeError('Nelze najít funkci společného publikačního pipeline.')
    text = text.replace(anchor, HELPER + f'\n# {MARKER}\n' + anchor, 1)
    old = '    run_common_pipeline()\n    payload = validate()\n'
    new = '    run_common_pipeline()\n    enforce_poll_markup_after_pipeline()\n    payload = validate()\n'
    if old not in text:
        raise RuntimeError('Nelze najít hlavní publikační posloupnost.')
    text = text.replace(old, new, 1)
    PATH.write_text(text, encoding='utf-8')
    print('Vložení funkční ankety po normalizaci bylo doplněno.')


if __name__ == '__main__':
    main()
