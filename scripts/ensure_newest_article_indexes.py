#!/usr/bin/env python3
"""Opraví zařazení nejnovějších článků do všech veřejných přehledů.

Skript je idempotentní. Slouží jako pojistka proti situaci, kdy vznikne článek,
ale následný automat přepíše titulní stránku, archiv nebo RSS starší verzí.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"
SITEMAP = ROOT / "sitemap.xml"

EPETICE_PATH = "/clanky/epetice-nemocnice-kadan.html"
EPETICE_URL = "https://nasekadan.cz" + EPETICE_PATH
POOL_PATH = "/clanky/pozemky-koupaliste-kadan.html"
POOL_URL = "https://nasekadan.cz" + POOL_PATH
WEEKLY_URL = "https://nasekadan.cz/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html"

EPETICE_HOME = '''
      <article class="article-card hospital" data-epetice-card>
        <div class="visual" style="background:linear-gradient(135deg,#14232d,#355d70 58%,#9f2626)"><strong>ePetice za nemocnici</strong></div>
        <div class="article-body">
          <span class="meta">26. 7. 2026 · 10:15 · Mimořádně</span>
          <h3>Papírová a elektronická verze musí být stejná</h3>
          <p>Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze elektronické a listinné podpisy vykazovat společně.</p>
          <a class="read-more" href="/clanky/epetice-nemocnice-kadan.html">Přečíst vysvětlení →</a>
        </div>
      </article>
'''

EPETICE_ARCHIVE = '''
    <article class="archive-item hospital" data-epetice-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#14232d,#355d70 58%,#9f2626)"><strong>ePetice za nemocnici</strong></div>
      <div class="archive-body">
        <span class="archive-meta">26. července 2026 v 10:15 · Mimořádně · Petice a nemocnice</span>
        <h2>Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná</h2>
        <p>Vysvětlení limitu 3500 znaků, podmínky totožného znění, ověřování podpisů a právních účinků oficiální ePetice.</p>
        <a href="/clanky/epetice-nemocnice-kadan.html">Přečíst mimořádný článek →</a>
      </div>
    </article>
'''

POOL_ARCHIVE = '''
    <article class="archive-item property" data-pool-land-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#173b37,#3f7168 58%,#b58b25)"><strong>Pozemky koupaliště</strong></div>
      <div class="archive-body">
        <span class="archive-meta">23. července 2026 · Majetek · Ověřujeme</span>
        <h2>Pět pozemků v areálu koupaliště změnilo majitele. Co přesně stát prodal?</h2>
        <p>Stát prodal pět pozemků o celkové výměře 2 093 m² za 3,6 milionu korun. Veřejné dokumenty ukazují vazbu k provozovateli koupaliště, jméno kupujícího ale zveřejněno nebylo.</p>
        <a href="/clanky/pozemky-koupaliste-kadan.html">Přečíst ověření →</a>
      </div>
    </article>
'''

EPETICE_RSS = '''    <item>
      <title>Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná</title>
      <description><![CDATA[Vysvětlujeme limit 3500 znaků, podmínku totožného listinného a elektronického textu, ověřování podpisů i právní účinky oficiální ePetice.]]></description>
      <link>https://nasekadan.cz/clanky/epetice-nemocnice-kadan.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/epetice-nemocnice-kadan.html</guid>
      <pubDate>Sun, 26 Jul 2026 10:15:00 +0200</pubDate>
      <category>Nemocnice Kadaň</category>
      <category>Petice</category>
      <category>Komunální politika</category>
      <category>eGovernment</category>
      <szn:image><szn:url>https://nasekadan.cz/social/epetice-nemocnice-kadan-71560a0788.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>

'''

POOL_RSS = '''    <item>
      <title>Pět pozemků v areálu koupaliště změnilo majitele</title>
      <description><![CDATA[Stát prodal pět pozemků v areálu koupaliště Kadaň za 3,6 milionu korun. Veřejné podklady ukazují vazbu k Tepelnému hospodářství Kadaň, kupující ale nebyl oficiálně zveřejněn.]]></description>
      <link>https://nasekadan.cz/clanky/pozemky-koupaliste-kadan.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/pozemky-koupaliste-kadan.html</guid>
      <pubDate>Thu, 23 Jul 2026 12:00:00 +0200</pubDate>
      <category>Majetek</category>
      <category>Koupaliště</category>
      <category>Kadaň</category>
      <szn:image><szn:url>https://nasekadan.cz/social-preview.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>

'''


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, text: str) -> bool:
    original = read(path)
    if original == text:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Opraveno: {path.relative_to(ROOT)}")
    return True


def ensure_home() -> bool:
    text = read(HOME)
    article_section = text.split('<div class="article-list">', 1)
    if len(article_section) != 2:
        raise RuntimeError("Na titulní stránce chybí seznam článků.")
    if EPETICE_PATH not in article_section[1]:
        marker = "      <!-- WEEKLY-EVENTS-END -->"
        if marker in text:
            text = text.replace(marker, marker + "\n" + EPETICE_HOME, 1)
        else:
            text = text.replace('<div class="article-list">', '<div class="article-list">' + EPETICE_HOME, 1)
    return write_if_changed(HOME, text)


def update_archive_jsonld(text: str) -> str:
    match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)
    if not match:
        raise RuntimeError("Archiv neobsahuje JSON-LD.")
    data = json.loads(match.group(1))
    itemlist = next((item for item in data.get("@graph", []) if item.get("@type") == "ItemList"), None)
    if itemlist is None:
        raise RuntimeError("V JSON-LD archivu chybí ItemList.")

    elements = [
        item
        for item in itemlist.get("itemListElement", [])
        if item.get("url") not in {EPETICE_URL, POOL_URL}
    ]
    epetice = {
        "@type": "ListItem",
        "url": EPETICE_URL,
        "name": "Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná",
    }
    pool = {
        "@type": "ListItem",
        "url": POOL_URL,
        "name": "Pět pozemků v areálu koupaliště změnilo majitele",
    }

    weekly_index = next((i for i, item in enumerate(elements) if item.get("url") == WEEKLY_URL), -1)
    elements.insert(weekly_index + 1 if weekly_index >= 0 else 0, epetice)
    elements.append(pool)
    for position, item in enumerate(elements, start=1):
        item["position"] = position
    itemlist["itemListElement"] = elements
    itemlist["numberOfItems"] = len(elements)

    replacement = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + "</script>"
    return text[: match.start()] + replacement + text[match.end() :]


def ensure_archive() -> bool:
    text = read(ARCHIVE)
    text = update_archive_jsonld(text)

    if EPETICE_PATH not in text.split('<section class="archive-list"', 1)[-1]:
        marker = "    <!-- WEEKLY-EVENTS-END -->"
        if marker in text:
            text = text.replace(marker, marker + "\n" + EPETICE_ARCHIVE, 1)
        else:
            text = text.replace(
                '<section class="archive-list" aria-label="Chronologický přehled článků">',
                '<section class="archive-list" aria-label="Chronologický přehled článků">' + EPETICE_ARCHIVE,
                1,
            )

    archive_section_end = "  </section>\n\n  <div class=\"archive-rule\">"
    if POOL_PATH not in text.split('<section class="archive-list"', 1)[-1]:
        if archive_section_end not in text:
            raise RuntimeError("V archivu nebyl nalezen konec seznamu článků.")
        text = text.replace(archive_section_end, POOL_ARCHIVE + archive_section_end, 1)

    return write_if_changed(ARCHIVE, text)


def ensure_rss() -> bool:
    text = read(RSS)
    if EPETICE_URL not in text:
        weekly = re.compile(r'(<item>.*?' + re.escape(WEEKLY_URL) + r'.*?</item>\s*)', re.S)
        text, count = weekly.subn(r"\1" + EPETICE_RSS, text, count=1)
        if count == 0:
            marker = '    <item>'
            if marker not in text:
                raise RuntimeError("RSS nemá žádnou položku.")
            text = text.replace(marker, EPETICE_RSS + marker, 1)

    if POOL_URL not in text:
        marker = "  </channel>"
        if marker not in text:
            raise RuntimeError("RSS nemá uzavírací channel.")
        text = text.replace(marker, POOL_RSS + marker, 1)
    return write_if_changed(RSS, text)


def ensure_sitemap() -> bool:
    text = read(SITEMAP)
    additions: list[str] = []
    if EPETICE_URL not in text:
        additions.append(f"  <url><loc>{EPETICE_URL}</loc><lastmod>2026-07-26</lastmod></url>\n")
    if POOL_URL not in text:
        additions.append(f"  <url><loc>{POOL_URL}</loc><lastmod>2026-07-23</lastmod></url>\n")
    if additions:
        marker = "</urlset>"
        if marker not in text:
            raise RuntimeError("Sitemap nemá uzavírací urlset.")
        text = text.replace(marker, "".join(additions) + marker, 1)
    return write_if_changed(SITEMAP, text)


def main() -> int:
    for relative in (EPETICE_PATH, POOL_PATH):
        if not (ROOT / relative.lstrip("/")).is_file():
            raise RuntimeError(f"Chybí zdrojový článek {relative}")
    changed = [ensure_home(), ensure_archive(), ensure_rss(), ensure_sitemap()]
    print("Zařazení nejnovějších článků dokončeno.", "Změny:" if any(changed) else "Beze změn.", sum(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
