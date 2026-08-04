#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "enforce_article_visibility.py"
HOME = ROOT / "index.html"
PIN_HREF = "/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html"
MARKER = "HOMEPAGE-PIN-STADIUM-20260804"


def patch_generator() -> None:
    text = GENERATOR.read_text(encoding="utf-8")
    if MARKER in text:
        compile(text, str(GENERATOR), "exec")
        return

    anchor = "PAGE_SIZE = 12\n"
    insert = (
        "PAGE_SIZE = 12\n"
        "# HOMEPAGE-PIN-STADIUM-20260804\n"
        "HOMEPAGE_PIN_HREF = '/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html'\n"
        "HOMEPAGE_PIN_UNTIL = datetime.fromisoformat('2026-08-05T18:00:00+02:00')\n"
    )
    if anchor not in text:
        raise RuntimeError("Nelze vložit konfiguraci připnutí.")
    text = text.replace(anchor, insert, 1)

    old = (
        "    homepage_articles = articles[:HOME_TOTAL]\n"
        "    home_cards = '\\n'.join(card(article) for article in homepage_articles[2:])\n"
    )
    new = (
        "    homepage_order = list(articles)\n"
        "    if datetime.now(timezone.utc) <= HOMEPAGE_PIN_UNTIL.astimezone(timezone.utc):\n"
        "        pinned = next((item for item in articles if item['href'] == HOMEPAGE_PIN_HREF), None)\n"
        "        if pinned is None:\n"
        "            raise RuntimeError('Připínaný článek nebyl nalezen.')\n"
        "        homepage_order = [pinned] + [item for item in articles if item['href'] != HOMEPAGE_PIN_HREF]\n"
        "    homepage_articles = homepage_order[:HOME_TOTAL]\n"
        "    home_cards = '\\n'.join(card(article) for article in homepage_articles[2:])\n"
    )
    if old not in text:
        raise RuntimeError("Nelze upravit pořadí článků na titulce.")
    text = text.replace(old, new, 1)

    old_hero = "hero(articles[0], articles[1] if len(articles) > 1 else None)"
    new_hero = "hero(homepage_order[0], homepage_order[1] if len(homepage_order) > 1 else None)"
    if old_hero not in text:
        raise RuntimeError("Nelze upravit hlavní blok titulky.")
    text = text.replace(old_hero, new_hero, 1)

    compile(text, str(GENERATOR), "exec")
    GENERATOR.write_text(text, encoding="utf-8", newline="\n")


def restore_non_home_outputs() -> None:
    subprocess.run(
        ["git", "restore", "--source=HEAD", "--worktree", "--", "clanky/index.html", "sitemap.xml"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        "git restore --source=HEAD --worktree -- clanky/strana-*.html 2>/dev/null || true",
        cwd=ROOT,
        shell=True,
        check=True,
    )


def validate_home() -> None:
    text = HOME.read_text(encoding="utf-8")
    hero = re.search(r'<section class="wrap hero" id="clanky".*?</section>', text, re.S)
    if not hero or f'data-latest-article-href="{PIN_HREF}"' not in hero.group(0):
        raise RuntimeError("Připnutí se nevytvořilo.")
    aside = re.search(r'<aside class="current-aside">.*?</aside>', hero.group(0), re.S)
    if not aside or PIN_HREF in aside.group(0):
        raise RuntimeError("Boční blok není zachován správně.")
    if "/pocasi.js" not in text:
        raise RuntimeError("Na titulce chybí počasí.")


if __name__ == "__main__":
    patch_generator()
    subprocess.run(["python3", str(GENERATOR)], cwd=ROOT, check=True)
    restore_non_home_outputs()
    validate_home()
    print("Připnutí článku o zimním stadionu bylo bezpečně obnoveno pouze na titulce.")
