#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "20260801-poll-system-v3"
NEW = "20260801-poll-system-v4"
MARKER = "POLL_GREENERY_HIGH_CONTRAST_V4"

SITE = ROOT / "site.js"
INSTALLER = ROOT / "scripts" / "install_poll_system_v2.py"
PREP = ROOT / "scripts" / "prepare_greenery_publication_20260801.py"
STALE_FIX = ROOT / "scripts" / "fix_poll_stale_browser_state.py"
REPAIR = ROOT / "scripts" / "repair_greenery_publication_now.sh"
ARTICLES = [
    ROOT / "clanky" / "sekani-travniku-kadan-spravci-vysky-2026.html",
    ROOT / "clanky" / "jaderne-tusimice-smr-voda-doprava-eia-2026.html",
    ROOT / ".github" / "drafts" / "jaderne-tusimice-smr-voda-doprava-eia-2026.html",
]

CONTRAST_CSS = r'''      /* POLL_GREENERY_HIGH_CONTRAST_V4: tmavá anketa potřebuje světlý text. */
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results{background:rgba(3,18,27,.30);border:1px solid rgba(255,255,255,.30);border-radius:16px;padding:18px 18px 14px}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-head,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-head strong,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-label{color:#ffffff!important;text-shadow:0 1px 2px rgba(0,0,0,.35)}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-total,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-value,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-status{color:#eef8fb!important;font-weight:800}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-track{background:#f5f8f9;box-shadow:0 0 0 1px rgba(255,255,255,.65)}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-fill{background:#d92f38}
'''


def add_contrast(text: str) -> str:
    if MARKER in text:
        return text
    needle = "      .poll-results-error{color:#8e2525!important}\n"
    if needle not in text:
        raise RuntimeError("Nebyl nalezen konec společných stylů ankety.")
    return text.replace(needle, needle + CONTRAST_CSS, 1)


def patch_file(path: Path, *, contrast: bool = False) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if contrast:
        text = add_contrast(text)
    text = text.replace(OLD, NEW)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    patch_file(SITE, contrast=True)
    patch_file(INSTALLER, contrast=True)
    patch_file(PREP)
    patch_file(STALE_FIX)
    patch_file(REPAIR)
    for path in ARTICLES:
        patch_file(path)

    site = SITE.read_text(encoding="utf-8")
    article = ARTICLES[0].read_text(encoding="utf-8")
    required = [
        MARKER,
        '[data-poll-id="sekani-travniku-kadan-2026"] .poll-result-label',
        'color:#ffffff!important',
        'color:#eef8fb!important',
        f'/site.js?v={NEW}',
    ]
    combined = site + "\n" + article
    missing = [item for item in required if item not in combined]
    if missing:
        raise RuntimeError("Po opravě chybí: " + ", ".join(missing))
    if f'/site.js?v={OLD}' in article:
        raise RuntimeError("Článek stále používá starou cache verzi skriptu.")
    print("Kontrast výsledků ankety je opraven a cache verze zvýšena na v4.")


if __name__ == "__main__":
    main()
