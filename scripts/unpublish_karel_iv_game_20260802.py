#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]

GAME_DIR = ROOT / "hry" / "prijezd-karla-iv"
GAMES_INDEX = ROOT / "hry" / "index.html"
SOCIAL = ROOT / "social" / "hra-prijezd-karla-iv-1367.png"
HOME = ROOT / "index.html"
ARTICLE = ROOT / "clanky" / "kulturni-zarizeni-kadan.html"
SITEMAP = ROOT / "sitemap.xml"

OLD_PUBLICATION_FILES = [
    ROOT / ".github" / "workflows" / "deploy-karel-iv-game-on-issue.yml",
    ROOT / ".github" / "workflows" / "recover-karel-iv-game-on-issue.yml",
    ROOT / ".github" / "workflows" / "recover-karel-iv-game-atomic.yml",
    ROOT / "scripts" / "publish_karel_iv_game_20260802.py",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def remove_game_nav(text: str) -> str:
    return text.replace('<a href="/hry/">Hry</a>', '')


def clean_home() -> None:
    text = read(HOME)
    text = re.sub(
        r"\s*<style\b[^>]*data-karel-game-promo-style[^>]*>.*?</style>",
        "",
        text,
        count=1,
        flags=re.S | re.I,
    )
    text = re.sub(
        r"\s*<section\b[^>]*data-karel-game-promo[^>]*>.*?</section>",
        "",
        text,
        count=1,
        flags=re.S | re.I,
    )
    text = remove_game_nav(text)
    write(HOME, text)


def clean_article() -> None:
    text = read(ARTICLE)
    text = re.sub(
        r"\s*<div\b[^>]*data-karel-game-link[^>]*>.*?</div>\s*</div>",
        "",
        text,
        count=1,
        flags=re.S | re.I,
    )
    # Záloha pro případ, že struktura tlačítka nebude mít vnořený uzavírací div.
    text = re.sub(
        r"\s*<div\b[^>]*data-karel-game-link[^>]*>.*?</div>",
        "",
        text,
        count=1,
        flags=re.S | re.I,
    )
    text = remove_game_nav(text)
    write(ARTICLE, text)


def clean_sitemap() -> None:
    text = read(SITEMAP)
    for url in (
        "https://nasekadan.cz/hry/",
        "https://nasekadan.cz/hry/prijezd-karla-iv/",
    ):
        text = re.sub(
            rf"\s*<url>\s*<loc>{re.escape(url)}</loc>.*?</url>",
            "",
            text,
            flags=re.S,
        )
    write(SITEMAP, text)


def remove_public_files() -> None:
    if GAME_DIR.exists():
        shutil.rmtree(GAME_DIR)
    if GAMES_INDEX.exists():
        GAMES_INDEX.unlink()
    games_root = ROOT / "hry"
    if games_root.exists() and not any(games_root.iterdir()):
        games_root.rmdir()
    if SOCIAL.exists():
        SOCIAL.unlink()
    for path in OLD_PUBLICATION_FILES:
        if path.exists():
            path.unlink()


def verify() -> None:
    for path in (HOME, ARTICLE, SITEMAP):
        text = read(path)
        if "/hry/prijezd-karla-iv/" in text or "data-karel-game" in text:
            raise SystemExit(f"Veřejný odkaz na hru zůstal v {path.relative_to(ROOT)}")
    if '<a href="/hry/">Hry</a>' in read(HOME) or '<a href="/hry/">Hry</a>' in read(ARTICLE):
        raise SystemExit("Ve veřejné navigaci zůstal odkaz Hry.")
    if GAME_DIR.exists() or GAMES_INDEX.exists() or SOCIAL.exists():
        raise SystemExit("Veřejné soubory hry nebyly odstraněny.")


def main() -> None:
    clean_home()
    clean_article()
    clean_sitemap()
    remove_public_files()
    verify()
    print("Veřejná hra a všechny její veřejné odkazy byly odstraněny ze zdrojové větve.")


if __name__ == "__main__":
    main()
