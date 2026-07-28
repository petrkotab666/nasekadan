#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"index.html"
ARTICLE=ROOT/"clanky"/"prakticti-lekari-nemocnice-kadan-srpen-2026.html"
HERO='  <section class="wrap hero" id="clanky">\n    <article class="lead" data-gp-august-hero>\n      <div class="photo" style="background:linear-gradient(135deg,#173240,#496d7c 58%,#9f2626)"><span>PRAKTICKÉ INFORMACE</span><strong>10.–14. SRPNA</strong></div>\n      <div class="copy">\n        <small>NEMOCNICE KADAŇ · 28. 07. 2026 · 19:45</small>\n        <h1>V srpnu omezí provoz více ordinací v Kadani a okolí</h1>\n        <p>Ambulance MUDr. Suchecké bude zavřená od 3. do 14. srpna. MUDr. Šindelář má dovolenou od 10. do 21. srpna.</p>\n        <a class="btn" href="/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">Přečíst praktické informace →</a>\n      </div>\n    </article>\n    <aside class="current-aside">\n      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>\n      <p class="aside-date">28. 7. 2026 v 11:30</p>\n      <h2>Odstávky elektřiny omezí provoz restaurace v Autokempu Prunéřov</h2>\n      <p>Ve dvou termínech otevře restaurace po 18. hodině, potřetí po 16. hodině.</p>\n      <a class="aside-button" href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst článek →</a>\n      <div class="aside-links"><a href="/clanky/arc-med-nemocnice-kadan.html">ARC-MED za 16 milionů</a><a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kulturní přehled na tento týden</a><a href="/clanky/">Všechny články podle data</a></div>\n    </aside>\n  </section>'
CARD='    <article class="article-card hospital" data-gp-august-card>\n      <div class="visual" style="background:linear-gradient(135deg,#173240,#496d7c 58%,#9f2626)"><strong>Omezení ordinací v srpnu</strong></div>\n      <div class="article-body"><span class="meta">28. 7. 2026 · 19:45 · Praktické informace</span><h3>Srpnová omezení se týkají více ordinací a ambulancí</h3><p>Nemocnice zveřejnila termíny uzavření a režim pro akutní případy.</p><a class="read-more" href="/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">Přečíst článek →</a></div>\n    </article>'
if not ARTICLE.exists(): raise SystemExit("Chybí nejnovější praktická zpráva")
text=HOME.read_text(encoding="utf-8")
text,count=re.subn(r'  <section class="wrap hero" id="clanky">.*?</section>',HERO,text,count=1,flags=re.S)
if count!=1: raise SystemExit("Nenalezena hero sekce")
text=re.sub(r'\s*<article\b[^>]*data-gp-august-card[^>]*>.*?</article>\s*','\n',text,flags=re.S)
marker='<div class="article-list">'
if marker not in text: raise SystemExit("Nenalezen seznam článků")
text=text.replace(marker,marker+'\n'+CARD,1)
HOME.write_text(text,encoding="utf-8",newline="\n")
print("Titulní stránka zachovává nejnovější praktickou zprávu o ambulancích.")
