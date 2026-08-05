#!/usr/bin/env python3
"""Sjednotí statickou patičku všech veřejných HTML stránek Naše Kadaň."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".github", ".image-parts", "lms-rescue", "node_modules"}
FOOTER_STYLESHEET = '<link rel="stylesheet" href="/footer.css?v=20260805-event-hotfix-3">'

FOOTER = '''<footer class="site-footer" data-site-footer="v1">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="logo" href="/" aria-label="Naše Kadaň – úvodní stránka"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
      <p>Nezávislé informace, události a příběhy města.</p>
    </div>
    <div class="footer-column">
      <strong>Obsah webu</strong>
      <a href="/">Úvod</a>
      <a href="/clanky/">Naše články</a>
      <a href="/#akce">Akce</a>
      <a href="/pruvodce/">Průvodce</a>
      <a href="/prehled-zdroju/">Přehled zdrojů</a>
    </div>
    <div class="footer-column">
      <strong>Praktické a kontakt</strong>
      <a href="/prakticke/">Praktická Kadaň</a>
      <a href="/doprava/">Doprava</a>
      <a href="/organizace/">Organizace</a>
      <a href="/zapojte-se/">Zapojte se</a>
      <a href="/inzerce/"><b>Inzerce a ceník</b></a>
      <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>
    </div>
  </div>
  <div class="footer-legal">
    <span>© 2026 Naše Kadaň</span>
    <a href="/o-webu/">O webu</a>
    <a href="/inzerce/">Inzerce</a>
    <a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a>
    <a href="/cookies/">Cookies</a>
    <a href="/provozovatel/">Provozovatel</a>
    <a href="/cookies/#nastaveni" data-open-privacy-settings>Nastavení soukromí</a>
    <a href="mailto:info@nasekadan.cz">Kontakt</a>
  </div>
</footer>'''

FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.IGNORECASE | re.DOTALL)
FOOTER_CSS_RE = re.compile(
    r"\s*<link\b[^>]*href=[\"'][^\"']*footer\.css[^\"']*[\"'][^>]*>",
    re.IGNORECASE,
)
HTML_OPEN_RE = re.compile(r"<html\b", re.IGNORECASE)
HEAD_CLOSE_RE = re.compile(r"</head\s*>", re.IGNORECASE)
BODY_CLOSE_RE = re.compile(r"</body\s*>", re.IGNORECASE)


def public_html_files() -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        directory_parts = relative.parts[:-1]
        if any(part in EXCLUDED_PARTS or part.startswith(".") for part in directory_parts):
            continue
        paths.append(path)
    return sorted(paths)


def normalized_html(text: str) -> str:
    # Jediný samostatný stylesheet má přednost před historickými lokálními
    # pravidly jednotlivých stránek, takže patička vypadá všude stejně.
    result = FOOTER_CSS_RE.sub("", text)
    if not HEAD_CLOSE_RE.search(result):
        raise ValueError("HTML nemá </head>")
    result = HEAD_CLOSE_RE.sub(f"  {FOOTER_STYLESHEET}\n</head>", result, count=1)

    matches = list(FOOTER_RE.finditer(result))
    if matches:
        start = matches[0].start()
        end = matches[-1].end()
        result = result[:start].rstrip() + "\n\n" + FOOTER + result[end:]
    else:
        if not BODY_CLOSE_RE.search(result):
            raise ValueError("HTML nemá </body>")
        result = BODY_CLOSE_RE.sub(FOOTER + "\n</body>", result, count=1)

    # Odstraní případnou druhou patičku, kterou do stránky vložil starší generátor.
    first_end = result.find("</footer>")
    if first_end >= 0:
        prefix = result[: first_end + len("</footer>")]
        suffix = FOOTER_RE.sub("", result[first_end + len("</footer>") :])
        result = prefix + suffix

    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Patičky skutečně přepsat")
    parser.add_argument("--check", action="store_true", help="Po úpravě ověřit jednotnost")
    args = parser.parse_args()

    changed: list[Path] = []
    skipped: list[Path] = []
    errors: list[str] = []

    for path in public_html_files():
        text = path.read_text(encoding="utf-8")

        # V repozitáři jsou také HTML fragmenty používané skládacími skripty a
        # ověřovací soubor Googlu. Nejsou to samostatné webové stránky a patička
        # do nich nepatří.
        if not HTML_OPEN_RE.search(text):
            skipped.append(path)
            continue

        try:
            normalized = normalized_html(text)
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        if normalized != text:
            changed.append(path)
            if args.write:
                path.write_text(normalized, encoding="utf-8", newline="\n")

        checked = normalized if args.write else text
        footer_count = len(FOOTER_RE.findall(checked))
        css_count = len(FOOTER_CSS_RE.findall(checked))
        if args.check and (
            footer_count != 1
            or FOOTER not in checked
            or css_count != 1
            or FOOTER_STYLESHEET not in checked
        ):
            errors.append(
                f"{path.relative_to(ROOT)}: očekávána jedna jednotná patička a jeden footer.css; "
                f"patiček {footer_count}, stylů {css_count}"
            )

    if changed:
        print("Stránky s rozdílnou patičkou:")
        for path in changed:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Všechny kontrolované stránky mají jednotnou patičku.")

    if skipped:
        print("Přeskočené HTML fragmenty a ověřovací soubory:")
        for path in skipped:
            print(f"- {path.relative_to(ROOT)}")

    if errors:
        print("Chyby:")
        for error in errors:
            print(f"- {error}")
        return 1

    if changed and not args.write:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
