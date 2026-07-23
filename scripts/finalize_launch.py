#!/usr/bin/env python3
from pathlib import Path
from html import escape
import json,re

ROOT=Path(__file__).resolve().parents[1]
BASE='https://nasekadan.cz'
OG_IMAGE=f'{BASE}/social-preview.png'

EXCLUDE_DIRS={'.git','.github','newsletter','scripts','deploy','nginx'}

def desc_from_html(text):
 m=re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)',text,re.I)
 if not m:
  m=re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',text,re.I)
 return m.group(1).strip() if m else 'Aktuální informace, události, praktické rady a příběhy z Kadaně.'

def title_from_html(text):
 m=re.search(r'<title>(.*?)</title>',text,re.I|re.S)
 return re.sub(r'\s+',' ',m.group(1)).strip() if m else 'Naše Kadaň'

def canonical_for(path):
 rel=path.relative_to(ROOT).as_posix()
 if rel=='index.html': return BASE+'/'
 if rel.endswith('/index.html'): return BASE+'/'+rel[:-10]
 return BASE+'/'+rel

def add_head_meta(text,path):
 title=title_from_html(text);desc=desc_from_html(text);canonical=canonical_for(path)
 text=re.sub(r'<link[^>]+rel=["\']canonical["\'][^>]*>','',text,flags=re.I)
 text=re.sub(r'<meta[^>]+property=["\']og:[^>]+>','',text,flags=re.I)
 text=re.sub(r'<meta[^>]+name=["\']twitter:[^>]+>','',text,flags=re.I)
 block=(f'<link rel="canonical" href="{escape(canonical)}">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="cs_CZ">'
        f'<meta property="og:site_name" content="Naše Kadaň">'
        f'<meta property="og:title" content="{escape(title,quote=True)}">'
        f'<meta property="og:description" content="{escape(desc,quote=True)}">'
        f'<meta property="og:url" content="{escape(canonical)}">'
        f'<meta property="og:image" content="{OG_IMAGE}">'
        f'<meta property="og:image:width" content="1200">'
        f'<meta property="og:image:height" content="630">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{escape(title,quote=True)}">'
        f'<meta name="twitter:description" content="{escape(desc,quote=True)}">'
        f'<meta name="twitter:image" content="{OG_IMAGE}">')
 return text.replace('</head>',block+'</head>',1)

def add_analytics(text):
 if '/analytics.js' not in text:
  text=text.replace('</body>','<script src="/analytics.js" defer></script></body>',1)
 return text

def add_footer_links(text):
 links='<span class="legal-links"><a href="/o-webu/">O webu</a> · <a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a> · <a href="/navstevnost/">Návštěvnost</a></span>'
 if '/o-webu/' in text and '/navstevnost/' in text:return text
 if '</footer>' in text:
  return text.replace('</footer>',f'<div class="wrap footer-legal">{links}</div></footer>',1)
 return text

def process_html(path):
 text=path.read_text(encoding='utf-8')
 text=text.replace('/pruvodce/mirove-namesti.html','/pruvodce/mestske-namesti.html')
 text=add_head_meta(text,path)
 text=add_analytics(text)
 text=add_footer_links(text)
 path.write_text(text,encoding='utf-8')

for path in ROOT.rglob('*.html'):
 if any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts):continue
 process_html(path)

# First-party, cookie-free analytics beacon.
(ROOT/'analytics.js').write_text("""(()=>{try{if(navigator.doNotTrack==='1')return;const payload={path:location.pathname,title:document.title,referrer:document.referrer?new URL(document.referrer).hostname:''};const body=JSON.stringify(payload);if(navigator.sendBeacon){navigator.sendBeacon('/api/analytics/pageview',new Blob([body],{type:'application/json'}));}else{fetch('/api/analytics/pageview',{method:'POST',headers:{'Content-Type':'application/json'},body,keepalive:true,credentials:'omit'}).catch(()=>{});}}catch(_){}})();\n""",encoding='utf-8')

# SEO discovery files.
urls=[]
for path in sorted(ROOT.rglob('*.html')):
 if any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts):continue
 if path.name=='404.html':continue
 urls.append(canonical_for(path))
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: https://nasekadan.cz/sitemap.xml\n',encoding='utf-8')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{escape(u)}</loc></url>\n' for u in urls)+'</urlset>\n',encoding='utf-8')

# Branded custom error page.
(ROOT/'404.html').write_text('''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stránka nenalezena | Naše Kadaň</title><meta name="description" content="Požadovaná stránka nebyla nalezena."><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"></head><body><header><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a></div></header><main class="wrap section"><p class="tag">CHYBA 404</p><h1>Stránka nebyla nalezena</h1><p class="section-intro">Odkaz mohl být změněn nebo stránka už neexistuje.</p><p><a class="btn" href="/">Zpět na úvodní stránku</a></p></main><footer><div class="wrap">© 2026 Naše Kadaň · <a href="/o-webu/">O webu</a> · <a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a></div></footer><script src="/analytics.js" defer></script></body></html>''',encoding='utf-8')

# About/operator transparency page.
about=ROOT/'o-webu';about.mkdir(exist_ok=True)
(about/'index.html').write_text('''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>O webu | Naše Kadaň</title><meta name="description" content="Informace o nezávislém informačním portálu Naše Kadaň, jeho obsahu, opravách a kontaktu."><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"></head><body><header><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="/">Úvod</a><a href="/zpravy/">Zprávy</a><a href="/zapojte-se/">Kontakt</a></nav></div></header><main class="wrap section" style="max-width:850px"><p class="tag">O PORTÁLU</p><h1>O webu Naše Kadaň</h1><p class="section-intro">Naše Kadaň je nezávislý informační portál o dění, akcích, historii a praktickém životě ve městě.</p><h2>Jak pracujeme</h2><p>U důležitých témat odkazujeme na původní veřejné dokumenty a zdroje. Automaticky načtené události průběžně kontrolujeme a u každé akce se snažíme uvádět přímý odkaz na pořadatele.</p><h2>Opravy a podněty</h2><p>Našli jste chybu, nefunkční odkaz nebo chybějící událost? Napište na <a href="mailto:info@nasekadan.cz"><b>info@nasekadan.cz</b></a>. Opravy provádíme bez zbytečného odkladu.</p><h2>Reklama</h2><p>Web obsahuje označené reklamní a partnerské odkazy. Příjmy z reklamy pomáhají financovat provoz, technické zabezpečení a tvorbu obsahu.</p><h2>Kontakt</h2><p>E-mail: <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></p></main><footer><div class="wrap">© 2026 Naše Kadaň · <a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a></div></footer></body></html>''',encoding='utf-8')

# Public aggregate analytics page; no personal data shown.
stats=ROOT/'navstevnost';stats.mkdir(exist_ok=True)
(stats/'index.html').write_text('''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Návštěvnost | Naše Kadaň</title><meta name="description" content="Souhrnná návštěvnost portálu Naše Kadaň bez cookies a reklamního profilování."><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><style>.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.stat{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px}.stat b{font:800 38px Georgia,serif;display:block}.top-pages{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px;margin-top:22px}.top-pages li{margin:10px 0}@media(max-width:700px){.stats{grid-template-columns:1fr}}</style></head><body><header><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="/">Úvod</a><a href="/o-webu/">O webu</a></nav></div></header><main class="wrap section"><p class="tag">TRANSPARENTNÍ STATISTIKY</p><h1>Návštěvnost portálu</h1><p class="section-intro">Souhrnné měření bez reklamních cookies. Unikátní návštěvy jsou pouze orientační a počítají se anonymizovaně po jednotlivých dnech.</p><div class="stats"><div class="stat"><span>Zobrazení celkem</span><b id="views">–</b></div><div class="stat"><span>Dnes</span><b id="today">–</b></div><div class="stat"><span>Unikátní dnes</span><b id="unique">–</b></div></div><div class="top-pages"><h2>Nejčtenější stránky za 30 dní</h2><ol id="pages"><li>Načítám…</li></ol></div></main><footer><div class="wrap">© 2026 Naše Kadaň · <a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a></div></footer><script>fetch('/api/analytics/summary',{cache:'no-store'}).then(r=>r.json()).then(d=>{views.textContent=(d.total||0).toLocaleString('cs-CZ');today.textContent=(d.today||0).toLocaleString('cs-CZ');unique.textContent=(d.uniqueToday||0).toLocaleString('cs-CZ');pages.innerHTML=(d.topPages||[]).map(x=>'<li><a href="'+x.path+'">'+x.path+'</a> — <b>'+x.views.toLocaleString('cs-CZ')+'</b></li>').join('')||'<li>Zatím bez dat.</li>'}).catch(()=>pages.innerHTML='<li>Statistiky se nyní nepodařilo načíst.</li>');</script></body></html>''',encoding='utf-8')

# Update privacy notice with aggregate measurement.
privacy=ROOT/'ochrana-osobnich-udaju'/'index.html'
if privacy.exists():
 text=privacy.read_text(encoding='utf-8')
 if 'Měření návštěvnosti' not in text:
  insert='<h2>Měření návštěvnosti</h2><p>Pro základní souhrnné statistiky zaznamenáváme navštívenou cestu, čas a anonymizovaný denní identifikátor odvozený z IP adresy. Nepoužíváme reklamní cookies ani nevytváříme uživatelské profily. Podrobné IP adresy se ve statistikách nezobrazují.</p>'
  text=text.replace('<h2>Vaše práva</h2>',insert+'<h2>Vaše práva</h2>')
  privacy.write_text(text,encoding='utf-8')

# Shared footer/legal styling.
style=ROOT/'style.css'
css=style.read_text(encoding='utf-8')
if '.footer-legal' not in css:
 css+=' .footer-legal{padding-top:22px;margin-top:22px;border-top:1px solid #ffffff1a;font-size:14px;color:#aebbc2}.footer-legal a{display:inline;color:inherit}.legal-links{display:block}'
 style.write_text(css,encoding='utf-8')

print(f'Finalizováno {len(urls)} indexovatelných stránek.')
