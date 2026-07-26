#!/usr/bin/env python3
"""Doplní ověřené znění listinné petice do hlavního článku.

Skript je idempotentní a spouští se při každém produkčním sestavení i serverové
aktualizaci. Nové podklady tak nemohou zůstat pouze v samostatném článku o
ePetici ani zmizet při přepsání webu starší automatizací.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "petice-nemocnice-kadan.html"

TOC_MARKER = '<li><a href="#prvni-sber">První sběr podpisů</a></li>'
TOC_LINK = '<li><a href="#plne-zneni-petice">Osm požadavků a rozpracovaná ePetice</a></li>'
ANCHOR = '  <h2 id="apoliticka">„Apolitická“ petice předkládaná kandidátkou</h2>'

SECTION = '''
  <h2 id="plne-zneni-petice">Petice obsahuje osm požadavků. Rozpracovaná ePetice narazila na limit</h2>
  <p>Nově zveřejněné snímky zachycují celé znění listinné petice. Dokument není omezen pouze na požadavek, aby Nemocnice Kadaň zůstala ve vlastnictví města. Obsahuje osm konkrétních bodů adresovaných zastupitelstvu, starostovi a radě města.</p>
  <ol>
    <li><strong>Veřejný závazek města</strong>, že nemocnice nebude prodána ani jinak převedena do soukromého vlastnictví.</li>
    <li><strong>Okamžité přijetí konkrétních opatření</strong> ke stabilizaci ekonomické situace nemocnice.</li>
    <li><strong>Zachování všech potřebných zdravotnických oborů a odborných ambulancí</strong> pro obyvatele regionu.</li>
    <li><strong>Pravidelné zveřejňování ekonomických výsledků</strong>, přijatých opatření a strategie dalšího rozvoje.</li>
    <li><strong>Nezávislé odborné posouzení současného řízení</strong> s předložením výsledků zastupitelům i veřejnosti.</li>
    <li><strong>Přijetí personálních změn</strong>, pokud se ukáže, že současné řízení nevede ke stabilizaci nebo nedokáže zastavit zhoršování stavu.</li>
    <li><strong>Obnovení otevřené komunikace</strong> mezi vedením nemocnice, zaměstnanci, městem a občany.</li>
    <li><strong>Zajištění dostatečných finančních prostředků na kvalitní zdravotní péči</strong>, aby pacienti ani zaměstnanci nenesli důsledky manažerských selhání.</li>
  </ol>
  <p>Listinný dokument tedy obsahuje majetkové, ekonomické, personální, provozní i informační požadavky. Pro posouzení elektronické varianty bude rozhodující, zda všechny tyto body zůstanou zachovány ve stejném znění.</p>

  <div class="factcheck"><h3>Co dokládají nové snímky</h3><ul>
    <li>Ve formuláři Portálu občana se zobrazilo upozornění na překročení limitu 3 500 znaků už ve chvíli, kdy byly ve viditelné části vloženy pouze první tři požadavky.</li>
    <li>Snímek části „Moje petice“ dokládá založený nebo rozpracovaný záznam. Sám o sobě ještě neprokazuje, že byla ePetice veřejně zveřejněna a otevřena k podpisu.</li>
    <li>Při souběžném listinném a elektronickém sběru musí být text obou verzí totožný. Odlišnou elektronickou verzi by bylo nutné vykazovat jako samostatný dokument.</li>
  </ul></div>

  <div class="callout"><strong>Osobní údaje na web nevkládáme</strong>Snímky listinné petice obsahují bydliště, e-mail a telefon předkladatelky. Slouží pouze jako redakční podklad. Na webu zveřejňujeme obsah požadavků, nikoli nezakryté kontaktní údaje.</div>

  <p>Podrobný rozbor pravidel elektronické a listinné varianty je v navazujícím článku <a href="/clanky/epetice-nemocnice-kadan.html">Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná</a>.</p>
'''

SOURCE = '<li>Fotografie úplného znění listinné petice a snímky rozpracovaného formuláře ePetice zveřejněné předkladatelkou; kontaktní údaje redakce dále nezveřejňuje.</li>'


def main() -> int:
    if not ARTICLE.is_file():
        raise SystemExit(f"Chybí článek: {ARTICLE.relative_to(ROOT)}")

    text = ARTICLE.read_text(encoding="utf-8")
    original = text

    if TOC_LINK not in text:
        if TOC_MARKER not in text:
            raise SystemExit("V obsahu článku chybí odkaz na první sběr podpisů.")
        text = text.replace(TOC_MARKER, TOC_MARKER + "\n      " + TOC_LINK, 1)

    if 'id="plne-zneni-petice"' not in text:
        if ANCHOR not in text:
            raise SystemExit("V článku chybí kapitola o apolitičnosti petice.")
        text = text.replace(ANCHOR, SECTION + "\n" + ANCHOR, 1)

    text = text.replace(
        '"dateModified":"2026-07-25T05:00:00+02:00"',
        '"dateModified":"2026-07-26T19:15:00+02:00"',
        1,
    )

    if SOURCE not in text:
        source_start = text.find('<div class="source-list">')
        source_end = text.find("</ul>", source_start) if source_start >= 0 else -1
        if source_end >= 0:
            text = text[:source_end] + SOURCE + text[source_end:]

    required = (
        "Petice obsahuje osm požadavků. Rozpracovaná ePetice narazila na limit",
        "Přijetí personálních změn",
        "Osobní údaje na web nevkládáme",
    )
    for phrase in required:
        if phrase not in text:
            raise SystemExit(f"Po úpravě chybí povinná část: {phrase}")

    if text != original:
        ARTICLE.write_text(text, encoding="utf-8", newline="\n")
        print("Doplněno:", ARTICLE.relative_to(ROOT))
    else:
        print("Hlavní článek už obsahuje úplné znění petice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
