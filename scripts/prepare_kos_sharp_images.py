#!/usr/bin/env python3
"""Build sharp, browser-safe WebP evidence images for the bin-collection article."""

from __future__ import annotations

import base64
import html
import re
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / ".github" / "kos-sharp-assets"
IMAGES = ROOT / "images" / "clanky"
ARTICLE = ROOT / "clanky" / "pretekajici-kose-kadan-technicke-sluzby-ridici.html"

PHOTO_ID = "10243275472011444"
PHOTO_URL = (
    "https://www.facebook.com/photo?fbid=10243275472011444"
    "&set=gm.1557730802517994&idorvanity=442280287396390"
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/126 Safari/537.36"
)


def rebuild_webp(prefix: str, target: Path) -> None:
    parts = sorted(CHUNKS.glob(f"{prefix}-*.txt"))
    if not parts:
        raise RuntimeError(f"Chybí datové části pro {prefix}")
    encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
    target.write_bytes(base64.b64decode(encoded, validate=True))
    with Image.open(target) as image:
        image.verify()
    if target.stat().st_size < 5_000:
        raise RuntimeError(f"Výsledný obrázek {target} je podezřele malý")


def download(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read(), response.headers.get("Content-Type", "")


def load_main_photo() -> bytes:
    for url in (
        f"https://graph.facebook.com/{PHOTO_ID}/picture?type=large&redirect=true",
        f"https://graph.facebook.com/{PHOTO_ID}/picture?redirect=true",
    ):
        try:
            body, content_type = download(url)
            if content_type.lower().startswith("image/") and len(body) > 5_000:
                return body
        except Exception as exc:  # Facebook occasionally blocks automated requests.
            print(f"Facebook image endpoint failed: {url}: {exc}")

    try:
        page, _ = download(PHOTO_URL)
        text = page.decode("utf-8", "ignore")
        match = (
            re.search(
                r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
                text,
                re.I,
            )
            or re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                text,
                re.I,
            )
        )
        if match:
            candidate = html.unescape(match.group(1)).replace("\\/", "/")
            body, content_type = download(candidate)
            if content_type.lower().startswith("image/") and len(body) > 5_000:
                return body
    except Exception as exc:
        print(f"Facebook OG image fallback failed: {exc}")

    fallback = IMAGES / "kadan-pretekajici-kos-facebook-real.svg"
    svg = fallback.read_text(encoding="utf-8")
    match = re.search(
        r'data:image/(?:jpeg|jpg|png);base64,([^"\']+)',
        svg,
        re.I,
    )
    if not match:
        raise RuntimeError("Nelze načíst ani záložní fotografii ze SVG")
    return base64.b64decode(match.group(1))


def build_main_photo(target: Path) -> None:
    with Image.open(BytesIO(load_main_photo())) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image = ImageOps.fit(
            image,
            (720, 1277),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
        image = image.filter(
            ImageFilter.UnsharpMask(radius=1.15, percent=125, threshold=2)
        )
        image.save(target, "WEBP", quality=88, method=6)


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    replacements = {
        "../images/clanky/kadan-pretekajici-kos-facebook-real.svg": "../images/clanky/kadan-pretekajici-kos-facebook-ostry.webp",
        "../images/clanky/kadan-forum-petra-pokorna-prispevek-real.svg": "../images/clanky/kadan-forum-petra-pokorna-prispevek-ostry.webp",
        "../images/clanky/jan-losenicky-komentar-facebook-real.svg": "../images/clanky/jan-losenicky-komentar-facebook-ostry.webp",
        'width="220" height="390" loading="eager"': 'width="720" height="1277" loading="eager"',
        'width="320" height="290" loading="lazy"': 'width="525" height="475" loading="lazy"',
        'width="360" height="130" loading="lazy"': 'width="620" height="391" loading="lazy"',
        'data-fb-photo-evidence="v2"': 'data-fb-photo-evidence="v3-sharp"',
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise RuntimeError(f"V článku chybí očekávaný obrazový odkaz: {old}")
    ARTICLE.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    rebuild_webp(
        "post", IMAGES / "kadan-forum-petra-pokorna-prispevek-ostry.webp"
    )
    rebuild_webp(
        "jan", IMAGES / "jan-losenicky-komentar-facebook-ostry.webp"
    )
    build_main_photo(IMAGES / "kadan-pretekajici-kos-facebook-ostry.webp")
    update_article()
    print("Sharp bin-article images prepared.")


if __name__ == "__main__":
    main()
