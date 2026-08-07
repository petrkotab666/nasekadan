#!/usr/bin/env python3
"""Normalizuje a blokujícím způsobem ověřuje sociální náhledy článků.

Facebook/Meta crawler nesmí být závislý na cizím serveru ani na souboru, který
není součástí stejného deploye. Každý veřejný článek proto musí mít vlastní
lokální /social/ obrázek, správný MIME typ, rozměr 1200x630, secure_url a shodný
Twitter náhled. Skript po --write metadata doplní a --check ověří i skutečný
obrazový soubor přes Pillow.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_DIR = ROOT / "clanky"
SITE = "https://nasekadan.cz"
WIDTH = 1200
HEIGHT = 630
FORMATS = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
}


def attr(tag: str, name: str) -> str:
    match = re.search(rf'\b{re.escape(name)}\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
    return html.unescape(match.group(2).strip()) if match else ""


def meta(text: str, *, prop: str | None = None, name: str | None = None) -> str:
    for match in re.finditer(r"<meta\b[^>]*>", text, re.I):
        tag = match.group(0)
        if prop and attr(tag, "property").lower() != prop.lower():
            continue
        if name and attr(tag, "name").lower() != name.lower():
            continue
        return attr(tag, "content")
    return ""


def replace_meta(text: str, key: str, value: str, *, property_meta: bool = True) -> str:
    attribute = "property" if property_meta else "name"
    pattern = re.compile(
        rf'<meta\b(?=[^>]*\b{attribute}\s*=\s*["\']{re.escape(key)}["\'])[^>]*>',
        re.I,
    )
    tag = f'<meta {attribute}="{key}" content="{html.escape(value, quote=True)}">'
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    match = re.search(r"</head>", text, re.I)
    if not match:
        return text
    return text[:match.start()] + tag + "\n" + text[match.start():]


def title(text: str) -> str:
    value = meta(text, prop="og:title")
    if value:
        return value
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.S)
    if not match:
        return "Naše Kadaň"
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", match.group(1))).split())


def is_article(path: Path, text: str) -> bool:
    if path.name == "index.html" or path.name.startswith("strana-"):
        return False
    return "article-shell" in text and "NewsArticle" in text


def image_info(image_url: str) -> tuple[Path | None, str | None, list[str]]:
    errors: list[str] = []
    if not image_url.startswith(f"{SITE}/social/"):
        return None, None, ["og:image není lokální URL v /social/"]
    relative = image_url.removeprefix(SITE).split("?", 1)[0].lstrip("/")
    path = ROOT / relative
    if not path.is_file():
        return path, None, [f"soubor OG obrázku neexistuje: {relative}"]
    if path.stat().st_size < 10_000:
        errors.append(f"OG obrázek je podezřele malý: {relative} ({path.stat().st_size} B)")
    try:
        with Image.open(path) as image:
            image.load()
            fmt = image.format or ""
            mime = FORMATS.get(fmt)
            if not mime:
                errors.append(f"nepodporovaný formát OG obrázku: {fmt or 'neznámý'}")
            if image.size != (WIDTH, HEIGHT):
                errors.append(
                    f"OG obrázek nemá {WIDTH}x{HEIGHT}: {relative} má {image.width}x{image.height}"
                )
            return path, mime, errors
    except Exception as exc:
        errors.append(f"OG obrázek nelze otevřít: {relative}: {exc}")
        return path, None, errors


def process(path: Path, *, write: bool) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not is_article(path, text):
        return []

    image_url = meta(text, prop="og:image")
    image_path, mime, errors = image_info(image_url)
    if image_path is None or mime is None:
        return errors

    if write:
        updated = text
        updated = replace_meta(updated, "og:image", image_url)
        updated = replace_meta(updated, "og:image:secure_url", image_url)
        updated = replace_meta(updated, "og:image:type", mime)
        updated = replace_meta(updated, "og:image:width", str(WIDTH))
        updated = replace_meta(updated, "og:image:height", str(HEIGHT))
        updated = replace_meta(updated, "og:image:alt", title(updated))
        updated = replace_meta(updated, "twitter:card", "summary_large_image", property_meta=False)
        updated = replace_meta(updated, "twitter:image", image_url, property_meta=False)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            text = updated

    expected = {
        "og:image": image_url,
        "og:image:secure_url": image_url,
        "og:image:type": mime,
        "og:image:width": str(WIDTH),
        "og:image:height": str(HEIGHT),
    }
    for key, value in expected.items():
        if meta(text, prop=key) != value:
            errors.append(f"{key} není správně nastaveno")
    if meta(text, name="twitter:card") != "summary_large_image":
        errors.append("twitter:card není summary_large_image")
    if meta(text, name="twitter:image") != image_url:
        errors.append("twitter:image se neshoduje s og:image")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        args.write = args.check = True

    failures: list[str] = []
    count = 0
    for path in sorted(ARTICLE_DIR.glob("*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not is_article(path, text):
            continue
        count += 1
        errors = process(path, write=args.write)
        if args.check:
            failures.extend(f"{path.relative_to(ROOT)}: {error}" for error in errors)

    print(f"Sociální náhledy zkontrolovány: {count} článků")
    if failures:
        print("KONTROLA SOCIÁLNÍCH NÁHLEDŮ SELHALA", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Facebook/OG obrázky: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
