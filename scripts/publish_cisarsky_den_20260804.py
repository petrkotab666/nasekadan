#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from email.utils import format_datetime
import json
from pathlib import Path
import re
import subprocess
import textwrap
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.github/drafts/cisarsky-den-kadan-historie-2026.html'
ARTICLE = ROOT / 'clanky/cisarsky-den-kadan-historie-2026.html'
SOCIAL = ROOT / 'social/cisarsky-den-kadan-2026-20260804.png'
URL = 'https://nasekadan.cz/clanky/cisarsky-den-kadan-historie-2026.html'
REL = '/clanky/cisarsky-den-kadan-historie-2026.html'
TITLE = 'Kadaň znovu vítá císaře: Co přinese Císařský den 2026 a jak celý příběh začal'
META_TITLE = 'Kadaň znovu vítá císaře: Císařský den 2026 | Naše Kadaň'
DESC = 'Císařský den 2026 v Kadani se koná 22. srpna od 10 do 22 hodin. Přinášíme potvrzené časy, praktické informace a velký příběh města od Karla IV. po současnost.'
IMAGE_URL = 'https://nasekadan.cz/social/cisarsky-den-kadan-2026-20260804.png'
PUBLISHED = datetime(2026, 8, 4, 18, 0, tzinfo=ZoneInfo('Europe/Prague'))
PUBLISHED_ISO = PUBLISHED.isoformat()
RSS_DATE = format_datetime(PUBLISHED)
DATE_ISO = PUBLISHED.date().isoformat()
EXPECTED_GENERATED = {
    'clanky/cisarsky-den-kadan-historie-2026.html',
    'social/cisarsky-den-kadan-2026-20260804.png',
    'index.html', 'clanky/index.html', 'rss.xml', 'sitemap.xml', 'news-sitemap.xml'
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def guard_release_window(force: bool, dry_run: bool) -> None:
    now = datetime.now(ZoneInfo('Europe/Prague'))
    if not force and not dry_run and now < PUBLISHED:
        raise SystemExit(f'Publikace je uzamčena do {PUBLISHED_ISO}; nyní je {now.isoformat()}.')


def build_article() -> str:
    text = DRAFT.read_text(encoding='utf-8')
    text = re.sub(r'<title>.*?</title>', f'<title>{META_TITLE}</title>', text, count=1, flags=re.S)
    text = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{DESC}">', text, count=1)
    text = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">', text, count=1)
    text = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{URL}">', text, count=1)
    text = re.sub(r'\s*<meta (?:property="(?:og:|article:)[^"]+"|name="(?:twitter:[^"]+|nasekadan:social-card)")[^>]*>', '', text)
    text = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', text, flags=re.S)
    schema = {
        '@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': TITLE,
        'description': DESC, 'datePublished': PUBLISHED_ISO, 'dateModified': PUBLISHED_ISO,
        'author': {'@type': 'Organization', '@id': 'https://nasekadan.cz/#organization', 'name': 'Naše Kadaň', 'url': 'https://nasekadan.cz/o-webu/'},
        'publisher': {'@id': 'https://nasekadan.cz/#organization'},
        'mainEntityOfPage': {'@type': 'WebPage', '@id': URL}, 'image': [IMAGE_URL],
        'inLanguage': 'cs-CZ', 'isAccessibleForFree': True,
        'about': [{'@type': 'Event', 'name': 'Císařský den 2026', 'startDate': '2026-08-22T10:00:00+02:00', 'endDate': '2026-08-22T22:00:00+02:00', 'eventStatus': 'https://schema.org/EventScheduled', 'location': {'@type': 'Place', 'name': 'Historické centrum Kadaně', 'address': {'@type': 'PostalAddress', 'addressLocality': 'Kadaň', 'addressCountry': 'CZ'}}}]
    }
    extras = f'''
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="{TITLE}">
  <meta property="og:description" content="{DESC}">
  <meta property="og:url" content="{URL}">
  <meta name="nasekadan:social-card" content="custom">
  <meta property="og:image" content="{IMAGE_URL}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE}">
  <meta name="twitter:description" content="{DESC}">
  <meta name="twitter:image" content="{IMAGE_URL}">
  <meta property="article:published_time" content="{PUBLISHED_ISO}">
  <meta property="article:modified_time" content="{PUBLISHED_ISO}">
  <link rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml">
  <link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
  <meta name="theme-color" content="#7f1d1d">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
'''
    text = text.replace('</head>', extras + '</head>', 1)
    text = re.sub(r'<h1>.*?</h1>', f'<h1>{TITLE}</h1>', text, count=1, flags=re.S)
    text = re.sub(r'<p class="leadtext">.*?</p>', '<p class="leadtext"><strong>V sobotu 22. srpna se historické centrum Kadaně znovu promění v císařské město. Přinášíme potvrzené časy hlavních okamžiků, praktický servis pro návštěvníky a rozsáhlý příběh skutečných návštěv Karla IV., vzniku novodobé slavnosti i proměn Kadaně až do současnosti.</strong></p>', text, count=1, flags=re.S)
    text = re.sub(r'<p class="tag">.*?</p>', '<p class="tag">KULTURA · HISTORIE · 4. SRPNA 2026 V 18:00</p>', text, count=1, flags=re.S)

    practical = '''
  <p class="updated">Průběžně aktualizujeme podle oficiálních informací pořadatelů.</p>
  <nav class="jump-nav" aria-label="Obsah článku"><a href="#program">Program 2026</a><a href="#prakticky">Praktické informace</a><a href="#historie">Karel IV. v Kadani</a><a href="#slavnost">Vznik slavnosti</a><a href="#rocniky">Počet ročníků</a><a href="#kadan1367">Kadaň roku 1367</a></nav>
  <section class="quick" id="program" aria-labelledby="quickTitle">
    <span class="status-badge">POTVRZENO POŘADATELEM</span><h2 id="quickTitle">Císařský den 2026 – rychlý přehled</h2><p>Sobota 22. srpna 2026 · historické centrum Kadaně · 10:00–22:00</p>
    <div class="quick-grid"><article class="quick-card"><time>14:00</time><b>Odchod císařského průvodu</b><span>Od františkánského kláštera.</span></article><article class="quick-card"><time>14:30</time><b>Slavnostní ceremonie</b><span>Mírové náměstí.</span></article><article class="quick-card"><time>18:00</time><b>Rytířský turnaj na koních</b><span>Smetanovy sady.</span></article></div>
    <p class="quick-note"><strong>Potvrzený rámec dne:</strong> Kulturní zařízení Kadaň uvádí konání od 10 do 22 hodin. Úplný rozpis všech scén a vystoupení zatím zveřejněn nebyl.</p>
  </section>
  <section class="game-cta"><p class="eyebrow">INTERAKTIVNÍ HISTORIE · START 12. SRPNA V 18:00</p><h2>Dokázali byste připravit Kadaň na příjezd Karla IV.?</h2><p>Pět let po ničivém požáru zbývá do císařovy návštěvy šest týdnů. Rozhodněte, co opravit, jak zabezpečit město a zda dokážete udržet obyvatele, zásoby, pořádek, pokladnu i císařskou přízeň v rovnováze.</p><p>Hru Příjezd císaře: Kadaň 1367 spustíme ve středu 12. srpna v 18:00. Před zveřejněním projde samostatnou živou kontrolou.</p><span class="game-button" aria-disabled="true">Hru spustíme 12. srpna v 18:00</span></section>
  <h2 id="prakticky">Co už je potvrzené a na co čekáme</h2>
  <div class="fact-status"><article class="fact-box confirmed"><b>POTVRZENO PRO ROK 2026</b><p>Datum, čas 10:00–22:00, 34. ročník a tři hlavní časy.</p></article><article class="fact-box tradition"><b>TRADIČNÍ SOUČÁST SLAVNOSTI</b><p>Tržiště, řemesla, hudba, dětské úkoly, vojenské ležení a večerní finále. Pro rok 2026 je zatím nevydáváme za úplný program.</p></article><article class="fact-box waiting"><b>ČEKÁME NA ZVEŘEJNĚNÍ</b><p>Podrobný harmonogram, mapa, parkování, uzavírky, zvláštní doprava, vstupné a změny kvůli počasí.</p></article></div>
  <div class="practical"><article><h3>Parkování a uzavírky</h3><p>Zatím nebyly zveřejněny.</p></article><article><h3>Vstupné</h3><p>Pro rok 2026 zatím nemáme potvrzené podmínky.</p></article><article><h3>Historické vlaky</h3><p>Pro rok 2026 zatím nepotvrzeno.</p></article><article><h3>Bezbariérovost a rodiny</h3><p>Podrobnosti čekají na zveřejnění.</p></article></div>
'''
    text = text.replace('<h2>Největší kulturní akce města</h2>', practical + '\n<h2>Největší kulturní akce města</h2>', 1)
    text = re.sub(r'\s*<h2>Co je zatím zveřejněno pro rok 2026</h2>.*?(?=<section data-actual-editions)', '\n', text, count=1, flags=re.S)
    text = re.sub(r'\s*<div class="sidebox editor">.*?</div>', '', text, count=1, flags=re.S)
    text = re.sub(r'<small>Před vydáním aktualizovat.*?</small>', '<small>Článek průběžně aktualizujeme podle oficiálních a důvěryhodných veřejných zdrojů.</small>', text, count=1, flags=re.S)
    text = text.replace('<main class="wrap article-shell">', '<main class="wrap article-shell" data-article-template="unified-v1">', 1)

    css = '''
    .updated{display:inline-flex;background:#f7f0e6;border:1px solid #e5d2ad;border-radius:999px;padding:8px 13px;font-size:14px!important;color:#634b23}.jump-nav{display:flex;gap:9px;flex-wrap:wrap;margin:22px 0}.jump-nav a{background:#fff;border:1px solid var(--line);border-radius:999px;padding:9px 13px;text-decoration:none;font-weight:800}.quick{background:#fff8e9;border:1px solid #e8d3a4;border-radius:22px;padding:25px;margin:30px 0}.status-badge{background:#e9f5ed;color:#1f6b38;border-radius:999px;padding:7px 10px;font-size:12px;font-weight:900}.quick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.quick-card{background:#fff;border:1px solid #eadbb9;border-radius:16px;padding:16px}.quick-card time{display:block;font:900 28px Georgia;color:#821f27}.quick-card b,.quick-card span{display:block}.game-cta{background:linear-gradient(135deg,#36151a,#7f1d1d);border-radius:23px;color:#fff;padding:28px;margin:34px 0}.game-cta h2{color:#fff}.game-cta .eyebrow{color:#f0cd8d;font-size:12px!important;font-weight:900}.game-button{display:inline-flex;background:#f1ce86;color:#3d2410;border-radius:12px;padding:11px 17px;font-weight:900}.fact-status{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.fact-box,.practical article{border:1px solid var(--line);border-radius:16px;padding:17px}.fact-box p,.practical p{font-size:15px!important}.practical{display:grid;grid-template-columns:1fr 1fr;gap:13px}@media(max-width:800px){.quick-grid,.fact-status,.practical{grid-template-columns:1fr}}
'''
    text = text.replace('</style>', css + '</style>', 1)
    aside = re.search(r'(<aside\b[^>]*class="sticky"[^>]*>)(.*?)(</aside>)', text, re.S)
    if aside:
        body = re.sub(r'\s*<div data-promos[^>]*>.*?</div>', '', aside.group(2), flags=re.S).rstrip()
        body += '\n<div data-promos data-context="sidebar"></div>\n'
        text = text[:aside.start()] + aside.group(1) + body + aside.group(3) + text[aside.end():]
    scripts = '<script src="/analytics.js" defer></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script>'
    text = text.replace('</body>', scripts + '</body>', 1)
    return text


def social_image() -> None:
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), (31, 18, 22)); px = img.load()
    for y in range(H):
        for x in range(W):
            t = x / W; px[x, y] = (int(40*(1-t)+113*t), int(22*(1-t)+38*t), int(28*(1-t)+41*t))
    draw = ImageDraw.Draw(img); draw.rectangle((0,520,W,H), fill=(22,17,20))
    draw.polygon([(740,520),(740,320),(790,280),(840,320),(840,520)], fill=(20,15,18)); draw.rectangle((765,350,815,520), fill=(20,15,18)); draw.polygon([(890,520),(890,380),(930,325),(970,380),(970,520)], fill=(20,15,18)); draw.rectangle((1010,410,1080,520), fill=(20,15,18))
    gold=(218,183,106); white=(255,250,237); burg=(152,33,42); bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'; regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    draw.ellipse((900,70,1135,305), outline=gold, width=8); draw.text((960,128),'1367',font=ImageFont.truetype(bold,54),fill=white); draw.text((954,205),'KADAŇ',font=ImageFont.truetype(bold,28),fill='white')
    draw.text((64,45),'NAŠE KADAŇ',font=ImageFont.truetype(bold,34),fill='white'); draw.rounded_rectangle((64,102,345,150),radius=18,fill=burg); draw.text((83,111),'CÍSAŘSKÝ DEN 2026',font=ImageFont.truetype(bold,22),fill='white')
    y=190; font=ImageFont.truetype(serif,55)
    for line in ['Kadaň znovu', 'vítá císaře']:
        draw.text((64,y),line,font=font,fill=white); y+=70
    for line in textwrap.wrap('Program, historie a příběh města od Karla IV. po současnost', width=45):
        draw.text((66,y+5),line,font=ImageFont.truetype(regular,28),fill=(230,222,207)); y+=38
    draw.rounded_rectangle((64,545,290,595),radius=18,fill='white'); draw.text((86,556),'22. 8. 2026',font=ImageFont.truetype(bold,23),fill=(80,26,31)); draw.rounded_rectangle((310,545,525,595),radius=18,fill=gold); draw.text((334,556),'10:00–22:00',font=ImageFont.truetype(bold,23),fill=(45,27,29))
    SOCIAL.parent.mkdir(parents=True, exist_ok=True); img.save(SOCIAL, optimize=True)


def update_home() -> None:
    path=ROOT/'index.html'; text=path.read_text(encoding='utf-8')
    hero='''<article class="lead"><div class="photo" style="background:linear-gradient(135deg,#36151a,#7f1d1d 58%,#c8a35a)"><span>CÍSAŘSKÝ DEN 2026</span><strong>1367</strong></div><div class="copy"><small>KULTURA · HISTORIE · 4. 8. 2026 V 18:00</small><h1>Kadaň znovu vítá císaře: Co přinese Císařský den 2026 a jak celý příběh začal</h1><p>Potvrzené časy, praktický servis a velký příběh Kadaně.</p><a class="btn" href="/clanky/cisarsky-den-kadan-historie-2026.html">Přečíst článek →</a></div></article>'''
    text,count=re.subn(r'<article class="lead">.*?</article>',hero,text,count=1,flags=re.S)
    if count!=1: raise SystemExit('Nepodařilo se vyměnit hlavní článek.')
    text=re.sub(r'data-latest-article-href="[^"]+"',f'data-latest-article-href="{REL}"',text,count=1); write(path,text)


def update_archive() -> None:
    path=ROOT/'clanky/index.html'; text=path.read_text(encoding='utf-8')
    text=re.sub(r'\s*<article\b[^>]*data-auto-article="cisarsky-den-2026"[^>]*>.*?</article>\s*','\n',text,flags=re.S)
    item='''<article class="article-card service" data-auto-article="cisarsky-den-2026"><div class="visual" style="background:linear-gradient(135deg,#36151a,#7f1d1d 58%,#c8a35a)"><strong>Kadaň znovu vítá císaře</strong></div><div class="article-body"><span class="meta">4. 8. 2026 · 18:00 · Kultura · Historie</span><h3>Kadaň znovu vítá císaře: Co přinese Císařský den 2026 a jak celý příběh začal</h3><p>Potvrzené časy, praktický servis a rozsáhlá historie.</p><a class="read-more" href="/clanky/cisarsky-den-kadan-historie-2026.html">Přečíst článek →</a></div></article>'''
    marker='<section class="archive-list" aria-label="Chronologický přehled článků">'
    if marker not in text: raise SystemExit('Archiv nemá očekávaný seznam článků.')
    text=text.replace(marker,marker+item,1); write(path,text)


def update_feeds() -> None:
    p=ROOT/'rss.xml'; text=p.read_text(encoding='utf-8'); text=re.sub(r'<lastBuildDate>.*?</lastBuildDate>',f'<lastBuildDate>{RSS_DATE}</lastBuildDate>',text,count=1)
    if URL not in text:
        item=f'<item><title>{TITLE}</title><description><![CDATA[{DESC}]]></description><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{RSS_DATE}</pubDate><category>Kultura</category><category>Historie</category><category>Kadaň</category><szn:image><szn:url>{IMAGE_URL}</szn:url></szn:image></item>\n'
        text=text.replace('<item>',item+'<item>',1)
    write(p,text)
    p=ROOT/'sitemap.xml'; text=p.read_text(encoding='utf-8')
    if URL not in text: text=text.replace('</urlset>',f'<url><loc>{URL}</loc><lastmod>{DATE_ISO}</lastmod></url></urlset>')
    write(p,text)
    p=ROOT/'news-sitemap.xml'
    if p.exists():
        text=p.read_text(encoding='utf-8')
        if URL not in text: text=text.replace('</urlset>',f'<url><loc>{URL}</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>{PUBLISHED_ISO}</news:publication_date><news:title>{TITLE}</news:title></news:news></url></urlset>')
        write(p,text)


def validate() -> None:
    text=ARTICLE.read_text(encoding='utf-8')
    required=[TITLE,'10:00–22:00','14:00','14:30','18:00',URL,IMAGE_URL,'NewsArticle','index,follow,max-image-preview:large','Hru spustíme 12. srpna v 18:00']
    missing=[x for x in required if x not in text]
    if missing: raise SystemExit(f'Článek postrádá: {missing}')
    forbidden=['PŘIPRAVOVANÝ ČLÁNEK','Stav návrhu','vstup zdarma','href="/hry/prijezd-karla-iv/"']
    found=[x for x in forbidden if x.lower() in text.lower()]
    if found: raise SystemExit(f'Článek obsahuje nepovolené prvky: {found}')
    with Image.open(SOCIAL) as image:
        if image.size!=(1200,630): raise SystemExit('Sociální karta nemá 1200 × 630.')
    for rel in ('index.html','clanky/index.html','rss.xml','sitemap.xml','news-sitemap.xml'):
        p=ROOT/rel
        if p.exists() and REL not in p.read_text(encoding='utf-8') and URL not in p.read_text(encoding='utf-8'): raise SystemExit(f'{rel} neobsahuje článek.')


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument('--dry-run',action='store_true'); parser.add_argument('--force',action='store_true'); args=parser.parse_args()
    guard_release_window(args.force,args.dry_run)
    write(ARTICLE,build_article()); social_image(); update_home(); update_archive(); update_feeds()
    protector=ROOT/'scripts/ensure_recent_home_articles_20260801.py'
    if protector.exists(): subprocess.run(['python3',str(protector)],check=True,cwd=ROOT)
    validate()
    changed=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines(); unexpected=set(changed)-EXPECTED_GENERATED
    if unexpected: raise SystemExit(f'Neočekávané změny: {sorted(unexpected)}')
    print('Publikační balíček Císařského dne je validní.'); print('\n'.join(changed))

if __name__=='__main__': main()
