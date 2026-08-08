#!/usr/bin/env python3
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publish_kadan_election_history_20260808 as pub


def validate_v2() -> None:
    text = pub.ARTICLE.read_text(encoding="utf-8")
    for heading in pub.REQUIRED_HEADINGS:
        if f">{heading}</h2>" not in text:
            raise RuntimeError(f"Po transformaci chybí kapitola: {heading}")
    rss = (ROOT / "rss.xml").read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    news = (ROOT / "news-sitemap.xml").read_text(encoding="utf-8")
    checks = {
        "h1": text.count(f"<h1>{pub.TITLE}</h1>") == 1,
        "indexable": "noindex" not in text.lower(),
        "canonical": f'<link rel="canonical" href="{pub.URL}">' in text,
        "published": pub.PUBLISHED in text,
        "social": pub.SOCIAL.is_file(),
        "homepage": pub.ARTICLE_REL in (ROOT / "index.html").read_text(encoding="utf-8"),
        "archive": pub.ARTICLE_REL in (ROOT / "clanky/index.html").read_text(encoding="utf-8"),
        "rss_link_once": rss.count(f"<link>{pub.URL}</link>") == 1,
        "rss_guid_once": rss.count(f'<guid isPermaLink="true">{pub.URL}</guid>') == 1,
        "sitemap_loc_once": sitemap.count(f"<loc>{pub.URL}</loc>") == 1,
        "news_loc_once": news.count(f"<loc>{pub.URL}</loc>") == 1,
        "llms": pub.ARTICLE_REL in (ROOT / "llms.txt").read_text(encoding="utf-8"),
        "registry": pub.URL in (ROOT / "data/published-content-index.json").read_text(encoding="utf-8"),
        "manifest": pub.URL in (ROOT / "data/article-integrity-manifest.json").read_text(encoding="utf-8"),
    }
    from PIL import Image
    with Image.open(pub.SOCIAL) as im:
        checks["social_dimensions"] = im.size == (1200, 630) and im.format == "PNG"
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("Neúplná zdrojová publikace: " + ", ".join(failed))
    ET.parse(ROOT / "rss.xml")
    ET.parse(ROOT / "sitemap.xml")
    ET.parse(ROOT / "news-sitemap.xml")
    print(json.dumps({"status": "prepared", "url": pub.URL, "checks": checks, "required_headings": len(pub.REQUIRED_HEADINGS)}, ensure_ascii=False, indent=2))


pub.validate = validate_v2
raise SystemExit(pub.main())
