#!/usr/bin/env python3
from __future__ import annotations

from email.utils import parsedate_to_datetime
from pathlib import Path
import importlib.util
import re
import subprocess
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PIN_HREF = '/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html'
PIN_UNTIL_ISO = '2026-08-05T16:00:00+00:00'
PIN_UNTIL_EXPR = f"datetime.fromisoformat('{PIN_UNTIL_ISO}')"
PUBLISHED = '2026-08-03T22:05:00+02:00'


def patch_source_rules() -> None:
    visibility = ROOT / 'scripts' / 'enforce_article_visibility.py'
    text = visibility.read_text(encoding='utf-8')
    text, href_count = re.subn(
        r'^HOMEPAGE_PIN_HREF\s*=.*$',
        f'HOMEPAGE_PIN_HREF = {PIN_HREF!r}',
        text,
        count=1,
        flags=re.M,
    )
    text, until_count = re.subn(
        r'^HOMEPAGE_PIN_UNTIL\s*=.*$',
        f'HOMEPAGE_PIN_UNTIL = {PIN_UNTIL_EXPR}',
        text,
        count=1,
        flags=re.M,
    )
    if href_count != 1 or until_count != 1:
        raise RuntimeError(f'Nejednoznačná konfigurace připnutí: {href_count}/{until_count}')
    compile(text, str(visibility), 'exec')
    visibility.write_text(text, encoding='utf-8', newline='\n')

    guard = ROOT / 'scripts' / 'run_article_integrity_guard.sh'
    guard_text = guard.read_text(encoding='utf-8')
    guard_text = guard_text.replace(
        "HOMEPAGE_PIN_HREF = ''",
        f'HOMEPAGE_PIN_HREF = {PIN_HREF!r}',
    )
    guard_text = guard_text.replace(
        'HOMEPAGE_PIN_UNTIL = datetime.fromtimestamp(0, tz=timezone.utc)',
        f'HOMEPAGE_PIN_UNTIL = {PIN_UNTIL_EXPR}',
    )
    expected_href = f'HOMEPAGE_PIN_HREF = {PIN_HREF!r}'
    expected_until = f'HOMEPAGE_PIN_UNTIL = {PIN_UNTIL_EXPR}'
    if expected_href not in guard_text or expected_until not in guard_text:
        raise RuntimeError('Kanonická pojistka nebyla přepnuta na aktivní připnutí.')
    guard.write_text(guard_text, encoding='utf-8', newline='\n')


def load_articles() -> list[dict]:
    module_path = ROOT / 'scripts' / 'enforce_article_visibility.py'
    spec = importlib.util.spec_from_file_location('visibility', module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Nelze načíst generátor článků.')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    articles: list[dict] = []
    for path in (ROOT / 'clanky').glob('*.html'):
        if path.name == 'index.html' or re.fullmatch(r'strana-\d+\.html', path.name):
            continue
        item = module.article_info(path)
        if item:
            articles.append(item)
    articles.sort(key=lambda item: item['dt'], reverse=True)
    if not articles:
        raise RuntimeError('Nebyl nalezen žádný publikovaný článek.')
    return articles


def validate_rss_order(path: Path) -> None:
    root = ET.parse(path).getroot()
    items = root.findall('./channel/item')
    if not items:
        raise RuntimeError('RSS neobsahuje žádné položky.')
    links = [item.findtext('link') or '' for item in items]
    dates = []
    for item in items:
        value = item.findtext('pubDate')
        if not value:
            raise RuntimeError('Položka RSS nemá datum publikace.')
        dates.append(parsedate_to_datetime(value))
    if dates != sorted(dates, reverse=True):
        raise RuntimeError('RSS není v chronologickém pořadí.')
    if links[0] == 'https://nasekadan.cz' + PIN_HREF:
        raise RuntimeError('Připínaný článek byl nesprávně přesunut na začátek RSS.')


def validate() -> str:
    article_path = ROOT / PIN_HREF.lstrip('/')
    article = article_path.read_text(encoding='utf-8')
    if f'article:published_time" content="{PUBLISHED}"' not in article:
        raise RuntimeError('Původní datum článku se změnilo.')

    articles = load_articles()
    latest = articles[0]['href']
    if latest == PIN_HREF:
        raise RuntimeError('Připínaný článek neočekávaně změnil chronologickou pozici.')

    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    hero_match = re.search(r'<section class="wrap hero" id="clanky".*?</section>', home, re.S)
    if not hero_match or f'data-latest-article-href="{PIN_HREF}"' not in hero_match.group(0):
        raise RuntimeError('Článek není hlavním zvýrazněným článkem.')
    aside_match = re.search(r'<aside class="current-aside">.*?</aside>', hero_match.group(0), re.S)
    if not aside_match or f'href="{latest}"' not in aside_match.group(0):
        raise RuntimeError(f'Boční blok neobsahuje nejnovější článek {latest}.')
    if '/pocasi.js' not in home:
        raise RuntimeError('Na titulce chybí loader počasí.')

    archive = (ROOT / 'clanky' / 'index.html').read_text(encoding='utf-8')
    first_archive = re.search(
        r'<article\b[^>]*class="[^"]*article-card[^"]*"[^>]*>.*?href="([^"]+)"',
        archive,
        re.S,
    )
    if not first_archive or first_archive.group(1) != latest:
        raise RuntimeError('Archiv není v chronologickém pořadí.')

    validate_rss_order(ROOT / 'rss.xml')
    return latest


def main() -> None:
    patch_source_rules()
    subprocess.run(
        ['python3', str(ROOT / 'scripts' / 'enforce_all_article_visibility.py')],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ['python3', str(ROOT / 'scripts' / 'ensure_weather_loader.py')],
        cwd=ROOT,
        check=True,
    )
    latest = validate()
    (ROOT / '.github' / 'stadium-pin-latest.txt').write_text(latest + '\n', encoding='utf-8')
    print(f'Připraveno: hlavní={PIN_HREF}; boční={latest}')


if __name__ == '__main__':
    main()
