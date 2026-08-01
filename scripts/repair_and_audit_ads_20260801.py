#!/usr/bin/env python3
"""Opraví a zkontroluje reklamní integraci napříč veřejným webem Naše Kadaň.

- každý sjednocený článek dostane právě jeden sidebar slot a jednotný balík skriptů,
- odstraní se přímé/duplicitní načítání reklamy-sidebar.js,
- veřejné nečlánkové stránky s data-promos dostanou potřebný reklamní balík,
- ověří se existence lokálních reklamních assetů,
- vznikne strojově čitelný report pro produkční kontrolu.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from normalize_articles import is_article, normalize_article, validate as validate_article_template

ROOT = Path(__file__).resolve().parents[1]
REPORT_DEFAULT = ROOT / ".github" / "ad-audit-status.json"
EXCLUDED_PARTS = {".git", ".github", "nahled", "research", "node_modules", "parts"}
ASSET_VERSION = "20260730-pojistime-rotation-4"

ARTICLE_REQUIRED = (
    "/site.js",
    "/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3",
    "/ad-spacing-guard.js",
    "/reklamy-oprava-obrazku.js",
    "/obsah-doplnky.js",
)
GENERAL_REQUIRED = (
    "/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3",
    "/ad-spacing-guard.js",
    "/reklamy-oprava-obrazku.js",
    "/obsah-doplnky.js",
)
GENERAL_SCRIPT_BLOCK = (
    '<script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script>\n'
    f'<script src="/ad-spacing-guard.js?v={ASSET_VERSION}" defer></script>\n'
    f'<script src="/reklamy-oprava-obrazku.js?v={ASSET_VERSION}"></script>\n'
    f'<script src="/obsah-doplnky.js?v={ASSET_VERSION}"></script>'
)

DIRECT_SIDEBAR_SCRIPT_RE = re.compile(
    r"\s*<script\b[^>]*\bsrc=[\"'][^\"']*/reklamy-sidebar\.js(?:\?[^\"']*)?[\"'][^>]*>\s*</script>",
    re.I,
)
GENERAL_AD_SCRIPT_RE = re.compile(
    r"\s*<script\b[^>]*\bsrc=[\"'][^\"']*/(?:reklamy\.js|ad-spacing-guard\.js|reklamy-oprava-obrazku\.js|reklamy-popisy\.js|obsah-doplnky\.js)(?:\?[^\"']*)?[\"'][^>]*>\s*</script>",
    re.I,
)
SIDEBAR_SLOT_RE = re.compile(
    r"\s*<div\b(?=[^>]*\bdata-promos\b)(?=[^>]*\bdata-context=[\"']sidebar[\"'])[^>]*>.*?</div>",
    re.I | re.S,
)
ASIDE_RE = re.compile(
    r"(<aside\b[^>]*class=[\"'][^\"']*\bsticky\b[^\"']*[\"'][^>]*>)(.*?)(</aside>)",
    re.I | re.S,
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def is_noindex(text: str) -> bool:
    values = re.findall(
        r'<meta\b[^>]*name=[\"\']robots[\"\'][^>]*content=[\"\']([^\"\']+)',
        text,
        re.I,
    )
    return any("noindex" in value.lower() for value in values)


def is_public_path(path: Path, text: str) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    return not is_noindex(text)


def public_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def normalize_sidebar_slot(text: str) -> str:
    match = ASIDE_RE.search(text)
    if not match:
        return text
    body = SIDEBAR_SLOT_RE.sub("", match.group(2)).rstrip()
    replacement = (
        f"{match.group(1)}{body}\n"
        '  <div data-promos data-context="sidebar"></div>\n'
        f"{match.group(3)}"
    )
    return text[: match.start()] + replacement + text[match.end() :]


def normalize_article_ads(text: str) -> str:
    text = normalize_article(text)
    text = DIRECT_SIDEBAR_SCRIPT_RE.sub("", text)
    text = normalize_sidebar_slot(text)
    return text


def normalize_general_ad_page(text: str) -> str:
    if "data-promos" not in text or is_article(text):
        return text
    text = DIRECT_SIDEBAR_SCRIPT_RE.sub("", text)
    text = GENERAL_AD_SCRIPT_RE.sub("", text)
    body = list(re.finditer(r"</body>", text, re.I))
    if body:
        pos = body[-1].start()
        text = text[:pos].rstrip() + "\n" + GENERAL_SCRIPT_BLOCK + "\n" + text[pos:]
    return text


def count_ref(text: str, ref: str) -> int:
    if "?" in ref:
        return text.count(ref)
    return len(re.findall(re.escape(ref) + r"(?:\?[^\"']*)?", text, re.I))


def validate_article_ads(path: Path, text: str) -> list[str]:
    errors = validate_article_template(path, text)
    slot_count = len(SIDEBAR_SLOT_RE.findall(text))
    if slot_count != 1:
        errors.append(f"sidebar reklamní slot je přítomen {slot_count}× místo 1×")
    if DIRECT_SIDEBAR_SCRIPT_RE.search(text):
        errors.append("reklamy-sidebar.js je načten přímo; má jej zavádět site.js")
    for ref in ARTICLE_REQUIRED:
        if count_ref(text, ref) != 1:
            errors.append(f"{ref} není načten právě jednou")
    for marker in (
        "static-article-ads",
        'class="static-article-ad"',
        "static-article-ads-style",
        'data-static-ads="locked-v1"',
    ):
        if marker in text:
            errors.append(f"zůstal zakázaný pevný reklamní systém: {marker}")
    return errors


def validate_general_ad_page(text: str) -> list[str]:
    errors: list[str] = []
    if "data-promos" not in text or is_article(text):
        return errors
    for ref in GENERAL_REQUIRED:
        if count_ref(text, ref) != 1:
            errors.append(f"{ref} není načten právě jednou")
    return errors


def local_ad_assets() -> tuple[list[str], list[str]]:
    checked: list[str] = []
    missing: list[str] = []
    required_files = (
        "reklamy.js",
        "reklamy-sidebar.js",
        "reklamy-sidebar.css",
        "reklamy-oprava-obrazku.js",
        "obsah-doplnky.js",
        "ad-spacing-guard.js",
        "site.js",
    )
    for item in required_files:
        checked.append(item)
        if not (ROOT / item).is_file():
            missing.append(item)

    reklamy = read(ROOT / "reklamy.js") if (ROOT / "reklamy.js").is_file() else ""
    refs = sorted(set(re.findall(r"[\"'](/assets/reklamy/[^\"']+)[\"']", reklamy)))
    for ref in refs:
        rel = ref.split("?", 1)[0].lstrip("/")
        checked.append(rel)
        if not (ROOT / rel).is_file():
            missing.append(rel)
    return checked, missing


def html_paths() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*.html"):
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        result.append(path)
    return sorted(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", default=str(REPORT_DEFAULT))
    args = parser.parse_args()

    changed: list[str] = []
    articles: list[str] = []
    ad_pages: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []
    public_count = 0

    for path in html_paths():
        original = read(path)
        public = is_public_path(path, original)
        if public:
            public_count += 1
        current = original

        if is_article(original):
            current = normalize_article_ads(original) if args.write else original
            if args.write and current != original:
                write(path, current)
                changed.append(path.relative_to(ROOT).as_posix())
            if public:
                url = public_url(path)
                articles.append(url)
                for error in validate_article_ads(path, current):
                    errors.append(f"{path.relative_to(ROOT)}: {error}")
        elif "data-promos" in original:
            current = normalize_general_ad_page(original) if args.write else original
            if args.write and current != original:
                write(path, current)
                changed.append(path.relative_to(ROOT).as_posix())
            if public:
                url = public_url(path)
                ad_pages.append(url)
                for error in validate_general_ad_page(current):
                    errors.append(f"{path.relative_to(ROOT)}: {error}")

    assets_checked, assets_missing = local_ad_assets()
    for item in assets_missing:
        errors.append(f"chybí lokální reklamní asset: {item}")

    petition = "/clanky/petice-nemocnice-kadan-podpisova-mista-2026.html"
    if petition not in articles:
        errors.append("poslední článek o podpisových místech petice nebyl nalezen mezi veřejnými články")

    report = {
        "ok": not errors,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "public_html_pages": public_count,
        "article_pages": len(articles),
        "ad_enabled_non_article_pages": len(ad_pages),
        "changed_files": changed,
        "articles": sorted(set(articles)),
        "ad_pages": sorted(set(ad_pages)),
        "local_ad_assets_checked": len(assets_checked),
        "missing_assets": assets_missing,
        "errors": errors,
        "warnings": warnings,
        "petition_article": petition,
    }
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"Audit reklam: {public_count} veřejných HTML, {len(articles)} článků, "
        f"{len(ad_pages)} dalších reklamních stránek, změněno {len(changed)} souborů."
    )
    if changed:
        print("Změněné soubory:")
        for item in changed:
            print(f"- {item}")
    if errors:
        print("CHYBY:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
