#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publish_mestska_policie_20260807 as mp
import publish_mestska_policie_20260807_rescue as rescue


def ensure_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    # Odstraň případné starší duplikáty cílové položky a vlož přesně jednu kanonickou položku.
    pattern = re.compile(
        r"\s*<url><loc>" + re.escape(mp.URL) + r"</loc>(?:<lastmod>[^<]+</lastmod>)?</url>\s*",
        re.I,
    )
    text = pattern.sub("\n", text)
    entry = f"  <url><loc>{mp.URL}</loc><lastmod>{mp.PUBLISHED_DATE}</lastmod></url>\n"
    marker = "  <url><loc>https://nasekadan.cz/clanky/</loc></url>\n"
    if marker in text:
        text = text.replace(marker, marker + entry, 1)
    elif "<urlset" in text:
        pos = text.find("\n", text.find("<urlset"))
        text = text[:pos + 1] + entry + text[pos + 1:]
    else:
        raise RuntimeError("sitemap.xml nemá očekávaný urlset.")
    path.write_text(text, encoding="utf-8", newline="\n")
    if text.count(mp.URL) != 1:
        raise RuntimeError(f"Cílová URL je v sitemapě {text.count(mp.URL)}× místo 1×.")


def main() -> int:
    mp.make_article()
    rescue.generate_social()
    rescue.patch_article_social()
    mp.upsert_registry()
    mp.rebuild_surfaces_and_manifest()
    mp.upsert_registry()
    ensure_sitemap()
    mp.validate()
    rescue.assert_article()
    print(json.dumps({
        "status": "prepared",
        "article": mp.URL,
        "social": rescue.SOCIAL_URL,
        "sitemap_occurrences": (ROOT / "sitemap.xml").read_text(encoding="utf-8").count(mp.URL),
        "source_commit": os.environ.get("ARTICLE_SOURCE_COMMIT"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
