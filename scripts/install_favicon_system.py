#!/usr/bin/env python3
"""Nainstaluje trvalé sjednocování favicon do publikačního procesu."""

from __future__ import annotations

from pathlib import Path
import re

from ensure_favicon import normalize_all

ROOT = Path(__file__).resolve().parents[1]
FINALIZER = ROOT / "scripts" / "finalize_launch.py"


def patch_finalizer() -> bool:
    text = FINALIZER.read_text(encoding="utf-8")
    original = text

    import_marker = "import sys\n"
    favicon_import = "from ensure_favicon import normalize_favicon_html\n"
    if favicon_import not in text:
        if import_marker not in text:
            raise RuntimeError("Ve finalize_launch.py chybí import sys.")
        text = text.replace(import_marker, import_marker + favicon_import, 1)

    process_marker = "    text = ensure_head_meta(text, path)\n"
    favicon_call = "    text = normalize_favicon_html(text)\n"
    if favicon_call not in text:
        if process_marker not in text:
            raise RuntimeError("Ve finalize_launch.py chybí ensure_head_meta marker.")
        text = text.replace(process_marker, process_marker + favicon_call, 1)

    analytics_write = re.compile(
        r"\n\s*\(ROOT / \"analytics\.js\"\)\.write_text\(\n"
        r"\s*\"\"\".*?\"\"\",\n"
        r"\s*encoding=\"utf-8\",\n"
        r"\s*\)\n",
        re.DOTALL,
    )
    text, count = analytics_write.subn("\n", text, count=1)
    if count == 0 and "(ROOT / \"analytics.js\").write_text" in text:
        raise RuntimeError("Nepodařilo se odstranit přepisování analytics.js.")

    if text != original:
        FINALIZER.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> int:
    finalizer_changed = patch_finalizer()
    changed, checked = normalize_all()
    print(
        f"Favicon systém nainstalován: finalizer_changed={finalizer_changed}, "
        f"HTML změněno={changed}, zkontrolováno={checked}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
