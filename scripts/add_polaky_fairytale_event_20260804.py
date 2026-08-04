#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-3-9-srpna-2026.html"
REGIONAL = ROOT / "data" / "regional-sources.json"
MODIFIED = "2026-08-04T20:25:00+02:00"
OFFICIAL_URL = "https://www.zamek-polaky.cz/"
FACEBOOK_URL = "https://www.facebook.com/zamekpolakycz/"
INSTAGRAM_URL = "https://www.instagram.com/zamekpolaky/"
EVENT_ID = "zamek-polaky-pohadkove-prohlidky-20260808"


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Nenalezen očekávaný blok: {label}")
    return text.replace(old, new, 1)


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '<meta property="article:modified_time" content="2026-08-04T06:15:00+02:00">',
        f'<meta property="article:modified_time" content="{MODIFIED}">',
        "article:modified_time",
    )
    text = replace_once(
        text,
        '"dateModified":"2026-08-04T06:15:00+02:00"',
        f'"dateModified":"{MODIFIED}"',
        "schema dateModified",
    )

    old_description = (
        "Ověřený přehled akcí na týden 3.–9. srpna 2026: módní show, dixieland, hudební víkend "
        "na Liďáku, ARG U Soudku, Medové odpoledne, kino, výstavy, koupání a Night Run v Mostě."
    )
    new_description = (
        "Ověřený přehled akcí na týden 3.–9. srpna 2026: módní show, dixieland, Liďák, pohádkové "
        "prohlídky zámku Poláky, Medové odpoledne, kino, výstavy, koupání a Night Run v Mostě."
    )
    text = text.replace(old_description, new_description)
    text = replace_once(
        text,
        '<meta name="twitter:description" content="Módní show, dixieland, hudební víkend na Liďáku, ARG U Soudku, Medové odpoledne, kino a Night Run v Mostě.">',
        '<meta name="twitter:description" content="Módní show, Liďák, pohádkové prohlídky zámku Poláky, Medové odpoledne, kino a Night Run v Mostě.">',
        "twitter description",
    )

    old_lead = (
        '<p class="leadtext">Nadcházející týden přinese do Kadaně módní přehlídku pod širým nebem, '
        'páteční dixieland na Studentském náměstí, páteční a sobotní hudební program na Liďáku, sobotní '
        'večer s ARG v Pivnici U Soudku a nedělní Medové odpoledne ve františkánské zahradě. Kino Hvězda '
        'nabídne čtyři projekce, pokračuje šest výstav a při horkém počasí zůstávají hlavními cíli obě '
        'koupaliště. Pro výjezd vybíráme výstavu kudlanek v chomutovském zooparku, Krásný Dvůr a velký '
        'Night Run v Mostě.</p>'
    )
    new_lead = (
        '<p class="leadtext">Nadcházející týden přinese do Kadaně módní přehlídku pod širým nebem, '
        'páteční dixieland na Studentském náměstí, páteční a sobotní hudební program na Liďáku, sobotní '
        'večer s ARG v Pivnici U Soudku a nedělní Medové odpoledne ve františkánské zahradě. Rodinám '
        'doporučujeme také sobotní pohádkové prohlídky zámku Poláky. Kino Hvězda nabídne čtyři projekce, '
        'pokračuje šest výstav a při horkém počasí zůstávají hlavními cíli obě koupaliště. Pro větší výjezd '
        'vybíráme Night Run v Mostě.</p>'
    )
    text = replace_once(text, old_lead, new_lead, "úvodní odstavec")

    text = replace_once(
        text,
        '<div class="hero-visual"><strong>Šest veřejných akcí v Kadani, čtyři filmy, šest výstav, dvě koupaliště a sobotní běžecký večer v Mostě. Nově jsme doplnili páteční a sobotní hudební program na Liďáku.</strong></div>',
        '<div class="hero-visual"><strong>Šest veřejných akcí v Kadani, pohádkové prohlídky na zámku Poláky, čtyři filmy, šest výstav, dvě koupaliště a sobotní běžecký večer v Mostě.</strong></div>',
        "souhrnný vizuál",
    )

    polaky_event = (
        '  <div class="event" data-event-id="zamek-polaky-pohadkove-prohlidky-20260808">'
        '<time datetime="2026-08-08T10:00:00+02:00">SOBOTA 8. 8. · 10:00–17:00</time>'
        '<h3>Pohádkové prohlídky zámku Poláky</h3>'
        '<p><span class="distance">zhruba 20 km · přibližně 20 minut autem</span></p>'
        '<p><strong>Zámek Poláky, obec Chbany.</strong> Zámeckými komnatami provedou návštěvníky herci v kostýmech a hranými scénami oživí známé české národní pohádky. Každá komnata nabídne jiný příběh. Prohlídky začínají každou celou hodinu a program je určený dětem i dospělým. Cenu vstupného doporučujeme před cestou ověřit u pořadatele.</p>'
        '<p><a href="https://www.zamek-polaky.cz/">Oficiální web zámku Poláky</a></p>'
        '<p><em>Doplněno 4. srpna podle oficiálního programu zámku a veřejné pozvánky pořadatele.</em></p>'
        '</div>\n'
    )
    nearby_anchor = '  <div class="event"><h3>Zámek a park Krásný Dvůr</h3>'
    if f'data-event-id="{EVENT_ID}"' not in text:
        text = replace_once(text, nearby_anchor, polaky_event + nearby_anchor, "vložení akce zámku Poláky")

    old_children = (
        '<p>Pro děti jsou tento týden nejjistější volbou dvě dabované či mládeži přístupné projekce Kina Hvězda, '
        'nedělní Putování s Fíkem v rámci Medového odpoledne, koupaliště a výstava kudlanek v Chomutově. KZK '
        'zároveň na svém webu zveřejňuje přihlášku do <strong>Tanečních pro mládež 2026</strong>; zájemci by '
        'měli aktuální dostupnost míst zkontrolovat přímo v přihláškovém formuláři.</p>'
    )
    new_children = (
        '<p>Pro děti jsou tento týden nejjistější volbou sobotní pohádkové prohlídky zámku Poláky, dvě dabované '
        'či mládeži přístupné projekce Kina Hvězda, nedělní Putování s Fíkem v rámci Medového odpoledne, '
        'koupaliště a výstava kudlanek v Chomutově. KZK zároveň na svém webu zveřejňuje přihlášku do '
        '<strong>Tanečních pro mládež 2026</strong>; zájemci by měli aktuální dostupnost míst zkontrolovat '
        'přímo v přihláškovém formuláři.</p>'
    )
    text = replace_once(text, old_children, new_children, "rodinné tipy v článku")

    text = replace_once(
        text,
        '<div class="sidebox"><h3>Rychlý výběr</h3><ul><li>Čtvrtek: módní show</li><li>Pátek: DIP a DJ Phantom na Liďáku</li><li>Sobota: GOLF na Liďáku, ARG U Soudku nebo Night Run Most</li><li>Neděle: Medové odpoledne</li></ul></div>',
        '<div class="sidebox"><h3>Rychlý výběr</h3><ul><li>Čtvrtek: módní show</li><li>Pátek: DIP a DJ Phantom na Liďáku</li><li>Sobota přes den: pohádkový zámek Poláky</li><li>Sobota večer: GOLF, ARG nebo Night Run Most</li><li>Neděle: Medové odpoledne</li></ul></div>',
        "rychlý výběr",
    )
    text = replace_once(
        text,
        '<div class="sidebox"><h3>Pro rodiny</h3><p>Tlapková patrola v kině, Putování s Fíkem, obě koupaliště a výstava kudlanek v Zooparku Chomutov.</p></div>',
        '<div class="sidebox"><h3>Pro rodiny</h3><p>Pohádkové prohlídky zámku Poláky, Tlapková patrola v kině, Putování s Fíkem, obě koupaliště a výstava kudlanek v Zooparku Chomutov.</p></div>',
        "rodinný box",
    )

    source_anchor = '    <li><a href="https://www.zamek-krasnydvur.cz/">Státní zámek Krásný Dvůr – návštěvní doba a vstupné</a></li>\n'
    polaky_source = '    <li><a href="https://www.zamek-polaky.cz/">Zámek Poláky – kulturní program, návštěvní doba a kontakty</a></li>\n'
    if "Zámek Poláky – kulturní program" not in text:
        text = replace_once(text, source_anchor, polaky_source + source_anchor, "zdroj zámku Poláky")

    text = replace_once(
        text,
        '<p><small>Stav ověření a poslední aktualizace: úterý 4. srpna 2026 v 6:15. U venkovních akcí, koupališť a restaurací se může provoz změnit podle počasí nebo rozhodnutí pořadatele.</small></p>',
        '<p><small>Stav ověření a poslední aktualizace: úterý 4. srpna 2026 ve 20:25. U venkovních akcí, koupališť a restaurací se může provoz změnit podle počasí nebo rozhodnutí pořadatele.</small></p>',
        "stav ověření",
    )

    write_text(ARTICLE, text)


def update_regional_monitoring() -> None:
    data = json.loads(REGIONAL.read_text(encoding="utf-8"))
    sources = data.setdefault("namedInstitutionsAndEventSources", [])
    existing = next((item for item in sources if isinstance(item, dict) and item.get("name") == "Zámek Poláky"), None)
    payload = {
        "name": "Zámek Poláky",
        "url": OFFICIAL_URL,
        "category": "culture",
        "monitorUrls": [OFFICIAL_URL, FACEBOOK_URL, INSTAGRAM_URL],
        "monitoringNote": "Kontrolovat kulturní program, změny termínů, vstupné a nové veřejné pozvánky; významné rodinné a historické akce zařazovat do týdenního přehledu pro Kadaň.",
        "verifiedAt": "2026-08-04",
    }
    if existing is None:
        sources.append(payload)
    else:
        existing.update(payload)
    data["updatedAt"] = "2026-08-04"
    write_text(REGIONAL, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    update_article()
    update_regional_monitoring()
    print(f"Doplněna akce {EVENT_ID} a rozšířen monitoring zámku Poláky.")


if __name__ == "__main__":
    main()
