#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / 'clanky' / 'mestska-policie-kadan-fakta-diskuse-2026.html'
SLUG = 'mestska-policie-kadan-fakta-diskuse-2026'
URL = f'https://nasekadan.cz/clanky/{SLUG}.html'
SOCIAL = f'/social/{SLUG}.png'
SOCIAL_URL = f'https://nasekadan.cz/social/{SLUG}.png'
TITLE = 'Neřeší městská policie dopravu? Bouřlivá debata přiměla redakci ověřit fakta'
DESC = ('Kritické vyjádření k práci Městské policie Kadaň vyvolalo bouřlivou debatu. '
        'Ověřili jsme dopravní přestupky, pravomoci strážníků, jejich další práci i aktuálnost oficiálního webu.')
PUBLISHED = '2026-08-07T04:00:00+02:00'

CSS = r'''
.article-shell{display:grid;grid-template-columns:minmax(0,840px) 300px;gap:36px;align-items:start;padding:54px 0 72px}
.article{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}
.article h1{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em;color:#17242d}
.article h2{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px;color:#17242d}
.article h3{font:900 24px/1.2 Georgia,serif;margin:34px 0 12px;color:#17242d}
.article p,.article li{font-size:18px;line-height:1.7}.article a{color:#9f2626;text-underline-offset:3px}
.tag{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}
.back-home{margin:0 0 18px!important;font-size:15px!important;font-weight:850}.back-home a{text-decoration:none}.back-home a:hover{text-decoration:underline}
.leadtext{font-size:23px!important;color:#465862;line-height:1.52!important}.lead{font-size:19px!important;color:#334650}
.hero-image{width:100%;height:auto;border-radius:23px;margin:28px 0 18px;display:block;box-shadow:0 17px 38px #16242d22}
.byline{font-size:14px!important;color:#6b7880;margin:0 0 28px!important}
.evidence-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:30px 0}.evidence-card{padding:22px;border:1px solid #dce3e6;border-radius:17px;background:#f7f9fa}.evidence-card p{font-size:16px!important;margin:12px 0 0}.evidence-name{font-weight:900;font-size:19px;color:#17242d}.evidence-role{font-size:13px;color:#6b7880;margin-top:2px}
.table-wrap{overflow-x:auto;margin:28px 0 14px;border:1px solid #dce3e6;border-radius:16px}.article table{border-collapse:collapse;width:100%;min-width:720px;background:#fff}.article th,.article td{padding:13px 16px;border-bottom:1px solid #e2e7ea;text-align:right;vertical-align:top}.article th:first-child,.article td:first-child{text-align:left}.article thead th{background:#f3f5f6;color:#17242d;font-size:14px}.article tbody tr:last-child td{border-bottom:0;font-weight:800}
.callout{border-left:7px solid #9f2626;background:#f8eeee;padding:22px 25px;margin:30px 0;border-radius:0 18px 18px 0}.callout.good{border-left-color:#317b48;background:#eef8f1}.callout.warn{border-left-color:#d47b00;background:#fff4e3}.callout p:last-child{margin-bottom:0}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:28px 0}.stat{padding:19px;border:1px solid #dce3e6;border-radius:16px;background:#f7f9fa}.stat b{display:block;font:900 28px Georgia,serif;color:#9f2626;margin-bottom:7px}.stat span{font-size:14px;color:#53626b}
.article blockquote{margin:28px 0;padding:21px 24px;border-left:7px solid #9f2626;background:#f8eeee;border-radius:0 18px 18px 0;font:700 21px/1.5 Georgia,serif;color:#263b45}
.verdict{margin:42px 0 0;padding:27px;border:1px solid #cfe2d4;background:#f1faf5;border-radius:18px}.verdict h2{margin:0 0 14px}
.sources{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}.sources h2{margin-top:0}.sources li,.sources p{font-size:14px!important}.sources ol{padding-left:22px}
.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:900 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px;line-height:1.5}.sidebox a{color:#9f2626;font-weight:850}
@media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}.stats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:700px){.article{padding:27px 21px}.article h1{font-size:42px}.leadtext{font-size:20px!important}.evidence-grid,.stats{grid-template-columns:1fr}.article table{min-width:650px}}
'''.strip()

FOOTER = '''<footer class="site-footer" data-site-footer="v1">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="logo" href="/" aria-label="Naše Kadaň – úvodní stránka"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
      <p>Nezávislé informace, události a příběhy města.</p>
    </div>
    <div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div>
    <div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div>
  </div>
  <div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a><a href="/provozovatel/">Provozovatel</a><a href="/cookies/#nastaveni" data-open-privacy-settings>Nastavení soukromí</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div>
</footer>'''


def schema() -> tuple[str, str]:
    news = {
        '@context':'https://schema.org','@type':'NewsArticle','headline':TITLE,'description':DESC,
        'datePublished':PUBLISHED,'dateModified':PUBLISHED,
        'author':{'@type':'Organization','@id':'https://nasekadan.cz/#organization','name':'Naše Kadaň','url':'https://nasekadan.cz/o-webu/'},
        'publisher':{'@id':'https://nasekadan.cz/#organization'},'mainEntityOfPage':{'@type':'WebPage','@id':URL},
        'image':[SOCIAL_URL],'inLanguage':'cs-CZ','isAccessibleForFree':True,
        'about':[{'@type':'GovernmentOrganization','name':'Městská policie Kadaň'},{'@type':'Place','name':'Kadaň'},{'@type':'Thing','name':'Dopravní přestupky'},{'@type':'Thing','name':'Měření rychlosti'},{'@type':'Thing','name':'Ověřování veřejných tvrzení'}],
    }
    crumbs = {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[
        {'@type':'ListItem','position':1,'name':'Naše Kadaň','item':'https://nasekadan.cz/'},
        {'@type':'ListItem','position':2,'name':'Články','item':'https://nasekadan.cz/clanky/'},
        {'@type':'ListItem','position':3,'name':TITLE,'item':URL},
    ]}
    return json.dumps(news,ensure_ascii=False,separators=(',',':')), json.dumps(crumbs,ensure_ascii=False,separators=(',',':'))


def main() -> int:
    if not ARTICLE.is_file():
        raise RuntimeError('Chybí publikovaný článek Městské policie Kadaň.')
    old = ARTICLE.read_text(encoding='utf-8')
    body_match = re.search(r'<div class="content">\s*(.*?)\s*</div>\s*</article>', old, re.S | re.I)
    if not body_match:
        if 'data-article-template="unified-v1"' in old and f'src="{SOCIAL}"' in old and '<a class="logo" href="/"' in old:
            print('Šablona článku o Městské policii je už sjednocená.')
            return 0
        raise RuntimeError('Nelze bezpečně oddělit obsah článku od staré šablony.')
    content = body_match.group(1).strip()
    deck_match = re.search(r'<p class="deck">(.*?)</p>', old, re.S | re.I)
    deck = deck_match.group(1).strip() if deck_match else DESC
    news, crumbs = schema()
    html = f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title><meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260805-event-hotfix-3">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
<script data-nk-newsarticle="1" type="application/ld+json">{news}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{crumbs}</script>
<style>{CSS}</style></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/" aria-label="Naše Kadaň – titulní strana"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="back-home"><a href="/">← Zpět na titulní stranu</a></p><p class="tag">KADAŇ · MĚSTSKÁ POLICIE · DOPRAVA · 7. SRPNA 2026 · 4:00</p><h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>{deck}</strong></p><img class="hero-image" src="{SOCIAL}" width="1200" height="630" alt="Redakční grafika k ověřování práce Městské policie Kadaň"><p class="byline">Redakce Naše Kadaň · 7. srpna 2026 · 4:00</p>
{content}
</article><aside class="sticky"><div class="sidebox"><h3>Městská policie Kadaň</h3><ul><li>24 strážníků vykázaných za rok 2025</li><li>1 886 doložených dopravních přestupkových výsledků ve dvou ministerských kategoriích</li><li>246 opatření na žádost Policie ČR</li></ul></div><div class="sidebox"><h3>Ověřujeme fakta</h3><p>Článek odděluje veřejná tvrzení, osobní zkušenosti a údaje z oficiálních statistik.</p><a href="/">Zpět na titulní stranu →</a></div><div data-promos data-context="sidebar"></div></aside></main>
{FOOTER}<script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/horko-feed.js?v=20260730-heat-rotation-1"></script></body></html>'''
    required = ['data-article-template="unified-v1"', f'src="{SOCIAL}"', '<a class="logo" href="/"', '← Zpět na titulní stranu', 'theme-color" content="#9f2626"', '/style.css']
    missing = [item for item in required if item not in html]
    if missing:
        raise RuntimeError('Opravená šablona postrádá: ' + repr(missing))
    ARTICLE.write_text(html, encoding='utf-8', newline='\n')
    print('Sjednocena šablona článku Městské policie Kadaň včetně obrázku a návratu na titulku.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
