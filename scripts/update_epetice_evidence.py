#!/usr/bin/env python3
from pathlib import Path
import re

path = Path('clanky/epetice-nemocnice-kadan.html')
text = path.read_text(encoding='utf-8')

text = text.replace(
    '<li><a href="#limit">Jak funguje limit 3500 znaků</a></li>',
    '<li><a href="#plne-zneni">Co obsahuje celé znění petice</a></li><li><a href="#limit">Jak funguje limit 3500 znaků</a></li>',
    1,
)

section = '''
  <h2 id="plne-zneni">Celé znění listinné petice obsahuje osm konkrétních požadavků</h2>
  <p>Nově zveřejněné snímky zachycují celé znění listinné petice. Nejde pouze o obecný požadavek, aby Nemocnice Kadaň zůstala ve vlastnictví města. Dokument obsahuje osm konkrétních bodů, které mají být adresovány zastupitelstvu, starostovi a radě města.</p>
  <ol>
    <li><strong>Veřejný závazek města</strong>, že Nemocnice Kadaň nebude prodána ani jinak převedena do soukromého vlastnictví.</li>
    <li><strong>Okamžité přijetí konkrétních opatření</strong> vedoucích ke stabilizaci ekonomické situace nemocnice.</li>
    <li><strong>Zachování všech zdravotnických oborů a odborných ambulancí</strong>, které jsou nezbytné pro obyvatele regionu.</li>
    <li><strong>Pravidelné zveřejňování ekonomických výsledků</strong>, přijatých opatření a strategie dalšího rozvoje.</li>
    <li><strong>Nezávislé odborné posouzení současného řízení nemocnice</strong>, jehož výsledky mají být předloženy zastupitelům i veřejnosti.</li>
    <li><strong>Přijetí personálních změn</strong>, pokud se ukáže, že současné řízení nevede ke stabilizaci nebo není schopné zastavit zhoršování.</li>
    <li><strong>Obnovení otevřené komunikace</strong> mezi vedením nemocnice, zaměstnanci, městem a občany.</li>
    <li><strong>Zajištění dostatečných finančních prostředků na kvalitní zdravotní péči</strong>, aby pacienti ani zaměstnanci nenesli důsledky manažerských selhání.</li>
  </ol>
  <p>Celý listinný dokument je tedy podstatně rozsáhlejší než samotný požadavek na zachování městského vlastnictví. Obsahuje také ekonomické, personální, provozní a informační požadavky.</p>

  <div class="status-box"><b>Co dokládají snímky z Portálu občana:</b> Ve formuláři ePetice se zobrazilo upozornění na překročení limitu 3500 znaků už ve chvíli, kdy byly ve viditelné části zadány pouze první tři požadavky. Další snímek dokládá založený nebo rozpracovaný záznam v části „Moje petice“. Sám o sobě ale ještě nepotvrzuje, že byla ePetice veřejně zveřejněna a otevřena k podpisu.</div>

  <p>Pokud chce předkladatelka současně sbírat listinné i elektronické podpisy jako podporu jedné petice, musí být konečné znění obou verzí naprosto stejné. Prakticky to znamená buď zkrátit a znovu použít totožný text na nových listinných arších i v ePetici, nebo pokračovat s původní listinnou verzí a elektronickou variantu evidovat jako samostatný dokument.</p>

  <div class="callout"><strong>Osobní údaje nezveřejňujeme</strong>Na snímcích listinné petice jsou uvedeny bydliště, e-mail a telefon předkladatelky. Redakce je používá pouze jako podklad k ověření dokumentu a na webu je nebude publikovat v nezakryté podobě.</div>
'''

anchor = '  <h2 id="limit">Limit 3500 znaků skutečně platí</h2>'
if 'id="plne-zneni"' not in text:
    if anchor not in text:
        raise SystemExit('Nenalezeno místo pro vložení nové části.')
    text = text.replace(anchor, section + '\n' + anchor, 1)

text = text.replace(
    '"dateModified":"2026-07-26T10:15:00+02:00"',
    '"dateModified":"2026-07-26T14:15:00+02:00"',
    1,
)

source_marker = '<li>Veřejný facebookový příspěvek předkladatelky petice Vlasty Štaubrové o přípravě ePetice, zachycený redakcí 26. 7. 2026.</li>'
source_addition = source_marker + '<li>Fotografie úplného znění listinné petice a snímky rozpracovaného formuláře ePetice zveřejněné předkladatelkou; osobní kontaktní údaje redakce dále nezveřejňuje.</li>'
if 'Fotografie úplného znění listinné petice' not in text and source_marker in text:
    text = text.replace(source_marker, source_addition, 1)

path.write_text(text, encoding='utf-8', newline='\n')
print('Článek o ePetici byl doplněn o celé znění požadavků a vyhodnocení nových snímků.')
