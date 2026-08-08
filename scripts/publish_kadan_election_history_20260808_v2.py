#!/usr/bin/env python3
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publish_kadan_election_history_20260808 as pub
import publish_gymnastika_kadan_20260806 as helper


def loc_count(path: Path) -> int:
    """Počítá cílovou URL strukturálně, bez závislosti na XML prefixu/formatování."""
    root = ET.parse(path).getroot()
    count = 0
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "loc":
            continue
        value = (node.text or "").strip().rstrip("/")
        if value == pub.URL.rstrip("/") or value.endswith("/" + pub.ARTICLE_REL):
            count += 1
    return count


def validate_v2() -> None:
    # Původní generátor sestaví manifest před normalizací konstrukce článků.
    # Obnova tady garantuje, že hash/bytes v manifestu odpovídají skutečně
    # finální podobě souborů, která půjde do commitu a na produkci.
    helper.rebuild_integrity_manifest()

    text = pub.ARTICLE.read_text(encoding="utf-8")
    for heading in pub.REQUIRED_HEADINGS:
        if f">{heading}</h2>" not in text:
            raise RuntimeError(f"Po transformaci chybí kapitola: {heading}")
    rss = (ROOT / "rss.xml").read_text(encoding="utf-8")
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
        "sitemap_loc_once": loc_count(ROOT / "sitemap.xml") == 1,
        "news_loc_once": loc_count(ROOT / "news-sitemap.xml") == 1,
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
