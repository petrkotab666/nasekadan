#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-3-9-srpna-2026.html"
EVENT_ID = "klasterec-minifestacek-lodenice-20260808"
BLOCK = '''  <div class="event" data-event-id="klasterec-minifestacek-lodenice-20260808"><time datetime="2026-08-08T16:00:00+02:00">SOBOTA 8. 8. · OD 16:00</time><h3>Minifestáček v Loděnici</h3><p><span class="distance">asi 13 km · přibližně 15 minut autem</span></p><p><strong>Loděnice, Klášterec nad Ohří.</strong> Komorní rockový minifestival nabídne čtyři regionální kapely: Abdera (rock / Jirkov), Black Ewe (crossover / rock / Jirkov), Izzy (hard rock / Jirkov) a Fext (pop / country / rock / Chomutov). Začátek je v 16:00 a <strong>vstup je dobrovolný</strong>.</p><p><em>Doplněno 8. srpna podle veřejné pozvánky Kláštereckého fóra nové generace; datum, místo, čas, účinkující a dobrovolné vstupné jsou uvedeny přímo na plakátu.</em></p></div>\n'''

text = ARTICLE.read_text(encoding="utf-8")
if f'data-event-id="{EVENT_ID}"' in text:
    print("already present")
    raise SystemExit(0)

anchor = '  <div class="event"><h3>Výstava kudlanek v Zooparku Chomutov</h3>'
if anchor not in text:
    raise SystemExit("anchor not found")
text = text.replace(anchor, BLOCK + anchor, 1)

text = re.sub(r'<meta property="article:modified_time" content="[^"]+">', '<meta property="article:modified_time" content="2026-08-08T05:45:00+02:00">', text, count=1)
text = re.sub(r'<p class="tag">.*?</p>', '<p class="tag">KULTURA · VOLNÝ ČAS · KADAŇ A REGION · AKTUALIZOVÁNO 8. SRPNA 2026 · 05:45</p>', text, count=1, flags=re.S)
text = text.replace('Týdenní přehled jsme rozšířili o sedm ověřených regionálních tipů.', 'Týdenní přehled jsme rozšířili také o dnešní Minifestáček v Loděnici v Klášterci nad Ohří a další ověřené regionální tipy.', 1)
ARTICLE.write_text(text, encoding="utf-8", newline="\n")
print("updated", ARTICLE)
