#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://nasekadan.cz'


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != 'meta':
            return
        values = {k.lower(): (v or '') for k, v in attrs}
        key = values.get('property') or values.get('name')
        if key:
            self.meta[key.lower()] = values.get('content', '').strip()


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.I | re.S)
    return match.group(1).strip() if match else ''


def parse_date(text: str) -> datetime | None:
    value = extract(r'article:published_time[^>]+content=["\']([^"\']+)', text)
    if not value:
        value = extract(r'"datePublished"\s*:\s*"([^"]+)"', text)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def marker_path(article_path: str) -> str:
    digest = hashlib.sha256(article_path.encode('utf-8')).hexdigest()[:10]
    return f'.github/facebook-published/{Path(article_path).stem}-{digest}.json'


def build_manifest(hours: int, limit: int) -> list[dict[str, str]]:
    now = datetime.now(timezone.utc)
    oldest = now - timedelta(hours=hours)
    found: list[tuple[datetime, dict[str, str]]] = []
    for path in (ROOT / 'clanky').glob('*.html'):
        if path.name == 'index.html':
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
            continue
        published = parse_date(text)
        if not published or published > now + timedelta(minutes=3) or published < oldest:
            continue
        article_path = path.relative_to(ROOT).as_posix()
        url = extract(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', text)
        image = extract(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', text)
        title = extract(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', text) or extract(r'<h1[^>]*>(.*?)</h1>', text)
        if not url:
            url = f'{SITE}/clanky/{path.name}'
        image_path = ''
        prefix = SITE + '/'
        if image.startswith(prefix):
            image_path = image[len(prefix):].split('?', 1)[0]
        found.append((published, {
            'article_path': article_path,
            'article_url': url,
            'title': re.sub(r'<[^>]+>', ' ', title).strip(),
            'image_url': image,
            'image_path': image_path,
            'published_at': published.isoformat(),
            'facebook_marker': marker_path(article_path),
        }))
    found.sort(key=lambda item: (item[0], item[1]['article_path']), reverse=True)
    return [item for _, item in found[:limit]]


def cache_bust(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    query.append(('integrity', str(time.time_ns())))
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query), parts.fragment))


def fetch(url: str) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(cache_bust(url), headers={'User-Agent': 'NaseKadanPublicationIntegrity/1.0', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.status, {key.lower(): value for key, value in response.headers.items()}, response.read()
    except Exception as exc:
        return 0, {}, str(exc).encode()


def png_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) >= 24 and data.startswith(b'\x89PNG\r\n\x1a\n'):
        return struct.unpack('>II', data[16:24])
    return None


def check(manifest: list[dict[str, str]]) -> dict[str, object]:
    shared: dict[str, str] = {}
    for key, url in {
        'home': SITE + '/',
        'archive': SITE + '/clanky/',
        'rss': SITE + '/rss.xml',
        'sitemap': SITE + '/sitemap.xml',
        'news': SITE + '/news-sitemap.xml',
    }.items():
        status, _, body = fetch(url)
        shared[key] = body.decode('utf-8', errors='replace') if status == 200 else ''

    results: list[dict[str, object]] = []
    for item in manifest:
        errors: list[str] = []
        status, _, body = fetch(item['article_url'])
        page = body.decode('utf-8', errors='replace') if status == 200 else ''
        if status != 200:
            errors.append(f'article_http_{status}')
        parser = MetaParser()
        parser.feed(page)
        live_image = parser.meta.get('og:image', '')
        if item['title'] and item['title'][:60] not in page:
            errors.append('title_missing')
        if live_image != item['image_url']:
            errors.append('og_image_mismatch')
        needle_path = '/' + item['article_path']
        needle_url = item['article_url']
        if needle_path not in shared['home']:
            errors.append('homepage_missing')
        if needle_path not in shared['archive']:
            errors.append('archive_missing')
        if needle_url not in shared['rss']:
            errors.append('rss_missing')
        if needle_url not in shared['sitemap']:
            errors.append('sitemap_missing')
        if needle_url not in shared['news']:
            errors.append('news_sitemap_missing')
        if not item['image_url'] or not item['image_path']:
            errors.append('image_not_local')
        else:
            image_status, headers, image_data = fetch(item['image_url'])
            content_type = headers.get('content-type', '').split(';', 1)[0].lower()
            if image_status != 200:
                errors.append(f'image_http_{image_status}')
            if content_type != 'image/png':
                errors.append('image_not_png')
            if png_dimensions(image_data) != (1200, 630):
                errors.append('image_dimensions')
            if len(image_data) < 10_000:
                errors.append('image_too_small')
        results.append({'article_path': item['article_path'], 'ok': not errors, 'errors': errors})
    return {'ok': all(result['ok'] for result in results), 'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'results': results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['manifest', 'check'])
    parser.add_argument('--hours', type=int, default=48)
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--manifest-file')
    parser.add_argument('--status-file')
    args = parser.parse_args()

    if args.mode == 'manifest':
        print(json.dumps(build_manifest(args.hours, args.limit), ensure_ascii=False, indent=2))
        return 0

    if not args.manifest_file:
        parser.error('--manifest-file je povinný pro režim check')
    manifest = json.loads(Path(args.manifest_file).read_text(encoding='utf-8'))
    status = check(manifest)
    rendered = json.dumps(status, ensure_ascii=False, indent=2) + '\n'
    if args.status_file:
        Path(args.status_file).write_text(rendered, encoding='utf-8')
    print(rendered, end='')
    return 0 if status['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
