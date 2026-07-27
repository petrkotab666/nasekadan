#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / ".github" / "drafts" / "nemocnice-kadan-profil-sluzby-budoucnost.html"
ARC = ROOT / ".github" / "drafts" / "arc-med-nemocnice-kadan.html"
SERIES = ROOT / "scripts" / "link_hospital_series.py"

SECTION = r'''
  <h2 id="obce" data-regional-funding>Kdo platí regionální význam nemocnice</h2>
  <p>Nemocnice slouží širšímu regionu, hlavní finanční odpovědnost však nese Kadaň jako její jediný vlastník. Veřejný přehled nemocnice uvádí mezi podporovateli za rok 2025 patnáct okolních měst a obcí. V letech 2023 a 2024 jich bylo šestnáct. Jde tedy o dlouhodobý model, v němž nemocnice žádá jednotlivé samosprávy o vlastní příspěvky.</p>
  <p>Doložené částky ukazují výrazné rozdíly podle velikosti obce. Klášterec nad Ohří poskytl v roce 2025 dvě dotace v celkové výši <strong>1 205 892 korun</strong>, Vejprty <strong>133 248 korun</strong> a Perštejn <strong>70 tisíc korun</strong>. Další menší obce se objevují v seznamu podporovatelů nemocnice, veřejný přehled ale neuvádí na jednom místě výši všech jejich příspěvků.</p>
  <div class="factcheck">
    <h3>Co lze a nelze z veřejných seznamů vyčíst</h3>
    <ul>
      <li>Řada spádových obcí nemocnici pravidelně podporuje a žádosti tedy neodmítá automaticky.</li>
      <li>Seznam sponzorů neukazuje, které obce byly v daném roce osloveny, které žádost výslovně odmítly a které vůbec požádány nebyly.</li>
      <li>Ve veřejných dokumentech jsme nenašli doklad, že by po zhoršení hospodaření v roce 2026 Kadaň obeslala celý spádový region s mimořádnou žádostí o společné financování další pomoci nemocnici.</li>
      <li>Doložené obecní příspěvky vypadají především jako pokračování každoročního systému, nikoli jako regionální dohoda o sdílení provozní ztráty a obnovy areálu.</li>
    </ul>
  </div>
  <div class="callout"><strong>Regionální služba, převážně kadaňský účet</strong>Okolní obce přispívají, ale hlavní břemeno zůstává na vlastníkovi. Jen v roce 2026 Kadaň nemocnici schválila nejméně 48 milionů korun v pravidelné, investiční a mimořádné pomoci. Závěrečná strategie by proto měla říci nejen to, co má nemocnice zachovat, ale také zda město usiluje o trvalejší spoluúčast celého spádového území.</div>
'''.strip()

SOURCES = [
    (
        "https://www.nemkadan.cz/pro-verejnost/sponzori/",
        "Nemocnice Kadaň: přehled podporujících měst a obcí podle jednotlivých let",
    ),
    (
        "https://smlouvy.gov.cz/vyhledavani?subject_name=Nemocnice+Kada%C5%88+s.r.o.",
        "Registr smluv: dotační smlouvy a příspěvky okolních samospráv",
    ),
    (
        "https://www.nemkadan.cz/pro-verejnost/verejnost/aktuality/klasterec-prida-kadanske-nemocnici-na-obnovu-sestinedeli-115cs.html",
        "Nemocnice Kadaň: postoj Klášterce k podpoře nemocnice a přepočtu podle obyvatel",
    ),
    (
        "https://www.obec-perstejn.cz/urad-223/uredni-deska/smlouva-o-poskytnuti-dotace-na-rok-2026-nemocnice-kadan-1436.html",
        "Obec Perštejn: smlouva o dotaci Nemocnici Kadaň pro rok 2026",
    ),
]

TEASER = r'''
  <section data-hospital-profile-teaser style="margin:44px 0 24px;padding:28px;border-radius:20px;background:linear-gradient(135deg,#10242e,#22606b 62%,#9d222a);color:#fff;box-shadow:0 18px 45px rgba(20,35,45,.20)">
    <p style="margin:0 0 8px;color:#d8f2f4;font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase">STŘEDA 29. 7. V 5:00 · ZÁVĚREČNÝ DÍL SÉRIE</p>
    <h2 style="margin:0 0 12px;color:#fff;font:800 32px/1.15 Georgia,serif">Nemocnice Kadaň není jen spor o miliony. Co všechno zajišťuje pro region</h2>
    <p style="margin:0 0 16px;color:#edf3f5;font-size:18px">Závěrečný díl představí nemocnici jako celek: její oddělení, 254 lůžek, téměř 480 pracovních úvazků, výkony, spádovou oblast i to, jak se na financování podílejí okolní obce.</p>
    <span style="display:inline-block;padding:10px 14px;border:1px solid rgba(255,255,255,.45);border-radius:999px;color:#fff;font-weight:900">Vyjde ve středu 29. 7. v 5:00</span>
  </section>
'''.strip()


def write_if_changed(path: Path, text: str) -> bool:
    original = path.read_text(encoding="utf-8")
    if original == text:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Upraveno: {path.relative_to(ROOT)}")
    return True


def patch_profile() -> bool:
    text = PROFILE.read_text(encoding="utf-8")
    original = text

    if 'href="#obce"' not in text:
        marker = '<li><a href="#historie">'
        item = '<li><a href="#obce">Kdo platí regionální význam nemocnice</a></li>'
        if marker not in text:
            raise RuntimeError("V profilu chybí položka historie v obsahu.")
        text = text.replace(marker, item + marker, 1)

    text = re.sub(
        r'\s*<h2 id="obce"[^>]*>.*?(?=\s*<h2 id="historie">)',
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    marker = '  <h2 id="historie">'
    if marker not in text:
        raise RuntimeError("V profilu chybí kapitola historie.")
    text = text.replace(marker, SECTION + "\n\n" + marker, 1)

    source_marker = "</ul><small>"
    if source_marker not in text:
        raise RuntimeError("V profilu chybí konec seznamu zdrojů.")
    additions = []
    for href, label in SOURCES:
        if href not in text:
            additions.append(
                f'    <li><a href="{href}" target="_blank" rel="noopener noreferrer">{label}</a></li>'
            )
    if additions:
        text = text.replace(source_marker, "\n" + "\n".join(additions) + "\n  " + source_marker, 1)

    text = text.replace(
        '<span class="series-nav__meta">Závěrečný díl série</span>',
        '<span class="series-nav__meta">29. července 2026 · 5:00</span>',
    )
    return write_if_changed(PROFILE, text) if text != original else False


def patch_arc() -> bool:
    text = ARC.read_text(encoding="utf-8")
    text = re.sub(
        r'\s*<section data-hospital-profile-teaser.*?</section>\s*',
        "\n",
        text,
        flags=re.S,
    )
    marker = '  <div class="source-list">'
    if marker in text:
        text = text.replace(marker, TEASER + "\n\n" + marker, 1)
    elif "</article>" in text:
        text = text.replace("</article>", TEASER + "\n</article>", 1)
    else:
        raise RuntimeError("ARC-MED nemá blok zdrojů ani konec article.")
    return write_if_changed(ARC, text)


def patch_series() -> bool:
    text = SERIES.read_text(encoding="utf-8")
    original = text
    text = text.replace(
        '"date": "Závěrečný díl série",',
        '"date": "29. července 2026 · 5:00",',
    )
    text = text.replace(
        '"scheduled_label": "Připravujeme závěrečný díl",',
        '"scheduled_label": "Vyjde ve středu 29. 7. v 5:00",',
    )
    text = text.replace(
        '>Připravujeme</span>',
        '>Vyjde ve středu 29. 7. v 5:00</span>',
    )
    text = text.replace(
        'label = "PŘIPRAVUJEME · ZÁVĚREČNÝ DÍL SÉRIE"',
        'label = "STŘEDA 29. 7. V 5:00 · ZÁVĚREČNÝ DÍL SÉRIE"',
    )
    text = text.replace(
        "Závěr série představí nemocnici jako celek: její oddělení, 254 lůžek, téměř 480 pracovních úvazků, výkony, spádovou oblast i otázky budoucnosti.",
        "Závěr série představí nemocnici jako celek: její oddělení, 254 lůžek, téměř 480 pracovních úvazků, výkony, spádovou oblast, příspěvky okolních obcí i otázky budoucnosti.",
    )
    return write_if_changed(SERIES, text) if text != original else False


def main() -> int:
    for path in (PROFILE, ARC, SERIES):
        if not path.is_file():
            raise FileNotFoundError(path)
    changed = [patch_profile(), patch_arc(), patch_series()]
    print("Aktualizace profilu, upoutávky a termínu dokončena.", "Změny:" if any(changed) else "Beze změn.", sum(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
