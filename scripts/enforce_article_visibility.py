#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from html import escape, unescape
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'index.html'
ARCHIVE = ROOT / 'clanky' / 'index.html'
CARD_FIX_MARKER = 'CARD-PREVIEW-FIX-20260803'
MONTHS = (
    'LEDNA|ÚNORA|BREZNA|BŘEZNA|DUBNA|KVĚTNA|KVETNA|ČERVNA|CERVNA|'
    'ČERVENCE|CERVENCE|SRPNA|ZÁŘÍ|ZARI|ŘÍJNA|RIJNA|LISTOPADU|PROSINCE'
)


def clean(v: str) -> str:
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', v))).strip()


def first(patterns, text, default=''):
    for p in patterns:
        m = re.search(p, text, re.I | re.S)
        if m:
            return clean(m.group(1))
    return default


def normalize_tag(value: str) -> str:
    """Odstraní datum a čas z konce rubriky, aby se v kartě neopakovaly."""
    tag = clean(value)
    patterns = (
        rf'\s*·\s*\d{{1,2}}\.\s*(?:{MONTHS})\s+\d{{4}}(?:\s*(?:·|V)\s*\d{{1,2}}:\d{{2}})?\s*$',
        r'\s*·\s*\d{1,2}\.\s*\d{1,2}\.\s*\d{4}(?:\s*(?:·|V)\s*\d{1,2}:\d{2})?\s*$',
    )
    while True:
        original = tag
        for pattern in patterns:
            tag = re.sub(pattern, '', tag, flags=re.I).strip(' ·')
        if tag == original:
            break
    return tag or 'AKTUÁLNĚ'


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
    tag = normalize_tag(first([
        r'<p[^>]+class=["\'][^"\']*tag[^"\']*["\'][^>]*>(.*?)</p>'
    ], text, 'AKTUÁLNĚ'))
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
    size = 'cover' if hero else 'contain'
    return (
        f"background-image:{overlay},url('{escape(image, quote=True)}');"
        f'background-color:#0b202b;background-size:{size};'
        'background-position:center;background-repeat:no-repeat'
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


def ensure_preview_css(text: str, archive: bool = False) -> str:
    if archive:
        css = f'''
    /* {CARD_FIX_MARKER} */
    .archive-list .article-card .visual{{background-size:contain!important;background-position:center!important;background-repeat:no-repeat!important;background-color:#0b202b!important}}
    .archive-list .article-card .visual:after{{display:none!important}}
'''
    else:
        css = f'''
    /* {CARD_FIX_MARKER} */
    .article-list .article-card .visual{{height:auto!important;min-height:0!important;aspect-ratio:1200/630;padding:0!important;background-size:contain!important;background-position:center!important;background-repeat:no-repeat!important;background-color:#0b202b!important}}
    .article-list .article-card .visual:after{{display:none!important}}
'''
    block_pattern = rf'\s*/\* {re.escape(CARD_FIX_MARKER)} \*/.*?(?=\n\s*</style>)'
    text = re.sub(block_pattern, '', text, flags=re.S)
    if '</style>' not in text:
        raise RuntimeError('Stránka nemá uzavírací značku </style>.')
    return text.replace('</style>', css + '  </style>', 1)


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
        if 'background-size:contain' not in visual_html:
            broken.append(f'{href}: náhled není contain')
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

    # Nejnovější články zůstávají nejen v hero bloku, ale také na začátku mřížky.
    home_cards = '\n'.join(card(a) for a in articles)
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
    h = ensure_preview_css(h, archive=False)
    HOME.write_text(h, encoding='utf-8', newline='\n')

    atext = ARCHIVE.read_text(encoding='utf-8')
    atext = replace_between(
        atext,
        '<section class="archive-list" aria-label="Chronologický přehled článků">',
        '</section>',
        archive_cards,
    )
    atext = ensure_preview_css(atext, archive=True)
    ARCHIVE.write_text(atext, encoding='utf-8', newline='\n')

    home_text = HOME.read_text(encoding='utf-8')
    archive_text = ARCHIVE.read_text(encoding='utf-8')
    article_list = home_text.split('<div class="article-list">', 1)[-1].split('<p class="archive-note">', 1)[0]
    assert all(x['href'] in article_list for x in articles)
    assert all(x['href'] in archive_text for x in articles)
    first_card = re.search(r'data-auto-article="([^"]+)"', article_list)
    assert first_card and first_card.group(1) == articles[0]['path'].stem
    assert CARD_FIX_MARKER in home_text and 'aspect-ratio:1200/630' in home_text
    validate_cards(home_text, 'Titulní strana')
    validate_cards(archive_text, 'Archiv článků')
    print(
        f'Viditelnost, pořadí, metadata a úplné náhledy zajištěny pro {len(articles)} článků. '
        f'První karta: {articles[0]["href"]}'
    )


if __name__ == '__main__':
    main()
