#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / ".github/drafts/koupaliste-kadan-skluzavka-niagara.html"

BLOCK = '''<!-- BEGIN COUNCIL APPROVAL 2026-07-29 -->
<section data-council-approval="2026-07-29">
  <h2 id="zastupitelstvo">Co přesně zaznělo na zastupitelstvu</h2>
  <p>Zápis z 25. června přináší nejkonkrétnější veřejné vysvětlení dvoumilionové částky. Jana Demjanová se zeptala, v čem cena skluzavky spočívá. Starosta Jan Losenický odpověděl, že jde o cenu skluzavky a všechny vedlejší práce.</p>
  <p>Jednatel Tepelného hospodářství Dušan Kučera doplnil, že podobné atrakce jsou samy o sobě velmi drahé a cena byla vysoutěžena ve výběrovém řízení. Zastupitelé pak dotaci schválili jednomyslně: 25 hlasů pro, nikdo proti a nikdo se nezdržel.</p>
  <div class="callout"><strong>Schválení po otevření není samo o sobě důkazem chyby</strong>Tepelné hospodářství mohlo být investorem a město mohlo následně schválit úhradu části uznatelných nákladů. Veřejné dokumenty ale stále musí umožnit zjistit, kdy byl závazek vůči dodavateli uzavřen, co přesně zahrnovaly vedlejší práce a kolik bylo skutečně čerpáno.</div>
</section>
<!-- END COUNCIL APPROVAL 2026-07-29 -->'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    original = text

    text = re.sub(
        r"\s*<!-- BEGIN COUNCIL APPROVAL 2026-07-29 -->.*?<!-- END COUNCIL APPROVAL 2026-07-29 -->\s*",
        "\n",
        text,
        flags=re.S,
    )

    toc_needle = '<li><a href="#casova-osa">Časová osa peněz a provozu</a></li>'
    toc_addition = toc_needle + '\n    <li><a href="#zastupitelstvo">Co zaznělo na zastupitelstvu</a></li>'
    if 'href="#zastupitelstvo"' not in text:
        text = text.replace(toc_needle, toc_addition, 1)

    marker = '<h2 id="financovani">'
    if marker not in text:
        raise RuntimeError("Ve finálním draftu chybí sekce financování")
    text = text.replace(marker, BLOCK + "\n\n  " + marker, 1)

    source = '    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5095122.pdf" target="_blank" rel="noopener noreferrer">Město Kadaň: zápis ze 17. zasedání zastupitelstva dne 25. června 2026</a></li>\n'
    source_marker = '    <li><a href="https://www.cez.cz/'
    if "filemanager/files/5095122.pdf" not in text:
        text = text.replace(source_marker, source + source_marker, 1)

    text = text.replace("2026-07-31T14:00:00+02:00", "2026-07-31T05:00:00+02:00")
    text = text.replace(
        "Připraveno pro pátek 31. července 2026.</strong>",
        "Připraveno pro pátek 31. července 2026 v 5:00.</strong>",
    )

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("Finální draft koupaliště:", "změněn" if text != original else "beze změn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
