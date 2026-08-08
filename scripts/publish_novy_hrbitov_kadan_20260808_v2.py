#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET

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


def validate_fixed() -> None:
    text = base.ARTICLE.read_text(encoding="utf-8")
    surfaces = {
        "homepage": (base.ROOT / "index.html").read_text(encoding="utf-8"),
        "archive": (base.ROOT / "clanky/index.html").read_text(encoding="utf-8"),
        "rss": (base.ROOT / "rss.xml").read_text(encoding="utf-8"),
        "sitemap": (base.ROOT / "sitemap.xml").read_text(encoding="utf-8"),
        "news": (base.ROOT / "news-sitemap.xml").read_text(encoding="utf-8"),
        "llms": (base.ROOT / "llms.txt").read_text(encoding="utf-8"),
        "registry": (base.ROOT / "data/published-content-index.json").read_text(encoding="utf-8"),
        "manifest": (base.ROOT / "data/article-integrity-manifest.json").read_text(encoding="utf-8"),
    }
    checks = {
        "h1": text.count(f"<h1>{base.TITLE}</h1>") == 1,
        "indexable": "noindex" not in text.lower(),
        "canonical": f'<link rel="canonical" href="{base.URL}">' in text,
        "social": base.SOCIAL.is_file(),
        "homepage": base.ARTICLE_REL in surfaces["homepage"],
        "archive": base.ARTICLE_REL in surfaces["archive"],
        "rss": base.URL in surfaces["rss"],
        "sitemap": base.URL in surfaces["sitemap"],
        "news": base.URL in surfaces["news"],
        "llms": base.ARTICLE_REL in surfaces["llms"],
        "registry": base.URL in surfaces["registry"],
        "manifest": base.URL in surfaces["manifest"],
    }
    from PIL import Image
    with Image.open(base.SOCIAL) as im:
        checks["social_dimensions"] = im.size == (1200, 630)
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("Neúplná zdrojová publikace: " + ", ".join(failed))
    ET.parse(base.ROOT / "rss.xml")
    ET.parse(base.ROOT / "sitemap.xml")
    ET.parse(base.ROOT / "news-sitemap.xml")
    print("Zdrojová publikace nového hřbitova je kompletní.")


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
    validate_fixed()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
