#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.github' / 'drafts' / 'koupaliste-kadan-pozemky-skluzavka-provoz-2026.html'
ARTICLE = ROOT / 'clanky' / 'koupaliste-kadan-pozemky-skluzavka-provoz-2026.html'
PUBLISHED = '2026-07-31T04:00:00+02:00'
TITLE = 'Kadaňské koupaliště slaví 50 let. Co nabízí a co není jasné kolem nové Niagary'
DESCRIPTION = ('Kadaňské koupaliště slaví 50 let. Přehled bazénů, vstupného, zimní nafukovací haly, '
               'nové skluzavky Niagara, jejího financování a otázek, které zatím zůstávají bez veřejné odpovědi.')
URL = 'https://nasekadan.cz/clanky/koupaliste-kadan-pozemky-skluzavka-provoz-2026.html'
IMAGE = 'https://nasekadan.cz/social/koupaliste-kadan-50-let-niagara-2026.png'


def set_meta(text: str, key: str, value: str, *, prop: bool) -> str:
    attr = 'property' if prop else 'name'
    pattern = re.compile(rf'<meta\b[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*>', re.I)
    tag = f'<meta {attr}="{key}" content="{value}">'
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    return text.replace('</head>', f'  {tag}\n</head>', 1)


def add_public_interest_text(text: str) -> str:
    paragraph = (
        '<p><strong>Veřejnost by proto oprávněně zajímalo, zda provozovatel nebo město připravují '
        'trvalé řešení, jak má vypadat a kdy by mohlo být provedeno.</strong> Nejde o požadavek na '
        'provoz za každou cenu, ale o to, aby bylo jasné, zda se problém řeší tak, aby se nová '
        'Niagara dala bezpečně používat i během běžných letních veder.</p>'
    )
    needle = (
        '<p>Do zveřejnění článku nebyla na webu provozovatele uvedena informace o trvalejším '
        'technickém řešení schodů. Ve veřejných zdrojích jsme nenašli dokumentaci schodiště, '
        'předávací protokol ani informaci o případné reklamaci či plánovaném zastínění.</p>'
    )
    if paragraph not in text and needle in text:
        text = text.replace(needle, needle + '\n' + paragraph, 1)

    text = text.replace(
        '<li>technická dokumentace a řešení přehřívání schodů,</li>',
        '<li>stanovisko, zda a jak bude přehřívání schodů trvale řešeno, včetně předpokládaného termínu,</li>',
    )

    original_end = (
        '<p>Zveřejnění těchto údajů by neubralo nic na významu koupaliště ani nové atrakce. '
        'Naopak by návštěvníkům poskytlo lepší přehled a kolem jubilejní investice by zůstalo '
        'méně prostoru pro dohady.</p>'
    )
    expanded_end = (
        '<p>Zveřejnění těchto údajů by neubralo nic na významu koupaliště ani nové atrakce. '
        'Naopak by návštěvníkům poskytlo lepší přehled a kolem jubilejní investice by zůstalo '
        'méně prostoru pro dohady. Veřejnost bude zajímat především jednoduchá odpověď: '
        '<strong>zda se problém s Niagarou bude řešit, jakým způsobem a kdy bude možné atrakci '
        'bezpečně používat i v horkých dnech.</strong></p>'
    )
    if original_end in text:
        text = text.replace(original_end, expanded_end, 1)
    return text


def main() -> int:
    if not DRAFT.is_file():
        raise FileNotFoundError(DRAFT)
    ARTICLE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DRAFT, ARTICLE)
    text = ARTICLE.read_text(encoding='utf-8')

    text = re.sub(
        r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">',
        text,
        count=1,
        flags=re.I,
    )
    text = text.replace('../../', '../')
    text = text.replace('PŘIPRAVENO KE ZVEŘEJNĚNÍ', '31. ČERVENCE 2026')
    text = text.replace('PŘIPRAVOVANÝ ČLÁNEK', '31. ČERVENCE 2026')
    text = add_public_interest_text(text)

    text = re.sub(
        r'<div class="sidebox"><h3>Stav článku</h3>.*?</div>',
        '',
        text,
        count=1,
        flags=re.S,
    )

    text = set_meta(text, 'og:title', TITLE, prop=True)
    text = set_meta(text, 'og:description', DESCRIPTION, prop=True)
    text = set_meta(text, 'og:url', URL, prop=True)
    text = set_meta(text, 'og:image', IMAGE, prop=True)
    text = set_meta(text, 'og:image:type', 'image/png', prop=True)
    text = set_meta(text, 'og:image:width', '1200', prop=True)
    text = set_meta(text, 'og:image:height', '630', prop=True)
    text = set_meta(text, 'twitter:card', 'summary_large_image', prop=False)
    text = set_meta(text, 'twitter:title', TITLE + ' | Naše Kadaň', prop=False)
    text = set_meta(text, 'twitter:description', DESCRIPTION, prop=False)
    text = set_meta(text, 'twitter:image', IMAGE, prop=False)
    text = set_meta(text, 'article:published_time', PUBLISHED, prop=True)
    text = set_meta(text, 'article:modified_time', PUBLISHED, prop=True)

    schema = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        'headline': TITLE,
        'description': DESCRIPTION,
        'datePublished': PUBLISHED,
        'dateModified': PUBLISHED,
        'author': {'@type': 'Organization', '@id': 'https://nasekadan.cz/#organization', 'name': 'Naše Kadaň', 'url': 'https://nasekadan.cz/o-webu/'},
        'publisher': {'@id': 'https://nasekadan.cz/#organization'},
        'mainEntityOfPage': {'@type': 'WebPage', '@id': URL},
        'inLanguage': 'cs-CZ',
        'isAccessibleForFree': True,
        'image': [IMAGE],
    }
    schema_tag = '<script data-pool-newsarticle="1" type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(',', ':')) + '</script>'
    text = re.sub(r'<script data-pool-newsarticle="1"[^>]*>.*?</script>', '', text, flags=re.S)
    text = text.replace('</head>', schema_tag + '\n</head>', 1)

    ARTICLE.write_text(text, encoding='utf-8', newline='\n')

    required = [
        '31. ČERVENCE 2026',
        'Veřejnost by proto oprávněně zajímalo',
        'kdy bude možné atrakci bezpečně používat i v horkých dnech',
        IMAGE,
        PUBLISHED,
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError('Ve veřejné verzi chybí: ' + ', '.join(missing))
    print(ARTICLE.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
