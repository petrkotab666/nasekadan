#!/usr/bin/env python3
"""Opraví zařazení historického článku ePetice ve staré šabloně.

Současný web používá automaticky generovanou titulku, stránkovaný archiv a vlastní
JSON-LD ItemList. V tomto režimu skript nesmí vracet starý článek na titulku ani
na první stranu archivu; moderní přehledy spravují obecné publikační generátory.
Podpora staré šablony zůstává zachována pro případ obnovy staršího snapshotu.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"
SITEMAP = ROOT / "sitemap.xml"

EPETICE_PATH = "/clanky/epetice-nemocnice-kadan.html"
EPETICE_URL = "https://nasekadan.cz" + EPETICE_PATH
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, text: str) -> bool:
    original = read(path)
    if original == text:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Opraveno: {path.relative_to(ROOT)}")
    return True


def modern_home(text: str) -> bool:
    return "data-auto-article=" in text


def modern_archive(text: str) -> bool:
    return 'data-nk-archive-schema="1"' in text or "article-pagination" in text


def ensure_home() -> bool:
    text = read(HOME)
    if modern_home(text):
        return False
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
    # Moderní archiv má samostatný top-level ItemList v označeném skriptu a je
    # generován ze všech článků. Historická pojistka jej nesmí ručně přepisovat.
    if modern_archive(text):
        return text

    scripts = list(
        re.finditer(
            r'<script\b([^>]*)type=["\']application/ld\+json["\']([^>]*)>\s*(.*?)\s*</script>',
            text,
            re.I | re.S,
        )
    )
    if not scripts:
        raise RuntimeError("Archiv neobsahuje JSON-LD.")

    selected = None
    data = None
    itemlist = None
    for candidate in scripts:
        try:
            parsed = json.loads(candidate.group(3))
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and parsed.get("@type") == "ItemList":
            selected, data, itemlist = candidate, parsed, parsed
            break
        if isinstance(parsed, dict):
            graph = parsed.get("@graph")
            if isinstance(graph, list):
                found = next(
                    (node for node in graph if isinstance(node, dict) and node.get("@type") == "ItemList"),
                    None,
                )
                if found is not None:
                    selected, data, itemlist = candidate, parsed, found
                    break
    if selected is None or data is None or itemlist is None:
        raise RuntimeError("V JSON-LD archivu chybí ItemList.")

    elements = [item for item in itemlist.get("itemListElement", []) if item.get("url") != EPETICE_URL]
    epetice = {
        "@type": "ListItem",
        "url": EPETICE_URL,
        "name": "Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná",
    }
    weekly_index = next((i for i, item in enumerate(elements) if item.get("url") == WEEKLY_URL), -1)
    elements.insert(weekly_index + 1 if weekly_index >= 0 else 0, epetice)
    for position, item in enumerate(elements, start=1):
        item["position"] = position
    itemlist["itemListElement"] = elements
    itemlist["numberOfItems"] = len(elements)

    attrs = (selected.group(1) + selected.group(2)).strip()
    prefix = f"<script {attrs} type=\"application/ld+json\">" if attrs else '<script type="application/ld+json">'
    replacement = prefix + json.dumps(data, ensure_ascii=False, indent=2) + "</script>"
    return text[: selected.start()] + replacement + text[selected.end() :]


def ensure_archive() -> bool:
    text = read(ARCHIVE)
    if modern_archive(text):
        return False
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
    return write_if_changed(ARCHIVE, text)


def ensure_rss() -> bool:
    text = read(RSS)
    if EPETICE_URL not in text:
        weekly = re.compile(r'(<item>.*?' + re.escape(WEEKLY_URL) + r'.*?</item>\s*)', re.S)
        text, count = weekly.subn(r"\1" + EPETICE_RSS, text, count=1)
        if count == 0:
            marker = "    <item>"
            if marker not in text:
                raise RuntimeError("RSS nemá žádnou položku.")
            text = text.replace(marker, EPETICE_RSS + marker, 1)
    return write_if_changed(RSS, text)


def ensure_sitemap() -> bool:
    text = read(SITEMAP)
    if EPETICE_URL not in text:
        marker = "</urlset>"
        if marker not in text:
            raise RuntimeError("Sitemap nemá uzavírací urlset.")
        addition = f"  <url><loc>{EPETICE_URL}</loc><lastmod>2026-07-26</lastmod></url>\n"
        text = text.replace(marker, addition + marker, 1)
    return write_if_changed(SITEMAP, text)


def enforce_current_articles() -> None:
    """Zařadí všechny aktuální schválené články a srovná jejich pořadí."""
    script = ROOT / "scripts" / "enforce_current_article_order.py"
    required = ROOT / "clanky" / "kolobezky-hriste-detektor-kovu-kadan.html"
    if required.is_file() and script.is_file():
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def main() -> int:
    if not (ROOT / EPETICE_PATH.lstrip("/")).is_file():
        raise RuntimeError(f"Chybí zdrojový článek {EPETICE_PATH}")
    changed = [ensure_home(), ensure_archive(), ensure_rss(), ensure_sitemap()]
    enforce_current_articles()
    print(
        "Zařazení nejnovějších schválených článků dokončeno.",
        "Změny:" if any(changed) else "Beze změn.",
        sum(changed),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
