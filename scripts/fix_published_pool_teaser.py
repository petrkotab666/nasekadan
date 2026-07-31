#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

FILES = (
    Path("clanky/strikacky-vchody-drogy-kadan.html"),
    Path(".github/drafts/strikacky-vchody-drogy-kadan.html"),
)

OLD = (
    '<div class="next-teaser" data-koupaliste-teaser="1"><span class="eyebrow">'
    'PŘIPRAVUJEME PRO NAŠE KADAŇ</span><h2>Kolik stály pozemky a nová skluzavka na koupališti?'
    '</h2><p>Prověřujeme prodej pěti pozemků, financování skluzavky Niagara, rozpálené kovové '
    'schody i provoz hlavních atrakcí. Termín zveřejnění stanovíme později.</p>'
    '<a data-koupaliste-link="1" href="/clanky/">Sledovat přehled článků</a></div>'
)

NEW = (
    '<div class="next-teaser" data-koupaliste-teaser="1"><span class="eyebrow">'
    'UŽ ZVEŘEJNĚNO</span><h2>Kadaňské koupaliště slaví 50 let. Co nabízí a co není jasné kolem nové Niagary'
    '</h2><p>Přečtěte si přehled provozu areálu, vstupného, nové skluzavky Niagara, jejího '
    'financování, kovových schodů i otázek, které zatím zůstávají bez veřejné odpovědi.</p>'
    '<a data-koupaliste-link="1" href="/clanky/koupaliste-kadan-pozemky-skluzavka-provoz-2026.html">'
    'Přečíst článek o koupališti</a></div>'
)

MODIFIED = "2026-07-31T06:52:00+02:00"


def update(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if OLD in text:
        text = text.replace(OLD, NEW, 1)
    elif NEW not in text:
        raise SystemExit(f"V {path} nebyl nalezen očekávaný starý ani nový blok.")

    text = re.sub(
        r'(<meta\s+property=["\']article:modified_time["\']\s+content=["\'])[^"\']+(["\'])',
        rf"\g<1>{MODIFIED}\g<2>",
        text,
        flags=re.I,
    )
    text = re.sub(
        r'("dateModified"\s*:\s*")[^"]+("\s*)',
        rf"\g<1>{MODIFIED}\g<2>",
        text,
    )
    path.write_text(text, encoding="utf-8", newline="\n")


for file_path in FILES:
    update(file_path)

print("Upoutávka na zveřejněný článek o koupališti byla opravena ve zdroji i veřejném článku.")
