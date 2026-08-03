#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from html import escape, unescape
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'index.html'
ARCHIVE = ROOT / 'clanky' / 'index.html'


def clean(v: str) -> str:
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', v))).strip()


def first(patterns, text, default=''):
    for p in patterns:
        m = re.search(p, text, re.I | re.S)
        if m:
            return clean(m.group(1))
    return default


def article_info(path: Path):
    text = path.read_text(encoding='utf-8', errors='replace')
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
        return None
    dt_raw = first([
        r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:published_time["\']',
        r'"datePublished"\s*:\s*"([^"]+)"'
    ], text)
    if not dt_raw:
        return None
    try:
        dt = datetime.fromisoformat(dt_raw.replace('Z', '+00:00'))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    title = first([r'<h1[^>]*>(.*?)</h1>', r'<title>(.*?)</title>'], text, path.stem)
    title = re.sub(r'\s*\|\s*Naše Kadaň\s*$', '', title)
    desc = first([
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
        r'<p[^>]+class=["\'][^"\']*leadtext[^"\']*["\'][^>]*>(.*?)</p>'
    ], text, '')
    tag = first([r'<p[^>]+class=["\'][^"\']*tag[^"\']*["\'][^>]*>(.*?)</p>'], text, 'AKTUÁLNĚ')
    image = first([
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)',
        r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)'
    ], text, '/social-card.png')
    href = '/clanky/' + path.name
    return {
        'path': path,
        'href': href,
        'dt': dt,
        'title': title,
        'desc': desc,
        'tag': tag,
        'image': image,
    }


def image_style(image: str, hero: bool = False) -> str:
    image = image.replace("'", '%27')
    overlay = (
        'linear-gradient(90deg,rgba(7,23,34,.76),rgba(7,23,34,.14) 72%)'
        if hero else
        'linear-gradient(rgba(7,23,34,.04),rgba(7,23,34,.18))'
    )
    return (
        f"background-image:{overlay},url('{escape(image, quote=True)}');"
        'background-size:cover;background-position:center;background-repeat:no-repeat'
    )


def card(a):
    d = a['dt']
    meta = f"{d.day}. {d.month}. {d.year} · {d.strftime('%H:%M')} · {a['tag']}"
    title = escape(a['title'])
    return f'''    <article class="article-card hospital" data-auto-article="{escape(a['path'].stem)}">
      <div class="visual" role="img" aria-label="{title}" style="{image_style(a['image'])}"></div>
      <div class="article-body"><span class="meta">{escape(meta)}</span><h3>{title}</h3><p>{escape(a['desc'])}</p><a class="read-more" href="{a['href']}">Přečíst článek →</a></div>
    </article>'''


def hero(a, second):
    d = a['dt']
    aside = ''
    if second:
        sd = second['dt']
        aside = f'''    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">{sd.day}. {sd.month}. {sd.year} v {sd.strftime('%H:%M')}</p>
      <h2>{escape(second['title'])}</h2>
      <p>{escape(second['desc'])}</p>
      <a class="aside-button" href="{second['href']}">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div>
    </aside>'''
    return f'''  <section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{escape(a['href'])}">
    <article class="lead">
      <div class="photo" style="{image_style(a['image'], hero=True)}"><span>{escape(a['tag'])}</span><strong>{d.day}. {d.month}. {d.year}</strong></div>
      <div class="copy">
        <small>{escape(a['tag'])} · {d.day}. {d.month}. {d.year} · {d.strftime('%H:%M')}</small>
        <h1>{escape(a['title'])}</h1>
        <p>{escape(a['desc'])}</p>
        <a class="btn" href="{a['href']}">Přečíst nejnovější článek →</a>
      </div>
    </article>
{aside}
  </section>'''


def replace_between(text, start, end, replacement):
    s = text.find(start)
    if s < 0:
        raise RuntimeError(f'Chybí marker {start}')
    e = text.find(end, s + len(start))
    if e < 0:
        raise RuntimeError(f'Chybí marker {end}')
    return text[:s + len(start)] + '\n' + replacement + '\n    ' + text[e:]


def validate_cards(text: str, label: str) -> None:
    cards = re.findall(r'<article\b[^>]*class="[^"]*article-card[^"]*"[^>]*>.*?</article>', text, re.I | re.S)
    if not cards:
        raise RuntimeError(f'{label}: nebyly nalezeny žádné karty článků')
    broken = []
    for block in cards:
        href = first([r'href=["\'](/clanky/[^"\']+\.html)'], block, 'neznámá karta')
        visual = re.search(r'<div\b[^>]*class=["\'][^"\']*visual[^"\']*["\'][^>]*>.*?</div>', block, re.I | re.S)
        if not visual:
            broken.append(f'{href}: chybí visual')
            continue
        visual_html = visual.group(0)
        if 'background-image:' not in visual_html:
            broken.append(f'{href}: chybí background-image')
        if re.search(r'<strong\b', visual_html, re.I):
            broken.append(f'{href}: zdvojený titulek ve visual')
    if broken:
        raise RuntimeError(label + ': ' + '; '.join(broken[:12]))


def main():
    articles = []
    for p in sorted((ROOT / 'clanky').glob('*.html')):
        if p.name == 'index.html':
            continue
        info = article_info(p)
        if info:
            articles.append(info)
    articles.sort(key=lambda x: x['dt'], reverse=True)
    if not articles:
        raise SystemExit('Nenalezen žádný publikovaný článek')

    featured = articles[:2]
    home_cards = '\n'.join(card(a) for a in articles[2:])
    archive_cards = '\n'.join(card(a) for a in articles)

    h = HOME.read_text(encoding='utf-8')
    h = re.sub(
        r'  <section class="wrap hero" id="clanky".*?</section>',
        hero(articles[0], articles[1] if len(articles) > 1 else None),
        h,
        count=1,
        flags=re.S,
    )
    h = replace_between(h, '<div class="article-list">', '<p class="archive-note">', home_cards)
    HOME.write_text(h, encoding='utf-8', newline='\n')

    atext = ARCHIVE.read_text(encoding='utf-8')
    atext = replace_between(
        atext,
        '<section class="archive-list" aria-label="Chronologický přehled článků">',
        '</section>',
        archive_cards,
    )
    ARCHIVE.write_text(atext, encoding='utf-8', newline='\n')

    home_text = HOME.read_text(encoding='utf-8')
    archive_text = ARCHIVE.read_text(encoding='utf-8')
    article_list = home_text.split('<div class="article-list">', 1)[-1].split('<p class="archive-note">', 1)[0]
    assert all(x['href'] in home_text for x in articles)
    assert all(x['href'] in archive_text for x in articles)
    assert all(x['href'] not in article_list for x in featured)
    validate_cards(home_text, 'Titulní strana')
    validate_cards(archive_text, 'Archiv článků')
    print(
        f'Viditelnost a obrázky zajištěny pro {len(articles)} článků. '
        f'Nejnovější dva se na titulce neopakují: {articles[0]["href"]}'
    )


if __name__ == '__main__':
    main()
