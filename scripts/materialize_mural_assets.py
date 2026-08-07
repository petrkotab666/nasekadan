#!/usr/bin/env python3
from __future__ import annotations

import base64
from io import BytesIO
import json
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "images/clanky/od-hlubin-k-nebi/ptaci-ara-zoborozec.webp": "6d90d5c3aa5caf7bcd58d80371289eb94ab162e5",
    "images/clanky/od-hlubin-k-nebi/ptaci-cela-stena.webp": "14a97e9acb273f50fa3cd7621a73254a8b27dfe7",
}
API = "https://api.github.com/repos/petrkotab666/nasekadan/git/blobs/{}"


def valid_webp(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 10_000:
        return False
    data = path.read_bytes()[:12]
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return False
    try:
        with Image.open(path) as image:
            return image.format == "WEBP" and image.width >= 800 and image.height >= 600
    except Exception:
        return False


def fetch_blob(sha: str) -> bytes:
    req = urllib.request.Request(
        API.format(sha),
        headers={"Accept": "application/vnd.github+json", "User-Agent": "nasekadan-build"},
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        payload = json.load(response)
    if payload.get("encoding") != "base64" or not payload.get("content"):
        raise RuntimeError(f"GitHub blob {sha} neobsahuje Base64 data")
    return base64.b64decode(payload["content"])


def materialize_webp(target: Path, source: bytes, relative: str) -> None:
    try:
        with Image.open(BytesIO(source)) as image:
            image.load()
            if image.width < 800 or image.height < 600:
                raise RuntimeError(
                    f"Zdroj muralu má příliš malé rozměry {image.width}x{image.height}: {relative}"
                )
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGB")
            elif image.mode == "RGBA":
                background = Image.new("RGB", image.size, "white")
                background.paste(image, mask=image.getchannel("A"))
                image = background
            image.save(target, format="WEBP", quality=92, method=6)
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise RuntimeError(f"Zdroj muralu nelze převést na WebP: {relative}: {exc}") from exc


def main() -> None:
    for relative, sha in TARGETS.items():
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if valid_webp(target):
            print(f"Mural WebP ověřen: {relative}")
            continue
        source = fetch_blob(sha)
        materialize_webp(target, source, relative)
        if not valid_webp(target):
            target.unlink(missing_ok=True)
            raise RuntimeError(f"Mural asset po převodu není platný WebP: {relative}")
        print(f"Mural WebP převeden z trvalého zdrojového blobu a ověřen: {relative}")


if __name__ == "__main__":
    main()
