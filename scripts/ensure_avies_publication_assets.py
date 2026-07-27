#!/usr/bin/env python3
from __future__ import annotations

import binascii
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "avies-nemocnice-kadan.html"
SITEMAP = ROOT / "sitemap.xml"
RSS = ROOT / "rss.xml"
IMAGE = ROOT / "social" / "avies-nemocnice-kadan-20260727.png"
URL = "https://nasekadan.cz/clanky/avies-nemocnice-kadan.html"
IMAGE_URL = "https://nasekadan.cz/social/avies-nemocnice-kadan-20260727.png"
TITLE = "Kdo nastavil nákupy léčiv od AVIES? Nemocnice za sedm let zaplatila téměř 170 milionů"
DESCRIPTION = (
    "Nemocnice Kadaň zaplatila AVIES v letech 2019 až 2025 téměř 170 milionů korun. "
    "Rekonstruujeme historii vztahu a hledáme chybějící dokument pro rok 2024."
)


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def ensure_png() -> None:
    if IMAGE.is_file() and IMAGE.stat().st_size >= 10_000:
        return
    IMAGE.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1200, 630
    rows: list[bytes] = []
    seed = 0xA71E5
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            # Tmavý červeno-modrý přechod s jemnou deterministickou texturou.
            seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
            noise = (seed >> 24) & 0x0F
            t = x / max(1, width - 1)
            v = y / max(1, height - 1)
            r = int(18 + 125 * t + 25 * v + noise)
            g = int(31 + 28 * t + 20 * (1 - v) + noise // 2)
            b = int(40 + 42 * (1 - t) + 18 * (1 - v) + noise // 3)
            # Světlý informační pás a grafické bloky připomínající titulní kartu.
            if 70 < y < 105:
                r, g, b = 210 + noise, 166 + noise // 2, 91
            if 120 < y < 490 and 90 < x < 1030 and ((x // 32 + y // 24) % 17 == 0):
                r, g, b = min(255, r + 28), min(255, g + 22), min(255, b + 18)
            if 510 < y < 555 and 90 < x < 760:
                r, g, b = 245 - noise, 239 - noise // 2, 222
            row.extend((max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
        rows.append(bytes(row))
    raw = b"".join(rows)
    payload = b"\x89PNG\r\n\x1a\n"
    payload += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += png_chunk(b"IDAT", zlib.compress(raw, level=8))
    payload += png_chunk(b"IEND", b"")
    IMAGE.write_bytes(payload)
    if IMAGE.stat().st_size < 10_000:
        raise RuntimeError("Vygenerovaný AVIES obrázek je příliš malý.")


def set_meta(text: str, attr: str, key: str, value: str) -> str:
    pattern = rf'<meta\s+[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*>'
    replacement = f'<meta {attr}="{key}" content="{value}">'
    if re.search(pattern, text, flags=re.I):
        return re.sub(pattern, replacement, text, count=1, flags=re.I)
    return text.replace("</head>", replacement + "\n</head>", 1)


def ensure_article_meta() -> None:
    if not ARTICLE.is_file():
        raise RuntimeError(f"Chybí {ARTICLE.relative_to(ROOT)}")
    text = ARTICLE.read_text(encoding="utf-8")
    for attr, key, value in (
        ("property", "og:locale", "cs_CZ"),
        ("property", "og:type", "article"),
        ("property", "og:site_name", "Naše Kadaň"),
        ("property", "og:title", TITLE),
        ("property", "og:description", DESCRIPTION),
        ("property", "og:url", URL),
        ("property", "og:image", IMAGE_URL),
        ("property", "og:image:type", "image/png"),
        ("property", "og:image:width", "1200"),
        ("property", "og:image:height", "630"),
        ("property", "og:image:alt", "AVIES a Nemocnice Kadaň – téměř 170 milionů korun za sedm let"),
        ("name", "twitter:card", "summary_large_image"),
        ("name", "twitter:title", TITLE),
        ("name", "twitter:description", DESCRIPTION),
        ("name", "twitter:image", IMAGE_URL),
    ):
        text = set_meta(text, attr, key, value)
    ARTICLE.write_text(text, encoding="utf-8", newline="\n")


def ensure_sitemap() -> None:
    if not SITEMAP.is_file():
        raise RuntimeError("Chybí sitemap.xml")
    text = SITEMAP.read_text(encoding="utf-8")
    if URL not in text:
        if "</urlset>" not in text:
            raise RuntimeError("sitemap.xml nemá ukončovací značku urlset")
        entry = f"  <url><loc>{URL}</loc><lastmod>2026-07-27</lastmod></url>\n"
        text = text.replace("</urlset>", entry + "</urlset>", 1)
        SITEMAP.write_text(text, encoding="utf-8", newline="\n")


def ensure_rss_image() -> None:
    if not RSS.is_file():
        raise RuntimeError("Chybí rss.xml")
    text = RSS.read_text(encoding="utf-8")
    pattern = rf'(<item>(?:(?!</item>).)*?{re.escape(URL)}(?:(?!</item>).)*?</item>)'
    match = re.search(pattern, text, flags=re.S)
    if not match:
        return
    item = match.group(1)
    image_tag = f"<szn:image><szn:url>{IMAGE_URL}</szn:url></szn:image>"
    if "<szn:image>" in item:
        item = re.sub(r"<szn:image>.*?</szn:image>", image_tag, item, count=1, flags=re.S)
    else:
        item = item.replace("</item>", f"      {image_tag}\n    </item>", 1)
    text = text[: match.start()] + item + text[match.end() :]
    RSS.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    ensure_png()
    ensure_article_meta()
    ensure_sitemap()
    ensure_rss_image()
    print(f"AVIES připraven pro web i Facebook: {IMAGE.relative_to(ROOT)} ({IMAGE.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
