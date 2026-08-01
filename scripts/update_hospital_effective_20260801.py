#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

old_modified = '2026-07-30T18:51:00+02:00'
new_modified = '2026-08-01T03:45:00+02:00'
text = text.replace(old_modified, new_modified)

text = text.replace(
    'Aktuální zpráva · aktualizováno v 18:51',
    'Aktuální zpráva · aktualizováno 1. srpna v 3:45'
)

text = text.replace(
    '<p class="leadtext"><strong>Nemocnice Kadaň bude mít od soboty 1. srpna nové vedení. Valná hromada městské společnosti odvolala z funkce jednatele Martina Krušinu. Novým jednatelem se stane Pavel Marek a do samostatné funkce ředitele bude jmenován Jiří Vlas. Prověřujeme také možné odchodové plnění a informace o svolání mimořádného zastupitelstva.</strong></p>',
    '<p class="leadtext"><strong>Nemocnice Kadaň má od soboty 1. srpna nové vedení. Valná hromada městské společnosti odvolala z funkce jednatele Martina Krušinu a novým jednatelem se stal Pavel Marek. Jiří Vlas má převzít samostatnou funkci ředitele. Prověřujeme také možné odchodové plnění a informace o svolání mimořádného zastupitelstva.</strong></p>'
)

text = text.replace('<h2>Co se mění od 1. srpna</h2>', '<h2>Co platí od 1. srpna</h2>')
text = text.replace('Má nést hlavní odpovědnost za strategii, ekonomiku a transformaci městské společnosti.', 'Nese hlavní odpovědnost za strategii, ekonomiku a transformaci městské společnosti.')
text = text.replace('Město jej nyní z funkce odvolalo.', 'Město jej z funkce odvolalo.')
text = text.replace('od 1. srpna má Krušinu ve funkci jednatele nahradit Pavel Marek', 'od 1. srpna Krušinu ve funkci jednatele nahradil Pavel Marek')
text = text.replace('<li>Změna vedení od 1. srpna</li>', '<li>Pavel Marek je jednatelem od 1. srpna</li>')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 18:51.', 'Poslední ověřená aktualizace 1. srpna 2026 v 3:45.')

marker = 'data-leadership-effective="20260801"'
if marker not in text:
    anchor = '  <div class="update-box" data-extraordinary-request="20260730">'
    if anchor not in text:
        raise SystemExit('Nenalezen bod vložení aktualizace účinnosti vedení')
    box = (
        '  <div class="update-box" data-leadership-effective="20260801"><strong>Aktualizace 1. srpna v 3:45: změna vedení je účinná</strong>'
        '<p>Od 1. srpna je podle oznámení nemocnice novým jednatelem Pavel Marek. Jiří Vlas má převzít samostatnou funkci ředitele. '
        'Město ani nemocnice zatím nezveřejnily smluvní podmínky nového vedení; kontaktní stránka nemocnice ještě uvádí Martina Krušinu jako jednatele '
        'a obchodní rejstřík dosud nezachycuje změnu jednatele. Oficiální pozvánka na mimořádné zastupitelstvo ani výpis rady z 29. července zatím zveřejněny nejsou.</p></div>\n'
    )
    text = text.replace(anchor, box + anchor, 1)

required = [
    marker,
    new_modified,
    'Nemocnice Kadaň má od soboty 1. srpna nové vedení.',
    'Pavel Marek je jednatelem od 1. srpna',
]
for item in required:
    if item not in text:
        raise SystemExit(f'Chybí očekávaný text: {item}')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek upraven k účinnosti změny vedení od 1. srpna 2026.')
