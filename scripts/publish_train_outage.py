#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_URL = "/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html"


def write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8")
    if old == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def update_home() -> bool:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")

    if ".article-card.transport .visual" not in html:
        html = html.replace(
            ".article-card.service .visual{",
            ".article-card.transport .visual{background:linear-gradient(135deg,#162b37,#405f70 58%,#ad5b23)}\n"
            "    .article-card.service .visual{",
            1,
        )

    html = re.sub(
        r'<div class="ticker">.*?</div>\s*</div>',
        '<div class="ticker">\n'
        '  <div class="wrap"><b>DOPRAVNÍ UPOZORNĚNÍ:</b> Od pondělí 27. července se vracejí noční výluky vlaků mezi Kadaní, Kláštercem a Chomutovem. Většinu spojů nahradí autobusy.</div>\n'
        '</div>',
        html,
        count=1,
        flags=re.S,
    )

    hero = '''  <section class="wrap hero" id="clanky">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(135deg,#162b37,#405f70 58%,#ad5b23)"><span>NEJNOVĚJŠÍ ZPRÁVA</span><strong>VÝLUKA</strong></div>
      <div class="copy">
        <small>PRAKTICKÉ INFORMACE · DOPRAVA · 25. 7. 2026 V 22:41</small>
        <h1>Noční výluky vlaků zasáhnou Kadaň, Klášterec i Chomutov</h1>
        <p>Od pondělí večer nahradí většinu nočních vlaků autobusy. Omezení se bude s přestávkami opakovat až do konce srpna.</p>
        <a class="btn" href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">25. 7. 2026 v 20:42</p>
      <h2>Interní ambulance Nemocnice Kadaň bude tři týdny uzavřená</h2>
      <p>Omezení začne 27. července a potrvá do 14. srpna. Klášterecké pracoviště má podle zveřejněných údajů dál běžnou ordinační dobu.</p>
      <a class="aside-button" href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      <div class="aside-links">
        <a href="/clanky/petice-nemocnice-kadan.html">Petice a Nemocnice Kadaň</a>
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
        card = '''      <article class="article-card transport">
        <div class="visual"><strong>Noční výluky vlaků</strong></div>
        <div class="article-body">
          <span class="meta">25. 7. 2026 · 22:41 · Doprava</span>
          <h3>Noční výluky zasáhnou Kadaň, Klášterec i Chomutov</h3>
          <p>Od 27. července nahradí většinu nočních vlaků autobusy. Omezení se bude s přestávkami opakovat také během srpna.</p>
          <a class="read-more" href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
        </div>
      </article>

'''
        html = html.replace('    <div class="article-list">\n', '    <div class="article-list">\n' + card, 1)

    return write_if_changed(path, html)


def update_archive() -> bool:
    path = ROOT / "clanky" / "index.html"
    html = path.read_text(encoding="utf-8")
    if ".archive-item.transport .archive-visual" not in html:
        html = html.replace(
            ".archive-item.service .archive-visual{",
            ".archive-item.transport .archive-visual{background:linear-gradient(135deg,#162b37,#405f70 58%,#ad5b23)}\n"
            "    .archive-item.service .archive-visual{",
            1,
        )
    if ARTICLE_URL not in html:
        item = '''    <article class="archive-item transport">
      <div class="archive-visual"><strong>Noční výluky vlaků</strong></div>
      <div class="archive-body">
        <span class="archive-meta">25. července 2026 v 22:41 · Praktické informace a doprava</span>
        <h2>Noční výluky vlaků zasáhnou Kadaň, Klášterec i Chomutov</h2>
        <p>Od pondělí 27. července budou většinu nočních vlaků nahrazovat autobusy. Výlukové bloky jsou naplánované s přestávkami až do konce srpna.</p>
        <a href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
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
    entry = '  <url><loc>https://nasekadan.cz/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html</loc><lastmod>2026-07-25</lastmod></url>\n'
    if "nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html" not in xml:
        marker = re.search(r'  <url><loc>https://nasekadan.cz/clanky/</loc><lastmod>[^<]+</lastmod></url>\n', xml)
        if not marker:
            raise RuntimeError("V sitemapě chybí položka archivu článků")
        xml = xml[:marker.end()] + entry + xml[marker.end():]
    return write_if_changed(path, xml)


def update_rss() -> bool:
    path = ROOT / "rss.xml"
    xml = path.read_text(encoding="utf-8")
    xml = re.sub(
        r'<lastBuildDate>.*?</lastBuildDate>',
        '<lastBuildDate>Sat, 25 Jul 2026 22:41:00 +0200</lastBuildDate>',
        xml,
        count=1,
    )
    if "nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html" not in xml:
        item = '''    <item>
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
        xml = xml.replace('    <item>\n', item + '    <item>\n', 1)
    return write_if_changed(path, xml)


if __name__ == "__main__":
    changed = [update_home(), update_archive(), update_sitemap(), update_rss()]
    article = ROOT / "clanky" / "nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html"
    assert article.is_file()
    assert ARTICLE_URL in (ROOT / "index.html").read_text(encoding="utf-8")
    assert ARTICLE_URL in (ROOT / "clanky" / "index.html").read_text(encoding="utf-8")
    assert "nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html" in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html" in (ROOT / "rss.xml").read_text(encoding="utf-8")
    print("Praktická zpráva o nočních výlukách je zařazena.", any(changed))
