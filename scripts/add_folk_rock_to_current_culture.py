#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

PATH = Path('clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html')
MARKER = 'data-folk-rock-loucna'
INSERT_BEFORE = '<section class="nearby regional-highlight">'
BLOCK = '''  <section class="nearby regional-highlight" data-folk-rock-loucna><p class="distance">Loučná pod Klínovcem · přibližně 35 minut autem · pátek 31. července a sobota 1. srpna</p><h3>Folk Rock Festival na Horách</h3><p>Na plácku u hraničního přechodu se uskuteční šestý ročník česko-německého hudebního festivalu. Vystoupí celkem 11 kapel různých žánrů. Páteční program začíná v 17:30, sobotní ve 14:00.</p><p><strong>Vstupné:</strong> 150 Kč na jeden den nebo 250 Kč na oba dny. Děti do 15 let a držitelé ZTP mají vstup zdarma. Na místě má být zajištěné občerstvení. <strong>Pořadatel:</strong> Město Loučná pod Klínovcem.</p></section>\n'''


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise RuntimeError(f'Nenalezen očekávaný text: {old[:80]}')
    return text.replace(old, new, 1)


def main() -> int:
    text = PATH.read_text(encoding='utf-8')
    if MARKER in text:
        print('Folk Rock Festival už je v článku.')
        return 0

    text = replace_once(
        text,
        '<meta property="article:modified_time" content="2026-07-28T13:15:00+02:00">',
        '<meta property="article:modified_time" content="2026-07-28T14:20:00+02:00">',
    )
    text = replace_once(
        text,
        '"dateModified":"2026-07-28T13:15:00+02:00"',
        '"dateModified":"2026-07-28T14:20:00+02:00"',
    )
    text = replace_once(
        text,
        '<div><b>9</b><span>vybraných tipů z okolí</span></div>',
        '<div><b>10</b><span>vybraných tipů z okolí</span></div>',
    )
    text = replace_once(
        text,
        INSERT_BEFORE,
        BLOCK + INSERT_BEFORE,
    )
    text = replace_once(
        text,
        '<li><a href="https://www.koupalistekadan.cz/inpage/vstupne-koupaliste-kadan/"',
        '<li><a href="https://www.loucna.eu/obcan/akce-mesta/folk-rock-festival-na-horach-810_95cs.html" target="_blank" rel="noopener noreferrer">Město Loučná pod Klínovcem – Folk Rock Festival na Horách</a></li>\n    <li><a href="https://www.koupalistekadan.cz/inpage/vstupne-koupaliste-kadan/"',
    )

    PATH.write_text(text, encoding='utf-8', newline='\n')
    print('Folk Rock Festival byl doplněn do aktuálního kulturního přehledu.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
