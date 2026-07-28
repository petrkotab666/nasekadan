#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = '<script src="/horko-feed.js?v=20260728-heat-1"></script>'


def eligible(path: Path, text: str) -> bool:
    if path.parts and any(part in {'.git', '.github', 'nahled', 'sdilet'} for part in path.parts):
        return False
    return '<body' in text.lower() and '</body>' in text.lower()


def main() -> int:
    changed = 0
    checked = 0
    for path in sorted(ROOT.rglob('*.html')):
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        if not eligible(path.relative_to(ROOT), text):
            continue
        checked += 1
        if '/horko-feed.js' in text:
            continue
        pos = text.lower().rfind('</body>')
        updated = text[:pos].rstrip() + '\n' + SCRIPT + '\n' + text[pos:]
        path.write_text(updated, encoding='utf-8', newline='\n')
        changed += 1
        print(f'Doplněno: {path.relative_to(ROOT)}')

    if checked == 0:
        raise RuntimeError('Nebyla nalezena žádná HTML stránka.')
    homepage = (ROOT / 'index.html').read_text(encoding='utf-8')
    if homepage.count('/horko-feed.js') != 1:
        raise RuntimeError('Titulní stránka nemá právě jeden sezónní feed.')
    article = ROOT / 'clanky' / 'hasici-kadan-vycvik-zachrana-voda-nechranice.html'
    if article.exists() and article.read_text(encoding='utf-8').count('/horko-feed.js') != 1:
        raise RuntimeError('Kontrolní článek nemá právě jeden sezónní feed.')
    print(f'HTML zkontrolováno: {checked}; změněno: {changed}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
