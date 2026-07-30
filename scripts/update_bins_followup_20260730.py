#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "pretekajici-kose-kadan-technicke-sluzby-ridici.html"
MODIFIED = "2026-07-30T18:34:00+02:00"
MARKER = 'data-kose-update="20260730"'


def main() -> int:
    text = ARTICLE.read_text(encoding="utf-8")

    text = re.sub(
        r'(<meta property="article:modified_time" content=")[^"]+(\">)',
        rf'\g<1>{MODIFIED}\g<2>',
        text,
        count=1,
    )
    text = re.sub(
        r'("dateModified"\s*:\s*")[^"]+(\")',
        rf'\g<1>{MODIFIED}\g<2>',
        text,
        count=1,
    )

    old_description = (
        "Přeplněný koš u zahrádkářské kolonie otevřel debatu o svozu odpadu v Kadani. "
        "Starosta uvedl, že odešli řidiči; část lidí upozorňuje i na nevhodné používání malých košů."
    )
    new_description = (
        "Koš u zahrádkářské kolonie byl po kritice vyprázdněn a obyvatelé hlásí úklid i jinde. "
        "Debata pokračuje kvůli četnosti svozu i odpadu odhazovanému vedle nádob."
    )
    text = text.replace(old_description, new_description)

    text = text.replace(
        "ODPADY · TECHNICKÉ SLUŽBY · 29. ČERVENCE 2026",
        "ODPADY · TECHNICKÉ SLUŽBY · AKTUALIZOVÁNO 30. ČERVENCE 2026",
        1,
    )

    if ".update-box{" not in text:
        text = text.replace(
            ".callout{border-left:6px solid var(--red);background:var(--cream);margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}",
            ".update-box{border:2px solid #a9232b;background:#fff7e7;margin:26px 0 32px;padding:22px 26px;border-radius:16px;box-shadow:0 10px 28px #16242d12}.update-box b{display:block;color:#a9232b;font-size:14px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}.update-box p{margin:0;font-size:17px}.callout{border-left:6px solid var(--red);background:var(--cream);margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}",
            1,
        )

    if MARKER not in text:
        update_box = '''\n  <div class="update-box" data-kose-update="20260730"><b>Aktualizováno 30. července 2026 v 18:34</b><p>Koš u zahrádkářské kolonie pod čerpací stanicí Shell byl podle nové fotografie vyprázdněn. Autorka původního podnětu technické služby pochválila, současně ale upozornila na odpad, který lidé dál odhazují do trávy nebo na beton. Další obyvatelé hlásili vyprázdněné koše také v Golovinově ulici a na dalších místech. V diskusi zároveň zaznělo, že některé nádoby byly od pondělí do středy přeplněné a svoz by měl být častější nebo dočasně zajištěný jiným způsobem.</p></div>\n'''
        text = text.replace(
            '  <div class="hero-visual"><strong><span class="hero-kicker">Spor o svoz a chování lidí</span>Přeplněné koše nejsou jen otázkou četnosti svozu. Debata ukazuje také na personální situaci technických služeb a nevhodné odkládání domovního či zahrádkářského odpadu.</strong></div>\n',
            '  <div class="hero-visual"><strong><span class="hero-kicker">Spor o svoz a chování lidí</span>Přeplněné koše nejsou jen otázkou četnosti svozu. Debata ukazuje také na personální situaci technických služeb a nevhodné odkládání domovního či zahrádkářského odpadu.</strong></div>\n' + update_box,
            1,
        )

        section = '''\n  <h2>Aktualizace: Koš byl vyprázdněn, debata ale pokračuje</h2>\n  <p>Ve čtvrtek 30. července zveřejnila Petra Pokorná novou fotografii stejného místa. Nádoba už byla prázdná a autorka příspěvku technickým službám za svoz poděkovala. Zároveň vyzvala obyvatele, aby odpad neodhazovali vedle košů do trávy nebo na zpevněnou plochu.</p>\n  <p>Také další lidé v diskusi uvedli, že byly vyprázdněny koše v jejich okolí, například v Golovinově ulici. Reakce však nebyly pouze pochvalné. Část obyvatel připomněla, že nádoby byly několik dnů přeplněné, vítr odpad roznášel po okolí a při nedostatku pracovníků by město nebo technické služby měly zvážit náhradní svoz externí firmou.</p>\n  <p>Nová fotografie dokládá, že konkrétní koš byl nakonec vyprázdněn. Neumožňuje ale určit, zda šlo o běžný plánovaný svoz, reakci na zveřejněný podnět nebo součást širšího úklidu. Stejně tak neřeší spor o potřebnou četnost svozu. Debata se proto posunula od otázky, zda se nádoba vyváží, k otázce, zda je současný režim dostatečně rychlý a jak zabránit tomu, aby lidé nechávali odpad vedle plných košů.</p>\n'''
        text = text.replace(
            "  <h2>Lidé jmenují další problémová místa</h2>",
            section + "\n  <h2>Lidé jmenují další problémová místa</h2>",
            1,
        )

        text = text.replace(
            "  <div class=\"source-list\"><h2>Zdroje</h2><ul>",
            "  <div class=\"source-list\"><h2>Zdroje</h2><ul>\n    <li>Navazující veřejný příspěvek Petry Pokorné ve skupině Kadaňské fórum z 30. července 2026; obrazový záznam má redakce k dispozici.</li>",
            1,
        )

        text = text.replace(
            "<aside class=\"sticky\">\n",
            "<aside class=\"sticky\">\n  <div class=\"sidebox\"><h3>Aktualizováno</h3><p><strong>Koš pod Shellem byl vyprázdněn.</strong> Obyvatelé hlásí svoz i jinde, současně ale žádají větší četnost a ohleduplnější chování lidí.</p></div>\n",
            1,
        )

    ARTICLE.write_text(text, encoding="utf-8", newline="\n")
    print("Článek o přeplněných koších byl doplněn o navazující úklid a reakce obyvatel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
