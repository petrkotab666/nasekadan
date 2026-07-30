#!/usr/bin/env python3
"""Sjednotí konstrukci článků Naše Kadaň a ověří její dodržení.

Pravidlo je záměrně centrální: každý článek používá stejný article-shell,
přímý pravý panel <aside class="sticky">, jeden sidebar reklamní slot a stejný
balík reklamních skriptů. Skript nemění redakční text článků.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEMPLATE_VERSION = "unified-v1"
ASSET_VERSION = "20260730-pojistime-rotation-4"
SCRIPT_BLOCK = (
    '<script src="/site.js" defer></script>\n'
    f'<script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script>\n'
    f'<script src="/ad-spacing-guard.js?v={ASSET_VERSION}" defer></script>\n'
    f'<script src="/reklamy-oprava-obrazku.js?v={ASSET_VERSION}"></script>\n'
    f'<script src="/obsah-doplnky.js?v={ASSET_VERSION}"></script>'
)

AD_SCRIPT_RE = re.compile(
    r"\s*<script\s+src=[\"'][^\"']*(?:site\.js|reklamy\.js|ad-spacing-guard\.js|reklamy-oprava-obrazku\.js|reklamy-popisy\.js|obsah-doplnky\.js)(?:\?[^\"']*)?[\"']\s*(?:defer)?\s*></script>",
    re.IGNORECASE,
)


def is_article(text: str) -> bool:
    return "article-shell" in text and re.search(r'<article\b[^>]*class=["\'][^"\']*\barticle\b', text, re.I) is not None


def normalize_sidebar(text: str) -> str:
    # Starší varianta: <aside><div class="sticky">…</div></aside>
    text, nested_count = re.subn(
        r'<aside\s*>\s*<div\s+class=["\']sticky["\']\s*>',
        '<aside class="sticky">',
        text,
        count=1,
        flags=re.I,
    )
    if nested_count:
        text = re.sub(
            r'</div>\s*</aside>(\s*</main>)',
            r'</aside>\1',
            text,
            count=1,
            flags=re.I,
        )

    # Jiná starší varianta: přímý aside bez třídy sticky.
    text = re.sub(r'<aside\s*>', '<aside class="sticky">', text, count=1, flags=re.I)

    # Sjednotit třídu, pokud aside sticky obsahuje další třídy v jiném pořadí.
    def normalize_aside_tag(match: re.Match[str]) -> str:
        attrs = match.group(1)
        class_match = re.search(r'class=["\']([^"\']*)["\']', attrs, re.I)
        classes = class_match.group(1).split() if class_match else []
        classes = [value for value in classes if value != "sticky"]
        classes.insert(0, "sticky")
        if class_match:
            attrs = attrs[: class_match.start()] + f'class="{" ".join(classes)}"' + attrs[class_match.end() :]
        else:
            attrs = f' class="{" ".join(classes)}"' + attrs
        return f'<aside{attrs}>'

    text = re.sub(
        r'<aside([^>]*)>',
        normalize_aside_tag,
        text,
        count=1,
        flags=re.I,
    )

    # Každý pravý panel má stejný reklamní slot.
    aside_match = re.search(
        r'(<aside\b[^>]*class=["\'][^"\']*\bsticky\b[^"\']*["\'][^>]*>)(.*?)(</aside>)',
        text,
        re.I | re.S,
    )
    if aside_match and "data-promos" not in aside_match.group(2):
        body = aside_match.group(2).rstrip()
        replacement = f'{aside_match.group(1)}{body}\n  <div data-promos data-context="sidebar"></div>\n{aside_match.group(3)}'
        text = text[: aside_match.start()] + replacement + text[aside_match.end() :]

    return text


def normalize_article(text: str) -> str:
    # Označení jednotné šablony umožní další automatické kontroly.
    text = re.sub(
        r'<main\b([^>]*class=["\'][^"\']*\barticle-shell\b[^"\']*["\'][^>]*)>',
        lambda match: (
            match.group(0)
            if "data-article-template" in match.group(1)
            else f'<main{match.group(1)} data-article-template="{TEMPLATE_VERSION}">'
        ),
        text,
        count=1,
        flags=re.I,
    )

    text = normalize_sidebar(text)

    # Jediný společný balík skriptů na konci stránky. site.js spouští průběžné
    # střídání různých partnerských nabídek v pravém sloupci; bez něj může být
    # slot přítomný, ale zůstane prázdný nebo statický. Pojistka rozestupů navíc
    # odstraní automatickou reklamu, pokud by se ocitla hned za jinou reklamou.
    text = AD_SCRIPT_RE.sub("", text)
    body_matches = list(re.finditer(r'</body>', text, re.I))
    if body_matches:
        pos = body_matches[-1].start()
        text = text[:pos].rstrip() + "\n" + SCRIPT_BLOCK + "\n" + text[pos:]

    return text


def validate(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    if f'data-article-template="{TEMPLATE_VERSION}"' not in text:
        errors.append("chybí označení jednotné šablony")
    if re.search(r'<aside\s*>\s*<div\s+class=["\']sticky["\']', text, re.I):
        errors.append("zůstal vnořený pravý panel")
    if not re.search(r'</article>\s*<aside\b[^>]*class=["\'][^"\']*\bsticky\b', text, re.I):
        errors.append("pravý panel není přímým sourozencem článku")
    if not re.search(
        r'<aside\b[^>]*class=["\'][^"\']*\bsticky\b[^"\']*["\'][^>]*>.*?data-promos[^>]*data-context=["\']sidebar["\'].*?</aside>',
        text,
        re.I | re.S,
    ):
        errors.append("pravý panel nemá společný reklamní slot")
    for asset in (
        "/site.js",
        "/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3",
        "/ad-spacing-guard.js",
        "/reklamy-oprava-obrazku.js",
        "/obsah-doplnky.js",
    ):
        if text.count(asset) != 1:
            errors.append(f"soubor {asset} není načten právě jednou")
    if f'/reklamy-oprava-obrazku.js?v={ASSET_VERSION}' not in text:
        errors.append("opravný reklamní balík nemá aktuální letní verzi")
    if "</body>" not in text.lower():
        errors.append("chybí ukončení body")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="zapsat sjednocenou konstrukci")
    parser.add_argument("--check", action="store_true", help="ověřit jednotnou konstrukci")
    args = parser.parse_args()
    if not args.write and not args.check:
        args.write = args.check = True

    article_paths = sorted(Path("clanky").glob("*.html"))
    changed = 0
    checked = 0
    failures: list[str] = []

    for path in article_paths:
        original = path.read_text(encoding="utf-8")
        if not is_article(original):
            continue
        checked += 1
        current = normalize_article(original) if args.write else original
        if args.write and current != original:
            path.write_text(current, encoding="utf-8")
            changed += 1
            print(f"Sjednoceno: {path}")
        if args.check:
            for error in validate(path, current):
                failures.append(f"{path}: {error}")

    print(f"Článků zkontrolováno: {checked}; změněno: {changed}")
    if failures:
        print("Chyby jednotné konstrukce:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
