#!/usr/bin/env python3
from pathlib import Path

path=Path('.github/drafts/cisarsky-den-kadan-historie-2026.html')
text=path.read_text(encoding='utf-8')

if 'data-2026-contract-minimum="861257"' in text:
    print('Rozšířený součet roku 2026 už je vložen.')
    raise SystemExit(0)

old='''  <div class="money-lead"><small>Čtyři konkrétní položky</small><strong>Nejméně 614 956 Kč</strong><p>Lovecká družina, tichý pyromuzikální ohňostroj, LED obrazovka a dobové hry.</p></div>
  <table class="money-table"><tr><th>Položka</th><th>Částka</th></tr><tr><td>Lovecká družina</td><td>229 500 Kč</td></tr><tr><td>Tichý pyromuzikální ohňostroj</td><td>229 900 Kč</td></tr><tr><td>LED obrazovka</td><td>98 836 Kč</td></tr><tr><td>Dobové hry a rekvizity</td><td>56 720 Kč</td></tr><tr class="sum"><td>Součet</td><td>614 956 Kč</td></tr></table>
  <p>Kraj poskytl městu dotaci 250 000 korun. Částka 614 956 korun není úplným rozpočtem slavnosti.</p>'''
new='''  <div class="money-lead" data-2026-contract-minimum="861257"><small>Šest konkrétních smluv roku 2026</small><strong>Nejméně 861 257 Kč</strong><p>Lovecká družina, rytířský turnaj, ohňostroj, LED obrazovka, dobové hry a hygienické zázemí. Stále nejde o úplný rozpočet.</p></div>
  <table class="money-table"><tr><th>Položka</th><th>Částka s DPH</th></tr><tr><td>Vystoupení lovecké družiny</td><td>229 500 Kč</td></tr><tr><td>Tichý pyromuzikální ohňostroj u Ohře</td><td>229 900 Kč</td></tr><tr><td>Rytířský turnaj na koních</td><td>146 500 Kč</td></tr><tr><td>Hygienické zázemí</td><td>99 801 Kč</td></tr><tr><td>LED obrazovka</td><td>98 836 Kč</td></tr><tr><td>Dobové hry a rekvizity</td><td>56 720 Kč</td></tr><tr class="sum"><td>Součet šesti smluv</td><td>861 257 Kč</td></tr></table>
  <p>Ústecký kraj poskytl městu na letošní Císařský den dotaci <strong>250 000 korun</strong>. Ani po jejím zohlednění nelze určit čistý náklad, protože zveřejněné smlouvy nepokrývají všechny výdaje ani všechny příjmy.</p>
  <div class="finding-warning"><strong>Další smlouva za 726 000 korun zůstává účetní neznámou</strong>V evidenci je vedena jako „Poskytnutí reklamní služby při pořádání akce Císařský den“ se smluvní stranou Václav Šťastný. Dokud nebude bezpečně rozlišeno, kdo komu a za jaké plnění částku hradí, nezapočítáváme ji ani do nákladů, ani do příjmů slavnosti.</div>'''
if old not in text:
    raise SystemExit('Původní čtyřpoložkový součet nebyl nalezen.')
text=text.replace(old,new,1)

aside='  <div class="sidebox"><h3>Hlavní historická osa</h3>'
box='  <div class="sidebox"><h3>Částečný účet 2026</h3><p><strong>861 257 Kč</strong> dává šest konkrétních smluv.</p><p>Kraj přidal dotaci <strong>250 000 Kč</strong>. Úplný účet zatím známý není.</p></div>\n'
if aside in text and 'Částečný účet 2026' not in text:
    text=text.replace(aside,box+aside,1)

path.write_text(text,encoding='utf-8',newline='\n')
for marker in ('data-2026-contract-minimum="861257"','Nejméně 861 257 Kč','Rytířský turnaj na koních','Hygienické zázemí','726 000 korun'):
    assert marker in text,marker
print('Součet smluv roku 2026 byl rozšířen na šest položek.')
