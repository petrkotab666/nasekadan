#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE_JS = ROOT / "site.js"
ARTICLE = ROOT / "clanky/alzbetinsky-klaster-kadan-pacienti-lecebna-1966.html"
DRAFT = ROOT / ".github/drafts/alzbetinsky-klaster-kadan-20260803.html"
VERSION = "20260803-alzbetinsky-contrast-v1"
MARKER = "POLL_ALZBETINSKY_HIGH_CONTRAST_V1"


def patch_site_js() -> None:
    text = SITE_JS.read_text(encoding="utf-8")

    if MARKER not in text:
        anchor = '      [data-poll-id=\\"sekani-travniku-kadan-2026\\"] .poll-result-fill{background:#d92f38}\n'
        if anchor not in text:
            raise SystemExit("V site.js chybí očekávaný blok kontrastu ankety.")
        block = '''      /* POLL_ALZBETINSKY_HIGH_CONTRAST_V1: světlý text a jasně označená zvolená odpověď. */
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-results{background:rgba(55,7,17,.34);border:1px solid rgba(255,255,255,.34);border-radius:16px;padding:18px 18px 14px}
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-results-head,
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-results-head strong,
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-result-label{color:#ffffff!important;text-shadow:0 1px 2px rgba(0,0,0,.38)}
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-results-total,
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-result-value,
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-results-status{color:#f9e9ed!important;font-weight:800}
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-results-error{color:#ffe1e1!important}
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-result-track{background:#fff7f8;box-shadow:0 0 0 1px rgba(255,255,255,.70)}
      [data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-result-fill{background:#e14650}
      [data-poll-id] .poll-option[aria-pressed=\\"true\\"]{background:#fff4f4!important;border-color:#f2c8cf!important;color:#74152a!important;text-shadow:none!important}
'''
        text = text.replace(anchor, anchor + block, 1)

    old = "        button.style.background = selected ? '#fff4f4' : '';\n        button.setAttribute('aria-pressed', selected ? 'true' : 'false');"
    new = "        button.style.background = selected ? '#fff4f4' : '';\n        button.style.color = selected ? '#74152a' : '';\n        button.setAttribute('aria-pressed', selected ? 'true' : 'false');"
    if old in text:
        text = text.replace(old, new, 1)
    elif "button.style.color = selected ? '#74152a' : '';" not in text:
        raise SystemExit("Nepodařilo se doplnit barvu zvolené odpovědi.")

    old_unlock = "const setUnlocked = () => buttons.forEach((button) => {button.disabled=false;button.style.borderColor='';button.style.background='';button.setAttribute('aria-pressed','false');});"
    new_unlock = "const setUnlocked = () => buttons.forEach((button) => {button.disabled=false;button.style.borderColor='';button.style.background='';button.style.color='';button.setAttribute('aria-pressed','false');});"
    if old_unlock in text:
        text = text.replace(old_unlock, new_unlock, 1)
    elif "button.style.color='';button.setAttribute('aria-pressed','false')" not in text:
        raise SystemExit("Nepodařilo se doplnit obnovení barvy tlačítka.")

    SITE_JS.write_text(text, encoding="utf-8", newline="\n")


def patch_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'/site\.js(?:\?v=[^\"\']*)?',
        f'/site.js?v={VERSION}',
        text,
    )
    if count == 0:
        raise SystemExit(f"V {path} nebyl nalezen odkaz na site.js.")
    path.write_text(updated, encoding="utf-8", newline="\n")


def main() -> None:
    patch_site_js()
    patch_html(ARTICLE)
    patch_html(DRAFT)

    site = SITE_JS.read_text(encoding="utf-8")
    article = ARTICLE.read_text(encoding="utf-8")
    required = [
        MARKER,
        '[data-poll-id=\\"alzbetinsky-klaster-kadan-2026\\"] .poll-result-label',
        "button.style.color = selected ? '#74152a' : '';",
        f'/site.js?v={VERSION}',
    ]
    missing = [item for item in required if item not in site and item not in article]
    if missing:
        raise SystemExit(f"Oprava není kompletní: {missing}")


if __name__ == "__main__":
    main()
