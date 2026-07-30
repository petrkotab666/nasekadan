#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

# Posun času poslední ověřené redakční aktualizace.
text = text.replace('2026-07-30T10:25:00+02:00', '2026-07-30T11:20:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 10:25', 'Aktuální zpráva · aktualizováno v 11:20')
text = text.replace('k 30. červenci v 10:25 oficiálně svoláno', 'k 30. červenci v 11:20 oficiálně svoláno')
text = text.replace('k 30. červenci v 10:25 nebyl', 'k 30. červenci v 11:20 nebyl')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 10:25.', 'Poslední ověřená aktualizace 30. července 2026 v 11:20.')

old_update = '<div class="update-box"><strong>Aktualizace 30. července v 10:25</strong><p>Ve zveřejněných usneseních rady města z 11. června, 25. června a 15. července jsme nenašli schválení odstupného ani jiné odchodové kompenzace pro Martina Krušinu. Rozhodující výpis z mimořádné rady města konané 29. července ale zatím zveřejněn nebyl. Mimořádné zastupitelstvo také dosud není oficiálně svolané.</p></div>'
new_update = '<div class="update-box"><strong>Aktualizace 30. července v 11:20</strong><p>Rozšířili jsme kontrolu o registr smluv, úřední desku, veřejná vyjádření, soukromou e-petici a dřívější zprávy vedení nemocnice. Konkrétní odstupné Martina Krušiny stále není doloženo. Částka 6,48 milionu korun, která se objevila ve veřejné debatě, není odstupným: Petr Hossner ji uvedl jako vlastní výpočet možné povinnosti jednatele vracet až dvouletou odměnu v hypotetickém insolvenčním řízení. Výpis z mimořádné rady 29. července ani pozvánka na mimořádné zastupitelstvo dosud zveřejněny nejsou.</p></div>'
text = text.replace(old_update, new_update)

insert_anchor = '  <h2>Mimořádné zastupitelstvo zatím není oficiálně svolané</h2>'
section = '''  <h2>Další veřejné stopy: co potvrzují a co nikoli</h2>
  <div class="fact-grid">
    <div class="fact-card"><span>Registr smluv</span><strong>Bez dohledané manažerské smlouvy</strong><p>Ve veřejně vyhledatelných záznamech Nemocnice Kadaň jsme nenašli smlouvu o výkonu funkce, pracovní smlouvu, dohodu o ukončení ani odchodové plnění Martina Krušiny, Pavla Marka nebo Jiřího Vlase. Nepřítomnost v registru sama o sobě nedokazuje, že dokument neexistuje nebo nemusí být zveřejněn.</p></div>
    <div class="fact-card"><span>Úřední deska</span><strong>Bez pozvánky na mimořádné zastupitelstvo</strong><p>Úřední deska zveřejňuje zprávu nemocnice za rok 2025 a další městské materiály, ale při kontrole neobsahovala termín ani program mimořádného zastupitelstva kvůli změně vedení nemocnice.</p></div>
  </div>
  <h3>Částka 6,48 milionu není odstupné</h3>
  <p>Zastupitel a bývalý šéf nemocnice Petr Hossner ve veřejné výzvě ze 14. července tvrdil, že nemocnici může hrozit úpadek. V této souvislosti vypočetl částku až 6,48 milionu korun jako možnou dvouletou odměnu, kterou by podle jeho právního názoru mohl insolvenční soud po jednateli požadovat zpět. Jde o Hossnerovo tvrzení a hypotetický scénář, nikoli o potvrzený insolvenční stav, schválenou platbu ani odstupné vyplácené Krušinovi.</p>
  <h3>Soukromá petice není žádostí třetiny zastupitelů</h3>
  <p>Na soukromém portálu e-petice.cz byla 21. července zveřejněna petice Vlasty Štaubrové za zachování nemocnice ve vlastnictví města. Požaduje stabilizační plán, pravidelné zveřejňování výsledků, nezávislé posouzení řízení a případné personální změny. Při kontrole portál uváděl 11 elektronických podpisů. Tato občanská iniciativa ale není formální žádostí alespoň třetiny členů zastupitelstva o svolání mimořádného zasedání.</p>
  <h3>Veřejná hodnocení výsledků nemocnice se rozcházejí</h3>
  <p>Martin Krušina v květnu 2025 veřejně uváděl, že nemocnice zvyšuje počet pacientů a výkonů, stabilizuje personál a drží se hospodářského plánu. Petr Hossner naopak v roce 2026 tvrdil, že produkce a úhrady klesají a finanční situace je vážná. Jde o protichůdná vyjádření zainteresovaných osob. Účetní ztráta 46,139 milionu korun za rok 2025 je doložená usnesením rady, ale sama nevysvětluje příčiny ztráty ani konkrétní důvod Krušinova odvolání.</p>
  <div class="callout"><strong>Rozhodující dokumenty stále chybějí</strong><p>Pro potvrzení odchodového plnění potřebujeme smlouvu o výkonu funkce, případný pracovní kontrakt či dohodu o ukončení a příslušné schválení. Pro objasnění personální změny je klíčový také dosud nezveřejněný výpis usnesení mimořádné rady města z 29. července.</p></div>

'''
if 'Další veřejné stopy: co potvrzují a co nikoli' not in text:
    text = text.replace(insert_anchor, section + insert_anchor)

# Zpřesnění seznamu otevřených otázek.
text = text.replace(
    '<li>Zda Krušinovi vznikl nárok na odchodové plnění, podle jaké smlouvy a v jaké výši.</li>',
    '<li>Zda Krušinovi vznikl nárok na odchodové plnění, podle jaké smlouvy a v jaké výši; veřejně zmiňovaných 6,48 milionu korun odstupným není.</li>'
)

source_anchor = '    <li><a href="https://www.mesto-kadan.cz/cs/mesto/zastupitelstvo-mesta/terminy-zasedani-zastupitelstva.html" target="_blank" rel="noopener noreferrer">Město Kadaň – termíny zasedání zastupitelstva</a>.</li>\n'
source_add = '''    <li><a href="https://smlouvy.gov.cz/vyhledavani?party_idnum=25479300" target="_blank" rel="noopener noreferrer">Registr smluv – vyhledávání smluv Nemocnice Kadaň, IČO 25479300</a>, kontrola 30. července 2026.</li>
    <li><a href="https://petrhossnerkadan.cz/aktuality/upozorneni-na-povinnosti-jednatele-nemocnice-kadan-a-vyzva-k-prevenci-dalsich-skod/" target="_blank" rel="noopener noreferrer">Petr Hossner – veřejná výzva jednateli ze 14. července 2026</a>; jde o stanovisko zastupitele a bývalého vedení, nikoli úřední závěr.</li>
    <li><a href="https://e-petice.cz/es/petitions/?display=1&amp;filt1=1&amp;filt2=5" target="_blank" rel="noopener noreferrer">e-petice.cz – Petice za zachování Nemocnice Kadaň ve vlastnictví města</a>, zveřejněná 21. července 2026 na soukromém portálu.</li>
    <li><a href="https://www.nemkadan.cz/pro-verejnost/verejnost/aktuality/zprava-jednatele-nemocnice-kadan-sro-mgr-martina-krusiny-mba-682cs.html" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – veřejná zpráva Martina Krušiny z 7. května 2025</a>.</li>
'''
if 'petrhossnerkadan.cz/aktuality/upozorneni-na-povinnosti' not in text:
    text = text.replace(source_anchor, source_add + source_anchor)

if 'Aktualizace 30. července v 11:20' not in text:
    raise SystemExit('Nová aktualizace se nevložila')
if 'Částka 6,48 milionu není odstupné' not in text:
    raise SystemExit('Chybí korekce částky 6,48 milionu')
if '2026-07-30T11:20:00+02:00' not in text:
    raise SystemExit('Čas aktualizace se nezměnil')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o registr smluv, veřejná stanoviska, petici a korekci částky 6,48 mil. Kč.')
