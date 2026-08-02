#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_social_cards.py"
ARTICLE = ROOT / "clanky/kulturni-zarizeni-kadan.html"
FIXER = ROOT / "scripts/fix_kzk_facebook_preview_20260802.py"
PUBLISHER = ROOT / "scripts/publish_kzk_20260802.py"
NEW_IMAGE = "https://nasekadan.cz/social/kzk-kultura-strelnice-klaster-20260802-v2.png"
MARKER = '<meta name="nasekadan:social-card" content="custom">'


def protect_generator() -> None:
    text = GENERATOR.read_text(encoding="utf-8")
    if "def custom_social_card_errors" not in text:
        anchor = "\ndef process_article(path: Path, write: bool) -> tuple[bool, list[str]]:\n"
        helper = '''\ndef custom_social_card_errors(text: str) -> list[str]:
    """Ověří ručně připravenou kartu, ale nikdy ji nepřegeneruje."""
    errors: list[str] = []
    image = meta_content(text, property_name="og:image")
    if not image:
        return ["ruční sociální karta nemá og:image"]
    if not image.startswith(f"{SITE}/social/"):
        errors.append("ruční sociální karta neleží v lokální složce social")
        return errors
    relative = image.removeprefix(SITE).split("?", 1)[0].lstrip("/")
    if not Path(relative).is_file():
        errors.append(f"soubor ruční sociální karty neexistuje: {relative}")
    if meta_content(text, property_name="og:image:width") != str(WIDTH):
        errors.append("ruční sociální karta nemá šířku 1200")
    if meta_content(text, property_name="og:image:height") != str(HEIGHT):
        errors.append("ruční sociální karta nemá výšku 630")
    return errors
'''
        if anchor not in text:
            raise SystemExit("V generátoru chybí funkce process_article.")
        text = text.replace(anchor, helper + anchor, 1)

    if 'meta_content(original, name="nasekadan:social-card")' not in text:
        anchor = '''    if "article-shell" not in original or "NewsArticle" not in original:
        return False, []

'''
        block = '''    if "article-shell" not in original or "NewsArticle" not in original:
        return False, []

    # Redakčně připravené karty mají přednost před automatickou šablonou.
    # Workflow je pouze ověří; nikdy nepřepíše jejich og:image ani twitter:image.
    if meta_content(original, name="nasekadan:social-card").lower() == "custom":
        errors = custom_social_card_errors(original)
        return False, errors

'''
        if anchor not in text:
            raise SystemExit("V generátoru chybí vstupní kontrola článku.")
        text = text.replace(anchor, block, 1)

    GENERATOR.write_text(text, encoding="utf-8", newline="\n")


def mark_article(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        anchor = f'<meta property="og:image" content="{NEW_IMAGE}">'
        if anchor not in text:
            raise SystemExit(f"{path}: chybí nový og:image.")
        text = text.replace(anchor, MARKER + "\n  " + anchor, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_fixer() -> None:
    text = FIXER.read_text(encoding="utf-8")
    if "nasekadan:social-card" not in text:
        anchor = '''    if 'property="og:image:secure_url"' not in html:
'''
        addition = '''    if 'name="nasekadan:social-card"' not in html:
        marker = f'<meta property="og:image" content="{NEW_IMAGE}">'
        html = html.replace(marker, '<meta name="nasekadan:social-card" content="custom">\\n  ' + marker, 1)
    if 'property="og:image:secure_url"' not in html:
'''
        if anchor not in text:
            raise SystemExit("V opravě KZK chybí kotva pro Open Graph.")
        text = text.replace(anchor, addition, 1)
    FIXER.write_text(text, encoding="utf-8", newline="\n")


def update_publisher() -> None:
    text = PUBLISHER.read_text(encoding="utf-8")
    if "nasekadan:social-card" not in text:
        anchor = '''  <meta property="og:image" content="{IMAGE_URL}">
'''
        replacement = '''  <meta name="nasekadan:social-card" content="custom">
  <meta property="og:image" content="{IMAGE_URL}">
'''
        if anchor not in text:
            raise SystemExit("V publikačním skriptu KZK chybí og:image kotva.")
        text = text.replace(anchor, replacement, 1)
    PUBLISHER.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    for path in (GENERATOR, ARTICLE, FIXER, PUBLISHER):
        if not path.exists():
            raise SystemExit(f"Chybí soubor: {path}")
    protect_generator()
    mark_article(ARTICLE)
    update_fixer()
    update_publisher()
    print("Ruční sociální karta KZK je chráněná před automatickým přepsáním.")


if __name__ == "__main__":
    main()
