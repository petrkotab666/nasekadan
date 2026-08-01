#!/usr/bin/env python3
from pathlib import Path
import re

path = Path('clanky/petice-nemocnice-kadan-podpisova-mista-2026.html')
text = path.read_text(encoding='utf-8')

marker = 'data-online-petition-update="20260801"'

# Aktualizovat perex tak, aby online možnost nebyla přehlédnutelná.
text = text.replace(
    'Podpisové archy budou v Kadani dostupné od 3. do 15. srpna. Petice žádá zachování nemocnice ve vlastnictví města a přichází krátce po další výměně jejího vedení, v době pokračujících právních sporů kolem minulého řízení.',
    'Podpisové archy budou v Kadani dostupné od 3. do 15. srpna a současně pokračuje také elektronická petice. Iniciativa žádá zachování nemocnice ve vlastnictví města a přichází krátce po další výměně jejího vedení, v době pokračujících právních sporů kolem minulého řízení.'
)

# Viditelný informační box s interním odkazem na podrobný článek.
if marker not in text:
    block = '''
  <section class="online-petition-callout" data-online-petition-update="20260801" aria-labelledby="online-petition-heading">
    <span class="online-petition-kicker">Petici lze podpořit také online</span>
    <h2 id="online-petition-heading">Elektronická petice pokračuje souběžně</h2>
    <p>Vedle podpisových archů je možné petici podpořit také elektronicky na soukromém portálu e-petice.cz. Nejde o státní nástroj ePetice na Portálu občana; podpora se potvrzuje prostřednictvím odkazu zaslaného na uvedený e-mail.</p>
    <p>Online verze obsahuje stejné hlavní požadavky jako listinná petice. <a class="online-petition-link" href="/clanky/epetice-nemocnice-kadan.html">V našem podrobném článku vysvětlujeme způsob potvrzení, rozdíl proti státní ePetici i právní význam online podpory&nbsp;→</a></p>
  </section>
'''
    anchor = '  <section class="signing-infographic" aria-label="Kde a kdy lze petici podepsat">'
    if anchor not in text:
        raise SystemExit('Nenalezeno místo před infografikou.')
    text = text.replace(anchor, block + '\n' + anchor, 1)

# Vzhled boxu vkládáme pouze do tohoto článku a izolovanými třídami.
if '.online-petition-callout{' not in text:
    css = '''.online-petition-callout{margin:32px 0 34px;padding:25px 27px;border:1px solid #cfdde2;border-left:6px solid #14849a;border-radius:0 18px 18px 0;background:linear-gradient(135deg,#eef8fa,#f8fbfc);box-shadow:0 10px 28px rgba(18,43,55,.08)}.online-petition-callout h2{margin:5px 0 12px!important;font-size:30px!important}.online-petition-callout p{margin:0 0 12px}.online-petition-callout p:last-child{margin-bottom:0}.online-petition-kicker{display:block;color:#0f7184;font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.online-petition-link{display:inline;font-weight:850}.online-petition-link:hover{text-decoration-thickness:2px}@media(max-width:700px){.online-petition-callout{padding:21px}.online-petition-callout h2{font-size:27px!important}}'''
    text = text.replace('.source-list{', css + '.source-list{', 1)

# Zpřesnit popisy pro vyhledávače a sdílení.
text = re.sub(
    r'<meta name="description" content="[^"]*">',
    '<meta name="description" content="Petici za zachování Nemocnice Kadaň lze od 3. do 15. srpna podepsat na třech místech a zároveň také elektronicky. Připomínáme změny vedení a právní spory.">',
    text,
    count=1,
)
text = re.sub(
    r'<meta property="og:description" content="[^"]*">',
    '<meta property="og:description" content="Petici lze od 3. do 15. srpna podepsat na třech místech a současně také elektronicky. Přinášíme adresy i souvislosti.">',
    text,
    count=1,
)
text = re.sub(
    r'<meta name="twitter:description" content="[^"]*">',
    '<meta name="twitter:description" content="Kde lze petici podepsat osobně, jak ji podpořit elektronicky a co současné iniciativě předcházelo.">',
    text,
    count=1,
)

modified = '2026-08-01T15:27:00+02:00'
text = re.sub(r'(<meta property="article:modified_time" content=")[^"]+("\s*/?>)', rf'\g<1>{modified}\g<2>', text, count=1)
text = re.sub(r'("dateModified"\s*:\s*")[^"]+("\s*,)', rf'\g<1>{modified}\g<2>', text, count=1)

required = (
    marker,
    'Elektronická petice pokračuje souběžně',
    '/clanky/epetice-nemocnice-kadan.html',
    'data-promos data-context="sidebar"',
    '/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3',
)
for value in required:
    if value not in text:
        raise SystemExit(f'Po úpravě chybí: {value}')

path.write_text(text, encoding='utf-8', newline='\n')
print('Doplněna výrazná informace o elektronické petici.')
