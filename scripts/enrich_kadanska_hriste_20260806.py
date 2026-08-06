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

OLD_DESC = (
    "Kadaň spravuje 62 veřejně přístupných hřišť a sportovišť a dalších sedm v uzavřených areálech. "
    "Prošli jsme objednávky bez textové vrstvy a sestavili přehled nových prvků, oprav a konkrétních lokalit."
)
NEW_DESC = (
    "Kadaň spravuje 62 veřejně přístupných hřišť a sportovišť a dalších sedm v uzavřených areálech. "
    "Přinášíme přehled nových prvků, oprav, rekonstrukcí a konkrétních lokalit."
)

OLD_LEAD = '''<p class="leadtext"><strong>Kadaň podle městské zprávy zajišťuje revize pro 62 veřejně přístupných dětských hřišť a sportovišť a dalších sedm zařízení v uzavřených areálech. Prošli jsme také naskenované objednávky, které běžné fulltextové vyhledávání neumělo přečíst. Díky tomu lze přesněji ukázat, co se letos mění a kam nové prvky míří.</strong></p>'''
NEW_LEAD = '''<p class="leadtext"><strong>Kadaň podle městské zprávy zajišťuje revize pro 62 veřejně přístupných dětských hřišť a sportovišť a dalších sedm zařízení v uzavřených areálech. Přehled ukazuje, co se letos mění, kam nové prvky míří a jaké větší rekonstrukce město připravuje.</strong></p>'''

OLD_PASSPORT = '''<p>Samotný úplný pasport všech hřišť s adresami, vybavením a daty posledních kontrol však město na veřejné mapě nevystavuje. Číselná označení se proto dají převádět na konkrétní místa jen postupně z objednávek a dalších podkladů.</p>'''
NEW_PASSPORT = '''<p>Samotný úplný pasport všech hřišť s adresami, vybavením a daty posledních kontrol však město na veřejné mapě nevystavuje. Veřejné podklady umožňují přiřadit ke konkrétním místům jen část číselných označení, úplný přehled ale stále chybí.</p>'''

OLD_METHOD = '''<p>U naskenovaných objednávek bez textové vrstvy redakce stáhla veřejné přílohy z Registru smluv, převedla jednotlivé stránky na obraz a použila české OCR. Částky a lokality byly následně kontrolovány proti samotným obrazům objednávek.</p>'''

PUBLIC_TEXT_FILES = (
    ROOT / "index.html",
    ROOT / "rss.xml",
    ROOT / "llms.txt",
    ROOT / "clanky" / "index.html",
)


def replace_once_idempotent(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new, 1)
    if count == 0 and new in text:
        return text
    raise RuntimeError(f"Nelze bezpečně doplnit {label}; očekáván 1 výskyt nebo hotová náhrada, nalezeno {count}.")


def sanitize(text: str) -> str:
    replacements = (
        (OLD_DESC, NEW_DESC),
        (OLD_LEAD, NEW_LEAD),
        (OLD_PASSPORT, NEW_PASSPORT),
        ("<h2>Přehled dosud rozpoznaných čísel</h2>", "<h2>Přehled známých čísel</h2>"),
        ("<h2>Zdroje a způsob ověření</h2>", "<h2>Zdroje</h2>"),
        (OLD_METHOD, ""),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def sanitize_public_outputs() -> None:
    paths = [ARTICLE, *PUBLIC_TEXT_FILES, *sorted((ROOT / "clanky").glob("strana-*.html"))]
    for path in paths:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        cleaned = sanitize(original)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8", newline="\n")


def main() -> int:
    text = ARTICLE.read_text(encoding="utf-8")
    text = replace_once_idempotent(text, OLD_PROJECT, NEW_PROJECT, "rekonstrukci hřiště 5.20")
    text = replace_once_idempotent(text, OLD_ROW, NEW_ROW, "řádek hřiště 5.20")
    ARTICLE.write_text(text, encoding="utf-8", newline="\n")
    sanitize_public_outputs()

    article = ARTICLE.read_text(encoding="utf-8")
    for required in (
        "953&nbsp;359 Kč včetně DPH",
        "zahájení od 1. července a dokončení do 31. srpna 2026",
        "odstranění původního povrchu hřiště 5.20",
        "VYSSPA Sports Technology",
        NEW_DESC,
        NEW_LEAD,
        "<h2>Zdroje</h2>",
    ):
        if required not in article:
            raise RuntimeError(f"Po doplnění chybí povinný údaj: {required}")

    forbidden = (
        "fulltextové vyhledávání",
        "bez textové vrstvy",
        "naskenované objednávky",
        "české OCR",
        "způsob ověření",
    )
    for phrase in forbidden:
        if phrase.casefold() in article.casefold():
            raise RuntimeError(f"Ve veřejném článku zůstal interní postup: {phrase}")

    print("Doplněn vývoj hřiště 5.20 a odstraněny interní postupy dohledávání z veřejných výstupů.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
