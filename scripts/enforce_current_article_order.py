#!/usr/bin/env python3
"""Doplní chybějící schválené karty a následně je chronologicky seřadí."""
from __future__ import annotations

from pathlib import Path

from sort_articles_chronologically import main as sort_all

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"

ARC_PATH = "/clanky/arc-med-nemocnice-kadan.html"
KOLOB_PATH = "/clanky/kolobezky-hriste-detektor-kovu-kadan.html"

ARC_HOME = '''
    <article class="article-card hospital" data-arc-med-card>
      <div class="visual" style="background:linear-gradient(135deg,#132630,#3f6576 58%,#a9232b)"><strong>ARC-MED za 16 milionů</strong></div>
      <div class="article-body">
        <span class="meta">28. 7. 2026 · 5:00 · Zdravotnictví a veřejné peníze</span>
        <h3>Dva posudky, nejasné schválení a spor o dvanáct milionů</h3>
        <p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p>
        <a class="read-more" href="/clanky/arc-med-nemocnice-kadan.html">Přečíst článek →</a>
      </div>
    </article>'''

ARC_ARCHIVE = '''
    <article class="archive-item hospital" data-arc-med-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#132630,#3f6576 58%,#a9232b)"><strong>ARC-MED za 16 milionů</strong></div>
      <div class="archive-body">
        <span class="archive-meta">28. července 2026 v 5:00 · Zdravotnictví a veřejné peníze</span>
        <h2>ARC-MED za 16 milionů: dva posudky, nejasné schválení a spor o dvanáct milionů</h2>
        <p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p>
        <a href="/clanky/arc-med-nemocnice-kadan.html">Přečíst celý článek →</a>
      </div>
    </article>'''

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

RSS_ITEMS = {
    "https://nasekadan.cz/clanky/arc-med-nemocnice-kadan.html": '''
    <item><title>ARC-MED za 16 milionů: dva posudky, nejasné schválení a spor o dvanáct milionů</title><description><![CDATA[Nemocnice Kadaň koupila ARC-MED podle veřejných vyjádření za 16 milionů korun. Rozebíráme dva odhady hodnoty, schvalování transakce a tvrzení o 12,1 milionu od pojišťovny.]]></description><link>https://nasekadan.cz/clanky/arc-med-nemocnice-kadan.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/arc-med-nemocnice-kadan.html</guid><pubDate>Tue, 28 Jul 2026 05:00:00 +0200</pubDate><category>Zdravotnictví</category><category>Veřejné peníze</category><category>Nemocnice Kadaň</category><szn:image><szn:url>https://nasekadan.cz/social/arc-med-nemocnice-kadan-4e6f70d9c0.png</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>''',
    "https://nasekadan.cz/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html": '''
    <item><title>Kadaňští hasiči cvičili na Nechranicích záchranu lidí z vody</title><description><![CDATA[Společný výcvik prověřil práci člunů i součinnost hasičů, policie a vodních záchranářů.]]></description><link>https://nasekadan.cz/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html</guid><pubDate>Mon, 27 Jul 2026 22:35:00 +0200</pubDate><category>Hasiči</category><category>Bezpečnost</category><category>Kadaň</category><szn:image><szn:url>https://nasekadan.cz/social/hasici-kadan-vycvik-zachrana-voda-nechranice-05468cfbcc.png</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>''',
    "https://nasekadan.cz/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html": '''
    <item><title>Z Kadaně až k frontové linii. Nemocnice darovala na Ukrajinu 82 lůžek</title><description><![CDATA[Funkční nemocniční postele dostaly druhou šanci tam, kde jsou mimořádně potřebné.]]></description><link>https://nasekadan.cz/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html</guid><pubDate>Mon, 27 Jul 2026 21:40:00 +0200</pubDate><category>Nemocnice Kadaň</category><category>Pomoc Ukrajině</category><szn:image><szn:url>https://nasekadan.cz/social/nemocnice-kadan-darovala-82-luzek-ukrajine-b7f09aa8e1.png</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>''',
    "https://nasekadan.cz/clanky/kolobezky-hriste-detektor-kovu-kadan.html": '''
    <item><title>Polovina prázdnin je za námi. Strážníci mají více sledovat koloběžky</title><description><![CDATA[Kadaňští strážníci avizovali větší letní dohled nad koloběžkami a jízdními koly. Dětská hřiště současně kontrolují i detektorem kovu.]]></description><link>https://nasekadan.cz/clanky/kolobezky-hriste-detektor-kovu-kadan.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/kolobezky-hriste-detektor-kovu-kadan.html</guid><pubDate>Mon, 27 Jul 2026 14:00:00 +0200</pubDate><category>Bezpečnost</category><category>Doprava</category><category>Kadaň</category><szn:image><szn:url>https://nasekadan.cz/social/kolobezky-hriste-detektor-kovu-kadan-dbbb2d5f7e.png</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>''',
    "https://nasekadan.cz/clanky/avies-nemocnice-kadan.html": '''
    <item><title>Kdo nastavil nákupy léčiv od AVIES? Nemocnice za sedm let zaplatila téměř 170 milionů</title><description><![CDATA[Analýza sedmi let plateb, vývoje smluvního vztahu, role jednotlivých vedení a veřejné dokumentační mezery roku 2024.]]></description><link>https://nasekadan.cz/clanky/avies-nemocnice-kadan.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/avies-nemocnice-kadan.html</guid><pubDate>Mon, 27 Jul 2026 05:00:00 +0200</pubDate><category>Zdravotnictví</category><category>Veřejné peníze</category><category>Nemocnice Kadaň</category><szn:image><szn:url>https://nasekadan.cz/social/avies-nemocnice-kadan-a52b96a304.png</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>''',
}


def ensure_card(path: Path, marker: str, href: str, card: str) -> None:
    text = path.read_text(encoding="utf-8")
    section = text.split(marker, 1)[-1]
    if href not in section:
        if marker not in text:
            raise RuntimeError(f"V {path} chybí vkládací bod")
        text = text.replace(marker, marker + card, 1)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    for article_path in (ARC_PATH, KOLOB_PATH):
        if not (ROOT / article_path.lstrip("/")).is_file():
            raise RuntimeError(f"Chybí veřejný článek {article_path}")

    ensure_card(HOME, '<div class="article-list">', ARC_PATH, ARC_HOME)
    ensure_card(ARCHIVE, '<section class="archive-list" aria-label="Chronologický přehled článků">', ARC_PATH, ARC_ARCHIVE)
    ensure_card(HOME, '<div class="article-list">', KOLOB_PATH, KOLOB_HOME)
    ensure_card(ARCHIVE, '<section class="archive-list" aria-label="Chronologický přehled článků">', KOLOB_PATH, KOLOB_ARCHIVE)

    rss = RSS.read_text(encoding="utf-8")
    anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if anchor not in rss:
        raise RuntimeError("RSS nemá vkládací bod")
    for url, item in RSS_ITEMS.items():
        if url not in rss:
            rss = rss.replace(anchor, anchor + item, 1)
    RSS.write_text(rss, encoding="utf-8", newline="\n")

    sort_all()
    print("Nejnovější schválené články jsou přítomné a chronologicky zařazené.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
