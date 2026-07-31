#!/usr/bin/env python3
from pathlib import Path
import re

article_path = Path('clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html')
rss_path = Path('rss.xml')
text = article_path.read_text(encoding='utf-8')

marker = 'data-vorac-srpen-2026'
section = '''
  <h3 data-vorac-srpen-2026>Kožní ambulance MUDr. Stanislava Voráče</h3>
  <p>Soukromá kožní ambulance MUDr. Stanislava Voráče oznámila dovolenou od <strong>3. do 14. srpna 2026</strong>. Uzavření se týká pracoviště v Kadani i v Klášterci nad Ohří. Kadaňská ordinace sídlí v poliklinice Nemocnice Kadaň, Golovinova 1559, a běžně ordinuje v pondělí od 7:00 do 15:00, ve středu od 7:00 do 13:30 a v pátek od 7:30 do 13:00. Klášterecká ordinace je v poliklinice Sadová 528 a běžně ordinuje v úterý od 7:30 do 12:00 a ve čtvrtek od 12:00 do 18:00.</p>
  <p>Kontakt pro Kadaň je <strong>474 944 246</strong>, pro Klášterec nad Ohří <strong>731 379 374</strong>; e-mail ordinace je <a href="mailto:vorac.s@seznam.cz">vorac.s@seznam.cz</a>. Ve zveřejněném oznámení není uvedena náhradní zastupující kožní ambulance, proto je vhodné neakutní záležitosti vyřídit před dovolenou nebo si další postup telefonicky ověřit.</p>
'''

text = text.replace(
    'Přehled omezení a změn ordinací v Kadani a okolí: praktičtí lékaři, neurologie, ORL, očkovací centrum, cévní ambulance, gynekologie a dětská ordinace v Klášterci.',
    'Přehled omezení a změn ordinací v Kadani a okolí: praktičtí lékaři, kožní ambulance, neurologie, ORL, očkovací centrum, cévní ambulance, gynekologie a dětská ordinace v Klášterci.'
)
text = text.replace(
    'Přehled zahrnuje praktické lékaře, neurologii, ORL, očkovací centrum, změnu cévní ambulance a dvě omezení pracovišť v Klášterci.',
    'Přehled zahrnuje praktické lékaře, kožní ambulanci, neurologii, ORL, očkovací centrum, změnu cévní ambulance a další omezení pracovišť v Klášterci.'
)
text = re.sub(r'(<meta property="article:modified_time" content=")[^"]+("\s*/?>)', r'\g<1>2026-07-31T17:52:00+02:00\2', text)
text = re.sub(r'("dateModified":")[^"]+("\s*[,}])', r'\g<1>2026-07-31T17:52:00+02:00\2', text)
text = text.replace('AKTUALIZOVÁNO 29. ČERVENCE 2026', 'AKTUALIZOVÁNO 31. ČERVENCE 2026')

lead_anchor = 'Přehled jsme doplnili také o další potvrzená omezení zdravotních služeb v Kadani a okolí.'
lead_replacement = ('Přehled jsme doplnili také o další potvrzená omezení zdravotních služeb v Kadani a okolí. '
                    'Nově je v něm dovolená kožní ambulance MUDr. Stanislava Voráče v Kadani i Klášterci od 3. do 14. srpna.')
text = text.replace(lead_anchor, lead_replacement)

date_anchor = '    <div><b>10.–21. 8.</b><span>dovolená MUDr. Šindeláře</span></div>\n'
if 'dovolená kožní ambulance MUDr. Voráče' not in text:
    text = text.replace(date_anchor, date_anchor + '    <div><b>3.–14. 8.</b><span>dovolená kožní ambulance MUDr. Voráče v Kadani i Klášterci</span></div>\n')

text = text.replace(
    '<div class="notice"><h3>V přehledu je osm kadaňských pracovišť a dvě regionální omezení</h3><p>V Kadani jde o tři ambulance praktických lékařů, neurologii, ORL, očkovací centrum, cévní ambulanci a interní ambulanci.',
    '<div class="notice"><h3>V přehledu je devět kadaňských pracovišť a tři regionální omezení</h3><p>V Kadani jde o tři ambulance praktických lékařů, kožní ambulanci MUDr. Voráče, neurologii, ORL, očkovací centrum, cévní ambulanci a interní ambulanci.'
)
text = text.replace(
    'V Klášterci nad Ohří se omezení týká gynekologické ambulance a ordinace praktického lékaře pro děti a dorost.',
    'V Klášterci nad Ohří se omezení týká kožní ambulance MUDr. Voráče, gynekologické ambulance a ordinace praktického lékaře pro děti a dorost.'
)

if marker not in text:
    text = text.replace('  <h3>ORL ambulance</h3>\n', section + '\n  <h3>ORL ambulance</h3>\n')

text = text.replace(
    'U neurologie, ORL a očkovacího centra jsou zveřejněny dny uzavření, nikoli konkrétní náhradní pracoviště.',
    'U kožní ambulance MUDr. Voráče, neurologie, ORL a očkovacího centra jsou zveřejněny dny uzavření, nikoli konkrétní náhradní pracoviště.'
)

source_anchor = '    <li><a href="https://www.nemkadan.cz/ambulance-1/orl-tonova-audiometrie-a-foniatrie/"'
source_item = ('    <li><a href="https://mudr-vorac.webnode.cz/" target="_blank" rel="noopener noreferrer">'
               'MUDr. Stanislav Voráč – oficiální web ordinace</a>: adresy, kontakty a běžné ordinační hodiny; '
               'termín dovolené 3.–14. srpna byl převzat z veřejného oznámení ambulance zachyceného 31. července 2026.</li>\n')
if 'MUDr. Stanislav Voráč – oficiální web ordinace' not in text:
    text = text.replace(source_anchor, source_item + source_anchor)

text = re.sub(r'<small>Stav ověřen [^<]+</small>', '<small>Stav aktualizován 31. července 2026 v 17:52.</small>', text)

sidebar_anchor = '<li>MUDr. Šindelář: dovolená 10.–21. 8.</li>'
if '<li>Kožní MUDr. Voráč: dovolená 3.–14. 8.</li>' not in text:
    text = text.replace(sidebar_anchor, sidebar_anchor + '<li>Kožní MUDr. Voráč: dovolená 3.–14. 8.</li>')
text = text.replace('Osm pracovišť v Kadani + dvě omezení v Klášterci', 'Devět pracovišť v Kadani + tři omezení v Klášterci')

article_path.write_text(text, encoding='utf-8', newline='\n')

if rss_path.exists():
    rss = rss_path.read_text(encoding='utf-8')
    rss = rss.replace(
        'Přehled zahrnuje praktické lékaře, neurologii, ORL, očkovací centrum, změnu cévní ambulance a dvě omezení pracovišť v Klášterci.',
        'Přehled zahrnuje také dovolenou kožní ambulance MUDr. Voráče v Kadani a Klášterci od 3. do 14. srpna.'
    )
    rss_path.write_text(rss, encoding='utf-8', newline='\n')

assert marker in text
assert '3.–14. 8.</b><span>dovolená kožní ambulance MUDr. Voráče' in text
assert '474 944 246' in text and '731 379 374' in text
assert 'Stav aktualizován 31. července 2026 v 17:52' in text
print('Kožní ambulance MUDr. Voráče byla doplněna do srpnového přehledu.')
