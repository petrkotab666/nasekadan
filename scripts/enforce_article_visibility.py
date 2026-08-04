#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape, unescape
from pathlib import Path
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'index.html'
ARCHIVE = ROOT / 'clanky' / 'index.html'
SITEMAP = ROOT / 'sitemap.xml'
HOME_TOTAL = 14
PAGE_SIZE = 12
HOMEPAGE_PIN_HREF = '/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html'
HOMEPAGE_PIN_UNTIL = datetime.fromisoformat('2026-08-05T16:00:00+00:00')
HOMEPAGE_PIN_MARKER = 'NK-TEMP-STADIUM-PIN-20260804'
CARD_FIX_MARKER = 'CARD-PREVIEW-FIX-20260803'
PAGINATION_MARKER = 'ARTICLE-PAGINATION-20260803'
MONTHS = (
    'LEDNA|ÚNORA|BREZNA|BŘEZNA|DUBNA|KVĚTNA|KVETNA|ČERVNA|CERVNA|'
    'ČERVENCE|CERVENCE|SRPNA|ZÁŘÍ|ZARI|ŘÍJNA|RIJNA|LISTOPADU|PROSINCE'
)


def clean(value: str) -> str:
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', value))).strip()


def first(patterns: list[str], text: str, default: str = '') -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return clean(match.group(1))
    return default


def normalize_tag(value: str) -> str:
    tag = clean(value)
    patterns = (
        rf'\s*·\s*\d{{1,2}}\.\s*(?:{MONTHS})\s+\d{{4}}(?:\s*(?:·|V)\s*\d{{1,2}}:\d{{2}})?\s*$',
        r'\s*·\s*\d{1,2}\.\s*\d{1,2}\.\s*\d{4}(?:\s*(?:·|V)\s*\d{1,2}:\d{2})?\s*$',
    )
    while True:
        previous = tag
        for pattern in patterns:
            tag = re.sub(pattern, '', tag, flags=re.I).strip(' ·')
        if tag == previous:
            break
    return tag or 'AKTUÁLNĚ'


def article_info(path: Path) -> dict | None:
    text = path.read_text(encoding='utf-8', errors='replace')
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
        return None
    date_raw = first([
        r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:published_time["\']',
        r'"datePublished"\s*:\s*"([^"]+)"',
    ], text)
    if not date_raw:
        return None
    try:
        published = datetime.fromisoformat(date_raw.replace('Z', '+00:00'))
    except ValueError:
        return None
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    title = first([r'<h1[^>]*>(.*?)</h1>', r'<title>(.*?)</title>'], text, path.stem)
    title = re.sub(r'\s*\|\s*Naše Kadaň\s*$', '', title)
    description = first([
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
        r'<p[^>]+class=["\'][^"\']*leadtext[^"\']*["\'][^>]*>(.*?)</p>',
    ], text)
    tag = normalize_tag(first([r'<p[^>]+class=["\'][^"\']*tag[^"\']*["\'][^>]*>(.*?)</p>'], text, 'AKTUÁLNĚ'))
    image = first([
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)',
    ], text, '/social-card.png')
    return {
        'path': path,
        'href': '/clanky/' + path.name,
        'dt': published,
        'title': title,
        'desc': description,
        'tag': tag,
        'image': image,
    }


def image_style(image: str, hero_image: bool = False) -> str:
    image = image.replace("'", '%27')
    overlay = (
        'linear-gradient(90deg,rgba(7,23,34,.76),rgba(7,23,34,.14) 72%)'
        if hero_image else
        'linear-gradient(rgba(7,23,34,.04),rgba(7,23,34,.18))'
    )
    size = 'cover' if hero_image else 'contain'
    return (
        f"background-image:{overlay},url('{escape(image, quote=True)}');"
        f'background-color:#0b202b;background-size:{size};'
        'background-position:center;background-repeat:no-repeat'
    )


def card(article: dict) -> str:
    date = article['dt']
    meta = f"{date.day}. {date.month}. {date.year} · {date.strftime('%H:%M')} · {article['tag']}"
    title = escape(article['title'])
    return f'''    <article class="article-card hospital" data-auto-article="{escape(article['path'].stem)}">
      <div class="visual" role="img" aria-label="{title}" style="{image_style(article['image'])}"></div>
      <div class="article-body"><span class="meta">{escape(meta)}</span><h3>{title}</h3><p>{escape(article['desc'])}</p><a class="read-more" href="{article['href']}">Přečíst článek →</a></div>
    </article>'''


def hero(first_article: dict, second_article: dict | None) -> str:
    date = first_article['dt']
    aside = ''
    if second_article:
        second_date = second_article['dt']
        aside = f'''    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">{second_date.day}. {second_date.month}. {second_date.year} v {second_date.strftime('%H:%M')}</p>
      <h2>{escape(second_article['title'])}</h2>
      <p>{escape(second_article['desc'])}</p>
      <a class="aside-button" href="{second_article['href']}">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div>
    </aside>'''
    return f'''  <section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{escape(first_article['href'])}">
    <article class="lead">
      <div class="photo" style="{image_style(first_article['image'], hero_image=True)}"><span>{escape(first_article['tag'])}</span><strong>{date.day}. {date.month}. {date.year}</strong></div>
      <div class="copy">
        <small>{escape(first_article['tag'])} · {date.day}. {date.month}. {date.year} · {date.strftime('%H:%M')}</small>
        <h1>{escape(first_article['title'])}</h1>
        <p>{escape(first_article['desc'])}</p>
        <a class="btn" href="{first_article['href']}">Přečíst nejnovější článek →</a>
      </div>
    </article>
{aside}
  </section>'''


def page_url(page: int) -> str:
    return '/clanky/' if page == 1 else f'/clanky/strana-{page}.html'


def absolute_page_url(page: int) -> str:
    return 'https://nasekadan.cz' + page_url(page)


def pagination(current: int, total: int, homepage: bool = False) -> str:
    if total <= 1:
        return ''
    items: list[str] = []
    if current > 1:
        items.append(f'<a class="pagination__edge" rel="prev" href="{page_url(current - 1)}">← Novější</a>')
    elif homepage:
        items.append('<span class="pagination__edge is-disabled">← Novější</span>')
    for number in range(1, total + 1):
        if number == current:
            items.append(f'<span class="is-current" aria-current="page">{number}</span>')
        else:
            items.append(f'<a href="{page_url(number)}" aria-label="Strana {number}">{number}</a>')
    if current < total:
        label = 'Starší články →' if homepage else 'Starší →'
        items.append(f'<a class="pagination__edge" rel="next" href="{page_url(current + 1)}">{label}</a>')
    else:
        items.append('<span class="pagination__edge is-disabled">Starší →</span>')
    return '<nav class="article-pagination" aria-label="Stránkování článků">' + ''.join(items) + '</nav>'


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    start_at = text.find(start)
    if start_at < 0:
        raise RuntimeError(f'Chybí marker {start}')
    end_at = text.find(end, start_at + len(start))
    if end_at < 0:
        raise RuntimeError(f'Chybí marker {end}')
    return text[:start_at + len(start)] + '\n' + replacement + '\n    ' + text[end_at:]


def ensure_css(text: str, archive_page: bool) -> str:
    common = f'''
    /* {CARD_FIX_MARKER} */
    .article-card .visual{{background-size:contain!important;background-position:center!important;background-repeat:no-repeat!important;background-color:#0b202b!important}}
    .article-card .visual:after{{display:none!important}}
    /* {PAGINATION_MARKER} */
    .article-pagination{{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;margin:38px 0 5px}}
    .article-pagination a,.article-pagination span{{display:inline-flex;align-items:center;justify-content:center;min-width:42px;height:42px;padding:0 12px;border:1px solid var(--line);border-radius:11px;background:#fff;color:#273b45;text-decoration:none;font-weight:850}}
    .article-pagination a:hover{{border-color:var(--red);color:var(--red)}}
    .article-pagination .is-current{{background:var(--red);border-color:var(--red);color:#fff}}
    .article-pagination .pagination__edge{{min-width:{'112px' if archive_page else '132px'}}}
    .article-pagination .is-disabled{{opacity:.45}}
'''
    for marker in (CARD_FIX_MARKER, PAGINATION_MARKER):
        text = re.sub(rf'\s*/\* {re.escape(marker)} \*/.*?(?=\n\s*/\*|\n\s*</style>)', '', text, flags=re.S)
    if '</style>' not in text:
        raise RuntimeError('Stránka nemá </style>.')
    return text.replace('</style>', common + '  </style>', 1)


def set_archive_meta(text: str, page: int, total_pages: int, articles: list[dict], total_articles: int) -> str:
    title = 'Všechny články | Naše Kadaň' if page == 1 else f'Články – strana {page} | Naše Kadaň'
    heading = 'Všechny články' if page == 1 else f'Všechny články – strana {page}'
    description = (
        'Chronologický přehled nejnovějších vlastních článků, analýz a ověřených zpráv portálu Naše Kadaň.'
        if page == 1 else
        f'Strana {page} chronologického archivu vlastních článků a ověřených zpráv portálu Naše Kadaň.'
    )
    canonical = absolute_page_url(page)
    text = re.sub(r'<title>.*?</title>', f'<title>{escape(title)}</title>', text, count=1, flags=re.S)
    text = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{escape(description, quote=True)}">', text, count=1)
    text = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{canonical}">', text, count=1)
    text = re.sub(r'<meta property="og:title"[^>]*>', f'<meta property="og:title" content="{escape(title, quote=True)}">', text, count=1)
    text = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{escape(description, quote=True)}">', text, count=1)
    text = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" content="{canonical}">', text, count=1)
    text = re.sub(r'<meta name="twitter:title"[^>]*>', f'<meta name="twitter:title" content="{escape(title, quote=True)}">', text, count=1)
    text = re.sub(r'<meta name="twitter:description"[^>]*>', f'<meta name="twitter:description" content="{escape(description, quote=True)}">', text, count=1)
    text = re.sub(r'<h1[^>]*>.*?</h1>', f'<h1>{escape(heading)}</h1>', text, count=1, flags=re.S)
    text = re.sub(r'\s*<link rel="(?:prev|next)"[^>]*>', '', text)
    relations = []
    if page > 1:
        relations.append(f'  <link rel="prev" href="{absolute_page_url(page - 1)}">')
    if page < total_pages:
        relations.append(f'  <link rel="next" href="{absolute_page_url(page + 1)}">')
    if relations:
        text = text.replace('</head>', '\n'.join(relations) + '\n</head>', 1)
    start_position = (page - 1) * PAGE_SIZE + 1
    schema = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': f'Články Naše Kadaň – strana {page}',
        'numberOfItems': total_articles,
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': start_position + index,
                'url': 'https://nasekadan.cz' + article['href'],
                'name': article['title'],
            }
            for index, article in enumerate(articles)
        ],
    }
    schema_html = '<script data-nk-archive-schema="1" type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
    text = re.sub(r'<script data-nk-archive-schema="1".*?</script>', '', text, flags=re.S)
    text = text.replace('</head>', schema_html + '\n</head>', 1)
    return text


def archive_page(template: str, page: int, total_pages: int, articles: list[dict], total_articles: int) -> str:
    content = '\n'.join(card(article) for article in articles) + '\n' + pagination(page, total_pages)
    text = replace_between(template, '<section class="archive-list" aria-label="Chronologický přehled článků">', '</section>', content)
    text = ensure_css(text, archive_page=True)
    return set_archive_meta(text, page, total_pages, articles, total_articles)


def update_sitemap(total_pages: int) -> None:
    text = SITEMAP.read_text(encoding='utf-8')
    text = re.sub(r'\s*<url>\s*<loc>https://nasekadan\.cz/clanky/strana-\d+\.html</loc>.*?</url>', '', text, flags=re.S)
    additions = ''.join(f'  <url><loc>{absolute_page_url(page)}</loc></url>\n' for page in range(2, total_pages + 1))
    SITEMAP.write_text(text.replace('</urlset>', additions + '</urlset>'), encoding='utf-8', newline='\n')


def validate_cards(text: str, maximum: int) -> list[str]:
    blocks = re.findall(r'<article\b[^>]*class="[^"]*article-card[^"]*"[^>]*>.*?</article>', text, re.I | re.S)
    if not blocks or len(blocks) > maximum:
        raise RuntimeError(f'Neplatný počet karet: {len(blocks)}, maximum {maximum}.')
    hrefs = []
    for block in blocks:
        href = first([r'href=["\'](/clanky/[^"\']+\.html)'], block)
        if not href or 'background-size:contain' not in block:
            raise RuntimeError(f'Neplatná karta {href or "bez odkazu"}.')
        hrefs.append(href)
    return hrefs


def main() -> None:
    articles: list[dict] = []
    for path in sorted((ROOT / 'clanky').glob('*.html')):
        if path.name == 'index.html' or re.fullmatch(r'strana-\d+\.html', path.name):
            continue
        item = article_info(path)
        if item:
            articles.append(item)
    articles.sort(key=lambda item: item['dt'], reverse=True)
    if not articles:
        raise SystemExit('Nenalezen žádný publikovaný článek.')

    total_pages = max(1, math.ceil(len(articles) / PAGE_SIZE))
    homepage_order = list(articles)
    pin_active = bool(HOMEPAGE_PIN_HREF) and datetime.now(timezone.utc) <= HOMEPAGE_PIN_UNTIL
    if pin_active:
        pinned = next((item for item in articles if item['href'] == HOMEPAGE_PIN_HREF), None)
        if pinned is None:
            raise RuntimeError(f'Připínaný článek nebyl nalezen: {HOMEPAGE_PIN_HREF}')
        homepage_order = [pinned] + [item for item in articles if item['href'] != HOMEPAGE_PIN_HREF]
    homepage_articles = homepage_order[:HOME_TOTAL]
    home_cards = '\n'.join(card(article) for article in homepage_articles[2:])
    home_replacement = home_cards + '\n    </div>\n' + pagination(1, total_pages, homepage=True)

    home = HOME.read_text(encoding='utf-8')
    home = re.sub(r'  <section class="wrap hero" id="clanky".*?</section>', hero(homepage_order[0], homepage_order[1] if len(homepage_order) > 1 else None), home, count=1, flags=re.S)
    home = replace_between(home, '<div class="article-list">', '<p class="archive-note">', home_replacement)
    home = ensure_css(home, archive_page=False)
    home = re.sub(
        r'<p class="archive-note">.*?</p>',
        f'<p class="archive-note">Na titulní straně je {min(HOME_TOTAL, len(articles))} nejnovějších článků. Starší texty najdete na dalších stránkách archivu.</p>',
        home,
        count=1,
        flags=re.S,
    )
    HOME.write_text(home, encoding='utf-8', newline='\n')

    template = ARCHIVE.read_text(encoding='utf-8')
    for old in (ROOT / 'clanky').glob('strana-*.html'):
        old.unlink()
    generated = []
    for page in range(1, total_pages + 1):
        start = (page - 1) * PAGE_SIZE
        chunk = articles[start:start + PAGE_SIZE]
        output = archive_page(template, page, total_pages, chunk, len(articles))
        target = ARCHIVE if page == 1 else ROOT / 'clanky' / f'strana-{page}.html'
        target.write_text(output, encoding='utf-8', newline='\n')
        generated.append(target)

    update_sitemap(total_pages)

    home_text = HOME.read_text(encoding='utf-8')
    grid = home_text.split('<div class="article-list">', 1)[1].split('<p class="archive-note">', 1)[0]
    home_hrefs = validate_cards(grid, maximum=HOME_TOTAL - 2)
    expected_home = [article['href'] for article in homepage_articles[2:]]
    if home_hrefs != expected_home:
        raise RuntimeError('Titulní strana nemá správných dvanáct navazujících článků.')
    if len(homepage_articles) == HOME_TOTAL and len(home_hrefs) != 12:
        raise RuntimeError('Na titulní straně musí být pod dvěma zvýrazněnými články dvanáct karet.')

    archive_hrefs: list[str] = []
    for page, target in enumerate(generated, start=1):
        page_text = target.read_text(encoding='utf-8')
        archive_hrefs.extend(validate_cards(page_text, maximum=PAGE_SIZE))
        if f'aria-current="page">{page}</span>' not in page_text:
            raise RuntimeError(f'Archivní strana {page} nemá aktivní číslo.')
    expected_archive = [article['href'] for article in articles]
    if archive_hrefs != expected_archive or len(set(archive_hrefs)) != len(archive_hrefs):
        raise RuntimeError('Archiv není úplný, seřazený nebo obsahuje duplicity.')

    print(
        f'Hotovo: {len(articles)} článků; titulka {min(HOME_TOTAL, len(articles))} '
        f'(2 zvýrazněné + {max(0, min(HOME_TOTAL, len(articles)) - 2)} karet); '
        f'archiv {total_pages} stran po nejvýše {PAGE_SIZE} článcích.'
    )


if __name__ == '__main__':
    main()
