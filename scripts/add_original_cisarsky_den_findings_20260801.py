#!/usr/bin/env python3
from pathlib import Path

path=Path('.github/drafts/cisarsky-den-kadan-historie-2026.html')
text=path.read_text(encoding='utf-8')
if 'data-original-findings="contracts-v1"' in text:
    print('Vlastní zjištění už jsou vložena.')
    raise SystemExit(0)

css='''    .money-lead{margin:36px 0;padding:27px;border-radius:20px;background:linear-gradient(135deg,#142b37,#243f4b);color:#fff;box-shadow:0 16px 40px rgba(18,35,45,.18)}.money-lead small{display:block;color:#ffdca1;font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.money-lead strong{display:block;margin:7px 0 9px;font:900 34px/1.08 Georgia,serif}.money-lead p{margin:0;color:#edf4f6;font-size:16px}\n    .money-table{width:100%;margin:25px 0;border-collapse:collapse;border-radius:17px;background:#fff;box-shadow:0 10px 30px rgba(18,35,45,.06)}.money-table th,.money-table td{padding:14px 15px;border-bottom:1px solid #e1e6e8;text-align:left;vertical-align:top}.money-table th{background:#172b37;color:#fff;font-size:14px}.money-table td{font-size:15px;line-height:1.45}.money-table td:last-child,.money-table th:last-child{text-align:right;white-space:nowrap}.money-table .sum td{font-weight:900;background:#f7f1e7}.finding-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:28px 0}.finding-card{padding:22px;border:1px solid #d9e2e5;border-radius:18px;background:#fff}.finding-card small{display:block;color:#9f2626;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.finding-card b{display:block;margin:6px 0 8px;font:900 25px/1.12 Georgia,serif}.finding-card p{margin:0;color:#53616a;font-size:15px}.finding-warning{margin:26px 0;padding:21px 23px;border:1px solid #d8c58e;border-left:6px solid #b1842f;border-radius:0 17px 17px 0;background:#fff9e9}.finding-warning strong{display:block;margin-bottom:6px;font:800 21px Georgia,serif}.cost-trend{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin:24px 0}.cost-trend div{padding:18px;border-radius:16px;background:#fff;border:1px solid #dce3e6;text-align:center}.cost-trend b{display:block;color:#9f2626;font:900 24px/1.1 Georgia,serif}.cost-trend span{display:block;margin-top:5px;color:#617078;font-size:13px}\n'''
anchor='    .source-list{margin-top:44px;padding:24px;border-radius:18px;background:#eef3f5}'
if anchor not in text: raise SystemExit('Chybí CSS kotva.')
text=text.replace(anchor,css+anchor,1)

section='''  <section data-original-findings="contracts-v1">
  <h2>„34. ročník“ neznamená 34 skutečně uskutečněných slavností</h2>
  <p>Kadaňské noviny označily návrat v roce 2022 za <strong>30. ročník po tříleté pauze</strong>. Rok 2022 byl zároveň třicátým kalendářním rokem od roku 1993 včetně. Číslo ročníku tak zřejmě sleduje kalendářní řadu tradice, nikoli pouze počet skutečně uskutečněných slavností. Letošní označení 34. ročník proto samo o sobě nedokládá, že se akce konala čtyřiatřicetkrát.</p>
  <div class="finding-grid"><div class="finding-card"><small>Počátek tradice</small><b>1993</b><p>Rok prvního pravidelně pořádaného Císařského dne.</p></div><div class="finding-card"><small>Doložené přerušení</small><b>Tříletá pauza</b><p>Návrat roku 2022 byl přesto označen jako 30. ročník.</p></div></div>

  <h2>Smlouvy už odhalují část programu roku 2026</h2>
  <p>Vedle průvodu, ceremonie a rytířského turnaje potvrzují smlouvy loveckou družinu, dobové hry, LED obrazovku a večerní tichý pyromuzikální ohňostroj u řeky Ohře.</p>
  <div class="money-lead"><small>Čtyři konkrétní programové položky roku 2026</small><strong>Nejméně 614 956 Kč</strong><p>Jde jen o částečný součet, nikoli o úplný rozpočet slavnosti.</p></div>
  <table class="money-table"><thead><tr><th>Položka</th><th>Dodavatel</th><th>Částka s DPH</th></tr></thead><tbody><tr><td>Vystoupení lovecké družiny</td><td>Klub Falconia</td><td>229 500 Kč</td></tr><tr><td>Tichý pyromuzikální ohňostroj u Ohře</td><td>Petr Burian</td><td>229 900 Kč</td></tr><tr><td>LED obrazovka</td><td>WEETEK</td><td>98 836 Kč</td></tr><tr><td>Dobové hry, rekvizity, praporce a štíty</td><td>TERCIE-CV</td><td>56 720 Kč</td></tr><tr class="sum"><td colspan="2">Součet</td><td>614 956 Kč</td></tr></tbody></table>
  <p>Ústecký kraj současně poskytl městu na Císařský den 2026 dotaci <strong>250 000 korun</strong>.</p>
  <div class="finding-warning"><strong>Nejde o cenu celé akce</strong>Chybějí další účinkující, produkce, technické služby, pódia, bezpečnost, úklid, doprava, kostýmy i práce města a KZK.</div>

  <h2>Rok 2025: šest konkrétních výdajů dává nejméně 864 595 korun</h2>
  <table class="money-table"><thead><tr><th>Vybraná položka roku 2025</th><th>Částka</th></tr></thead><tbody><tr><td>Zajištění akce prostřednictvím KZK</td><td>249 900 Kč</td></tr><tr><td>Produkční zajištění</td><td>166 500 Kč</td></tr><tr><td>Přípravné práce, kostýmy a rekvizity</td><td>165 000 Kč</td></tr><tr><td>Velkoplošná obrazovka</td><td>96 010 Kč</td></tr><tr><td>Celodenní historické vystoupení</td><td>50 100 Kč</td></tr><tr><td>Sedm párů posilových vlaků</td><td>137 085 Kč</td></tr><tr class="sum"><td>Součet šesti identifikovaných výdajů</td><td>864 595 Kč</td></tr></tbody></table>
  <p>Město bylo zároveň příjemcem reklamní platby 242 tisíc korun. Ani po jejím odečtení nelze určit čistý účet, protože ve veřejném součtu nejsou všechny výdaje ani všechny příjmy.</p>

  <h3>Opakující se položka KZK se nominálně téměř ztrojnásobila</h3>
  <p>Technické či celkové zajištění uváděné ve smlouvách vzrostlo z 82 652 korun bez DPH v roce 2018 na 229 900 korun bez DPH v roce 2024.</p>
  <div class="cost-trend"><div><b>82 652 Kč</b><span>2018 · bez DPH</span></div><div><b>161 074 Kč</b><span>2022 · bez DPH</span></div><div><b>229 900 Kč</b><span>2024 · bez DPH</span></div></div>
  <p>Hodnota roku 2024 byla přibližně <strong>2,8krát vyšší</strong> než v roce 2018. Nelze ji ale automaticky vydávat za zdražení stejné služby, protože se mohl měnit rozsah prací a způsob rozdělení úkolů.</p>

  <h3>Sedm párů posilových vlaků ukazuje skutečný rozsah akce</h3>
  <p>Objednávka posilových vlaků za 137 085 korun připomíná, že slavnost není jen soubor vystoupení. Na jeden den mění dopravu, zásobování, bezpečnost, úklid i fungování velké části historického centra.</p>
  </section>

'''
insert='  <h2>Proč slavnost přežila více než tři desetiletí</h2>\n'
if insert not in text: raise SystemExit('Chybí obsahová kotva.')
text=text.replace(insert,section+insert,1)

aside='  <div class="sidebox"><h3>Hlavní historická osa</h3>'
if aside in text:text=text.replace(aside,'  <div class="sidebox"><h3>Co už víme o ceně</h3><p><strong>614 956 Kč</strong> dávají čtyři konkrétní smlouvy roku 2026. Úplný účet bude vyšší.</p><p>Kraj přidal dotaci <strong>250 000 Kč</strong>.</p></div>\n'+aside,1)

path.write_text(text,encoding='utf-8',newline='\n')
for marker in ('data-original-findings="contracts-v1"','Nejméně 614 956 Kč','864 595 Kč','2,8krát vyšší','30. ročník po tříleté pauze','Sedm párů posilových vlaků'):
    if marker not in text:raise SystemExit('Chybí: '+marker)
print('Vlastní zjištění vložena.')
