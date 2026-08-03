#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "zaregistrovala-se-v-kadani-darovala-krvetvorne-bunky-2026.html"
PUBLISHER = ROOT / "scripts" / "publish_darci_krvetvornych_bunek_20260803.py"

OLD_HEADING = "<h2>Samotný odběr proběhl ze\u00a0krve</h2>"
NEW_HEADING = "<h2>Krvetvorné buňky jí odebrali pomocí separátoru</h2>"

OLD_PARAGRAPH = (
    "<p>V jejím případě nebylo potřeba odebírat kostní dřeň z pánevní kosti. "
    "Několik dní před odběrem si aplikovala přípravné injekce a krvetvorné buňky "
    "byly následně odebrány pomocí separátoru z krve. Odběr trval přibližně čtyři "
    "hodiny a probíhal pod dohledem zdravotníků.</p>"
)
NEW_PARAGRAPH = (
    "<p>V jejím případě nebylo potřeba odebírat kostní dřeň z pánevní kosti. "
    "Několik dní před odběrem si aplikovala přípravné injekce, které pomohly "
    "vyplavit krvetvorné buňky do krevního oběhu. Při samotném odběru proudila "
    "krev přes separátor, který potřebné buňky oddělil, zatímco ostatní složky "
    "krve se vracely zpět do těla. Celý výkon trval přibližně čtyři hodiny a "
    "probíhal pod dohledem zdravotníků.</p>"
)


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    heading_count = text.count(OLD_HEADING)
    paragraph_count = text.count(OLD_PARAGRAPH)
    if heading_count != 1 or paragraph_count != 1:
        raise RuntimeError(
            f"Neočekávaný stav v {path}: heading={heading_count}, paragraph={paragraph_count}"
        )
    text = text.replace(OLD_HEADING, NEW_HEADING, 1)
    text = text.replace(OLD_PARAGRAPH, NEW_PARAGRAPH, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    patch(ARTICLE)
    patch(PUBLISHER)
    print("Opraven nadpis i popis odběru v článku a publikačním skriptu.")


if __name__ == "__main__":
    main()
