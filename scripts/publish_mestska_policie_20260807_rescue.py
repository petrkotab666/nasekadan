#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publish_mestska_policie_20260807 as mp

SOCIAL_REL = "social/mestska-policie-kadan-fakta-diskuse-2026.png"
SOCIAL_URL = f"https://nasekadan.cz/{SOCIAL_REL}"


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def fit_lines(draw, text: str, fnt, max_width: int):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        box = draw.textbbox((0, 0), trial, font=fnt)
        if box[2] - box[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_social() -> None:
    path = ROOT / SOCIAL_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1200, 630), (8, 43, 71))
    draw = ImageDraw.Draw(img)
    # redakční akcenty bez závislosti na externí fotografii
    draw.rectangle((0, 0, 1200, 22), fill=(223, 58, 49))
    draw.rectangle((70, 72, 405, 122), fill=(242, 180, 38))
    draw.text((91, 83), "NAŠE KADAŇ · OVĚŘUJEME FAKTA", font=font(24, True), fill=(8, 43, 71))

    headline_font = font(56, True)
    sub_font = font(31, False)
    x = 74
    y = 164
    for line in fit_lines(draw, "Neřeší městská policie dopravu?", headline_font, 1050):
        draw.text((x, y), line, font=headline_font, fill=(255, 255, 255))
        y += 69
    y += 20
    for line in fit_lines(draw, "Bouřlivá debata přiměla redakci ověřit fakta", sub_font, 1030):
        draw.text((x, y), line, font=sub_font, fill=(215, 228, 238))
        y += 43

    draw.line((74, 521, 1125, 521), fill=(86, 126, 154), width=2)
    draw.text((74, 546), "7. srpna 2026 · nasekadan.cz", font=font(27, True), fill=(255, 255, 255))
    img.save(path, format="PNG", optimize=True)


def patch_article_social() -> None:
    text = mp.ARTICLE.read_text(encoding="utf-8")
    text = text.replace("https://nasekadan.cz/social-card.png", SOCIAL_URL)
    mp.write(mp.ARTICLE, text)


def assert_article() -> None:
    text = mp.ARTICLE.read_text(encoding="utf-8")
    required = [
        f"<h1>{mp.TITLE}</h1>",
        "1 886",
        "3 840",
        "Obyvatelé popisují rychlé reakce hlídek",
        'data-nk-newsarticle="1"',
        '"@type":"NewsArticle"',
        f'<meta property="og:image" content="{SOCIAL_URL}">',
        f'<meta name="twitter:image" content="{SOCIAL_URL}">',
        SOCIAL_URL,
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError("Chybí povinné části článku: " + repr(missing))
    if "noindex" in text.lower():
        raise RuntimeError("Článek zůstal noindex.")
    with Image.open(ROOT / SOCIAL_REL) as im:
        if im.size != (1200, 630):
            raise RuntimeError(f"Sociální obrázek má rozměr {im.size}, očekáváno 1200x630.")


def main() -> int:
    mp.make_article()
    generate_social()
    patch_article_social()
    # Registr musí existovat dříve, než helper znovu sestaví sitemapu.
    mp.upsert_registry()
    mp.rebuild_surfaces_and_manifest()
    # Druhý průchod registru srovná počty RSS/news-sitemap po rebuildingu.
    mp.upsert_registry()
    mp.validate()
    assert_article()
    print(json.dumps({
        "status": "prepared",
        "article": mp.URL,
        "social": SOCIAL_URL,
        "source_commit": os.environ.get("ARTICLE_SOURCE_COMMIT"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
