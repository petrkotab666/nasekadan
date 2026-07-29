#!/usr/bin/env python3
from pathlib import Path
import re

p = Path('index.html')
t = p.read_text(encoding='utf-8')

hero = '''  <section class="wrap hero" id="clanky">
    <article class="lead" data-hospital-profile-hero>
      <div class="photo" style="background:linear-gradient(135deg,#10242e,#22606b 55%,#9d222a)"><span>ZDRAVOTNICTVÍ · REGION</span><strong>254 LŮŽEK</strong></div>
      <div class="copy">
        <small>NEMOCNICE KADAŇ · 29. 07. 2026 · 5:00</small>
        <h1>Nemocnice Kadaň není jen spor o miliony</h1>
        <p>Co všechno zajišťuje pro region: 254 lůžek, téměř 480 pracovních úvazků, více než 114 tisíc ambulantních vyšetření a otázky dalšího směřování.</p>
        <a class="btn" href="/clanky/nemocnice-kadan-profil-sluzby-budoucnost.html">Přečíst závěrečný díl série →</a>
      </div>
    </article>
    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">28. 7. 2026 v 19:45</p>
      <h2>V srpnu omezí provoz více ordinací v Kadani a okolí</h2>
      <p>Ambulance MUDr. Suchecké bude zavřená od 3. do 14. srpna. MUDr. Šindelář má dovolenou od 10. do 21. srpna.</p>
      <a class="aside-button" href="/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">Přečíst praktické informace →</a>
      <div class="aside-links"><a href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Odstávky v Autokempu Prunéřov</a><a href="/clanky/arc-med-nemocnice-kadan.html">ARC-MED za 16 milionů</a><a href="/clanky/">Všechny články podle data</a></div>
    </aside>
  </section>'''

t, n = re.subn(r'  <section class="wrap hero" id="clanky">.*?</section>', hero, t, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Hero section not found')

card = '''    <article class="article-card hospital" data-hospital-profile-card>
      <div class="visual" style="background:linear-gradient(135deg,#10242e,#22606b 55%,#9d222a)"><strong>Nemocnice jako celek</strong></div>
      <div class="article-body"><span class="meta">29. 7. 2026 · 5:00 · Zdravotnictví a region</span><h3>Nemocnice Kadaň není jen spor o miliony</h3><p>254 lůžek, téměř 480 pracovních úvazků, výkony, spádová oblast a otázky budoucnosti.</p><a class="read-more" href="/clanky/nemocnice-kadan-profil-sluzby-budoucnost.html">Přečíst článek →</a></div>
    </article>
'''
if 'data-hospital-profile-card' not in t:
    t = t.replace('    <div class="article-list">\n', '    <div class="article-list">\n' + card, 1)

p.write_text(t, encoding='utf-8', newline='\n')
print('Titulní stránka přepnuta na závěrečný profil nemocnice.')
