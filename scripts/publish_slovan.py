#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = "/clanky/slovan-lavka-shell-kadan.html"

PHOTOS = {
    "slovan-lavka-hero-20260724": (3, "6fd5d7171cba8577f6401e7b40cea4d9657a78b4ad4862faafc2b94bfa97edfd"),
    "slovan-detail-20260724": (2, "1a10fd44da4f611f0d04baff2e18a6003ec180c06b13e90ac83b942871dee963"),
    "lavka-shell-20260724": (2, "a29657c7c695aa7c43272576c0abaaf99de72be81527ef9e82fa447322e93adb"),
    "slovan-vstup-20260724": (2, "3e7ca08bdf7bc7912a9539ba10c14845b12bbf359fa9447c62bb7e6bc6e90746"),
}

def write_if_changed(path: Path, content: str) -> None:
    if path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")

def build_photos() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    parts_dir = ROOT / ".image-parts"
    for base, (count, expected) in PHOTOS.items():
        chunks = []
        for index in range(1, count + 1):
            part = parts_dir / f"{base}.part-{index:02d}"
            chunks.append("".join(part.read_text(encoding="utf-8").split()))
        data = base64.b64decode("".join(chunks), validate=True)
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected:
            raise RuntimeError(f"Kontrolní součet fotografie {base} nesouhlasí: {digest}")
        (assets / f"{base}.jpg").write_bytes(data)

def publish_homepage() -> None:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    if ".article-card.slovan .visual" not in html:
        html = html.replace(
            ".article-card.accident .visual{",
            ".article-card.slovan .visual{background:linear-gradient(135deg,#14232d,#75604b 60%,#a9232b)}\n"
            "    .article-card.accident .visual{",
            1,
        )
    html = re.sub(
        r'<div class="ticker">.*?</div>\s*</div>',
        '<div class="ticker">\n'
        '  <div class="wrap"><b>NOVÁ ANALÝZA:</b> Jáma po Slovanu a lávka u Shellu. Veřejné smlouvy ukazují desítky milionů, ale úplný účet první etapy Slovanu stále chybí.</div>\n'
        '</div>',
        html,
        count=1,
        flags=re.S,
    )
    hero = '''  <section class="wrap hero" id="clanky">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(135deg,#14232d,#75604b 60%,#a9232b)"><span>NEJNOVĚJŠÍ ANALÝZA</span><strong>JÁMA A MOST</strong></div>
      <div class="copy">
        <small>VEŘEJNÉ INVESTICE · SLOVAN · LÁVKA · 24. 7. 2026 V 20:43</small>
        <h1>Jáma po Slovanu a lávka u Shellu: kolik stály dvě stavby, které se staly symbolem sporu</h1>
        <p>Aktuální fotografie a veřejné smlouvy ukazují, co se stalo se Slovanem, kolik stojí lávka u Shellu a proč nelze dosavadní částky jednoduše sečíst.</p>
        <a class="btn" href="/clanky/slovan-lavka-shell-kadan.html">Přečíst celou analýzu →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">Aktualizováno 24. 7. 2026 v 18:48</p>
      <h2>V Prunéřově se střetlo osobní a nákladní auto</h2>
      <p>Nehoda byla hlášena se zraněním. Počet zraněných, příčina a případné omezení dopravy zatím zveřejněny nebyly.</p>
      <a class="aside-button" href="/clanky/dopravni-nehoda-se-zranenim-kadan-24-cervence-2026.html">Přečíst článek o nehodě →</a>
      <div class="aside-links">
        <a href="/clanky/vypadek-internetu-kadan-kradez-kabelu.html">Výpadek internetu a poškozená optika</a>
        <a href="/clanky/nemocnice-kadan.html">Analýza Nemocnice Kadaň</a>
        <a href="/clanky/">Všechny články podle data</a>
      </div>
    </aside>
  </section>'''
    html = re.sub(
        r'  <section class="wrap hero" id="clanky">.*?  </section>',
        hero,
        html,
        count=1,
        flags=re.S,
    )
    if 'href="/clanky/slovan-lavka-shell-kadan.html"' not in html.split('<div class="article-list">', 1)[1]:
        card = '''      <article class="article-card slovan">
        <div class="visual"><strong>Slovan a lávka</strong></div>
        <div class="article-body">
          <span class="meta">24. 7. 2026 · Veřejné investice</span>
          <h3>Jáma po Slovanu a lávka u Shellu: kolik stály dvě stavby</h3>
          <p>Původní projekt Slovanu skončil po demolici, nový se právě soutěží. Hlavní smlouva na lávku činí 26,15 milionu korun s DPH.</p>
          <a class="read-more" href="/clanky/slovan-lavka-shell-kadan.html">Přečíst celou analýzu →</a>
        </div>
      </article>

'''
        html = html.replace('    <div class="article-list">\n', '    <div class="article-list">\n' + card, 1)
    write_if_changed(path, html)

def publish_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    html = path.read_text(encoding="utf-8")
    if ".archive-item.slovan .archive-visual" not in html:
        html = html.replace(
            ".archive-item.accident .archive-visual{",
            ".archive-item.slovan .archive-visual{background:linear-gradient(135deg,#14232d,#75604b 60%,#a9232b)}\n"
            "    .archive-item.accident .archive-visual{",
            1,
        )
    if ARTICLE not in html:
        item = '''    <article class="archive-item slovan">
      <div class="archive-visual"><strong>Slovan a lávka</strong></div>
      <div class="archive-body">
        <span class="archive-meta">24. července 2026 · 20:43 · Veřejné investice</span>
        <h2>Jáma po Slovanu a lávka u Shellu: kolik stály dvě stavby, které se staly symbolem sporu</h2>
        <p>Aktuální fotografie, smlouvy a časová osa ukazují, proč původní projekt Slovanu skončil po demolici, co se soutěží znovu a kolik stojí lávka u Shellu.</p>
        <a href="/clanky/slovan-lavka-shell-kadan.html">Přečíst celou analýzu →</a>
      </div>
    </article>

'''
        html = html.replace(
            '  <section class="archive-list" aria-label="Chronologický přehled článků">\n',
            '  <section class="archive-list" aria-label="Chronologický přehled článků">\n' + item,
            1,
        )
    write_if_changed(path, html)

def publish_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    xml = path.read_text(encoding="utf-8")
    url = '  <url><loc>https://nasekadan.cz/clanky/slovan-lavka-shell-kadan.html</loc><lastmod>2026-07-24</lastmod></url>\n'
    if "slovan-lavka-shell-kadan.html" not in xml:
        xml = xml.replace(
            '  <url><loc>https://nasekadan.cz/clanky/</loc><lastmod>2026-07-24</lastmod></url>\n',
            '  <url><loc>https://nasekadan.cz/clanky/</loc><lastmod>2026-07-24</lastmod></url>\n' + url,
            1,
        )
    write_if_changed(path, xml)

if __name__ == "__main__":
    build_photos()
    publish_homepage()
    publish_archive()
    publish_sitemap()
    print("Slovan, lávka, fotografie, homepage, archiv a sitemap jsou připravené.")
