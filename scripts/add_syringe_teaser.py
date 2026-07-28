#!/usr/bin/env python3
from pathlib import Path
import re

TEASER = '''
<section class="callout" data-next-syringe-article>
  <strong>Příště: stříkačky ve vchodech a podezřelé byty</strong>
  <p>Ve čtvrtek 31. července v 5:00 zveřejníme článek o odhozených injekčních stříkačkách, podnětech obyvatel na podezřelé byty a o tom, co může Kadaň dělat kromě samotného sběru jehel.</p>
  <p><a href="/clanky/strikacky-vchody-drogy-kadan.html">Článek bude dostupný zde po zveřejnění →</a></p>
</section>
'''

def apply(path: Path) -> None:
    text = path.read_text(encoding='utf-8')
    if 'data-next-syringe-article' in text:
        return
    marker = '<div class="source-list">'
    if marker in text:
        text = text.replace(marker, TEASER + '\n' + marker, 1)
    else:
        text = re.sub(r'</article>', TEASER + '\n</article>', text, count=1)
    path.write_text(text, encoding='utf-8', newline='\n')

for candidate in [
    Path('.github/drafts/nemocnice-kadan-profil-sluzby-budoucnost.html'),
    Path('clanky/nemocnice-kadan-profil-sluzby-budoucnost.html'),
]:
    if candidate.exists():
        apply(candidate)
