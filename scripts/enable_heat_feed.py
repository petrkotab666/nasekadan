#!/usr/bin/env python3
from __future__ import annotations

import os
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
GYMNASTIKA_ARTICLE = ROOT / 'clanky' / 'gymnastika-kadan-treneri-prosinec-2026.html'
GYMNASTIKA_SOCIAL = ROOT / 'social' / 'gymnastika-kadan-treneri-prosinec-2026.png'
GYMNASTIKA_GENERATOR = ROOT / 'scripts' / 'publish_gymnastika_kadan_20260806.py'


def ensure_pillow() -> None:
    try:
        __import__('PIL')
        return
    except ImportError:
        pass

    attempts = (
        [sys.executable, '-m', 'pip', 'install', '--user', 'Pillow'],
        [sys.executable, '-m', 'pip', 'install', '--user', '--break-system-packages', 'Pillow'],
    )
    for command in attempts:
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode == 0:
            __import__('PIL')
            return
    raise RuntimeError('Pillow se nepodařilo nainstalovat pro sociální grafiku Gymnastiky Kadaň.')


def ensure_gymnastika_publication() -> None:
    """Vytvoří schválený článek na vlastním runneru po resetu na aktuální main.

    Hook je idempotentní. Jakmile budou hotové soubory jednou uloženy přímo v
    hlavní větvi, už nic negeneruje. Do té doby zajistí, že každý kanonický
    produkční deploy článek znovu vytvoří ještě před validací a Docker buildem.
    """
    if GYMNASTIKA_ARTICLE.is_file() and GYMNASTIKA_SOCIAL.is_file():
        return
    if not GYMNASTIKA_GENERATOR.is_file():
        raise RuntimeError('Chybí generátor publikace Gymnastiky Kadaň.')

    ensure_pillow()
    env = os.environ.copy()
    try:
        source_commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        source_commit = 'canonical-self-hosted-deploy'
    env['ARTICLE_SOURCE_COMMIT'] = source_commit
    subprocess.run(
        [sys.executable, str(GYMNASTIKA_GENERATOR)],
        cwd=ROOT,
        env=env,
        check=True,
    )
    if not GYMNASTIKA_ARTICLE.is_file() or not GYMNASTIKA_SOCIAL.is_file():
        raise RuntimeError('Generátor nevytvořil úplnou publikaci Gymnastiky Kadaň.')
    print('Připraven článek Gymnastiky Kadaň pro kanonický produkční deploy.')


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
    ensure_gymnastika_publication()

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
