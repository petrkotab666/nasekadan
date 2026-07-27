#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "clanky" / "epetice-nemocnice-kadan.html"
text = path.read_text(encoding="utf-8")

replacements = {
    '<h1>Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná</h1>':
        '<h1>Petice za nemocnici je online na soukromém portálu. Co to mění</h1>',
    '<p>To je zásadní právě ve chvíli, kdy delší listinný text přesahuje elektronický limit. Pokud se elektronická verze zkrátí tak, že vypustí některý požadavek, změní rozsah závazku nebo jinak posune význam, nejde už o podpisy pod jedním totožným dokumentem.</p>':
        '<p>Veřejná verze na e-petice.cz nyní obsahuje všech osm hlavních požadavků. Při dalším vývoji je proto důležité hlídat, zda se její text nezmění a zda případné souhrnné počty stále odkazují ke stejnému znění jako listinné archy.</p>',
    '<p>Může tedy jít o technický problém, rozpracovaný návrh, kontrolu podmínek systému nebo pouze nepřesné pojmenování čekání na zveřejnění. Dokud se petice neobjeví ve veřejném seznamu, nelze její skutečný stav nezávisle ověřit.</p>':
        '<p>Veřejná petice už nyní na e-petice.cz dostupná je. Původní formulace o čekání na schválení tak popisovala pouze dřívější fázi před zveřejněním; z veřejných podkladů nelze určit, zda tehdy šlo o technické zpracování, interní kontrolu soukromého portálu nebo jen nepřesné označení rozpracovaného návrhu.</p>',
    '"image":"https://nasekadan.cz/social-card.png"':
        '"image":"https://nasekadan.cz/social/epetice-nemocnice-kadan-71560a0788.png"',
}

for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"Chybí očekávaný text: {old[:80]}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8", newline="\n")
print("Dokončena následná oprava článku o soukromém portálu e-petice.cz.")
