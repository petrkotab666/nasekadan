#!/usr/bin/env python3
"""Spustí finální sociální a SEO audit produkčního obrazu."""
from __future__ import annotations

import re
import subprocess
import sys

import seo_ai_audit as audit

_original_audit_page = audit.audit_page


def _audit_page(path, findings):
    is_paginated_archive = (
        path.parent == audit.ARTICLE_DIR
        and bool(re.fullmatch(r"strana-\d+\.html", path.name))
    )
    if not is_paginated_archive:
        return _original_audit_page(path, findings)

    original_article_dir = audit.ARTICLE_DIR
    try:
        audit.ARTICLE_DIR = audit.ROOT / "__not_an_article_directory__"
        return _original_audit_page(path, findings)
    finally:
        audit.ARTICLE_DIR = original_article_dir


def verify_social_previews() -> None:
    # Běží až v produkčním Docker buildu, kde je Pillow povinně nainstalované.
    # Každý článek musí mít fyzicky přítomnou lokální 1200x630 kartu a kompletní
    # OG/Twitter metadata; jinak se obraz vůbec nesestaví.
    subprocess.run(
        [sys.executable, str(audit.ROOT / "scripts" / "normalize_social_preview.py"), "--write", "--check"],
        cwd=audit.ROOT,
        check=True,
    )


audit.audit_page = _audit_page

if __name__ == "__main__":
    verify_social_previews()
    raise SystemExit(audit.main())
