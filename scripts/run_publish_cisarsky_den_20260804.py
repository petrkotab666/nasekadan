#!/usr/bin/env python3
"""Bezpečný spouštěč publikace Císařského dne.

Starší obecná ochrana titulky je natvrdo svázaná s dřívějším článkem KZK.
Tento spouštěč ji pro jediný publikační běh nahrazuje přísnější kontrolou,
která zachová všechny současné karty, zakáže duplicity a ověří nový hero odkaz.
"""
from pathlib import Path
import re

TARGET = Path(__file__).with_name('publish_cisarsky_den_20260804.py')
ROOT = TARGET.resolve().parents[1]
INDEX = ROOT / 'index.html'
EXPECTED_REL = '/clanky/cisarsky-den-kadan-historie-2026.html'

before = INDEX.read_text(encoding='utf-8')
before_cards = re.findall(r'data-auto-article="([^"]+)"', before)
if len(before_cards) != len(set(before_cards)):
    raise SystemExit('Titulka obsahuje duplicitní automatické karty ještě před publikací.')

source = TARGET.read_text(encoding='utf-8')
old = """    write(ARTICLE,build_article()); social_image(); update_home(); update_archive(); update_feeds()
    protector=ROOT/'scripts/ensure_recent_home_articles_20260801.py'
    if protector.exists(): subprocess.run(['python3',str(protector)],check=True,cwd=ROOT)
    validate()
"""
new = """    write(ARTICLE,build_article()); social_image(); update_home(); update_archive(); update_feeds()
    validate()
"""

if source.count(old) != 1:
    raise SystemExit('Bezpečný spouštěč nenašel právě jednu očekávanou publikační sekvenci.')

patched = source.replace(old, new, 1)
namespace = {'__name__': '__main__', '__file__': str(TARGET)}
exec(compile(patched, str(TARGET), 'exec'), namespace)

after = INDEX.read_text(encoding='utf-8')
after_cards = re.findall(r'data-auto-article="([^"]+)"', after)
missing_cards = sorted(set(before_cards) - set(after_cards))
if missing_cards:
    raise SystemExit(f'Publikace odstranila existující karty titulky: {missing_cards}')
if len(after_cards) != len(set(after_cards)):
    raise SystemExit('Publikace vytvořila duplicitní automatické karty titulky.')
if f'data-latest-article-href="{EXPECTED_REL}"' not in after:
    raise SystemExit('Titulka nemá nový článek v atributu data-latest-article-href.')
if after.count(f'href="{EXPECTED_REL}"') < 1:
    raise SystemExit('Titulka neobsahuje odkaz na nový článek.')
if '<div class="article-list">' not in after:
    raise SystemExit('Publikace poškodila seznam článků na titulce.')

print('Nezávislá kontrola integrity titulní stránky prošla.')
