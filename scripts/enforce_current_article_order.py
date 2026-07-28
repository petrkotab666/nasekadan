#!/usr/bin/env python3
"""Doplní chybějící schválené karty a následně je chronologicky seřadí."""
from __future__ import annotations

from pathlib import Path

from sort_articles_chronologically import main as sort_all

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"
KOLOB_PATH = "/clanky/kolobezky-hriste-detektor-kovu-kadan.html"
KOLOB_URL = "https://nasekadan.cz" + KOLOB_PATH

KOLOB_HOME = '''
    <article class="article-card transport" data-kolobezky-card>
      <div class="visual" style="background:linear-gradient(135deg,#173442,#416d64 58%,#b08838)"><strong>Koloběžky a bezpečnost</strong></div>
      <div class="article-body">
        <span class="meta">27. 7. 2026 · 14:00 · Bezpečnost a doprava</span>
        <h3>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</h3>
        <p>Větší dohled byl ohlášen na celé léto. Hřiště se současně kontrolují i detektorem kovu.</p>
        <a class="read-more" href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst článek →</a>
      </div>
    </article>'''

KOLOB_ARCHIVE = '''
    <article class="archive-item transport" data-kolobezky-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#173442,#416d64 58%,#b08838)"><strong>Koloběžky a bezpečnost</strong></div>
      <div class="archive-body">
        <span class="archive-meta">27. července 2026 v 14:00 · Bezpečnost a doprava</span>
        <h2>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</h2>
        <p>Větší dohled byl ohlášen na celé léto. Hřiště se současně kontrolují i detektorem kovu.</p>
        <a href="/clanky/kolobezky-hriste-detektor-kovu-kadan.html">Přečíst článek →</a>
      </div>
    </article>'''

KOLOB_RSS = '''
    <item>
      <title>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</title>
      <description><![CDATA[Kadaňští strážníci avizovali větší letní dohled nad koloběžkami a jízdními koly. Dětská hřiště současně kontrolují i detektorem kovu.]]></description>
      <link>https://nasekadan.cz/clanky/kolobezky-hriste-detektor-kovu-kadan.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/kolobezky-hriste-detektor-kovu-kadan.html</guid>
      <pubDate>Mon, 27 Jul 2026 14:00:00 +0200</pubDate>
      <category>Bezpečnost</category><category>Doprava</category><category>Kadaň</category>
      <szn:image><szn:url>https://nasekadan.cz/social/kolobezky-hriste-detektor-kovu-kadan-dbbb2d5f7e.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>
    </item>'''


def ensure_card(path: Path, marker: str, href: str, card: str) -> None:
    text = path.read_text(encoding="utf-8")
    if href not in text.split(marker, 1)[-1]:
        if marker not in text:
            raise RuntimeError(f"V {path} chybí vkládací bod")
        text = text.replace(marker, marker + card, 1)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    article = ROOT / KOLOB_PATH.lstrip("/")
    if not article.is_file():
        raise RuntimeError(f"Chybí veřejný článek {KOLOB_PATH}")

    ensure_card(HOME, '<div class="article-list">', KOLOB_PATH, KOLOB_HOME)
    ensure_card(ARCHIVE, '<section class="archive-list" aria-label="Chronologický přehled článků">', KOLOB_PATH, KOLOB_ARCHIVE)

    rss = RSS.read_text(encoding="utf-8")
    if KOLOB_URL not in rss:
        anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
        if anchor not in rss:
            raise RuntimeError("RSS nemá vkládací bod")
        rss = rss.replace(anchor, anchor + KOLOB_RSS, 1)
        RSS.write_text(rss, encoding="utf-8", newline="\n")

    sort_all()
    print("Karta článku o koloběžkách je přítomná a chronologicky zařazená.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
