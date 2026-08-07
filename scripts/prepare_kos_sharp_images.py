#!/usr/bin/env python3
"""Run the historical sharp-image builder and materialize current mural WebP assets."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)


def main() -> None:
    run("prepare_kos_sharp_images_original.py")
    run("materialize_mural_assets.py")


if __name__ == "__main__":
    main()
