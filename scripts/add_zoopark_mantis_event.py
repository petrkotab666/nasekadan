#!/usr/bin/env python3
from pathlib import Path
import re

path = Path('clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html')
text = path.read_text(encoding='utf-8')

if 'data-zoopark-kudlanky' not in text:
    block = '''
  <section class="nearby regional-highlight" data-zoopark-kudlanky>
    <p class="distance">Chomutov · přibližně 25 minut autem · denně 9:00–18:00</p>
    <h3>Historicky první výstava kudlanek v Česku</h3>
    <p>Zoopark Chomutov od 25. července do 15. srpna 2026 představuje více než <strong>50 druhů živých kudlanek z celého světa</strong>. Návštěvníci uvidí druhy známé mimořádným maskováním, trpělivostí a rychlým útokem. Výstava je podle pořadatele historicky první svého druhu v České republice.</p>
    <p><strong>Místo:</strong> Zoopark Chomutov. <strong>Otevřeno:</strong> denně 9:00–18:00. Výstava je vhodná jako rodinný výlet; před cestou doporučujeme ověřit aktuální vstupné a provoz areálu.</p>
  </section>
'''
    marker = '<section class="nearby"><p class="distance">Jirkov – Červený Hrádek'
    if marker in text:
        text = text.replace(marker, block + marker, 1)
    else:
        marker = '<section class="nearby"><p class="distance">Podbořany'
        text = text.replace(marker, block + marker, 1)

text = text.replace('<div><b>11</b><span>vybraných tipů z okolí</span></div>', '<div><b>12</b><span>vybraných tipů z okolí</span></div>')
text = text.replace('Přidáváme také tipy z Klášterce, Chomutova, Jirkova, Žatce, Vejprt, okolních zámků a Karlových Varů.', 'Přidáváme také tipy z Klášterce, Chomutova včetně výstavy více než 50 druhů kudlanek, Jirkova, Žatce, Vejprt, okolních zámků a Karlových Varů.')
text = re.sub(r'<meta property="article:modified_time" content="[^"]+">', '<meta property="article:modified_time" content="2026-07-28T22:30:00+02:00">', text, count=1)
text = re.sub(r'"dateModified":"[^"]+"', '"dateModified":"2026-07-28T22:30:00+02:00"', text, count=1)
source = '<li><a href="https://zoopark.cz/udalosti/vystava-kudlanek/" target="_blank" rel="noopener noreferrer">Zoopark Chomutov – Výstava kudlanek</a></li>'
if source not in text:
    text = text.replace('<div class="source-list"><h2>Zdroje a kontrola údajů</h2><ul>', '<div class="source-list"><h2>Zdroje a kontrola údajů</h2><ul>\n    ' + source, 1)

path.write_text(text, encoding='utf-8', newline='\n')
print('Výstava kudlanek doplněna.')
