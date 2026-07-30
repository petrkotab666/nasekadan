#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

# Sjednotit čas aktualizace v metadatech, štítku a časových kontrolách.
for old in (
    '2026-07-30T12:15:00+02:00',
    '2026-07-30T13:24:00+02:00',
    '2026-07-30T13:50:00+02:00',
):
    text = text.replace(old, '2026-07-30T14:29:00+02:00')
for old in (
    'Aktuální zpráva · aktualizováno v 12:15',
    'Aktuální zpráva · aktualizováno v 13:24',
    'Aktuální zpráva · aktualizováno v 13:50',
):
    text = text.replace(old, 'Aktuální zpráva · aktualizováno v 14:29')
for old in (
    'k 30. červenci v 12:15 nebyl',
    'k 30. červenci v 13:24 nebyl',
    'k 30. červenci v 13:50 nebyl',
):
    text = text.replace(old, 'k 30. červenci v 14:29 nebyl')
for old in (
    'při kontrole 30. července v 12:15 zveřejněna',
    'při kontrole 30. července v 13:24 zveřejněna',
    'při kontrole 30. července v 13:50 zveřejněna',
):
    text = text.replace(old, 'při kontrole 30. července v 14:29 zveřejněna')
for old in (
    'Poslední ověřená aktualizace 30. července 2026 v 12:15.',
    'Poslední ověřená aktualizace 30. července 2026 v 13:24.',
    'Poslední ověřená aktualizace 30. července 2026 v 13:50.',
):
    text = text.replace(old, 'Poslední ověřená aktualizace 30. července 2026 v 14:29.')

new_box = '<div class="update-box"><strong>Aktualizace 30. července v 14:29</strong><p>Prošli jsme také přílohy Registru smluv, které běžný fulltext nečetl. Červnový dodatek s metadatovou hodnotou 170 milionů nebyl novým úvěrem: pouze prodloužil čerpání dříve sníženého rámce. Červencový dodatek potvrzuje aktuální limit 80 milionů a vyčerpání 55,169 milionu korun. U smluv STAPRO jsme ověřili, že dodatek za 4,722 milionu není další zakázkou navíc, ale snížením původní ceny po vypuštění položky C1. Pevný základ implementace a pětiletého servisu činí 7,376 milionu korun bez DPH. Při nové kontrole město stále nezveřejnilo výpis z rady 29. července ani pozvánku na mimořádné zastupitelstvo a nemocnice svůj článek o změně vedení od 8:59 neupravila.</p></div>'

start = text.find('<div class="update-box"><strong>Aktualizace 30. července v ')
if start < 0:
    raise SystemExit('Nenalezen aktualizační box')
end = text.find('</div>', start)
if end < 0:
    raise SystemExit('Nenalezen konec aktualizačního boxu')
text = text[:start] + new_box + text[end + len('</div>'):]

anchor = '  <h2>Dokumenty ukazují, že změna se připravovala nejméně od června</h2>'
section = '''  <h2>Co odhalily neindexované úvěrové a IT smlouvy</h2>
  <p>Redakce prošla šest příloh Registru smluv, včetně dokumentu bez použitelné textové vrstvy. Stažené soubory jsme ověřili proti SHA-256 otiskům zveřejněným Registrem smluv a nečitelný úvěrový dodatek převedli obrazově několika režimy OCR.</p>
  <div class="fact-grid">
    <div class="fact-card"><span>Investiční úvěr</span><strong>80 mil. Kč</strong><p>Původní úvěr z roku 2021 činil 270 milionů korun. Dodatky jej postupně snížily nejprve na 170 milionů a poté na 80 milionů korun.</p></div>
    <div class="fact-card"><span>Čerpání k 9. červenci</span><strong>55,169 mil. Kč</strong><p>Z limitu 80 milionů bylo podle dodatku č. 4 vyčerpáno 55 168 704,80 Kč. Nevyčerpaný prostor činil přibližně 24,831 milionu korun.</p></div>
    <div class="fact-card"><span>Projekt NIS po dodatku</span><strong>4,722 mil. Kč bez DPH</strong><p>Původní cena projektu byla 8,645 milionu korun bez DPH. Nemocnice využila předem vyhrazené vypuštění položky C1 a dodatkem cenu snížila na 4,721821 milionu.</p></div>
    <div class="fact-card"><span>Pětiletý servis</span><strong>2,654 mil. Kč bez DPH</strong><p>Základní paušál činí 132 695 Kč za čtvrtletí po dobu pěti let. Vývojové práce za 1 530 Kč za hodinu a budoucí indexace jsou nad tento základ.</p></div>
  </div>
  <h3>Úvěrový limit se v červenci nezvyšoval</h3>
  <p>Dodatek č. 3 ze dne 26. června prodloužil možnost čerpání úvěru do 31. srpna 2026. Dodatek č. 4 ze dne 9. července posunul konečný termín až na 31. prosince 2026 a rozšířil investiční účel na rekonstrukce, modernizace, stavební úpravy a infrastrukturu. Z dokumentu nevyplývá zvýšení osmdesátimilionového limitu.</p>
  <p>Dodatek č. 4 současně vypouští tři dřívější povinnosti nemocnice označené jako odstavce 11, 13 a 14 článku X. Bez úplného znění předchozích verzí smlouvy zatím nelze spolehlivě určit jejich obsah ani význam vypuštění.</p>
  <h3>Projekt STAPRO byl zlevněn, nikoli zdražen</h3>
  <p>Hlavní smlouva na modernizaci a interoperabilitu nemocničního informačního systému byla uzavřena 25. června jako projekt financovaný mimo jiné z Národního plánu obnovy. Dodatek podepsaný 30. června potvrzuje, že cena klesla z 8,644821 na 4,721821 milionu korun bez DPH vypuštěním vyhrazené položky C1. Rutinní provoz měl podle nového harmonogramu začít kolem 24. srpna 2026 a servisní podpora následující den.</p>
  <p>Základní pevný závazek po změně činí přibližně <strong>7,376 milionu korun bez DPH</strong>: 4,722 milionu za implementaci a 2,654 milionu za pětiletý servis. Bylo by chybné přičítat dodatek k původní implementační ceně, protože ji nahrazuje a snižuje.</p>
  <div class="callout"><strong>Co tyto smlouvy neprokazují</strong><p>Úvěrové ani IT smlouvy neobsahují rozhodnutí o odchodovém plnění Martina Krušiny. Přinášejí ale přesnější obraz investičního financování, smluvních závazků a projektů, které nové vedení přebírá.</p></div>

'''
if 'Co odhalily neindexované úvěrové a IT smlouvy' not in text:
    if anchor not in text:
        raise SystemExit('Nenalezen bod vložení nové sekce')
    text = text.replace(anchor, section + anchor)

source_anchor = '    <li><a href="https://smlouvy.gov.cz/vyhledavani?party_idnum=25479300" target="_blank" rel="noopener noreferrer">Registr smluv – Nemocnice Kadaň, IČO 25479300</a>, zejména běžná neinvestiční dotace č. 1/2026 ve výši 22 milionů korun a mimořádná neinvestiční dotace č. 12/2026 ve výši 25 milionů korun; kontrola 30. července 2026.</li>\n'
source_add = '''    <li><a href="https://smlouvy.gov.cz/smlouva/38556652" target="_blank" rel="noopener noreferrer">Registr smluv – dodatek č. 3 k úvěrové smlouvě č. 770/21-120</a>, obrazová příloha ověřena podle SHA-256.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38715676" target="_blank" rel="noopener noreferrer">Registr smluv – dodatek č. 4 k úvěrové smlouvě č. 770/21-120</a>, včetně výše aktuálního čerpání.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38532420" target="_blank" rel="noopener noreferrer">Registr smluv – modernizace a interoperabilita NIS se společností STAPRO</a>, smlouva č. 2026-34.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38590016" target="_blank" rel="noopener noreferrer">Registr smluv – dodatek č. 1 k modernizaci NIS</a>, snížení ceny a nový harmonogram.</li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38533088" target="_blank" rel="noopener noreferrer">Registr smluv – pětiletá servisní smlouva STAPRO</a>, smlouva č. 2026-35.</li>
'''
if 'smlouva/38556652' not in text:
    if source_anchor not in text:
        raise SystemExit('Nenalezen bod vložení zdrojů')
    text = text.replace(source_anchor, source_anchor + source_add)

if '<li>Investiční úvěr: limit 80 mil., čerpáno 55,169 mil. Kč</li>' not in text:
    text = text.replace(
        '<li>Rok 2025 skončil ztrátou 46,139 mil. Kč</li>',
        '<li>Rok 2025 skončil ztrátou 46,139 mil. Kč</li><li>Investiční úvěr: limit 80 mil., čerpáno 55,169 mil. Kč</li><li>STAPRO: pevný základ 7,376 mil. Kč bez DPH</li>'
    )

if '55 168 704,80 Kč' not in text:
    raise SystemExit('Chybí výše čerpání úvěru')
if '7,376 milionu korun bez DPH' not in text:
    raise SystemExit('Chybí součet STAPRO')
if '2026-07-30T14:29:00+02:00' not in text:
    raise SystemExit('Čas aktualizace nebyl změněn')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek aktualizován na 14:29 včetně OCR smluv a nové kontroly zdrojů.')
