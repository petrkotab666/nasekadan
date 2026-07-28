#!/usr/bin/env python3
"""Idempotentně doplní Let It Roll 2026 do aktuálního kulturního přehledu."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f"Nenalezen očekávaný blok: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "<title>Kam v Kadani a okolí od 27. července do 2. srpna: festival, koupání, kino a výlety | Naše Kadaň</title>",
        "<title>Kam v Kadani a okolí od 27. července do 2. srpna: Let It Roll, festivaly, kino a výlety | Naše Kadaň</title>",
        "title",
    )
    text = replace_once(
        text,
        '<meta name="description" content="Přehled akcí a letních tipů v Kadani a okolí na týden od 27. července do 2. srpna 2026: živá hudba na Liďáku, festival čaje, Kino Hvězda, koupaliště, výstavy, historický vlak a galakoncert v Karlových Varech.">',
        '<meta name="description" content="Přehled akcí v Kadani a okolí od 27. července do 2. srpna 2026: Let It Roll u Jezera Most, živá hudba, festival čaje, kino, koupání, historický vlak a další regionální tipy.">',
        "meta description",
    )
    text = replace_once(
        text,
        '<meta property="og:description" content="Café Lingua Romania v RADCE, živá hudba na Liďáku, festival čaje, osm projekcí Kina Hvězda, koupaliště, historický vlak a galakoncert s Karlovarským symfonickým orchestrem.">',
        '<meta property="og:description" content="Let It Roll 2026 u Jezera Most, Café Lingua Romania, živá hudba na Liďáku, festival čaje, Kino Hvězda, koupání, historický vlak a další tipy.">',
        "og description",
    )
    text = text.replace(
        '<meta property="article:modified_time" content="2026-07-28T14:30:00+02:00">',
        '<meta property="article:modified_time" content="2026-07-28T22:30:00+02:00">',
        1,
    )
    text = replace_once(
        text,
        '"description":"Ověřený týdenní přehled veřejných akcí a letních možností v Kadani a širším okolí včetně hudebního večera na Liďáku a významného programu v Karlových Varech.","datePublished":"2026-07-26T12:00:00+02:00","dateModified":"2026-07-28T14:30:00+02:00"',
        '"description":"Ověřený týdenní přehled veřejných akcí v Kadani a širším okolí včetně festivalu Let It Roll 2026 u Jezera Most.","datePublished":"2026-07-26T12:00:00+02:00","dateModified":"2026-07-28T22:30:00+02:00"',
        "schema",
    )
    text = replace_once(
        text,
        "<h1>Kam v Kadani a okolí od 27. července do 2. srpna: festival, koupání, kino a výlety</h1>",
        "<h1>Kam v Kadani a okolí od 27. července do 2. srpna: Let It Roll, festivaly, kino a výlety</h1>",
        "h1",
    )
    text = replace_once(
        text,
        '<p class="leadtext">Nadcházející týden nabídne v Kadani čtvrteční Café Lingua Romania v RADCE, páteční živou hudbu na Liďáku, sobotní festival čaje, osm filmových projekcí, letní výstavy, otevřené památky a dvě možnosti koupání. Přidáváme také výběr akcí z Klášterce, Chomutova, Jirkova, Podbořan, Žatce, Vejprt, okolních zámků a výrazný hudební program v Karlových Varech.</p>',
        '<p class="leadtext">Nadcházející týden nabídne v Kadani Café Lingua Romania, živou hudbu na Liďáku, festival čaje, osm filmových projekcí, letní výstavy, památky a koupání. Největší akcí v dostupném okolí je třídenní festival Let It Roll 2026 u Jezera Most. Přidáváme také tipy z Klášterce, Chomutova, Jirkova, Litvínovska, Podbořan, Žatce, Vejprt, okolních zámků a Karlových Varů.</p>',
        "lead",
    )
    text = replace_once(
        text,
        '<div class="hero-visual"><strong>Mezi hlavní tipy patří čtvrteční Café Lingua Romania v RADCE, páteční hudební večer na Liďáku, sobotní festival čaje, historický motorák do Krušných hor a gala s Karlovarským symfonickým orchestrem.</strong></div>',
        '<div class="hero-visual"><strong>Největším regionálním tipem je Let It Roll 2026 u Jezera Most. Přímo v Kadani následují Café Lingua Romania, hudební večer na Liďáku a sobotní festival čaje.</strong></div>',
        "hero",
    )
    text = replace_once(
        text,
        '<div><b>10</b><span>vybraných tipů z okolí</span></div>',
        '<div><b>11</b><span>vybraných tipů z okolí</span></div>',
        "count",
    )

    if 'data-let-it-roll-2026' not in text:
        anchor = '  <section class="nearby"><p class="distance">Vejprty a Krušné hory · sobota 1. srpna</p>'
        if anchor not in text:
            raise SystemExit("Nenalezen bod pro vložení Let It Roll.")
        block = '''  <section class="nearby regional-highlight" data-let-it-roll-2026><p class="distance">Jezero Most · z Kadaně zhruba do hodiny autem · čtvrtek 30. července až sobota 1. srpna · pouze 18+</p><h3>Let It Roll 2026: tři festivalové noci a světová drum &amp; bassová jména</h3><p>U Jezera Most se od čtvrtka do soboty uskuteční jeden z největších drum &amp; bassových festivalů na světě. Hlavní program nabídne například <strong>Chase &amp; Status</strong>, <strong>Pendulum v živém provedení</strong>, Camo &amp; Krooked B2B Mefjus, Hybrid Minds, Netsky, Wilkinson, Delta Heavy, Fox Stevenson, Kanine, Luude B2B Rova a desítky dalších interpretů.</p><p>Hudební areál je ve čtvrtek otevřen od 12:00 do 1:00, v pátek a v sobotu od 13:00 do 5:00. Festival je bez výjimky přístupný pouze od 18 let. Vstupenky jsou vázané na jméno, nelze je běžně vrátit a pořadatel doporučuje využívat pouze oficiální prodej nebo oficiální přeprodejní systém.</p><p><strong>Místo:</strong> Jezero Most. <strong>Termín:</strong> 30. července až 1. srpna 2026. <a href="https://letitroll.cz/akce/let-it-roll-2026/" target="_blank" rel="noopener noreferrer">Program, harmonogram, mapa a vstupenky na webu pořadatele</a>.</p></section>\n'''
        text = text.replace(anchor, block + anchor, 1)

    text = replace_once(
        text,
        '<p>Samostatné veřejné akce pro sledovaný týden jsme v době uzávěrky nepotvrdili v kalendářích Perštejna, Vilémova, Radonic, Měděnce, Mašťova, Chban, Libědic a Rokle. Prověřili jsme také Most, Litvínov a další větší regionální kalendáře, ale pro tento týden jsme v nich nenašli mimořádnou velkou událost srovnatelnou například s Mosteckou slavností. U přírodního koupání na Nechranicích jsme nenašli dostatečně aktuální jednotný provozní údaj, proto jej neuvádíme jako organizovanou akci ani jako koupaliště se zajištěným dohledem.</p>',
        '<p>Samostatné veřejné akce pro sledovaný týden jsme v době uzávěrky nepotvrdili v kalendářích Perštejna, Vilémova, Radonic, Měděnce, Mašťova, Chban, Libědic a Rokle. Původní formulace, že jsme v Mostě nenašli velkou akci, byla chybná: Let It Roll 2026 je jedním z nejvýznamnějších festivalů celého regionu a do přehledu jsme jej doplnili. Most a Litvínov nyní kontrolujeme také přes samostatné pořadatelské, kulturní a městské zdroje. U přírodního koupání na Nechranicích jsme nenašli dostatečně aktuální jednotný provozní údaj, proto jej neuvádíme jako organizovanou akci ani jako koupaliště se zajištěným dohledem.</p>',
        "correction paragraph",
    )

    if 'data-let-it-roll-source' not in text:
        source_anchor = '    <li><a href="https://www.loucna.eu/obcan/akce-mesta/folk-rock-festival-na-horach-810_95cs.html"'
        source = '    <li data-let-it-roll-source><a href="https://letitroll.cz/akce/let-it-roll-2026/" target="_blank" rel="noopener noreferrer">Let It Roll 2026 – oficiální program, místo, harmonogram a pravidla</a></li>\n'
        if source_anchor not in text:
            raise SystemExit("Nenalezen bod pro zdroj Let It Roll.")
        text = text.replace(source_anchor, source + source_anchor, 1)

    text = text.replace(
        'Aktualizováno v pondělí 27. července 2026 ve 20:29.',
        'Aktualizováno v úterý 28. července 2026 ve 22:30.',
        1,
    )
    text = replace_once(
        text,
        '<div class="sidebox"><h3>Rychlé shrnutí</h3><p><strong>Pátek přináší živou hudbu přímo v Kadani, sobota festival čaje a silný program v okolí.</strong></p><p>Na Liďáku zahrají Adéla a David Prokešovi, na Studentském náměstí proběhne festival čaje a v okolí se konají horalské hry, jízda historického vlaku i koncerty v Karlových Varech.</p><p class="updated">Aktualizováno: 27. 7. 2026 ve 20:29</p></div>',
        '<div class="sidebox"><h3>Rychlé shrnutí</h3><p><strong>Největší akcí týdne v širším okolí je Let It Roll 2026 u Jezera Most.</strong></p><p>Přímo v Kadani se konají Café Lingua Romania, hudební večer na Liďáku a festival čaje. V okolí následují historický vlak, Folk Rock Festival, Chvála medu a koncerty v Karlových Varech.</p><p class="updated">Aktualizováno: 28. 7. 2026 ve 22:30</p></div>',
        "sidebar",
    )

    ARTICLE.write_text(text, encoding="utf-8", newline="\n")
    print("Let It Roll 2026 byl doplněn do kulturního přehledu.")


if __name__ == "__main__":
    main()
