#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"
URL = "https://radka.kadan.cz/udalosti/vymena-mladeze-beyond-labels/"

BLOCK = '''
  <section class="event" data-beyond-labels-radka>
    <time datetime="2026-08-02">NEDĚLE 2. SRPNA · ZAČÁTEK VÝMĚNY</time>
    <h3>Beyond Labels: mezinárodní výměna mládeže v Měděnci</h3>
    <p>RADKA zahajuje v neděli 2. srpna mezinárodní výměnu mládeže v rámci programu Erasmus+. Pobyt potrvá do 12. srpna a zaměří se na duševní zdraví, emoční pohodu, sebedůvěru, zvládání stresu, sociální tlak a vytváření zdravých návyků. Součástí mají být také kreativita a sebevyjádření.</p>
    <p><strong>Místo:</strong> Měděnec. <strong>Termín:</strong> 2.–12. srpna 2026. Jde o pobytovou výměnu s přihlášením, nikoli o volně přístupnou jednodenní akci. Informace pro účastníky a odkaz na přihlášku zveřejňuje <a href="https://radka.kadan.cz/udalosti/vymena-mladeze-beyond-labels/" target="_blank" rel="noopener noreferrer">RADKA na stránce akce</a>.</p>
  </section>
'''

SOURCE = '''    <li><a href="https://radka.kadan.cz/udalosti/vymena-mladeze-beyond-labels/" target="_blank" rel="noopener noreferrer">RADKA – Beyond Labels, mezinárodní výměna mládeže v Měděnci</a></li>\n'''


def main() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    if 'data-beyond-labels-radka' not in text:
        pattern = r'(<div class="fact"><h3>Plavecký tábor RADKY: Pod hladinou</h3>.*?</div>)'
        text, count = re.subn(pattern, r'\1\n' + BLOCK, text, count=1, flags=re.S)
        if count != 1:
            raise SystemExit("Nenalezen blok plaveckého tábora RADKY")

    text = text.replace(
        'Perštejna, Vilémova, Radonic, Měděnce, Mašťova, Chban, Libědic a Rokle',
        'Perštejna, Vilémova, Radonic, Mašťova, Chban, Libědic a Rokle',
    )

    if URL not in text.split('<div class="source-list">', 1)[-1]:
        marker = '    <li><a href="https://radka.kadan.cz/uvodni-stranka/tabory-a-pobyty/"'
        if marker not in text:
            raise SystemExit("Nenalezen zdrojový odkaz RADKY")
        text = text.replace(marker, SOURCE + marker, 1)

    text = re.sub(
        r'<meta property="article:modified_time" content="[^"]+">',
        '<meta property="article:modified_time" content="2026-07-29T18:00:00+02:00">',
        text,
        count=1,
    )
    text = re.sub(
        r'"dateModified":"[^"]+"',
        '"dateModified":"2026-07-29T18:00:00+02:00"',
        text,
        count=1,
    )
    ARTICLE.write_text(text, encoding="utf-8", newline="\n")

    result = ARTICLE.read_text(encoding="utf-8")
    assert 'data-beyond-labels-radka' in result
    assert URL in result
    print("Beyond Labels bylo doplněno do kulturního přehledu.")


if __name__ == "__main__":
    main()
