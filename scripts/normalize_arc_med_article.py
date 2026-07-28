#!/usr/bin/env python3
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
path = root / 'clanky' / 'arc-med-nemocnice-kadan.html'
text = path.read_text(encoding='utf-8')

# Veřejná verze a standardní cesty.
text = text.replace('content="noindex,nofollow"', 'content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"')
text = text.replace('href="../../favicon.svg"', 'href="../favicon.svg"')
text = text.replace('href="../../style.css"', 'href="../style.css"')
text = text.replace('href="../../index.html"', 'href="../index.html"')
text = text.replace('href="../../pruvodce/"', 'href="../pruvodce/"')
text = text.replace('src="../../site.js"', 'src="../site.js"')
text = text.replace('ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · PŘIPRAVOVANÝ ČLÁNEK', 'ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · 28. ČERVENCE 2026')

# Stejná struktura jako u ostatních článků.
text = re.sub(r'<article(?![^>]*class=)>', '<article class="article">', text, count=1)
text = re.sub(r'<article\s+class="(?![^"]*\barticle\b)([^"]*)">', r'<article class="article \1">', text, count=1)

# Odstranit návrhové formulace.
text = re.sub(r'\s*<div class="sidebox"><h3>Pracovní verze</h3>.*?</div>', '', text, count=1, flags=re.S)
text = text.replace('Pracovní text odděluje ověřitelné dokumenty od tvrzení jednotlivých stran.', 'Článek odděluje ověřitelné dokumenty od tvrzení jednotlivých stran.')
text = text.replace(' Před zveřejněním doporučujeme zaslat dotazy nemocnici, městu, Petru Hossnerovi a bývalým vlastníkům ARC-MED.', '')

# Pevný statický systém nesmí v článku zůstat.
text = re.sub(r'<style id="static-article-ads-style">.*?</style>\s*', '', text, flags=re.S)
text = re.sub(r'<div class="static-article-ads".*?</div>', '', text, flags=re.S)
text = re.sub(r'<div class="article-aside-tower".*?</div>', '', text, flags=re.S)

# Standardní dynamická reklamní pozice v pravém sloupci.
text = re.sub(r'<div\s+data-promos\s+data-context="sidebar"[^>]*>.*?</div>', '', text, flags=re.S)
text = text.replace('</aside>', '  <div data-promos data-context="sidebar"></div>\n</aside>', 1)

# Datum publikace v meta datech a JSON-LD.
published = '2026-07-28T05:00:00+02:00'
if 'article:published_time' not in text:
    text = text.replace('</head>', f'  <meta property="article:published_time" content="{published}">\n  <meta property="article:modified_time" content="{published}">\n</head>', 1)
else:
    text = re.sub(r'(<meta property="article:published_time" content=")[^"]+', r'\g<1>' + published, text)
    text = re.sub(r'(<meta property="article:modified_time" content=")[^"]+', r'\g<1>' + published, text)

pattern = r'(<script type="application/ld\+json">)(.*?)(</script>)'
def update_json(match: re.Match[str]) -> str:
    try:
        data = json.loads(match.group(2))
    except json.JSONDecodeError:
        return match.group(0)
    if isinstance(data, dict) and data.get('@type') == 'NewsArticle':
        data['datePublished'] = published
        data['dateModified'] = published
    return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + match.group(3)
text = re.sub(pattern, update_json, text, count=1, flags=re.S)

# Jediný správný reklamní systém: reklamy.js + proud různých nabídek vpravo.
for script_name in ('reklamy.js', 'reklamy-sidebar.js', 'reklamy-oprava-obrazku.js', 'obsah-doplnky.js'):
    text = re.sub(rf'\s*<script[^>]+src="/{re.escape(script_name)}[^>]*></script>', '', text)

scripts = '''
<script src="/reklamy.js?v=20260728-dynamic-2"></script>
<script src="/reklamy-sidebar.js?v=20260728-adstream-4"></script>
<script src="/reklamy-oprava-obrazku.js?v=20260728-dynamic-2"></script>
<script src="/obsah-doplnky.js?v=20260728-dynamic-2"></script>
'''
text = text.replace('</body>', scripts + '</body>', 1)

# Povinné kontroly.
assert 'noindex' not in text
assert 'PŘIPRAVOVANÝ ČLÁNEK' not in text
assert 'Pracovní verze' not in text
assert 'static-article-ads' not in text
assert '<article class="article">' in text
assert '<div data-promos data-context="sidebar"></div>' in text
assert '/reklamy.js?' in text
assert '/reklamy-sidebar.js?' in text

path.write_text(text, encoding='utf-8', newline='\n')
print('ARC-MED sjednocen s dynamickým reklamním proudem různých nabídek.')
