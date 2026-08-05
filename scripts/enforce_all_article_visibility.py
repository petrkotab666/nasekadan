#!/usr/bin/env python3
"""Kanonická pojistka viditelnosti všech publikovaných článků.

Jediným zdrojem pravdy jsou indexovatelné HTML články v ``clanky/``. Skript
z nich znovu sestaví titulku, celý stránkovaný archiv a sitemapu. Ignoruje
budoucí naplánované články a ruší jednorázová historická připnutí titulky,
aby pozdější workflow nemohlo přepsat novější článek starším obsahem.

Součástí pojistky je také jediná kanonická struktura ItemList na každé
archivní stránce a deduplikace sitemap.xml. Tím se po dalších publikacích
nemohou vrátit staré neoznačené archivní JSON-LD bloky ani duplicitní URL.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
import importlib.util
import json
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
SCRIPT_RE = re.compile(r'<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script>', re.I | re.S)
URL_BLOCK_RE = re.compile(r'<url\b[^>]*>.*?</url>', re.I | re.S)
LOC_RE = re.compile(r'<loc>\s*([^<]+?)\s*</loc>', re.I | re.S)


def load_engine():
    spec = importlib.util.spec_from_file_location("nk_article_visibility", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nelze načíst kanonický generátor článků.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive_pages() -> list[Path]:
    return [ROOT / "clanky" / "index.html"] + sorted(
        (ROOT / "clanky").glob("strana-*.html"),
        key=lambda path: int(re.search(r"(\d+)", path.stem).group(1)),
    )


def jsonld_types(value) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        item_type = value.get("@type")
        if isinstance(item_type, str):
            found.add(item_type)
        elif isinstance(item_type, list):
            found.update(item for item in item_type if isinstance(item, str))
        for nested in value.values():
            found.update(jsonld_types(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(jsonld_types(nested))
    return found


def remove_legacy_archive_schemas() -> None:
    """Odstraní staré neoznačené CollectionPage+ItemList bloky archivu.

    Generátor následně ponechá právě jeden aktuální blok označený atributem
    ``data-nk-archive-schema=1``. Organizační a WebSite JSON-LD se nemění.
    """
    for path in archive_pages():
        text = path.read_text(encoding="utf-8")

        def replace_script(match: re.Match[str]) -> str:
            attrs = match.group("attrs")
            attrs_lower = attrs.lower()
            if "application/ld+json" not in attrs_lower:
                return match.group(0)
            if "data-nk-archive-schema" in attrs_lower:
                return match.group(0)
            try:
                payload = json.loads(match.group("body"))
            except json.JSONDecodeError:
                return match.group(0)
            types = jsonld_types(payload)
            if "CollectionPage" in types and "ItemList" in types:
                return ""
            return match.group(0)

        text = SCRIPT_RE.sub(replace_script, text)
        canonical_count = len(
            re.findall(r'<script\b[^>]*data-nk-archive-schema=["\']1["\'][^>]*>', text, re.I)
        )
        if canonical_count != 1:
            raise RuntimeError(
                f"Archivní stránka {path.name} nemá právě jeden kanonický ItemList: {canonical_count}"
            )
        path.write_text(text, encoding="utf-8", newline="\n")


def sitemap_block_score(block: str) -> tuple[int, int]:
    metadata_tags = re.findall(
        r'<(?:lastmod|changefreq|priority|image:[a-z0-9_-]+|news:[a-z0-9_-]+)\b',
        block,
        re.I,
    )
    return (len(metadata_tags), len(block))


def deduplicate_sitemap() -> list[str]:
    """Ponechá každou URL právě jednou a upřednostní úplnější záznam.

    Sitemapu skládá z čistého prefixu, jediné normalizované sady URL a
    původního suffixu. Opakované spuštění je proto idempotentní a nemůže
    hromadit prázdné řádky po odstraněných blocích ``<url>``.
    """
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if "</urlset>" not in text:
        raise RuntimeError("Sitemap nemá uzavírací značku urlset.")

    order: list[str] = []
    selected: dict[str, str] = {}
    duplicates: list[str] = []
    matches = list(URL_BLOCK_RE.finditer(text))
    for match in matches:
        block = match.group(0).strip()
        loc_match = LOC_RE.search(block)
        if not loc_match:
            raise RuntimeError("Záznam sitemap neobsahuje loc.")
        loc = loc_match.group(1).strip()
        if loc not in selected:
            order.append(loc)
            selected[loc] = block
            continue
        duplicates.append(loc)
        if sitemap_block_score(block) > sitemap_block_score(selected[loc]):
            selected[loc] = block

    rendered = "\n".join("  " + selected[loc] for loc in order) + "\n"
    if matches:
        prefix = text[: matches[0].start()].rstrip()
        suffix = text[matches[-1].end() :].lstrip()
        text = prefix + "\n" + rendered + suffix
    else:
        text = text.replace("</urlset>", rendered + "</urlset>", 1)
    path.write_text(text, encoding="utf-8", newline="\n")

    final_locs = [match.group(1).strip() for match in LOC_RE.finditer(text)]
    if len(final_locs) != len(set(final_locs)):
        raise RuntimeError("Sitemap obsahuje duplicity i po opravě.")
    return sorted(set(duplicates))


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
    existing_locs = {match.group(1).strip() for match in LOC_RE.finditer(text)}
    for item in articles:
        absolute = f"https://nasekadan.cz{item['href']}"
        if absolute in existing_locs:
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
        existing_locs.add(absolute)

    if additions:
        text = text.replace("</urlset>", "".join(additions) + "</urlset>", 1)
        path.write_text(text, encoding="utf-8", newline="\n")


def validate_archive_schema() -> None:
    for path in archive_pages():
        text = path.read_text(encoding="utf-8")
        canonical_count = len(
            re.findall(r'<script\b[^>]*data-nk-archive-schema=["\']1["\'][^>]*>', text, re.I)
        )
        if canonical_count != 1:
            raise RuntimeError(f"Archivní stránka {path.name} má {canonical_count} kanonických ItemListů.")
        legacy_count = 0
        for match in SCRIPT_RE.finditer(text):
            attrs_lower = match.group("attrs").lower()
            if "application/ld+json" not in attrs_lower or "data-nk-archive-schema" in attrs_lower:
                continue
            try:
                payload = json.loads(match.group("body"))
            except json.JSONDecodeError:
                continue
            types = jsonld_types(payload)
            if "CollectionPage" in types and "ItemList" in types:
                legacy_count += 1
        if legacy_count:
            raise RuntimeError(f"Archivní stránka {path.name} stále obsahuje starý ItemList.")


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
    remove_legacy_archive_schemas()

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
    pages = archive_pages()
    for page in pages:
        archive_hrefs.extend(CARD_LINK_RE.findall(page.read_text(encoding="utf-8")))
    if archive_hrefs != all_hrefs:
        missing = [href for href in all_hrefs if href not in archive_hrefs]
        extra = [href for href in archive_hrefs if href not in all_hrefs]
        raise RuntimeError(f"Archiv není úplný nebo seřazený. Chybí={missing}, navíc={extra}")

    validate_archive_schema()
    ensure_article_sitemap_entries(articles)
    removed_duplicates = deduplicate_sitemap()
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_locs = [match.group(1).strip() for match in LOC_RE.finditer(sitemap)]
    if len(sitemap_locs) != len(set(sitemap_locs)):
        raise RuntimeError("Sitemap obsahuje duplicitní loc.")
    for href in all_hrefs:
        if f"https://nasekadan.cz{href}" not in sitemap_locs:
            raise RuntimeError(f"Článek chybí v sitemapě: {href}")

    print(
        f"Viditelnost obnovena: {len(all_hrefs)} článků, "
        f"nejnovější {latest}, titulka {len(expected_home)}, archiv {len(pages)} stran, "
        f"odstraněné duplicity sitemap {len(removed_duplicates)}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
