#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_TITLE = "Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná"
NEW_TITLE = "Petice za nemocnici je online na soukromém portálu. Co to mění"
OLD_DESC = "Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze sčítat elektronické a listinné podpisy."
NEW_DESC = "Petice běží na e-petice.cz, nikoli ve státním nástroji. Vysvětlujeme způsob potvrzení online podpory a skutečné právní účinky."
OLD_LONG_DESC = "Předkladatelka petice za Nemocnici Kadaň připravuje ePetici. Vysvětlujeme limit 3500 znaků, totožnost obou verzí, ověřené podpisy i právní účinky."
NEW_LONG_DESC = "Petice za Nemocnici Kadaň je zveřejněna na soukromém portálu e-petice.cz. Článek odlišuje online podporu potvrzenou e-mailem od státní ePetice a listinných podpisů."


def patch(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"Opraveno: {path.relative_to(ROOT)}")


def main() -> int:
    patch(ROOT / "index.html", [
        ("<strong>ePetice za nemocnici</strong>", "<strong>Online petice za nemocnici</strong>"),
        ("<h3>Papírová a elektronická verze musí být stejná</h3>", "<h3>Soukromý portál není státní ePetice</h3>"),
        ("<p>Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze elektronické a listinné podpisy vykazovat společně.</p>", "<p>Petice běží na e-petice.cz. Co soukromý portál ověřuje a jaké účinky mají potvrzené online podpory.</p>"),
        ("Přečíst vysvětlení →", "Přečíst aktualizované vysvětlení →"),
    ])
    patch(ROOT / "clanky" / "index.html", [
        (OLD_TITLE, NEW_TITLE),
        ("<strong>ePetice za nemocnici</strong>", "<strong>Online petice za nemocnici</strong>"),
        ("Vysvětlení limitu 3500 znaků, podmínky totožného znění, ověřování podpisů a právních účinků oficiální ePetice.", "Rozlišení soukromé platformy e-petice.cz, listinných podpisů a státem ověřené ePetice."),
        ("Přečíst mimořádný článek →", "Přečíst aktualizovaný článek →"),
    ])
    patch(ROOT / "rss.xml", [
        (OLD_TITLE, NEW_TITLE),
        (OLD_DESC, NEW_DESC),
    ])
    patch(ROOT / "llms.txt", [
        (OLD_TITLE, NEW_TITLE),
        (OLD_LONG_DESC, NEW_LONG_DESC),
    ])
    patch(ROOT / "news-sitemap.xml", [(OLD_TITLE, NEW_TITLE)])
    print("Odkazy na článek o soukromé e-petici byly sjednoceny.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
