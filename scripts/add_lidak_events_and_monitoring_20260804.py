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
MODIFIED = "2026-08-04T06:15:00+02:00"

OFFICIAL_URL = "https://restaurant-and-pub-lidak.eatbu.com/?lang=cs"
FACEBOOK_URL = "https://www.facebook.com/lidovydumkadan"
INSTAGRAM_URL = "https://www.instagram.com/restaurant_pub_lidak/"
SEARCH_URL = "https://www.bing.com/search?q=%22Li%C4%8F%C3%A1k+Kada%C5%88%22+akce+program"


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
        '<meta property="article:modified_time" content="2026-08-03T13:20:00+02:00">',
        f'<meta property="article:modified_time" content="{MODIFIED}">',
        "article:modified_time",
    )
    text = replace_once(
        text,
        '"dateModified":"2026-08-03T13:20:00+02:00"',
        f'"dateModified":"{MODIFIED}"',
        "schema dateModified",
    )

    old_description = (
        "Ověřený přehled veřejných akcí a volnočasových možností na týden 3.–9. srpna 2026: "
        "módní show, pouliční dixieland, Medové odpoledne, kino, výstavy, koupání a Night Run v Mostě."
    )
    new_description = (
        "Ověřený přehled akcí na týden 3.–9. srpna 2026: módní show, dixieland, hudební víkend "
        "na Liďáku, ARG U Soudku, Medové odpoledne, kino, výstavy, koupání a Night Run v Mostě."
    )
    text = text.replace(old_description, new_description)
    text = replace_once(
        text,
        '<meta name="twitter:description" content="Módní show, dixieland, Medové odpoledne, čtyři filmy, výstavy, koupaliště a Night Run v Mostě.">',
        '<meta name="twitter:description" content="Módní show, dixieland, hudební víkend na Liďáku, ARG U Soudku, Medové odpoledne, kino a Night Run v Mostě.">',
        "twitter description",
    )

    old_lead = (
        '<p class="leadtext">Nadcházející týden přinese do Kadaně módní přehlídku pod širým nebem, '
        'páteční dixieland na Studentském náměstí, sobotní hudební večer s ARG v Pivnici U Soudku a '
        'nedělní Medové odpoledne ve františkánské zahradě. Kino Hvězda nabídne čtyři projekce, pokračuje '
        'šest výstav a při horkém počasí zůstávají hlavními cíli obě koupaliště. Pro výjezd vybíráme výstavu '
        'kudlanek v chomutovském zooparku, Krásný Dvůr a velký Night Run v Mostě.</p>'
    )
    new_lead = (
        '<p class="leadtext">Nadcházející týden přinese do Kadaně módní přehlídku pod širým nebem, '
        'páteční dixieland na Studentském náměstí, páteční a sobotní hudební program na Liďáku, sobotní '
        'večer s ARG v Pivnici U Soudku a nedělní Medové odpoledne ve františkánské zahradě. Kino Hvězda '
        'nabídne čtyři projekce, pokračuje šest výstav a při horkém počasí zůstávají hlavními cíli obě '
        'koupaliště. Pro výjezd vybíráme výstavu kudlanek v chomutovském zooparku, Krásný Dvůr a velký '
        'Night Run v Mostě.</p>'
    )
    text = replace_once(text, old_lead, new_lead, "úvodní odstavec")

    text = replace_once(
        text,
        '<div class="hero-visual"><strong>Čtyři veřejné akce v Kadani, čtyři filmy, šest výstav, dvě koupaliště a sobotní běžecký večer v Mostě. Nově jsme doplnili hudební večer s ARG v Pivnici U Soudku.</strong></div>',
        '<div class="hero-visual"><strong>Šest veřejných akcí v Kadani, čtyři filmy, šest výstav, dvě koupaliště a sobotní běžecký večer v Mostě. Nově jsme doplnili páteční a sobotní hudební program na Liďáku.</strong></div>',
        "souhrnný vizuál",
    )
    text = replace_once(
        text,
        '<div class="numbers"><div><b>4</b><span>hlavní akce přímo v Kadani</span></div>',
        '<div class="numbers"><div><b>6</b><span>hlavních akcí přímo v Kadani</span></div>',
        "počet akcí",
    )

    friday_anchor = (
        '  <div class="event"><time datetime="2026-08-07T18:00:00+02:00">PÁTEK 7. 8. · 18:00</time>'
        '<h3>Hudba za rohem: DIP</h3><p><strong>Studentské náměstí, centrum Kadaně.</strong> Další díl '
        'pravidelné série pouličních koncertů přiveze kapelu DIP a dixieland. Jde o venkovní program; při '
        'nepříznivém počasí doporučujeme ověřit změnu místa či zrušení u KZK. Na veřejné stránce není uveden '
        'prodej vstupenek.</p><p><a href="https://www.kultura-kadan.cz/dre-cs/75526-hudba-za-rohem-dip.html">'
        'Oficiální záznam KZK</a></p></div>\n'
    )
    lidak_events = (
        '  <div class="event" data-event-id="lidak-dj-phantom-20260807"><time datetime="2026-08-07T17:00:00+02:00">PÁTEK 7. 8. · 17:00–22:00</time>'
        '<h3>The Best of Rock, Metal &amp; Punk s DJ Phantomem</h3><p><strong>Liďák Irish Pub &amp; Restaurant, Žitná 893, Kadaň.</strong> '
        'Hudební večer na letní zahrádce nabídne výběr rocku, metalu a punku. Vstupné je 25 Kč. Pořadatel '
        'avizuje také občerstvení a Jameson Happy Hour, při níž návštěvník ke koupenému panáku dostane druhý zdarma. '
        'Rezervace jsou možné na telefonu 704 252 637.</p><p><em>Doplněno 4. srpna podle veřejné pozvánky pořadatele.</em></p></div>\n'
        '  <div class="event" data-event-id="lidak-golf-20260808"><time datetime="2026-08-08T17:00:00+02:00">SOBOTA 8. 8. · 17:00–22:00</time>'
        '<h3>Hudební srpnové léto na Liďáku s kapelou GOLF</h3><p><strong>Liďák Irish Pub &amp; Restaurant, Žitná 893, Kadaň.</strong> '
        'K tanci a poslechu zahraje lounská kapela GOLF. Vstupné je 25 Kč. Připravené bude občerstvení a '
        'Jameson Happy Hour; rezervace jsou možné na telefonu 704 252 637.</p><p><em>Doplněno 4. srpna podle '
        'veřejné pozvánky pořadatele.</em></p></div>\n'
    )
    if 'data-event-id="lidak-dj-phantom-20260807"' not in text:
        text = replace_once(text, friday_anchor, friday_anchor + lidak_events, "páteční akce pro vložení Liďáku")

    text = replace_once(
        text,
        '<div class="sidebox"><h3>Rychlý výběr</h3><ul><li>Čtvrtek: módní show</li><li>Pátek: dixieland DIP</li><li>Sobota: Night Run Most</li><li>Neděle: Medové odpoledne</li></ul></div>',
        '<div class="sidebox"><h3>Rychlý výběr</h3><ul><li>Čtvrtek: módní show</li><li>Pátek: DIP a DJ Phantom na Liďáku</li><li>Sobota: GOLF na Liďáku, ARG U Soudku nebo Night Run Most</li><li>Neděle: Medové odpoledne</li></ul></div>',
        "rychlý výběr",
    )

    source_anchor = '    <li><a href="https://www.kinokadan.cz/">Kino Hvězda Kadaň – program a vstupenky</a></li>\n'
    lidak_source = f'    <li><a href="{OFFICIAL_URL}">Liďák Kadaň – oficiální web, kontakt a rezervace</a></li>\n'
    if "Liďák Kadaň – oficiální web" not in text:
        text = replace_once(text, source_anchor, source_anchor + lidak_source, "zdroj Liďáku")

    text = replace_once(
        text,
        '<p><small>Stav ověření: neděle 2. srpna 2026 před polednem. U venkovních akcí, koupališť a restaurací se může provoz změnit podle počasí nebo rozhodnutí pořadatele.</small></p>',
        '<p><small>Stav ověření a poslední aktualizace: úterý 4. srpna 2026 v 6:15. U venkovních akcí, koupališť a restaurací se může provoz změnit podle počasí nebo rozhodnutí pořadatele.</small></p>',
        "stav ověření",
    )

    write_text(ARTICLE, text)


def update_sources() -> None:
    data = json.loads(CITY_SOURCES.read_text(encoding="utf-8"))
    sources = data.setdefault("sources", [])
    names = {item.get("name") for item in sources if isinstance(item, dict)}
    additions = [
        {"name": "Liďák Kadaň – oficiální web", "url": OFFICIAL_URL, "category": "Kultura a volný čas"},
        {"name": "Liďák Kadaň – Facebook", "url": FACEBOOK_URL, "category": "Kultura a volný čas – sociální zdroje"},
        {"name": "Liďák Kadaň – Instagram", "url": INSTAGRAM_URL, "category": "Kultura a volný čas – sociální zdroje"},
        {"name": "Sociální monitoring – Liďák Kadaň a nové akce", "url": SEARCH_URL, "category": "Kultura a volný čas – sociální zdroje"},
    ]
    for item in additions:
        if item["name"] not in names:
            sources.append(item)
    data["updatedAt"] = "2026-08-04"
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
    existing = next((item for item in all_items if item.get("name") == "Liďák Kadaň"), None)
    payload = {
        "name": "Liďák Kadaň",
        "description": "Restaurace, pub a letní zahrádka, která pořádá hudební a společenské akce; sledovat web, Facebook, Instagram a veřejné pozvánky.",
        "address": "Žitná 893, 432 01 Kadaň",
        "url": OFFICIAL_URL,
        "monitorUrls": [OFFICIAL_URL, FACEBOOK_URL, INSTAGRAM_URL, SEARCH_URL],
    }
    if existing is not None:
        existing.update(payload)
    else:
        target = next(
            (group for group in data.get("groups", []) if isinstance(group, dict) and group.get("name") == "Kultura, památky a volný čas"),
            None,
        )
        if target is None:
            raise RuntimeError("Nenalezena skupina Kultura, památky a volný čas")
        target.setdefault("items", []).append(payload)
    data["updatedAt"] = "2026-08-04"
    write_text(ORGANIZATIONS, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def update_registry() -> None:
    if not REGISTRY.exists():
        return
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for item in data.get("articles", []):
        if isinstance(item, dict) and item.get("url") == URL:
            item["modified_at"] = MODIFIED
            organizations = item.setdefault("organizations", [])
            if "Liďák Kadaň" not in organizations:
                organizations.append("Liďák Kadaň")
            cases = item.setdefault("cases", [])
            for case in (
                "DJ Phantom na Liďáku – 7. srpna 2026",
                "Kapela GOLF na Liďáku – 8. srpna 2026",
            ):
                if case not in cases:
                    cases.append(case)
            break
    write_text(REGISTRY, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    update_article()
    update_sources()
    update_organizations()
    update_registry()

    article = ARTICLE.read_text(encoding="utf-8")
    assert 'data-event-id="lidak-dj-phantom-20260807"' in article
    assert 'data-event-id="lidak-golf-20260808"' in article
    assert "Šest veřejných akcí v Kadani" in article
    assert "Liďák Kadaň – oficiální web" in article
    assert MODIFIED in article
    print("Doplněny dvě víkendové akce Liďáku a přidány zdroje do kulturního monitoringu.")


if __name__ == "__main__":
    main()
