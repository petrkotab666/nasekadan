#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'index.html'

ARC_URL = '/clanky/arc-med-nemocnice-kadan.html'
FIRE_URL = '/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html'
BEDS_URL = '/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html'
CULTURE_URL = '/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html'

HERO = '''<article class="lead" data-arc-med-hero>
      <div class="photo" style="background:linear-gradient(135deg,#132630,#3f6576 58%,#a9232b)"><span>ZDRAVOTNICTVÍ</span><strong>ARC-MED</strong></div>
      <div class="copy">
        <small>VEŘEJNÉ PENÍZE · 28. 07. 2026 · 5:00</small>
        <h1>ARC-MED za 16 milionů: dva posudky, nejasné schválení a spor o dvanáct milionů</h1>
        <p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p>
        <a class="btn" href="/clanky/arc-med-nemocnice-kadan.html">Přečíst celý článek →</a>
      </div>
    </article>'''

ASIDE = '''<aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">27. 7. 2026 v 22:35</p>
      <h2>Kadaňští hasiči cvičili na Nechranicích záchranu lidí z vody</h2>
      <p>Společný výcvik prověřil práci člunů i součinnost hasičů, policie a vodních záchranářů.</p>
      <a class="aside-button" href="/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html">Přečíst článek →</a>
      <div class="aside-links">
        <a href="/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html">82 lůžek z Kadaně pro Ukrajinu</a>
        <a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kulturní přehled na tento týden</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>'''

ARC_CARD = '''<article class="article-card hospital" data-arc-med-card>
      <div class="visual" style="background:linear-gradient(135deg,#132630,#3f6576 58%,#a9232b)"><strong>ARC-MED za 16 milionů</strong></div>
      <div class="article-body">
        <span class="meta">28. 7. 2026 · 5:00 · Zdravotnictví a veřejné peníze</span>
        <h3>Dva posudky, nejasné schválení a spor o dvanáct milionů</h3>
        <p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p>
        <a class="read-more" href="/clanky/arc-med-nemocnice-kadan.html">Přečíst článek →</a>
      </div>
    </article>'''

FIRE_CARD = '''<article class="article-card transport" data-nechranice-card>
      <div class="visual" style="background:linear-gradient(135deg,#12313f,#28617a 58%,#a56b24)"><strong>Záchrana na vodě</strong></div>
      <div class="article-body">
        <span class="meta">27. 7. 2026 · 22:35 · Hasiči</span>
        <h3>Kadaňští hasiči cvičili na Nechranicích</h3>
        <p>Společný výcvik prověřil práci člunů i součinnost záchranných složek.</p>
        <a class="read-more" href="/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html">Přečíst článek →</a>
      </div>
    </article>'''

BEDS_CARD = '''<article class="article-card hospital" data-beds-card>
      <div class="visual" style="background:linear-gradient(135deg,#142b37,#36586a 58%,#9d222a)"><strong>82 lůžek pro Ukrajinu</strong></div>
      <div class="article-body">
        <span class="meta">27. 7. 2026 · 21:40 · Nemocnice Kadaň</span>
        <h3>Z Kadaně až k frontové linii</h3>
        <p>Funkční nemocniční postele dostaly druhou šanci tam, kde jsou mimořádně potřebné.</p>
        <a class="read-more" href="/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html">Přečíst článek →</a>
      </div>
    </article>'''

CULTURE_CARD = '''<article class="article-card events" data-weekly-events-card>
      <div class="visual" style="background:linear-gradient(135deg,#143342,#39748a 58%,#b58b25)"><strong>Kam příští týden</strong></div>
      <div class="article-body">
        <span class="meta">26. 07. 2026 · 12:00 · Kultura a volný čas</span>
        <h3>Kam v Kadani a okolí od 27. července do 2. srpna</h3>
        <p>Živá hudba na Liďáku, festival čaje, kino, koupaliště, historický vlak a galakoncert.</p>
        <a class="read-more" href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Otevřít celý přehled →</a>
      </div>
    </article>'''

text = HOME.read_text(encoding='utf-8')
hero_section = re.compile(r'(<section class="wrap hero" id="clanky">).*?(</section>)', re.S)
replacement = r'''\1
    ''' + HERO + '\n\n    ' + ASIDE + r'''
  \2'''
text, count = hero_section.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit('Nepodařilo se přepsat hlavní hero sekci.')

list_match = re.search(r'(<div class="article-list">)(.*?)(</div>\s*<p class="archive-note">)', text, re.S)
if not list_match:
    raise SystemExit('Nenalezen seznam článků na titulní stránce.')
body = list_match.group(2)
for attr in ('data-arc-med-card','data-nechranice-card','data-beds-card','data-weekly-events-card'):
    body = re.sub(r'<article\b[^>]*' + re.escape(attr) + r'[^>]*>.*?</article>\s*', '', body, flags=re.S)
body = re.sub(r'\s*<!-- WEEKLY-EVENTS-(?:START|END) -->\s*', '\n', body)
ordered = '\n    ' + ARC_CARD + '\n    ' + FIRE_CARD + '\n    ' + BEDS_CARD + '\n    ' + CULTURE_CARD + '\n' + body.lstrip()
text = text[:list_match.start(2)] + ordered + text[list_match.end(2):]

for url in (ARC_URL, FIRE_URL, BEDS_URL, CULTURE_URL):
    if text.find(url) < 0:
        raise SystemExit(f'Po opravě chybí odkaz {url}')
positions = [text.find(url) for url in (ARC_URL, FIRE_URL, BEDS_URL, CULTURE_URL)]
if positions != sorted(positions):
    raise SystemExit(f'Nesprávné pořadí článků: {positions}')

HOME.write_text(text, encoding='utf-8', newline='\n')
print('Titulní stránka: ARC-MED, hasiči, 82 lůžek, kultura.')
