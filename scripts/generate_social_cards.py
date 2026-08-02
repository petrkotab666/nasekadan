#!/usr/bin/env python3
"""Vytvoří jedinečný 1200×630 obrázek pro každý článek a zapíše OG metadata.

Každý obrázek používá název článku, rubriku a jednoduchý tematický motiv.
Název souboru obsahuje hash metadat, takže změna článku vytvoří novou URL a
omezí problém se starou cache Facebooku. Redakční text článku se nemění.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1200
HEIGHT = 630
SOCIAL_DIR = Path("social")
SITE = "https://nasekadan.cz"
GENERIC_IMAGES = {
    f"{SITE}/social-card.png",
    "/social-card.png",
    "social-card.png",
}


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(value).split())


def meta_content(text: str, *, property_name: str | None = None, name: str | None = None) -> str:
    if property_name:
        pattern = rf'<meta\b[^>]*property=["\']{re.escape(property_name)}["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
    else:
        pattern = rf'<meta\b[^>]*name=["\']{re.escape(name or "")}["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
    match = re.search(pattern, text, re.I)
    return html.unescape(match.group(1)).strip() if match else ""


def title_from_html(text: str) -> str:
    return (
        meta_content(text, property_name="og:title")
        or (strip_tags(match.group(1)) if (match := re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.S)) else "")
        or (strip_tags(match.group(1)).split(" | ", 1)[0] if (match := re.search(r"<title>(.*?)</title>", text, re.I | re.S)) else "Naše Kadaň")
    )


def description_from_html(text: str) -> str:
    return meta_content(text, property_name="og:description") or meta_content(text, name="description")


def category_from_html(text: str) -> str:
    match = re.search(r'<p\b[^>]*class=["\'][^"\']*\btag\b[^"\']*["\'][^>]*>(.*?)</p>', text, re.I | re.S)
    if not match:
        return "NAŠE KADAŇ"
    value = strip_tags(match.group(1))
    value = re.split(r"\s*[·|]\s*|\s+\d{1,2}\.\s*\w+", value, maxsplit=1, flags=re.I)[0]
    return value[:46].upper() or "NAŠE KADAŇ"


def select_palette(title: str, category: str) -> tuple[tuple[int, int, int], tuple[int, int, int], str]:
    value = f"{title} {category}".lower()
    if any(token in value for token in ("kyber", "software", "internet", "technolog")):
        return (7, 24, 39), (10, 101, 145), "lock"
    if any(token in value for token in ("nemocnic", "ambulanc", "zdrav")):
        return (16, 35, 45), (31, 126, 140), "health"
    if any(token in value for token in ("vlak", "výluk", "doprava", "nehod")):
        return (22, 37, 49), (176, 91, 35), "transport"
    if any(token in value for token in ("volb", "město", "zastupitel", "polit")):
        return (31, 32, 45), (119, 50, 75), "city"
    return (14, 32, 43), (49, 96, 116), "city"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_title(draw: ImageDraw.ImageDraw, title: str, max_width: int, max_lines: int = 4) -> tuple[list[str], ImageFont.FreeTypeFont]:
    for size in range(58, 37, -2):
        current = font(size, bold=True)
        words = title.split()
        lines: list[str] = []
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=current)[2] <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        if len(lines) <= max_lines:
            return lines, current
    return textwrap.wrap(title, width=30)[:max_lines], font(38, bold=True)


def draw_icon(draw: ImageDraw.ImageDraw, kind: str, accent: tuple[int, int, int]) -> None:
    white = (226, 246, 252, 255)
    if kind == "lock":
        draw.arc((790, 70, 1070, 330), 180, 360, fill=white, width=34)
        draw.rounded_rectangle((755, 220, 1105, 505), radius=34, fill=(*accent, 235), outline=white, width=5)
        draw.ellipse((905, 315, 957, 367), fill=white)
        draw.polygon([(931, 354), (908, 425), (954, 425)], fill=white)
    elif kind == "health":
        draw.rounded_rectangle((770, 115, 1095, 500), radius=34, fill=(*accent, 235), outline=white, width=5)
        draw.rectangle((895, 190, 970, 425), fill=white)
        draw.rectangle((815, 270, 1050, 345), fill=white)
    elif kind == "transport":
        draw.rounded_rectangle((760, 135, 1100, 485), radius=38, fill=(*accent, 235), outline=white, width=5)
        draw.rounded_rectangle((815, 190, 1045, 310), radius=16, fill=white)
        draw.ellipse((815, 400, 885, 470), fill=white)
        draw.ellipse((975, 400, 1045, 470), fill=white)
        draw.line((800, 530, 1060, 530), fill=white, width=8)
    else:
        draw.rounded_rectangle((790, 180, 1070, 490), radius=26, fill=(*accent, 235), outline=white, width=5)
        draw.polygon([(760, 210), (930, 75), (1100, 210)], fill=white)
        for x in (830, 910, 990):
            draw.rectangle((x, 250, x + 45, 430), fill=white)
        draw.rectangle((800, 430, 1060, 475), fill=white)


def create_card(title: str, category: str, output: Path) -> None:
    base, accent, icon = select_palette(title, category)
    image = Image.new("RGBA", (WIDTH, HEIGHT), (*base, 255))
    draw = ImageDraw.Draw(image)

    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT - 1)
        color = tuple(int(base[index] + (accent[index] - base[index]) * ratio * 0.22) for index in range(3))
        draw.line((0, y, WIDTH, y), fill=(*color, 255))

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((660, -80, 1260, 530), fill=(*accent, 100))
    image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(55)))
    draw = ImageDraw.Draw(image)

    for x in range(690, WIDTH, 48):
        draw.line((x, 0, x, HEIGHT), fill=(*accent, 100), width=1)
    for y in range(0, HEIGHT, 48):
        draw.line((660, y, WIDTH, y), fill=(*accent, 100), width=1)

    draw.polygon([(0, 0), (770, 0), (625, HEIGHT), (0, HEIGHT)], fill=(5, 18, 30, 238))
    draw_icon(draw, icon, accent)

    draw.text((70, 52), "NAŠE KADAŇ", font=font(29, bold=True), fill="white")
    draw.rectangle((70, 98, 565, 106), fill=(177, 36, 47, 255))

    category_font = font(23, bold=True)
    category_width = min(535, draw.textbbox((0, 0), category, font=category_font)[2] + 38)
    draw.rounded_rectangle((70, 130, 70 + category_width, 175), radius=9, fill=(177, 36, 47, 255))
    draw.text((88, 139), category, font=category_font, fill="white")

    lines, title_font = fit_title(draw, title, 575)
    y = 205
    line_height = title_font.size + 9
    for line in lines:
        draw.text((70, y), line, font=title_font, fill="white")
        y += line_height

    draw.line((70, 520, 610, 520), fill=(129, 184, 205, 255), width=3)
    badge = "AKTUÁLNĚ NA NASEKADAN.CZ"
    badge_font = font(22, bold=True)
    badge_width = draw.textbbox((0, 0), badge, font=badge_font)[2] + 38
    draw.rounded_rectangle((70, 548, 70 + badge_width, 594), radius=8, fill=(232, 237, 240, 255))
    draw.text((89, 557), badge, font=badge_font, fill=(27, 48, 60, 255))
    draw.rounded_rectangle((1080, 545, 1145, 600), radius=10, fill=(177, 36, 47, 255))
    draw.text((1092, 556), "NK", font=font(23, bold=True), fill="white")

    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG", optimize=True)


def replace_meta(text: str, key: str, value: str, *, property_meta: bool = True) -> str:
    attribute = "property" if property_meta else "name"
    pattern = re.compile(rf'<meta\b[^>]*{attribute}=["\']{re.escape(key)}["\'][^>]*>', re.I)
    tag = f'<meta {attribute}="{key}" content="{html.escape(value, quote=True)}">'
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    head_end = re.search(r"</head>", text, re.I)
    if not head_end:
        return text
    return text[: head_end.start()] + "  " + tag + "\n" + text[head_end.start() :]


def custom_social_card_errors(text: str) -> list[str]:
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

def process_article(path: Path, write: bool) -> tuple[bool, list[str]]:
    original = path.read_text(encoding="utf-8")
    if "article-shell" not in original or "NewsArticle" not in original:
        return False, []

    # Redakčně připravené karty mají přednost před automatickou šablonou.
    # Workflow je pouze ověří; nikdy nepřepíše jejich og:image ani twitter:image.
    if meta_content(original, name="nasekadan:social-card").lower() == "custom":
        errors = custom_social_card_errors(original)
        return False, errors

    title = title_from_html(original)
    description = description_from_html(original)
    category = category_from_html(original)
    digest = hashlib.sha256(f"{path.stem}|{title}|{description}|{category}".encode("utf-8")).hexdigest()[:10]
    relative = f"/social/{path.stem}-{digest}.png"
    absolute = f"{SITE}{relative}"
    output = SOCIAL_DIR / f"{path.stem}-{digest}.png"

    updated = original
    updated = replace_meta(updated, "og:image", absolute, property_meta=True)
    updated = replace_meta(updated, "og:image:type", "image/png", property_meta=True)
    updated = replace_meta(updated, "og:image:width", str(WIDTH), property_meta=True)
    updated = replace_meta(updated, "og:image:height", str(HEIGHT), property_meta=True)
    updated = replace_meta(updated, "twitter:image", absolute, property_meta=False)

    errors: list[str] = []
    current_image = meta_content(updated, property_name="og:image")
    if current_image in GENERIC_IMAGES or not current_image.endswith(f"-{digest}.png"):
        errors.append("OG obrázek není jedinečný pro článek")

    changed = updated != original or not output.exists()
    if write:
        if not output.exists():
            create_card(title, category, output)
        if updated != original:
            path.write_text(updated, encoding="utf-8")

    if write and not output.exists():
        errors.append("soubor sociálního obrázku nebyl vytvořen")
    return changed, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.write and not args.check:
        args.write = args.check = True

    changed = 0
    checked = 0
    failures: list[str] = []
    for path in sorted(Path("clanky").glob("*.html")):
        did_change, errors = process_article(path, args.write)
        if "article-shell" not in path.read_text(encoding="utf-8"):
            continue
        checked += 1
        if did_change:
            changed += 1
            print(f"Sociální obrázek: {path}")
        if args.check:
            failures.extend(f"{path}: {error}" for error in errors)

    print(f"Článků zkontrolováno: {checked}; změněno nebo doplněno: {changed}")
    if failures:
        print("Chyby sociálních obrázků:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
