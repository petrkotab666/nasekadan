#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "jak-se-kadan-stara-o-hriste-2026.html"

OLD_PROJECT = '''<p>Investiční plán města uvádí také větší sportovní projekty, které přesahují běžnou výměnu jednotlivých prvků. Patří mezi ně obnova sportoviště na sídlišti C v prostoru u Golovinovy ulice, za bývalým kravínem poblíž domů čp. 1341 až 1353, modernizace fotbalového areálu, příprava softballového hřiště a technické zázemí sportoviště Tatran.</p>'''

NEW_PROJECT = '''<p><strong>Nejpodrobněji je doložena obnova hřiště 5.20 v Golovinově ulici na sídlišti C.</strong> Smlouva určuje místo za panelovým domem čp. 1341 až 1354, zahájení od 1. července a dokončení do 31. srpna 2026. Zhotovitelem je PETROM STAVBY a pokládku umělého povrchu má jako subdodavatel provést VYSSPA Sports Technology. Cena činí 787&nbsp;900 Kč bez DPH, tedy 953&nbsp;359 Kč včetně DPH.</p>
<p>Jde o pokračování delší proměny místa. Už v květnu 2025 město objednalo odstranění původního povrchu hřiště 5.20 za 148&nbsp;000 Kč bez DPH, tedy 179&nbsp;080 Kč včetně DPH. Až letošní smlouva ale řeší kompletní obnovu povrchu a vybavení.</p>
<p>Investiční plán města uvádí také další větší sportovní projekty, které přesahují běžnou výměnu jednotlivých prvků. Patří mezi ně modernizace fotbalového areálu, příprava softballového hřiště a technické zázemí sportoviště Tatran.</p>'''

OLD_ROW = '''<tr><td>5.19</td><td>Florbalové branky a obnova lajnování.</td></tr>'''
NEW_ROW = '''<tr><td>5.19</td><td>Florbalové branky a obnova lajnování.</td></tr>
<tr><td>5.20</td><td>Golovinova u čp. 1341 až 1354 na sídlišti C; kompletní obnova povrchu a vybavení v červenci a srpnu 2026.</td></tr>'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Nelze bezpečně doplnit {label}; očekáván 1 výskyt, nalezeno {count}.")
    return text.replace(old, new, 1)


def main() -> int:
    text = ARTICLE.read_text(encoding="utf-8")
    text = replace_once(text, OLD_PROJECT, NEW_PROJECT, "rekonstrukci hřiště 5.20")
    text = replace_once(text, OLD_ROW, NEW_ROW, "řádek hřiště 5.20")
    for required in (
        "953&nbsp;359 Kč včetně DPH",
        "zahájení od 1. července a dokončení do 31. srpna 2026",
        "odstranění původního povrchu hřiště 5.20",
        "VYSSPA Sports Technology",
    ):
        if required not in text:
            raise RuntimeError(f"Po doplnění chybí povinný údaj: {required}")
    ARTICLE.write_text(text, encoding="utf-8", newline="\n")
    print("Doplněn úplný veřejně doložený vývoj hřiště 5.20.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
