#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

import publish_novy_hrbitov_kadan_20260808 as base


def ensure_article_sitemap() -> None:
    path = base.ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if base.URL not in text:
        base.write(
            path,
            text.replace(
                "</urlset>",
                f"  <url><loc>{base.URL}</loc><lastmod>2026-08-08</lastmod></url>\n</urlset>",
            ),
        )


def main() -> int:
    base.make_social()
    base.write(base.ARTICLE, base.article_html())

    sys.path.insert(0, str(base.ROOT / "scripts"))
    import publish_gymnastika_kadan_20260806 as helper

    helper.rebuild_surfaces()
    ensure_article_sitemap()
    helper.rebuild_integrity_manifest()
    base.upsert_registry()

    subprocess.run(
        [sys.executable, str(base.ROOT / "scripts/normalize_footers.py"), "--write", "--check"],
        cwd=base.ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(base.ROOT / "scripts/normalize_articles.py"), "--write", "--check"],
        cwd=base.ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(base.ROOT / "scripts/sort_articles_chronologically.py")],
        cwd=base.ROOT,
        check=True,
    )
    base.validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
