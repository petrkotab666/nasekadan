#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "prakticti-lekari-nemocnice-kadan-srpen-2026.html"
RSS = ROOT / "rss.xml"
MODIFIED = "2026-07-28T22:48:00+02:00"


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
        'content="Přehled srpnových omezení ordinací v Kadani a okolí: dovolené praktických lékařů, neurologie, ORL, očkovací centrum a gynekologie v Klášterci.">',
        'content="Přehled srpnových omezení ordinací v Kadani a okolí: praktičtí lékaři, neurologie, ORL, očkovací centrum, gynekologie a dětská ordinace v Klášterci.">',
        "meta description",
    )
    text = replace_once(
        text,
        'content="Pět pracovních dnů se překryjí dovolené dvou praktiků. Přehled doplňujeme o další potvrzená omezení zdravotních služeb v Kadani a okolí.">',
        'content="Přehled zahrnuje praktické lékaře, neurologii, ORL, očkovací centrum a dvě omezení pracovišť v Klášterci včetně dětské ordinace.">',
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
            "Přehled srpnových omezení ordinací v Kadani a okolí: praktičtí lékaři, "
            "neurologie, ORL, očkovací centrum, gynekologie a dětská ordinace v Klášterci."
        )
        data["dateModified"] = MODIFIED
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"

    text = re.sub(
        r'<script type="application/ld\+json">(\{.*?\})</script>',
        update_ld,
        text,
        count=1,
        flags=re.S,
    )

    text = replace_once(
        text,
        "Přehled jsme doplnili také o další potvrzená omezení zdravotních služeb v Kadani a okolí.</strong></p>",
        "Přehled jsme doplnili také o další potvrzená omezení zdravotních služeb v Kadani a okolí. Dětská ordinace MUDr. Mirky Doškové v Klášterci je nyní uzavřená a další dovolenou má od 10. do 14. srpna.</strong></p>",
        "lead",
    )

    text = replace_once(
        text,
        '    <div><b>12., 17., 20. a 24. 8.</b><span>neordinuje gynekologie v Klášterci</span></div>\n  </div>',
        '    <div><b>12., 17., 20. a 24. 8.</b><span>neordinuje gynekologie v Klášterci</span></div>\n'
        '    <div><b>27.–31. 7., 10.–14. 8. a 1. 9.</b><span>uzavřená dětská ordinace MUDr. Doškové v Klášterci</span></div>\n'
        '  </div>',
        "date card",
    )

    text = replace_once(
        text,
        '<div class="notice"><h3>V přehledu je sedm kadaňských pracovišť a jedno regionální omezení</h3><p>V Kadani jde o tři ambulance praktických lékařů, neurologii, ORL, očkovací centrum a interní ambulanci. Interna má vlastní samostatný článek, proto její termín znovu podrobně nerozepisujeme. <a href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Podrobnosti o uzavření interní ambulance jsou zde.</a> Navíc přidáváme omezení gynekologické ambulance Nemocnice Kadaň v Klášterci nad Ohří, které může zvýšit zájem pacientek o pracoviště v Kadani; to je redakční předpoklad, nikoli zveřejněné tvrzení nemocnice.</p></div>',
        '<div class="notice"><h3>V přehledu je sedm kadaňských pracovišť a dvě regionální omezení</h3><p>V Kadani jde o tři ambulance praktických lékařů, neurologii, ORL, očkovací centrum a interní ambulanci. Interna má vlastní samostatný článek, proto její termín znovu podrobně nerozepisujeme. <a href="/clanky/interni-ambulance-nemocnice-kadan-uzavrena-cervenec-srpen-2026.html">Podrobnosti o uzavření interní ambulance jsou zde.</a> V Klášterci nad Ohří se omezení týká gynekologické ambulance a ordinace praktického lékaře pro děti a dorost. U obou může vzniknout větší zájem o náhradní nebo okolní pracoviště; jde o redakční předpoklad, nikoli zveřejněné tvrzení nemocnice.</p></div>',
        "notice count",
    )

    pediatric_section = '''\n  <h3>Dětská ordinace MUDr. Mirky Doškové v Klášterci nad Ohří</h3>\n  <p>Ordinace praktického lékaře pro děti a dorost v Sadové 528 je uzavřená od 27. do 31. července, dále od 10. do 14. srpna a také 1. září. Nemocnice jako zástup uvádí MUDr. Kadlecovou z Ordinace u sluníčka na stejné adrese, a to v jejích ordinačních hodinách. Kontakt na ordinaci MUDr. Doškové je 474 376 341 a <a href="mailto:plddklasterec@nemkadan.cz">plddklasterec@nemkadan.cz</a>.</p>\n'''
    marker = '  <h2>Kontakty na ambulance MUDr. Suchecké a MUDr. Šindeláře</h2>'
    if pediatric_section.strip() not in text:
        if marker not in text:
            raise RuntimeError("Nenalezen marker pro dětskou ordinaci")
        text = text.replace(marker, pediatric_section + "\n" + marker, 1)

    text = replace_once(
        text,
        '    <li><a href="https://www.nemkadan.cz/ambulance-1/gynekologie/" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – Gynekologie</a>: omezení kláštereckého pracoviště a provoz kadaňské příjmové ambulance.</li>',
        '    <li><a href="https://www.nemkadan.cz/ambulance-1/gynekologie/" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – Gynekologie</a>: omezení kláštereckého pracoviště a provoz kadaňské příjmové ambulance.</li>\n'
        '    <li><a href="https://www.nemkadan.cz/ambulance-1/prakticky-lekar-pro-deti-a-dorost/" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – Praktický lékař pro děti a dorost</a>: termíny uzavření ordinace MUDr. Doškové v Klášterci a uvedený zástup.</li>',
        "source pediatric",
    )
    text = replace_once(
        text,
        "Stav ověřen 28. července 2026 ve 21:47.",
        "Stav ověřen 28. července 2026 ve 22:48.",
        "verified time",
    )
    text = replace_once(
        text,
        '<li>Gynekologie Klášterec: 12., 17., 20. a 24. 8.</li><li>Sedm pracovišť v Kadani + jedno v Klášterci</li>',
        '<li>Gynekologie Klášterec: 12., 17., 20. a 24. 8.</li><li>Dětská ordinace Klášterec: 27.–31. 7., 10.–14. 8. a 1. 9.</li><li>Sedm pracovišť v Kadani + dvě omezení v Klášterci</li>',
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
        r'gynekologii a dětskou ordinaci v Klášterci.\3'
    )
    text, count = pattern.subn(replacement, text, count=1)
    if count:
        RSS.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    update_article()
    update_rss()
    print("Doplněna dětská ordinace MUDr. Doškové v Klášterci.")


if __name__ == "__main__":
    main()
