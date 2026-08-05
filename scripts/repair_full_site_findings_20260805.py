#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_CULTURAL_IMAGE = "kam-v-kadani-a-okoli-3-9-srpna-2026-199cb73db2.png"
NEW_CULTURAL_IMAGE = "kam-v-kadani-a-okoli-3-9-srpna-2026-bff154b86a.png"


def write_if_changed(path: Path, text: str, original: str) -> bool:
    if text == original:
        return False
    path.write_text(text, encoding="utf-8", newline="\n")
    print("Opraveno:", path.relative_to(ROOT))
    return True


def replace(path: str | Path, old: str, new: str) -> bool:
    target = ROOT / path
    if not target.is_file():
        return False
    original = target.read_text(encoding="utf-8", errors="replace")
    return write_if_changed(target, original.replace(old, new), original)


def replace_cultural_image_everywhere() -> None:
    candidates: set[Path] = {
        ROOT / "index.html",
        ROOT / "rss.xml",
        ROOT / "sitemap.xml",
        ROOT / "news-sitemap.xml",
        ROOT / "llms.txt",
        ROOT / ".github" / "workflows" / "sync-all-public-images-20260805.yml",
    }
    for folder, patterns in (
        (ROOT / "clanky", ("*.html",)),
        (ROOT / "data", ("*.json", "*.xml", "*.txt")),
    ):
        if not folder.is_dir():
            continue
        for pattern in patterns:
            candidates.update(folder.rglob(pattern))
    for path in sorted(candidates):
        if not path.is_file() or path.resolve() == Path(__file__).resolve():
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        write_if_changed(path, original.replace(OLD_CULTURAL_IMAGE, NEW_CULTURAL_IMAGE), original)


def jsonld_blocks(text: str) -> list[re.Match[str]]:
    return list(
        re.finditer(
            r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>.*?</script>\s*",
            text,
            re.I | re.S,
        )
    )


def keep_single_schema(path: str, schema_pattern: str, preferred_attribute: str | None = None) -> None:
    target = ROOT / path
    original = target.read_text(encoding="utf-8", errors="replace")
    matches = [m for m in jsonld_blocks(original) if re.search(schema_pattern, m.group(0), re.I | re.S)]
    if len(matches) <= 1:
        return
    keep = matches[0]
    if preferred_attribute:
        keep = next((m for m in matches if preferred_attribute in m.group(0)), keep)
    text = original
    for match in reversed(matches):
        if match.start() == keep.start() and match.end() == keep.end():
            continue
        text = text[: match.start()] + text[match.end() :]
    write_if_changed(target, text, original)


def ensure_breadcrumb(path: str) -> None:
    target = ROOT / path
    original = target.read_text(encoding="utf-8", errors="replace")
    if re.search(r'"@type"\s*:\s*"BreadcrumbList"', original):
        return
    title = re.search(r"<h1[^>]*>(.*?)</h1>", original, re.I | re.S)
    name = re.sub(r"<[^>]+>", " ", title.group(1)).strip() if title else "Článek"
    canonical = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', original, re.I)
    url = canonical.group(1) if canonical else "https://nasekadan.cz/"
    payload = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Naše Kadaň", "item": "https://nasekadan.cz/"},
            {"@type": "ListItem", "position": 2, "name": "Články", "item": "https://nasekadan.cz/clanky/"},
            {"@type": "ListItem", "position": 3, "name": name, "item": url},
        ],
    }
    block = '<script data-nasekadan-breadcrumbs="1" type="application/ld+json">' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>\n"
    text = original.replace("</head>", block + "</head>", 1)
    write_if_changed(target, text, original)


def assert_clean() -> None:
    checks = {
        ROOT / "clanky" / "parts" / "slovan-01.html": ["/assets/lavka-shell-20260724.jpg"],
        ROOT / "clanky" / "parts" / "slovan-04.html": ["/assets/slovan-vstup-20260724.jpg"],
        ROOT / "nahled" / "lavka-shell-pracovni-7c26.html": ["/assets/lavka-shell-20260724.jpg"],
        ROOT / "clanky" / "kam-v-kadani-a-okoli-3-9-srpna-2026.html": [OLD_CULTURAL_IMAGE],
        ROOT / "index.html": [OLD_CULTURAL_IMAGE],
    }
    for path, forbidden in checks.items():
        text = path.read_text(encoding="utf-8", errors="replace")
        for value in forbidden:
            if value in text:
                raise SystemExit(f"Oprava se nepropsala: {path.relative_to(ROOT)} stále obsahuje {value}")

    schema_expectations = {
        ROOT / "clanky" / "kadansti-plavacci-zapis-podzim-2026.html": (r'"@type"\s*:\s*"BreadcrumbList"', 1),
        ROOT / "clanky" / "nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026.html": (r'"@type"\s*:\s*"BreadcrumbList"', 1),
        ROOT / "clanky" / "strikacky-vchody-drogy-kadan.html": (r'"@type"\s*:\s*"(?:NewsArticle|Article)"', 1),
    }
    for path, (pattern, expected) in schema_expectations.items():
        count = sum(bool(re.search(pattern, m.group(0), re.I | re.S)) for m in jsonld_blocks(path.read_text(encoding="utf-8", errors="replace")))
        if count != expected:
            raise SystemExit(f"Neplatný počet schémat v {path.relative_to(ROOT)}: {count}, očekáváno {expected}")

    emperor = (ROOT / "clanky" / "cisarsky-den-kadan-historie-2026.html").read_text(encoding="utf-8", errors="replace")
    if 'data-site-header="v1"' not in emperor:
        raise SystemExit("Článek o Císařském dni stále nemá sjednocenou hlavičku.")


# Neexistující staré fotografie z neveřejných fragmentů a pracovního náhledu
# nahraď stabilní grafikou, kterou používá i veřejný článek.
for path in ("clanky/parts/slovan-01.html", "nahled/lavka-shell-pracovni-7c26.html"):
    replace(path, "/assets/lavka-shell-20260724.jpg", "/social/slovan-druhy-pokus-e2e4356bbb.png")
replace("clanky/parts/slovan-04.html", "/assets/slovan-vstup-20260724.jpg", "/social/slovan-druhy-pokus-e2e4356bbb.png")

# Sjednoť kulturní obrázek ve stránce, kartách, registru i kontrole obrázků.
replace_cultural_image_everywhere()

# Oprav strukturovaná data potvrzená auditem.
keep_single_schema(
    "clanky/kadansti-plavacci-zapis-podzim-2026.html",
    r'"@type"\s*:\s*"BreadcrumbList"',
    'data-nasekadan-breadcrumbs="1"',
)
ensure_breadcrumb("clanky/nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026.html")
keep_single_schema("clanky/strikacky-vchody-drogy-kadan.html", r'"@type"\s*:\s*"(?:NewsArticle|Article)"')

# Nejdříve sjednoť šablony, potom znovu sestav publikační povrch.
subprocess.run(["python3", "scripts/normalize_site_header.py"], cwd=ROOT, check=True)
subprocess.run(["python3", "scripts/enforce_all_article_visibility.py"], cwd=ROOT, check=True)
subprocess.run(["python3", "scripts/sort_articles_chronologically.py"], cwd=ROOT, check=True)

# Generátor mohl přepsat karty; proveď deterministickou poslední normalizaci.
replace_cultural_image_everywhere()
keep_single_schema(
    "clanky/kadansti-plavacci-zapis-podzim-2026.html",
    r'"@type"\s*:\s*"BreadcrumbList"',
    'data-nasekadan-breadcrumbs="1"',
)
ensure_breadcrumb("clanky/nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026.html")
keep_single_schema("clanky/strikacky-vchody-drogy-kadan.html", r'"@type"\s*:\s*"(?:NewsArticle|Article)"')
assert_clean()
print("Cílené opravy úplného auditu byly provedeny a ověřeny.")
