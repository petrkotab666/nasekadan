#!/usr/bin/env python3
"""Bezpečně zachová a znovu zapojí publikovaný článek o uzavírce II/225.

Článek je redakčně spravovaný přímo v HTML. Tento skript jej nesmí přepisovat
starší šablonou; pouze ověří aktuální text a obnoví titulku, archiv a discovery.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'silnice-zatec-kadan-prejezd-uzavirka-srpen-2026'
ARTICLE = ROOT / 'clanky' / f'{SLUG}.html'
SOCIAL = ROOT / 'social' / 'silnice-zatec-kadan-prejezd-uzavirka-20260803.png'
URL = f'https://nasekadan.cz/clanky/{SLUG}.html'
TITLE = 'Dva přejezdy, dva termíny: silnice Žatec–Kadaň se zavře už 4. srpna'
CITY_SOURCE = 'https://www.mesto-zatec.cz/mesto/aktualne/zacne-tydenni-uzavirka-silnice-ii-225-u-zeleznicniho-prejezdu-smerem-na-kadan-5020cs.html'
DUK_SOURCE = 'https://provoz.kr-ustecky.cz/TMD/LockoutsCTO/Get?pdsei=0'


def require(text: str, value: str) -> None:
    if value not in text:
        raise SystemExit(f'Článek postrádá povinný údaj: {value}')


def ensure_sitemap() -> None:
    path = ROOT / 'sitemap.xml'
    text = path.read_text(encoding='utf-8')
    if URL not in text:
        text = text.replace('</urlset>', f'  <url><loc>{URL}</loc><lastmod>2026-08-03</lastmod></url>\n</urlset>')
        path.write_text(text, encoding='utf-8', newline='\n')


def main() -> None:
    if not ARTICLE.is_file():
        raise SystemExit(f'Chybí publikovaný článek {ARTICLE}.')
    text = ARTICLE.read_text(encoding='utf-8', errors='replace')
    required = [
        f'<h1>{TITLE}</h1>',
        '4. srpna 2026 v 7:00',
        '11. srpna 2026 v 6:00',
        'Druhý přejezd má vlastní termín',
        'Jde však o jiný přejezd',
        'Jde o dvě samostatné uzavírky na různých místech.',
        'Vozidla do 3,5 tuny',
        'Vysoké Třebčice',
        CITY_SOURCE,
        DUK_SOURCE,
        'data-promos data-context="sidebar"',
    ]
    for value in required:
        require(text, value)
    if 'zmatek' in text.lower() or 'noindex' in text.lower():
        raise SystemExit('Článek obsahuje zakázanou starou formulaci nebo noindex.')
    if not SOCIAL.is_file() or SOCIAL.stat().st_size < 10_000:
        raise SystemExit('Chybí původní sociální obrázek článku.')

    subprocess.run(['python3', str(ROOT / 'scripts' / 'enforce_article_visibility.py')], cwd=ROOT, check=True)
    subprocess.run(['python3', str(ROOT / 'scripts' / 'prepare_discovery.py')], cwd=ROOT, check=True)
    ensure_sitemap()

    for rel in ('index.html', 'clanky/index.html', 'rss.xml', 'sitemap.xml', 'news-sitemap.xml', 'llms.txt'):
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f'Chybí {rel}.')
        output = path.read_text(encoding='utf-8', errors='replace')
        if f'/clanky/{SLUG}.html' not in output and URL not in output:
            raise SystemExit(f'{rel} neobsahuje článek.')

    print(f'Publikovaný článek zachován a znovu zapojen: {ARTICLE.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
