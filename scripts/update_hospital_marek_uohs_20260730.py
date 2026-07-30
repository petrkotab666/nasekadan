#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

text = text.replace('2026-07-30T12:04:00+02:00', '2026-07-30T12:09:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 12:04', 'Aktuální zpráva · aktualizováno v 12:09')
text = text.replace('k 30. červenci v 12:04 nebyl', 'k 30. červenci v 12:09 nebyl')
text = text.replace('při kontrole 30. července v 12:04', 'při kontrole 30. července v 12:09')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 12:04.', 'Poslední ověřená aktualizace 30. července 2026 v 12:09.')

old_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 12:04</strong><p>Registr smluv potvrzuje, že mimořádná provozní dotace 25 milionů korun nezůstala pouze u usnesení: smlouva č. 12/2026 byla zveřejněna v červenci. Nemocnice už měla pro rok 2026 uzavřenou také běžnou provozní dotaci 22 milionů korun. Přímé provozní dotace města pro rok 2026 tak podle zveřejněných smluv činí 47 milionů korun. Navýšený kontokorent o dalších 25 milionů je samostatná možnost bankovního financování, nikoli další dotace.</p></div>'''
new_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 12:09</strong><p>Prověřili jsme profesní minulost Pavla Marka a letošní řízení ÚOHS k zakázce na nemocniční lůžka. Marek byl v roce 2017 v České Lípě vybrán hodnoticí komisí a po devíti letech odešel na konci roku 2025 podle oficiálních zdrojů z vlastní iniciativy v souvislosti s fúzí nemocnic. Veřejný doklad o výběrovém řízení pro jeho novou funkci v Kadani jsme nenašli. V případě zakázky na lůžka ÚOHS návrh vyloučeného dodavatele zamítl a nenašel důvod k nápravnému opatření.</p></div>'''
if old_update not in text:
    raise SystemExit('Nenalezen aktualizační box 12:04')
text = text.replace(old_update, new_update)

anchor = '''  <h2>Mimořádné zastupitelstvo zatím není oficiálně svolané</h2>'''
section = '''  <h2>Další prověřené okolnosti změny vedení</h2>
  <h3>Pavel Marek odešel z České Lípy dobrovolně při fúzi</h3>
  <p>Pavel Marek vedl českolipskou nemocnici od roku 2017. Do funkce generálního ředitele jej tehdy doporučila hodnoticí komise, která podle dobového zpravodajství vybírala ze dvou kandidátů. K 31. prosinci 2025 Marek z vedení odešel. Nemocnice i Liberecký kraj uvedly, že šlo o jeho vlastní iniciativu a osobní rozhodnutí v době slučování českolipské nemocnice s Krajskou nemocnicí Liberec.</p>
  <p>Marek nadále veřejně figuruje jako člen představenstva MMN, a.s., provozující nemocnice v Jilemnici a Semilech. Kadaňská rada mu při vstupu do dozorčí rady výslovně povolila souběh této funkce. Veřejný dokument, který by popisoval výběrové řízení na nového jednatele Nemocnice Kadaň, počet kandidátů nebo hodnoticí kritéria, jsme zatím nenašli.</p>
  <div class="callout"><strong>Politická kritika existuje, úředním závěrem ale není</strong><p>Liberečtí Zelení v červnu 2025 veřejně kritizovali personální situaci českolipské interny, Markovo řízení i jeho vztah k hejtmanovi. Jde o politické stanovisko. Oficiální zdroje naopak při jeho odchodu uváděly dobrovolné rozhodnutí a poděkování za odvedenou práci. Bez dalších podkladů nelze kritiku vydávat za prokázaný důvod jeho odchodu.</p></div>
  <h3>ÚOHS neshledal důvod zasáhnout do zakázky na lůžka</h3>
  <p>Dodavatel PROMA REHA napadl své vyloučení z otevřeného řízení na dodávku nemocničních lůžek. ÚOHS během přezkumu dočasně zakázal uzavřít smlouvu, konečným rozhodnutím z 20. dubna 2026 však návrh zamítl, protože neshledal důvody pro uložení nápravného opatření. Rozhodnutí nabylo právní moci 8. května. Samotná existence řízení proto není důkazem nezákonného postupu nemocnice.</p>

'''
if 'Další prověřené okolnosti změny vedení' not in text:
    if anchor not in text:
        raise SystemExit('Nenalezen nadpis mimořádného zastupitelstva')
    text = text.replace(anchor, section + anchor)

source_anchor = '''    <li><a href="https://www.nemkadan.cz/pro-verejnost/verejnost/aktuality/novym-jednatelem-nemocnice-kadan-sro-se-stal-mgr-martin-krusina-mba-564cs.html" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – jmenování Martina Krušiny v září 2024</a>.</li>'''
source_add = '''    <li><a href="https://www.nemcl.cz/nemocnice/novinky/2017-10-04-novy-generalni-reditel-nemocnice" target="_blank" rel="noopener noreferrer">Nemocnice Česká Lípa – jmenování Pavla Marka generálním ředitelem po doporučení hodnoticí komise v roce 2017</a>.</li>
    <li><a href="https://www.nemcl.cz/nemocnice/marketing/nemocnice-s-poliklinikou-ceska-lipa-a-s-se-k-1-lednu-2026-slouci-s-krajskou-nemocnici-liberec" target="_blank" rel="noopener noreferrer">Nemocnice Česká Lípa – fúze a dobrovolný odchod Pavla Marka k 31. prosinci 2025</a>.</li>
    <li><a href="https://www.nemocnicelk.cz/otazky-a-odpovedi/" target="_blank" rel="noopener noreferrer">Nemocnice Libereckého kraje – odpověď k odchodu části českolipského managementu</a>.</li>
    <li><a href="https://liberecko.zeleni.cz/nemocnice-si-nezaslouzi-aby-o-ni-rozhodoval-jediny-clovek/" target="_blank" rel="noopener noreferrer">Strana zelených Liberecký kraj – kritické politické stanovisko k Pavlu Markovi z 5. června 2025</a>.</li>
    <li><a href="https://uohs.gov.cz/cs/verejne-zakazky/sbirky-rozhodnuti/detail-23982.html" target="_blank" rel="noopener noreferrer">ÚOHS – rozhodnutí S0098/2026/VZ k dodávce lůžek Nemocnici Kadaň</a>.</li>
'''
if 'uohs.gov.cz/cs/verejne-zakazky/sbirky-rozhodnuti/detail-23982.html' not in text:
    text = text.replace(source_anchor, source_add + source_anchor)

text = text.replace(
    '<li>Zda a jak proběhlo výběrové řízení na jednatele a ředitele.</li>',
    '<li>Zda a jak proběhlo výběrové řízení na jednatele a ředitele; veřejný doklad o výběrovém procesu jsme zatím nenašli.</li>'
)

required = [
    'Další prověřené okolnosti změny vedení',
    'Pavel Marek odešel z České Lípy dobrovolně při fúzi',
    'ÚOHS neshledal důvod zasáhnout do zakázky na lůžka',
    '2026-07-30T12:09:00+02:00',
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'Chybí aktualizace: {needle}')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o profesní profil Pavla Marka a výsledek řízení ÚOHS.')
