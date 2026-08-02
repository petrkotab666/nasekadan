#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from email.utils import format_datetime
from html import escape
import json, re, subprocess, textwrap
import markdown
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
DRAFT=ROOT/'.github/drafts/fve-epr-letiste-bess-kadan-2026.md'
SLUG='fve-epr-letiste-bess-kadan-2026'
ARTICLE=ROOT/'clanky'/f'{SLUG}.html'
SOCIAL=ROOT/'social/fve-epr-letiste-baterie-kadan-20260803.png'
URL=f'https://nasekadan.cz/clanky/{SLUG}.html'
REL=f'/clanky/{SLUG}.html'
TITLE='ČEZ chce u Kadaně postavit solární park s bateriemi. Jejich velikost, cena i platby městu zůstávají neznámé'
DESC='ČEZ chce k připravované FVE EPR Letiště v Tušimicích doplnit bateriové úložiště. Veřejné dokumenty neukazují jeho přesný výkon, kapacitu, cenu ani výši plateb městu.'
PUBLISHED='2026-08-03T10:30:00+02:00'
IMAGE_URL=f'https://nasekadan.cz/social/{SOCIAL.name}'
RSS_DATE=format_datetime(datetime.fromisoformat(PUBLISHED))

def write(p,s): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')

def body():
    raw=DRAFT.read_text(encoding='utf-8')
    raw=raw.split('\n---\n',1)[1] if '\n---\n' in raw else raw
    raw=re.sub(r'^# .*?\n+','',raw,count=1)
    raw=raw.replace('K původní solární elektrárně má přibýt','K připravované solární elektrárně má přibýt')
    raw=raw.replace('ČEZ přidává k solárnímu parku u Kadaně baterie. Přesnou kapacitu ani platby městu veřejné dokumenty neukazují',TITLE)
    clarify='''<div class="clarify"><strong>Solární park zatím není v provozu</strong><p>ČEZ má pro FVE EPR Letiště vydané povolení a nyní žádá o změnu záměru před dokončením. Veřejné dokumenty nedokládají, že by byl celý park již dokončen a vyráběl elektřinu.</p></div>\n\n'''
    raw=clarify+raw
    leti='''## Proč se projektu říká „Letiště“, když tu žádné letiště není?

Název může místní čtenáře snadno zmást. Panely ale nemají vzniknout na letištní dráze a součástí projektu není letiště pro letadla.

<div class="namebox"><div class="namebox-icon">EPR</div><div><h3>„Letiště“ je starý název lokality</h3><p>ČEZ už v dubnu 2007 popisoval jedno ze složišť pro prunéřovské elektrárny, kterému se říkalo <strong>Letiště</strong>. Šlo o prostor mezi Tušimicemi a Prunéřovem.</p><p>Složiště se tehdy uzavíralo a připravovalo k rekultivaci. Současný solární projekt převzal název této starší lokality.</p></div></div>

Zkratka **EPR** v tomto případě odkazuje na Elektrárny Prunéřov. Celé označení FVE EPR Letiště lze proto chápat jako pracovní název fotovoltaické elektrárny v prunéřovské lokalitě zvané Letiště.

**Proč se samotnému složišti začalo říkat právě Letiště, se v autoritativních podkladech vysvětlit nepodařilo.** Domněnku, že šlo o odkaz na velkou rovnou plochu, proto neuvádíme jako fakt.

'''
    marker='## Solární park má vzniknout na rekultivovaném území'
    if 'Proč se projektu říká „Letiště“' not in raw: raw=raw.replace(marker,leti+marker,1)
    if 'Tisková zpráva ČEZ z roku 2007' not in raw:
        raw += '\n- [Tisková zpráva ČEZ z roku 2007 – lokalita zvaná Letiště](https://ekolist.cz/cz/zpravodajstvi/tiskove-zpravy/z-tusimickeho-sloziste-popilku-bude-prazska-periferie)\n'
    return markdown.markdown(raw,extensions=['extra','sane_lists'])

def page():
    schema={'@context':'https://schema.org','@type':'NewsArticle','headline':TITLE,'description':DESC,'datePublished':PUBLISHED,'dateModified':PUBLISHED,'author':{'@type':'Organization','@id':'https://nasekadan.cz/#organization','name':'Naše Kadaň','url':'https://nasekadan.cz/o-webu/'},'publisher':{'@id':'https://nasekadan.cz/#organization'},'mainEntityOfPage':{'@type':'WebPage','@id':URL},'image':[IMAGE_URL],'inLanguage':'cs-CZ','isAccessibleForFree':True}
    return f'''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title><meta name="description" content="{escape(DESC)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><link rel="canonical" href="{URL}"><link rel="stylesheet" href="../style.css">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE)}"><meta property="og:description" content="{escape(DESC)}"><meta property="og:url" content="{URL}"><meta name="nasekadan:social-card" content="custom"><meta property="og:image" content="{IMAGE_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE)}"><meta name="twitter:description" content="{escape(DESC)}"><meta name="twitter:image" content="{IMAGE_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<style>.article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}}.article h1{{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}}.article h2{{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}}.article h3{{font:800 25px/1.2 Georgia,serif;margin:30px 0 10px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-decoration:underline;text-underline-offset:3px}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.55!important}}.clarify{{background:#fff7ec;border:1px solid #ead4af;border-left:7px solid #cb7a18;border-radius:0 16px 16px 0;padding:20px 23px;margin:28px 0}}.clarify strong{{display:block;font:800 24px Georgia,serif;color:#6f4310;margin-bottom:7px}}.clarify p{{margin:0}}.namebox{{display:grid;grid-template-columns:80px 1fr;gap:20px;align-items:start;background:#edf5f7;border:1px solid #d0e0e5;border-radius:20px;padding:24px 26px;margin:30px 0}}.namebox-icon{{display:grid;place-items:center;width:80px;height:80px;border-radius:50%;background:#173f54;color:#fff;font:800 27px Georgia,serif}}.namebox h3{{margin:0 0 8px;color:#173f54}}.namebox p{{margin:0 0 9px}}.source-list,.article>ul:last-of-type{{background:#eef3f5;padding:24px;border-radius:18px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:800 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:700px){{.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.namebox{{grid-template-columns:1fr}}}}</style>
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script><link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2"><meta name="theme-color" content="#9f2626"></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="tag">ENERGETIKA · TUŠIMICE · VEŘEJNÉ DOKUMENTY · 3. SRPNA 2026 · 10:30</p><h1>{escape(TITLE)}</h1><p class="leadtext"><strong>{escape(DESC)} Nejde o součást připravované jaderné elektrárny.</strong></p>{body()}</article>
<aside class="sticky"><div class="sidebox"><h3>Nejdůležitější upřesnění</h3><p><strong>Park zatím není v provozu.</strong> Jde o povolený projekt, který ČEZ před dokončením mění.</p><p><strong>„Letiště“ není letiště pro letadla.</strong> Je to historický název rekultivované lokality někdejšího složiště.</p></div><div class="sidebox"><h3>Stále chybí</h3><ul><li>MW a MWh baterie</li><li>počet kontejnerů</li><li>cena a harmonogram</li><li>požární řešení</li><li>platby městu</li></ul></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script></body></html>'''

def social():
    SOCIAL.parent.mkdir(parents=True,exist_ok=True);W,H=1200,630;im=Image.new('RGB',(W,H),(19,40,50));d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H;d.line([(0,y),(W,y)],fill=(int(19*(1-t)+80*t),int(40*(1-t)+66*t),int(50*(1-t)+55*t)))
    d.rectangle([0,0,18,H],fill=(159,38,38));d.rectangle([0,H-18,W,H],fill=(200,164,88))
    for row,yy in enumerate((330,420)):
        for col in range(4):
            x=650+col*125+row*25;d.polygon([(x,yy),(x+105,yy-28),(x+118,yy+32),(x+12,yy+60)],fill=(28,68,91),outline=(120,170,190))
    bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    d.text((58,48),'NAŠE KADAŇ',font=ImageFont.truetype(bold,36),fill='white');d.rounded_rectangle([58,118,350,165],radius=18,fill=(159,38,38));d.text((78,128),'ENERGETIKA • TUŠIMICE',font=ImageFont.truetype(bold,23),fill='white')
    y=205
    for line in textwrap.wrap('ČEZ chce u Kadaně solární park s bateriemi',width=28): d.text((58,y),line,font=ImageFont.truetype(bold,54),fill='white');y+=65
    d.text((60,500),'Velikost, cena i platby městu zůstávají neznámé',font=ImageFont.truetype(reg,27),fill=(232,239,242));im.save(SOCIAL,optimize=True)

def feeds():
    p=ROOT/'rss.xml';s=p.read_text(encoding='utf-8');s=re.sub(r'\s*<item>.*?<link>'+re.escape(URL)+r'</link>.*?</item>\s*','\n',s,flags=re.S)
    item=f'    <item><title>{escape(TITLE)}</title><description><![CDATA[{DESC}]]></description><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{RSS_DATE}</pubDate><category>Energetika</category><category>Tušimice</category><szn:image><szn:url>{IMAGE_URL}</szn:url></szn:image></item>\n\n'
    s=re.sub(r'<lastBuildDate>.*?</lastBuildDate>',f'<lastBuildDate>{RSS_DATE}</lastBuildDate>',s,count=1);s=s.replace('    <item>',item+'    <item>',1);write(p,s)
    p=ROOT/'sitemap.xml';s=p.read_text(encoding='utf-8');s=re.sub(r'\s*<url>\s*<loc>'+re.escape(URL)+r'</loc>.*?</url>\s*','\n',s,flags=re.S);s=s.replace('</urlset>',f'  <url><loc>{URL}</loc><lastmod>2026-08-03</lastmod></url>\n</urlset>');write(p,s)

def validate():
    a=ARTICLE.read_text(encoding='utf-8')
    for x in (TITLE,'Solární park zatím není v provozu','„Letiště“ je starý název lokality','data-promos data-context="sidebar"','/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3'): assert x in a,x
    assert 'noindex' not in a
    for n in ('index.html','clanky/index.html','rss.xml','sitemap.xml','news-sitemap.xml','llms.txt'):
        s=(ROOT/n).read_text(encoding='utf-8');assert REL in s or URL in s,n
    assert SOCIAL.stat().st_size>10000

def main():
    write(ARTICLE,page());social();subprocess.run(['python3',str(ROOT/'scripts/enforce_article_visibility.py')],check=True,cwd=ROOT);feeds();subprocess.run(['python3',str(ROOT/'scripts/prepare_discovery.py')],check=True,cwd=ROOT);validate();print('FVE EPR Letiště připraveno.')

if __name__=='__main__': main()
