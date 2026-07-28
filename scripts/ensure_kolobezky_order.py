#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
# LATEST_AUTOKEMP_GUARD: staré opravné skripty nesmějí přepsat novější titulní článek.
if (ROOT / "clanky" / "odstavky-elektriny-autokemp-prunerov-srpen-2026.html").exists():
    print("Novější článek o odstávkách Autokempu Prunéřov je již publikován; staré pořadí se nepoužije.")
    raise SystemExit(0)
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
CULTURE = ROOT / "clanky" / "kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"
URL = "/clanky/kolobezky-hriste-detektor-kovu-kadan.html"

hero = '''  <section class="wrap hero" id="clanky">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(135deg,#173442,#416d64 58%,#b08838)"><span>BEZPEČNOST · DOPRAVA</span><strong>KOLoběžky a hřiště</strong></div>
      <div class="copy">
        <small>BEZPEČNOST · DOPRAVA · 27. 07. 2026 · 14:00</small>
        <h1>Koloběžky pod větším dohledem. Hřiště kontroluje detektor kovu</h1>
        <p>Strážníci se v létě více zaměří na koloběžky. Vysvětlujeme také, co může detektor na dětském hřišti odhalit a kde má své limity.</p>
        <a class="btn" href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst celý článek →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">PŘEDCHOZÍ ČLÁNEK</p>
      <p class="aside-date">26. 7. 2026 v 12:00</p>
      <h2>Kam v Kadani a okolí od 27. července do 2. srpna</h2>
      <p>Živá hudba na Liďáku, festival čaje, kino, koupaliště, historický vlak a regionální tipy.</p>
      <a class="aside-button" href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Otevřít kulturní přehled →</a>
      <div class="aside-links">
        <a href="/clanky/avies-nemocnice-kadan.html">Analýza AVIES a nemocnice</a>
        <a href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Noční vlakové výluky</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>
  </section>'''

home_card = '''      <article class="article-card service" data-kolobezky-card>
        <div class="visual"><strong>Koloběžky a hřiště</strong></div>
        <div class="article-body">
          <span class="meta">27. 07. 2026 · 14:00 · Bezpečnost a doprava</span>
          <h3>Koloběžky pod větším dohledem. Hřiště kontroluje detektor kovu</h3>
          <p>Co může detektor odhalit, kde má své limity a proč kontrola hřiště není totéž jako monitoring odhozených stříkaček.</p>
          <a class="read-more" href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst celý článek →</a>
        </div>
      </article>

'''

archive_card = '''    <article class="archive-item service" data-kolobezky-card>
      <div class="archive-visual"><strong>Koloběžky a hřiště</strong></div>
      <div class="archive-body">
        <span class="archive-meta">27. července 2026 v 14:00 · Bezpečnost a doprava</span>
        <h2>Koloběžky pod větším dohledem. Kadaňská hřiště strážníci kontrolují i detektorem kovu</h2>
        <p>Co detektor na hřišti dokáže odhalit, kde má své limity a proč kontrola hřiště není systematickým monitoringem celého města.</p>
        <a href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst celý článek →</a>
      </div>
    </article>

'''

def write(path: Path, text: str):
    path.write_text(text, encoding="utf-8", newline="\n")

html = HOME.read_text(encoding="utf-8")
html = re.sub(r'  <section class="wrap hero" id="clanky">.*?  </section>', hero, html, count=1, flags=re.S)
html = re.sub(r'\s*<article class="article-card[^>]*data-kolobezky-card.*?</article>\s*', '\n', html, flags=re.S)
html = html.replace('    <div class="article-list">\n', '    <div class="article-list">\n' + home_card, 1)
write(HOME, html)

archive = ARCHIVE.read_text(encoding="utf-8")
archive = re.sub(r'\s*<article class="archive-item[^>]*data-kolobezky-card.*?</article>\s*', '\n', archive, flags=re.S)
archive = archive.replace('  <section class="archive-list" aria-label="Chronologický přehled článků">\n', '  <section class="archive-list" aria-label="Chronologický přehled článků">\n' + archive_card, 1)
write(ARCHIVE, archive)

culture = CULTURE.read_text(encoding="utf-8")
old = re.compile(r'\s*<div class="fact"><h3>Nově kontrolujeme jednotlivě všechny kadaňské školy a školky</h3><p>.*?</p></div>', re.S)
replacement = '\n  <div class="fact"><h3>Prázdninový provoz MŠ Hvězdička</h3><p>MŠ Hvězdička upozorňuje na přerušení provozu od 27. července do 21. srpna. Rodiče by měli sledovat aktuální provozní oznámení své konkrétní školky.</p></div>'
culture = old.sub(replacement, culture, count=1)
write(CULTURE, culture)

print("Pořadí článků a kulturní přehled byly opraveny.")
