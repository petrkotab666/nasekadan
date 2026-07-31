#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.github/drafts/nebezpeci-pozaru-ustecky-kraj-kadan-2026.html'
ARTICLE = ROOT / 'clanky/nebezpeci-pozaru-ustecky-kraj-kadan-2026.html'
SOCIAL = ROOT / 'social/nebezpeci-pozaru-ustecky-kraj-kadan-2026.png'
TITLE = 'Ústecký kraj znovu omezil rozdělávání ohňů. Opatření platí i pro Kadaň do konce srpna'
DESC = 'Od 29. července 2026 od 15 hodin platí v celém Ústeckém kraji zvýšené nebezpečí vzniku požárů. Přehled zákazů pro Kadaň, Prunéřov, Tušimice a okolí.'
URL = 'https://nasekadan.cz/clanky/nebezpeci-pozaru-ustecky-kraj-kadan-2026.html'
IMAGE = 'https://nasekadan.cz/social/nebezpeci-pozaru-ustecky-kraj-kadan-2026.png'
PUBLISHED = '2026-07-31T09:16:00+02:00'


def font(size: int, bold: bool = False):
    from PIL import ImageFont
    choices = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/dejavu/DejaVuSans.ttf',
    ]
    for path in choices:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def make_social() -> None:
    from PIL import Image, ImageDraw
    w, h = 1200, 630
    im = Image.new('RGB', (w, h), '#10283a')
    px = im.load()
    for y in range(h):
        for x in range(540, w):
            t = (x - 540) / (w - 540)
            v = y / h
            r = int(178 + 70 * t + 18 * (1-v))
            g = int(92 + 75 * t + 45 * (1-v))
            b = int(45 + 26 * (1-t) + 28 * (1-v))
            px[x, y] = (min(r,255), min(g,255), min(b,255))
    d = ImageDraw.Draw(im)
    d.polygon([(500,390),(650,310),(790,350),(930,270),(1200,330),(1200,630),(500,630)], fill='#9b5b2e')
    d.polygon([(520,465),(690,405),(845,445),(1000,365),(1200,410),(1200,630),(520,630)], fill='#6e4028')
    for x in (1010,1065,1125,1170):
        d.rectangle((x,95,x+13,500), fill='#243127')
        d.polygon([(x-70,170),(x+8,75),(x+78,175)], fill='#2d3e2d')
        d.polygon([(x-62,245),(x+8,135),(x+70,245)], fill='#314831')
    d.rectangle((330,123,600,147), fill='#0b1e2d')
    for x, ww, hh in [(355,45,45),(415,58,65),(490,48,52),(552,40,75)]:
        d.rectangle((x,147-hh,x+ww,147), fill='#0b1e2d')
        d.polygon([(x-4,147-hh),(x+ww/2,115-hh),(x+ww+4,147-hh)], fill='#0b1e2d')
    d.rectangle((388,55,402,147), fill='#0b1e2d')
    d.polygon([(377,58),(395,24),(413,58)], fill='#0b1e2d')
    d.polygon([(0,0),(690,0),(620,630),(0,630)], fill='#071c2e')
    d.polygon([(0,39),(300,39),(330,75),(300,111),(0,111)], fill='#0c4e9d')
    d.text((38,55),'Naše Kadaň',font=font(38,True),fill='white')
    d.text((43,155),'Ústecký kraj',font=font(62,True),fill='white')
    d.text((43,225),'znovu omezil',font=font(62,True),fill='white')
    d.text((43,295),'rozdělávání ohňů',font=font(54,True),fill='white')
    d.rectangle((44,367,590,372),fill='#d92c2c')
    d.text((44,392),'Opatření platí i pro Kadaň',font=font(36,True),fill='#ffc247')
    d.text((44,438),'do konce srpna',font=font(36,True),fill='#ffc247')
    d.rounded_rectangle((42,510,645,583),radius=14,fill='#cf2026')
    d.rounded_rectangle((61,527,102,568),radius=6,outline='white',width=4)
    d.line((61,540,102,540),fill='white',width=4)
    d.line((72,520,72,536),fill='white',width=4)
    d.line((91,520,91,536),fill='white',width=4)
    d.text((120,526),'29. 7. 2026, 15:00 – 31. 8. 2026',font=font(26,True),fill='white')
    d.rounded_rectangle((835,145,1124,476),radius=22,fill='#e9ddc9',outline='#772018',width=9)
    d.ellipse((870,190,1090,410),outline='#c51d24',width=25)
    d.polygon([(980,350),(940,318),(958,274),(976,300),(989,230),(1035,292),(1023,340)],fill='#151515')
    d.rectangle((929,355,1038,372),fill='#151515')
    d.line((895,214,1065,385),fill='#c51d24',width=27)
    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    im.save(SOCIAL, 'PNG', optimize=True, compress_level=9)
    with Image.open(SOCIAL) as check:
        assert check.size == (1200, 630) and check.format == 'PNG'


def article_html() -> str:
    draft = DRAFT.read_text(encoding='utf-8')
    match = re.search(r'(<article>.*?</article>)', draft, re.S)
    if not match:
        raise RuntimeError('V konceptu chybí článek.')
    body = match.group(1)
    figure = f'''\n  <figure class="article-photo">\n    <img src="../social/{SOCIAL.name}" width="1200" height="630" loading="eager" fetchpriority="high" alt="Grafika upozorňující na omezení rozdělávání ohně v Ústeckém kraji">\n    <figcaption>Opatření platí pro celé území Ústeckého kraje. Ilustrační grafika: Naše Kadaň</figcaption>\n  </figure>'''
    body = re.sub(r'(</p>\s*\n\s*<p>Krajský úřad)', figure + r'\n\n  <p>Krajský úřad', body, count=1)
    linked_sources = '''<section class="source-list">\n    <h2>Zdroje</h2>\n    <ul>\n      <li><a href="https://www.kr-ustecky.cz/vystraha-pro-zvysene-nebezpeci-vzniku-pozaru-opet-v-platnosti" target="_blank" rel="noopener noreferrer">Ústecký kraj – aktuální vyhlášení</a>, aktualizováno 29. července 2026.</li>\n      <li><a href="https://www.mesto-kadan.cz/cs/system/uredni-deska-nova.html" target="_blank" rel="noopener noreferrer">Úřední deska města Kadaň</a>, MUKK/33218/2026.</li>\n      <li><a href="https://archiv.kr-ustecky.cz/pozarni-ochrana-narizeni-usteckeho-kraje/d-1669434" target="_blank" rel="noopener noreferrer">Nařízení Ústeckého kraje č. 5/2003</a>.</li>\n    </ul>\n    <p><small>Stav ověřen 31. července 2026 v 9:16.</small></p>\n  </section>'''
    body = re.sub(r'<section class="source-list">.*?</section>', linked_sources, body, flags=re.S)
    body = body.replace('<h2>Kraj opatření obnovil po několika dnech</h2>', '<p>Sucho se na Kadaňsku projevilo také <a href="/clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html">zákazem odběru vody ze čtrnácti toků</a>.</p>\n\n  <h2>Kraj opatření obnovil po několika dnech</h2>')
    aside = '''<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>Celý Ústecký kraj</li><li>Od 29. července, 15:00</li><li>Do 31. srpna 2026</li><li>Oheň a kouření u lesa zakázány</li><li>Bez plošného zákazu vstupu do lesa</li></ul></div><div data-promos data-context="sidebar"></div></aside>'''
    style = '''.article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}.article h1{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}.article h2{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}.article p,.article li{font-size:18px;line-height:1.7}.leadtext{font-size:23px!important;color:#465862;line-height:1.55!important}.article a{color:#9f2626;text-decoration:underline;text-underline-offset:3px}.article-photo{margin:30px 0}.article-photo img{display:block;width:100%;height:auto;border-radius:24px;box-shadow:0 14px 38px #16242d1c}.article-photo figcaption{font-size:14px;color:#677780;margin-top:9px}.callout{border-left:6px solid #9f2626;background:#f7f1e7;padding:22px 26px;border-radius:0 16px 16px 0;margin:30px 0}.callout strong{display:block;font:800 24px Georgia,serif;margin-bottom:7px}.callout p{margin:0}.source-list{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}.source-list li{font-size:15px;margin-bottom:8px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px}@media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}@media(max-width:700px){.article h1{font-size:42px}.leadtext{font-size:20px!important}}'''
    news = '{"@context":"https://schema.org","@type":"NewsArticle","headline":"'+TITLE+'","description":"'+DESC+'","datePublished":"'+PUBLISHED+'","dateModified":"'+PUBLISHED+'","author":{"@type":"Organization","@id":"https://nasekadan.cz/#organization","name":"Naše Kadaň","url":"https://nasekadan.cz/o-webu/"},"publisher":{"@id":"https://nasekadan.cz/#organization"},"mainEntityOfPage":{"@type":"WebPage","@id":"'+URL+'"},"inLanguage":"cs-CZ","image":["'+IMAGE+'"],"isAccessibleForFree":true}'
    crumbs = '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Naše Kadaň","item":"https://nasekadan.cz/"},{"@type":"ListItem","position":2,"name":"Články","item":"https://nasekadan.cz/clanky/"},{"@type":"ListItem","position":3,"name":"'+TITLE+'","item":"'+URL+'"}]}'
    header = '''<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>'''
    footer = '''<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/o-webu/#provozovatel">Provozovatel</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>'''
    return f'''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE} | Naše Kadaň</title><meta name="description" content="{DESC}"><link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css"><link rel="canonical" href="{URL}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{TITLE}"><meta property="og:description" content="{DESC}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{IMAGE}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{TITLE}"><meta name="twitter:description" content="{DESC}"><meta name="twitter:image" content="{IMAGE}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}"><style>{style}</style><script type="application/ld+json">{news}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{crumbs}</script><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2"></head><body>{header}<main class="wrap article-shell" data-article-template="unified-v1">{body}{aside}</main>{footer}<script src="/site.js" defer></script><script src="/reklamy.js"></script><script src="/reklamy-oprava-obrazku.js"></script><script src="/obsah-doplnky.js"></script><script src="/horko-feed.js"></script></body></html>'''


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> int:
    if not DRAFT.is_file():
        raise RuntimeError('Chybí ověřený redakční koncept.')
    make_social()
    ARTICLE.parent.mkdir(parents=True, exist_ok=True)
    ARTICLE.write_text(article_html(), encoding='utf-8', newline='\n')
    run('scripts/enforce_current_article_order.py')
    run('scripts/finalize_launch.py')
    run('scripts/enforce_current_article_order.py')
    html = ARTICLE.read_text(encoding='utf-8')
    required = [TITLE, IMAGE, PUBLISHED, 'MUKK/33218/2026']
    assert all(x in html for x in required)
    href = '/clanky/' + ARTICLE.name
    absolute = 'https://nasekadan.cz' + href
    assert href in (ROOT/'index.html').read_text(encoding='utf-8')
    assert href in (ROOT/'clanky/index.html').read_text(encoding='utf-8')
    assert absolute in (ROOT/'rss.xml').read_text(encoding='utf-8')
    assert absolute in (ROOT/'sitemap.xml').read_text(encoding='utf-8')
    assert absolute in (ROOT/'news-sitemap.xml').read_text(encoding='utf-8')
    print('Článek, sociální obrázek a všechny veřejné přehledy jsou připravené.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
