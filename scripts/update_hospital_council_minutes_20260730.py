#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

text = text.replace('2026-07-30T11:29:00+02:00', '2026-07-30T11:51:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 11:29', 'Aktuální zpráva · aktualizováno v 11:51')
text = text.replace('k 30. červenci v 11:29 nebyl', 'k 30. červenci v 11:51 nebyl')
text = text.replace('při kontrole 30. července v 11:29', 'při kontrole 30. července v 11:51')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 11:29.', 'Poslední ověřená aktualizace 30. července 2026 v 11:51.')

old_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 11:29</strong><p>Prověřili jsme také kompletní výroční zprávu a audit za rok 2025. Konkrétní odstupné Martina Krušiny stále není doloženo a veřejně zmiňovaných 6,48 milionu korun odstupným není. Nemocnice měla na konci roku jen 12 milionů korun peněžních prostředků oproti 109,7 milionu o rok dříve, výroční zpráva však uvádí dodavatelské závazky celé ve lhůtě splatnosti. Výpis z mimořádné rady 29. července ani pozvánka na mimořádné zastupitelstvo dosud zveřejněny nejsou.</p></div>'''
new_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 11:51</strong><p>Oficiální zápis zastupitelstva z 25. června potvrzuje dvě odlišná opatření: rada už 11. června navýšila kontokorent nemocnice o 25 milionů korun a zastupitelstvo 25. června schválilo samostatnou neinvestiční dotaci dalších 25 milionů. Pro dotaci hlasovalo 15 zastupitelů, nikdo nebyl proti a 11 se zdrželo. Jiří Kulhánek už tehdy požadoval mimořádné zastupitelstvo a starosta připustil jeho možné svolání. Formální nový termín však stále zveřejněn není.</p></div>'''
if old_update not in text:
    raise SystemExit('Nenalezen původní aktualizační box')
text = text.replace(old_update, new_update)

anchor = '  <h2>Dokumenty ukazují, že změna se připravovala nejméně od června</h2>'
section = '''  <h2>Dvě různá opatření po 25 milionech korun</h2>
  <div class="fact-grid">
    <div class="fact-card"><span>11. června · rada města</span><strong>Kontokorent +25 mil. Kč</strong><p>Rada v působnosti valné hromady schválila navýšení kontokorentního úvěru u UniCredit Bank o 25 milionů korun. Současně umožnila použít nevyčerpané prostředky jiného úvěru také na provoz.</p></div>
    <div class="fact-card"><span>25. června · zastupitelstvo</span><strong>Dotace +25 mil. Kč</strong><p>Zastupitelstvo schválilo samostatnou individuální neinvestiční dotaci na stabilní provoz nemocnice a zachování dostupnosti péče. Hlasování skončilo 15 pro, nikdo proti a 11 zastupitelů se zdrželo.</p></div>
  </div>
  <p>Nejde o jednu a tutéž částku ani o stejný typ podpory. Kontokorent zvyšuje možnost nemocnice čerpat bankovní úvěr, zatímco dotace je přímá podpora z rozpočtu města. Obě rozhodnutí ale dohromady ukazují, že během dvou týdnů město otevřelo nemocnici dva samostatné finanční zdroje po 25 milionech korun.</p>
  <div class="callout"><strong>Starosta oznámil přísnější kontrolu</strong><p>V zápisu uvedl, že dozorčí rada má dostávat měsíční reporting cash-flow, závazků, pohledávek, úhrad pojišťoven, dotací a personálních nákladů. Valná hromada se měla během léta scházet flexibilně; první další jednání bylo plánováno na 15. července.</p></div>

'''
if 'Dvě různá opatření po 25 milionech korun' not in text:
    text = text.replace(anchor, section + anchor)

old_timeline = '''    <div><b>11. června: zadání transformačních variant</b><p>Jednatel nemocnice měl ve spolupráci s předsedou dozorčí rady připravit varianty ekonomického, provozního a zdravotnického směřování nemocnice, včetně omezení nároků na rozpočet města a možné spolupráce s Ústeckým krajem.</p></div>
    <div><b>25. června: ztráta 46,139 milionu korun</b>'''
new_timeline = '''    <div><b>11. června: zadání transformačních variant</b><p>Jednatel nemocnice měl ve spolupráci s předsedou dozorčí rady připravit varianty ekonomického, provozního a zdravotnického směřování nemocnice, včetně omezení nároků na rozpočet města a možné spolupráce s Ústeckým krajem.</p></div>
    <div><b>25. června: zastupitelstvo schválilo provozní dotaci</b><p>Samostatnou neinvestiční dotaci 25 milionů korun podpořilo 15 zastupitelů, nikdo nebyl proti a 11 se zdrželo. Starosta zároveň oznámil ztrátu 17 milionů korun už za první čtvrtletí roku 2026.</p></div>
    <div><b>25. června: veřejně zazněl požadavek na změnu vedení</b><p>Petr Hossner během diskuse vyzval k odvolání jednatele a jmenování jiného. Jiří Kulhánek požadoval mimořádné zasedání zastupitelstva a upozornil, že schválených 25 milionů nemusí být konečná částka.</p></div>
    <div><b>25. června: ztráta 46,139 milionu korun</b>'''
if '25. června: zastupitelstvo schválilo provozní dotaci' not in text:
    text = text.replace(old_timeline, new_timeline)

extra_anchor = '''  <h2>Mimořádné zastupitelstvo zatím není oficiálně svolané</h2>
  <p>Oficiální stránka města uvádí jako další plánované jednání zastupitelstva 24. září 2026.'''
extra_repl = '''  <h2>Mimořádné zastupitelstvo zatím není oficiálně svolané</h2>
  <h3>Požadavek zazněl už 25. června</h3>
  <p>Oficiální zápis zachycuje, že PaedDr. Jiří Kulhánek během červnového jednání řekl, že by mělo být svoláno mimořádné zasedání zastupitelstva. Starosta následně připustil, že mimořádné zastupitelstvo může být svoláno, protože existuje mnoho proměnných a město bude muset jednat operativně. Šlo však o veřejnou diskusi, nikoli o doložené doručení formální žádosti alespoň třetiny zastupitelů.</p>
  <p>Oficiální stránka města uvádí jako další plánované jednání zastupitelstva 24. září 2026.'''
if 'Požadavek zazněl už 25. června' not in text:
    text = text.replace(extra_anchor, extra_repl)

marek_old = '''  <p>Rada města jej zvolila členem dozorčí rady už 11. června 2026 s účinností od následujícího dne. Aktuální oznámení nemocnice jej označuje za dosavadního předsedu dozorčí rady. Z kontrolní pozice nyní přechází do výkonné funkce jednatele.</p>'''
marek_new = '''  <p>Rada města jej zvolila členem dozorčí rady už 11. června 2026 s účinností od následujícího dne. Aktuální oznámení nemocnice jej označuje za dosavadního předsedu dozorčí rady. Starosta na zastupitelstvu uvedl, že odměna předsedy dozorčí rady byla schválena ve výši 20 tisíc korun měsíčně. Tento údaj se týká kontrolní funkce, nikoli dosud nezveřejněné odměny nového jednatele. Z kontrolní pozice nyní Marek přechází do výkonné funkce.</p>'''
text = text.replace(marek_old, marek_new)

source_anchor = '''    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5076063.pdf" target="_blank" rel="noopener noreferrer">Město Kadaň – výpis usnesení 37. rady města ze dne 11. června 2026</a>, zejména usnesení 371 až 377.</li>'''
source_add = '''    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5095122.pdf" target="_blank" rel="noopener noreferrer">Město Kadaň – úplný zápis 17. zasedání zastupitelstva ze dne 25. června 2026</a>, zejména bod 9 a usnesení 67/2026.</li>
'''
if 'filemanager/files/5095122.pdf' not in text:
    text = text.replace(source_anchor, source_anchor + '\n' + source_add.rstrip())

text = text.replace(
    '<li>Mimořádné zastupitelstvo není zveřejněné</li>',
    '<li>Dvě samostatná opatření po 25 mil. Kč</li><li>Požadavek na mimořádné ZM zazněl 25. června</li><li>Mimořádné zastupitelstvo není zveřejněné</li>'
)

required = [
    'Dvě různá opatření po 25 milionech korun',
    'Hlasování skončilo 15 pro',
    'Požadavek zazněl už 25. června',
    'odměna předsedy dozorčí rady byla schválena ve výši 20 tisíc korun měsíčně',
    '2026-07-30T11:51:00+02:00',
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'Chybí očekávaná aktualizace: {needle}')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o úplný zápis zastupitelstva a dvě opatření po 25 milionech.')
