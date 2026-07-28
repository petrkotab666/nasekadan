#!/usr/bin/env python3
from pathlib import Path
import re

path = Path('clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html')
text = path.read_text(encoding='utf-8')

folk = '''  <section class="nearby regional-highlight" data-folk-rock-loucna><p class="distance">Loučná pod Klínovcem · přibližně 35 minut autem · pátek 31. července a sobota 1. srpna</p><h3>Folk Rock Festival na Horách</h3><p>Na plácku u hraničního přechodu se uskuteční šestý ročník česko-německého hudebního festivalu. Vystoupí celkem 11 kapel různých žánrů. Páteční program začíná v 17:30, sobotní ve 14:00.</p><p><strong>Vstupné:</strong> 150 Kč na jeden den nebo 250 Kč na oba dny. Děti do 15 let a držitelé ZTP mají vstup zdarma. Na místě má být zajištěné občerstvení. <strong>Pořadatel:</strong> Město Loučná pod Klínovcem.</p></section>'''

honey = '''  <section class="nearby regional-highlight" data-chvala-medu-horni-hrad><p class="distance">Horní hrad (Hauenštejn) · přibližně 45 minut autem · sobota 1. srpna</p><h3>Chvála medu na Horním hradě</h3><p>Horní hrad pořádá XXII. ročník tradiční akce věnované včelařství, medu a řemeslům. Odborný program začíná v 10:00 tématem současných problémů včelařství a pokračuje informacemi o předpisech pro včelaře. Součástí bývá také doprovodný program pro veřejnost a hradní občerstvení.</p><p><strong>Místo:</strong> Horní hrad u Stráže nad Ohří. <strong>Termín:</strong> sobota 1. srpna 2026. Přesnou provozní dobu a vstupné doporučujeme před cestou zkontrolovat přímo u pořadatele.</p></section>'''

if 'data-folk-rock-loucna' not in text:
    marker = '<section class="nearby regional-highlight"><p class="distance">Karlovy Vary'
    text = text.replace(marker, folk + '\n' + marker, 1)

if 'data-chvala-medu-horni-hrad' not in text:
    marker = '<section class="nearby regional-highlight"><p class="distance">Karlovy Vary'
    text = text.replace(marker, honey + '\n' + marker, 1)

if 'Město Loučná pod Klínovcem – Folk Rock Festival na Horách' not in text:
    marker = '<li><a href="https://www.koupalistekadan.cz/'
    source = '<li><a href="https://www.loucna.eu/obcan/akce-mesta/folk-rock-festival-na-horach-810_95cs.html" target="_blank" rel="noopener noreferrer">Město Loučná pod Klínovcem – Folk Rock Festival na Horách</a></li>\n    '
    text = text.replace(marker, source + marker, 1)

if 'Horní hrad – Chvála medu' not in text:
    marker = '<li><a href="https://www.koupalistekadan.cz/'
    source = '<li><a href="https://hornihrad.cz/chvala-medu-1-8-2026-termin-kazdorocni-skvele-akce-se-uz-blizi/" target="_blank" rel="noopener noreferrer">Horní hrad – Chvála medu</a></li>\n    '
    text = text.replace(marker, source + marker, 1)

text = re.sub(r'<meta property="article:modified_time" content="[^"]+">', '<meta property="article:modified_time" content="2026-07-28T14:30:00+02:00">', text, count=1)
text = re.sub(r'"dateModified":"[^"]+"', '"dateModified":"2026-07-28T14:30:00+02:00"', text, count=1)
path.write_text(text, encoding='utf-8', newline='\n')
print('Doplněn Folk Rock Festival a Chvála medu.')
