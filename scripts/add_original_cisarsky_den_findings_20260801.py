#!/usr/bin/env python3
from pathlib import Path
p=Path('.github/drafts/cisarsky-den-kadan-historie-2026.html')
t=p.read_text(encoding='utf-8')
if 'data-original-findings="contracts-v1"' in t:
 print('Hotovo');raise SystemExit(0)
a='    .source-list{margin-top:44px;padding:24px;border-radius:18px;background:#eef3f5}'
c='''    .money-lead{margin:36px 0;padding:27px;border-radius:20px;background:#142b37;color:#fff}.money-lead strong{display:block;margin:7px 0;font:900 34px Georgia,serif}.money-table{width:100%;margin:25px 0;border-collapse:collapse;background:#fff}.money-table th,.money-table td{padding:14px;border-bottom:1px solid #e1e6e8;text-align:left}.money-table th{background:#172b37;color:#fff}.money-table td:last-child,.money-table th:last-child{text-align:right}.money-table .sum td{font-weight:900;background:#f7f1e7}.finding-grid,.cost-trend{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:28px 0}.finding-card,.cost-trend div{padding:20px;border:1px solid #d9e2e5;border-radius:17px;background:#fff}.finding-card b,.cost-trend b{display:block;color:#9f2626;font:900 24px Georgia,serif}.finding-warning{margin:25px 0;padding:21px;border-left:6px solid #b1842f;background:#fff9e9}\n'''
if a not in t:raise SystemExit('CSS')
t=t.replace(a,c+a,1)
s='''  <section data-original-findings="contracts-v1">
  <h2>„34. ročník“ neznamená 34 skutečně uskutečněných slavností</h2>
  <p>Kadaňské noviny označily návrat v roce 2022 za <strong>30. ročník po tříleté pauze</strong>. Číslo ročníku proto zřejmě sleduje kalendářní řadu tradice, nikoli pouze počet skutečně uskutečněných slavností.</p>
  <div class="finding-grid"><div class="finding-card"><b>1993</b><p>Začátek pravidelné tradice.</p></div><div class="finding-card"><b>Tříletá pauza</b><p>Doložené přerušení před návratem v roce 2022.</p></div></div>
  <h2>Smlouvy už odhalují část programu roku 2026</h2>
  <div class="money-lead"><small>Čtyři konkrétní položky</small><strong>Nejméně 614 956 Kč</strong><p>Lovecká družina, tichý pyromuzikální ohňostroj, LED obrazovka a dobové hry.</p></div>
  <table class="money-table"><tr><th>Položka</th><th>Částka</th></tr><tr><td>Lovecká družina</td><td>229 500 Kč</td></tr><tr><td>Tichý pyromuzikální ohňostroj</td><td>229 900 Kč</td></tr><tr><td>LED obrazovka</td><td>98 836 Kč</td></tr><tr><td>Dobové hry a rekvizity</td><td>56 720 Kč</td></tr><tr class="sum"><td>Součet</td><td>614 956 Kč</td></tr></table>
  <p>Kraj poskytl městu dotaci 250 000 korun. Částka 614 956 korun není úplným rozpočtem slavnosti.</p>
  <h2>Rok 2025: šest výdajů dává nejméně 864 595 korun</h2>
  <table class="money-table"><tr><th>Položka</th><th>Částka</th></tr><tr><td>Zajištění prostřednictvím KZK</td><td>249 900 Kč</td></tr><tr><td>Produkce</td><td>166 500 Kč</td></tr><tr><td>Kostýmy, rekvizity a příprava</td><td>165 000 Kč</td></tr><tr><td>Obrazovka</td><td>96 010 Kč</td></tr><tr><td>Historické vystoupení</td><td>50 100 Kč</td></tr><tr><td>Sedm párů posilových vlaků</td><td>137 085 Kč</td></tr><tr class="sum"><td>Součet šesti identifikovaných výdajů</td><td>864 595 Kč</td></tr></table>
  <h3>Opakující se položka KZK se nominálně téměř ztrojnásobila</h3>
  <div class="cost-trend"><div><b>82 652 Kč</b><p>2018, bez DPH</p></div><div><b>229 900 Kč</b><p>2024, bez DPH</p></div></div>
  <p>Částka roku 2024 byla přibližně <strong>2,8krát vyšší</strong>. Rozsah služeb se ale mohl měnit, takže nejde automaticky o srovnání totožného plnění.</p>
  </section>

'''
i='  <h2>Proč slavnost přežila více než tři desetiletí</h2>\n'
if i not in t:raise SystemExit('kotva')
t=t.replace(i,s+i,1)
p.write_text(t,encoding='utf-8',newline='\n')
for x in ('data-original-findings="contracts-v1"','Nejméně 614 956 Kč','864 595 Kč','2,8krát vyšší','Sedm párů posilových vlaků'):
 assert x in t,x
print('Hotovo')
