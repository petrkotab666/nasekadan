#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"
MODIFIED = "2026-07-30T18:00:00+02:00"


def main() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    if 'data-pamatky-v-kapse' not in text:
        anchor = '  </div>\n\n  <h2 id="koupani">'
        block = '''  </div>\n\n  <div class="fact" data-pamatky-v-kapse>\n    <h3>Památky v kapse: jedna vstupenka za 150 Kč na celý den</h3>\n    <p>Městské muzeum v Kadani nabízí společnou vstupenku <strong>Památky v kapse</strong>. Za 150 Kč lze během jednoho dne navštívit všech pět muzejních objektů: Radniční věž, Mikulovickou neboli Svatou bránu, hlavní prohlídkový okruh Františkánského kláštera, Kadaňský hrad a Minoritskou baštu se stálou expozicí Militaria.</p>\n    <p>V ceně jsou také aktuální výstavy <strong>Uhlí</strong> ve Františkánském klášteře, <strong>Broučci</strong> na Kadaňském hradě a <strong>Betonová hranice</strong> v Minoritské baště. Vstupenku lze koupit na pokladnách muzejních objektů a v Turistickém informačním centru Kadaň. Pro návštěvníka, který chce během dne projít více památek, jde o výhodnější variantu než jednotlivé vstupy.</p>\n  </div>\n\n  <h2 id="koupani">'''
        if anchor not in text:
            raise SystemExit("V článku nebyl nalezen konec bloku památek.")
        text = text.replace(anchor, block, 1)

    if 'Městské muzeum v Kadani – společná vstupenka Památky v kapse' not in text:
        source_anchor = '  <div class="source-list"><h2>Zdroje a kontrola údajů</h2><ul>\n'
        source = '    <li><a href="https://www.facebook.com/muzeumvKadani/" target="_blank" rel="noopener noreferrer">Městské muzeum v Kadani – společná vstupenka Památky v kapse</a></li>\n'
        if source_anchor not in text:
            raise SystemExit("V článku nebyl nalezen seznam zdrojů.")
        text = text.replace(source_anchor, source_anchor + source, 1)

    text = re.sub(
        r'(<meta property="article:modified_time" content=")[^"]+("\s*/?>)',
        rf'\g<1>{MODIFIED}\2',
        text,
        count=1,
    )
    text = re.sub(r'"dateModified":"[^"]+"', f'"dateModified":"{MODIFIED}"', text, count=1)
    text = re.sub(
        r'<small>Aktualizováno[^<]*</small>',
        '<small>Aktualizováno ve čtvrtek 30. července 2026 v 18:00. Venkovní program, doprava, dostupnost vstupenek a kapacita aktivit se mohou změnit. Před cestou doporučujeme otevřít odkaz pořadatele.</small>',
        text,
        count=1,
    )
    text = re.sub(
        r'<p class="updated">Aktualizováno:[^<]+</p>',
        '<p class="updated">Aktualizováno: 30. 7. 2026 v 18:00</p>',
        text,
        count=1,
    )

    required = [
        'data-pamatky-v-kapse',
        'Památky v kapse: jedna vstupenka za 150 Kč na celý den',
        'Mikulovickou neboli Svatou bránu',
        'https://www.facebook.com/muzeumvKadani/',
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"Po úpravě chybí povinný obsah: {missing}")

    ARTICLE.write_text(text, encoding="utf-8", newline="\n")
    print("Kulturní přehled doplněn o vstupenku Památky v kapse.")


if __name__ == "__main__":
    main()
