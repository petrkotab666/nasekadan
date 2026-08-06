#!/usr/bin/env python3
"""Spustí plný SEO audit a správně odliší stránky archivu od článků."""
from __future__ import annotations

import re

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


audit.audit_page = _audit_page

if __name__ == "__main__":
    raise SystemExit(audit.main())
