#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from html import escape, unescape
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'index.html'
ARCHIVE = ROOT / 'clanky' / 'index.html'
SITEMAP = ROOT / 'sitemap.xml'
CARD_FIX_MARKER = 'CARD-PREVIEW-FIX-20260803'
PAGINATION_MARKER = 'ARTICLE-PAGINATION-20260803'
HOME_TOTAL = 12
PAGE_SIZE = 12
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


def page_url(page: int) -> str:
    return '/clanky/' if page == 1 else f'/clanky/strana-{page}.html'


def absolute_page_url(page: int) -> str:
    return 'https://nasekadan.cz' + page_url(page)


def pagination(current: int, total: int, homepage: bool = False) -> str:
    if total <= 1:
        return ''
    links = []
    if current > 1:
        links.append(f'<a class="pagination__edge" rel="prev" href="{page_url(current - 1)}">← Novější</a>')
    elif homepage:
        links.append('<span class="pagination__edge is-disabled">← Novější</span>')

    for number in range(1, total + 1):
        if number == current:
            links.append(f'<span class="is-current" aria-current="page">{number}</span>')
        else:
            links.append(f'<a href="{page_url(number)}" aria-label="Strana {number}">{number}</a>')

    if current < total:
        label = 'Starší články →' if homepage else 'Starší →'
        links.append(f'<a class="pagination__edge" rel="next" href="{page_url(current + 1)}">{label}</a>')
    else:
        links.append('<span class="pagination__edge is-disabled">Starší →</span>')

    return '<nav class="article-pagination" aria-label="Stránkování článků">' + ''.join(links) + '</nav>'


def ensure_preview_css(text: str, archive: bool = False) -> str:
    if archive:
        css = f'''
    /* {CARD_FIX_MARKER} */
    .archive-list .article-card .visual{{background-size:contain!important;background-position:center!important;background-repeat:no-repeat!important;background-color:#0b202b!important}}
    .archive-list .article-card .visual:after{{display:none!important}}
    /* {PAGINATION_MARKER} */
    .article-pagination{{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;margin:38px 0 5px}}
    .article-pagination a,.article-pagination span{{display:inline-flex;align-items:center;justify-content:center;min-width:42px;height:42px;padding:0 12px;border:1px solid var(--line);border-radius:11px;background:#fff;color:#273b45;text-decoration:none;font-weight:850}}
    .article-pagination a:hover{{border-color:var(--red);color:var(--red)}}
    .article-pagination .is-current{{background:var(--red);border-color:var(--red);color:#fff}}
    .article-pagination .pagination__edge{{min-width:112px}}
    .article-pagination .is-disabled{{opacity:.45}}
'''
    else:
        css = f'''
    /* {CARD_FIX_MARKER} */
    .article-list .article-card .visual{{height:auto!important;min-height:0!important;aspect-ratio:1200/630;padding:0!important;background-size:contain!important;background-position:center!important;background-repeat:no-repeat!important;background-color:#0b202b!important}}
    .article-list .article-card .visual:after{{display:none!important}}
    /* {PAGINATION_MARKER} */
    .article-pagination{{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;margin:30px 0 0}}
    .article-pagination a,.article-pagination span{{display:inline-flex;align-items:center;justify-content:center;min-width:42px;height:42px;padding:0 12px;border:1px solid var(--line);border-radius:11px;background:#fff;color:#273b45;text-decoration:none;font-weight:850}}
    .article-pagination a:hover{{border-color:var(--red);color:var(--red)}}
    .article-pagination .is-current{{background:var(--red);border-color:var(--red);color:#fff}}
    .article-pagination .pagination__edge{{min-width:132px}}
    .article-pagination .is-disabled{{opacity:.45}}
'''
    for marker in (CARD_FIX_MARKER, PAGINATION_MARKER):
        block_pattern = rf'\s*/\* {re.escape(marker)} \*/.*?(?=\n\s*/\*|\n\s*</style>)'
        text = re.sub(block_pattern, '', text, flags=re.S)
    if '</style>' not in text:
        raise RuntimeError('Stránka nemá uzavírací značku </style>.')
    return text.replace('</style>', css + '  </style>', 1)


def set_meta(text: str, page: int, total_pages: int, page_articles: list[dict], total_articles: int) -> str:
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
        '@graph': [
            {
                '@type': 'CollectionPage',
                '@id': canonical + '#webpage',
                'url': canonical,
                'name': title,
                'description': description,
                'inLanguage': 'cs-CZ',
                'isPartOf': {'@id': 'https://nasekadan.cz/#website'},
                'mainEntity': {'@id': canonical + '#article-list'},
            },
            {
                '@type': 'ItemList',
                '@id': canonical + '#article-list',
                'name': f'Články Naše Kadaň – strana {page}',
                'itemListOrder': 'https://schema.org/ItemListOrderDescending',
                'numberOfItems': total_articles,
                'itemListElement': [
                    {
                        '@type': 'ListItem',
                        'position': start_position + index,
                        'url': 'https://nasekadan.cz' + article['href'],
                        'name': article['title'],
                    }
                    for index, article in enumerate(page_articles)
                ],
            },
        ],
    }
    schema_html = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'
    text, count = re.subn(
        r'<script type="application/ld\+json">\s*\{.*?"CollectionPage".*?</script>',
        schema_html,
        text,
        count=1,
        flags=re.S,
    )
    if count == 0:
        text = text.replace('</head>', schema_html + '\n</head>', 1)
    return text


def archive_page(template: str, page: int, total_pages: int, page_articles: list[dict], total_articles: int) -> str:
    cards = '\n'.join(card(article) for article in page_articles)
    content = cards + '\n' + pagination(page, total_pages)
    text = replace_between(
        template,
        '<section class="archive-list" aria-label="Chronologický přehled článků">',
        '</section>',
        content,
    )
    text = ensure_preview_css(text, archive=True)
    text = set_meta(text, page, total_pages, page_articles, total_articles)
    return text


def update_sitemap(total_pages: int) -> None:
    text = SITEMAP.read_text(encoding='utf-8')
    text = re.sub(
        r'\s*<url>\s*<loc>https://nasekadan\.cz/clanky/strana-\d+\.html</loc>.*?</url>',
        '',
        text,
        flags=re.S,
    )
    entries = ''.join(
        f'  <url><loc>{absolute_page_url(page)}</loc></url>\n'
        for page in range(2, total_pages + 1)
    )
    text = text.replace('</urlset>', entries + '</urlset>')
    SITEMAP.write_text(text, encoding='utf-8', newline='\n')


def validate_cards(text: str, label: str, maximum: int | None = None) -> list[str]:
    cards = re.findall(r'<article\b[^>]*class="[^"]*article-card[^"]*"[^>]*>.*?</article>', text, re.I | re.S)
    if not cards:
        raise RuntimeError(f'{label}: nebyly nalezeny žádné karty článků')
    if maximum is not None and len(cards) > maximum:
        raise RuntimeError(f'{label}: obsahuje {len(cards)} karet, maximum je {maximum}')
    broken = []
    hrefs = []
    for block in cards:
        href = first([r'href=["\'](/clanky/[^"\']+\.html)'], block, 'neznámá karta')
        hrefs.append(href)
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
    return hrefs


def main():
    articles = []
    for path in sorted((ROOT / 'clanky').glob('*.html')):
        if path.name == 'index.html' or re.fullmatch(r'strana-\d+\.html', path.name):
            continue
        info = article_info(path)
        if info:
            articles.append(info)
    articles.sort(key=lambda item: item['dt'], reverse=True)
    if not articles:
        raise SystemExit('Nenalezen žádný publikovaný článek')

    total_pages = max(1, math.ceil(len(articles) / PAGE_SIZE))
    homepage_articles = articles[:HOME_TOTAL]
    home_cards = '\n'.join(card(article) for article in homepage_articles[2:])
    home_content = home_cards + '\n    </div>\n' + pagination(1, total_pages, homepage=True)

    home = HOME.read_text(encoding='utf-8')
    home = re.sub(
        r'  <section class="wrap hero" id="clanky".*?</section>',
        hero(articles[0], articles[1] if len(articles) > 1 else None),
        home,
        count=1,
        flags=re.S,
    )
    home = replace_between(home, '<div class="article-list">', '<p class="archive-note">', home_content)
    home = ensure_preview_css(home, archive=False)
    home = re.sub(
        r'<p class="archive-note">.*?</p>',
        f'<p class="archive-note">Na titulní straně je {min(HOME_TOTAL, len(articles))} nejnovějších článků. Starší texty najdete na dalších stránkách archivu.</p>',
        home,
        count=1,
        flags=re.S,
    )
    HOME.write_text(home, encoding='utf-8', newline='\n')

    template = ARCHIVE.read_text(encoding='utf-8')
    for old_page in (ROOT / 'clanky').glob('strana-*.html'):
        old_page.unlink()

    generated_pages = []
    for page in range(1, total_pages + 1):
        start = (page - 1) * PAGE_SIZE
        chunk = articles[start:start + PAGE_SIZE]
        output = archive_page(template, page, total_pages, chunk, len(articles))
        path = ARCHIVE if page == 1 else ROOT / 'clanky' / f'strana-{page}.html'
        path.write_text(output, encoding='utf-8', newline='\n')
        generated_pages.append(path)

    update_sitemap(total_pages)

    home_text = HOME.read_text(encoding='utf-8')
    home_grid = home_text.split('<div class="article-list">', 1)[-1].split('<p class="archive-note">', 1)[0]
    home_grid_hrefs = validate_cards(home_grid, 'Titulní strana', maximum=max(1, HOME_TOTAL - 2))
    expected_grid = [article['href'] for article in homepage_articles[2:]]
    if home_grid_hrefs != expected_grid:
        raise RuntimeError('Titulní strana nemá správných deset navazujících článků.')
    for article in homepage_articles:
        if article['href'] not in home_text:
            raise RuntimeError(f'Titulní strana postrádá {article["href"]}')
    if len(articles) > HOME_TOTAL and articles[HOME_TOTAL]['href'] in home_grid:
        raise RuntimeError('Titulní strana obsahuje více než dvanáct nejnovějších článků.')
    if total_pages > 1 and page_url(2) not in home_text:
        raise RuntimeError('Na titulní straně chybí odkaz na starší články.')

    archived_hrefs = []
    for page, path in enumerate(generated_pages, start=1):
        text = path.read_text(encoding='utf-8')
        hrefs = validate_cards(text, f'Archiv strana {page}', maximum=PAGE_SIZE)
        archived_hrefs.extend(hrefs)
        if f'aria-current="page">{page}</span>' not in text:
            raise RuntimeError(f'Archiv strana {page} nemá aktivní číslo stránky.')
    expected_archive = [article['href'] for article in articles]
    if archived_hrefs != expected_archive:
        raise RuntimeError('Články nejsou v archivu rozdělené beze ztrát a ve správném pořadí.')
    if len(set(archived_hrefs)) != len(archived_hrefs):
        raise RuntimeError('Stránkovaný archiv obsahuje duplicitní články.')
    if CARD_FIX_MARKER not in home_text or PAGINATION_MARKER not in home_text:
        raise RuntimeError('Na titulní straně chybí trvalé CSS pojistky.')

    print(
        f'Hotovo: {len(articles)} článků, titulka {min(HOME_TOTAL, len(articles))}, '
        f'archiv {total_pages} stran po nejvýše {PAGE_SIZE} článcích.'
    )


if __name__ == '__main__':
    main()
