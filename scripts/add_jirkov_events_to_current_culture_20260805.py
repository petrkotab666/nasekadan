#!/usr/bin/env python3
from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "kam-v-kadani-a-okoli-3-9-srpna-2026.html"
REGISTRY = ROOT / "data" / "published-content-index.json"
URL = "https://nasekadan.cz/clanky/kam-v-kadani-a-okoli-3-9-srpna-2026.html"
MODIFIED = "2026-08-05T13:39:00+02:00"

DESC = (
    "Ověřený přehled akcí na týden 3.–9. srpna 2026: Kadaň, komentovaná procházka "
    "centrem Jirkova, pohádka v jirkovské synagoze, zámek Poláky, kino, koupání a Night Run v Mostě."
)
TWITTER_DESC = (
    "Kam 3.–9. srpna: Kadaň, dnešní procházka Jirkovem, pohádka v synagoze, zámek Poláky, kino a Night Run."
)
LEAD = (
    "Nadcházející týden přinese do Kadaně módní přehlídku pod širým nebem, páteční dixieland na "
    "Studentském náměstí, páteční a sobotní hudební program na Liďáku, sobotní večer s ARG v Pivnici "
    "U Soudku a nedělní Medové odpoledne ve františkánské zahradě. Nově jsme doplnili dnešní "
    "komentovanou procházku centrem Jirkova a čtvrteční pohádku O rybáři a rybce v jirkovské synagoze. "
    "Rodinám doporučujeme také sobotní pohádkové prohlídky zámku Poláky. Kino Hvězda nabídne čtyři "
    "projekce, pokračuje šest výstav a při horkém počasí zůstávají hlavními cíli obě koupaliště. "
    "Pro větší výjezd vybíráme Night Run v Mostě."
)
HERO = (
    "Šest veřejných akcí v Kadani, dvě čerstvě doplněné akce v Jirkově, pohádkové prohlídky zámku "
    "Poláky, čtyři filmy, šest výstav, dvě koupaliště a sobotní běžecký večer v Mostě."
)

JIRKOV_CALENDAR = "https://www.jirkov.cz/volny-cas/kalendar-akci-2/"
WALK_URL = (
    "https://www.jirkov.cz/volny-cas/kalendar-akci-2/"
    "komentovana-prochazka-centrem-jirkova-392_185cs4698.html"
)
FAIRYTALE_URL = (
    "https://www.jirkov.cz/volny-cas/kalendar-akci-2/"
    "pohadky-v-synagoze-o-rybari-a-rybce-368_178cs4698.html"
)


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
    return text.replace("</head>", replacement + "\n</head>", 1)


def patch_json_ld(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, raw, suffix = match.group(1), match.group(2), match.group(3)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            data["description"] = DESC
            data["dateModified"] = MODIFIED
        return prefix + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + suffix

    return re.sub(
        r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        repl,
        text,
        flags=re.S,
    )


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    text = replace_meta(text, "name", "description", DESC)
    text = replace_meta(text, "property", "og:description", DESC)
    text = replace_meta(text, "name", "twitter:description", TWITTER_DESC)
    text = replace_meta(text, "property", "article:modified_time", MODIFIED)
    text = patch_json_ld(text)

    text = re.sub(
        r'<p class="tag">.*?</p>',
        '<p class="tag">KULTURA · VOLNÝ ČAS · KADAŇ A REGION · AKTUALIZOVÁNO 5. SRPNA 2026 · 13:39</p>',
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

    walk = (
        '  <div class="event" data-event-id="jirkov-komentovana-prochazka-20260805">'
        '<time datetime="2026-08-05T15:00:00+02:00">STŘEDA 5. 8. · 15:00</time>'
        '<h3>Komentovaná procházka centrem Jirkova</h3>'
        '<p><span class="distance">asi 26 km · přibližně 30 minut autem</span></p>'
        '<p><strong>Sraz u Informačního centra v Jirkově.</strong> Procházka představí památky centra města '
        'a příběhy ukryté za místními sochami, fontánami a historickými budovami. Pořadatel na veřejné '
        'stránce neuvádí cenu vstupného ani nutnost předchozí registrace.</p>'
        f'<p><a href="{WALK_URL}">Oficiální detail města Jirkov</a></p>'
        '<p><em>Doplněno 5. srpna ve 13:39 podle oficiálního kalendáře města Jirkov.</em></p></div>\n'
    )
    fairytale = (
        '  <div class="event" data-event-id="jirkov-pohadka-rybar-rybka-20260806">'
        '<time datetime="2026-08-06T16:00:00+02:00">ČTVRTEK 6. 8. · 16:00</time>'
        '<h3>Pohádky v synagoze: O rybáři a rybce</h3>'
        '<p><span class="distance">asi 26 km · přibližně 30 minut autem</span></p>'
        '<p><strong>Jirkovská synagoga.</strong> Čtvrteční pohádkové odpoledne pro malé i velké nabídne '
        'příběh O rybáři a rybce v podání Dětského divadla Z bedny. Cena vstupného není ve veřejném '
        'kalendáři uvedena, proto ji doporučujeme před cestou ověřit u pořadatele.</p>'
        f'<p><a href="{FAIRYTALE_URL}">Oficiální detail města Jirkov</a></p>'
        '<p><em>Doplněno 5. srpna ve 13:39 podle oficiálního kalendáře města Jirkov.</em></p></div>\n'
    )

    anchor = '  <h2 id="okoli">5) Tipy z blízkého okolí</h2>\n'
    if anchor not in text:
        raise RuntimeError("Nelze najít sekci Tipy z blízkého okolí.")
    blocks = ""
    if 'data-event-id="jirkov-komentovana-prochazka-20260805"' not in text:
        blocks += walk
    if 'data-event-id="jirkov-pohadka-rybar-rybka-20260806"' not in text:
        blocks += fairytale
    if blocks:
        text = text.replace(anchor, anchor + blocks, 1)

    old_children = (
        "Pro děti jsou tento týden nejjistější volbou sobotní pohádkové prohlídky zámku Poláky, dvě "
        "dabované či mládeži přístupné projekce Kina Hvězda, nedělní Putování s Fíkem v rámci Medového "
        "odpoledne, koupaliště a výstava kudlanek v Chomutově."
    )
    new_children = (
        "Pro děti jsou tento týden nejjistější volbou čtvrteční pohádka O rybáři a rybce v jirkovské "
        "synagoze, sobotní pohádkové prohlídky zámku Poláky, dvě dabované či mládeži přístupné projekce "
        "Kina Hvězda, nedělní Putování s Fíkem v rámci Medového odpoledne, koupaliště a výstava kudlanek "
        "v Chomutově."
    )
    if old_children in text:
        text = text.replace(old_children, new_children, 1)

    quick_pattern = re.compile(
        r'<div class="sidebox"><h3>Rychlý výběr</h3><ul>.*?</ul></div>',
        re.S,
    )
    quick = (
        '<div class="sidebox"><h3>Rychlý výběr</h3><ul>'
        '<li>Středa: komentovaná procházka Jirkovem</li>'
        '<li>Čtvrtek: pohádka v jirkovské synagoze nebo módní show v Kadani</li>'
        '<li>Pátek: DIP a DJ Phantom na Liďáku</li>'
        '<li>Sobota přes den: pohádkový zámek Poláky</li>'
        '<li>Sobota večer: GOLF, ARG nebo Night Run Most</li>'
        '<li>Neděle: Medové odpoledne</li>'
        '</ul></div>'
    )
    if not quick_pattern.search(text):
        raise RuntimeError("Nelze najít rychlý výběr.")
    text = quick_pattern.sub(quick, text, count=1)

    source_item = (
        f'    <li><a href="{JIRKOV_CALENDAR}">Město Jirkov – oficiální kalendář akcí</a></li>\n'
    )
    source_anchor = '    <li><a href="https://zoopark.cz/">Zoopark Chomutov – výstava, otevírací doba a ceník</a></li>\n'
    if "Město Jirkov – oficiální kalendář akcí" not in text:
        if source_anchor not in text:
            raise RuntimeError("Nelze najít místo pro zdroj města Jirkov.")
        text = text.replace(source_anchor, source_item + source_anchor, 1)

    text = re.sub(
        r'<p><small>Stav ověření a poslední aktualizace:.*?</small></p>',
        '<p><small>Stav ověření a poslední aktualizace: středa 5. srpna 2026 ve 13:39. '
        'U venkovních akcí, koupališť a restaurací se může provoz změnit podle počasí nebo rozhodnutí '
        'pořadatele.</small></p>',
        text,
        count=1,
        flags=re.S,
    )

    for required in (
        'data-event-id="jirkov-komentovana-prochazka-20260805"',
        'data-event-id="jirkov-pohadka-rybar-rybka-20260806"',
        "Město Jirkov – oficiální kalendář akcí",
        MODIFIED,
    ):
        if required not in text:
            raise RuntimeError(f"Po úpravě chybí: {required}")

    write(ARTICLE, text)


def update_registry() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    article = next(
        (item for item in data.get("articles", []) if isinstance(item, dict) and item.get("url") == URL),
        None,
    )
    if article is None:
        raise RuntimeError("Kulturní přehled chybí v kanonickém registru.")

    article["modified_at"] = MODIFIED
    article["source_commit"] = "pending-jirkov-events-commit"

    for key, values in {
        "organizations": ["Město Jirkov", "Dětské divadlo Z bedny"],
        "places": ["Jirkov", "Informační centrum Jirkov", "Jirkovská synagoga"],
        "cases": [
            "Komentovaná procházka centrem Jirkova 5. srpna 2026",
            "Pohádka O rybáři a rybce v jirkovské synagoze 6. srpna 2026",
        ],
        "topics": ["Jirkov", "Komentované procházky", "Pohádky v synagoze"],
    }.items():
        bucket = article.setdefault(key, [])
        for value in values:
            if value not in bucket:
                bucket.append(value)

    data["article_count"] = len(data.get("articles", []))
    write(REGISTRY, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    update_article()
    update_registry()
    print("Jirkovské akce byly doplněny do aktuálního kulturního přehledu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
