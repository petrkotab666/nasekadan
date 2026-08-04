#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import ssl
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

BASE = 'https://nasekadan.cz'
PIN = '/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html'
PUBLISHED = '2026-08-03T22:05:00+02:00'
ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ssl.create_default_context()


def fetch(path: str, nonce: str) -> str:
    separator = '&' if '?' in path else '?'
    url = f'{BASE}{path}{separator}{urlencode({"pincheck": nonce})}'
    request = Request(
        url,
        headers={
            'User-Agent': 'NaseKadan-Stadium-Pin-Check/20260804',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        },
    )
    with urlopen(request, timeout=40, context=CONTEXT) as response:
        return response.read().decode('utf-8', errors='replace')


def verify_once(latest: str, nonce: str) -> None:
    home = fetch('/', nonce)
    article = fetch(PIN, nonce)
    archive = fetch('/clanky/', nonce)
    rss = fetch('/rss.xml', nonce)
    forecast = fetch('/api/pocasi-predpoved.json', nonce)

    hero = re.search(r'<section class="wrap hero" id="clanky".*?</section>', home, re.S)
    if not hero or f'data-latest-article-href="{PIN}"' not in hero.group(0):
        raise RuntimeError('Připínaný článek není hlavním článkem živé titulky.')
    aside = re.search(r'<aside class="current-aside">.*?</aside>', hero.group(0), re.S)
    if not aside or f'href="{latest}"' not in aside.group(0):
        raise RuntimeError(f'Boční blok živé titulky neobsahuje {latest}.')
    if '/pocasi.js' not in home:
        raise RuntimeError('Na živé titulce chybí loader počasí.')
    if f'article:published_time" content="{PUBLISHED}"' not in article:
        raise RuntimeError('Živý článek nemá původní datum publikace.')

    first_archive = re.search(
        r'<article\b[^>]*class="[^"]*article-card[^"]*"[^>]*>.*?href="([^"]+)"',
        archive,
        re.S,
    )
    if not first_archive or first_archive.group(1) != latest:
        raise RuntimeError('Živý archiv není v chronologickém pořadí.')

    root = ET.fromstring(rss)
    if root.findtext('./channel/item/link') != BASE + latest:
        raise RuntimeError('Živé RSS není v chronologickém pořadí.')

    weather = json.loads(forecast)
    timeseries = weather.get('properties', {}).get('timeseries')
    if not isinstance(timeseries, list) or not timeseries:
        raise RuntimeError('Veřejná předpověď počasí neobsahuje data.')


def main() -> None:
    latest_path = ROOT / '.github' / 'stadium-pin-latest.txt'
    latest = latest_path.read_text(encoding='utf-8').strip()
    if not latest.startswith('/clanky/') or latest == PIN:
        raise SystemExit('Neplatný boční článek.')

    last_error: Exception | None = None
    for attempt in range(1, 16):
        nonce = f'{int(datetime.now(timezone.utc).timestamp())}-{attempt}'
        try:
            verify_once(latest, nonce)
            print(f'Veřejná kontrola prošla: hlavní={PIN}; boční={latest}; počasí=ok')
            return
        except Exception as exc:
            last_error = exc
            print(f'Pokus {attempt}/15 neprošel: {exc}', file=sys.stderr)
            if attempt < 15:
                time.sleep(10)
    raise SystemExit(f'Veřejná kontrola neprošla: {last_error}')


if __name__ == '__main__':
    main()
