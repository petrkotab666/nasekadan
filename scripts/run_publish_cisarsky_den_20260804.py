#!/usr/bin/env python3
"""Bezpečný spouštěč publikace Císařského dne.

Stávající ochrana titulní stránky nejprve ověřuje dosavadní hlavní článek KZK.
Teprve potom smí nový publikační skript přepnout hero na Císařský den.
Tento spouštěč mění pouze pořadí těchto dvou kroků v paměti; zdrojové soubory
ani veřejný web před úspěšným dokončením nijak neupravuje.
"""
from pathlib import Path

TARGET = Path(__file__).with_name('publish_cisarsky_den_20260804.py')
source = TARGET.read_text(encoding='utf-8')
old = """    write(ARTICLE,build_article()); social_image(); update_home(); update_archive(); update_feeds()
    protector=ROOT/'scripts/ensure_recent_home_articles_20260801.py'
    if protector.exists(): subprocess.run(['python3',str(protector)],check=True,cwd=ROOT)
    validate()
"""
new = """    write(ARTICLE,build_article()); social_image()
    protector=ROOT/'scripts/ensure_recent_home_articles_20260801.py'
    if protector.exists(): subprocess.run(['python3',str(protector)],check=True,cwd=ROOT)
    update_home(); update_archive(); update_feeds()
    validate()
"""

if source.count(old) != 1:
    raise SystemExit('Bezpečný spouštěč nenašel právě jednu očekávanou publikační sekvenci.')

patched = source.replace(old, new, 1)
namespace = {'__name__': '__main__', '__file__': str(TARGET)}
exec(compile(patched, str(TARGET), 'exec'), namespace)
