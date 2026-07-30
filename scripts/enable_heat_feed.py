#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20260730-heat-rotation-1'
SCRIPT = f'<script src="/horko-feed.js?v={VERSION}"></script>'
SCRIPT_RE = re.compile(
    r'\s*<script\s+src=["\']/horko-feed\.js(?:\?[^"\']*)?["\'][^>]*></script>\s*',
    re.IGNORECASE,
)


def is_public_article(path: Path, text: str) -> bool:
    relative = path.relative_to(ROOT)
    return (
        len(relative.parts) == 2
        and relative.parts[0] == 'clanky'
        and relative.name != 'index.html'
        and 'article-shell' in text
        and re.search(r'<article\b[^>]*class=["\'][^"\']*\barticle\b', text, re.I) is not None
        and '<body' in text.lower()
        and '</body>' in text.lower()
    )


def main() -> int:
    articles = 0
    changed = 0
    for path in sorted(ROOT.rglob('*.html')):
        relative = path.relative_to(ROOT)
        if any(part in {'.git', '.github', 'nahled', 'sdilet'} for part in relative.parts):
            continue
        try:
            original = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue

        current = SCRIPT_RE.sub('\n', original)
        if is_public_article(path, current):
            articles += 1
            pos = current.lower().rfind('</body>')
            current = current[:pos].rstrip() + '\n' + SCRIPT + '\n' + current[pos:]

        if current != original:
            path.write_text(current, encoding='utf-8', newline='\n')
            changed += 1
            print(f'Upraveno: {relative}')

    if articles == 0:
        raise RuntimeError('Nebyl nalezen žádný veřejný článek.')

    failures = []
    expected = f'/horko-feed.js?v={VERSION}'
    for path in sorted((ROOT / 'clanky').glob('*.html')):
        text = path.read_text(encoding='utf-8')
        if is_public_article(path, text) and text.count(expected) != 1:
            failures.append(str(path.relative_to(ROOT)))
    if failures:
        raise RuntimeError('Feed není právě jednou v článcích: ' + ', '.join(failures))

    for path in (ROOT / 'index.html', ROOT / 'clanky' / 'index.html'):
        if path.exists() and '/horko-feed.js' in path.read_text(encoding='utf-8'):
            raise RuntimeError(f'Feed zůstal na nečlánkové stránce: {path.relative_to(ROOT)}')

    # Tento skript volá produkční deploy i Docker build. Po každém vložení feedu
    # proto zároveň sjednotit cache verzi hlavního reklamního balíku na všech
    # veřejných stránkách, nikoli jen v článcích.
    subprocess.run(
        [
            sys.executable,
            str(ROOT / 'scripts' / 'ensure_summer_ad_rotation.py'),
            '--write',
            '--check',
        ],
        cwd=ROOT,
        check=True,
    )

    print(f'Veřejných článků: {articles}; změněných souborů: {changed}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
