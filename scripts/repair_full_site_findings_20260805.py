#!/usr/bin/env python3
from pathlib import Path
import re, subprocess

ROOT=Path(__file__).resolve().parents[1]

def replace(path, old, new):
    p=ROOT/path
    text=p.read_text(encoding='utf-8',errors='replace')
    updated=text.replace(old,new)
    if updated!=text:
        p.write_text(updated,encoding='utf-8',newline='\n')
        print('Opraveno:',path)

# Neexistující staré fotografie v neveřejných částech a náhledu nahraď stabilní grafikou.
for path in ['clanky/parts/slovan-01.html','nahled/lavka-shell-pracovni-7c26.html']:
    replace(path,'/assets/lavka-shell-20260724.jpg','/social/slovan-druhy-pokus-e2e4356bbb.png')
replace('clanky/parts/slovan-04.html','/assets/slovan-vstup-20260724.jpg','/social/slovan-druhy-pokus-e2e4356bbb.png')

# Kulturní přehled: první sociální obrázek je tmavý/nevhodný pro kartu, sjednoť metadata
# s viditelnou grafikou používanou v těle článku.
replace('clanky/kam-v-kadani-a-okoli-3-9-srpna-2026.html',
        'https://nasekadan.cz/social/kam-v-kadani-a-okoli-3-9-srpna-2026-199cb73db2.png',
        'https://nasekadan.cz/social/kam-v-kadani-a-okoli-3-9-srpna-2026-bff154b86a.png')
replace('clanky/kam-v-kadani-a-okoli-3-9-srpna-2026.html',
        '/social/kam-v-kadani-a-okoli-3-9-srpna-2026-199cb73db2.png',
        '/social/kam-v-kadani-a-okoli-3-9-srpna-2026-bff154b86a.png')

# Odstraň duplicitní neoznačený BreadcrumbList u Plaváčků; ponech kanonický označený blok.
p=ROOT/'clanky/kadansti-plavacci-zapis-podzim-2026.html'
text=p.read_text(encoding='utf-8',errors='replace')
blocks=list(re.finditer(r'<script(?![^>]*data-nasekadan-breadcrumbs)[^>]*type=["\']application/ld\+json["\'][^>]*>.*?"@type"\s*:\s*"BreadcrumbList".*?</script>\s*',text,re.I|re.S))
if blocks:
    for m in reversed(blocks): text=text[:m.start()]+text[m.end():]
    p.write_text(text,encoding='utf-8',newline='\n'); print('Opraveno: Plaváčci breadcrumb')

# Přidej chybějící BreadcrumbList do článku o krvi, pokud chybí.
p=ROOT/'clanky/nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026.html'
text=p.read_text(encoding='utf-8',errors='replace')
if 'BreadcrumbList' not in text:
    title=re.search(r'<h1[^>]*>(.*?)</h1>',text,re.I|re.S)
    name=re.sub(r'<[^>]+>',' ',title.group(1)).strip() if title else 'Nemocnice Kadaň hledá dárce krve'
    url='https://nasekadan.cz/clanky/nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026.html'
    block='<script data-nasekadan-breadcrumbs="1" type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Naše Kadaň","item":"https://nasekadan.cz/"},{"@type":"ListItem","position":2,"name":"Články","item":"https://nasekadan.cz/clanky/"},{"@type":"ListItem","position":3,"name":'+repr(name).replace("'",'"')+',"item":"'+url+'"}]}</script>\n'
    text=text.replace('</head>',block+'</head>',1)
    p.write_text(text,encoding='utf-8',newline='\n'); print('Opraveno: krev breadcrumb')

# U článku o stříkačkách ponech pouze první NewsArticle/Article JSON-LD blok.
p=ROOT/'clanky/strikacky-vchody-drogy-kadan.html'
text=p.read_text(encoding='utf-8',errors='replace')
article_blocks=list(re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>.*?"@type"\s*:\s*"(?:NewsArticle|Article)".*?</script>\s*',text,re.I|re.S))
if len(article_blocks)>1:
    for m in reversed(article_blocks[1:]): text=text[:m.start()]+text[m.end():]
    p.write_text(text,encoding='utf-8',newline='\n'); print('Opraveno: stříkačky schema')

subprocess.run(['python3','scripts/enforce_all_article_visibility.py'],cwd=ROOT,check=True)
subprocess.run(['python3','scripts/sort_articles_chronologically.py'],cwd=ROOT,check=True)
print('Cílené opravy úplného auditu dokončeny.')
