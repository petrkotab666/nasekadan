#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky/nova-revmatologicka-ambulance-kadan-podzim-2026.html"
MARKER = 'data-revma-registry-context="1"'

text = ARTICLE.read_text(encoding="utf-8")

if MARKER not in text:
    section = '''<section class="callout" data-revma-registry-context="1"><strong>Co potvrzují odborné registry</strong><p>Česká revmatologická společnost uvádí MUDr. Vlastimila Novotného jako kontakt centra biologické léčby pro dospělé při Nemocnici Kadaň na adrese Golovinova 1559. Registr Ministerstva zdravotnictví současně eviduje Nemocnici Kadaň jako akreditované ambulantní pracoviště pro specializovaný výcvik v revmatologii s platností do 31. prosince 2026.</p><p><strong>Důležité upřesnění:</strong> tyto veřejné záznamy se vztahují k Nemocnici Kadaň v Golovinově ulici. Samy o sobě nepotvrzují, že nové pracoviště na adrese kpt. Jaroše 609 je pobočkou nemocnice nebo že bude poskytovat biologickou léčbu.</p></section>'''
    anchor = '<h2>Další odborná péče přímo ve městě</h2>'
    if anchor not in text:
        raise SystemExit("V článku chybí vkládací bod pro registry.")
    text = text.replace(anchor, section + "\n" + anchor, 1)

    source_note = '''<p><strong>Doplněné veřejné registry:</strong> <a href="https://revmatologicka-spolecnost.cz/centra-biologicke-lecby/" rel="nofollow noopener">Česká revmatologická společnost – centra biologické léčby</a>; <a href="https://akreditace.mzcr.cz/poskytovatele/view/42281" rel="nofollow noopener">Ministerstvo zdravotnictví – akreditace Nemocnice Kadaň</a>.</p>'''
    text = text.replace('</div>\n</article>', source_note + '</div>\n</article>', 1)

now = datetime.now(ZoneInfo("Europe/Prague")).replace(microsecond=0).isoformat()
text = re.sub(
    r'(<meta property="article:modified_time" content=")[^"]+(\">)',
    rf'\g<1>{now}\g<2>',
    text,
    count=1,
)
text = re.sub(
    r'("dateModified"\s*:\s*")[^"]+(\")',
    rf'\g<1>{now}\g<2>',
    text,
    count=1,
)

ARTICLE.write_text(text, encoding="utf-8", newline="\n")
assert MARKER in text
assert "revmatologicka-spolecnost.cz/centra-biologicke-lecby/" in text
assert "akreditace.mzcr.cz/poskytovatele/view/42281" in text
print("Ověřené odborné registry byly doplněny do článku o revmatologii.")
