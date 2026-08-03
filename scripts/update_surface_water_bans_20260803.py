#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html"
RSS = ROOT / "rss.xml"
SITEMAP = ROOT / "sitemap.xml"
PUBLISHED_INDEX = ROOT / "data/published-content-index.json"

URL = "https://nasekadan.cz/clanky/zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026.html"
SLUG = "zakaz-odberu-povrchovych-vod-kadansko-cervenec-2026"
MODIFIED = "2026-08-03T22:50:00+02:00"
MODIFIED_HUMAN = "3. srpna 2026 ve 22:50"
DESCRIPTION = (
    "Vodoprávní úřad v Kadani zakázal odběr ze 14 toků. Samostatné opatření "
    "Chomutova zahrnuje dalších 11 toků včetně horní části Prunéřovského potoka."
)
UPDATE_MARKER_START = "<!-- WATER-BAN-UPDATE-20260803-START -->"
UPDATE_MARKER_END = "<!-- WATER-BAN-UPDATE-20260803-END -->"
CSS_MARKER_START = "/* WATER-BAN-UPDATE-20260803-START */"
CSS_MARKER_END = "/* WATER-BAN-UPDATE-20260803-END */"


def clean_trailing_whitespace(text: str) -> str:
    """Remove trailing spaces while preserving one final newline."""
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def replace_one(text: str, pattern: str, replacement: str, *, flags: int = 0, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"Nepodařilo se nahradit právě jeden prvek: {label} (nalezeno {count}).")
    return updated


def upsert_meta(text: str, *, attr: str, key: str, content: str) -> str:
    pattern = rf'<meta\b(?=[^>]*\b{re.escape(attr)}=["\']{re.escape(key)}["\'])[^>]*>'
    replacement = f'<meta {attr}="{key}" content="{content}">'
    if re.search(pattern, text, re.I):
        return re.sub(pattern, replacement, text, count=1, flags=re.I)
    return text.replace("</head>", f"  {replacement}\n</head>", 1)


def update_newsarticle_jsonld(text: str) -> str:
    pattern = re.compile(
        r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        re.I | re.S,
    )

    def patch_node(node: object) -> bool:
        if not isinstance(node, dict):
            return False
        raw_type = node.get("@type")
        types = {raw_type} if isinstance(raw_type, str) else set(raw_type or []) if isinstance(raw_type, list) else set()
        changed = False
        if "NewsArticle" in types:
            node["description"] = DESCRIPTION
            node["dateModified"] = MODIFIED
            changed = True
        graph = node.get("@graph")
        if isinstance(graph, list):
            for child in graph:
                changed = patch_node(child) or changed
        return changed

    def repl(match: re.Match[str]) -> str:
        opening, raw, closing = match.groups()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        if not patch_node(data):
            return match.group(0)
        return opening + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + closing

    return pattern.sub(repl, text)


def article_update_block() -> str:
    return f'''{UPDATE_MARKER_START}
  <div class="update-box"><strong>Aktualizace {MODIFIED_HUMAN}</strong><p>Původní článek popisoval opatření vydané vodoprávním úřadem v Kadani. Doplnili jsme samostatný zákaz Magistrátu města Chomutova, který platí už od 30. června 2026. Jde o dvě různá opatření dvou vodoprávních úřadů.</p></div>

  <h2>Zákaz je širší než původní kadaňský seznam</h2>
  <p>Vedle čtrnácti toků a úseků uvedených v opatření Městského úřadu Kadaň platí do odvolání také samostatné opatření Magistrátu města Chomutova. To se vztahuje na dalších jedenáct toků a jejich vymezených částí na Chomutovsku, Jirkovsku a v Krušných horách.</p>
  <p>Zakázané jsou zejména odběry pro zalévání zahrad, hřišť a trávníků, mytí automobilů a napouštění nádrží nebo bazénů. Dodržování zákazu mají kontrolovat vodoprávní úřady.</p>

  <h2>Chomutovské opatření: dalších 11 toků a úseků</h2>
  <ul class="stream-list">
    <li>Hačka, říční km 0,000–10,400</li>
    <li>Hutná I, říční km 8,900–17,200</li>
    <li>Hutná II, říční km 0,000–6,700</li>
    <li>Lužec neboli Nivský potok, říční km 0,000–1,800</li>
    <li>Srpina, od říčního km 22,300 k prameni</li>
    <li>Hutní potok I, od ústí k prameni</li>
    <li>Prunéřovský potok, říční km 8,700–16,700</li>
    <li>Bílina včetně odběrů z vodní nádrže Březenec, říční km 66,700–72,000</li>
    <li>Chomutovka, říční km 18,300–50,200</li>
    <li>PPV – Přivaděč Ohře–Bílina, říční km 0,000–17,600</li>
    <li>PKP II – Přivaděč Ohře–Bílina, od ústí k prameni</li>
  </ul>

  <div class="callout"><strong>Prunéřovský potok: zákaz se netýká celého toku</strong><p>Zveřejněný seznam uvádí pouze úsek mezi říčními kilometry 8,700 a 16,700 na území Výsluní, Křimova a Místa. Dolní část toku v okolí Prunéřova a Kadaně v tomto chomutovském opatření uvedena není.</p></div>

  <h2>Nejde o zákaz vody z kohoutku</h2>
  <p>Obě opatření se týkají odběru <strong>povrchové vody přímo z vyjmenovaných toků a úseků</strong>. Neznamenají zákaz běžného používání pitné vody z veřejného vodovodu. Kadaňské opatření navíc výslovně ponechává výjimku pro zásobování obyvatel pitnou vodou a pro hašení požárů.</p>
{UPDATE_MARKER_END}'''


def patch_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    # Odstranit případnou starší verzi aktualizačního bloku a stylů – skript je idempotentní.
    text = re.sub(
        re.escape(UPDATE_MARKER_START) + r".*?" + re.escape(UPDATE_MARKER_END),
        "",
        text,
        flags=re.S,
    )
    text = re.sub(
        re.escape(CSS_MARKER_START) + r".*?" + re.escape(CSS_MARKER_END),
        "",
        text,
        flags=re.S,
    )

    text = upsert_meta(text, attr="name", key="description", content=DESCRIPTION)
    text = upsert_meta(text, attr="property", key="og:description", content=DESCRIPTION)
    text = upsert_meta(text, attr="name", key="twitter:description", content=DESCRIPTION)
    text = upsert_meta(text, attr="property", key="article:modified_time", content=MODIFIED)
    text = update_newsarticle_jsonld(text)

    css = f'''
    {CSS_MARKER_START}
    .update-box{{background:#fff4dd;border:1px solid #e7c883;border-left:7px solid #b8740f;border-radius:0 18px 18px 0;padding:22px 25px;margin:28px 0}}
    .update-box strong{{display:block;font:800 24px Georgia,serif;color:#6b430d;margin-bottom:7px}}
    .update-box p{{margin:0}}
    {CSS_MARKER_END}
'''
    text = text.replace("</style>", css + "  </style>", 1)

    text = replace_one(
        text,
        r'<p class="tag">.*?</p>',
        '<p class="tag">DŮLEŽITÉ UPOZORNĚNÍ · VODA · AKTUALIZOVÁNO 3. SRPNA 2026</p>',
        flags=re.S,
        label="štítek článku",
    )
    text = replace_one(
        text,
        r'<p class="leadtext">.*?</p>',
        '<p class="leadtext"><strong>Na Kadaňsku platí zákaz odběru povrchové vody ze čtrnácti toků a úseků. Nyní doplňujeme, že samostatné opatření chomutovského vodoprávního úřadu zahrnuje dalších jedenáct toků, mimo jiné horní část Prunéřovského potoka. Obě opatření platí do odvolání.</strong></p>',
        flags=re.S,
        label="úvod článku",
    )
    text = replace_one(
        text,
        r'<div class="hero-visual">.*?</div>',
        '<div class="hero-visual"><strong>V regionu současně platí dvě různá opatření. Kadaňské uvádí 14 toků a úseků, chomutovské dalších 11. Nejde o omezení běžné vody z veřejného vodovodu.</strong></div>',
        flags=re.S,
        label="hlavní vizuální box",
    )
    text = text.replace(
        '<h2>Kterých toků se zákaz týká</h2>',
        '<h2>Kadaňské opatření: kterých 14 toků se zákaz týká</h2>',
        1,
    )

    hero_end = '<div class="hero-visual"><strong>V regionu současně platí dvě různá opatření. Kadaňské uvádí 14 toků a úseků, chomutovské dalších 11. Nejde o omezení běžné vody z veřejného vodovodu.</strong></div>'
    if hero_end not in text:
        raise RuntimeError("Po úpravě nebyl nalezen očekávaný hlavní box.")
    text = text.replace(hero_end, hero_end + "\n\n" + article_update_block(), 1)

    sources = f'''<div class="source-list"><h2>Zdroje</h2><ul>
    <li><a href="https://www.mesto-kadan.cz/cs/system/uredni-deska-nova.html" target="_blank" rel="noopener noreferrer">Město Kadaň – úřední deska</a>, opatření MUKK/28368/2026 „Zákaz odběru povrchových vod do odvolání“, zveřejněné 27. července 2026.</li>
    <li><a href="https://www.jirkov.cz/nabidka-temat/otevrena-radnice/aktuality/zakaz-odberu-povrchovych-vod-7094cs.html" target="_blank" rel="noopener noreferrer">Město Jirkov – Zákaz odběru povrchových vod</a>, oficiální zveřejnění opatření Magistrátu města Chomutova účinného od 30. června 2026.</li>
  </ul><p><small>Aktualizováno {MODIFIED_HUMAN}. Na uvedených oficiálních stránkách nebylo při kontrole uvedeno, že by některé z opatření bylo zrušeno.</small></p></div>'''
    text = replace_one(
        text,
        r'<div class="source-list">.*?</div>',
        sources,
        flags=re.S,
        label="seznam zdrojů",
    )

    sidebar = '''<div class="sidebox"><h3>Rychlý přehled po aktualizaci</h3><ul><li>Dvě samostatná opatření</li><li>Kadaň: 14 toků a úseků</li><li>Chomutov: dalších 11 toků a úseků</li><li>Obě platí do odvolání</li><li>Prunéřovský potok jen km 8,700–16,700</li><li>Voda z veřejného vodovodu není zakázaná</li><li>Úřady avizují kontroly</li></ul></div>'''
    text = replace_one(
        text,
        r'<div class="sidebox"><h3>Rychlý přehled</h3>.*?</div>',
        sidebar,
        flags=re.S,
        label="postranní přehled",
    )

    required = [
        UPDATE_MARKER_START,
        "30. června 2026",
        "Prunéřovský potok, říční km 8,700–16,700",
        "Dolní část toku v okolí Prunéřova a Kadaně",
        "Nejde o zákaz vody z kohoutku",
        MODIFIED,
        "zakaz-odberu-povrchovych-vod-7094cs.html",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"Aktualizovaný článek postrádá: {missing}")
    if "noindex" in text.lower():
        raise RuntimeError("Veřejný článek nesmí obsahovat noindex.")
    if text.count(UPDATE_MARKER_START) != 1 or text.count(UPDATE_MARKER_END) != 1:
        raise RuntimeError("Aktualizační blok není právě jednou.")

    ARTICLE.write_text(clean_trailing_whitespace(text), encoding="utf-8", newline="\n")


def patch_rss() -> None:
    if not RSS.exists():
        return
    text = RSS.read_text(encoding="utf-8")
    pattern = re.compile(r"<item>.*?" + re.escape(URL) + r".*?</item>", re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("RSS neobsahuje původní článek o zákazu odběru vody.")
    block = match.group(0)
    block = re.sub(
        r"<description>.*?</description>",
        "<description><![CDATA[" + DESCRIPTION + "]]></description>",
        block,
        count=1,
        flags=re.S,
    )
    text = text[:match.start()] + block + text[match.end():]
    RSS.write_text(clean_trailing_whitespace(text), encoding="utf-8", newline="\n")


def patch_sitemap() -> None:
    if not SITEMAP.exists():
        return
    text = SITEMAP.read_text(encoding="utf-8")
    pattern = re.compile(r"<url>\s*<loc>" + re.escape(URL) + r"</loc>.*?</url>", re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Sitemap neobsahuje článek o zákazu odběru vody.")
    block = match.group(0)
    if "<lastmod>" in block:
        block = re.sub(r"<lastmod>.*?</lastmod>", "<lastmod>2026-08-03</lastmod>", block, count=1)
    else:
        block = block.replace("</url>", "<lastmod>2026-08-03</lastmod></url>", 1)
    text = text[:match.start()] + block + text[match.end():]
    SITEMAP.write_text(clean_trailing_whitespace(text), encoding="utf-8", newline="\n")


def patch_published_index() -> None:
    if not PUBLISHED_INDEX.exists():
        return
    try:
        data = json.loads(PUBLISHED_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    changed = False

    def walk(value: object) -> None:
        nonlocal changed
        if isinstance(value, dict):
            values = {str(item) for item in value.values() if isinstance(item, (str, int, float))}
            matched = value.get("slug") == SLUG or URL in values or f"/clanky/{SLUG}.html" in values
            if matched:
                for key in ("description", "summary", "excerpt"):
                    if key in value:
                        value[key] = DESCRIPTION
                for key in ("modified", "modified_at", "updated_at", "dateModified", "last_modified"):
                    if key in value:
                        value[key] = MODIFIED
                changed = True
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    if changed:
        PUBLISHED_INDEX.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )


def main() -> None:
    patch_article()
    patch_rss()
    patch_sitemap()
    patch_published_index()
    print("Aktualizace článku o zákazu odběru vody je připravena.")


if __name__ == "__main__":
    main()
