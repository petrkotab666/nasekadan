#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

text = text.replace('2026-07-30T12:15:00+02:00', '2026-07-30T13:15:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 12:15', 'Aktuální zpráva · aktualizováno v 13:15')
text = text.replace('k 30. červenci v 12:15 nebyl', 'k 30. červenci v 13:15 nebyl')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 12:15.', 'Poslední ověřená aktualizace 30. července 2026 v 13:15.')

old_update = '<div class="update-box"><strong>Aktualizace 30. července v 12:15</strong><p>Kadaň má v tomto volebním období 27 zastupitelů. Zákonná žádost o mimořádné zasedání proto musí mít podpis nejméně devíti členů zastupitelstva. Veřejný požadavek Jiřího Kulhánka ze zasedání 25. června je doložen, ale veřejný dokument s devíti podpisy, datem doručení a navrženým programem jsme zatím nenašli. Město dosud nezveřejnilo ani pozvánku na mimořádné zasedání.</p></div>'
new_update = '<div class="update-box"><strong>Aktualizace 30. července v 13:15</strong><p>Prošli jsme také přílohy Registru smluv, které běžný fulltext nečte, a ověřili jejich SHA-256 proti otevřeným datům registru. Červnový dodatek s metadatovou hodnotou 170 milionů nebyl novým úvěrem: pouze prodloužil čerpání dříve sníženého rámce. Červencový dodatek potvrzuje aktuální limit 80 milionů a vyčerpání 55,169 milionu. U smluv STAPRO jsme ověřili, že dodatek za 4,722 milionu není další zakázkou navíc, ale snížením původní ceny po vypuštění položky C1.</p></div>'
if old_update not in text:
    raise SystemExit('Nenašel se aktuální update-box 12:15')
text = text.replace(old_update, new_update)

anchor = '  <h2>Dokumenty ukazují, že změna se připravovala nejméně od června</h2>'
section = '''  <h2>Co odhalily neindexované a obrazové smlouvy</h2>
  <p>Registr smluv výslovně upozorňuje, že dokumenty bez textové vrstvy nelze prohledávat fulltextem. Redakce proto stáhla otevřená data registru za červen a červenec, vytipovala 110 záznamů Nemocnice Kadaň a šest klíčových příloh převedla do čitelné podoby. U úvěrových dodatků jsme stažené soubory ověřili proti kontrolním otiskům SHA-256 zveřejněným registrem.</p>

  <h3>Úvěr nebyl v červnu navýšen o dalších 170 milionů</h3>
  <div class="timeline">
    <div><b>2. listopadu 2021: původní rámec 270 milionů</b><p>Pozdější bankovní dodatky shodně rekapitulují, že původní investiční úvěr UniCredit Bank činil 270 milionů korun.</p></div>
    <div><b>Dodatek č. 1: snížení na 170 milionů</b><p>Obrazový dodatek č. 3 potvrzuje, že už dodatkem č. 1 byl úvěrový rámec snížen ze 270 na 170 milionů korun.</p></div>
    <div><b>Dodatek č. 2: další snížení na 80 milionů</b><p>Červencový dodatek č. 4 rekapituluje, že dodatkem č. 2 byl rámec dále snížen na 80 milionů korun. Samostatnou veřejnou přílohu dodatku č. 2 dál dohledáváme.</p></div>
    <div><b>26. června 2026: pouze prodloužení čerpání</b><p>Dodatek č. 3 změnil konečný termín čerpání na 31. srpna 2026. Částka 170 milionů uvedená v metadatech registru tedy není nově poskytnutým úvěrem ani navýšením.</p></div>
    <div><b>9. července 2026: vyčerpáno 55,169 milionu</b><p>Dodatek č. 4 uvádí přesné čerpání 55 168 704,80 Kč. Prodloužil možnost čerpat do 31. prosince 2026 a rozšířil uznatelný investiční účel na rekonstrukce, modernizace a infrastrukturu. Úvěrový limit ale nezvýšil.</p></div>
  </div>
  <div class="callout"><strong>Jde o jiný úvěr než červnový kontokorent</strong><p>Investiční úvěr s aktuálním rámcem 80 milionů nelze zaměňovat s navýšením kontokorentního rámce o 25 milionů. Stejně tak jej nelze přičítat k 47 milionům přímých provozních dotací jako další dotaci města.</p></div>
  <p>Dodatek č. 4 zároveň vypustil z dřívější smlouvy tři povinnosti nemocnice označené jako odstavce 11, 13 a 14 článku X. Bez úplného předchozího znění zatím nelze spolehlivě určit, jaké závazky byly odstraněny; jejich obsah proto nebudeme odhadovat.</p>

  <h3>STAPRO: cena implementace byla dodatkem snížena, nikoli navýšena</h3>
  <div class="fact-grid">
    <div class="fact-card"><span>Implementace po dodatku</span><strong>4,722 mil. Kč bez DPH</strong><p>Původní smlouva uváděla cenu 8,645 milionu bez DPH a současně variantu bez vyhrazené položky C1 za 4,722 milionu. Dodatek č. 1 tuto změnu skutečně uplatnil a cenu snížil na 4,722 milionu.</p></div>
    <div class="fact-card"><span>Pětiletý servis</span><strong>2,654 mil. Kč bez DPH</strong><p>Základní čtvrtletní paušál činí 132 695 Kč bez DPH po dobu pěti let. Vývojové práce za 1 530 Kč za hodinu, případná indexace a některé mimořádné náklady jsou nad rámec pevného paušálu.</p></div>
  </div>
  <p>Základní pevný závazek po změně tak činí přibližně <strong>7,376 milionu korun bez DPH</strong>: 4,722 milionu za implementaci a 2,654 milionu za pětiletý servis. Bylo by chybné sčítat původních 8,645 milionu, dodatek 4,722 milionu a servis 2,654 milionu, protože dodatek původní implementační cenu nahrazuje a snižuje.</p>
  <p>Dodatek byl uzavřen pouhých pět dní po hlavní smlouvě. Jako důvod uvádí prodlení při komunikaci s poskytovatelem dotace a Ministerstvem zdravotnictví. Nový harmonogram počítal se spuštěním rutinního provozu a převzetím systému kolem 24. srpna 2026 a se zahájením servisní podpory následující den.</p>
  <div class="callout"><strong>Co dál ověřujeme</strong><p>Budeme hledat původní smlouvu z roku 2021, samostatný dodatek č. 2 a předchozí úplné znění článku X, abychom mohli přesně popsat všechny změny úvěrových podmínek. U projektu STAPRO budeme sledovat předávací a akceptační dokumenty a skutečné faktury.</p></div>

'''
if 'Co odhalily neindexované a obrazové smlouvy' not in text:
    if anchor not in text:
        raise SystemExit('Chybí kotva před časovou osou')
    text = text.replace(anchor, section + anchor)

# Otevřené otázky doplníme bez opakování.
text = text.replace(
    '<li>Jaká přesná usnesení přijala mimořádná rada města 29. července.</li>',
    '<li>Jaká přesná usnesení přijala mimořádná rada města 29. července.</li>\n    <li>Jaké povinnosti z článku X úvěrové smlouvy byly dodatkem č. 4 vypuštěny a co přesně stanovil samostatný dodatek č. 2.</li>'
)

source_anchor = '    <li><a href="https://smlouvy.gov.cz/vyhledavani?party_idnum=25479300" target="_blank" rel="noopener noreferrer">Registr smluv – vyhledávání smluv Nemocnice Kadaň, IČO 25479300</a>, kontrola 30. července 2026.</li>\n'
source_add = '''    <li><a href="https://smlouvy.gov.cz/smlouva/38556652" target="_blank" rel="noopener noreferrer">Registr smluv – dodatek č. 3 k úvěrové smlouvě 770/21-120</a>, obrazová příloha ověřena podle SHA-256.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38715676" target="_blank" rel="noopener noreferrer">Registr smluv – dodatek č. 4 k úvěrové smlouvě 770/21-120</a>, včetně výše aktuálního čerpání.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38532420" target="_blank" rel="noopener noreferrer">Registr smluv – smlouva o modernizaci a interoperabilitě NIS se společností STAPRO</a>.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38590016" target="_blank" rel="noopener noreferrer">Registr smluv – dodatek č. 1 ke smlouvě STAPRO</a>, snížení ceny a nový harmonogram.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38533088" target="_blank" rel="noopener noreferrer">Registr smluv – pětiletá servisní smlouva STAPRO</a>.</li>
'''
if 'smlouva/38556652' not in text:
    if source_anchor not in text:
        raise SystemExit('Chybí kotva zdrojů Registru smluv')
    text = text.replace(source_anchor, source_anchor + source_add)

# Sidebar rychlý přehled.
text = text.replace(
    '<li>Mimořádné zastupitelstvo není zveřejněné</li>',
    '<li>Mimořádné zastupitelstvo není zveřejněné</li><li>Investiční úvěr má rámec 80 mil. Kč</li><li>K 9. červenci čerpáno 55,169 mil. Kč</li><li>STAPRO: pevný základ 7,376 mil. Kč bez DPH</li>'
)

if '55 168 704,80 Kč' not in text or '7,376 milionu korun bez DPH' not in text:
    raise SystemExit('Nová zjištění se nevložila')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o neindexované úvěrové a IT smlouvy.')
