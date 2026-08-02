#!/usr/bin/env python3
"""Statická kontrola právních a CMP podmínek před zapnutím Seznam Partner reklamy."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(text: str, needle: str, label: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{label}: chybí {needle!r}")


def main() -> int:
    errors: list[str] = []

    operator = read("provozovatel/index.html")
    for needle in (
        "Petr Kotáb",
        "08780200",
        "Chomutovská 1284",
        "432 01 Kadaň",
        "živnostenském rejstříku",
        "info@nasekadan.cz",
    ):
        require(operator, needle, "provozovatel/index.html", errors)

    about = read("o-webu/index.html")
    privacy = read("ochrana-osobnich-udaju/index.html")
    cookies = read("cookies/index.html")
    analytics = read("analytics.js")
    controls = read("privacy-controls.js")
    footer_source = read("scripts/normalize_footers.py")
    sitemap = read("sitemap.xml")

    for text, label in ((about, "o-webu"), (privacy, "ochrana osobních údajů"), (cookies, "cookies")):
        require(text, "IAB TCF 2.2", label, errors)
        require(text, "/provozovatel/", label, errors)

    require(analytics, "/privacy-controls.js", "analytics.js", errors)
    require(controls, "/cmp-config.json", "privacy-controls.js", errors)
    require(controls, "displayConsentUi", "privacy-controls.js", errors)

    for needle in (
        '<a href="/cookies/">Cookies</a>',
        '<a href="/provozovatel/">Provozovatel</a>',
        "data-open-privacy-settings",
    ):
        require(footer_source, needle, "normalize_footers.py", errors)

    for url in (
        "https://nasekadan.cz/cookies/",
        "https://nasekadan.cz/provozovatel/",
        "https://nasekadan.cz/ochrana-osobnich-udaju/",
    ):
        require(sitemap, url, "sitemap.xml", errors)

    config = json.loads(read("cmp-config.json"))
    enabled = bool(config.get("enabled"))
    script_url = str(config.get("scriptUrl") or "").strip()
    if enabled and not script_url.startswith("https://"):
        errors.append("cmp-config.json: aktivní CMP musí mít HTTPS scriptUrl")
    if not enabled and script_url:
        errors.append("cmp-config.json: vypnutá CMP nesmí obsahovat aktivní scriptUrl")

    # Reklamní kód Seznam Partner se nesmí nasadit dřív než certifikovaná CMP.
    possible_ad_files = [
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and ".github" not in path.parts
    ]
    possible_ad_files += [ROOT / "site.js", ROOT / "analytics.js"]
    seznam_ad_markers = ("ssp.seznam.cz", "c.imedia.cz", "seznam partner ad", "zoneId")
    active_markers: list[str] = []
    for path in possible_ad_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if any(marker.lower() in text for marker in seznam_ad_markers):
            active_markers.append(str(path.relative_to(ROOT)))
    if active_markers and not enabled:
        errors.append(
            "Seznam reklamní kód nalezen bez aktivní CMP: " + ", ".join(sorted(active_markers))
        )

    if errors:
        print("Kontrola Seznam Partner připravenosti selhala:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Právní údaje, odkazy a bezpečný před-CMP stav jsou v pořádku.")
    if enabled:
        print("CMP je konfigurovaná; před reklamou ještě ověřte vendor ID a živý TCF řetězec.")
    else:
        print("CMP je záměrně vypnutá a Seznam reklama se nesmí načítat. Pro plné schválení vložte kód certifikované TCF 2.2 CMP.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
