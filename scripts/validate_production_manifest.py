#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "production-content-manifest.json"


def validate(root: Path) -> list[str]:
    data = json.loads((root / MANIFEST.name).read_text(encoding="utf-8"))
    errors: list[str] = []

    home_path = root / "index.html"
    archive_path = root / "clanky" / "index.html"
    if not home_path.is_file():
        errors.append("chybí index.html")
        home = ""
    else:
        home = home_path.read_text(encoding="utf-8", errors="replace")
    if not archive_path.is_file():
        errors.append("chybí clanky/index.html")
        archive = ""
    else:
        archive = archive_path.read_text(encoding="utf-8", errors="replace")

    for asset in data["required_assets"]:
        if not (root / asset).is_file():
            errors.append(f"chybí povinný soubor {asset}")

    for item in data["required_articles"]:
        path = root / item["path"]
        href = "/" + item["path"]
        if not path.is_file():
            errors.append(f"chybí článek {item['path']}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if item["needle"] not in text:
            errors.append(f"článek {item['path']} neobsahuje kontrolní titulek")
        for token in data["required_article_tokens"]:
            if token not in text:
                errors.append(f"článek {item['path']} neobsahuje {token}")
        if item.get("must_be_on_home") and href not in home:
            errors.append(f"titulní stránka neodkazuje na {item['path']}")
        if item.get("must_be_in_archive") and href not in archive:
            errors.append(f"archiv neodkazuje na {item['path']}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = validate(root)
    if errors:
        print("Produkční pojistka selhala:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Produkční manifest je úplný: obsah, odkazy, reklamy i metadata jsou přítomné.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
