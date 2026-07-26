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
]

DRAFTS = {
    ".github/drafts/nemocnice-kadan-software-kyberbezpecnost.html": 2,
}

CSS = r'''
/* Série Nemocnice Kadaň */
.series-nav{margin:28px 0 34px;padding:24px;border:1px solid var(--line);border-radius:20px;background:linear-gradient(135deg,#f8fafb,#f5eee5);box-shadow:0 12px 34px rgba(20,35,45,.08)}
.series-nav__eyebrow{margin:0 0 7px!important;color:var(--red);font-size:12px!important;font-weight:900;letter-spacing:.09em;text-transform:uppercase}
.series-nav h2{margin:0 0 8px!important;font:800 28px/1.15 Georgia,serif!important}
.series-nav__intro{margin:0 0 18px!important;color:#52616a;font-size:16px!important}
.series-nav__list{display:grid;gap:10px;margin:0;padding:0;list-style:none;counter-reset:hospital-series}
.series-nav__item{counter-increment:hospital-series;position:relative;margin:0!important;padding:0!important}
.series-nav__item>a,.series-nav__current{display:block;padding:15px 16px 15px 54px;border:1px solid #d6e0e4;border-radius:14px;background:#fff;color:#172b38!important;text-decoration:none!important;transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease}
.series-nav__item>a:before,.series-nav__current:before{content:counter(hospital-series);position:absolute;left:16px;top:16px;width:25px;height:25px;border-radius:50%;display:grid;place-items:center;background:#172b38;color:#fff;font-size:13px;font-weight:900}
.series-nav__item>a:hover{transform:translateY(-1px);border-color:#a9232b;box-shadow:0 8px 20px rgba(20,35,45,.09)}
.series-nav__current{border-color:#a9232b;background:#fff7f7;box-shadow:inset 4px 0 0 #a9232b}
.series-nav__current:before{background:#a9232b}
.series-nav__title{display:block;font:800 18px/1.25 Georgia,serif}
.series-nav__meta{display:block;margin-top:3px;color:#6a7880;font-size:13px}
.series-nav__summary{display:block;margin-top:5px;color:#52616a;font-size:14px;line-height:1.45}
.series-nav__state{display:inline-block;margin-top:7px;color:#a9232b;font-size:12px;font-weight:900;letter-spacing:.05em;text-transform:uppercase}
@media(max-width:700px){.series-nav{padding:19px}.series-nav h2{font-size:24px!important}.series-nav__item>a,.series-nav__current{padding-left:49px}}
/* /Série Nemocnice Kadaň */
'''.strip()


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
        else:
            inner = f'<a href="{item["url"]}">{body}</a>'
        items.append(f'      <li class="series-nav__item">{inner}</li>')

    return "\n".join(
        [
            '  <section class="series-nav" data-hospital-series aria-labelledby="hospital-series-title">',
            '    <p class="series-nav__eyebrow">SÉRIE NAŠE KADAŇ</p>',
            '    <h2 id="hospital-series-title">Nemocnice Kadaň: celý příběh krok za krokem</h2>',
            '    <p class="series-nav__intro">Jednotlivé texty na sebe navazují. Série odděluje doložená fakta, veřejná tvrzení a otázky, na které nemocnice nebo město zatím neodpověděly.</p>',
            '    <ol class="series-nav__list">',
            *items,
            '    </ol>',
            '  </section>',
        ]
    )


def rel_links(current_index: int) -> str:
    lines: list[str] = []
    if current_index > 0:
        lines.append(f'  <link rel="prev" href="https://nasekadan.cz{SERIES[current_index - 1]["url"]}" data-hospital-series-rel>')
    if current_index < len(SERIES) - 1:
        lines.append(f'  <link rel="next" href="https://nasekadan.cz{SERIES[current_index + 1]["url"]}" data-hospital-series-rel>')
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
        if index == current_index:
            if item["title"] not in text or 'aria-current="page"' not in text:
                raise RuntimeError(f"V {path} není označen aktuální díl")
        elif f'href="{item["url"]}"' not in text:
            raise RuntimeError(f"V {path} chybí odkaz na {item['url']}")


def main() -> int:
    changed = patch_style()
    for index, item in enumerate(SERIES):
        path = ROOT / item["path"]
        if not path.is_file():
            raise RuntimeError(f"Chybí článek {path}")
        changed = patch_article(path, index) or changed
        validate(path, index)

    for draft, index in DRAFTS.items():
        path = ROOT / draft
        if path.is_file():
            changed = patch_article(path, index) or changed
            validate(path, index)

    css = STYLE.read_text(encoding="utf-8")
    if ".series-nav__list" not in css:
        raise RuntimeError("V globálním stylu chybí pravidla série")

    print("Propojení série Nemocnice Kadaň je kompletní.", "Změněno." if changed else "Beze změn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
