#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
SITEMAP = ROOT / "sitemap.xml"
RSS = ROOT / "rss.xml"

TRAIN_PATH = "/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html"
TRAIN_URL = "https://nasekadan.cz" + TRAIN_PATH
SOFTWARE_PATH = "/clanky/nemocnice-kadan-software-kyberbezpecnost.html"
SOFTWARE_URL = "https://nasekadan.cz" + SOFTWARE_PATH
AMBULANCE_PATH = "/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html"

TRANSPORT_CARD = '''
      <article class="article-card transport" data-train-outage-card>
        <div class="visual"><strong>Noční výluky vlaků</strong></div>
        <div class="article-body">
          <span class="meta">25. 7. 2026 · 22:41 · Doprava</span>
          <h3>Noční výluky zasáhnou Kadaň, Klášterec i Chomutov</h3>
          <p>Od 27. července nahradí většinu nočních vlaků autobusy. Omezení se bude s přestávkami opakovat také během srpna.</p>
          <a class="read-more" href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
        </div>
      </article>
'''

TRANSPORT_ARCHIVE = '''
    <article class="archive-item transport" data-train-outage-card>
      <div class="archive-visual"><strong>Noční výluky vlaků</strong></div>
      <div class="archive-body">
        <span class="archive-meta">25. července 2026 v 22:41 · Praktické informace a doprava</span>
        <h2>Noční výluky vlaků zasáhnou Kadaň, Klášterec i Chomutov</h2>
        <p>Od pondělí 27. července budou většinu nočních vlaků nahrazovat autobusy. Výlukové bloky jsou naplánované s přestávkami až do konce srpna.</p>
        <a href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      </div>
    </article>
'''

TRANSPORT_ASIDE = '''<aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">25. 7. 2026 v 22:41</p>
      <h2>Noční výluky vlaků zasáhnou Kadaň, Klášterec i Chomutov</h2>
      <p>Od pondělí večer nahradí většinu nočních vlaků autobusy. Omezení se bude s přestávkami opakovat až do konce srpna.</p>
      <a class="aside-button" href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      <div class="aside-links">
        <a href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Uzavření interní ambulance</a>
        <a href="/clanky/petice-nemocnice-kadan.html">Petice, 100 milionů a údajný prodej nemocnice</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>'''

RSS_ITEM = '''
    <item>
      <title>Noční výluky vlaků zasáhnou Kadaň, Klášterec i Chomutov</title>
      <description><![CDATA[Od pondělí 27. července budou většinu nočních vlaků mezi Kadaní, Kláštercem a Chomutovem nahrazovat autobusy. Omezení se bude s přestávkami opakovat až do konce srpna.]]></description>
      <link>https://nasekadan.cz/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html</guid>
      <pubDate>Sat, 25 Jul 2026 22:41:00 +0200</pubDate>
      <category>Praktické informace</category>
      <category>Doprava</category>
      <category>Kadaň</category>
      <category>Klášterec nad Ohří</category>
      <szn:image><szn:url>https://nasekadan.cz/social-card.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>
'''

SITEMAP_ENTRY = (
    "  <url><loc>https://nasekadan.cz/clanky/"
    "nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html"
    "</loc><lastmod>2026-07-25</lastmod></url>\n"
)


def read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Chybí soubor {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, content: str) -> bool:
    original = read(path)
    if original == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Opraveno: {path.relative_to(ROOT)}")
    return True


def ensure_home() -> bool:
    html = read(HOME)

    if ".article-card.transport .visual" not in html:
        html = html.replace(
            ".article-card.service .visual{",
            ".article-card.transport .visual{background:linear-gradient(135deg,#162b37,#405f70 58%,#ad5b23)}\n"
            "    .article-card.service .visual{",
            1,
        )

    if "Interní ambulance Nemocnice Kadaň bude od 27. července do 14. srpna uzavřena" in html:
        html = re.sub(
            r'<div class="ticker">.*?</div>\s*</div>',
            '<div class="ticker">\n'
            '  <div class="wrap"><b>DOPRAVNÍ UPOZORNĚNÍ:</b> Od pondělí 27. července se vracejí noční výluky vlaků mezi Kadaní, Kláštercem a Chomutovem. Většinu spojů nahradí autobusy.</div>\n'
            '</div>',
            html,
            count=1,
            flags=re.S,
        )

    hero_match = re.search(r'<article class="lead">(.*?)</article>', html, flags=re.S)
    aside_match = re.search(r'<aside class="current-aside">.*?</aside>', html, flags=re.S)
    hero_contains_software = bool(hero_match and SOFTWARE_PATH in hero_match.group(1))
    aside_contains_ambulance = bool(aside_match and AMBULANCE_PATH in aside_match.group(0))
    if hero_contains_software and aside_contains_ambulance and TRAIN_PATH not in aside_match.group(0):
        html = html[: aside_match.start()] + TRANSPORT_ASIDE + html[aside_match.end() :]

    article_list_split = html.split('<div class="article-list">', 1)
    list_contains_train = len(article_list_split) == 2 and TRAIN_PATH in article_list_split[1]
    if not list_contains_train:
        software_pattern = re.compile(
            r'(<article class="article-card hospital" data-software-card>.*?</article>\s*)',
            flags=re.S,
        )
        html, count = software_pattern.subn(r"\1" + TRANSPORT_CARD, html, count=1)
        if count == 0:
            html = html.replace(
                '<div class="article-list">',
                '<div class="article-list">' + TRANSPORT_CARD,
                1,
            )

    return write_if_changed(HOME, html)


def ensure_archive() -> bool:
    html = read(ARCHIVE)
    if ".archive-item.transport .archive-visual" not in html:
        html = html.replace(
            ".archive-item.service .archive-visual{",
            ".archive-item.transport .archive-visual{background:linear-gradient(135deg,#162b37,#405f70 58%,#ad5b23)}\n"
            "    .archive-item.service .archive-visual{",
            1,
        )

    if TRAIN_PATH not in html:
        software_pattern = re.compile(
            r'(<article class="archive-item hospital" data-software-card>.*?</article>\s*)',
            flags=re.S,
        )
        html, count = software_pattern.subn(r"\1" + TRANSPORT_ARCHIVE, html, count=1)
        if count == 0:
            html = html.replace(
                '<section class="archive-list" aria-label="Chronologický přehled článků">',
                '<section class="archive-list" aria-label="Chronologický přehled článků">' + TRANSPORT_ARCHIVE,
                1,
            )

    return write_if_changed(ARCHIVE, html)


def ensure_sitemap() -> bool:
    xml = read(SITEMAP)
    if TRAIN_URL not in xml:
        software_entry = re.compile(
            r'(  <url><loc>' + re.escape(SOFTWARE_URL) + r'</loc><lastmod>[^<]+</lastmod></url>\n)'
        )
        xml, count = software_entry.subn(r"\1" + SITEMAP_ENTRY, xml, count=1)
        if count == 0:
            marker = re.compile(
                r'(  <url><loc>https://nasekadan\.cz/clanky/</loc><lastmod>[^<]+</lastmod></url>\n)'
            )
            xml, count = marker.subn(r"\1" + SITEMAP_ENTRY, xml, count=1)
        if count == 0:
            raise RuntimeError("Do sitemap.xml se nepodařilo vložit článek o nočních výlukách.")
    return write_if_changed(SITEMAP, xml)


def ensure_rss() -> bool:
    xml = read(RSS)
    if TRAIN_URL not in xml:
        software_item = re.compile(
            r'(<item>.*?' + re.escape(SOFTWARE_URL) + r'.*?</item>\s*)',
            flags=re.S,
        )
        xml, count = software_item.subn(r"\1" + RSS_ITEM, xml, count=1)
        if count == 0:
            anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
            if anchor not in xml:
                raise RuntimeError("V rss.xml chybí kotevní atom:link.")
            xml = xml.replace(anchor, anchor + "\n" + RSS_ITEM, 1)
    return write_if_changed(RSS, xml)


def main() -> int:
    train_file = ROOT / "clanky" / TRAIN_PATH.rsplit("/", 1)[-1]
    if not train_file.is_file():
        raise RuntimeError("Zdrojový článek o nočních výlukách chybí; automatická oprava byla zastavena.")

    changed = [ensure_home(), ensure_archive(), ensure_sitemap(), ensure_rss()]
    print("Obnova publikace dokončena.", "Změny:" if any(changed) else "Beze změn.", sum(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
