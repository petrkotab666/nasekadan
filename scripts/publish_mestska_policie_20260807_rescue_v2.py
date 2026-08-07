#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publish_mestska_policie_20260807 as mp
import publish_mestska_policie_20260807_rescue as rescue

REPAIR_TEMPLATE = ROOT / 'scripts' / 'repair_mestska_policie_template_20260807.py'


def ensure_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
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


def normalize_generated_whitespace() -> None:
    paths = [ROOT / "index.html", ROOT / "clanky" / "index.html"]
    paths.extend(sorted((ROOT / "clanky").glob("strana-*.html")))
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        clean = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
        path.write_text(clean, encoding="utf-8", newline="\n")


def assert_template() -> None:
    text = mp.ARTICLE.read_text(encoding='utf-8')
    required = [
        'data-article-template="unified-v1"',
        '<link rel="stylesheet" href="/style.css">',
        '<meta name="theme-color" content="#9f2626">',
        '<a class="logo" href="/"',
        '← Zpět na titulní stranu',
        'class="hero-image"',
        'src="/social/mestska-policie-kadan-fakta-diskuse-2026.png"',
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError('Článek nemá jednotnou šablonu: ' + repr(missing))


def main() -> int:
    mp.make_article()
    rescue.generate_social()
    rescue.patch_article_social()
    if not REPAIR_TEMPLATE.is_file():
        raise RuntimeError('Chybí skript pro sjednocení šablony Městské policie.')
    subprocess.run([sys.executable, str(REPAIR_TEMPLATE)], cwd=ROOT, check=True)
    mp.upsert_registry()
    mp.rebuild_surfaces_and_manifest()
    mp.upsert_registry()
    ensure_sitemap()
    normalize_generated_whitespace()
    mp.validate()
    rescue.assert_article()
    assert_template()
    print(json.dumps({
        "status": "prepared",
        "article": mp.URL,
        "social": rescue.SOCIAL_URL,
        "sitemap_occurrences": (ROOT / "sitemap.xml").read_text(encoding="utf-8").count(mp.URL),
        "template": "unified-v1",
        "source_commit": os.environ.get("ARTICLE_SOURCE_COMMIT"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
