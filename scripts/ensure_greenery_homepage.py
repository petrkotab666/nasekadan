#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

INDEX = Path('index.html')
SLUG = 'sekani-travniku-kadan-spravci-vysky-2026'
HREF = f'/clanky/{SLUG}.html'
TITLE = 'Sedm centimetrů i dvě seče ročně. Jak Kadaň skutečně udržuje městské trávníky'
DESCRIPTION = 'Veřejný GIS rozděluje přes 105 hektarů zeleně do 282 ploch. Dokumenty ukazují rozdílné režimy sečení, ale veřejná pravidla pro horko a sucho chybějí.'


def main() -> None:
    text = INDEX.read_text(encoding='utf-8')

    # Nejnovější petice zůstává hlavním hero článkem. V pravém boxu má být
    # chronologicky následující článek o sečení, nikoli starší Tušimice.
    aside = f'''<aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">1. 8. 2026 v 11:00</p>
      <h2>{TITLE}</h2>
      <p>{DESCRIPTION}</p>
      <a class="aside-button" href="{HREF}">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div>
    </aside>'''
    text, count = re.subn(
        r'<aside class="current-aside">.*?</aside>',
        aside,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit('Na titulní straně nebyl nalezen pravý box aktuálního článku.')

    # Karta musí zůstat v seznamu i po publikaci novějších článků.
    if f'data-auto-article="{SLUG}"' not in text:
        card = f'''\n      <article class="article-card service" data-auto-article="{SLUG}">
        <div class="visual" style="background:linear-gradient(135deg,#284533,#71904d 58%,#a88435)"><strong>{TITLE}</strong></div>
        <div class="article-body">
          <span class="meta">1. 8. 2026 · 11:00 · Město · Životní prostředí</span>
          <h3>{TITLE}</h3>
          <p>{DESCRIPTION}</p>
          <a class="read-more" href="{HREF}">Přečíst článek →</a>
        </div>
      </article>\n'''
        petition = re.search(
            r'(<article class="article-card hospital" data-petice-podpisy-card>.*?</article>)',
            text,
            flags=re.S,
        )
        if petition:
            text = text[:petition.end()] + card + text[petition.end():]
        else:
            marker = '<div class="article-list">'
            if marker not in text:
                raise SystemExit('Na titulní straně nebyl nalezen seznam článků.')
            text = text.replace(marker, marker + card, 1)

    if HREF not in text or f'data-auto-article="{SLUG}"' not in text:
        raise SystemExit('Článek o sečení se nepodařilo vrátit na titulní stranu.')

    INDEX.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
