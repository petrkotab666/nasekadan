#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "epetice-nemocnice-kadan.html"
PRIVATE_URL = "https://e-petice.cz/en/petitions/petice-za-zachovani-nemocnice-kadan-s-r-o-ve-vlastnictvi-mesta.html"
MODIFIED = "2026-07-27T14:25:00+02:00"


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_article() -> None:
    if not ARTICLE.exists():
        return

    text = ARTICLE.read_text(encoding="utf-8")

    # Přesný stav při redakční kontrole. Počet je vždy časově označen, protože
    # se může průběžně měnit.
    text = re.sub(
        r'<div class="status-box"><b>Aktuální stav:</b>.*?</div>',
        (
            '<div class="status-box"><b>Stav při kontrole 27. července 2026:</b> '
            f'Petice na soukromém portálu <a href="{PRIVATE_URL}" target="_blank" '
            'rel="noopener noreferrer">e-petice.cz</a> uváděla dva potvrzené podpisy. '
            'Jako autorka je uvedena Vlasta Štaubrová a stránka uvádí datum nahrání '
            '21. července 2026. Jeden podpis byl veřejně zobrazen pod jménem autorky, '
            'údaje druhého podporovatele zveřejněny nebyly. Nejde o státní ePetici '
            'v Portálu občana.</div>'
        ),
        text,
        count=1,
        flags=re.S,
    )

    text = re.sub(
        r'<div class="numbers">.*?</div></div>',
        (
            '<div class="numbers">'
            '<div><b>2 podpisy</b><span>stav zobrazený při kontrole 27. 7. 2026</span></div>'
            '<div><b>21. 7. 2026</b><span>datum nahrání uvedené na stránce petice</span></div>'
            '<div><b>8 požadavků</b><span>online text zachovává všech osm bodů listinné verze</span></div>'
            '<div><b>Soukromý portál</b><span>nejde o státní ePetici podepisovanou Identitou občana</span></div>'
            '</div>'
        ),
        text,
        count=1,
        flags=re.S,
    )

    # Změnit nadpis části a přidat přesný výsledek porovnání. Text osobních
    # kontaktů předkladatelky se záměrně nepřebírá.
    text = text.replace(
        '<h2 id="plne-zneni">Celé znění listinné petice obsahuje osm konkrétních požadavků</h2>',
        '<h2 id="plne-zneni">Online a listinná verze obsahují stejných osm požadavků</h2>',
        1,
    )

    comparison_marker = '<h2 id="plne-zneni">Online a listinná verze obsahují stejných osm požadavků</h2>'
    comparison = (
        comparison_marker
        + '<div class="factcheck" id="porovnani-zneni"><h3>Výsledek porovnání</h3>'
        + '<ul><li><strong>Všech osm číslovaných požadavků je zachováno ve stejném pořadí a se stejným věcným zněním.</strong></li>'
        + '<li>Online verze obsahuje také úvodní odůvodnění, pět otázek vedení města a závěrečnou výzvu k zachování nemocnice.</li>'
        + '<li>Nejde tedy o dříve zvažovanou zkrácenou variantu omezenou limitem 3500 znaků. Soukromá platforma umožnila zveřejnit celý dlouhý text.</li>'
        + '<li>Rozdíl je ve způsobu sběru podpisů: e-petice.cz potvrzuje podpis odkazem zaslaným e-mailem, zatímco státní ePetice ověřuje totožnost prostřednictvím Identity občana.</li>'
        + '</ul></div>'
        + '<p>Podle úplného textu zveřejněného na online stránce a dříve doloženého listinného dokumentu jsme nenašli věcný rozdíl v požadavcích petice. Online stránka přebírá celé znění včetně všech osmi bodů. Kontaktní adresu, telefon a e-mail předkladatelky redakce znovu nezveřejňuje, přestože jsou na veřejné stránce uvedeny.</p>'
    )
    if 'id="porovnani-zneni"' not in text and comparison_marker in text:
        text = text.replace(comparison_marker, comparison, 1)

    # Doplnit přesný stav do sledovací části.
    text = text.replace(
        '<p>U zveřejněné petice na e-petice.cz budeme kontrolovat zejména úplné znění, veřejný počet podporovatelů, případné změny a informaci o jejím předání městu. Současně budeme ověřovat, zda se petice neobjeví také v oficiálním seznamu státních ePetic.</p>',
        '<p>Úplné znění jsme již porovnali: všech osm požadavků je zachováno. Dále budeme sledovat veřejný počet podporovatelů, případné změny textu, informaci o předání petice městu a to, zda se stejná iniciativa neobjeví také v oficiálním seznamu státních ePetic.</p>',
        1,
    )

    # Aktualizovat boční box bez zveřejnění osobních kontaktních údajů.
    text = re.sub(
        r'<div class="sidebox"><h3>Aktuální stav</h3>.*?</div><div class="sidebox"><h3>Důležité rozlišení</h3>',
        (
            '<div class="sidebox"><h3>Aktuální stav</h3>'
            '<p class="updated">Kontrola: 27. 7. 2026</p>'
            '<p><strong>2 potvrzené podpisy</strong> na soukromém portálu.</p>'
            '<p>Text obsahuje všech osm požadavků listinné verze.</p>'
            f'<p><a href="{PRIVATE_URL}" target="_blank" rel="noopener noreferrer">Otevřít petici →</a></p>'
            '</div><div class="sidebox"><h3>Důležité rozlišení</h3>'
        ),
        text,
        count=1,
        flags=re.S,
    )

    # Přidat zdrojový záznam a přesný časový údaj.
    source_marker = '<div class="source-list"><h2>Zdroje a metodika</h2><ul>'
    source_entry = (
        '<li>Úplný text a stav petice na e-petice.cz: při kontrole 27. 7. 2026 '
        'stránka uváděla autorku Vlastu Štaubrovou, datum nahrání 21. 7. 2026 '
        'a dva potvrzené podpisy. Osobní kontaktní údaje z veřejné stránky '
        'redakce znovu nepublikuje.</li>'
    )
    if source_marker in text and 'dva potvrzené podpisy' not in text[text.find(source_marker):]:
        text = text.replace(source_marker, source_marker + source_entry, 1)

    text = re.sub(
        r'<small>Aktualizováno 27\. 7\. 2026.*?</small>',
        '<small>Aktualizováno 27. 7. 2026 po ověření úplného online textu a stavu dvou podpisů. Počet podpisů se může průběžně měnit.</small>',
        text,
        count=1,
        flags=re.S,
    )

    # Aktualizovat strukturovaná data.
    def update_schema(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        if data.get("@type") == "NewsArticle":
            data["dateModified"] = MODIFIED
            data["description"] = (
                "Online petice za Nemocnici Kadaň běží na soukromém portálu. "
                "Při kontrole měla dva podpisy a obsahovala všech osm požadavků listinné verze."
            )
        return '<script type="application/ld+json">' + json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        ) + "</script>"

    text = re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        update_schema,
        text,
        count=1,
        flags=re.S,
    )

    write(ARTICLE, text)


def main() -> int:
    update_article()
    print("Článek byl doplněn o přesný počet podpisů, datum nahrání a výsledek porovnání obou verzí petice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
