#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / ".github" / "drafts" / "slovan-druhy-pokus.html"
ARTICLE = ROOT / "clanky" / "slovan-druhy-pokus.html"
PREVIEW = ROOT / "nahled" / "slovan-druhy-pokus-5b7c2a.html"
ARTICLE_URL = "/clanky/slovan-druhy-pokus.html"
TITLE = "Slovan podruhé: Kadaň chystá 48 bytů za 195 milionů. Účet prvního pokusu stále chybí"
DESCRIPTION = "Kadaň připravuje nový Slovan se 48 byty. Veřejnost ale stále nezná úplné vypořádání první stavby ani přesný osud dotace SFPI."
TZ = ZoneInfo("Europe/Prague")
MONTHS = {
    1: "LEDNA", 2: "ÚNORA", 3: "BŘEZNA", 4: "DUBNA", 5: "KVĚTNA", 6: "ČERVNA",
    7: "ČERVENCE", 8: "SRPNA", 9: "ZÁŘÍ", 10: "ŘÍJNA", 11: "LISTOPADU", 12: "PROSINCE",
}
MONTHS_LOWER = {
    1: "ledna", 2: "února", 3: "března", 4: "dubna", 5: "května", 6: "června",
    7: "července", 8: "srpna", 9: "září", 10: "října", 11: "listopadu", 12: "prosince",
}


def write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def prepare_article(now: datetime) -> bool:
    if ARTICLE.exists():
        print("Článek už je publikovaný.")
        return False
    if not DRAFT.is_file() or DRAFT.stat().st_size == 0:
        raise SystemExit("Chybí neprázdný návrh článku.")

    text = DRAFT.read_text(encoding="utf-8")
    text = text.replace(
        "noindex,nofollow",
        "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1",
    )
    text = text.replace("../../", "../")
    date_label = f"{now.day}. {MONTHS[now.month]} {now.year} · {now:%H:%M}"
    text = text.replace("PŘIPRAVOVANÝ ČLÁNEK", date_label)
    text = re.sub(
        r'<div class="sidebox preview-note">.*?</div>',
        "",
        text,
        count=1,
        flags=re.S,
    )

    iso = now.isoformat(timespec="seconds")
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": TITLE,
        "description": DESCRIPTION,
        "datePublished": iso,
        "dateModified": iso,
        "author": {"@type": "Organization", "name": "Naše Kadaň"},
        "publisher": {"@type": "Organization", "name": "Naše Kadaň"},
        "image": "https://nasekadan.cz/assets/slovan-detail-20260724.jpg",
        "mainEntityOfPage": "https://nasekadan.cz/clanky/slovan-druhy-pokus.html",
    }
    schema_tag = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    text = text.replace("</head>", schema_tag + "\n</head>", 1)
    return write_if_changed(ARTICLE, text)


def update_home(now: datetime) -> bool:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    if ".article-card.slovan .visual" not in html:
        html = html.replace(
            ".article-card.service .visual{",
            ".article-card.slovan .visual{background:linear-gradient(135deg,rgba(18,35,45,.18),rgba(159,38,38,.28)),url('/assets/slovan-detail-20260724.jpg') center/cover}\n"
            "    .article-card.service .visual{",
            1,
        )

    display = f"{now.day}. {now.month}. {now.year} V {now:%H:%M}"
    aside_date = f"25. 7. 2026 v 20:42"
    hero = f'''  <section class="wrap hero" id="clanky">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(135deg,rgba(18,35,45,.20),rgba(159,38,38,.28)),url('/assets/slovan-detail-20260724.jpg') center/cover"><span>INVESTICE A BYDLENÍ</span><strong>SLOVAN</strong></div>
      <div class="copy">
        <small>INVESTICE · BYDLENÍ · VEŘEJNÉ PENÍZE · {display}</small>
        <h1>Slovan podruhé: Kadaň chystá 48 bytů za 195 milionů</h1>
        <p>První stavba skončila demolicí a ukončením smlouvy. Nový tendr už běží, úplný účet prvního pokusu a přesný osud podpory SFPI však veřejnost stále nezná.</p>
        <a class="btn" href="{ARTICLE_URL}">Přečíst celou analýzu →</a>
      </div>
    </article>

    <aside class="current-aside">
      <p class="aside-label">PŘEDCHOZÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">{aside_date}</p>
      <h2>Interní ambulance Nemocnice Kadaň bude tři týdny uzavřená</h2>
      <p>Omezení začne 27. července a potrvá do 14. srpna. Na týden se uzavře také pokladna nemocnice.</p>
      <a class="aside-button" href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Přečíst praktické informace →</a>
      <div class="aside-links">
        <a href="/clanky/petice-nemocnice-kadan.html">Petice a volební spor kolem nemocnice</a>
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
        card = f'''      <article class="article-card slovan">
        <div class="visual"><strong>Slovan podruhé</strong></div>
        <div class="article-body">
          <span class="meta">{now.day}. {now.month}. {now.year} · {now:%H:%M} · Investice a bydlení</span>
          <h3>Kadaň chystá 48 bytů za 195 milionů. Účet prvního pokusu stále chybí</h3>
          <p>Co se stalo s původní stavbou, kolik už Slovan nejméně stál a proč není jasný přesný osud podpory SFPI.</p>
          <a class="read-more" href="{ARTICLE_URL}">Přečíst celou analýzu →</a>
        </div>
      </article>

'''
        html = html.replace('    <div class="article-list">\n', '    <div class="article-list">\n' + card, 1)
    return write_if_changed(path, html)


def update_archive(now: datetime) -> bool:
    path = ROOT / "clanky" / "index.html"
    html = path.read_text(encoding="utf-8")
    if ".archive-item.slovan .archive-visual" not in html:
        html = html.replace(
            ".archive-item.service .archive-visual{",
            ".archive-item.slovan .archive-visual{background:linear-gradient(135deg,rgba(18,35,45,.18),rgba(159,38,38,.28)),url('/assets/slovan-detail-20260724.jpg') center/cover}\n"
            "    .archive-item.service .archive-visual{",
            1,
        )
    if ARTICLE_URL not in html:
        item = f'''    <article class="archive-item slovan">
      <div class="archive-visual"><strong>Slovan podruhé</strong></div>
      <div class="archive-body">
        <span class="archive-meta">{now.day}. {MONTHS_LOWER[now.month]} {now.year} v {now:%H:%M} · Investice, bydlení a veřejné peníze</span>
        <h2>Slovan podruhé: Kadaň chystá 48 bytů za 195 milionů. Účet prvního pokusu stále chybí</h2>
        <p>Původní rekonstrukce skončila demolicí a ukončením smlouvy. Město připravuje nový dům, ale úplné vypořádání první stavby veřejné není.</p>
        <a href="{ARTICLE_URL}">Přečíst celou analýzu →</a>
      </div>
    </article>

'''
        html = html.replace(
            '  <section class="archive-list" aria-label="Chronologický přehled článků">\n',
            '  <section class="archive-list" aria-label="Chronologický přehled článků">\n' + item,
            1,
        )
    return write_if_changed(path, html)


def update_rss(now: datetime) -> bool:
    path = ROOT / "rss.xml"
    xml = path.read_text(encoding="utf-8")
    rfc = format_datetime(now)
    xml = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{rfc}</lastBuildDate>', xml, count=1)
    if "slovan-druhy-pokus.html" not in xml:
        item = f'''    <item>
      <title>Slovan podruhé: Kadaň chystá 48 bytů za 195 milionů</title>
      <description><![CDATA[První stavba Slovanu skončila demolicí a ukončením smlouvy. Nový tendr už běží, úplný účet prvního pokusu a přesný osud podpory SFPI však veřejnost stále nezná.]]></description>
      <link>https://nasekadan.cz{ARTICLE_URL}</link>
      <guid isPermaLink="true">https://nasekadan.cz{ARTICLE_URL}</guid>
      <pubDate>{rfc}</pubDate>
      <category>Investice</category>
      <category>Bydlení</category>
      <category>Veřejné peníze</category>
      <category>Kadaň</category>
      <szn:image><szn:url>https://nasekadan.cz/assets/slovan-detail-20260724.jpg</szn:url></szn:image>
      <geo:lat>50.3809</geo:lat>
      <geo:long>13.2660</geo:long>
    </item>

'''
        xml = xml.replace("    <item>\n", item + "    <item>\n", 1)
    return write_if_changed(path, xml)


def main() -> None:
    now = datetime.now(TZ).replace(microsecond=0)
    if not prepare_article(now):
        return
    changed = [update_home(now), update_archive(now), update_rss(now)]
    if PREVIEW.exists():
        PREVIEW.unlink()
        changed.append(True)
    assert ARTICLE.is_file()
    assert ARTICLE_URL in (ROOT / "index.html").read_text(encoding="utf-8")
    assert ARTICLE_URL in (ROOT / "clanky" / "index.html").read_text(encoding="utf-8")
    assert "slovan-druhy-pokus.html" in (ROOT / "rss.xml").read_text(encoding="utf-8")
    print("Článek o Slovanu je připravený k nasazení.", any(changed))


if __name__ == "__main__":
    main()
