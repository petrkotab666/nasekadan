#!/usr/bin/env python3
from pathlib import Path
import html, json, re

ROOT=Path(__file__).resolve().parents[1]
BASE='https://nasekadan.cz'
TODAY='2026-07-24'
ASSET_VERSION='20260724-mobile-5'
SOCIAL=f'{BASE}/social-card.png'
LEGAL='<div class="footer-legal"><a href="/o-webu/">O webu</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div>'
HEADER='''<header><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní menu"><a href="/">Úvod</a><a href="/#clanky">Naše články</a><a href="/prehled-zdroju/">Přehled zdrojů</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a></nav></div></header>'''


def canonical_for(path:Path)->str:
 rel=path.relative_to(ROOT).as_posix()
 if rel=='index.html':return BASE+'/'
 if rel.endswith('/index.html'):return BASE+'/'+rel[:-10]
 return BASE+'/'+rel


def get_tag(text:str,tag:str)->str:
 match=re.search(rf'<{tag}[^>]*>(.*?)</{tag}>',text,re.I|re.S)
 return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',match.group(1))).strip() if match else ''


def get_description(text:str)->str:
 for match in re.finditer(r'<meta\b[^>]*>',text,re.I):
  tag=match.group(0)
  if re.search(r'\bname=["\']description["\']',tag,re.I):
   content=re.search(r'\bcontent=["\']([^"\']*)',tag,re.I)
   if content:return html.unescape(content.group(1)).strip()
 return ''


def version_assets(text:str)->str:
 text=re.sub(
  r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])(?=[^>]*\bhref=["\'](?:\.\./|\./|/)?style\.css(?:\?[^"\']*)?["\'])[^>]*>',
  f'<link rel="stylesheet" href="/style.css?v={ASSET_VERSION}">',
  text,
  flags=re.I,
 )
 text=re.sub(
  r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])(?=[^>]*\bhref=["\'](?:\.\./|\./|/)?mobile\.css(?:\?[^"\']*)?["\'])[^>]*>\s*',
  '',
  text,
  flags=re.I,
 )
 mobile=f'<link rel="stylesheet" href="/mobile.css?v={ASSET_VERSION}">'
 text=text.replace('</head>',mobile+'</head>',1)
 text=re.sub(
  r'<script\b[^>]*\bsrc=["\'](?:\.\./|\./|/)?site\.js(?:\?[^"\']*)?["\'][^>]*>\s*</script>',
  f'<script src="/site.js?v={ASSET_VERSION}" defer></script>',
  text,
  flags=re.I,
 )
 return text


def normalize_hospital_article(path:Path,text:str)->str:
 if path.relative_to(ROOT).as_posix()!='clanky/nemocnice-kadan.html':
  return text
 text=text.replace('ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · AKTUALIZOVÁNO 23. ČERVENCE 2026','ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 24. ČERVENCE 2026')
 text=text.replace('ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 23. ČERVENCE 2026','ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 24. ČERVENCE 2026')
 text=text.replace('<p class="updated">Aktualizováno: 23. 7. 2026</p>','<p class="updated">Publikováno: 24. 7. 2026</p>')
 text=text.replace('<p class="updated">Publikováno: 23. 7. 2026</p>','<p class="updated">Publikováno: 24. 7. 2026</p>')
 text=text.replace('"datePublished":"2026-07-23"','"datePublished":"2026-07-24"')
 text=text.replace('"dateModified":"2026-07-23"','"dateModified":"2026-07-24"')
 text=text.replace('Stav informací k 23. červenci 2026.','Stav informací k 24. červenci 2026.')
 return text


def finish_html(path:Path)->None:
 text=path.read_text(encoding='utf-8')
 text=normalize_hospital_article(path,text)
 text=text.replace('mirove-namesti.html','mestske-namesti.html').replace('<span class="logo-mark">K</span>','<span class="logo-mark">NK</span>').replace('Přečíst celý vlastní článek','Přečíst celý článek')
 if re.search(r'<header\b[^>]*>.*?</header>',text,re.I|re.S):
  text=re.sub(r'<header\b[^>]*>.*?</header>',HEADER,text,count=1,flags=re.I|re.S)
 else:
  text=text.replace('<body>','<body>'+HEADER,1)
 patterns=[r'<link\b[^>]*rel=["\']canonical["\'][^>]*>\s*',r'<meta\b[^>]*(?:property=["\']og:[^"\']+["\']|name=["\']twitter:[^"\']+["\']|name=["\']robots["\']|name=["\']theme-color["\'])[^>]*>\s*']
 for pattern in patterns:text=re.sub(pattern,'',text,flags=re.I)
 canonical=canonical_for(path)
 title=get_tag(text,'title') or 'Naše Kadaň'
 description=get_description(text) or 'Vlastní články, akce, praktické informace a průvodce městem Kadaň.'
 is_404=path.name=='404.html'
 og_type='article' if 'clanky' in path.parts else 'website'
 robots='noindex,follow' if is_404 else 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1'
 metadata=(f'<link rel="canonical" href="{html.escape(canonical,quote=True)}"><meta name="robots" content="{robots}"><meta name="theme-color" content="#a9232b"><meta property="og:locale" content="cs_CZ"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{html.escape(title,quote=True)}"><meta property="og:description" content="{html.escape(description,quote=True)}"><meta property="og:url" content="{html.escape(canonical,quote=True)}"><meta property="og:image" content="{SOCIAL}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Naše Kadaň – vlastní články, akce a průvodce městem"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(title,quote=True)}"><meta name="twitter:description" content="{html.escape(description,quote=True)}"><meta name="twitter:image" content="{SOCIAL}">')
 text=text.replace('</head>',metadata+'</head>',1)
 if 'footer-legal' not in text:
  if '</footer>' in text:text=text.replace('</footer>',LEGAL+'</footer>',1)
  else:text=text.replace('</body>',f'<footer><div class="wrap">© 2026 Naše Kadaň</div>{LEGAL}</footer></body>',1)
 if '/site.js' not in text:text=text.replace('</body>','<script src="/site.js" defer></script></body>',1)
 text=version_assets(text)
 path.write_text(text,encoding='utf-8')


def main()->None:
 for path in sorted(ROOT.rglob('*.html')):
  if any(part in {'.git','.github'} for part in path.parts):continue
  finish_html(path)
 home=ROOT/'index.html'
 text=home.read_text(encoding='utf-8')
 if '"@type":"WebSite"' not in text:
  data={"@context":"https://schema.org","@graph":[{"@type":"WebSite","@id":BASE+"/#website","url":BASE+"/","name":"Naše Kadaň","inLanguage":"cs","publisher":{"@id":BASE+"/#organization"}},{"@type":"Organization","@id":BASE+"/#organization","name":"Naše Kadaň","url":BASE+"/","email":"info@nasekadan.cz","logo":{"@type":"ImageObject","url":SOCIAL}}]}
  text=text.replace('</head>',f'<script type="application/ld+json">{json.dumps(data,ensure_ascii=False,separators=(",",":"))}</script></head>',1)
  home.write_text(text,encoding='utf-8')
 (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /data/\nDisallow: /statistiky/\nSitemap: https://nasekadan.cz/sitemap.xml\n',encoding='utf-8')
 urls=[canonical_for(path) for path in sorted(ROOT.rglob('*.html')) if not any(part in {'.git','.github'} for part in path.parts) and path.name!='404.html']
 sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{html.escape(url)}</loc><lastmod>{TODAY}</lastmod></url>\n' for url in sorted(set(urls)))+'</urlset>\n'
 (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')


if __name__=='__main__':main()
