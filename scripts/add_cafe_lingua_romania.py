#!/usr/bin/env python3
from pathlib import Path

path = Path('clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html')
text = path.read_text(encoding='utf-8')

block = '''  <section class="event" data-cafe-lingua-romania>
    <time datetime="2026-07-30T17:00:00+02:00">ČTVRTEK 30. ČERVENCE · 17:00</time>
    <h3>Café Lingua Romania v RADCE</h3>
    <p>Mezinárodní dobrovolnice Georgiana představí rumunskou kulturu, krajinu, legendy i některá typická jídla. Setkání nabídne neformální poznávání Rumunska prostřednictvím vyprávění, fotografií a ochutnávky.</p>
    <p><strong>Místo:</strong> RADKA, kpt. Jaroše 630, Kadaň. <strong>Pořadatel:</strong> RADKA – Rodiče a děti Kadaně.</p>
  </section>
'''

if 'data-cafe-lingua-romania' not in text:
    marker = '  <h2 id="kadan">1. Co se děje přímo v Kadani</h2>\n'
    if marker not in text:
        raise SystemExit('Nenalezena sekce akcí přímo v Kadani.')
    text = text.replace(marker, marker + block, 1)

internal = '  <div class="fact"><h3>Nově kontrolujeme jednotlivě všechny kadaňské školy a školky</h3><p>Při večerní aktualizaci jsme rozšířili monitoring o weby všech místních mateřských a základních škol, ZUŠ, Gymnázia Kadaň, SPŠS a OA, školy při nemocnici i soukromého zařízení ZAČÍT SPOLU. Pro tento týden jsme na nich nepotvrdili další jednorázovou akci otevřenou široké veřejnosti. MŠ Hvězdička současně upozorňuje na přerušení provozu od 27. července do 21. srpna; rodiče by měli sledovat provozní oznámení své konkrétní školky.</p></div>\n'
text = text.replace(internal, '')

text = text.replace('Živá hudba na Liďáku, festival čaje, osm projekcí Kina Hvězda, koupaliště, historický vlak a galakoncert s Karlovarským symfonickým orchestrem.', 'Café Lingua Romania v RADCE, živá hudba na Liďáku, festival čaje, osm projekcí Kina Hvězda, koupaliště, historický vlak a galakoncert s Karlovarským symfonickým orchestrem.')
text = text.replace('Nadcházející týden nabídne v Kadani páteční živou hudbu na Liďáku, sobotní festival čaje, osm filmových projekcí, letní výstavy, otevřené památky a dvě možnosti koupání.', 'Nadcházející týden nabídne v Kadani čtvrteční Café Lingua Romania v RADCE, páteční živou hudbu na Liďáku, sobotní festival čaje, osm filmových projekcí, letní výstavy, otevřené památky a dvě možnosti koupání.')
text = text.replace('Nejsilnějšími tipy jsou páteční hudební večer na Liďáku, sobotní festival čaje v Kadani, historický motorák do Krušných hor a čtvrteční gala s Karlovarským symfonickým orchestrem.', 'Mezi hlavní tipy patří čtvrteční Café Lingua Romania v RADCE, páteční hudební večer na Liďáku, sobotní festival čaje, historický motorák do Krušných hor a gala s Karlovarským symfonickým orchestrem.')
text = text.replace('2026-07-28T11:30:00+02:00', '2026-07-28T13:15:00+02:00')

path.write_text(text, encoding='utf-8', newline='\n')
print('Doplněno Café Lingua Romania a odstraněn interní odstavec o monitoringu škol.')
