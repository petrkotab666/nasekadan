#!/usr/bin/env python3
"""Sjednotí hlavní hlavičku a menu na všech veřejných HTML stránkách."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "deploy",
    "docker-entrypoint.d",
    "lms-rescue",
    "nahled",
    "newsletter",
    "nginx",
    "scripts",
    "sdilet",
    "tools",
}

HEADER = """<header data-site-header="v1">
  <div class="wrap head">
    <a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
    <nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav>
  </div>
</header>"""

HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.IGNORECASE | re.DOTALL)
BODY_RE = re.compile(r"(<body\b[^>]*>)", re.IGNORECASE)


def is_public_html(path: Path) -> bool:
    return not any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts)


def normalize_header_html(text: str) -> str:
    for match in HEADER_RE.finditer(text):
        block = match.group(0)
        if "logo-mark" not in block and "class=\"logo\"" not in block and "class='logo'" not in block:
            continue
        return text[: match.start()] + HEADER + text[match.end() :]

    if "<header" not in text.lower():
        return BODY_RE.sub(r"\1\n" + HEADER, text, count=1)
    return text


def ensure_site_script(text: str) -> str:
    if "/site.js" in text:
        return text
    return text.replace("</body>", '<script src="/site.js" defer></script></body>', 1)


def normalize_all_headers() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if not is_public_html(path):
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        updated = ensure_site_script(normalize_header_html(original))
        if updated == original:
            continue
        path.write_text(updated, encoding="utf-8", newline="\n")
        changed += 1
    return changed


def main() -> int:
    changed = normalize_all_headers()
    print(f"Sjednoceno menu na {changed} veřejných HTML stránkách.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
