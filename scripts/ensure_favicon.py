#!/usr/bin/env python3
"""Sjednotí favicon tagy ve všech veřejných HTML stránkách Naše Kadaň."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FAVICON_VERSION = "20260801-2"
FAVICON_HREF = f"/favicon.svg?v={FAVICON_VERSION}"
PRIMARY_TAG = (
    f'<link data-nasekadan-favicon="primary" rel="icon" '
    f'href="{FAVICON_HREF}" type="image/svg+xml" sizes="any">'
)
SHORTCUT_TAG = (
    f'<link data-nasekadan-favicon="shortcut" rel="shortcut icon" '
    f'href="{FAVICON_HREF}" type="image/svg+xml">'
)
THEME_TAG = '<meta name="theme-color" content="#9f2626">'

EXCLUDE_DIRS = {
    ".git",
    ".github",
    "deploy",
    "docker-entrypoint.d",
    "lms-rescue",
    "nahled",
    "newsletter",
    "nginx",
    "parts",
    "scripts",
    "sdilet",
    "tools",
}

LINK_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
THEME_RE = re.compile(
    r"<meta\b(?=[^>]*\bname=[\"']theme-color[\"'])[^>]*>\s*",
    re.IGNORECASE,
)


def is_public_html(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDE_DIRS for part in relative.parts):
        return False
    if path.name.lower().startswith("google"):
        return False
    return True


def is_icon_link(tag: str) -> bool:
    rel = re.search(r"\brel=[\"']([^\"']+)[\"']", tag, re.IGNORECASE)
    return bool(rel and "icon" in rel.group(1).lower().split())


def normalize_favicon_html(text: str) -> str:
    if "</head>" not in text.lower():
        return text

    text = LINK_RE.sub(lambda match: "" if is_icon_link(match.group(0)) else match.group(0), text)
    text = THEME_RE.sub("", text)
    tags = f"  {PRIMARY_TAG}\n  {SHORTCUT_TAG}\n  {THEME_TAG}\n"
    return re.sub(r"</head>", tags + "</head>", text, count=1, flags=re.IGNORECASE)


def normalize_all() -> tuple[int, int]:
    changed = 0
    checked = 0
    for path in sorted(ROOT.rglob("*.html")):
        if not is_public_html(path):
            continue
        checked += 1
        original = path.read_text(encoding="utf-8", errors="replace")
        updated = normalize_favicon_html(original)
        if updated == original:
            continue
        path.write_text(updated, encoding="utf-8", newline="\n")
        changed += 1
    return changed, checked


def main() -> int:
    changed, checked = normalize_all()
    print(f"Favicon sjednocena na {changed} z {checked} veřejných HTML stránek.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
