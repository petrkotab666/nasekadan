#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html"
MARKER = 'data-extraordinary-request="20260730"'
UPDATED = "2026-07-30T18:51:00+02:00"

LATEST_BOX = '''  <div class="update-box" data-extraordinary-request="20260730"><strong>Aktualizace 30. července v 18:51: ANO zveřejnilo podanou žádost</strong><p>Místní profil <em>ANO, tohle je Kadaň</em> zveřejnil kopii žádosti o svolání mimořádného zasedání zastupitelstva, která je datována 27. července 2026. Dokument uvádí, že podepsaní zastupitelé tvoří nejméně jednu třetinu všech členů zastupitelstva, žádají projednat aktuální stav a organizaci Nemocnice Kadaň a chtějí přítomnost jejího jednatele. Oficiální pozvánka města zatím zveřejněna není. Redakce současně zachytila neoficiální informaci o termínu 17. srpna 2026 v 8:00; dokud město nezveřejní pozvánku, jde pouze o neoficiální údaj.</p></div>
'''

SECTION = '''  <h2>ANO doložilo podání žádosti o mimořádné zastupitelstvo</h2>
  <h3>Žádost je datována 27. července</h3>
  <p>Místní politický profil <strong>ANO, tohle je Kadaň</strong> zveřejnil 28. července kopii žádosti adresované starostovi Janu Losenickému. Dokument je datován 27. července 2026 a odkazuje na § 92 odst. 1 zákona o obcích. V textu stojí, že níže podepsaní zastupitelé tvoří nejméně jednu třetinu všech členů kadaňského zastupitelstva.</p>
  <p>Žádost navrhuje, aby se mimořádné zasedání věnovalo aktuální zprávě o organizaci Nemocnice Kadaň a následné diskusi. Signatáři zároveň požadují, aby byl přítomen jednatel nemocnice Martin Krušina. Dokument vznikl ještě před oznámením, že od 1. srpna má Krušinu ve funkci jednatele nahradit Pavel Marek, takže bude nutné upřesnit, které vedení nemocnice bude na zasedání odpovídat.</p>
  <div class="fact-grid">
    <div class="fact-card"><span>Zastupitelstvo Kadaně</span><strong>27 členů</strong><p>Jedna třetina znamená nejméně devět zastupitelů. Zveřejněná kopie žádosti tvrdí, že tento práh byl splněn; úplný seznam podpisů na zveřejněném snímku není čitelný.</p></div>
    <div class="fact-card"><span>Zákonná lhůta</span><strong>Nejpozději do 21 dnů</strong><p>Pokud byla žádost úřadu doručena 27. července, zasedání se má konat nejpozději 17. srpna 2026.</p></div>
  </div>
  <h3>Neoficiálně se mluví o 17. srpnu v 8:00</h3>
  <p>Redakce zachytila neoficiální informaci, že by se mimořádné zastupitelstvo mohlo konat <strong>17. srpna 2026 v 8:00</strong>. Tento údaj časově odpovídá poslednímu dni jednadvacetidenní lhůty počítané od 27. července. Město ale při aktualizaci článku nezveřejnilo oficiální pozvánku, místo konání ani konečný program, proto termín zatím neuvádíme jako potvrzený.</p>
  <div class="callout"><strong>Žádost není totéž jako oficiální pozvánka</strong><p>Podáním žádosti vzniká zákonná povinnost zasedání svolat, veřejnost se však může spolehnout až na oficiálně zveřejněnou informaci města s datem, místem a programem.</p></div>
  <p>Redakce bude dále ověřovat přesné datum doručení, úplný seznam signatářů, potvrzení starosty a zveřejnění oficiální pozvánky.</p>
'''

SOURCE = '''    <li><a href="https://www.facebook.com/profile.php?id=100064347145382" target="_blank" rel="noopener noreferrer">ANO, tohle je Kadaň – veřejný příspěvek z 28. července 2026</a>: zveřejněná kopie žádosti datované 27. července 2026 a tvrzení o jejím podání; obrazový záznam má redakce k dispozici.</li>
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Nenalezen blok: {label}")
    return text.replace(old, new, 1)


def main() -> int:
    text = ARTICLE.read_text(encoding="utf-8")

    text = re.sub(
        r'(<meta property="article:modified_time" content=")[^"]+(\">)',
        rf'\g<1>{UPDATED}\2',
        text,
        count=1,
    )
    text = re.sub(
        r'("dateModified"\s*:\s*")[^"]+("\s*)',
        rf'\g<1>{UPDATED}\2',
        text,
        count=1,
    )
    text = re.sub(
        r'<span class="breaking">.*?</span>',
        '<span class="breaking">Aktuální zpráva · aktualizováno v 18:51</span>',
        text,
        count=1,
        flags=re.S,
    )

    if MARKER not in text:
        anchor = '  <div class="update-box"><strong>Aktualizace 30. července v 14:29</strong>'
        if anchor not in text:
            raise RuntimeError("Chybí původní aktualizační box.")
        text = text.replace(anchor, LATEST_BOX + anchor, 1)

    start = text.find('  <h2>Mimořádné zastupitelstvo zatím není oficiálně svolané</h2>')
    end = text.find('  <h2>Kdo je Pavel Marek</h2>', start)
    if start < 0 or end < 0:
        raise RuntimeError("Nelze najít původní kapitolu o mimořádném zastupitelstvu.")
    text = text[:start] + SECTION + "\n" + text[end:]

    text = text.replace(
        '    <li>Zda byla úřadu doručena formální žádost nejméně devíti zastupitelů, kdy a s jakým programem.</li>',
        '    <li>Kdy přesně byla žádost úřadu doručena, kdo ji podepsal a kdy město zveřejní oficiální pozvánku.</li>',
        1,
    )

    if SOURCE.strip() not in text:
        source_anchor = '    <li><a href="https://www.nemkadan.cz/pro-verejnost/verejnost/aktuality/nemocnice-kadan-sro-ma-nove-vedeni-949cs.html"'
        idx = text.find(source_anchor)
        if idx < 0:
            raise RuntimeError("Chybí začátek seznamu zdrojů.")
        text = text[:idx] + SOURCE + text[idx:]

    text = text.replace(
        'První verze článku zveřejněna 30. července 2026 v 9:10. Poslední ověřená aktualizace 30. července 2026 v 14:29.',
        'První verze článku zveřejněna 30. července 2026 v 9:10. Poslední ověřená aktualizace 30. července 2026 v 18:51.',
        1,
    )

    text = text.replace(
        '<li>Požadavek na mimořádné ZM zazněl 25. června</li><li>Mimořádné zastupitelstvo není zveřejněné</li>',
        '<li>Žádost o mimořádné ZM je datována 27. července</li><li>Neoficiálně: 17. srpna v 8:00</li><li>Oficiální pozvánka zatím není zveřejněná</li>',
        1,
    )

    ARTICLE.write_text(text, encoding="utf-8", newline="\n")

    check = ARTICLE.read_text(encoding="utf-8")
    required = [
        MARKER,
        'ANO doložilo podání žádosti o mimořádné zastupitelstvo',
        '17. srpna 2026 v 8:00',
        UPDATED,
        'Oficiální pozvánka zatím není zveřejněná',
    ]
    for needle in required:
        if needle not in check:
            raise RuntimeError(f"Po aktualizaci chybí: {needle}")

    print("Článek o změně vedení nemocnice byl doplněn o žádost ANO a neoficiální termín.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
