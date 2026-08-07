#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path

SITE = "https://nasekadan.cz"
WIDTH = 1200
HEIGHT = 630


def meta_content(text: str, key: str, *, prop: bool = True) -> str:
    attr = "property" if prop else "name"
    m = re.search(
        rf'<meta\b[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*content=["\']([^"\']*)["\'][^>]*>',
        text,
        re.I,
    )
    return html.unescape(m.group(1)).strip() if m else ""


def replace_meta(text: str, key: str, value: str, *, prop: bool = True) -> str:
    attr = "property" if prop else "name"
    pattern = re.compile(rf'<meta\b[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*>', re.I)
    tag = f'<meta {attr}="{key}" content="{html.escape(value, quote=True)}">'
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    end = re.search(r'</head>', text, re.I)
    if not end:
        raise RuntimeError("HTML nemá </head>")
    return text[:end.start()] + tag + "\n" + text[end.start():]


def png_dimensions(path: Path) -> tuple[int, int]:
    head = path.read_bytes()[:24]
    if len(head) < 24 or not head.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"{path} není platný PNG")
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def process(path: Path, *, write: bool) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "NewsArticle" not in text or "article-shell" not in text:
        return False, []
    image = meta_content(text, "og:image")
    if not image.startswith(SITE + "/social/"):
        return False, [f"{path}: og:image není lokální social karta"]
    clean = image.split("?", 1)[0]
    asset = Path(clean.removeprefix(SITE).lstrip("/"))
    if not asset.is_file() or asset.stat().st_size < 10_000:
        return False, [f"{path}: chybí sociální obrázek {asset}"]
    try:
        width, height = png_dimensions(asset)
    except RuntimeError as exc:
        return False, [str(exc)]
    if (width, height) != (WIDTH, HEIGHT):
        return False, [f"{path}: sociální obrázek má {width}x{height}, očekáváno 1200x630"]
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:16]
    versioned = f"{clean}?fb={digest}"
    new = text
    new = replace_meta(new, "og:image", versioned)
    new = replace_meta(new, "og:image:secure_url", versioned)
    new = replace_meta(new, "og:image:type", "image/png")
    new = replace_meta(new, "og:image:width", str(WIDTH))
    new = replace_meta(new, "og:image:height", str(HEIGHT))
    new = replace_meta(new, "twitter:image", versioned, prop=False)
    new = re.sub(
        r'"image"\s*:\s*\[\s*"[^"]+"\s*\]',
        f'"image":["{versioned}"]',
        new,
        count=1,
    )
    changed = new != text
    if changed and write:
        path.write_text(new, encoding="utf-8")
    return changed, []


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--paths", nargs="*")
    a = p.parse_args()
    paths = [Path(x) for x in a.paths] if a.paths else sorted(Path("clanky").glob("*.html"))
    changed = 0
    errors: list[str] = []
    for path in paths:
        did_change, errs = process(path, write=a.write)
        changed += int(did_change)
        errors.extend(errs)
    if errors:
        print("FACEBOOK META CHYBY:")
        for error in errors:
            print("-", error)
        return 1
    if a.check:
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            if "NewsArticle" not in text or "article-shell" not in text:
                continue
            image = meta_content(text, "og:image")
            secure = meta_content(text, "og:image:secure_url")
            if "?fb=" not in image or secure != image:
                print(f"- {path}: chybí verzované og:image/secure_url")
                return 1
    print(f"Facebook metadata OK; změněno {changed} článků.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
