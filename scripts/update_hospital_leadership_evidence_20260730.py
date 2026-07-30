#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

# Poslední ověřená redakční aktualizace.
for old in ('2026-07-30T10:25:00+02:00', '2026-07-30T11:20:00+02:00'):
    text = text.replace(old, '2026-07-30T11:29:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 10:25', 'Aktuální zpráva · aktualizováno v 11:29')
text = text.replace('Aktuální zpráva · aktualizováno v 11:20', 'Aktuální zpráva · aktualizováno v 11:29')
text = text.replace('Aktualizace 30. července v 11:20', 'Aktualizace 30. července v 11:29')
text = text.replace('k 30. červenci v 10:25 nebyl', 'k 30. červenci v 11:29 nebyl')
text = text.replace('k 30. červenci v 11:20 nebyl', 'k 30. červenci v 11:29 nebyl')
text = text.replace('při kontrole 30. července v 10:25', 'při kontrole 30. července v 11:29')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 10:25.', 'Poslední ověřená aktualizace 30. července 2026 v 11:29.')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 11:20.', 'Poslední ověřená aktualizace 30. července 2026 v 11:29.')

old_update = ('<div class="update-box"><strong>Aktualizace 30. července v 11:29</strong><p>'
              'Rozšířili jsme kontrolu o registr smluv, úřední desku, veřejná vyjádření, soukromou e-petici a dřívější zprávy vedení nemocnice. '
              'Konkrétní odstupné Martina Krušiny stále není doloženo. Částka 6,48 milionu korun, která se objevila ve veřejné debatě, není odstupným: '
              'Petr Hossner ji uvedl jako vlastní výpočet možné povinnosti jednatele vracet až dvouletou odměnu v hypotetickém insolvenčním řízení. '
              'Výpis z mimořádné rady 29. července ani pozvánka na mimořádné zastupitelstvo dosud zveřejněny nejsou.</p></div>')
new_update = ('<div class="update-box"><strong>Aktualizace 30. července v 11:29</strong><p>'
              'Prověřili jsme také kompletní výroční zprávu a audit za rok 2025. Konkrétní odstupné Martina Krušiny stále není doloženo a veřejně zmiňovaných 6,48 milionu korun odstupným není. '
              'Nemocnice měla na konci roku jen 12 milionů korun peněžních prostředků oproti 109,7 milionu o rok dříve, výroční zpráva však uvádí dodavatelské závazky celé ve lhůtě splatnosti. '
              'Výpis z mimořádné rady 29. července ani pozvánka na mimořádné zastupitelstvo dosud zveřejněny nejsou.</p></div>')
if old_update in text:
    text = text.replace(old_update, new_update)

anchor = '  <h2>Mimořádné zastupitelstvo zatím není oficiálně svolané</h2>'
financial = '''  <h2>Co přesně ukazuje výroční zpráva za rok 2025</h2>
  <p>Výroční zpráva podepsaná Martinem Krušinou popisuje ekonomickou situaci jako složitou, nikoli však jako potvrzený úpadek. Za hlavní příčinu záporného výsledku označuje růst mezd a zákonných odvodů, nutnost stabilizovat personál a úhrady zdravotních pojišťoven, které podle vedení nepokrývají skutečné náklady regionální akutní péče.</p>
  <div class="fact-grid">
    <div class="fact-card"><span>Likvidita</span><strong>12 mil. Kč</strong><p>Peněžní prostředky klesly ze 109,659 milionu na 12 milionů korun. Jde o nejvýraznější varovný ukazatel zveřejněných výkazů.</p></div>
    <div class="fact-card"><span>Závazky</span><strong>105,177 mil. Kč</strong><p>Krátkodobé závazky byly vysoké, ale dodavatelské závazky ve výši 28,002 milionu zpráva vykazuje celé ve lhůtě splatnosti. To samo o sobě nepotvrzuje platební neschopnost.</p></div>
    <div class="fact-card"><span>Personál</span><strong>479,58 úvazku</strong><p>Přepočtený počet zaměstnanců vzrostl z 464,93 na 479,58. Osobní náklady se zvýšily o 28,487 milionu na 491,581 milionu korun.</p></div>
    <div class="fact-card"><span>Péče</span><strong>Vývoj byl smíšený</strong><p>Hospitalizace klesly z 8 929 na 8 287 a porody z 567 na 469. Operace naopak vzrostly z 2 790 na 2 906, ambulantní vyšetření zůstala téměř stejná.</p></div>
  </div>
  <p>Lůžkový fond se zároveň rozšířil z 234 na 254 lůžek, zejména zvýšením kapacity LDN z 34 na 54 lůžek. Nemocnice v roce 2025 pořídila dlouhodobý majetek za 66,185 milionu korun, z toho 64,728 milionu připadlo na software. Tato investice je samostatně rozebrána v dřívějším článku Naší Kadaně.</p>
  <div class="callout"><strong>Co z čísel nelze vyvodit</strong><p>Výroční zpráva dokládá prudký úbytek hotovosti a vysokou ztrátu. Bez aktuálních údajů o splatných závazcích po 31. prosinci, cash-flow v roce 2026 a platební schopnosti však nelze jako fakt tvrdit, že nemocnice byla nebo je v úpadku.</p></div>

'''
if 'Co přesně ukazuje výroční zpráva za rok 2025' not in text:
    text = text.replace(anchor, financial + anchor)

source_anchor = '    <li><a href="https://www.mesto-kadan.cz/cs/mesto/zastupitelstvo-mesta/terminy-zasedani-zastupitelstva.html" target="_blank" rel="noopener noreferrer">Město Kadaň – termíny zasedání zastupitelstva</a>.</li>\n'
annual_source = ('    <li><a href="https://www.nemkadan.cz/pro-verejnost/o-nas/vyrocni-zpravy/" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – výroční zpráva, účetní závěrka a výrok auditora za rok 2025</a>.</li>\n'
                 '    <li><a href="https://nasekadan.cz/clanky/nemocnice-kadan.html" target="_blank" rel="noopener noreferrer">Naše Kadaň – podrobná analýza hospodaření nemocnice za rok 2025</a>.</li>\n')
if 'výroční zpráva, účetní závěrka a výrok auditora za rok 2025' not in text:
    text = text.replace(source_anchor, annual_source + source_anchor)

if 'Co přesně ukazuje výroční zpráva za rok 2025' not in text:
    raise SystemExit('Finanční část se nevložila')
if '2026-07-30T11:29:00+02:00' not in text:
    raise SystemExit('Čas aktualizace se nezměnil')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o úplná čísla výroční zprávy a audit za rok 2025.')
