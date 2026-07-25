#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_URL = "/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html"


def write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8")
    if old == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def update_home() -> bool:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")

    if ".article-card.service .visual" not in html:
        html = html.replace(
            ".article-card.accident .visual{",
            ".article-card.service .visual{background:linear-gradient(135deg,#173044,#47778a 58%,#a9232b)}\n"
            "    .article-card.accident .visual{",
            1,
        )

    html = re.sub(
        r'<div class="ticker">.*?</div>\s*</div>',
        '<div class="ticker">\n'
        '  <div class="wrap"><b>PRAKTICKÉ UPOZORNĚNÍ:</b> Interní ambulance Nemocnice Kadaň bude od 27. července do 14. srpna uzavřena. Na týden se uzavře také pokladna.</div>\n'
        '</div>',
        html,
        count=1,
        flags=re.S,
    )

    hero = '''  <section class="wrap hero" id="clanky">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(135deg,#173044,#47778a 58%,#a9232b)"><span>NEJNOVĚJŠÍ ZPRÁVA</span><strong>AMBULANCE</strong></div>
      <div class="copy">
        <small>PRAKTICKÉ INFORMACE · ZDRAVOTNICTVÍ · 25. 7. 2026 V 20:42</small>
        <h1>Interní ambulance Nemocnice Kadaň bude tři týdny uzavřená</h1>
        <p>Omezení začne v pondělí 27. července a potrvá do 14. srpna. Nemocnice zároveň na týden uzavře pokladnu pro pacienty a zaměstnance.</p>
        <a class="btn" href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">25. 7. 2026 v 5:00</p>
      <h2>Petice rozjela volební spor kolem nemocnice</h2>
      <p>Prověřili jsme 100 milionů na účtech, cenu kyberbezpečnosti, čekání na refundaci i tvrzení o údajném plánu nemocnici prodat.</p>
      <a class="aside-button" href="/clanky/petice-nemocnice-kadan.html">Přečíst celý článek →</a>
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

    if ARTICLE_URL not in html.split('<div class="article-list">', 1)[1]:
        card = '''      <article class="article-card service">
        <div class="visual"><strong>Omezení ambulance</strong></div>
        <div class="article-body">
          <span class="meta">25. 7. 2026 · 20:42 · Praktické informace</span>
          <h3>Interní ambulance Nemocnice Kadaň bude tři týdny uzavřená</h3>
          <p>Od 27. července do 14. srpna bude uzavřeno ambulantní pracoviště v poliklinice. Pokladna bude zavřená od 27. do 31. července.</p>
          <a class="read-more" href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
        </div>
      </article>

'''
        html = html.replace('    <div class="article-list">\n', '    <div class="article-list">\n' + card, 1)

    return write_if_changed(path, html)


def update_archive() -> bool:
    path = ROOT / "clanky" / "index.html"
    html = path.read_text(encoding="utf-8")
    if ".archive-item.service .archive-visual" not in html:
        html = html.replace(
            ".archive-item.accident .archive-visual{",
            ".archive-item.service .archive-visual{background:linear-gradient(135deg,#173044,#47778a 58%,#a9232b)}\n"
            "    .archive-item.accident .archive-visual{",
            1,
        )
    if ARTICLE_URL not in html:
        item = '''    <article class="archive-item service">
      <div class="archive-visual"><strong>Omezení ambulance</strong></div>
      <div class="archive-body">
        <span class="archive-meta">25. července 2026 v 20:42 · Praktické informace a zdravotnictví</span>
        <h2>Interní ambulance Nemocnice Kadaň bude tři týdny uzavřená</h2>
        <p>Ambulantní pracoviště v kadaňské poliklinice bude od 27. července do 14. srpna uzavřeno. Nemocnice zároveň oznámila týdenní uzavření pokladny.</p>
        <a href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      </div>
    </article>

'''
        html = html.replace(
            '  <section class="archive-list" aria-label="Chronologický přehled článků">\n',
            '  <section class="archive-list" aria-label="Chronologický přehled článků">\n' + item,
            1,
        )
    return write_if_changed(path, html)


def update_sitemap() -> bool:
    path = ROOT / "sitemap.xml"
    xml = path.read_text(encoding="utf-8")
    entry = '  <url><loc>https://nasekadan.cz/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html</loc><lastmod>2026-07-25</lastmod></url>\n'
    if "interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html" not in xml:
        xml = xml.replace(
            '  <url><loc>https://nasekadan.cz/clanky/</loc><lastmod>2026-07-25</lastmod></url>\n',
            '  <url><loc>https://nasekadan.cz/clanky/</loc><lastmod>2026-07-25</lastmod></url>\n' + entry,
            1,
        )
    return write_if_changed(path, xml)


def update_rss() -> bool:
    path = ROOT / "rss.xml"
    xml = path.read_text(encoding="utf-8")
    xml = re.sub(
        r'<lastBuildDate>.*?</lastBuildDate>',
        '<lastBuildDate>Sat, 25 Jul 2026 20:42:00 +0200</lastBuildDate>',
        xml,
        count=1,
    )
    if "interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html" not in xml:
        item = '''    <item>
      <title>Interní ambulance Nemocnice Kadaň bude tři týdny uzavřená</title>
      <description><![CDATA[Ambulantní pracoviště v kadaňské poliklinice bude od 27. července do 14. srpna uzavřeno. Pokladna nemocnice bude zavřená od 27. do 31. července.]]></description>
      <link>https://nasekadan.cz/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html</link>
      <guid isPermaLink="true">https://nasekadan.cz/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html</guid>
      <pubDate>Sat, 25 Jul 2026 20:42:00 +0200</pubDate>
      <category>Praktické informace</category>
      <category>Zdravotnictví</category>
      <category>Kadaň</category>
      <category>Nemocnice Kadaň</category>
      <szn:image><szn:url>https://nasekadan.cz/social-card.png</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>

'''
        xml = xml.replace('    <item>\n', item + '    <item>\n', 1)
    return write_if_changed(path, xml)


if __name__ == "__main__":
    changed = [update_home(), update_archive(), update_sitemap(), update_rss()]
    article = ROOT / "clanky" / "interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html"
    assert article.is_file()
    assert ARTICLE_URL in (ROOT / "index.html").read_text(encoding="utf-8")
    assert ARTICLE_URL in (ROOT / "clanky" / "index.html").read_text(encoding="utf-8")
    assert "interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html" in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html" in (ROOT / "rss.xml").read_text(encoding="utf-8")
    print("Praktická zpráva o interní ambulanci je zařazena.", any(changed))
