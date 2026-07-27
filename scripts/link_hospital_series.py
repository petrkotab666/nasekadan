#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "style.css"

SERIES = [
    {
        "path": "clanky/nemocnice-kadan.html",
        "url": "/clanky/nemocnice-kadan.html",
        "date": "24. července 2026",
        "title": "Ztráta 46 milionů, pomoc města a rozkol ODS",
        "summary": "Výchozí analýza hospodaření, propadu hotovosti, provozu a politické odpovědnosti.",
    },
    {
        "path": "clanky/petice-nemocnice-kadan.html",
        "url": "/clanky/petice-nemocnice-kadan.html",
        "date": "25. července 2026",
        "title": "Petice, 100 milionů a údajný prodej nemocnice",
        "summary": "Ověření tvrzení o dotacích, kyberbezpečnosti, refundaci a budoucím vlastnictví.",
    },
    {
        "path": "clanky/nemocnice-kadan-software-kyberbezpecnost.html",
        "url": "/clanky/nemocnice-kadan-software-kyberbezpecnost.html",
        "date": "26. července 2026",
        "title": "64,7 milionu za software a kyberbezpečnost",
        "summary": "Rozpad IT investic, smluv se STAPRO, servisu a dosud nevysvětleného konečného účtu.",
    },
    {
        "path": "clanky/avies-nemocnice-kadan.html",
        "url": "/clanky/avies-nemocnice-kadan.html",
        "date": "27. července 2026",
        "title": "Téměř 170 milionů za léčiva od AVIES",
        "summary": "Sedm let plateb, vývoj smluvního vztahu, konsignační sklad a chybějící dokument pro rok 2024.",
    },
    {
        "path": "clanky/arc-med-nemocnice-kadan.html",
        "url": "/clanky/arc-med-nemocnice-kadan.html",
        "date": "28. července 2026 · 5:00",
        "title": "ARC-MED za 16 milionů: dva posudky a nejasné schválení",
        "summary": "Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.",
        "scheduled_label": "Vyjde v úterý 28. 7. v 5:00",
    },
]

DRAFTS = {
    ".github/drafts/nemocnice-kadan-software-kyberbezpecnost.html": 2,
    ".github/drafts/arc-med-nemocnice-kadan.html": 4,
}

CSS = r'''
/* Série Nemocnice Kadaň */
.series-nav{margin:28px 0 34px;padding:24px;border:1px solid var(--line);border-radius:20px;background:linear-gradient(135deg,#f8fafb,#f5eee5);box-shadow:0 12px 34px rgba(20,35,45,.08)}
.series-nav__eyebrow{margin:0 0 7px!important;color:var(--red);font-size:12px!important;font-weight:900;letter-spacing:.09em;text-transform:uppercase}
.series-nav h2{margin:0 0 8px!important;font:800 28px/1.15 Georgia,serif!important}
.series-nav__intro{margin:0 0 18px!important;color:#52616a;font-size:16px!important}
.series-nav__list{display:grid;gap:10px;margin:0;padding:0;list-style:none;counter-reset:hospital-series}
.series-nav__item{counter-increment:hospital-series;position:relative;margin:0!important;padding:0!important}
.series-nav__item>a,.series-nav__current,.series-nav__scheduled{display:block;padding:15px 16px 15px 54px;border:1px solid #d6e0e4;border-radius:14px;background:#fff;color:#172b38!important;text-decoration:none!important;transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease}
.series-nav__item>a:before,.series-nav__current:before,.series-nav__scheduled:before{content:counter(hospital-series);position:absolute;left:16px;top:16px;width:25px;height:25px;border-radius:50%;display:grid;place-items:center;background:#172b38;color:#fff;font-size:13px;font-weight:900}
.series-nav__item>a:hover{transform:translateY(-1px);border-color:#a9232b;box-shadow:0 8px 20px rgba(20,35,45,.09)}
.series-nav__current{border-color:#a9232b;background:#fff7f7;box-shadow:inset 4px 0 0 #a9232b}
.series-nav__current:before{background:#a9232b}
.series-nav__scheduled{border-style:dashed;background:#f8fafb;color:#53636c!important}
.series-nav__scheduled:before{background:#73838b}
.series-nav__title{display:block;font:800 18px/1.25 Georgia,serif}
.series-nav__meta{display:block;margin-top:3px;color:#6a7880;font-size:13px}
.series-nav__summary{display:block;margin-top:5px;color:#52616a;font-size:14px;line-height:1.45}
.series-nav__state{display:inline-block;margin-top:7px;color:#a9232b;font-size:12px;font-weight:900;letter-spacing:.05em;text-transform:uppercase}
.series-nav__scheduled .series-nav__state{color:#5c6b73}
@media(max-width:700px){.series-nav{padding:19px}.series-nav h2{font-size:24px!important}.series-nav__item>a,.series-nav__current,.series-nav__scheduled{padding-left:49px}}
/* /Série Nemocnice Kadaň */
'''.strip()


def is_public(index: int) -> bool:
    return (ROOT / SERIES[index]["path"]).is_file()


def series_block(current_index: int) -> str:
    items: list[str] = []
    for index, item in enumerate(SERIES):
        body = (
            f'<span class="series-nav__title">{item["title"]}</span>'
            f'<span class="series-nav__meta">{item["date"]}</span>'
            f'<span class="series-nav__summary">{item["summary"]}</span>'
        )
        if index == current_index:
            inner = f'<span class="series-nav__current" aria-current="page">{body}<span class="series-nav__state">Právě čtete</span></span>'
        elif is_public(index):
            inner = f'<a href="{item["url"]}">{body}</a>'
        else:
            state = item.get("scheduled_label", "Připravujeme")
            inner = f'<span class="series-nav__scheduled" aria-disabled="true">{body}<span class="series-nav__state">{state}</span></span>'
        items.append(f'      <li class="series-nav__item">{inner}</li>')

    return "\n".join(
        [
            '  <section class="series-nav" data-hospital-series aria-labelledby="hospital-series-title">',
            '    <p class="series-nav__eyebrow">SÉRIE NAŠE KADAŇ</p>',
            '    <h2 id="hospital-series-title">Nemocnice Kadaň: celý příběh krok za krokem</h2>',
            '    <p class="series-nav__intro">Pět navazujících textů odděluje doložená fakta, veřejná tvrzení a otázky, na které nemocnice nebo město zatím neodpověděly.</p>',
            '    <ol class="series-nav__list">',
            *items,
            '    </ol>',
            '  </section>',
        ]
    )


def rel_links(current_index: int) -> str:
    lines: list[str] = []
    previous = next((i for i in range(current_index - 1, -1, -1) if is_public(i)), None)
    following = next((i for i in range(current_index + 1, len(SERIES)) if is_public(i)), None)
    if previous is not None:
        lines.append(f'  <link rel="prev" href="https://nasekadan.cz{SERIES[previous]["url"]}" data-hospital-series-rel>')
    if following is not None:
        lines.append(f'  <link rel="next" href="https://nasekadan.cz{SERIES[following]["url"]}" data-hospital-series-rel>')
    return "\n".join(lines)


def patch_article(path: Path, current_index: int) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = re.sub(
        r'\s*<section class="series-nav" data-hospital-series.*?</section>\s*',
        "\n\n",
        text,
        flags=re.S,
    )
    text = re.sub(r'\s*<link[^>]+data-hospital-series-rel[^>]*>\s*', "\n", text)

    # Starší AVIES box nahradí jednotná navigace pětidílné série.
    text = re.sub(
        r'\s*<div class="series-box">\s*<strong>Série Naší Kadaně: Nemocnice Kadaň</strong>.*?</div>\s*',
        "\n\n",
        text,
        count=1,
        flags=re.S,
    )

    lead = re.search(r'<p class="leadtext">.*?</p>', text, flags=re.S)
    if not lead:
        raise RuntimeError(f"V {path} chybí úvodní odstavec leadtext")
    block = "\n\n" + series_block(current_index)
    text = text[: lead.end()] + block + text[lead.end() :]

    rel = rel_links(current_index)
    if rel:
        if "</head>" not in text:
            raise RuntimeError(f"V {path} chybí </head>")
        text = text.replace("</head>", rel + "\n</head>", 1)

    path.write_text(text, encoding="utf-8", newline="\n")
    return text != original


def arc_med_teaser() -> str:
    if is_public(4):
        cta = '<a href="/clanky/arc-med-nemocnice-kadan.html" style="display:inline-flex;padding:13px 18px;border-radius:10px;background:#fff;color:#8f2027;font-weight:900;text-decoration:none">Přečíst navazující analýzu →</a>'
        label = "NOVĚ ZVEŘEJNĚNO · PÁTÝ DÍL SÉRIE"
    else:
        cta = '<span style="display:inline-block;padding:10px 14px;border:1px solid rgba(255,255,255,.45);border-radius:999px;color:#fff;font-weight:900">Vyjde v úterý 28. 7. v 5:00</span>'
        label = "ZÍTRA V 5:00 · PÁTÝ DÍL SÉRIE"
    return f'''
  <section data-arc-med-teaser style="margin:44px 0 24px;padding:28px;border-radius:20px;background:linear-gradient(135deg,#14232d,#355d70 62%,#9f2626);color:#fff;box-shadow:0 18px 45px rgba(20,35,45,.20)">
    <p style="margin:0 0 8px;color:#ffd9d9;font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase">{label}</p>
    <h2 style="margin:0 0 12px;color:#fff;font:800 32px/1.15 Georgia,serif">ARC-MED za 16 milionů: dva posudky, nejasné schválení a spor o dvanáct milionů</h2>
    <p style="margin:0 0 16px;color:#edf3f5;font-size:18px">Co nemocnice skutečně koupila, proč se dva odhady hodnoty výrazně rozcházejí, kdo o ceně věděl a co zatím veřejné dokumenty neprokazují.</p>
    {cta}
  </section>'''


def patch_avies_teaser() -> bool:
    path = ROOT / "clanky" / "avies-nemocnice-kadan.html"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r'\s*<section data-arc-med-teaser.*?</section>\s*', "\n", text, flags=re.S)
    marker = '  <div class="source-list">'
    teaser = arc_med_teaser() + "\n\n"
    if marker in text:
        text = text.replace(marker, teaser + marker, 1)
    elif "</article>" in text:
        text = text.replace("</article>", teaser + "</article>", 1)
    else:
        raise RuntimeError("Článek AVIES nemá blok zdrojů ani konec article.")
    path.write_text(text, encoding="utf-8", newline="\n")
    return text != original


def patch_style() -> bool:
    text = STYLE.read_text(encoding="utf-8")
    original = text
    text = re.sub(
        r'\n?/\* Série Nemocnice Kadaň \*/.*?/\* /Série Nemocnice Kadaň \*/\n?',
        "\n",
        text,
        flags=re.S,
    ).rstrip()
    text += "\n\n" + CSS + "\n"
    STYLE.write_text(text, encoding="utf-8", newline="\n")
    return text != original


def validate(path: Path, current_index: int) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count('data-hospital-series') < 1:
        raise RuntimeError(f"V {path} chybí navigace série")
    for index, item in enumerate(SERIES):
        if item["title"] not in text:
            raise RuntimeError(f"V {path} chybí díl série: {item['title']}")
        if index == current_index:
            if 'aria-current="page"' not in text:
                raise RuntimeError(f"V {path} není označen aktuální díl")
        elif is_public(index):
            if f'href="{item["url"]}"' not in text:
                raise RuntimeError(f"V {path} chybí odkaz na {item['url']}")
        elif 'series-nav__scheduled' not in text:
            raise RuntimeError(f"V {path} chybí označení připravovaného dílu")


def main() -> int:
    changed = patch_style()
    for index, item in enumerate(SERIES):
        path = ROOT / item["path"]
        if not path.is_file():
            continue
        changed = patch_article(path, index) or changed
        validate(path, index)

    for draft, index in DRAFTS.items():
        path = ROOT / draft
        if path.is_file():
            changed = patch_article(path, index) or changed
            validate(path, index)

    changed = patch_avies_teaser() or changed

    css = STYLE.read_text(encoding="utf-8")
    if ".series-nav__scheduled" not in css:
        raise RuntimeError("V globálním stylu chybí pravidla pětidílné série")

    print("Propojení pěti dílů série Nemocnice Kadaň je kompletní.", "Změněno." if changed else "Beze změn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
