#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"

HOME_OLD_VISUAL = ".article-card .visual{height:170px;display:flex;align-items:flex-end;padding:22px;color:#fff;position:relative;overflow:hidden}"
HOME_NEW_VISUAL = ".article-card .visual{height:240px;display:flex;align-items:flex-end;padding:24px 22px;color:#fff;position:relative;overflow:hidden}"
HOME_OLD_TITLE = ".article-card .visual strong{position:relative;z-index:1;font:900 31px/1 Georgia,serif}"
HOME_NEW_TITLE = ".article-card .visual strong{position:relative;z-index:1;max-width:100%;font:900 clamp(24px,1.8vw,29px)/1.06 Georgia,serif;overflow-wrap:anywhere;hyphens:auto}"
HOME_OLD_MEDIA = "@media(max-width:850px){.article-list{grid-template-columns:1fr}.section-head{display:block}.section-head .btn{margin-top:18px}.current-aside .aside-button{width:100%;justify-content:center}}"
HOME_NEW_MEDIA = "@media(max-width:850px){.article-list{grid-template-columns:1fr}.article-card .visual{height:auto;min-height:165px}.article-card .visual strong{font-size:27px}.section-head{display:block}.section-head .btn{margin-top:18px}.current-aside .aside-button{width:100%;justify-content:center}}"

ARCHIVE_CARD_CSS = """
    /* Automaticky generované karty používají stejné úplné nadpisy jako úvodní stránka. */
    .archive-list .article-card{display:grid;grid-template-columns:300px 1fr;background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden;box-shadow:var(--shadow)}
    .archive-list .article-card .visual{min-height:230px;display:flex;align-items:flex-end;padding:24px;color:#fff;position:relative;overflow:hidden}
    .archive-list .article-card .visual:after{content:'';position:absolute;inset:0;background:linear-gradient(transparent,rgba(0,0,0,.58))}
    .archive-list .article-card .visual strong{position:relative;z-index:1;max-width:100%;font:900 clamp(24px,2.1vw,30px)/1.06 Georgia,serif;overflow-wrap:anywhere;hyphens:auto}
    .archive-list .article-card .article-body{padding:26px;display:flex;flex-direction:column}
    .archive-list .article-card .meta{color:var(--red);font-size:12px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
    .archive-list .article-card h3{font:800 32px/1.15 Georgia,serif;margin:8px 0 12px}
    .archive-list .article-card p{color:#58666e;font-size:17px;margin:0 0 20px}
    .archive-list .article-card .read-more{margin-top:auto;color:var(--red);font-weight:900}
""".rstrip()

ARCHIVE_OLD_MEDIA = "@media(max-width:760px){.archive-item{grid-template-columns:1fr}.archive-visual{min-height:150px}.archive-body h2{font-size:27px}}"
ARCHIVE_NEW_MEDIA = "@media(max-width:760px){.archive-item,.archive-list .article-card{grid-template-columns:1fr}.archive-visual,.archive-list .article-card .visual{min-height:165px;height:auto}.archive-body h2,.archive-list .article-card h3{font-size:27px}}"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Nelze najít očekávaný styl: {label}")
    return text.replace(old, new, 1)


def fix_home() -> None:
    text = HOME.read_text(encoding="utf-8")
    text = replace_once(text, HOME_OLD_VISUAL, HOME_NEW_VISUAL, "výška vizuálu karty")
    text = replace_once(text, HOME_OLD_TITLE, HOME_NEW_TITLE, "typografie nadpisu karty")
    text = replace_once(text, HOME_OLD_MEDIA, HOME_NEW_MEDIA, "mobilní zobrazení karet")
    HOME.write_text(text, encoding="utf-8", newline="\n")


def fix_archive() -> None:
    text = ARCHIVE.read_text(encoding="utf-8")
    if ARCHIVE_CARD_CSS not in text:
        marker = "    .archive-rule{margin-top:34px;padding:24px;background:var(--cream);border-radius:16px}"
        if marker not in text:
            raise RuntimeError("V archivu chybí kotevní styl .archive-rule")
        text = text.replace(marker, marker + "\n" + ARCHIVE_CARD_CSS, 1)
    text = replace_once(text, ARCHIVE_OLD_MEDIA, ARCHIVE_NEW_MEDIA, "mobilní archiv")
    ARCHIVE.write_text(text, encoding="utf-8", newline="\n")


def verify() -> None:
    home = HOME.read_text(encoding="utf-8")
    archive = ARCHIVE.read_text(encoding="utf-8")
    assert "[:54]" not in (ROOT / "scripts" / "enforce_article_visibility.py").read_text(encoding="utf-8")
    assert HOME_NEW_VISUAL in home
    assert HOME_NEW_TITLE in home
    assert "Starosta: Nemocnice to zvládne, na Béčku vyroste vyšší dům a na nepedagogy peníze budou</strong>" in home
    assert "Přetékající koše v Kadani budí kritiku. Město mluví o odchodu řidičů</strong>" in home
    assert "ZŠ Chomutovská od září zdraží obědy. Rodiče mají zvýšit limit inkasa</strong>" in home
    assert ARCHIVE_CARD_CSS in archive
    assert "height:170px" not in home


def main() -> None:
    fix_home()
    fix_archive()
    verify()
    print("Úplné nadpisy karet a pružné rozměry byly nastaveny na úvodu i v archivu.")


if __name__ == "__main__":
    main()
