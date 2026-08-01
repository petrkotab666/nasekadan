#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "odstavky-elektriny-autokemp-prunerov-srpen-2026.html"
ORGANIZATIONS = ROOT / "data" / "organizations.json"
CITY_SOURCES = ROOT / "data" / "city-sources.json"
MODIFIED = "2026-08-01T12:25:00+02:00"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f"V článku chybí očekávaný úsek: {label}")
    return text.replace(old, new, 1)


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'content="Restaurace v Autokempu Prunéřov otevře 3. a 10. srpna až po 18. hodině a 14. srpna po 16. hodině. Pro odstávku 10. srpna jsou známé přesné časy, adresy a parcela."',
        'content="Aktualizace: restaurace Autokempu Prunéřov bude 3. srpna otevřená v běžné pracovní době. Během odstávky poběží díky elektrocentrále v omezeném režimu; další omezení jsou hlášena na 10. a 14. srpna."',
        "meta description",
    )
    text = replace_once(
        text,
        'content="Odstávka 10. srpna potrvá od 9:00 do 18:00 a zasáhne Prunéřov 387, Zelenou 217 a parcelu 841/3 v katastru Vernéřov."',
        'content="Dne 3. srpna zůstane restaurace otevřená díky elektrocentrále. Během odstávky nabídne výčep, polévku a menší občerstvení."',
        "og description",
    )
    text = text.replace('content="2026-07-30T07:45:00+02:00"', f'content="{MODIFIED}"')
    text = text.replace('"dateModified":"2026-07-30T07:45:00+02:00"', f'"dateModified":"{MODIFIED}"')
    text = replace_once(
        text,
        '"description":"Restaurace v Autokempu Prunéřov otevře 3. a 10. srpna až po 18. hodině a 14. srpna po 16. hodině. Pro odstávku 10. srpna jsou známé přesné časy, adresy a parcela."',
        '"description":"Aktualizace: restaurace Autokempu Prunéřov bude 3. srpna otevřená v běžné pracovní době. Během odstávky poběží díky elektrocentrále v omezeném režimu; další omezení jsou hlášena na 10. a 14. srpna."',
        "JSON-LD description",
    )
    text = replace_once(
        text,
        '<meta name="twitter:description" content="Odstávka 10. srpna potrvá od 9:00 do 18:00 a zasáhne Prunéřov 387, Zelenou 217 a parcelu 841/3 v katastru Vernéřov.">',
        '<meta name="twitter:description" content="Dne 3. srpna zůstane restaurace otevřená díky elektrocentrále. Během odstávky nabídne výčep, polévku a menší občerstvení.">',
        "twitter description",
    )
    text = replace_once(
        text,
        '<p class="tag">PRAKTICKÉ INFORMACE · PRUNÉŘOV · 28. ČERVENCE 2026</p>',
        '<p class="tag">PRAKTICKÉ INFORMACE · PRUNÉŘOV · AKTUALIZOVÁNO 1. SRPNA 2026</p>',
        "tag",
    )
    text = replace_once(
        text,
        '<p class="leadtext"><strong>Tři plánované odstávky elektřiny ovlivní v srpnu provoz restaurace v Autokempu Prunéřov. V pondělí 3. srpna a v pondělí 10. srpna otevře až po 18. hodině, v pátek 14. srpna pak po 16. hodině.</strong></p>',
        '<p class="leadtext"><strong>Aktualizace: restaurace v Autokempu Prunéřov bude v pondělí 3. srpna otevřená v běžné pracovní době. Provozovatel sehnal elektrocentrálu; během odstávky pojede výčep a nabídka polévky a menšího občerstvení. Původně oznámená omezení pro 10. a 14. srpna zatím zůstávají beze změny.</strong></p>',
        "lead",
    )
    text = replace_once(
        text,
        '<div class="hero-visual"><strong>Ubytovaní hosté se na recepci dostanou i během odstávek. Platební terminál ale bez elektřiny nebude fungovat, proto bude potřeba hotovost.</strong></div>',
        '<div class="hero-visual"><strong>Dobrá zpráva pro pondělí 3. srpna: elektrocentrála udrží v provozu výčep a základní občerstvení. Po obnovení elektřiny se restaurace vrátí do normálního režimu.</strong></div>',
        "hero",
    )
    text = replace_once(
        text,
        '<div class="dates"><div><b>3. srpna</b><span>restaurace otevře po 18:00</span></div><div><b>10. srpna</b><span>odstávka 9:00–18:00, restaurace otevře poté</span></div><div><b>14. srpna</b><span>restaurace otevře po 16:00</span></div></div>',
        '<div class="dates"><div><b>3. srpna</b><span>otevřeno v běžné pracovní době; při odstávce omezený režim</span></div><div><b>10. srpna</b><span>odstávka 9:00–18:00, restaurace otevře poté</span></div><div><b>14. srpna</b><span>restaurace otevře po 16:00</span></div></div>',
        "dates",
    )
    text = replace_once(
        text,
        '<p>Provozovatel Autokempu Prunéřov zveřejnil upozornění, podle něhož omezení souvisí s plánovanými odstávkami společnosti ČEZ. Restaurace proto v uvedených dnech zůstane do odpoledních nebo podvečerních hodin zavřená.</p>',
        '<div class="callout"><strong>Nové řešení pro 3. srpna</strong><p>Provozovatel 31. července oznámil, že se mu podařilo zajistit elektrocentrálu. Restaurace proto v pondělí 3. srpna otevře v normální pracovní době. Po dobu výpadku poběží omezená nabídka: výčep, polévka a něco malého k jídlu. Jakmile ČEZ dodávku obnoví, provoz se vrátí do běžného režimu.</p></div><p>Původní oznámení počítalo 3. srpna s otevřením až po 18. hodině. Tento údaj už neplatí. U termínů 10. a 14. srpna zatím provozovatel změnu neoznámil.</p>',
        "first update paragraph",
    )
    text = replace_once(
        text,
        '<div class="callout"><strong>Kartu nechte jako záložní možnost</strong><p>Během přerušení dodávky elektřiny nebude možné platit kartou. Provozovatel proto návštěvníkům doporučuje připravit si hotovost.</p></div>',
        '<div class="callout"><strong>Hotovost je stále rozumná pojistka</strong><p>Nové oznámení neuvádí, zda elektrocentrála napájí také platební terminál. Návštěvníci by proto měli mít pro dobu odstávky připravenou hotovost.</p></div>',
        "payment callout",
    )
    text = replace_once(
        text,
        '<p>Z oznámení kempu nelze určit úplný seznam dalších dotčených adres ani přesný čas, kdy ČEZ dodávku elektřiny vypne a znovu obnoví. Jisté je provozní opatření kempu: restaurace otevře v každém ze tří termínů až po uvedené hodině.</p>',
        '<p>Z oznámení kempu nelze určit úplný seznam dalších dotčených adres ani přesný čas, kdy ČEZ dodávku elektřiny vypne a znovu obnoví. Pro 3. srpna je ale provozní režim potvrzený: restaurace zůstane otevřená a během odstávky nabídne omezené občerstvení. Pro 10. a 14. srpna nadále platí dříve oznámené pozdější otevření, dokud provozovatel nezveřejní další změnu.</p>',
        "scope paragraph",
    )
    text = replace_once(
        text,
        '<h2>Informaci jsme doplnili také do kulturního přehledu</h2>\n  <p>Autokemp a prunéřovské koupaliště jsou součástí našeho pravidelného přehledu volnočasových možností. Upozornění na srpnová omezení jsme proto doplnili i do článku <a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kam v Kadani a okolí od 27. července do 2. srpna</a>, aby návštěvníci našli provozní změnu také u původního tipu.</p>',
        '<h2>Autokemp bude součástí každého nedělního přehledu</h2>\n  <p>Autokemp, jeho restaurace a navazující koupaliště patří mezi důležité letní možnosti v bezprostředním okolí Kadaně. Odteď budou jeho oficiální web, aktuality a veřejné sociální profily povinným zdrojem nedělního přehledu. V článku pro týden od 3. do 9. srpna uvedeme také omezený provoz během pondělní odstávky.</p>',
        "culture section",
    )
    text = replace_once(
        text,
        '<li>Veřejné provozní oznámení Autokempu Prunéřov zveřejněné na Facebooku a sdílené stránkou Kultura v Kadani.</li>',
        '<li>Veřejné provozní oznámení Autokempu Prunéřov zveřejněné 31. července 2026 na oficiálním Facebooku provozovatele.</li>',
        "source item",
    )
    text = replace_once(
        text,
        '<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>3. 8. restaurace po 18:00</li><li>10. 8. odstávka 9:00–18:00</li><li>Prunéřov 387</li><li>Zelená 217</li><li>parcela 841/3, k. ú. Vernéřov</li><li>14. 8. dvě úřední oznámení ČEZ</li><li>Recepce otevřená</li><li>Platba pouze hotově</li></ul></div><div data-promos data-context="sidebar"></div></aside>',
        '<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>3. 8. otevřeno v běžné době</li><li>Při odstávce: výčep, polévka a malé občerstvení</li><li>Po zapnutí elektřiny normální režim</li><li>10. 8. odstávka 9:00–18:00</li><li>14. 8. dvě úřední oznámení ČEZ</li><li>Hotovost doporučena</li></ul></div><div data-promos data-context="sidebar"></div></aside>',
        "sidebar",
    )
    ARTICLE.write_text(text, encoding="utf-8", newline="\n")


def update_registries() -> None:
    organizations = json.loads(ORGANIZATIONS.read_text(encoding="utf-8"))
    exists = any(
        item.get("name") == "Autokemp Prunéřov"
        for group in organizations.get("groups", [])
        for item in group.get("items", [])
        if isinstance(item, dict)
    )
    if not exists:
        target = next(
            (g for g in organizations.get("groups", []) if "volný čas" in str(g.get("name", "")).lower()),
            None,
        ) or next(
            (g for g in organizations.get("groups", []) if "sport" in str(g.get("name", "")).lower()),
            None,
        )
        if target is None:
            organizations.setdefault("groups", []).append({"name": "Volný čas a cestovní ruch", "items": []})
            target = organizations["groups"][-1]
        target.setdefault("items", []).append({
            "name": "Autokemp Prunéřov",
            "description": "Kemp, restaurace, ubytování, veřejné akce a provozní oznámení včetně změn otevírací doby.",
            "address": "Prunéřov 383, 432 01 Kadaň",
            "url": "https://www.autokemp-prunerov.cz/",
            "monitorUrls": [
                "https://www.autokemp-prunerov.cz/",
                "https://www.autokemp-prunerov.cz/aktuality/",
                "https://www.autokemp-prunerov.cz/restaurace/",
                "https://www.facebook.com/prunerov/",
            ],
        })
        organizations["updatedAt"] = "2026-08-01"
        ORGANIZATIONS.write_text(json.dumps(organizations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    city_sources = json.loads(CITY_SOURCES.read_text(encoding="utf-8"))
    if not any(s.get("name") == "Autokemp Prunéřov – aktuality" for s in city_sources.get("sources", [])):
        city_sources.setdefault("sources", []).append({
            "name": "Autokemp Prunéřov – aktuality",
            "url": "https://www.autokemp-prunerov.cz/aktuality/",
            "category": "Volný čas, ubytování a provozní informace",
        })
        city_sources["updatedAt"] = "2026-08-01"
        CITY_SOURCES.write_text(json.dumps(city_sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    update_article()
    update_registries()
    print("Aktualizace Autokempu, registru organizací a zdrojů byla připravena.")


if __name__ == "__main__":
    main()
