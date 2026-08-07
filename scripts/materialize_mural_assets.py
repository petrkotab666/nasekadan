#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "images/clanky/od-hlubin-k-nebi/ptaci-ara-zoborozec.webp": "725c1c09724df0a7a64b5e8ed4f9a8c69ab68c39",
    "images/clanky/od-hlubin-k-nebi/ptaci-cela-stena.webp": "3896d0f5b341af7b03d5d3c246c82b800eba2ee6",
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


def main() -> None:
    for relative, sha in TARGETS.items():
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if valid_webp(target):
            print(f"Mural WebP ověřen: {relative}")
            continue
        target.write_bytes(fetch_blob(sha))
        if not valid_webp(target):
            target.unlink(missing_ok=True)
            raise RuntimeError(f"Mural asset není platný WebP: {relative}")
        print(f"Mural WebP materializován a ověřen: {relative}")


if __name__ == "__main__":
    main()
