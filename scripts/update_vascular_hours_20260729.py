#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "prakticti-lekari-nemocnice-kadan-srpen-2026.html"
RSS = ROOT / "rss.xml"
MODIFIED = "2026-07-29T08:20:00+02:00"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise RuntimeError(f"Nenalezen očekávaný úsek: {label}")
    return text.replace(old, new, 1)


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        'content="Přehled srpnových omezení ordinací v Kadani a okolí: praktičtí lékaři, neurologie, ORL, očkovací centrum, gynekologie a dětská ordinace v Klášterci.">',
        'content="Přehled omezení a změn ordinací v Kadani a okolí: praktičtí lékaři, neurologie, ORL, očkovací centrum, cévní ambulance, gynekologie a dětská ordinace v Klášterci.">',
        "meta description",
    )
    text = replace_once(
        text,
        'content="Přehled zahrnuje praktické lékaře, neurologii, ORL, očkovací centrum a dvě omezení pracovišť v Klášterci včetně dětské ordinace.">',
        'content="Přehled zahrnuje praktické lékaře, neurologii, ORL, očkovací centrum, změnu cévní ambulance a dvě omezení pracovišť v Klášterci.">',
        "OG description",
    )
    text = re.sub(
        r'(<meta property="article:modified_time" content=")[^"]+("\s*/?>)',
        rf'\g<1>{MODIFIED}\2',
        text,
        count=1,
    )

    def update_ld(match: re.Match[str]) -> str:
        data = json.loads(match.group(1))
        if data.get("@type") != "NewsArticle":
            return match.group(0)
        data["description"] = (
            "Přehled omezení a změn ordinací v Kadani a okolí: praktičtí lékaři, "
            "neurologie, ORL, očkovací centrum, cévní ambulance, gynekologie a "
            "dětská ordinace v Klášterci."
        )
        data["dateModified"] = MODIFIED
        return '<script type="application/ld+json">' + json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        ) + "</script>"

    text = re.sub(
        r'<script type="application/ld\+json">(\{.*?\})</script>',
        update_ld,
        text,
        count=1,
        flags=re.S,
    )

    text = replace_once(
        text,
        '<p class="tag">PRAKTICKÉ INFORMACE · ZDRAVOTNICTVÍ · AKTUALIZOVÁNO 29. ČERVENCE 2026</p>',
        '<p class="tag">PRAKTICKÉ INFORMACE · ZDRAVOTNICTVÍ · AKTUALIZOVÁNO 29. ČERVENCE 2026</p>',
        "tag",
    )

    if 'Cévní ambulance: od 1. 9. 10:00–14:00' not in text:
        text = replace_once(
            text,
            '    <div><b>27.–31. 7., 10.–14. 8. a 1. 9.</b><span>uzavřená dětská ordinace MUDr. Doškové v Klášterci</span></div>\n  </div>',
            '    <div><b>27.–31. 7., 10.–14. 8. a 1. 9.</b><span>uzavřená dětská ordinace MUDr. Doškové v Klášterci</span></div>\n'
            '    <div><b>Od 1. 9.</b><span>cévní ambulance nově 10:00–14:00</span></div>\n'
            '  </div>',
            "date card",
        )

    text = replace_once(
        text,
        '<div class="notice"><h3>V přehledu je sedm kadaňských pracovišť a dvě regionální omezení</h3><p>V Kadani jde o tři ambulance praktických lékařů, neurologii, ORL, očkovací centrum a interní ambulanci.',
        '<div class="notice"><h3>V přehledu je osm kadaňských pracovišť a dvě regionální omezení</h3><p>V Kadani jde o tři ambulance praktických lékařů, neurologii, ORL, očkovací centrum, cévní ambulanci a interní ambulanci.',
        "notice count",
    )

    vascular_section = '''\n  <h3>Cévní ambulance: změna od 1. září</h3>\n  <p>Od 1. září 2026 se mění ordinační doba cévní ambulance v poliklinice Nemocnice Kadaň. Nově bude ambulance otevřena od 10:00 do 14:00. Pracoviště přijímá pouze objednané pacienty s doporučením lékaře. Objednání je možné přes recepce nemocnice na číslech 474 944 703, 474 944 704, 474 944 705 a 474 944 428.</p>\n'''
    marker = '  <h2>Kontakty na ambulance MUDr. Suchecké a MUDr. Šindeláře</h2>'
    if vascular_section.strip() not in text:
        if marker not in text:
            raise RuntimeError("Nenalezen marker pro cévní ambulanci")
        text = text.replace(marker, vascular_section + "\n" + marker, 1)

    text = replace_once(
        text,
        '    <li><a href="https://mudrkurakova.cz/" target="_blank" rel="noopener noreferrer">MUDr. Kuraková, s.r.o. – oficiální web ordinace</a>: letní dovolená, zastupující lékařka, kontakt a aktuálně ordinující lékařka.</li>',
        '    <li><a href="https://mudrkurakova.cz/" target="_blank" rel="noopener noreferrer">MUDr. Kuraková, s.r.o. – oficiální web ordinace</a>: letní dovolená, zastupující lékařka, kontakt a aktuálně ordinující lékařka.</li>\n'
        '    <li><a href="https://www.nemkadan.cz/ambulance-1/cevni-ambulance/" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – Cévní ambulance</a>: změna ordinační doby od 1. září 2026 a objednávací režim.</li>',
        "vascular source",
    )
    text = re.sub(
        r'Stav ověřen [^<]+\.',
        'Stav ověřen 29. července 2026 v 08:20.',
        text,
        count=1,
    )
    text = replace_once(
        text,
        '<li>Dětská ordinace Klášterec: 27.–31. 7., 10.–14. 8. a 1. 9.</li><li>Sedm pracovišť v Kadani + dvě omezení v Klášterci</li>',
        '<li>Dětská ordinace Klášterec: 27.–31. 7., 10.–14. 8. a 1. 9.</li><li>Cévní ambulance: od 1. 9. 10:00–14:00</li><li>Osm pracovišť v Kadani + dvě omezení v Klášterci</li>',
        "sidebar",
    )

    ARTICLE.write_text(text, encoding="utf-8", newline="\n")


def update_rss() -> None:
    if not RSS.exists():
        return
    text = RSS.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<item><title>V srpnu omezí provoz více ordinací v Kadani a okolí.*?</title><description><!\[CDATA\[)(.*?)(\]\]></description>)',
        re.S,
    )
    replacement = (
        r'\1Přehled zahrnuje praktické lékaře, neurologii, ORL, očkovací centrum, '
        r'změnu cévní ambulance a dvě omezení pracovišť v Klášterci.\3'
    )
    text, count = pattern.subn(replacement, text, count=1)
    if count:
        RSS.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    update_article()
    update_rss()
    print("Doplněna změna ordinační doby cévní ambulance od 1. září 2026.")


if __name__ == "__main__":
    main()
