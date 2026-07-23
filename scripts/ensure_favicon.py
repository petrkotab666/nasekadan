#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TAG = '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'

changed = 0
for path in ROOT.rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    if re.search(r'<link[^>]+rel=["\'](?:shortcut )?icon["\']', text, re.I):
        continue
    if '</head>' not in text:
        continue
    text = text.replace('</head>', f'{TAG}</head>', 1)
    path.write_text(text, encoding='utf-8')
    changed += 1

print(f'Favicon doplněn do {changed} HTML souborů.')
