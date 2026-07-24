#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = "/clanky/slovan-lavka-shell-kadan.html"


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def restore_homepage() -> None:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    html = html.replace(
        ".article-card.slovan .visual{background:linear-gradient(135deg,#14232d,#75604b 60%,#a9232b)}\n    ",
        "",
    )
    html = re.sub(
        r'<div class="ticker">.*?</div>\s*</div>',
        '<div class="ticker">\n'
        '  <div class="wrap"><b>AKTUALIZOVÁNO:</b> Nehoda se zraněním se stala v Prunéřově. Podle hasičského zpravodajského servisu se střetlo osobní a nákladní vozidlo.</div>\n'
        '</div>',
        html,
        count=1,
        flags=re.S,
    )
    hero = '''  <section class="wrap hero" id="clanky">
    <article class="lead">
      <div class="photo"><span>NEJNOVĚJŠÍ ČLÁNEK</span><strong>NEHODA</strong></div>
      <div class="copy">
        <small>DOPRAVA · SLOŽKY IZS · AKTUALIZOVÁNO 24. 7. 2026 V 18:48</small>
        <h1>V Prunéřově se střetlo osobní a nákladní auto. Nehoda byla hlášena se zraněním</h1>
        <p>Krajský portál potvrdil nehodu v 11:26. Novější informace upřesnily místo na Prunéřov a střet osobního s nákladním vozidlem; počet zraněných zatím znám není.</p>
        <a class="btn" href="/clanky/dopravni-nehoda-se-zranenim-kadan-24-cervence-2026.html">Přečíst aktualizovaný článek →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">Aktualizováno 24. 7. 2026 ve 12:13</p>
      <h2>Internet a televize v Kadani opět fungují</h2>
      <p>Služby KTK byly během dopoledne obnoveny. Policie dál prověřuje poškození páteřní optické trasy u stavby horkovodu.</p>
      <a class="aside-button" href="/clanky/vypadek-internetu-kadan-kradez-kabelu.html">Přečíst článek o výpadku →</a>
      <div class="aside-links">
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
    html = re.sub(
        r'\s*<article class="article-card slovan">.*?</article>\s*',
        "\n",
        html,
        count=1,
        flags=re.S,
    )
    write(path, html)


def restore_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    html = path.read_text(encoding="utf-8")
    html = html.replace(
        ".archive-item.slovan .archive-visual{background:linear-gradient(135deg,#14232d,#75604b 60%,#a9232b)}\n    ",
        "",
    )
    html = re.sub(
        r'\s*<article class="archive-item slovan">.*?</article>\s*',
        "\n",
        html,
        count=1,
        flags=re.S,
    )
    write(path, html)


def restore_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    xml = path.read_text(encoding="utf-8")
    xml = re.sub(
        r'\s*<url><loc>https://nasekadan\.cz/clanky/slovan-lavka-shell-kadan\.html</loc><lastmod>2026-07-24</lastmod></url>\s*',
        "\n",
        xml,
        count=1,
    )
    write(path, xml)


def remove_public_files() -> None:
    paths = [
        ROOT / "clanky" / "slovan-lavka-shell-kadan.html",
        ROOT / "slovan-article.js",
        ROOT / "slovan-article.css",
        ROOT / "assets" / "slovan-lavka-hero-20260724.jpg",
        ROOT / "assets" / "slovan-detail-20260724.jpg",
        ROOT / "assets" / "lavka-shell-20260724.jpg",
        ROOT / "assets" / "slovan-vstup-20260724.jpg",
    ]
    for path in paths:
        if path.exists():
            path.unlink()
    parts = ROOT / ".image-parts"
    if parts.exists():
        shutil.rmtree(parts)


def restore_dockerfile() -> None:
    path = ROOT / "Dockerfile"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'\n# Z jednotlivých textových částí sestavit ověřené fotografie.*?python3 /usr/share/nginx/html/scripts/publish_slovan\.py\n',
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    write(path, text)


if __name__ == "__main__":
    restore_homepage()
    restore_archive()
    restore_sitemap()
    remove_public_files()
    restore_dockerfile()
    print("Rozpracovaný článek Slovanu a lávky byl stažen z veřejné části webu.")
