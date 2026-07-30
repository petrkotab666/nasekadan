#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

text = text.replace('2026-07-30T10:05:00+02:00', '2026-07-30T10:25:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 10:05', 'Aktuální zpráva · aktualizováno v 10:25')
text = text.replace('k 30. červenci v 10:05 oficiálně svoláno', 'k 30. červenci v 10:25 oficiálně svoláno')
text = text.replace('kontrola 30. července 2026 v 10:05', 'kontrola 30. července 2026 v 10:25')
text = text.replace('K 10:05 nebylo možné', 'K 10:25 nebylo možné')

css_anchor = '    .verified-box{background:#f2f7f5;border:1px solid #bad3c7;border-radius:18px;padding:23px 25px;margin:28px 0}.verified-box strong{font:800 23px Georgia,serif;display:block;color:#245b43;margin-bottom:7px}\n'
css_add = "    .timeline{border-left:4px solid #d7dde0;margin:28px 0;padding-left:24px}.timeline div{position:relative;padding:0 0 24px}.timeline div:before{content:'';position:absolute;left:-33px;top:7px;width:14px;height:14px;border-radius:50%;background:var(--red);border:4px solid #f7f8f8}.timeline b{display:block;font:800 21px Georgia,serif}.timeline p{margin:5px 0}\n"
if '.timeline{' not in text:
    text = text.replace(css_anchor, css_anchor + css_add)

old_update = '<div class="update-box"><strong>Článek průběžně doplňujeme</strong><p>Žádáme město, nemocnici i odcházejícího jednatele o potvrzení, zda mu náleží jakékoli odstupné nebo jiné odchodové plnění, v jaké výši a podle jakého smluvního ustanovení. Zjišťujeme také, zda už byla městu doručena žádost zastupitelů o mimořádné zasedání.</p></div>'
new_update = '<div class="update-box"><strong>Aktualizace 30. července v 10:25</strong><p>Ve zveřejněných usneseních rady města z 11. června, 25. června a 15. července jsme nenašli schválení odstupného ani jiné odchodové kompenzace pro Martina Krušinu. Rozhodující výpis z mimořádné rady města konané 29. července ale zatím zveřejněn nebyl. Mimořádné zastupitelstvo také dosud není oficiálně svolané.</p></div>'
text = text.replace(old_update, new_update)

insert_anchor = '  <h2>Mimořádné zastupitelstvo zatím není oficiálně svolané</h2>'
section = '''  <h2>Dokumenty ukazují, že změna se připravovala nejméně od června</h2>
  <div class="timeline">
    <div><b>11. června: Pavel Marek vstoupil do dozorčí rady</b><p>Rada města jej zvolila členem dozorčí rady s účinností od 12. června a výslovně povolila jeho souběžné působení v představenstvu společnosti MMN.</p></div>
    <div><b>11. června: zadání transformačních variant</b><p>Jednatel nemocnice měl ve spolupráci s předsedou dozorčí rady připravit varianty ekonomického, provozního a zdravotnického směřování nemocnice, včetně omezení nároků na rozpočet města a možné spolupráce s Ústeckým krajem.</p></div>
    <div><b>25. června: ztráta 46,139 milionu korun</b><p>Rada jako valná hromada schválila účetní závěrku za rok 2025 se ztrátou 46,139 milionu korun. Současně schválila smlouvu o výkonu funkce předsedy dozorčí rady s úpravou článku 4; veřejný výpis však obsah tohoto článku ani výši odměny neuvádí.</p></div>
    <div><b>15. července: termín zkrácen na 4. září</b><p>Město požadovalo dopracování financování do konce roku 2026 a výhledu na rok 2027, podklady pro spolupráci s krajem a posouzení přeměny nemocnice na akciovou společnost. Termín transformačních podkladů posunulo z 30. září na 4. září.</p></div>
    <div><b>29. července: mimořádná rada města</b><p>Její svolání bylo schváleno už 15. července. Právě po této schůzi nemocnice oznámila změnu vedení, výpis usnesení ale k 30. červenci v 10:25 nebyl na webu města zveřejněn.</p></div>
  </div>

'''
if 'Dokumenty ukazují, že změna se připravovala' not in text:
    text = text.replace(insert_anchor, section + insert_anchor)

text = text.replace(
    'V obchodním rejstříku byl 21. července 2026 zapsán jako člen dozorčí rady Nemocnice Kadaň. Aktuální oznámení nemocnice jej označuje za dosavadního předsedu dozorčí rady. Nyní přechází do výkonné funkce jednatele.',
    'Rada města jej zvolila členem dozorčí rady už 11. června 2026 s účinností od následujícího dne. Aktuální oznámení nemocnice jej označuje za dosavadního předsedu dozorčí rady. Z kontrolní pozice nyní přechází do výkonné funkce jednatele.'
)

text = text.replace(
    '<li>Zda Martin Krušina obdrží odstupné nebo jiné odchodové plnění, v jaké výši a podle jaké smlouvy.</li>',
    '<li>Zda Martin Krušina obdrží odstupné nebo jiné odchodové plnění, v jaké výši a podle jaké smlouvy.</li>\n    <li>Jaká přesná usnesení přijala mimořádná rada města 29. července.</li>'
)

source_anchor = '    <li><a href="https://www.mesto-kadan.cz/cs/mesto/zastupitelstvo-mesta/terminy-zasedani-zastupitelstva.html" target="_blank" rel="noopener noreferrer">Město Kadaň – termíny zasedání zastupitelstva</a>, kontrola 30. července 2026.</li>\n'
source_add = '''    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5076063.pdf" target="_blank" rel="noopener noreferrer">Město Kadaň – výpis usnesení 37. rady města ze dne 11. června 2026</a>, zejména usnesení 371 až 377.</li>
    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5090957.pdf" target="_blank" rel="noopener noreferrer">Město Kadaň – výpis usnesení mimořádné rady města ze dne 25. června 2026</a>, zejména usnesení 510 až 515.</li>
    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5105200.pdf" target="_blank" rel="noopener noreferrer">Město Kadaň – výpis usnesení mimořádné rady města ze dne 15. července 2026</a>, zejména usnesení 559 až 561.</li>
'''
if 'filemanager/files/5076063.pdf' not in text:
    text = text.replace(source_anchor, source_add + source_anchor)

text = text.replace(
    'Aktualizováno v 10:05 o prověření odstupného a stavu možného mimořádného zastupitelstva. Text doplníme po obdržení vyjádření.',
    'Aktualizováno v 10:25 o časovou osu rozhodnutí rady města, hospodářskou ztrátu za rok 2025 a dosud nezveřejněný výpis z mimořádné rady 29. července. Text doplníme po obdržení vyjádření.'
)
text = text.replace(
    '<li>Výše odstupného není doložena</li><li>Mimořádné zastupitelstvo není oficiálně svoláno</li>',
    '<li>Výše odstupného není doložena</li><li>Ztráta za rok 2025 činila 46,139 mil. Kč</li><li>Výpis z rady 29. července zatím chybí</li><li>Mimořádné zastupitelstvo není oficiálně svoláno</li>'
)
text = text.replace(
    'Právní titul a výši případného odchodového plnění, existenci žádosti zastupitelů, důvod odvolání a smluvní podmínky nového vedení.',
    'Výpis z mimořádné rady 29. července, právní titul a výši případného odchodového plnění, existenci žádosti zastupitelů, důvod odvolání a smluvní podmínky nového vedení.'
)

if '46,139 milionu korun' not in text:
    raise SystemExit('Aktualizace se nevložila')
if '2026-07-30T10:25:00+02:00' not in text:
    raise SystemExit('Čas aktualizace se nezměnil')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o časovou osu a veřejné dokumenty.')
