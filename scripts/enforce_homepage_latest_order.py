#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"index.html"
ARTICLE=ROOT/"clanky"/"odstavky-elektriny-autokemp-prunerov-srpen-2026.html"
HERO='  <section class="wrap hero" id="clanky">\n    <article class="lead" data-autokemp-outages-hero>\n      <div class="photo" style="background:linear-gradient(135deg,#172c37,#6d3030 58%,#ba2027)"><span>PRAKTICKÉ INFORMACE</span><strong>3 ODSTÁVKY</strong></div>\n      <div class="copy">\n        <small>PRUNÉŘOV · 28. 07. 2026 · 11:30</small>\n        <h1>Odstávky elektřiny omezí provoz restaurace v Autokempu Prunéřov</h1>\n        <p>Ve dvou termínech otevře restaurace až po 18. hodině, potřetí po 16. hodině. Recepce zůstane otevřená, kartou ale nepůjde platit.</p>\n        <a class="btn" href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst praktické informace →</a>\n      </div>\n    </article>\n    <aside class="current-aside">\n      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>\n      <p class="aside-date">28. 7. 2026 v 5:00</p>\n      <h2>ARC-MED za 16 milionů: dva posudky, nejasné schválení a spor o dvanáct milionů</h2>\n      <p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p>\n      <a class="aside-button" href="/clanky/arc-med-nemocnice-kadan.html">Přečíst celý článek →</a>\n      <div class="aside-links">\n        <a href="/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html">Výcvik hasičů na Nechranicích</a>\n        <a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kulturní přehled na tento týden</a>\n        <a href="/clanky/">Všechny články podle data</a>\n      </div>\n    </aside>\n  </section>'
CARD='    <article class="article-card service" data-autokemp-outages-card>\n      <div class="visual" style="background:linear-gradient(135deg,#172c37,#6d3030 58%,#ba2027)"><strong>Odstávky v autokempu</strong></div>\n      <div class="article-body"><span class="meta">28. 7. 2026 · 11:30 · Praktické informace</span><h3>Restaurace v Prunéřově třikrát otevře později</h3><p>Recepce zůstane otevřená, během odstávek ale nebude možné platit kartou.</p><a class="read-more" href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst článek →</a></div>\n    </article>'
if not ARTICLE.exists():
    raise SystemExit("Chybí nejnovější článek Autokempu Prunéřov")
text=HOME.read_text(encoding="utf-8")
text,count=re.subn(r'  <section class="wrap hero" id="clanky">.*?</section>',HERO,text,count=1,flags=re.S)
if count!=1: raise SystemExit("Nenalezena hero sekce")
text=re.sub(r'\s*<article\b[^>]*data-autokemp-outages-card[^>]*>.*?</article>\s*','\n',text,flags=re.S)
marker='<div class="article-list">'
if marker not in text: raise SystemExit("Nenalezen seznam článků")
text=text.replace(marker,marker+'\n'+CARD,1)
HOME.write_text(text,encoding="utf-8",newline="\n")
print("Titulní stránka zachovává nejnovější článek o odstávkách v Autokempu Prunéřov.")
