#!/usr/bin/env python3
"""Udrží na titulní straně tři nejnovější důležité články v pevném pořadí.

Skript je idempotentní: existující karty nejprve odstraní a následně je vloží
začátkem seznamu článků v pořadí petice, sečení, Tušimice. Hlavní hero ani
pravý box nemění.
"""
from __future__ import annotations

import re
from pathlib import Path

INDEX = Path("index.html")

CARDS = [
    (
        "petice-nemocnice-kadan-podpisova-mista-2026",
        '''      <article class="article-card hospital" data-auto-article="petice-nemocnice-kadan-podpisova-mista-2026">
        <div class="visual" style="background:linear-gradient(135deg,#173746,#315d70 58%,#9f2626)"><strong>Petice za nemocnici míří do ulic. Podepisovat se bude na třech místech</strong></div>
        <div class="article-body">
          <span class="meta">1. 8. 2026 · 12:19 · Zdravotnictví · Petice</span>
          <h3>Petice za nemocnici míří do ulic. Podepisovat se bude na třech místech</h3>
          <p>Podpisová místa, termín sběru a přehled změn vedení i neuzavřených sporů.</p>
          <a class="read-more" href="/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html">Přečíst článek →</a>
        </div>
      </article>''',
    ),
    (
        "sekani-travniku-kadan-spravci-vysky-2026",
        '''      <article class="article-card service" data-auto-article="sekani-travniku-kadan-spravci-vysky-2026">
        <div class="visual" style="background:linear-gradient(135deg,#284533,#71904d 58%,#a88435)"><strong>Sedm centimetrů i dvě seče ročně. Jak Kadaň skutečně udržuje městské trávníky</strong></div>
        <div class="article-body">
          <span class="meta">1. 8. 2026 · 11:00 · Město · Životní prostředí</span>
          <h3>Sedm centimetrů i dvě seče ročně. Jak Kadaň skutečně udržuje městské trávníky</h3>
          <p>Veřejný GIS rozděluje přes 105 hektarů zeleně do 282 ploch. Dokumenty ukazují rozdílné režimy sečení.</p>
          <a class="read-more" href="/clanky/sekani-travniku-kadan-spravci-vysky-2026.html">Přečíst článek →</a>
        </div>
      </article>''',
    ),
    (
        "jaderne-tusimice-smr-voda-doprava-eia-2026",
        '''      <article class="article-card service" data-auto-article="jaderne-tusimice-smr-voda-doprava-eia-2026">
        <div class="visual" style="background:linear-gradient(135deg,#10242e,#315d70 58%,#9d222a)"><strong>Jaderné Tušimice se připravují naplno. O vodě, dopravě i připojení ale stále není rozhodnuto</strong></div>
        <div class="article-body">
          <span class="meta">1. 8. 2026 · 04:00 · Energetika · Životní prostředí · Doprava</span>
          <h3>Jaderné Tušimice se připravují naplno. O vodě, dopravě i připojení ale stále není rozhodnuto</h3>
          <p>Úplná EIA měla být podle harmonogramu předána 12. května. Co víme o vodě, dopravě, připojení a přípravě SMR.</p>
          <a class="read-more" href="/clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html">Přečíst článek →</a>
        </div>
      </article>''',
    ),
]


def remove_existing_card(text: str, slug: str) -> str:
    patterns = [
        rf"\s*<article\b[^>]*data-auto-article=\"{re.escape(slug)}\"[^>]*>.*?</article>\s*",
        # Starší ruční označení karty petice.
        r"\s*<article\b[^>]*data-petice-podpisy-card[^>]*>.*?</article>\s*" if slug.startswith("petice-") else r"(?!)",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "\n", text, flags=re.S)
    return text


def main() -> None:
    if not INDEX.is_file():
        raise SystemExit("Chybí index.html")
    text = INDEX.read_text(encoding="utf-8")

    marker = '<div class="article-list">'
    if marker not in text:
        raise SystemExit("Na titulní straně chybí seznam článků.")

    for slug, _ in CARDS:
        text = remove_existing_card(text, slug)

    block = "\n" + "\n".join(card for _, card in CARDS) + "\n"
    text = text.replace(marker, marker + block, 1)

    # Bezpečnostní kontroly proti duplicitám a nechtěnému přepsání hero článku.
    for slug, _ in CARDS:
        count = text.count(f'data-auto-article="{slug}"')
        if count != 1:
            raise SystemExit(f"Karta {slug} je po úpravě {count}× místo 1×.")
    if 'data-latest-article-href="/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html"' not in text:
        raise SystemExit("Hlavní článek o petici se nesmí změnit.")

    INDEX.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
