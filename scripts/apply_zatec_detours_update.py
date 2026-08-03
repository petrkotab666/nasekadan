#!/usr/bin/env python3
from pathlib import Path

PATH = Path(__file__).resolve().parent / 'publish_zatec_kadan_prejezd_20260803.py'
text = PATH.read_text(encoding='utf-8')

if 'MODIFIED = "2026-08-03T21:55:00+02:00"' not in text:
    text = text.replace(
        'PUBLISHED = "2026-08-03T18:35:00+02:00"\nRSS_DATE = "Mon, 03 Aug 2026 18:35:00 +0200"',
        'PUBLISHED = "2026-08-03T18:35:00+02:00"\nMODIFIED = "2026-08-03T21:55:00+02:00"\nRSS_DATE = "Mon, 03 Aug 2026 18:35:00 +0200"',
        1,
    )
text = text.replace('"dateModified": PUBLISHED,', '"dateModified": MODIFIED,', 1)
text = text.replace('<meta property="article:modified_time" content="{PUBLISHED}">', '<meta property="article:modified_time" content="{MODIFIED}">', 1)

text = text.replace(
    '    .leadtext{{font-size:23px!important;color:#465862;line-height:1.55!important}}\n',
    '    .leadtext{{font-size:23px!important;color:#465862;line-height:1.55!important}}\n    .updated-note{{background:#fff4dc;border:1px solid #ead19a;border-radius:12px;padding:12px 15px;font-size:15px!important;color:#674b13}}\n',
    1,
)

lead = '''  <p class="leadtext"><strong>Úplná uzavírka silnice II/225 za Žatcem začne v úterý 4. srpna v 7 hodin a skončit má 11. srpna v 6 hodin. Kraj současně eviduje další přejezd označený jako Žabokliky, který bude uzavřen od 11. do 28. srpna. Právě dvě různá místa způsobila zmatek v termínech.</strong></p>'''
if 'class="updated-note"' not in text:
    text = text.replace(
        lead,
        lead + '\n  <p class="updated-note"><strong>Aktualizováno 3. srpna ve 21:55:</strong> Město Žatec zveřejnilo přesné objízdné trasy pro vozidla do 3,5 tuny a nad 3,5 tuny. Článek jsme podle oficiálního oznámení doplnili.</p>',
        1,
    )

reason_anchor = '''  <p>Odbor dopravně správních agend Městského úřadu Žatec povolil uzavírku od <strong>4. srpna 2026 v 7:00</strong> do <strong>11. srpna 2026 v 6:00</strong>. Stejný interval uvádí také informační systém Dopravy Ústeckého kraje, který tuto událost vede pod názvem <strong>Nové Sedlo – uzavírka železničního přejezdu</strong>.</p>'''
if 'výstavba nového přejezdového systému' not in text:
    text = text.replace(
        reason_anchor,
        reason_anchor + '\n\n  <p>Důvodem omezení je podle města <strong>výstavba nového přejezdového systému</strong>, která má zvýšit bezpečnost silniční i železniční dopravy.</p>',
        1,
    )

old_route = '''  <h2>Co čeká řidiče na cestě mezi Žatcem a Kadaní</h2>
  <p>Přes první opravovaný přejezd na silnici II/225 nebude možné projet. Pro osobní a nákladní dopravu bude rozhodující dočasné dopravní značení na místě.</p>

  <p>V dostupném oznámení města ani v krajském přehledu není podrobně popsána celá objízdná trasa pro běžná auta. Proto není bezpečné doporučovat konkrétní zkratku pouze podle mapy. Řidiči by měli počítat s delší cestou, sledovat značení a před cestou si nechat časovou rezervu.</p>

  <p>Uzavírka začíná už následující ráno. Omezení tak může zasáhnout dojíždění za prací, cesty k lékaři i běžné spojení mezi Kadaní, obcemi na trase a Žatcem.</p>'''
new_route = '''  <h2>Osobní auta přes Žabokliky, těžší vozidla dlouhou objížďkou</h2>
  <p>Přes uzavřený přejezd na silnici II/225 nebude možné projet. Město Žatec zveřejnilo dvě rozdílné objízdné trasy podle hmotnosti vozidla.</p>

  <div class="info-box">
    <strong>Vozidla do 3,5 tuny:</strong> budou vedena <strong>obousměrně přes Žabokliky</strong>. Tato kratší objížďka se týká zejména osobních aut a lehkých dodávek.
  </div>

  <div class="info-box">
    <strong>Vozidla nad 3,5 tuny:</strong> ve směru ze Žatce pojedou od Kauflandu směrem na Plzeň přes <strong>Radíčeves, Sýrovice, Pšov, Dolánky, Vysoké Třebčice, Široké Třebčice, Račetice a Pětipsy</strong>. V Pětipsech se napojí zpět na silnici II/225.
  </div>

  <p>Pro těžší dopravu jde o výrazně delší trasu vedenou jižně od Nechranické přehrady. Řidiči jedoucí v opačném směru se musí řídit dočasným dopravním značením. Město vyzývá k vyšší opatrnosti a k počítání s delší dobou jízdy.</p>

  <p>Uzavírka začíná už následující ráno. Omezení tak může zasáhnout dojíždění za prací, cesty k lékaři i běžné spojení mezi Kadaní, obcemi na trase a Žatcem.</p>'''
if old_route in text:
    text = text.replace(old_route, new_route, 1)

text = text.replace(
    '    <li>přesnou trasu značené objížďky pro všechna osobní a nákladní vozidla,</li>\n    <li>podrobný technický rozsah opravy jednotlivých přejezdů,</li>',
    '    <li>podrobnou technickou specifikaci nového přejezdového systému,</li>',
    1,
)
text = text.replace(
    'Město Žatec – oznámení úplné uzavírky silnice II/225 od 4. do 11. srpna',
    'Město Žatec – oznámení, objízdné trasy a mapa uzavírky silnice II/225',
    1,
)
if '<h3>Objížďky</h3>' not in text:
    text = text.replace(
        '  <div class="sidebox"><h3>Autobus 415</h3>',
        '  <div class="sidebox"><h3>Objížďky</h3><ul><li>Do 3,5 t přes Žabokliky</li><li>Nad 3,5 t přes Pětipsy a Račetice</li></ul></div>\n  <div class="sidebox"><h3>Autobus 415</h3>',
        1,
    )

required = [
    'MODIFIED = "2026-08-03T21:55:00+02:00"',
    'Osobní auta přes Žabokliky',
    'Vysoké Třebčice',
    'výstavba nového přejezdového systému',
    '<h3>Objížďky</h3>',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f'Nepodařilo se doplnit: {missing}')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Publikační zdroj objížděk byl trvale aktualizován.')
