#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/drafts/kulturni-zarizeni-kadan.html')
text = path.read_text(encoding='utf-8')

old = (
    'K nejvýraznějším událostem městského kalendáře patří nebo v minulých ročnících '
    'patřily například Císařský den, Narozeniny Maxipsa Fíka, Kadaňský pohádkový festival, '
    'Vysmáté léto, food festival, vinobraní a adventní program.'
)
new = (
    'K nejvýraznějším událostem městského kalendáře patří nebo v minulých ročnících '
    'patřily například Císařský den, Narozeniny Maxipsa Fíka, Vysmáté léto, food festival, '
    'vinobraní a adventní program.'
)

if old not in text:
    raise SystemExit('Nenalezena původní věta se špatným přiřazením festivalu.')
text = text.replace(old, new, 1)

anchor = '</p>\n\n    <div class="callout" id="cisarsky-den">'
clarification = (
    '</p>\n'
    '    <p><strong>Kadaňský pohádkový festival není akcí KZK.</strong> Pořádají jej '
    'Kabelová televize Kadaň, a. s., a Kino Hvězda Kadaň ve spolupráci s městem Kadaň. '
    'KZK se může zapojovat poskytnutím jednotlivých programových prostor, například Orfea, '
    'nejde však o hlavního pořadatele festivalu.</p>\n\n'
    '    <div class="callout" id="cisarsky-den">'
)
if anchor not in text:
    raise SystemExit('Nenalezen bod pro vložení upřesnění pořadatele.')
text = text.replace(anchor, clarification, 1)

path.write_text(text, encoding='utf-8')
print('Opraveno:', path)
