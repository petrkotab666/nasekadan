#!/usr/bin/env python3
"""Kontrola a automatická oprava červených textových štítků sociálních grafik.

Skript prochází sociální obrázky skutečně použité v publikovaných článcích,
vyhledá plné červené štítky v horní části grafiky a změří vnitřní odsazení
světlého textu. Pokud text nemá bezpečnou rezervu, štítek rozšíří, vytvoří
nový soubor s obsahovým hashem a přepíše odkazy bez rizika staré cache.

Současně umí opravit hlavní generátor sociálních karet tak, aby budoucí
štítky vždy měřily text, zmenšily písmo a text svisle i vodorovně vystředily.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://nasekadan.cz"
ARTICLES_DIR = ROOT / "clanky"
SOCIAL_DIR = ROOT / "social"
GENERATOR = ROOT / "scripts" / "generate_social_cards.py"
REPORT_DEFAULT = ROOT / "data" / "social-badge-audit.json"

MIN_PAD_X = 18
MIN_PAD_Y = 8
MAX_BADGE_X = 760
MAX_BADGE_Y_RATIO = 0.46
RED_DENSITY_MIN = 0.42
MARKER = "SOCIAL-BADGE-FIT-V1"


@dataclass
class BadgeFinding:
    image: str
    article_count: int
    box: list[int]
    text_box: list[int]
    padding: dict[str, int]
    needs_fix: bool
    reason: str


@dataclass
class ImageResult:
    image: str
    articles: list[str]
    badges: list[BadgeFinding]
    changed: bool = False
    new_image: str | None = None


def meta_content(text: str, key: str, *, property_meta: bool = True) -> str:
    attr = "property" if property_meta else "name"
    match = re.search(
        rf'<meta\b[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*content=["\']([^"\']+)["\'][^>]*>',
        text,
        re.I,
    )
    if not match:
        match = re.search(
            rf'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*{attr}=["\']{re.escape(key)}["\'][^>]*>',
            text,
            re.I,
        )
    return html.unescape(match.group(1)).strip() if match else ""


def local_social_path(url: str) -> Path | None:
    clean = html.unescape(url).split("?", 1)[0]
    if clean.startswith(f"{SITE}/social/"):
        return ROOT / clean.removeprefix(f"{SITE}/")
    if clean.startswith("/social/"):
        return ROOT / clean.lstrip("/")
    return None


def article_image_index() -> dict[Path, list[Path]]:
    result: dict[Path, list[Path]] = {}
    for article in sorted(ARTICLES_DIR.glob("*.html")):
        if article.name == "index.html" or re.fullmatch(r"strana-\d+\.html", article.name):
            continue
        text = article.read_text(encoding="utf-8", errors="replace")
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
            continue
        image_url = meta_content(text, "og:image")
        image_path = local_social_path(image_url)
        if image_path and image_path.is_file():
            result.setdefault(image_path, []).append(article)
    return result


def runs(active: np.ndarray) -> list[tuple[int, int]]:
    """Vrátí souvislé úseky True jako intervaly [start, end)."""
    output: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(active.tolist() + [False]):
        if value and start is None:
            start = index
        elif not value and start is not None:
            output.append((start, index))
            start = None
    return output


def red_mask(array: np.ndarray) -> np.ndarray:
    rgb = array[..., :3].astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (
        (r >= 115)
        & (r >= g + 42)
        & (r >= b + 32)
        & (g <= 125)
        & (b <= 135)
    )


def light_mask(array: np.ndarray) -> np.ndarray:
    rgb = array[..., :3].astype(np.int16)
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    luma = (rgb[..., 0] * 299 + rgb[..., 1] * 587 + rgb[..., 2] * 114) // 1000
    return (luma >= 125) & (maximum >= 150) & ((maximum - minimum) <= 145)


def detect_badges(image: Image.Image, image_name: str, article_count: int) -> list[BadgeFinding]:
    array = np.asarray(image.convert("RGB"))
    height, width = array.shape[:2]
    red = red_mask(array)
    roi_height = max(1, int(height * MAX_BADGE_Y_RATIO))
    roi_width = min(width, MAX_BADGE_X)
    roi = red[:roi_height, :roi_width]

    row_threshold = max(24, int(width * 0.018))
    row_active = roi.sum(axis=1) >= row_threshold
    findings: list[BadgeFinding] = []

    for y1, y2 in runs(row_active):
        band_height = y2 - y1
        if not 18 <= band_height <= 78:
            continue
        band = roi[y1:y2]
        col_threshold = max(3, int(band_height * 0.38))
        col_active = band.sum(axis=0) >= col_threshold
        for x1, x2 in runs(col_active):
            box_width = x2 - x1
            if not 48 <= box_width <= 690:
                continue
            density = float(band[:, x1:x2].mean())
            if density < RED_DENSITY_MIN:
                continue

            sx1 = max(0, x1 - 8)
            sx2 = min(roi_width, max(x2 + 260, x1 + 300))
            sy1 = max(0, y1 - 5)
            sy2 = min(roi_height, y2 + 5)
            light = light_mask(array[sy1:sy2, sx1:sx2])
            light &= ~red[sy1:sy2, sx1:sx2]

            # Písmena musí vytvářet alespoň několik pixelů v řádku i sloupci.
            ys, xs = np.where(light)
            if len(xs) < 12:
                continue
            valid_cols = np.where(light.sum(axis=0) >= 2)[0]
            valid_rows = np.where(light.sum(axis=1) >= 2)[0]
            if len(valid_cols) == 0 or len(valid_rows) == 0:
                continue
            tx1 = sx1 + int(valid_cols.min())
            tx2 = sx1 + int(valid_cols.max()) + 1
            ty1 = sy1 + int(valid_rows.min())
            ty2 = sy1 + int(valid_rows.max()) + 1

            # Text musí alespoň zčásti ležet uvnitř červeného prvku.
            overlap_x = max(0, min(x2, tx2) - max(x1, tx1))
            overlap_y = max(0, min(y2, ty2) - max(y1, ty1))
            if overlap_x < 12 or overlap_y < 6:
                continue

            padding = {
                "left": tx1 - x1,
                "right": x2 - tx2,
                "top": ty1 - y1,
                "bottom": y2 - ty2,
            }
            needs_fix = (
                padding["left"] < MIN_PAD_X
                or padding["right"] < MIN_PAD_X
                or padding["top"] < MIN_PAD_Y
                or padding["bottom"] < MIN_PAD_Y
            )
            reasons = [
                name
                for name, value, minimum in (
                    ("levý okraj", padding["left"], MIN_PAD_X),
                    ("pravý okraj", padding["right"], MIN_PAD_X),
                    ("horní okraj", padding["top"], MIN_PAD_Y),
                    ("dolní okraj", padding["bottom"], MIN_PAD_Y),
                )
                if value < minimum
            ]
            findings.append(
                BadgeFinding(
                    image=image_name,
                    article_count=article_count,
                    box=[x1, y1, x2, y2],
                    text_box=[tx1, ty1, tx2, ty2],
                    padding=padding,
                    needs_fix=needs_fix,
                    reason=", ".join(reasons) if reasons else "v pořádku",
                )
            )
    return findings


def median_red(array: np.ndarray, box: list[int]) -> tuple[int, int, int]:
    x1, y1, x2, y2 = box
    region = array[y1:y2, x1:x2, :3]
    mask = red_mask(region)
    pixels = region[mask]
    if len(pixels) == 0:
        return (177, 36, 47)
    value = np.median(pixels, axis=0).astype(int)
    return tuple(int(channel) for channel in value[:3])


def normalize_image(image: Image.Image, findings: list[BadgeFinding]) -> Image.Image:
    base = image.convert("RGB")
    for finding in findings:
        if not finding.needs_fix:
            continue
        original = np.asarray(base).copy()
        height, width = original.shape[:2]
        x1, y1, x2, y2 = finding.box
        tx1, ty1, tx2, ty2 = finding.text_box
        nx1 = max(0, min(x1, tx1 - MIN_PAD_X))
        nx2 = min(width, max(x2, tx2 + MIN_PAD_X))
        ny1 = max(0, min(y1, ty1 - MIN_PAD_Y))
        ny2 = min(height, max(y2, ty2 + MIN_PAD_Y))
        fill = median_red(original, finding.box)

        overlay = base.copy()
        overlay_draw = ImageDraw.Draw(overlay)
        radius = max(7, min(13, (ny2 - ny1) // 4))
        overlay_draw.rounded_rectangle((nx1, ny1, nx2, ny2), radius=radius, fill=fill)
        changed = np.asarray(overlay).copy().astype(np.float32)

        # Vrátí původní světlé textové pixely včetně antialiasovaných okrajů.
        crop = original[ny1:ny2, nx1:nx2, :3].astype(np.float32)
        luma = (crop[..., 0] * 0.299 + crop[..., 1] * 0.587 + crop[..., 2] * 0.114)
        red_here = red_mask(original[ny1:ny2, nx1:nx2])
        alpha = np.clip((luma - 62.0) / 118.0, 0.0, 1.0)
        alpha *= (~red_here).astype(np.float32)
        alpha = alpha[..., None]
        target = changed[ny1:ny2, nx1:nx2, :3]
        target[:] = target * (1.0 - alpha) + crop * alpha
        changed[ny1:ny2, nx1:nx2, :3] = target
        base = Image.fromarray(np.clip(changed, 0, 255).astype(np.uint8), "RGB")
    return base


def image_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def badgefix_path(old_path: Path, content: bytes) -> Path:
    stem = re.sub(r"-badgefix-[0-9a-f]{10}$", "", old_path.stem)
    digest = hashlib.sha256(content).hexdigest()[:10]
    return old_path.with_name(f"{stem}-badgefix-{digest}.png")


def replacement_pairs(old_path: Path, new_path: Path) -> list[tuple[str, str]]:
    old_rel = "/" + old_path.relative_to(ROOT).as_posix()
    new_rel = "/" + new_path.relative_to(ROOT).as_posix()
    return [
        (f"{SITE}{old_rel}", f"{SITE}{new_rel}"),
        (old_rel, new_rel),
        (old_rel.lstrip("/"), new_rel.lstrip("/")),
    ]


def public_text_files() -> Iterable[Path]:
    yield ROOT / "index.html"
    for path in sorted(ARTICLES_DIR.glob("*.html")):
        yield path
    for name in ("rss.xml", "sitemap.xml", "news-sitemap.xml", "llms.txt"):
        path = ROOT / name
        if path.exists():
            yield path


def apply_replacements(replacements: list[tuple[str, str]]) -> list[str]:
    changed: list[str] = []
    if not replacements:
        return changed
    for path in public_text_files():
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        updated = original
        for old, new in replacements:
            updated = updated.replace(old, new)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(path.relative_to(ROOT).as_posix())
    return changed


def patch_generator(write: bool) -> bool:
    if not GENERATOR.is_file():
        return False
    original = GENERATOR.read_text(encoding="utf-8")
    if MARKER in original:
        return False

    helper = r'''

# SOCIAL-BADGE-FIT-V1
# Každý textový štítek měří skutečný text, zmenší písmo a ponechá bezpečný okraj.
def draw_fitted_badge(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    *,
    max_width: int = 535,
    fill: tuple[int, int, int, int] = (177, 36, 47, 255),
    max_font_size: int = 23,
    min_font_size: int = 14,
    pad_x: int = 18,
    pad_y: int = 8,
) -> tuple[int, int, int, int]:
    display = " ".join(text.split())
    selected = font(min_font_size, bold=True)
    bbox = draw.textbbox((0, 0), display, font=selected)
    for size in range(max_font_size, min_font_size - 1, -1):
        candidate = font(size, bold=True)
        candidate_bbox = draw.textbbox((0, 0), display, font=candidate)
        if candidate_bbox[2] - candidate_bbox[0] <= max_width - 2 * pad_x:
            selected = candidate
            bbox = candidate_bbox
            break
    while display and bbox[2] - bbox[0] > max_width - 2 * pad_x:
        display = display[:-2].rstrip() + "…"
        bbox = draw.textbbox((0, 0), display, font=selected)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    box_width = min(max_width, text_width + 2 * pad_x)
    box_height = max(45, text_height + 2 * pad_y)
    draw.rounded_rectangle((x, y, x + box_width, y + box_height), radius=9, fill=fill)
    text_x = x + (box_width - text_width) / 2 - bbox[0]
    text_y = y + (box_height - text_height) / 2 - bbox[1]
    draw.text((text_x, text_y), display, font=selected, fill="white")
    return (x, y, x + box_width, y + box_height)
'''
    if "\ndef create_card(" not in original:
        raise RuntimeError("Generátor neobsahuje funkci create_card.")
    updated = original.replace("\ndef create_card(", helper + "\n\ndef create_card(", 1)

    old_block = '''    category_font = font(23, bold=True)\n    category_width = min(535, draw.textbbox((0, 0), category, font=category_font)[2] + 38)\n    draw.rounded_rectangle((70, 130, 70 + category_width, 175), radius=9, fill=(177, 36, 47, 255))\n    draw.text((88, 139), category, font=category_font, fill="white")'''
    new_block = '''    draw_fitted_badge(\n        draw,\n        70,\n        130,\n        category,\n        max_width=535,\n        fill=(177, 36, 47, 255),\n    )'''
    if old_block not in updated:
        raise RuntimeError("Nenalezen původní pevný blok červeného štítku v generátoru.")
    updated = updated.replace(old_block, new_block, 1)
    if write:
        GENERATOR.write_text(updated, encoding="utf-8", newline="\n")
    return True


def run(write: bool, patch: bool, report_path: Path) -> tuple[dict, int]:
    generator_changed = patch_generator(write) if patch else False
    index = article_image_index()
    results: list[ImageResult] = []
    replacements: list[tuple[str, str]] = []
    bad_before = 0

    for image_path, articles in sorted(index.items(), key=lambda item: item[0].as_posix()):
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as exc:  # noqa: BLE001
            results.append(
                ImageResult(
                    image=image_path.relative_to(ROOT).as_posix(),
                    articles=[path.relative_to(ROOT).as_posix() for path in articles],
                    badges=[],
                    changed=False,
                    new_image=f"CHYBA: {exc}",
                )
            )
            bad_before += 1
            continue

        findings = detect_badges(image, image_path.relative_to(ROOT).as_posix(), len(articles))
        bad = [finding for finding in findings if finding.needs_fix]
        bad_before += len(bad)
        result = ImageResult(
            image=image_path.relative_to(ROOT).as_posix(),
            articles=[path.relative_to(ROOT).as_posix() for path in articles],
            badges=findings,
        )
        if bad and write:
            normalized = normalize_image(image, findings)
            # Druhá kontrola musí potvrdit bezpečné okraje.
            after = detect_badges(normalized, image_path.name, len(articles))
            remaining = [finding for finding in after if finding.needs_fix]
            if remaining:
                # Je-li detektor kvůli antialiasingu stále přísný, přidá ještě jednu rezervu.
                normalized = normalize_image(normalized, after)
                after = detect_badges(normalized, image_path.name, len(articles))
                remaining = [finding for finding in after if finding.needs_fix]
            if remaining:
                raise RuntimeError(f"Po opravě stále nesedí štítek v {image_path}: {remaining}")
            content = image_bytes(normalized)
            new_path = badgefix_path(image_path, content)
            new_path.parent.mkdir(parents=True, exist_ok=True)
            new_path.write_bytes(content)
            replacements.extend(replacement_pairs(image_path, new_path))
            result.changed = True
            result.new_image = new_path.relative_to(ROOT).as_posix()
            result.badges = after
        results.append(result)

    changed_text_files = apply_replacements(replacements) if write else []

    report = {
        "version": 1,
        "generatorMarker": MARKER,
        "generatorChanged": generator_changed,
        "imagesScanned": len(index),
        "badgesFound": sum(len(result.badges) for result in results),
        "issuesBefore": bad_before,
        "imagesChanged": sum(1 for result in results if result.changed),
        "changedTextFiles": changed_text_files,
        "results": [
            {
                **asdict(result),
                "badges": [asdict(badge) for badge in result.badges],
            }
            for result in results
        ],
    }
    if write or report_path.exists():
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    issues_after = 0
    # Kontrola odkazovaných výsledných obrázků po přepsání metadat.
    final_index = article_image_index()
    for image_path, articles in final_index.items():
        image = Image.open(image_path).convert("RGB")
        issues_after += sum(
            finding.needs_fix
            for finding in detect_badges(image, image_path.relative_to(ROOT).as_posix(), len(articles))
        )
    report["issuesAfter"] = int(issues_after)
    if write:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report, int(issues_after)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="opravit obrázky a přepsat odkazy")
    parser.add_argument("--check", action="store_true", help="vrátit chybu, pokud některý štítek nesedí")
    parser.add_argument("--patch-generator", action="store_true", help="opravit hlavní generátor")
    parser.add_argument("--report", type=Path, default=REPORT_DEFAULT)
    args = parser.parse_args()
    if not args.write and not args.check:
        args.check = True

    report, issues_after = run(args.write, args.patch_generator, args.report)
    print(
        "Sociální štítky: "
        f"obrázky {report['imagesScanned']}, nalezené štítky {report['badgesFound']}, "
        f"před opravou {report['issuesBefore']}, změněné obrázky {report['imagesChanged']}, "
        f"po opravě {issues_after}."
    )
    if args.check and issues_after:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
