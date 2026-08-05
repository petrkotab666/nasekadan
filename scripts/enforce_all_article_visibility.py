#!/usr/bin/env python3
"""Kanonická pojistka viditelnosti všech publikovaných článků.

Jediným zdrojem pravdy jsou indexovatelné HTML články v ``clanky/``. Skript
z nich znovu sestaví titulku, celý stránkovaný archiv a sitemapu. Ignoruje
budoucí naplánované články a ruší jednorázová historická připnutí titulky,
aby pozdější workflow nemohlo přepsat novější článek starším obsahem.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "scripts" / "enforce_article_visibility.py"
ARTICLE_LINK_RE = re.compile(r'href=["\'](/clanky/[^"\']+\.html)["\']', re.I)
CARD_LINK_RE = re.compile(
    r'<article\b[^>]*class=["\'][^"\']*article-card[^"\']*["\'][^>]*>.*?'
    r'href=["\'](/clanky/[^"\']+\.html)["\'].*?</article>',
    re.I | re.S,
)


def load_engine():
    spec = importlib.util.spec_from_file_location("nk_article_visibility", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nelze načíst kanonický generátor článků.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ensure_article_sitemap_entries(articles: list[dict]) -> None:
    """Doplní do sitemap všechny indexovatelné články, které v ní chybějí.

    Základní generátor spravuje stránkování archivu. Tato pojistka navíc
    zajišťuje, že úplně nová URL článku bude v sitemapě ještě před finální
    kontrolou. Existující záznamy nemění a nevytváří duplicity.
    """
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if "</urlset>" not in text:
        raise RuntimeError("Sitemap nemá uzavírací značku urlset.")

    additions: list[str] = []
    for item in articles:
        absolute = f"https://nasekadan.cz{item['href']}"
        if absolute in text:
            continue
        published = item["dt"]
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        lastmod = published.date().isoformat()
        additions.append(
            "  <url><loc>"
            + escape(absolute)
            + "</loc><lastmod>"
            + lastmod
            + "</lastmod></url>\n"
        )

    if additions:
        text = text.replace("</urlset>", "".join(additions) + "</urlset>", 1)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    engine = load_engine()
    original_article_info = engine.article_info
    cutoff = datetime.now(timezone.utc) + timedelta(minutes=2)

    def safe_article_info(path: Path):
        item = original_article_info(path)
        if item is None:
            return None
        published = item["dt"]
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        if published.astimezone(timezone.utc) > cutoff:
            return None
        return item

    # Jediné pořadí: article:published_time sestupně.
    engine.article_info = safe_article_info
    engine.main()

    articles = []
    for path in sorted((ROOT / "clanky").glob("*.html")):
        if path.name == "index.html" or re.fullmatch(r"strana-\d+\.html", path.name):
            continue
        item = safe_article_info(path)
        if item:
            articles.append(item)
    articles.sort(key=lambda item: item["dt"], reverse=True)
    if not articles:
        raise RuntimeError("Po obnově nebyl nalezen žádný publikovaný článek.")

    all_hrefs = [item["href"] for item in articles]
    if len(all_hrefs) != len(set(all_hrefs)):
        raise RuntimeError("Publikované články obsahují duplicitní URL.")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    latest = all_hrefs[0]
    expected_hero = latest
    hero = re.search(
        r'<section\b[^>]*class=["\'][^"\']*\bhero\b[^"\']*["\'][^>]*\bid=["\']clanky["\'][^>]*>.*?</section>',
        home,
        re.I | re.S,
    )
    if not hero or f'data-latest-article-href="{expected_hero}"' not in hero.group(0):
        raise RuntimeError(f"Titulka nemá očekávaný hlavní článek: {expected_hero}")

    expected_home = all_hrefs[: min(engine.HOME_TOTAL, len(all_hrefs))]
    home_article_area = home.split('<section class="wrap section home-articles">', 1)[-1].split(
        '<section class="wrap promo-wrap"', 1
    )[0]
    for href in expected_home:
        if href not in hero.group(0) and href not in home_article_area:
            raise RuntimeError(f"Jeden z nejnovějších článků zmizel z titulky: {href}")

    archive_hrefs: list[str] = []
    pages = [ROOT / "clanky" / "index.html"] + sorted(
        (ROOT / "clanky").glob("strana-*.html"),
        key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
    )
    for page in pages:
        archive_hrefs.extend(CARD_LINK_RE.findall(page.read_text(encoding="utf-8")))
    if archive_hrefs != all_hrefs:
        missing = [href for href in all_hrefs if href not in archive_hrefs]
        extra = [href for href in archive_hrefs if href not in all_hrefs]
        raise RuntimeError(f"Archiv není úplný nebo seřazený. Chybí={missing}, navíc={extra}")

    ensure_article_sitemap_entries(articles)
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for href in all_hrefs:
        if f"https://nasekadan.cz{href}" not in sitemap:
            raise RuntimeError(f"Článek chybí v sitemapě: {href}")

    print(
        f"Viditelnost obnovena: {len(all_hrefs)} článků, "
        f"nejnovější {latest}, titulka {len(expected_home)}, archiv {len(pages)} stran."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
