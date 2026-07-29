#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "pretekajici-kose-kadan-technicke-sluzby-ridici"
PATH = f"/clanky/{SLUG}.html"
URL = "https://nasekadan.cz" + PATH
TITLE = "Přetékající koše v Kadani budí kritiku. Město mluví o odchodu řidičů"
DESCRIPTION = (
    "Přeplněný koš u zahrádkářské kolonie otevřel debatu o svozu odpadu v Kadani. "
    "Starosta popsal odchod řidičů a část lidí upozorňuje i na nevhodné používání malých košů."
)
PUBLISHED_ISO = "2026-07-29T18:53:00+02:00"
SOCIAL_IMAGE = f"https://nasekadan.cz/social/{SLUG}-32f37e0a74.png"

HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
RSS = ROOT / "rss.xml"
SITEMAP = ROOT / "sitemap.xml"
NEWS = ROOT / "news-sitemap.xml"
MANIFEST = ROOT / "production-content-manifest.json"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"

HOME_CARD = f'''<article class="article-card service" data-bins-technical-services-card>
  <div class="visual" style="background:linear-gradient(135deg,#162c38,#5b4740 54%,#a9232b)"><strong>Přetékající koše</strong></div>
  <div class="article-body">
    <span class="meta">29. 7. 2026 · 18:53 · Odpady a technické služby</span>
    <h3>Přetékající koše v Kadani budí kritiku</h3>
    <p>Město mluví o odchodu řidičů. Debata upozorňuje také na domovní a zahrádkářský odpad v malých pouličních koších.</p>
    <a class="read-more" href="{PATH}">Přečíst celý článek →</a>
  </div>
</article>'''

ARCHIVE_CARD = f'''<article class="archive-item service" data-bins-technical-services-card>
  <div class="archive-visual" style="background:linear-gradient(135deg,#162c38,#5b4740 54%,#a9232b)"><strong>Přetékající koše</strong></div>
  <div class="archive-body">
    <span class="archive-meta">29. července 2026 v 18:53 · Odpady a technické služby</span>
    <h2>Přetékající koše v Kadani budí kritiku. Město mluví o odchodu řidičů</h2>
    <p>Obyvatelé upozorňují na více míst. Článek odděluje personální komplikace technických služeb od nevhodného používání malých košů.</p>
    <a href="{PATH}">Přečíst celý článek →</a>
  </div>
</article>'''

RSS_ITEM = f'''<item>
  <title>{TITLE}</title>
  <description><![CDATA[{DESCRIPTION}]]></description>
  <link>{URL}</link>
  <guid isPermaLink="true">{URL}</guid>
  <pubDate>Wed, 29 Jul 2026 18:53:00 +0200</pubDate>
  <category>Kadaň</category>
  <category>Odpady</category>
  <category>Technické služby</category>
  <category>Veřejný prostor</category>
  <szn:image><szn:url>{SOCIAL_IMAGE}</szn:url></szn:image>
  <geo:lat>50.375984</geo:lat>
  <geo:long>13.271307</geo:long>
</item>'''

SITEMAP_ENTRY = f"  <url><loc>{URL}</loc><lastmod>2026-07-29</lastmod></url>\n"
NEWS_ENTRY = f'''  <url>
    <loc>{URL}</loc>
    <news:news>
      <news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication>
      <news:publication_date>{PUBLISHED_ISO}</news:publication_date>
      <news:title>{TITLE}</news:title>
    </news:news>
  </url>\n'''


def read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Chybí soubor {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, text: str) -> bool:
    old = read(path)
    if old == text:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Změněno: {path.relative_to(ROOT)}")
    return True


def ensure_home() -> bool:
    text = read(HOME)
    if PATH not in text.split('<div class="article-list">', 1)[-1]:
        marker = '<div class="article-list">'
        if marker not in text:
            raise RuntimeError("Na titulní stránce chybí seznam článků.")
        text = text.replace(marker, marker + "\n" + HOME_CARD, 1)
    return write_if_changed(HOME, text)


def ensure_archive() -> bool:
    text = read(ARCHIVE)
    section = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if PATH not in text.split(section, 1)[-1]:
        if section not in text:
            raise RuntimeError("V archivu chybí seznam článků.")
        text = text.replace(section, section + "\n" + ARCHIVE_CARD, 1)
    return write_if_changed(ARCHIVE, text)


def ensure_rss() -> bool:
    text = read(RSS)
    if URL not in text:
        anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
        if anchor not in text:
            raise RuntimeError("RSS nemá kotevní atom:link.")
        text = text.replace(anchor, anchor + "\n    " + RSS_ITEM, 1)
    return write_if_changed(RSS, text)


def ensure_sitemap() -> bool:
    text = read(SITEMAP)
    if URL not in text:
        if "</urlset>" not in text:
            raise RuntimeError("Sitemap nemá uzavírací urlset.")
        text = text.replace("</urlset>", SITEMAP_ENTRY + "</urlset>", 1)
    return write_if_changed(SITEMAP, text)


def ensure_news() -> bool:
    text = read(NEWS)
    if URL not in text:
        if "</urlset>" not in text:
            raise RuntimeError("News sitemap nemá uzavírací urlset.")
        text = text.replace("</urlset>", NEWS_ENTRY + "</urlset>", 1)
    return write_if_changed(NEWS, text)


def ensure_manifest() -> bool:
    data = json.loads(read(MANIFEST))
    items = data.setdefault("required_articles", [])
    if not any(item.get("path") == f"clanky/{SLUG}.html" for item in items):
        items.insert(0, {
            "path": f"clanky/{SLUG}.html",
            "needle": "Přetékající koše v Kadani budí kritiku",
            "must_be_on_home": True,
            "must_be_in_archive": True,
        })
    new_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    return write_if_changed(MANIFEST, new_text)


def main() -> int:
    if not ARTICLE.is_file():
        raise RuntimeError(f"Chybí zdrojový článek {ARTICLE.relative_to(ROOT)}")

    changed = [
        ensure_home(),
        ensure_archive(),
        ensure_rss(),
        ensure_sitemap(),
        ensure_news(),
        ensure_manifest(),
    ]

    subprocess.run([sys.executable, "scripts/sort_articles_chronologically.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/enforce_latest_homepage_hero.py"], cwd=ROOT, check=True)

    home = read(HOME)
    archive = read(ARCHIVE)
    if PATH not in home or PATH not in archive or URL not in read(RSS) or URL not in read(SITEMAP):
        raise RuntimeError("Závěrečná kontrola publikace neprošla.")

    print("Článek o přeplněných koších je zařazen na titulce, v archivu, RSS a sitemapách.")
    print("Počet přímo změněných souborů:", sum(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
