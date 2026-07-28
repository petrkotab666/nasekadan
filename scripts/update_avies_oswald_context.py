#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'clanky' / 'avies-nemocnice-kadan.html'
text = PATH.read_text(encoding='utf-8')

BLOCK = '''
  <div class="callout" data-oswald-avies-context>
    <strong>Majetková a politická vazba, kterou má čtenář znát</strong>
    <p>Společnost AVIES s.r.o. je personálně i majetkově spojena s kadaňským radním PharmDr. Radkem Oswaldem. Podle veřejných rejstříků je jejím jednatelem a vlastní padesátiprocentní podíl; druhou polovinu vlastní PharmDr. Věra Oswaldová, která je rovněž jednatelkou. Samotná tato vazba neprokazuje porušení zákona ani střet zájmů, je však důležitým kontextem při hodnocení transparentnosti dlouhodobých dodávek léčiv městské nemocnici.</p>
  </div>
'''

if 'data-oswald-avies-context' not in text:
    lead = re.search(r'(<p class="leadtext">.*?</p>)', text, flags=re.S)
    if not lead:
        raise SystemExit('V článku AVIES nebyl nalezen úvodní odstavec.')
    text = text[:lead.end()] + BLOCK + text[lead.end():]

sources = '''
<li data-oswald-source><a href="https://www.finmag.cz/obchodni-rejstrik/28733401-avies-s-r-o" rel="noopener" target="_blank">Veřejný obchodní rejstřík: jednatelé a společníci AVIES s.r.o.</a></li>
<li data-oswald-source><a href="https://www.seznamzpravy.cz/clanek/porady-ve-stinu-exsef-nemocnice-kadan-odmita-vracet-miliony-majetek-prevadi-na-manzelku-308451" rel="noopener" target="_blank">Seznam Zprávy: Radek Oswald, Rada města Kadaně a obchodní vztah AVIES s nemocnicí</a></li>
<li data-oswald-source><a href="https://smlouvy.gov.cz/vyhledavani?party_idnum=28733401" rel="noopener" target="_blank">Registr smluv: smlouvy společnosti AVIES s veřejnými subjekty</a></li>
'''
if 'data-oswald-source' not in text:
    source_list = re.search(r'(<div class="source-list".*?<ul>)', text, flags=re.S)
    if source_list:
        text = text[:source_list.end()] + sources + text[source_list.end():]

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Doplněna vazba AVIES – Radek Oswald a zdroje.')
