#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# LATEST_AUTOKEMP_GUARD: staré opravné skripty nesmějí přepsat novější titulní článek.
if (ROOT / "clanky" / "odstavky-elektriny-autokemp-prunerov-srpen-2026.html").exists():
    print("Novější článek o odstávkách Autokempu Prunéřov je již publikován; staré pořadí se nepoužije.")
    raise SystemExit(0)
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"

BEDS_PATH = "/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html"
KOLOB_PATH = "/clanky/kolobezky-hriste-detektor-kovu-kadan.html"
AVIES_PATH = "/clanky/avies-nemocnice-kadan.html"
CULTURE_PATH = "/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"
KOLOB_URL = "https://nasekadan.cz" + KOLOB_PATH

BEDS_HOME = '''
      <article class="article-card hospital" data-beds-card>
        <div class="visual" style="background:linear-gradient(135deg,#142b37,#36586a 58%,#9d222a)"><strong>82 lůžek pro Ukrajinu</strong></div>
        <div class="article-body">
          <span class="meta">27. 7. 2026 · 21:40 · Nemocnice Kadaň</span>
          <h3>Z Kadaně až k frontové linii</h3>
          <p>Funkční nemocniční postele dostaly druhou šanci tam, kde jsou mimořádně potřebné.</p>
          <a class="read-more" href="/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html">Přečíst článek →</a>
        </div>
      </article>
'''

BEDS_ARCHIVE = '''
    <article class="archive-item hospital" data-beds-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#142b37,#36586a 58%,#9d222a)"><strong>82 lůžek pro Ukrajinu</strong></div>
      <div class="archive-body">
        <span class="archive-meta">27. července 2026 v 21:40 · Nemocnice Kadaň</span>
        <h2>Z Kadaně až k frontové linii. Nemocnice darovala na Ukrajinu 82 lůžek</h2>
        <p>Darovaná lůžka byla převezena do vojenské nemocnice v Kyjevě a mají pokračovat do zařízení poblíž fronty.</p>
        <a href="/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html">Přečíst celý článek →</a>
      </div>
    </article>
'''

KOLOB_HOME = '''
      <article class="article-card transport" data-kolobezky-card>
        <div class="visual" style="background:linear-gradient(135deg,#173442,#416d64 58%,#b08838)"><strong>Koloběžky a bezpečnost</strong></div>
        <div class="article-body">
          <span class="meta">27. 7. 2026 · 14:00 · Bezpečnost a doprava</span>
          <h3>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</h3>
          <p>Větší dohled byl ohlášen na celé léto. Hřiště se současně kontrolují i detektorem kovu.</p>
          <a class="read-more" href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst článek →</a>
        </div>
      </article>
'''

KOLOB_ARCHIVE = '''
    <article class="archive-item transport" data-kolobezky-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#173442,#416d64 58%,#b08838)"><strong>Koloběžky a bezpečnost</strong></div>
      <div class="archive-body">
        <span class="archive-meta">27. července 2026 v 14:00 · Bezpečnost a doprava</span>
        <h2>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</h2>
        <p>Větší dohled byl ohlášen na celé léto. Hřiště se současně kontrolují i detektorem kovu.</p>
        <a href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst článek →</a>
      </div>
    </article>
'''

KOLOB_RSS = '''    <item>
      <title>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</title>
      <description><![CDATA[Kadaňští strážníci avizovali větší letní dohled nad koloběžkami a jízdními koly. Dětská hřiště současně kontrolují i detektorem kovu.]]></description>
      <link>https://nasekadan.cz/clanky/kolobezky-hriste-detektor-kovu-kadan.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/kolobezky-hriste-detektor-kovu-kadan.html</guid>
      <pubDate>Mon, 27 Jul 2026 14:00:00 +0200</pubDate>
      <category>Bezpečnost</category>
      <category>Doprava</category>
      <category>Kadaň</category>
      <szn:image><szn:url>https://nasekadan.cz/social/kolobezky-hriste-detektor-kovu-kadan-dbbb2d5f7e.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>

'''

HERO = '''  <section class="wrap hero" id="clanky">
    <article class="lead" data-beds-hero>
      <div class="photo" style="background:radial-gradient(circle at 78% 18%,rgba(255,255,255,.16),transparent 27%),linear-gradient(135deg,#142b37,#36586a 52%,#9d222a)"><span>POMOC UKRAJINĚ</span><strong>82 LŮŽEK</strong></div>
      <div class="copy">
        <small>NEMOCNICE KADAŇ · 27. 07. 2026 · 21:40</small>
        <h1>Z Kadaně až k frontové linii</h1>
        <p>Nemocnice darovala 82 stále funkčních lůžek. Z Kyjeva mají zamířit do zařízení poblíž frontové linie.</p>
        <a class="btn" href="/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html">Přečíst celý článek →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">DALŠÍ DNEŠNÍ ČLÁNEK</p>
      <p class="aside-date">27. 7. 2026</p>
      <h2>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</h2>
      <p>Větší dohled byl ohlášen na celé léto. Hřiště se současně kontrolují i detektorem kovu.</p>
      <a class="aside-button" href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst článek →</a>
      <div class="aside-links">
        <a href="/clanky/avies-nemocnice-kadan.html">Dnešní analýza AVIES</a>
        <a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kulturní přehled na tento týden</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>
  </section>'''


def article_blocks(section: str) -> list[str]:
    return re.findall(r"<article\b[^>]*>.*?</article>", section, flags=re.S | re.I)


def find_optional(blocks: list[str], path: str) -> str | None:
    for block in blocks:
        if f'href="{path}"' in block:
            return block
    return None


def reorder_section(text: str, start_marker: str, end_marker: str, archive: bool) -> str:
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker, start)
    section = text[start:end]
    blocks = article_blocks(section)

    beds = find_optional(blocks, BEDS_PATH) or (BEDS_ARCHIVE if archive else BEDS_HOME)
    kolob = find_optional(blocks, KOLOB_PATH) or (KOLOB_ARCHIVE if archive else KOLOB_HOME)
    avies = find_optional(blocks, AVIES_PATH)
    culture = find_optional(blocks, CULTURE_PATH)
    if avies is None or culture is None:
        raise RuntimeError("Chybí karta AVIES nebo kulturního přehledu.")

    wanted = {BEDS_PATH, KOLOB_PATH, AVIES_PATH, CULTURE_PATH}
    remaining = [b for b in blocks if not any(f'href="{p}"' in b for p in wanted)]
    ordered = [beds, kolob, avies, culture, *remaining]
    replacement = "\n" + "\n".join(block.strip("\n") for block in ordered) + "\n    "
    return text[:start] + replacement + text[end:]


def update_archive_jsonld(text: str) -> str:
    match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)
    if not match:
        return text
    data = json.loads(match.group(1))
    itemlist = next((x for x in data.get("@graph", []) if x.get("@type") == "ItemList"), None)
    if not itemlist:
        return text

    urls = [
        ("https://nasekadan.cz" + BEDS_PATH, "Z Kadaně až k frontové linii. Nemocnice darovala na Ukrajinu 82 lůžek"),
        ("https://nasekadan.cz" + KOLOB_PATH, "Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky"),
        ("https://nasekadan.cz" + AVIES_PATH, "Kdo nastavil nákupy léčiv od AVIES? Nemocnice za sedm let zaplatila téměř 170 milionů"),
        ("https://nasekadan.cz" + CULTURE_PATH, "Kam v Kadani a okolí od 27. července do 2. srpna"),
    ]
    existing = itemlist.get("itemListElement", [])
    wanted_urls = {u for u, _ in urls}
    rest = [x for x in existing if x.get("url") not in wanted_urls]
    ordered = [{"@type": "ListItem", "url": u, "name": n} for u, n in urls] + rest
    for i, item in enumerate(ordered, 1):
        item["position"] = i
    itemlist["itemListElement"] = ordered
    itemlist["numberOfItems"] = len(ordered)
    replacement = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + "</script>"
    return text[: match.start()] + replacement + text[match.end() :]


def ensure_rss(text: str) -> str:
    # Odebrat případnou starší nebo duplicitní položku a vložit ji chronologicky
    # za večerní článek o 82 lůžkách. Tím je výsledek idempotentní.
    item_re = re.compile(
        r"\s*<item>.*?<link>" + re.escape(KOLOB_URL) + r"</link>.*?</item>\s*",
        re.S,
    )
    text = item_re.sub("\n", text)
    beds_item = re.compile(
        r"(<item>.*?<link>https://nasekadan\.cz" + re.escape(BEDS_PATH) + r"</link>.*?</item>\s*)",
        re.S,
    )
    text, count = beds_item.subn(r"\1\n" + KOLOB_RSS, text, count=1)
    if count == 0:
        marker = "    <item>"
        if marker not in text:
            raise RuntimeError("RSS nemá žádnou položku.")
        text = text.replace(marker, KOLOB_RSS + marker, 1)
    return text


def main() -> int:
    for required in (BEDS_PATH, KOLOB_PATH, AVIES_PATH, CULTURE_PATH):
        if not (ROOT / required.lstrip("/")).is_file():
            raise RuntimeError(f"Chybí veřejný článek {required}")

    home = HOME.read_text(encoding="utf-8")
    home = re.sub(r'  <section class="wrap hero" id="clanky">.*?</section>', HERO, home, count=1, flags=re.S)
    home = reorder_section(home, '<div class="article-list">', '<p class="archive-note">', archive=False)
    HOME.write_text(home, encoding="utf-8", newline="\n")

    archive = ARCHIVE.read_text(encoding="utf-8")
    archive = reorder_section(
        archive,
        '<section class="archive-list" aria-label="Chronologický přehled článků">',
        "</section>",
        archive=True,
    )
    archive = update_archive_jsonld(archive)
    ARCHIVE.write_text(archive, encoding="utf-8", newline="\n")

    rss = ensure_rss(RSS.read_text(encoding="utf-8"))
    RSS.write_text(rss, encoding="utf-8", newline="\n")

    print("Pořadí článků a RSS: 82 lůžek, koloběžky, AVIES, kultura.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
