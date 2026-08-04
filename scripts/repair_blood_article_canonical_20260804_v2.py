#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

import repair_blood_article_canonical_20260804 as repair


def ensure_sitemap() -> None:
    path = repair.ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if repair.URL not in text:
        node = (
            f"  <url><loc>{repair.URL}</loc><lastmod>2026-08-04</lastmod>"
            "<changefreq>daily</changefreq><priority>0.9</priority></url>\n"
        )
        text = text.replace("</urlset>", node + "</urlset>", 1)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    repair.validate_article()
    repair.update_rss()
    repair.update_news_sitemap()
    repair.update_llms()
    repair.update_registry()
    subprocess.run(["python3", "scripts/enforce_article_visibility.py"], cwd=repair.ROOT, check=True)
    ensure_sitemap()
    repair.update_audit_status()
    repair.validate_repo_surfaces()
    print(f"Připraveno: 47 článků, doplněn {repair.URL}, source commit {repair.source_commit()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
