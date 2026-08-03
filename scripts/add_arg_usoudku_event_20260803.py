#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-3-9-srpna-2026.html"
ORGANIZATIONS = ROOT / "data" / "organizations.json"
CITY_SOURCES = ROOT / "data" / "city-sources.json"
REGISTRY = ROOT / "data" / "published-content-index.json"
URL = "https://nasekadan.cz/clanky/kam-v-kadani-a-okoli-3-9-srpna-2026.html"
MODIFIED = "2026-08-03T13:20:00+02:00"

VENUE_URL = "https://www.pivnidenicek.cz/restaurace-a-hospody/ceska-republika/ustecky-kraj/chomutov/kadan/47163-u-soudku"
SEARCH_VENUE = "https://www.bing.com/search?q=%22Pivnice+U+Soudku%22+Kada%C5%88"
SEARCH_ARG = "https://www.bing.com/search?q=%22ARG%22+%22Kada%C5%88%22+hudba"


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise RuntimeError(f"Nenalezen očekávaný blok: {label}")
    return text.replace(old, new, 1)


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '<meta property="article:modified_time" content="2026-08-02T12:00:00+02:00">',
        f'<meta property="article:modified_time" content="{MODIFIED}">',
        "article:modified_time",
    )
    text = replace_once(
        text,
        '"dateModified":"2026-08-02T12:00:00+02:00"',
        f'"dateModified":"{MODIFIED}"',
        "schema dateModified",
    )

    old_lead = (
        '<p class="leadtext">Nadcházející týden přinese do Kadaně módní přehlídku pod širým nebem, '
        'páteční dixieland na Studentském náměstí a nedělní Medové odpoledne ve františkánské zahradě. '
        'Kino Hvězda nabídne čtyři projekce, pokračuje šest výstav a při horkém počasí zůstávají hlavními '
        'cíli obě koupaliště. Pro výjezd vybíráme výstavu kudlanek v chomutovském zooparku, Krásný Dvůr '
        'a velký Night Run v Mostě.</p>'
    )
    new_lead = (
        '<p class="leadtext">Nadcházející týden přinese do Kadaně módní přehlídku pod širým nebem, '
        'páteční dixieland na Studentském náměstí, sobotní hudební večer s ARG v Pivnici U Soudku a '
        'nedělní Medové odpoledne ve františkánské zahradě. Kino Hvězda nabídne čtyři projekce, pokračuje '
        'šest výstav a při horkém počasí zůstávají hlavními cíli obě koupaliště. Pro výjezd vybíráme výstavu '
        'kudlanek v chomutovském zooparku, Krásný Dvůr a velký Night Run v Mostě.</p>'
    )
    text = replace_once(text, old_lead, new_lead, "úvodní odstavec")

    text = replace_once(
        text,
        '<div class="hero-visual"><strong>Tři veřejné akce v Kadani, čtyři filmy, šest výstav, dvě koupaliště a sobotní běžecký večer v Mostě. Vše ověřeno pro týden od pondělí 3. do neděle 9. srpna.</strong></div>',
        '<div class="hero-visual"><strong>Čtyři veřejné akce v Kadani, čtyři filmy, šest výstav, dvě koupaliště a sobotní běžecký večer v Mostě. Nově jsme doplnili hudební večer s ARG v Pivnici U Soudku.</strong></div>',
        "souhrnný vizuál",
    )
    text = replace_once(
        text,
        '<div class="numbers"><div><b>3</b><span>hlavní akce přímo v Kadani</span></div>',
        '<div class="numbers"><div><b>4</b><span>hlavní akce přímo v Kadani</span></div>',
        "počet akcí",
    )

    friday = (
        '  <div class="event"><time datetime="2026-08-07T18:00:00+02:00">PÁTEK 7. 8. · 18:00</time>'
        '<h3>Hudba za rohem: DIP</h3><p><strong>Studentské náměstí, centrum Kadaně.</strong> Další díl '
        'pravidelné série pouličních koncertů přiveze kapelu DIP a dixieland. Jde o venkovní program; při '
        'nepříznivém počasí doporučujeme ověřit změnu místa či zrušení u KZK. Na veřejné stránce není uveden '
        'prodej vstupenek.</p><p><a href="https://www.kultura-kadan.cz/dre-cs/75526-hudba-za-rohem-dip.html">'
        'Oficiální záznam KZK</a></p></div>\n'
    )
    saturday = (
        '  <div class="event"><time datetime="2026-08-08T18:00:00+02:00">SOBOTA 8. 8. · OD 18:00</time>'
        '<h3>Na plný pecky s ARG</h3><p><strong>Pivnice U Soudku, Kadaň.</strong> Hudební večer s kapelou '
        'ARG. Veřejná pozvánka zve návštěvníky k tanci, posezení a občerstvení. Začátek je v 18:00; cena '
        'vstupu ani případná rezervace v pozvánce uvedeny nebyly.</p><p><em>Doplněno 3. srpna ve 13:20 podle '
        'čerstvé veřejné pozvánky zveřejněné ve skupině Kadaň – otevřené fórum.</em></p></div>\n'
    )
    if 'data-event-id="arg-u-soudku-20260808"' not in text:
        saturday = saturday.replace('<div class="event">', '<div class="event" data-event-id="arg-u-soudku-20260808">', 1)
        text = replace_once(text, friday, friday + saturday, "páteční akce pro vložení soboty")

    write_text(ARTICLE, text)


def update_sources() -> None:
    data = json.loads(CITY_SOURCES.read_text(encoding="utf-8"))
    sources = data.setdefault("sources", [])
    names = {item.get("name") for item in sources if isinstance(item, dict)}
    additions = [
        {
            "name": "Pivnice U Soudku Kadaň – veřejné informace",
            "url": VENUE_URL,
            "category": "Kultura a volný čas",
        },
        {
            "name": "Sociální monitoring – Pivnice U Soudku Kadaň",
            "url": SEARCH_VENUE,
            "category": "Kultura a volný čas – sociální zdroje",
        },
        {
            "name": "Sociální monitoring – ARG a hudba v Kadani",
            "url": SEARCH_ARG,
            "category": "Kultura a volný čas – sociální zdroje",
        },
    ]
    for item in additions:
        if item["name"] not in names:
            sources.append(item)
    data["updatedAt"] = "2026-08-03"
    write_text(CITY_SOURCES, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def update_organizations() -> None:
    data = json.loads(ORGANIZATIONS.read_text(encoding="utf-8"))
    all_items = [
        item
        for group in data.get("groups", [])
        if isinstance(group, dict)
        for item in group.get("items", [])
        if isinstance(item, dict)
    ]
    if any(item.get("name") == "Pivnice U Soudku Kadaň" for item in all_items):
        return
    target = next(
        (group for group in data.get("groups", []) if isinstance(group, dict) and group.get("name") == "Kultura, památky a volný čas"),
        None,
    )
    if target is None:
        raise RuntimeError("Nenalezena skupina Kultura, památky a volný čas")
    target.setdefault("items", []).append(
        {
            "name": "Pivnice U Soudku Kadaň",
            "description": "Místní pivnice a pořadatel hudebních večerů; pozvánky se objevují zejména na Facebooku a v místních veřejných skupinách.",
            "address": "Poštovní 842, Kadaň",
            "url": VENUE_URL,
            "monitorUrls": [VENUE_URL, SEARCH_VENUE, SEARCH_ARG],
        }
    )
    data["updatedAt"] = "2026-08-03"
    write_text(ORGANIZATIONS, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def update_registry() -> None:
    if not REGISTRY.exists():
        return
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for item in data.get("articles", []):
        if isinstance(item, dict) and item.get("url") == URL:
            item["modified_at"] = MODIFIED
            organizations = item.setdefault("organizations", [])
            if "Pivnice U Soudku Kadaň" not in organizations:
                organizations.append("Pivnice U Soudku Kadaň")
            cases = item.setdefault("cases", [])
            if "Na plný pecky s ARG – 8. srpna 2026" not in cases:
                cases.append("Na plný pecky s ARG – 8. srpna 2026")
            break
    write_text(REGISTRY, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    update_article()
    update_sources()
    update_organizations()
    update_registry()

    article = ARTICLE.read_text(encoding="utf-8")
    assert 'data-event-id="arg-u-soudku-20260808"' in article
    assert "Na plný pecky s ARG" in article
    assert "Čtyři veřejné akce v Kadani" in article
    assert MODIFIED in article
    print("Doplněna akce ARG U Soudku a rozšířen monitoring sociálních zdrojů.")


if __name__ == "__main__":
    main()
