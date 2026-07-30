#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

text = text.replace('2026-07-30T11:51:00+02:00', '2026-07-30T12:04:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 11:51', 'Aktuální zpráva · aktualizováno v 12:04')
text = text.replace('k 30. červenci v 11:51 nebyl', 'k 30. červenci v 12:04 nebyl')
text = text.replace('při kontrole 30. července v 11:51', 'při kontrole 30. července v 12:04')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 11:51.', 'Poslední ověřená aktualizace 30. července 2026 v 12:04.')

old_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 11:51</strong><p>Oficiální zápis zastupitelstva z 25. června potvrzuje dvě odlišná opatření: rada už 11. června navýšila kontokorent nemocnice o 25 milionů korun a zastupitelstvo 25. června schválilo samostatnou neinvestiční dotaci dalších 25 milionů. Pro dotaci hlasovalo 15 zastupitelů, nikdo nebyl proti a 11 se zdrželo. Jiří Kulhánek už tehdy požadoval mimořádné zastupitelstvo a starosta připustil jeho možné svolání. Formální nový termín však stále zveřejněn není.</p></div>'''
new_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 12:04</strong><p>Registr smluv potvrzuje, že mimořádná provozní dotace 25 milionů korun nezůstala pouze u usnesení: smlouva č. 12/2026 byla zveřejněna v červenci. Nemocnice už měla pro rok 2026 uzavřenou také běžnou provozní dotaci 22 milionů korun. Přímé provozní dotace města pro rok 2026 tak podle zveřejněných smluv činí 47 milionů korun. Navýšený kontokorent o dalších 25 milionů je samostatná možnost bankovního financování, nikoli další dotace.</p></div>'''
if old_update not in text:
    raise SystemExit('Nenalezen aktualizační box 11:51')
text = text.replace(old_update, new_update)

anchor = '''  <p>Nejde o jednu a tutéž částku ani o stejný typ podpory. Kontokorent zvyšuje možnost nemocnice čerpat bankovní úvěr, zatímco dotace je přímá podpora z rozpočtu města. Obě rozhodnutí ale dohromady ukazují, že během dvou týdnů město otevřelo nemocnici dva samostatné finanční zdroje po 25 milionech korun.</p>'''
addition = anchor + '''
  <h3>Registr smluv: 47 milionů přímých provozních dotací</h3>
  <p>Registr smluv eviduje běžnou individuální neinvestiční dotaci č. 1/2026 ve výši 22 milionů korun, zveřejněnou v lednu 2026, a mimořádnou individuální neinvestiční dotaci č. 12/2026 ve výši 25 milionů korun, zveřejněnou v červenci. Součet těchto dvou smluv je 47 milionů korun přímé provozní podpory města pro rok 2026.</p>
  <div class="callout"><strong>Dvě zveřejnění neznamenají dvě dotace po 25 milionech</strong><p>Registr zobrazuje smlouvu č. 12/2026 u zveřejnění z 3. a 9. července. Jde o záznamy či verze stejné smlouvy, nikoli o dvě různé mimořádné dotace. Do součtu proto započítáváme 25 milionů pouze jednou.</p></div>'''
if 'Registr smluv: 47 milionů přímých provozních dotací' not in text:
    if anchor not in text:
        raise SystemExit('Nenalezen odstavec k opatřením po 25 milionech')
    text = text.replace(anchor, addition)

source_anchor = '''    <li><a href="https://smlouvy.gov.cz/vyhledavani?party_idnum=25479300" target="_blank" rel="noopener noreferrer">Registr smluv – vyhledávání smluv Nemocnice Kadaň, IČO 25479300</a>, kontrola 30. července 2026.</li>'''
source_repl = '''    <li><a href="https://smlouvy.gov.cz/vyhledavani?party_idnum=25479300" target="_blank" rel="noopener noreferrer">Registr smluv – Nemocnice Kadaň, IČO 25479300</a>, zejména běžná neinvestiční dotace č. 1/2026 ve výši 22 milionů korun a mimořádná neinvestiční dotace č. 12/2026 ve výši 25 milionů korun; kontrola 30. července 2026.</li>'''
text = text.replace(source_anchor, source_repl)

text = text.replace(
    '<li>Dvě samostatná opatření po 25 mil. Kč</li>',
    '<li>47 mil. Kč přímých provozních dotací</li><li>Kontokorent +25 mil. Kč je úvěrový rámec</li>'
)

required = [
    'Registr smluv: 47 milionů přímých provozních dotací',
    'Dvě zveřejnění neznamenají dvě dotace po 25 milionech',
    '2026-07-30T12:04:00+02:00',
    'Přímé provozní dotace města pro rok 2026 tak podle zveřejněných smluv činí 47 milionů korun',
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'Chybí aktualizace: {needle}')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o smluvně zveřejněné provozní dotace 22 + 25 milionů korun.')
