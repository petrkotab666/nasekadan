#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_VERSION = "20260801-poll-system-v2"
NEW_VERSION = "20260801-poll-system-v3"
MARKER = "POLL_SERVER_AUTHORITATIVE_V3"

SITE = ROOT / "site.js"
INSTALLER = ROOT / "scripts" / "install_poll_system_v2.py"
GREENERY_PREP = ROOT / "scripts" / "prepare_greenery_publication_20260801.py"
ARTICLES = [
    ROOT / "clanky" / "jaderne-tusimice-smr-voda-doprava-eia-2026.html",
    ROOT / ".github" / "drafts" / "jaderne-tusimice-smr-voda-doprava-eia-2026.html",
    ROOT / "clanky" / "sekani-travniku-kadan-spravci-vysky-2026.html",
]


def patch_poll_javascript(text: str) -> str:
    if MARKER in text:
        return text.replace(OLD_VERSION, NEW_VERSION)

    old_render = """      if (payload && payload.selected) {
        try { localStorage.setItem(storageKey, payload.selected); } catch (_) {}
        setLocked(payload.selected);
      }
"""
    new_render = """      // POLL_SERVER_AUTHORITATIVE_V3: cookie a databáze jsou jediný zdroj pravdy.
      if (payload && payload.selected) {
        try { localStorage.setItem(storageKey, payload.selected); } catch (_) {}
        setLocked(payload.selected);
        setMessage('Děkujeme, váš hlas už byl zaznamenán.');
      } else {
        // Starší nefunkční anketa mohla uložit pouze localStorage bez serverového hlasu.
        // Takový záznam nesmí blokovat nové hlasování.
        try { localStorage.removeItem(storageKey); } catch (_) {}
        setUnlocked();
        if (message && /Ověřujeme dřívější hlas|už byl zaznamenán/.test(message.textContent || '')) {
          message.classList.remove('show');
        }
      }
"""
    if old_render not in text:
        raise RuntimeError("V site.js/instalačním bloku nebyla nalezena obsluha serverového výběru.")
    text = text.replace(old_render, new_render, 1)

    old_initial = """    try {const saved=localStorage.getItem(storageKey);if(saved){setLocked(saved);setMessage('Děkujeme, váš hlas už byl zaznamenán.');}} catch (_) {}
    loadResults();
"""
    new_initial = """    // Lokální záznam je pouze nápověda; tlačítka uzamkne až potvrzení serveru.
    try {
      if (localStorage.getItem(storageKey)) setMessage('Ověřujeme dřívější hlas…');
    } catch (_) {}
    loadResults();
"""
    if old_initial not in text:
        raise RuntimeError("Nebyl nalezen blok, který předčasně věřil localStorage.")
    text = text.replace(old_initial, new_initial, 1)

    old_click = """        let saved='';try{saved=localStorage.getItem(storageKey)||'';}catch(_){}
        if(saved){setLocked(saved);setMessage('Děkujeme, váš hlas už byl zaznamenán.');await loadResults();return;}
        const vote=button.getAttribute('data-poll-vote');if(!vote)return;
"""
    new_click = """        // Hlas vždy posíláme serveru. Duplicitní hlas bezpečně odmítne databáze podle cookie.
        const vote=button.getAttribute('data-poll-vote');if(!vote)return;
"""
    if old_click not in text:
        raise RuntimeError("Nebyl nalezen blok, který odmítal kliknutí pouze podle localStorage.")
    text = text.replace(old_click, new_click, 1)
    return text.replace(OLD_VERSION, NEW_VERSION)


def patch_site() -> None:
    text = SITE.read_text(encoding="utf-8")
    SITE.write_text(patch_poll_javascript(text), encoding="utf-8", newline="\n")


def patch_installer() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    text = text.replace(f'VERSION = "{OLD_VERSION}"', f'VERSION = "{NEW_VERSION}"')
    text = patch_poll_javascript(text)
    INSTALLER.write_text(text, encoding="utf-8", newline="\n")


def patch_greenery_preparation() -> None:
    text = GREENERY_PREP.read_text(encoding="utf-8")
    text = text.replace(f'POLL_VERSION = "{OLD_VERSION}"', f'POLL_VERSION = "{NEW_VERSION}"')
    GREENERY_PREP.write_text(text, encoding="utf-8", newline="\n")


def patch_articles() -> None:
    for path in ARTICLES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(OLD_VERSION, NEW_VERSION)
        path.write_text(text, encoding="utf-8", newline="\n")


def validate() -> None:
    site = SITE.read_text(encoding="utf-8")
    required = [
        MARKER,
        "localStorage.removeItem(storageKey)",
        "Hlas vždy posíláme serveru",
        "/api/newsletter/poll/vote",
        "/api/newsletter/poll/results",
    ]
    missing = [item for item in required if item not in site]
    if missing:
        raise RuntimeError("V opraveném site.js chybí: " + ", ".join(missing))
    forbidden = "if(saved){setLocked(saved);setMessage('Děkujeme, váš hlas už byl zaznamenán.');await loadResults();return;}"
    if forbidden in site:
        raise RuntimeError("site.js stále odmítá hlas pouze podle localStorage.")
    for path in ARTICLES:
        if path.exists() and "data-poll-id=" in path.read_text(encoding="utf-8"):
            text = path.read_text(encoding="utf-8")
            if f"/site.js?v={NEW_VERSION}" not in text:
                raise RuntimeError(f"{path.relative_to(ROOT)} nemá novou verzi hlasovacího skriptu.")


def main() -> None:
    patch_site()
    patch_installer()
    patch_greenery_preparation()
    patch_articles()
    validate()
    print("Stará lokální volba už nemůže zablokovat serverové hlasování.")


if __name__ == "__main__":
    main()
