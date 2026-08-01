#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy

PATH = Path('.github/drafts/cisarsky-den-kadan-historie-2026.html')
EXPANDER = Path('scripts/expand_cisarsky_den_draft_20260801.py')

if not PATH.is_file():
    raise SystemExit('Chybí návrh článku o Císařském dni.')

text = PATH.read_text(encoding='utf-8')

# Nejdřív bezpečně dokončit předchozí obsahové rozšíření. Skript je idempotentní.
if 'data-expanded-cisarsky-den="v2"' not in text:
    if not EXPANDER.is_file():
        raise SystemExit('Chybí předchozí rozšiřující skript.')
    runpy.run_path(str(EXPANDER), run_name='__main__')
    text = PATH.read_text(encoding='utf-8')

if 'data-original-findings="contracts-v1"' in text:
    print('Vlastní zjištění už jsou v návrhu vložena.')
    raise SystemExit(0)

css_anchor = '    .source-list{margin-top:44px;padding:24px;border-radius:18px;background:#eef3f5}'
css_extra = '''    .money-lead{margin:36px 0;padding:27px;border-radius:20px;background:linear-gradient(135deg,#142b37,#243f4b);color:#fff;box-shadow:0 16px 40px rgba(18,35,45,.18)}.money-lead small{display:block;color:#ffdca1;font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.money-lead strong{display:block;margin:7px 0 9px;font:900 34px/1.08 Georgia,serif}.money-lead p{margin:0;color:#edf4f6;font-size:16px}\n    .money-table{width:100%;margin:25px 0;border-collapse:collapse;overflow:hidden;border-radius:17px;background:#fff;box-shadow:0 10px 30px rgba(18,35,45,.06)}.money-table th,.money-table td{padding:14px 15px;border-bottom:1px solid #e1e6e8;text-align:left;vertical-align:top}.money-table th{background:#172b37;color:#fff;font-size:14px}.money-table td{font-size:15px;line-height:1.45}.money-table td:last-child,.money-table th:last-child{text-align:right;white-space:nowrap}.money-table tr:last-child td{border-bottom:0}.money-table .sum td{font-weight:900;background:#f7f1e7;color:#172b37}\n    .finding-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:28px 0}.finding-card{padding:22px;border:1px solid #d9e2e5;border-radius:18px;background:#fff;box-shadow:0 9px 27px rgba(18,35,45,.05)}.finding-card small{display:block;color:#9f2626;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.finding-card b{display:block;margin:6px 0 8px;font:900 25px/1.12 Georgia,serif}.finding-card p{margin:0;color:#53616a;font-size:15px}.finding-warning{margin:26px 0;padding:21px 23px;border:1px solid #d8c58e;border-left:6px solid #b1842f;border-radius:0 17px 17px 0;background:#fff9e9}.finding-warning strong{display:block;margin-bottom:6px;font:800 21px Georgia,serif}\n    .cost-trend{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin:24px 0}.cost-trend div{padding:18px;border-radius:16px;background:#fff;border:1px solid #dce3e6;text-align:center}.cost-trend b{display:block;color:#9f2626;font:900 24px/1.1 Georgia,serif}.cost-trend span{display:block;margin-top:5px;color:#617078;font-size:13px}\n'''
if css_anchor not in text:
    raise SystemExit('Chybí CSS kotva pro vlastní zjištění.')
text = text.replace(css_anchor, css_extra + css_anchor, 1)

# Mobilní rozložení nových tabulek a karet.
mobile_old = '@media(max-width:700px){.facts,.fact-grid,.role-grid,.route-grid,.comparison{grid-template-columns:1fr}.program div{grid-template-columns:1fr}.toc ol,.practical ul{columns:1}'
mobile_new = '@media(max-width:700px){.facts,.fact-grid,.role-grid,.route-grid,.comparison,.finding-grid,.cost-trend{grid-template-columns:1fr}.program div{grid-template-columns:1fr}.toc ol,.practical ul{columns:1}.money-table{display:block;overflow-x:auto}'
if mobile_old in text:
    text = text.replace(mobile_old, mobile_new, 1)
elif '.finding-grid' not in text.split('@media(max-width:700px)', 1)[-1]:
    raise SystemExit('Nepodařilo se doplnit mobilní styly.')

# Rozšířit obsahový přehled o originální zjištění.
toc_anchor = '<li><a href="#poradatelstvi">Kdo akci pořádá</a></li>'
toc_extra = '<li><a href="#prerusena-tradice">Přerušená tradice</a></li><li><a href="#smlouvy-2026">Co už prozradily smlouvy</a></li><li><a href="#kolik-stoji">Kolik stojí vybrané části</a></li>'
if toc_anchor in text and '#kolik-stoji' not in text:
    text = text.replace(toc_anchor, toc_anchor + toc_extra, 1)

insert_anchor = '  <h2>Proč slavnost přežila více než tři desetiletí</h2>\n'
if insert_anchor not in text:
    raise SystemExit('Chybí místo pro vložení vlastních zjištění.')

original = '''  <section data-original-findings="contracts-v1">
  <h2 id="prerusena-tradice">„34. ročník“ neznamená 34 skutečně uskutečněných slavností</h2>
  <p>Na první pohled se zdá, že Císařský den probíhá bez přerušení od roku 1993. Číslování ale vypráví přesnější příběh. Kadaňské noviny označily návrat v roce 2022 za <strong>30. ročník po tříleté pauze</strong>. Rok 2022 byl zároveň třicátým kalendářním rokem od roku 1993 včetně.</p>
  <p>Z toho vyplývá, že číslo ročníku zřejmě sleduje kalendářní řadu tradice, nikoli pouze počet skutečně uskutečněných slavností. Letošní označení <strong>34. ročník</strong> proto není samo o sobě důkazem, že se akce konala čtyřiatřicetkrát. Přesný seznam všech uskutečněných a vynechaných ročníků by musel potvrdit městský archiv.</p>

  <div class="finding-grid">
    <div class="finding-card"><small>Oficiální tradice</small><b>Od roku 1993</b><p>Oficiální historie datuje pravidelné pořádání právě od tohoto roku.</p></div>
    <div class="finding-card"><small>Doložená mezera</small><b>Návrat v roce 2022</b><p>Místní noviny jej popsaly jako třicátý ročník po tříleté pauze.</p></div>
  </div>

  <h2 id="smlouvy-2026">Úplný program ještě není venku. Smlouvy už ale odhalují část letošního scénáře</h2>
  <p>Oficiální web zatím zdůrazňuje průvod, ceremonii a rytířský turnaj. Uzavřené smlouvy pro rok 2026 ukazují další konkrétní části, které se do stručné pozvánky dosud nevešly.</p>

  <div class="money-lead"><small>Čtyři zveřejněné programové položky roku 2026</small><strong>Nejméně 614 956 Kč</strong><p>Součet lovecké družiny, tichého pyromuzikálního ohňostroje, LED obrazovky a dobových her s rekvizitami. Nejde o úplný rozpočet akce.</p></div>

  <table class="money-table" aria-label="Vybrané smlouvy Císařského dne 2026">
    <thead><tr><th>Co smlouva zajišťuje</th><th>Dodavatel</th><th>Částka s DPH</th></tr></thead>
    <tbody>
      <tr><td>Vystoupení lovecké družiny</td><td>Klub Falconia, z. s.</td><td>229 500 Kč</td></tr>
      <tr><td>Tichý pyromuzikální ohňostroj u řeky Ohře</td><td>Petr Burian</td><td>229 900 Kč</td></tr>
      <tr><td>LED obrazovka v rámci Císařského dne</td><td>WEETEK s. r. o.</td><td>98 836 Kč</td></tr>
      <tr><td>Dobové hry, rekvizity, praporce a štíty</td><td>TERCIE-CV s. r. o.</td><td>56 720 Kč</td></tr>
      <tr class="sum"><td colspan="2">Součet těchto čtyř položek</td><td>614 956 Kč</td></tr>
    </tbody>
  </table>

  <p>Smlouvy tak předem potvrzují sokolnickou či loveckou část programu, dětské dobové hry, velkoplošnou obrazovku a večerní finále v podobě <strong>tichého pyromuzikálního ohňostroje u Ohře</strong>. Ústecký kraj současně poskytl městu na Císařský den 2026 dotaci 250 tisíc korun.</p>
  <div class="finding-warning"><strong>614 956 korun není cena celé slavnosti</strong>V částce nejsou započítány další účinkující, technické služby, produkce, kostýmy, bezpečnost, úklid, doprava, hlavní pódium ani vlastní práce města a KZK. Jde pouze o bezpečně sečtené položky, které byly k 1. srpnu 2026 ve veřejné evidenci popsány dostatečně konkrétně.</div>

  <h2 id="kolik-stoji">Kolik stojí Císařský den? Úplný účet veřejné záznamy samy nedají</h2>
  <p>Rozpočet slavnosti není zveřejněn jako jediná konečná částka. Platby jsou rozděleny mezi produkci, KZK, jednotlivé soubory, techniku, dopravu a další služby. Z roku 2025 lze přesto sestavit konzervativní minimum z šesti jednoznačně přiřaditelných smluv.</p>

  <table class="money-table" aria-label="Vybrané smlouvy Císařského dne 2025">
    <thead><tr><th>Vybraná položka roku 2025</th><th>Částka</th></tr></thead>
    <tbody>
      <tr><td>Zajištění akce prostřednictvím KZK</td><td>249 900 Kč</td></tr>
      <tr><td>Produkční zajištění</td><td>166 500 Kč</td></tr>
      <tr><td>Přípravné a realizační práce, kostýmy a rekvizity</td><td>165 000 Kč</td></tr>
      <tr><td>Velkoplošná obrazovka</td><td>96 010 Kč</td></tr>
      <tr><td>Celodenní historické vystoupení</td><td>50 100 Kč</td></tr>
      <tr><td>Sedm párů posilových vlaků</td><td>137 085 Kč</td></tr>
      <tr class="sum"><td>Součet šesti identifikovaných výdajů</td><td>864 595 Kč</td></tr>
    </tbody>
  </table>

  <p>Město mělo pro ročník 2025 zároveň reklamní smlouvu, v níž bylo uvedeno jako příjemce částky 242 tisíc korun. Prosté odečtení by u uvedených položek dalo 622 595 korun, ani to však není konečný čistý náklad: chybějí další výdaje i případné další příjmy.</p>

  <h3>Jedna opakující se položka se za šest let téměř ztrojnásobila</h3>
  <p>U smluv uzavíraných s KZK na technické nebo celkové zajištění je vidět výrazný nominální růst. V roce 2018 registr uváděl 82 652 korun bez DPH, v roce 2019 už 118 421 korun bez DPH, roku 2022 částku 161 074 korun bez DPH, v roce 2023 190 tisíc korun bez DPH a v roce 2024 229 900 korun bez DPH.</p>
  <div class="cost-trend">
    <div><b>82 652 Kč</b><span>2018 · technické zajištění, bez DPH</span></div>
    <div><b>161 074 Kč</b><span>2022 · technické zajištění, bez DPH</span></div>
    <div><b>229 900 Kč</b><span>2024 · technické zajištění, bez DPH</span></div>
  </div>
  <p>Částka roku 2024 byla přibližně <strong>2,8krát vyšší</strong> než hodnota uvedená u smlouvy z roku 2018. Samotné porovnání ale neprokazuje zdražení stejné služby: mohl se měnit rozsah, počet scén, technické požadavky i rozdělení prací mezi město a KZK.</p>

  <h3>Slavnost není jen kulturní program, ale celodenní městská operace</h3>
  <p>Smlouva na sedm párů posilových vlaků za 137 085 korun v roce 2025 ukazuje rozsah, který z běžné pozvánky není vidět. K tomu přistupují uzavírky, zásobování stánků, příprava několika scén, úklid, elektřina, bezpečnost, zázemí účinkujících a přesuny koní i historických skupin.</p>
  <p>Právě tato provozní vrstva vysvětluje, proč nelze náklady na Císařský den poměřovat pouze počtem koncertů nebo délkou programu. Na jeden den se mění způsob fungování velké části historického centra.</p>
  </section>

'''

text = text.replace(insert_anchor, original + insert_anchor, 1)

# Doplnit odkazy na zdroje, z nichž lze kontrolovat uvedené částky.
source_anchor = '      <li><a href="https://www.regionalni-znacky.cz/poohri/zazitky/cisarsky-den-v-kadani" target="_blank" rel="noopener">Poohří regionální produkt – certifikovaný zážitek Císařský den</a></li>\n'
source_extra = '''      <li><a href="https://www.noviny-kadan.cz/l/cisarsky-den-potricate/" target="_blank" rel="noopener">Kadaňské noviny – návrat 30. ročníku po tříleté pauze</a></li>
      <li><a href="https://smlouvy.gov.cz/smlouva/34560125" target="_blank" rel="noopener">Registr smluv – zajištění Císařského dne prostřednictvím KZK v roce 2025</a></li>
      <li><a href="https://smlouvy.gov.cz/smlouva/34368853" target="_blank" rel="noopener">Registr smluv – produkční zajištění ročníku 2025</a></li>
      <li><a href="https://smlouvy.gov.cz/smlouva/34368377" target="_blank" rel="noopener">Registr smluv – přípravné práce, kostýmy a rekvizity v roce 2025</a></li>
      <li><a href="https://smlouvy.gov.cz/smlouva/32980704" target="_blank" rel="noopener">Registr smluv – sedm párů posilových vlaků pro ročník 2025</a></li>
      <li><a href="https://smlouvy.gov.cz/vyhledavani?q=00261912" target="_blank" rel="noopener">Registr smluv – aktuální smlouvy města Kadaně včetně příprav ročníku 2026</a></li>
'''
if source_anchor not in text:
    raise SystemExit('Chybí kotva v seznamu zdrojů.')
text = text.replace(source_anchor, source_anchor + source_extra, 1)

# Postranní box s hlavním vlastním zjištěním.
aside_anchor = '  <div class="sidebox"><h3>Hlavní historická osa</h3>'
aside_box = '  <div class="sidebox"><h3>Co už víme o ceně</h3><p><strong>614 956 Kč</strong> dávají čtyři konkrétní smlouvy pro rok 2026. Úplný účet bude vyšší.</p><p><strong>250 000 Kč</strong> poskytl Ústecký kraj jako dotaci.</p></div>\n'
if aside_anchor in text:
    text = text.replace(aside_anchor, aside_box + aside_anchor, 1)

PATH.write_text(text, encoding='utf-8', newline='\n')

checks = (
    'data-expanded-cisarsky-den="v2"',
    'data-original-findings="contracts-v1"',
    'Nejméně 614 956 Kč',
    'Součet šesti identifikovaných výdajů',
    '864 595 Kč',
    '2,8krát vyšší',
    '30. ročník po tříleté pauze',
    'sedm párů posilových vlaků',
)
for marker in checks:
    if marker not in text:
        raise SystemExit(f'Chybí kontrolní značka: {marker}')

print('Do návrhu byla doplněna vlastní rekonstrukce ročníků, programu a nákladů.')
