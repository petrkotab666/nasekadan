#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky/kulturni-zarizeni-kadan.html"
RSS = ROOT / "rss.xml"
PUBLISHER = ROOT / "scripts/publish_kzk_20260802.py"
SOCIAL = ROOT / "social/kzk-kultura-strelnice-klaster-20260802-v2.png"
OLD_IMAGE = "https://nasekadan.cz/social/kulturni-zarizeni-kadan-20260802.png"
NEW_IMAGE = "https://nasekadan.cz/social/kzk-kultura-strelnice-klaster-20260802-v2.png"
TITLE = "Od Střelnice po klášter. Co všechno pro Kadaň zajišťuje KZK"
MODIFIED = "2026-08-02T06:05:00+02:00"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def gradient(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    start = (12, 31, 42)
    end = (48, 78, 91)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(round(start[i] * (1 - t) + end[i] * t) for i in range(3))
        draw.line((0, y, width, y), fill=color)


def draw_book(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    mid = (x1 + x2) // 2
    draw.rounded_rectangle((x1, y1, mid - 5, y2), 8, fill=(239, 246, 248), outline=(201, 164, 90), width=3)
    draw.rounded_rectangle((mid + 5, y1, x2, y2), 8, fill=(239, 246, 248), outline=(201, 164, 90), width=3)
    draw.line((mid, y1 + 4, mid, y2 - 4), fill=(201, 164, 90), width=4)


def draw_stage(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, 10, outline=(239, 246, 248), width=4)
    draw.polygon([(x1, y1), (x1 + 38, y1), (x1 + 62, y2 - 14), (x1, y2)], fill=(169, 35, 43))
    draw.polygon([(x2, y1), (x2 - 38, y1), (x2 - 62, y2 - 14), (x2, y2)], fill=(169, 35, 43))
    draw.line((x1 + 18, y2 - 12, x2 - 18, y2 - 12), fill=(201, 164, 90), width=4)


def draw_tower(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    draw.polygon([(cx, y1), (x1 + 14, y1 + 38), (x2 - 14, y1 + 38)], fill=(201, 164, 90))
    draw.rectangle((x1 + 24, y1 + 38, x2 - 24, y2), fill=(239, 246, 248), outline=(201, 164, 90), width=3)
    for yy in (y1 + 57, y1 + 82):
        draw.rounded_rectangle((cx - 8, yy, cx + 8, yy + 17), 3, fill=(28, 54, 67))


def draw_cup(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 12, y1 + 27, x2 - 22, y2 - 9), 12, fill=(239, 246, 248), outline=(201, 164, 90), width=3)
    draw.ellipse((x2 - 34, y1 + 38, x2, y2 - 17), outline=(239, 246, 248), width=5)
    for xx in (x1 + 30, x1 + 54, x1 + 78):
        draw.arc((xx, y1 - 2, xx + 22, y1 + 38), 70, 250, fill=(239, 246, 248), width=4)


def build_social() -> None:
    w, h = 1200, 630
    image = Image.new("RGB", (w, h), (12, 31, 42))
    draw = ImageDraw.Draw(image)
    gradient(draw, w, h)

    draw.rectangle((0, 0, 20, h), fill=(169, 35, 43))
    draw.rectangle((20, h - 18, w, h), fill=(201, 164, 90))
    draw.polygon([(735, 0), (1200, 0), (1200, 630), (850, 630)], fill=(9, 25, 34))
    draw.line((735, 0, 850, 630), fill=(201, 164, 90), width=3)

    draw.text((62, 45), "NAŠE KADAŇ", font=font(BOLD, 34), fill=(255, 255, 255))
    draw.rounded_rectangle((62, 108, 316, 157), 22, fill=(169, 35, 43))
    draw.text((83, 119), "NEDĚLNÍ ČTENÍ", font=font(BOLD, 22), fill=(255, 255, 255))

    y = 196
    for line in ("OD STŘELNICE", "PO KLÁŠTER"):
        draw.text((62, y), line, font=font(BOLD, 58), fill=(255, 255, 255))
        y += 70

    subtitle = "Co všechno pro Kadaň zajišťuje KZK"
    for line in textwrap.wrap(subtitle, width=34):
        draw.text((64, y + 6), line, font=font(REGULAR, 30), fill=(224, 236, 240))
        y += 41

    chips = ["STŘELNICE", "ORFEUM", "KNIHOVNA", "KLÁŠTER", "KONÍRNA"]
    cx, cy = 62, 535
    small = font(BOLD, 15)
    for chip in chips:
        bbox = draw.textbbox((0, 0), chip, font=small)
        cw = bbox[2] - bbox[0] + 28
        if cx + cw > 715:
            break
        draw.rounded_rectangle((cx, cy, cx + cw, cy + 38), 19, fill=(239, 246, 248))
        draw.text((cx + 14, cy + 9), chip, font=small, fill=(20, 42, 54))
        cx += cw + 10

    cards = [
        ((805, 70, 980, 270), "DIVADLO", draw_stage),
        ((995, 70, 1170, 270), "KNIHY", draw_book),
        ((805, 300, 980, 500), "PAMÁTKY", draw_tower),
        ((995, 300, 1170, 500), "SETKÁVÁNÍ", draw_cup),
    ]
    card_title = font(BOLD, 17)
    for (x1, y1, x2, y2), label, icon in cards:
        draw.rounded_rectangle((x1, y1, x2, y2), 22, fill=(23, 50, 63), outline=(71, 104, 117), width=2)
        icon(draw, (x1 + 30, y1 + 28, x2 - 30, y1 + 133))
        tb = draw.textbbox((0, 0), label, font=card_title)
        tw = tb[2] - tb[0]
        draw.text(((x1 + x2 - tw) // 2, y2 - 43), label, font=card_title, fill=(255, 255, 255))

    draw.text((810, 548), "KULTURA • HISTORIE • MĚSTO", font=font(BOLD, 17), fill=(234, 241, 243))
    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image.save(SOCIAL, format="PNG", optimize=True)


def replace_meta(html: str) -> str:
    html = html.replace(OLD_IMAGE, NEW_IMAGE)
    html = re.sub(
        r'<meta property="article:modified_time" content="[^"]+">',
        f'<meta property="article:modified_time" content="{MODIFIED}">',
        html,
        count=1,
    )
    if 'name="nasekadan:social-card"' not in html:
        marker = f'<meta property="og:image" content="{NEW_IMAGE}">'
        html = html.replace(marker, '<meta name="nasekadan:social-card" content="custom">\n  ' + marker, 1)
    if 'property="og:image:secure_url"' not in html:
        marker = f'<meta property="og:image" content="{NEW_IMAGE}">'
        extras = (
            f'\n  <meta property="og:image:secure_url" content="{NEW_IMAGE}">'
            f'\n  <meta property="og:image:alt" content="{TITLE}">'
            f'\n  <link rel="image_src" href="{NEW_IMAGE}">'
        )
        html = html.replace(marker, marker + extras, 1)
    html = re.sub(
        r'("dateModified"\s*:\s*")[^"]+("\s*,)',
        rf'\g<1>{MODIFIED}\2',
        html,
        count=1,
    )
    return html


def update_publisher() -> None:
    if not PUBLISHER.exists():
        return
    text = PUBLISHER.read_text(encoding="utf-8")
    text = text.replace("social/kulturni-zarizeni-kadan-20260802.png", "social/kzk-kultura-strelnice-klaster-20260802-v2.png")
    text = text.replace(OLD_IMAGE, NEW_IMAGE)
    PUBLISHER.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    if not ARTICLE.exists():
        raise SystemExit("Chybí zveřejněný článek KZK.")
    build_social()
    article = replace_meta(ARTICLE.read_text(encoding="utf-8"))
    ARTICLE.write_text(article, encoding="utf-8", newline="\n")
    if RSS.exists():
        RSS.write_text(RSS.read_text(encoding="utf-8").replace(OLD_IMAGE, NEW_IMAGE), encoding="utf-8", newline="\n")
    update_publisher()

    with Image.open(SOCIAL) as check:
        if check.size != (1200, 630) or check.mode != "RGB":
            raise SystemExit(f"Neplatný sociální obrázek: {check.size}, {check.mode}")
    article = ARTICLE.read_text(encoding="utf-8")
    required = [NEW_IMAGE, 'og:image:secure_url', 'og:image:alt', 'summary_large_image']
    missing = [item for item in required if item not in article]
    if missing:
        raise SystemExit(f"V článku chybí Open Graph údaje: {missing}")
    if OLD_IMAGE in article:
        raise SystemExit("Článek stále odkazuje na starý sociální obrázek.")
    print(f"Nový sociální obrázek: {SOCIAL} ({SOCIAL.stat().st_size} B)")


if __name__ == "__main__":
    main()
