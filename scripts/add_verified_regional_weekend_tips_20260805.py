#!/usr/bin/env python3
from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-3-9-srpna-2026.html"
REGISTRY = ROOT / "data" / "published-content-index.json"
ARTICLE_URL = "https://nasekadan.cz/clanky/kam-v-kadani-a-okoli-3-9-srpna-2026.html"
MODIFIED = "2026-08-05T13:59:00+02:00"

DESCRIPTION = (
    "Ověřený přehled akcí na 3.–9. srpna 2026: Kadaň, Jirkov, Archeologické léto v Bílině, "
    "Perseidy ve Stranné, festival ve Spořicích, Večerní věž v Lounech, Bitva Budyně, "
    "exoti v Libochovicích a pouť v Horním Jiřetíně."
)
TWITTER_DESCRIPTION = (
    "Kam o víkendu: Bílina, Stranná, Spořice, Louny, Budyně, Libochovice, Horní Jiřetín i Kadaň."
)
LEAD = (
    "Týdenní přehled jsme rozšířili o sedm ověřených regionálních tipů. V pátek lze vyrazit na "
    "Archeologické léto do Bíliny nebo na Večerní věž v Lounech. Sobota nabídne Perseidy s vínem ve "
    "Stranné, multižánrový festival ve Spořicích, velkou středověkou Bitvu Budyně, výstavu exotického "
    "ptactva v Libochovicích a městské slavnosti s poutí v Horním Jiřetíně. V přehledu samozřejmě "
    "zůstávají také akce v Kadani, Jirkově, na zámku Poláky, program Kina Hvězda, koupaliště a Night Run v Mostě."
)
HERO = (
    "Kadaň a Jirkov doplňuje sedm ověřených výjezdních tipů: archeologie, hvězdy a víno, velké koncerty, "
    "večerní věž, středověká bitva, exotické ptactvo a městská pouť."
)

SOURCES = {
    "archeo": "https://www.archeologickeleto.cz/",
    "brezno": "https://www.obecbrezno.cz/vsechny-akce/",
    "epydemye": "https://www.epydemye.cz/events/next/2026",
    "poetika": "https://poetikamusic.cz/",
    "louny": "https://mojelouny.cz/akce/stitek/akce-o-vikendu/",
    "budyne": "https://www.bitva-budyne.cz/pro-navstevniky/",
    "libochovice": "https://www.zamek-libochovice.cz/cs/akce/132164-vystava-exotickeho-ptactva-zamek-libochovice-2026",
    "jiretin": "https://www.hornijiretin.cz/kultura-a-sport/",
}


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_meta(text: str, attr: str, key: str, value: str) -> str:
    patterns = (
        rf'<meta\s+{attr}="{re.escape(key)}"\s+content="[^"]*"\s*/?>',
        rf'<meta\s+content="[^"]*"\s+{attr}="{re.escape(key)}"\s*/?>',
    )
    replacement = f'<meta {attr}="{key}" content="{escape(value, quote=True)}">'
    for pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            return re.sub(pattern, replacement, text, count=1, flags=re.I)
    raise RuntimeError(f"Nenalezen meta údaj {key}")


def patch_json_ld(text: str) -> str:
    changed = False

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        prefix, raw, suffix = match.group(1), match.group(2), match.group(3)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            data["description"] = DESCRIPTION
            data["dateModified"] = MODIFIED
            changed = True
        return prefix + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + suffix

    result = re.sub(
        r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        repl,
        text,
        flags=re.S,
    )
    if not changed:
        raise RuntimeError("Nenalezen NewsArticle JSON-LD")
    return result


def event(event_id: str, time_html: str, heading: str, body: str, source_url: str, source_label: str) -> str:
    return (
        f'  <div class="event" data-event-id="{event_id}">{time_html}<h3>{heading}</h3>'
        f'{body}<p><a href="{source_url}">{source_label}</a></p>'
        '<p><em>Doplněno 5. srpna ve 13:59 po kontrole veřejných a pořadatelských zdrojů.</em></p></div>\n'
    )


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    text = replace_meta(text, "name", "description", DESCRIPTION)
    text = replace_meta(text, "property", "og:description", DESCRIPTION)
    text = replace_meta(text, "name", "twitter:description", TWITTER_DESCRIPTION)
    text = replace_meta(text, "property", "article:modified_time", MODIFIED)
    text = patch_json_ld(text)

    text = re.sub(
        r'<p class="tag">.*?</p>',
        '<p class="tag">KULTURA · VOLNÝ ČAS · KADAŇ A REGION · AKTUALIZOVÁNO 5. SRPNA 2026 · 13:59</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p class="leadtext">.*?</p>',
        f'<p class="leadtext">{escape(LEAD)}</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<div class="hero-visual"><strong>.*?</strong></div>',
        f'<div class="hero-visual"><strong>{escape(HERO)}</strong></div>',
        text,
        count=1,
        flags=re.S,
    )

    archeo = event(
        "bilina-archeologicke-leto-20260807",
        '<time datetime="2026-08-07T14:00:00+02:00">PÁTEK 7. 8. · 14:00</time>',
        "Archeologické léto na hradišti Bílina",
        '<p><strong>Sraz na Mírovém náměstí v Bílině.</strong> Archeolog Daniel Dvořáček provede návštěvníky '
        'středověkým hradištěm. Trasa má obtížnost 2 z 5 a vede po zpevněných cestách bez výrazného převýšení. '
        'Akce je součástí celostátního Archeologického léta; před cestou doporučujeme v rezervačním systému '
        'ověřit volná místa.</p>',
        SOURCES["archeo"],
        "Archeologické léto – oficiální program a rezervace",
    )
    perseidy = event(
        "stranna-perseidy-vino-20260808",
        '<time datetime="2026-08-08T16:00:00+02:00">SOBOTA 8. 8. · 16:00–22:00</time>',
        "Perseidy s vínem ve Stranné",
        '<p><strong>Stranná u Nechranické přehrady.</strong> Večer spojí vína místních vinařů, občerstvení '
        'restaurace Republika a při vhodném počasí pozorování meteorického roje Perseid. Obec Březno '
        'zajišťuje kyvadlovou dopravu z Března; aktuální odjezdy doporučujeme zkontrolovat před cestou.</p>',
        SOURCES["brezno"],
        "Obec Březno – oficiální kalendář akcí",
    )
    sporice = event(
        "sporice-multizanrovy-festival-20260808",
        '<time datetime="2026-08-08T12:30:00+02:00">SOBOTA 8. 8. · OD 12:30</time>',
        "Multižánrový festival ve Spořicích",
        '<p><strong>Areál u koupaliště ve Spořicích.</strong> Regionální program uvádí odpolední hudební '
        'festival pro široké publikum. Turné kalendáře interpretů potvrzují vystoupení skupin Epydemye, '
        'Poetika, Polemic a N.O.H.A.; Epydemye má uvedený čas 14:45 a Poetika 16:00. Kompletní pořadí, '
        'vstupné a případné změny doporučujeme ověřit u pořadatele.</p>',
        SOURCES["epydemye"],
        "Epydemye – potvrzený termín koncertu ve Spořicích",
    )

    nearby_anchor = '  <div class="event"><h3>Výstava kudlanek v Zooparku Chomutov</h3>'
    if nearby_anchor not in text:
        raise RuntimeError("Nenalezeno místo pro regionální tipy")
    nearby_blocks = ""
    for marker, block in (
        ("bilina-archeologicke-leto-20260807", archeo),
        ("stranna-perseidy-vino-20260808", perseidy),
        ("sporice-multizanrovy-festival-20260808", sporice),
    ):
        if f'data-event-id="{marker}"' not in text:
            nearby_blocks += block
    if nearby_blocks:
        text = text.replace(nearby_anchor, nearby_blocks + nearby_anchor, 1)

    louny = event(
        "louny-vecerni-vez-20260807",
        '<time datetime="2026-08-07T19:00:00+02:00">PÁTEK 7. 8. · 19:00–21:00</time>',
        "Večerní věž kostela sv. Mikuláše v Lounech",
        '<p>Návštěvníci mohou vystoupat na ochoz věže, prohlédnout si byt hlásného a dobový betlém a '
        'pozorovat večerní Louny i České středohoří. Vstupné je 50 Kč pro dospělé, 30 Kč pro děti a seniory '
        'a 100 Kč za rodinné vstupné.</p>',
        SOURCES["louny"],
        "Město Louny – oficiální komunitní kalendář",
    )
    budyne = event(
        "bitva-budyne-20260808",
        '<time datetime="2026-08-08T10:00:00+02:00">SOBOTA 8. 8. · 10:00–17:00</time>',
        "Bitva Budyně: dvě bitvy, vojenský tábor a středověké tržiště",
        '<p><strong>Vodní hrad Budyně nad Ohří.</strong> Komentovaná ukázka výcviku vojska začne v 11:00, '
        'hlavní bitvy proběhnou od 13:00 a 16:00. Celodenní program doplní dobová hudba a tanec, tržiště, '
        'středověká kuchyně, zbrojnice, prohlídky vojenského ležení a šerm. Vstupné: dospělí 250 Kč, děti '
        'od sedmi let 150 Kč, rodinné 600 Kč; malé děti zdarma.</p>',
        SOURCES["budyne"],
        "Bitva Budyně – oficiální program pro návštěvníky",
    )
    libochovice = event(
        "libochovice-exoticke-ptactvo-20260808",
        '<time datetime="2026-08-08T09:00:00+02:00">SOBOTA 8. 8. A NEDĚLE 9. 8. · 9:00–15:00</time>',
        "Výstava exotického ptactva na zámku Libochovice",
        '<p><strong>Produkční skleník zámku Libochovice.</strong> Dvoudenní výstava představí pestré '
        'exotické ptactvo v zámeckém prostředí. Pořadatel uvádí vstupné 30 Kč a snížené 10 Kč.</p>',
        SOURCES["libochovice"],
        "Zámek Libochovice – oficiální detail výstavy",
    )
    jiretin = event(
        "horni-jiretin-pout-20260808",
        '<time datetime="2026-08-08T10:00:00+02:00">SOBOTA 8. 8. · OD 10:00</time>',
        "Městské slavnosti a pouť v Horním Jiřetíně",
        '<p>Hlavní sobotní program nabídne čtyři hudební scény. Vystoupí Pokáč, The Apples, Beatles Revival '
        'Kladno, Michal Šindelář a další. Součástí budou pouťové atrakce, rytířský tábor a historický šerm '
        'skupiny Fictum, divadlo, hry pro děti, prohlídky kostela a kavárna na jeho balkonech. Slavnosti '
        'pokračují také v neděli 9. srpna.</p>',
        SOURCES["jiretin"],
        "Město Horní Jiřetín – oficiální program slavností",
    )

    big_anchor = '  <div class="event"><time datetime="2026-08-08T15:00:00+02:00">SOBOTA 8. 8. · 15:00–22:30</time><h3>NN Night Run Most</h3>'
    if big_anchor not in text:
        raise RuntimeError("Nenalezeno místo pro velké výjezdní akce")
    big_blocks = ""
    for marker, block in (
        ("louny-vecerni-vez-20260807", louny),
        ("bitva-budyne-20260808", budyne),
        ("libochovice-exoticke-ptactvo-20260808", libochovice),
        ("horni-jiretin-pout-20260808", jiretin),
    ):
        if f'data-event-id="{marker}"' not in text:
            big_blocks += block
    if big_blocks:
        text = text.replace(big_anchor, big_blocks + big_anchor, 1)

    quick_pattern = re.compile(r'<div class="sidebox"><h3>Rychlý výběr</h3><ul>.*?</ul></div>', re.S)
    quick = (
        '<div class="sidebox"><h3>Rychlý výběr</h3><ul>'
        '<li>Středa: komentovaná procházka Jirkovem</li>'
        '<li>Čtvrtek: pohádka v jirkovské synagoze nebo módní show v Kadani</li>'
        '<li>Pátek: Bílina, Večerní věž Louny, DIP nebo Liďák</li>'
        '<li>Sobota: Spořice, Stranná, Budyně, Libochovice, Horní Jiřetín, Poláky nebo Night Run</li>'
        '<li>Neděle: Medové odpoledne a exoti v Libochovicích</li>'
        '</ul></div>'
    )
    if not quick_pattern.search(text):
        raise RuntimeError("Nenalezen rychlý výběr")
    text = quick_pattern.sub(quick, text, count=1)

    children_pattern = re.compile(r'<h2 id="deti">4\) Děti, školy a přihlášky</h2>\s*<p>.*?</p>', re.S)
    children = (
        '<h2 id="deti">4) Děti, školy a přihlášky</h2>\n'
        '<p>Pro děti jsou tento týden nejjistější volbou čtvrteční pohádka v jirkovské synagoze, sobotní '
        'pohádkové prohlídky zámku Poláky, Bitva Budyně, výstava exotického ptactva v Libochovicích, '
        'Jiřetínská pouť, koupaliště, Zoopark Chomutov a mládeži přístupné projekce Kina Hvězda. KZK zároveň '
        'zveřejňuje přihlášku do <strong>Tanečních pro mládež 2026</strong>; dostupnost míst je třeba '
        'zkontrolovat přímo v přihláškovém formuláři.</p>'
    )
    if not children_pattern.search(text):
        raise RuntimeError("Nenalezena dětská sekce")
    text = children_pattern.sub(children, text, count=1)

    source_anchor = '    <li><a href="https://www.jirkov.cz/volny-cas/kalendar-akci-2/">Město Jirkov – oficiální kalendář akcí</a></li>\n'
    if source_anchor not in text:
        raise RuntimeError("Nenalezen zdrojový seznam")
    source_items = [
        (SOURCES["archeo"], "Archeologické léto – program a rezervace"),
        (SOURCES["brezno"], "Obec Březno – Perseidy ve Stranné"),
        (SOURCES["epydemye"], "Epydemye – turné kalendář a Spořice"),
        (SOURCES["poetika"], "Poetika – turné kalendář a Spořice"),
        (SOURCES["louny"], "Město Louny – Večerní věž"),
        (SOURCES["budyne"], "Bitva Budyně – program a vstupné"),
        (SOURCES["libochovice"], "Zámek Libochovice – výstava exotického ptactva"),
        (SOURCES["jiretin"], "Město Horní Jiřetín – slavnosti a pouť"),
    ]
    additions = ""
    for url, label in source_items:
        if label not in text:
            additions += f'    <li><a href="{url}">{label}</a></li>\n'
    if additions:
        text = text.replace(source_anchor, source_anchor + additions, 1)

    text = re.sub(
        r'<p><small>Stav ověření a poslední aktualizace:.*?</small></p>',
        '<p><small>Stav ověření a poslední aktualizace: středa 5. srpna 2026 ve 13:59. '
        'U venkovních akcí se program může změnit podle počasí nebo rozhodnutí pořadatele.</small></p>',
        text,
        count=1,
        flags=re.S,
    )

    required = [
        "bilina-archeologicke-leto-20260807",
        "stranna-perseidy-vino-20260808",
        "sporice-multizanrovy-festival-20260808",
        "louny-vecerni-vez-20260807",
        "bitva-budyne-20260808",
        "libochovice-exoticke-ptactvo-20260808",
        "horni-jiretin-pout-20260808",
        MODIFIED,
    ]
    for value in required:
        if value not in text:
            raise RuntimeError(f"Po úpravě chybí {value}")

    write(ARTICLE, text)


def update_registry() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    article = next((item for item in data.get("articles", []) if item.get("url") == ARTICLE_URL), None)
    if article is None:
        raise RuntimeError("Kulturní přehled chybí v registru")

    article["modified_at"] = MODIFIED
    article["source_commit"] = "pending-regional-weekend-tips"
    additions = {
        "organizations": [
            "Archeologický ústav AV ČR", "Obec Březno", "Obec Spořice", "Město Louny",
            "Bitva Budyně", "Státní zámek Libochovice", "Město Horní Jiřetín",
        ],
        "places": [
            "Hradiště Bílina", "Stranná", "Spořice", "Kostel sv. Mikuláše v Lounech",
            "Vodní hrad Budyně nad Ohří", "Zámek Libochovice", "Horní Jiřetín",
        ],
        "topics": [
            "Archeologické léto", "Perseidy", "Víno", "Hudební festivaly", "Večerní prohlídky",
            "Historické bitvy", "Exotické ptactvo", "Městské slavnosti a poutě",
        ],
        "cases": [
            "Archeologické léto Bílina 7. srpna 2026",
            "Perseidy ve Stranné 8. srpna 2026",
            "Multižánrový festival Spořice 8. srpna 2026",
            "Večerní věž Louny 7. srpna 2026",
            "Bitva Budyně 8. srpna 2026",
            "Výstava exotického ptactva Libochovice 8.–9. srpna 2026",
            "Městské slavnosti a pouť Horní Jiřetín 8.–9. srpna 2026",
        ],
    }
    for key, values in additions.items():
        bucket = article.setdefault(key, [])
        for value in values:
            if value not in bucket:
                bucket.append(value)

    validation = data.setdefault("validation", {})
    validation["repair_pending_public_verification"] = True
    validation["last_cultural_update"] = {
        "status": "pending_public_verification",
        "updated_url": ARTICLE_URL,
        "modified_at": MODIFIED,
        "events": [
            "bilina-archeologicke-leto-20260807",
            "stranna-perseidy-vino-20260808",
            "sporice-multizanrovy-festival-20260808",
            "louny-vecerni-vez-20260807",
            "bitva-budyne-20260808",
            "libochovice-exoticke-ptactvo-20260808",
            "horni-jiretin-pout-20260808",
        ],
        "excluded_unverified": ["Kokeš fest – Hipodrom Most"],
    }
    data["article_count"] = len(data.get("articles", []))
    write(REGISTRY, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    update_article()
    update_registry()
    print("Sedm ověřených regionálních tipů bylo doplněno do kulturního přehledu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
