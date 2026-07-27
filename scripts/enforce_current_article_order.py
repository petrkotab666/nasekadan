#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"

KOLOB_PATH = "/clanky/kolobezky-hriste-detektor-kovu-kadan.html"
AVIES_PATH = "/clanky/avies-nemocnice-kadan.html"
CULTURE_PATH = "/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"

KOLOB_HOME = '''
      <article class="article-card transport" data-kolobezky-card>
        <div class="visual" style="background:linear-gradient(135deg,#173442,#416d64 58%,#b08838)"><strong>Koloběžky a bezpečnost</strong></div>
        <div class="article-body">
          <span class="meta">27. 7. 2026 · Bezpečnost a doprava</span>
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
        <span class="archive-meta">27. července 2026 · Bezpečnost a doprava</span>
        <h2>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</h2>
        <p>Větší dohled byl ohlášen na celé léto. Hřiště se současně kontrolují i detektorem kovu.</p>
        <a href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst článek →</a>
      </div>
    </article>
'''

HERO = '''  <section class="wrap hero" id="clanky">
    <article class="lead" data-kolobezky-hero>
      <div class="photo" style="background:linear-gradient(135deg,#173442,#416d64 58%,#b08838)"><span>BEZPEČNOST</span><strong>Koloběžky</strong></div>
      <div class="copy">
        <small>BEZPEČNOST · DOPRAVA · 27. 07. 2026</small>
        <h1>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</h1>
        <p>Větší dohled byl ohlášen na celé léto. Dětská hřiště strážníci současně kontrolují i detektorem kovu.</p>
        <a class="btn" href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Otevřít celý článek →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">DALŠÍ DNEŠNÍ ČLÁNEK</p>
      <p class="aside-date">27. 7. 2026 v 5:00</p>
      <h2>Sedm let plateb, téměř 170 milionů a chybějící dokument</h2>
      <p>Co je doložené, kdo dlouhodobý systém převzal a proč zůstává klíčový rok 2024.</p>
      <a class="aside-button" href="/clanky/avies-nemocnice-kadan.html">Přečíst analýzu nemocnice →</a>
      <div class="aside-links">
        <a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Včerejší kulturní přehled</a>
        <a href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Noční výluky vlaků</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>
  </section>'''


def article_blocks(section: str) -> list[str]:
    return re.findall(r"<article\b[^>]*>.*?</article>", section, flags=re.S | re.I)


def find_block(blocks: list[str], path: str) -> str:
    for block in blocks:
        if f'href="{path}"' in block:
            return block
    raise RuntimeError(f"Chybí karta článku {path}")


def reorder_section(text: str, start_marker: str, end_marker: str, archive: bool) -> str:
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker, start)
    section = text[start:end]
    blocks = article_blocks(section)
    avies = find_block(blocks, AVIES_PATH)
    culture = find_block(blocks, CULTURE_PATH)
    wanted = {KOLOB_PATH, AVIES_PATH, CULTURE_PATH}
    remaining = [b for b in blocks if not any(f'href="{p}"' in b for p in wanted)]
    ordered = [KOLOB_ARCHIVE if archive else KOLOB_HOME, avies, culture, *remaining]
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
    replacement = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + '</script>'
    return text[:match.start()] + replacement + text[match.end():]


def main() -> int:
    home = HOME.read_text(encoding="utf-8")
    home = re.sub(r'  <section class="wrap hero" id="clanky">.*?</section>', HERO, home, count=1, flags=re.S)
    home = reorder_section(home, '<div class="article-list">', '<p class="archive-note">', archive=False)
    HOME.write_text(home, encoding="utf-8", newline="\n")

    archive = ARCHIVE.read_text(encoding="utf-8")
    archive = reorder_section(archive, '<section class="archive-list" aria-label="Chronologický přehled článků">', '</section>', archive=True)
    archive = update_archive_jsonld(archive)
    ARCHIVE.write_text(archive, encoding="utf-8", newline="\n")
    print("Pořadí článků: koloběžky, AVIES, kultura.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
