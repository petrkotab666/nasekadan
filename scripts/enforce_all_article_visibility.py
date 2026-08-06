#!/usr/bin/env python3
"""Jednorázový publikační most pro článek o Apoleně Švábíkové.

Po úspěšné veřejné publikaci bootstrap tento soubor automaticky vrátí na
kanonickou verzi z commitu 70dd13c09d6d96927d8cb4db3324a76d548c13c9.
"""
from __future__ import annotations

from pathlib import Path
import runpy
import subprocess

from apolena_bootstrap_runtime import run_bootstrap

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_COMMIT = "70dd13c09d6d96927d8cb4db3324a76d548c13c9"


def main() -> None:
    run_bootstrap()
    runtime_copy = ROOT / "scripts" / ".enforce_all_article_visibility_original_runtime.py"
    original = subprocess.check_output(
        ["git", "show", f"{ORIGINAL_COMMIT}:scripts/enforce_all_article_visibility.py"],
        cwd=ROOT,
    )
    runtime_copy.write_bytes(original)
    runpy.run_path(str(runtime_copy), run_name="__main__")


if __name__ == "__main__":
    main()
