#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

PATH = Path('.github/drafts/cisarsky-den-kadan-historie-2026.html')
text = PATH.read_text(encoding='utf-8')

# Odstranit dřívější nákladovou kapitolu z hlavního článku.
text = re.sub(
    r'\n\s*<section data-original-findings="contracts-v[12]">.*?</section>\s*\n',
    '\n',
    text,
    flags=re.S,
)

# Odstranit případný pravý box s částečným účtem.
text = re.sub(
    r'\s*<div class="sidebox"><h3>Částečný účet 2026</h3>.*?</div>\s*',
    '\n  ',
    text,
    flags=re.S,
)

if 'data-actual-editions="31-held"' in text:
    PATH.write_text(text, encoding='utf-8', newline='\n')
    print('Historické okénko a počet ročníků už jsou vložené.')
    raise SystemExit(0)

css_anchor = '    .source-list{margin-top:44px;padding:24px;border-radius:18px;background:#eef3f5}'
css = '''    .edition-result{margin:36px 0;padding:28px;border-radius:21px;background:linear-gradient(135deg,#152c38,#294957 62%,#84212a);color:#fff;box-shadow:0 17px 42px rgba(18,35,45,.19)}.edition-result small{display:block;color:#ffd99a;font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.edition-result strong{display:block;margin:8px 0;font:900 38px/1.05 Georgia,serif}.edition-result p{margin:0;color:#edf3f5;font-size:16px}.edition-grid,.day-grid,.justice-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;margin:28px 0}.edition-card,.day-card,.justice-card{padding:21px;border:1px solid #dbe3e6;border-radius:17px;background:#fff;box-shadow:0 9px 27px rgba(18,35,45,.05)}.edition-card b,.day-card b,.justice-card b{display:block;margin-bottom:7px;color:#9f2626;font:800 21px/1.18 Georgia,serif}.edition-card p,.day-card p,.justice-card p{margin:0;color:#53616a;font-size:15px}.history-window{margin:38px 0;padding:29px;border:1px solid #d8c69c;border-radius:22px;background:radial-gradient(circle at 92% 10%,rgba(201,164,90,.17),transparent 30%),linear-gradient(135deg,#fff9ec,#f3eee5)}.history-window>small{display:block;color:#87591d;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.history-window>h2{margin:7px 0 14px!important}.truth-box{margin:28px 0;padding:22px 24px;border-left:6px solid #2f6e4f;border-radius:0 17px 17px 0;background:#f1f7f3}.truth-box strong{display:block;font:800 22px Georgia,serif;margin-bottom:7px}.dark-box{border-left-color:#7f1720;background:#f8eeee}.walk{margin:30px 0;padding-left:25px;border-left:4px solid #d4dde0}.walk-step{position:relative;padding:0 0 25px}.walk-step:before{content:'';position:absolute;left:-34px;top:8px;width:14px;height:14px;border-radius:50%;background:#9f2626;border:4px solid #fff;box-shadow:0 0 0 1px #9f2626}.walk-step b{display:block;font:800 21px Georgia,serif}.walk-step p{margin:5px 0}.source-note{font-size:14px!important;color:#66757d!important}
'''
if css_anchor not in text:
    raise SystemExit('Chybí CSS kotva.')
text = text.replace(css_anchor, css + css_anchor, 1)
text = text.replace(
    '@media(max-width:700px){.facts{grid-template-columns:1fr}.program div{grid-template-columns:1fr}',
    '@media(max-width:700px){.facts,.edition-grid,.day-grid,.justice-grid{grid-template-columns:1fr}.program div{grid-template-columns:1fr}',
    1,
)

anchor = '  <h2>Proč slavnost přežila více než tři desetiletí</h2>'
if anchor not in text:
    raise SystemExit('Chybí obsahová kotva.')

section = '''  <section data-actual-editions="31-held">
  <h2>Kolikrát se Císařský den skutečně konal</h2>
  <p>Oficiální označení <strong>34. ročník</strong> neodpovídá počtu skutečně uskutečněných slavností. První Císařský den se konal roku 1993 a dobové zprávy potvrzují dvacátý ročník v roce 2012, čtyřiadvacátý v roce 2016 a sedmadvacátý v roce 2019. To znamená nepřerušenou řadu 27 uskutečněných slavností v letech 1993 až 2019.</p>
  <p>Ročníky 2020 a 2021 byly zrušeny kvůli epidemickým omezením. Slavnost se vrátila roku 2022 a proběhla také v letech 2023, 2024 a 2025.</p>

  <div class="edition-result">
    <small>Výsledek rekonstrukce Naší Kadaně</small>
    <strong>31 uskutečněných slavností</strong>
    <p>Tolik Císařských dnů proběhlo od roku 1993 do konce roku 2025. Letošní slavnost 22. srpna 2026 bude při uskutečnění ve skutečnosti dvaatřicátou, přestože nese oficiální označení 34. ročník.</p>
  </div>

  <div class="edition-grid">
    <div class="edition-card"><b>1993–2019: 27</b><p>Každoroční nepřerušená řada doložená průběžným číslováním 20., 24. a 27. ročníku.</p></div>
    <div class="edition-card"><b>2020–2021: 0</b><p>Dva zrušené ročníky v době epidemických omezení.</p></div>
    <div class="edition-card"><b>2022–2025: 4</b><p>Návrat slavnosti a čtyři další uskutečněné ročníky.</p></div>
    <div class="edition-card"><b>Rok 2026: plán</b><p>Oficiálně 34. ročník, podle počtu uskutečněných akcí by šlo o 32. slavnost.</p></div>
  </div>
  <p class="source-note">Rozdíl vznikl tím, že pořadové číslo pokračovalo podle kalendářní řady tradice, i když se dva ročníky nekonaly.</p>

  <div class="history-window">
    <small>Historické okénko</small>
    <h2>Jak vypadala Kadaň, do které roku 1367 přijel Karel IV.</h2>
    <p>Císař nepřijížděl do romantického města, které dnes napodobují kulisy slavnosti. Přijel do rušného královského města pouhých pět let po katastrofě. Roku 1362 vyhořela Kadaň i s hradem. Město se rychle obnovovalo z kamene, zdokonalovalo opevnění a budovalo radnici i nové měšťanské domy. Když Karel IV. dorazil roku 1367, procházel tedy městem, které bylo čerstvě přestavěné a svou prosperitu dávalo viditelně najevo.</p>

    <div class="day-grid">
      <div class="day-card"><b>Dům byl zároveň dílnou</b><p>V přízemí se pracovalo, prodávalo a skladovalo zboží, v dalších částech domu se vařilo a spalo. Řemeslo a rodinný život nebyly oddělené jako dnes.</p></div>
      <div class="day-card"><b>Náměstí bylo obchodním centrem</b><p>Trhy znamenaly potraviny, látky, kůže, kovové výrobky, nádoby i zprávy z okolí. Osmidenní výroční trh udělený Karlem IV. byl hospodářskou výsadou, ne jen slavností.</p></div>
      <div class="day-card"><b>Pivo bylo jídlo i nápoj</b><p>Mílové právo chránilo kadaňské vaření piva a další řemesla před konkurencí v okolí. Středověké pivo bylo slabší, kalnější a někdy se podávalo i teplé.</p></div>
      <div class="day-card"><b>Večeře nebyla hostina</b><p>V českých městech 14. století převládalo pečivo, kaše, luštěniny, zelí, cibule, vejce a podle možností ryby či maso. Bohatší měšťané jedli pestřeji než čeleď, nádeníci a chudina.</p></div>
    </div>

    <h3>Procházka městem jednoho dne</h3>
    <div class="walk">
      <div class="walk-step"><b>Ráno: otevření bran</b><p>Po nočním uzavření města proudili branami obchodníci, sedláci a povozy. Hradby nebyly dekorací, ale kontrolovaly pohyb lidí i zboží.</p></div>
      <div class="walk-step"><b>Dopoledne: hluk dílen a trhu</b><p>Z domů se ozývali kováři, ševci, řezníci, pekaři a další řemeslníci. Na náměstí se smlouvalo, vážilo a vybíraly poplatky.</p></div>
      <div class="walk-step"><b>Odpoledne: rada, soud a úřadování</b><p>Kadaň získala právo úplné samosprávy roku 1366. Městská rada proto neřešila jen správu majetku, ale také spory, pořádek a tresty.</p></div>
      <div class="walk-step"><b>Večer: zavřené město</b><p>Po uzavření hlavních bran se dovnitř nevcházelo volně. Katova ulička sloužila také jako nouzová spojnice a současně odváděla vodu z náměstí směrem k Bystřickému potoku.</p></div>
    </div>

    <h3>Spravedlnost nebyla schovaná před veřejností</h3>
    <p>Ve 13. a na počátku 14. století vykonával kadaňské hrdelní právo purkrabí na hradě. Později těžké zločiny vyšetřovala městská rada nebo městský soud. Trest neměl pouze potrestat pachatele, ale také varovat ostatní, proto se pranýř i popravy odehrávaly veřejně.</p>

    <div class="justice-grid">
      <div class="justice-card"><b>Kat žil na okraji společnosti</b><p>Kadaňští kati po staletí sídlili v hradební baště u Katovy uličky. Vedle výkonu trestů se věnovali bylinkářství a ranhojičství.</p></div>
      <div class="justice-card"><b>Menší tresty byly viditelné</b><p>Pranýř na hlavním náměstí vystavoval provinilce veřejné hanbě. Podstatou trestu bylo, aby jej město vidělo.</p></div>
      <div class="justice-card"><b>Odsouzenec procházel městem</b><p>Z pozdějších kadaňských záznamů známe cestu od radnice přes Žateckou bránu k šibenici či popravnímu špalku.</p></div>
      <div class="justice-card"><b>Trest závisel na činu</b><p>Pozdější kadaňské prameny zmiňují stínání, oběšení a také utopení dvou zlodějek v Ohři roku 1519.</p></div>
    </div>

    <div class="truth-box"><strong>Co můžeme vztáhnout přímo k roku 1367</strong>Požár a kamennou obnovu města, nové opevnění, samosprávu, trh, mílové právo, pivovarnictví a fungování městské justice.</div>
    <div class="truth-box dark-box"><strong>Co známe až z pozdějších záznamů</strong>Přesnou trasu odsouzenců, konkrétní druhy kadaňských poprav, šatlavu u Vodní brány a jednotlivé případy z 16. až 18. století. V článku je proto nepřenášíme automaticky do roku 1367, ale používáme je jako okno do dlouhodobého fungování městské spravedlnosti.</div>
  </div>
  </section>

'''

text = text.replace(anchor, section + anchor, 1)

# Nahradit případný starý box v pravém sloupci novým výsledkem.
side_anchor = '<div class="sidebox"><h3>Hlavní historická osa</h3>'
side = '<div class="sidebox"><h3>Skutečný počet</h3><p><strong>31 slavností</strong> proběhlo do konce roku 2025.</p><p>Letošní by byla ve skutečnosti 32., nikoli 34.</p></div>\n  '
if side_anchor in text and '<h3>Skutečný počet</h3>' not in text:
    text = text.replace(side_anchor, side + side_anchor, 1)

# Doplnit zdroje k číslování a historickému okénku.
source_marker = '      <li><a href="https://www.regionalni-znacky.cz/poohri/zazitky/cisarsky-den-v-kadani"'
if source_marker in text and 'cisarsky-den-potricate' not in text:
    pos = text.find(source_marker)
    end = text.find('</li>', pos) + len('</li>')
    extra = '''\n      <li><a href="https://www.novinky.cz/clanek/vase-zpravy-v-kadani-hledaji-historicke-a-zajimave-fotky-z-cisarskeho-dne-40134263" target="_blank" rel="noopener">Rok 2012 jako 20. ročník a počátek roku 1993</a></li>\n      <li><a href="https://chomutovsky.denik.cz/volny-cas/tydenni-prehled-kulturnich-akci-na-chomutovsku-20160826.html" target="_blank" rel="noopener">Rok 2016 jako 24. ročník</a></li>\n      <li><a href="https://www.bakchus.eu/en/cisarsky-den-kadan-cz/" target="_blank" rel="noopener">Rok 2019 jako 27. uskutečněný příjezd</a></li>\n      <li><a href="https://chomutovsky.denik.cz/zpravy_region/kadan-cisarsky-den-20220720.html" target="_blank" rel="noopener">Návrat v roce 2022 po zrušení let 2020 a 2021</a></li>\n      <li><a href="https://kadan.eu/kadan-historicka/" target="_blank" rel="noopener">Požár 1362, kamenná obnova a samospráva</a></li>\n      <li><a href="https://kadan.eu/pamatky/katova-ulicka/" target="_blank" rel="noopener">Katova ulička, katův dům, stoková a obranná funkce</a></li>'''
    text = text[:end] + extra + text[end:]

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Nákladová kapitola nahrazena skutečným počtem ročníků a historickým okénkem.')
