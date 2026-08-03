#!/usr/bin/env python3
"""Build the public sitemap from allowed HTML and purge non-public web output.

This is the final sitemap authority used after all publication scripts. It does
not trust previously appended sitemap entries: it scans the resulting public
HTML, excludes technical/private paths, deduplicates canonical URLs and then
validates the finished XML.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
SITEMAP = ROOT / "sitemap.xml"

# Any directory with one of these names is implementation detail, a draft,
# diagnostics or private research and must not become an indexable page.
PUBLIC_SKIP_DIRS = {
    ".git",
    ".github",
    ".image-parts",
    "deploy",
    "docker-entrypoint.d",
    "lms-rescue",
    "nahled",
    "newsletter",
    "nginx",
    "parts",
    "research",
    "scripts",
    "sdilet",
    "tools",
}

GOOGLE_FILE_RE = re.compile(r"^google[a-z0-9_-]+\.html$", re.IGNORECASE)
NOINDEX_RE = re.compile(
    r'<meta\b(?=[^>]*\bname=["\']robots["\'])(?=[^>]*\bcontent=["\'][^"\']*\bnoindex\b)',
    re.IGNORECASE,
)
FORBIDDEN_URL_RE = re.compile(
    r"^https://nasekadan\.cz/(?:"
    r"clanky/parts/|research/|nahled/|api/|data/|statistiky/|"
    r"google[a-z0-9_-]+\.html(?:$|[?#])"
    r")",
    re.IGNORECASE,
)


def relative(path: Path) -> Path:
    return path.relative_to(ROOT)


def canonical_for(path: Path) -> str:
    rel = relative(path).as_posix()
    if rel == "index.html":
        return f"{BASE}/"
    if rel.endswith("/index.html"):
        return f"{BASE}/{rel[:-10]}"
    return f"{BASE}/{rel}"


def is_public_html(path: Path) -> bool:
    rel = relative(path)
    if any(part in PUBLIC_SKIP_DIRS for part in rel.parts):
        return False
    if path.name == "404.html" or GOOGLE_FILE_RE.fullmatch(path.name):
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return not bool(NOINDEX_RE.search(text))


def purge_nonpublic_output() -> list[str]:
    """Remove files that must never be copied into the production document root."""
    removed: list[str] = []
    for path in (ROOT / "research", ROOT / "clanky" / "parts"):
        if path.exists():
            removed.append(relative(path).as_posix() + "/")
            shutil.rmtree(path)

    for path in ROOT.glob("google*.html"):
        if path.is_file() and GOOGLE_FILE_RE.fullmatch(path.name):
            removed.append(relative(path).as_posix())
            path.unlink()
    return removed


def build_urls() -> list[str]:
    urls = {
        canonical_for(path)
        for path in ROOT.rglob("*.html")
        if is_public_html(path)
    }
    return sorted(urls)


def write_sitemap(urls: list[str]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    lines.extend(f"  <url><loc>{escape(url)}</loc></url>" for url in urls)
    lines.append("</urlset>")
    SITEMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_sitemap() -> tuple[int, list[str]]:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root = ET.parse(SITEMAP).getroot()
    locations: list[str] = []
    for node in root:
        loc = next((child for child in node if child.tag.endswith("loc")), None)
        value = (loc.text or "").strip() if loc is not None else ""
        if not value:
            raise SystemExit("Sitemap obsahuje prázdnou položku <loc>.")
        if not value.startswith(f"{BASE}/"):
            raise SystemExit(f"Cizí nebo neplatná adresa v sitemapě: {value}")
        if FORBIDDEN_URL_RE.search(value):
            raise SystemExit(f"Technická nebo neveřejná adresa v sitemapě: {value}")
        locations.append(value)

    duplicates = sorted({url for url in locations if locations.count(url) > 1})
    if duplicates:
        raise SystemExit("Duplicitní adresy v sitemapě: " + ", ".join(duplicates))

    weather_page = ROOT / "pocasi" / "index.html"
    if weather_page.exists() and f"{BASE}/pocasi/" not in locations:
        raise SystemExit("Veřejná stránka /pocasi/ chybí v sitemapě.")
    return len(locations), locations


def main() -> int:
    removed = purge_nonpublic_output()
    urls = build_urls()
    write_sitemap(urls)
    count, _ = validate_sitemap()

    if removed:
        print("Z veřejného výstupu odstraněno:")
        for item in removed:
            print(f"- {item}")
    print(
        f"Sitemap znovu sestavena: {count} jedinečných veřejných adres; "
        "technické cesty a duplicity: 0."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
