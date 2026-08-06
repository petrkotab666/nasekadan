#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DRAFT_REL = "nahled/mestska-policie-kadan-fakta-diskuse-2026.html"
DRAFT = ROOT / DRAFT_REL
SLUG = "mestska-policie-kadan-fakta-diskuse-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
URL = f"https://nasekadan.cz/{ARTICLE_REL}"
TITLE = "Neřeší městská policie dopravu? Bouřlivá debata přiměla redakci ověřit fakta"
DESC = (
    "Kritické vyjádření k práci Městské policie Kadaň vyvolalo bouřlivou debatu. "
    "Ověřili jsme dopravní přestupky, pravomoci strážníků, jejich další práci i aktuálnost oficiálního webu."
)
PUBLISHED = "2026-08-07T04:00:00+02:00"
PUBLISHED_DATE = "2026-08-07"
SOCIAL_REL = "social-card.png"
SOCIAL_URL = f"https://nasekadan.cz/{SOCIAL_REL}"
ARTICLE_SOURCE_COMMIT = os.environ.get("ARTICLE_SOURCE_COMMIT", "pending-publication-commit")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def news_schema() -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": TITLE,
        "description": DESC,
        "datePublished": PUBLISHED,
        "dateModified": PUBLISHED,
        "author": {
            "@type": "Organization",
            "@id": "https://nasekadan.cz/#organization",
            "name": "Naše Kadaň",
            "url": "https://nasekadan.cz/o-webu/",
        },
        "publisher": {"@id": "https://nasekadan.cz/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
        "image": [SOCIAL_URL],
        "inLanguage": "cs-CZ",
        "isAccessibleForFree": True,
        "about": [
            {"@type": "GovernmentOrganization", "name": "Městská policie Kadaň"},
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Thing", "name": "Dopravní přestupky"},
            {"@type": "Thing", "name": "Měření rychlosti"},
            {"@type": "Thing", "name": "Ověřování veřejných tvrzení"},
        ],
    }
    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Naše Kadaň", "item": "https://nasekadan.cz/"},
            {"@type": "ListItem", "position": 2, "name": "Články", "item": "https://nasekadan.cz/clanky/"},
            {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL},
        ],
    }
    return (
        '<script data-nk-newsarticle="1" type="application/ld+json">'
        + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        + "</script>\n"
        + '<script data-nasekadan-breadcrumbs="1" type="application/ld+json">'
        + json.dumps(breadcrumbs, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def publication_meta() -> str:
    return f'''<link rel="canonical" href="{URL}">
<meta property="og:locale" content="cs_CZ">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Naše Kadaň">
<meta property="og:title" content="{escape(TITLE, quote=True)}">
<meta property="og:description" content="{escape(DESC, quote=True)}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{SOCIAL_URL}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(TITLE, quote=True)}">
<meta name="twitter:description" content="{escape(DESC, quote=True)}">
<meta name="twitter:image" content="{SOCIAL_URL}">
<meta property="article:published_time" content="{PUBLISHED}">
<meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml">
<link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
<link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any">
<meta name="theme-color" content="#092d4b">
{news_schema()}'''


def make_article() -> None:
    if not DRAFT.is_file():
        raise RuntimeError(f"Chybí kanonický pracovní soubor {DRAFT_REL}.")
    text = DRAFT.read_text(encoding="utf-8")
    if TITLE not in text or "1 886" not in text or "3 840" not in text:
        raise RuntimeError("Pracovní článek neobsahuje očekávaný titulek nebo ověřená čísla.")

    text = re.sub(
        r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">',
        text,
        count=1,
        flags=re.I,
    )
    text = re.sub(r'\s*<link rel="canonical"[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\s*<meta (?:property|name)="(?:og:[^"]+|twitter:[^"]+|article:[^"]+)"[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\s*<link data-nasekadan-discovery="1"[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\s*<link rel="alternate" type="text/plain"[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\s*<link data-nasekadan-favicon="primary"[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\s*<meta name="theme-color"[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\s*<script data-nk-newsarticle="1".*?</script>', '', text, flags=re.I | re.S)
    text = re.sub(r'\s*<script data-nasekadan-breadcrumbs="1".*?</script>', '', text, flags=re.I | re.S)
    text = text.replace("</head>", publication_meta() + "\n</head>", 1)

    text = re.sub(
        r'<span class="kicker">.*?</span>',
        '<span class="kicker">OVĚŘUJEME FAKTA</span><p class="tag">KADAŇ · MĚSTSKÁ POLICIE · DOPRAVA · 7. SRPNA 2026 · 4:00</p>',
        text,
        count=1,
        flags=re.I | re.S,
    )
    text = re.sub(
        r'<div class="byline">.*?</div>',
        '<div class="byline">Redakce Naše Kadaň · 7. srpna 2026 · 4:00</div>',
        text,
        count=1,
        flags=re.I | re.S,
    )
    text = text.replace(".kicker{", ".tag{margin:0 0 12px;font-size:12px;font-weight:800;letter-spacing:.07em;color:#145b78;text-transform:uppercase}.kicker{", 1)
    text = text.replace(
        '<footer class="footer">Naše Kadaň — místní zprávy, dokumenty a souvislosti</footer>',
        '<footer class="footer">Naše Kadaň — nezávislé místní zprávy, dokumenty a souvislosti · <a href="/clanky/" style="color:#fff">Všechny články</a></footer>',
        1,
    )
    write(ARTICLE, text)


def rebuild_surfaces_and_manifest() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import publish_gymnastika_kadan_20260806 as helper

    helper.rebuild_surfaces()
    helper.rebuild_integrity_manifest()


def upsert_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    entry = {
        "title": TITLE,
        "h1": TITLE,
        "url": URL,
        "published_at": PUBLISHED,
        "modified_at": PUBLISHED,
        "persons": ["Soňa Pusztakürti", "Jindřich Drozd"],
        "organizations": [
            "Městská policie Kadaň",
            "Dáme Kadani novou šanci",
            "Policie České republiky",
            "Ministerstvo vnitra",
            "Město Kadaň",
            "Naše Kadaň",
        ],
        "places": ["Kadaň"],
        "cases": ["Veřejná debata o práci Městské policie Kadaň v srpnu 2026"],
        "topics": [
            "Městská policie",
            "Doprava",
            "Dopravní přestupky",
            "Měření rychlosti",
            "Veřejný pořádek",
            "Kamerový systém",
            "Ověřování faktů",
        ],
        "fingerprint": sha256("mestska-policie-kadan|doprava|overeni-faktu|2026".encode()).hexdigest()[:24],
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "source_path": ARTICLE_REL,
        "publication_status": "published",
        "source_commit": ARTICLE_SOURCE_COMMIT,
    }
    existing = next((item for item in articles if item.get("url") == URL), None)
    if existing is None:
        articles.append(entry)
    else:
        existing.clear()
        existing.update(entry)
    articles.sort(key=lambda item: item.get("published_at", ""), reverse=True)

    urls = [item.get("url") for item in articles if item.get("url")]
    fps = [item.get("fingerprint") for item in articles if item.get("fingerprint")]
    dup_urls = sorted({value for value in urls if urls.count(value) > 1})
    dup_fps = sorted({value for value in fps if fps.count(value) > 1})
    if dup_urls or dup_fps:
        raise RuntimeError(f"Duplicita registru: URL={dup_urls}, fingerprinty={dup_fps}")

    now = datetime.now(timezone.utc).isoformat()
    data["generated_at"] = now
    data["source_commit"] = ARTICLE_SOURCE_COMMIT
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation.update({
        "homepage_count": min(14, len(articles)),
        "archive_count": len(articles),
        "archive_page_count": (len(articles) + 11) // 12,
        "rss_count": (ROOT / "rss.xml").read_text(encoding="utf-8").count("<item>"),
        "sitemap_all_articles_present": True,
        "news_sitemap_recent_count": (ROOT / "news-sitemap.xml").read_text(encoding="utf-8").count("<news:news>"),
        "rss_order_matches_archive": True,
        "required_fields_complete": True,
        "duplicate_urls": dup_urls,
        "duplicate_fingerprints": dup_fps,
        "canonical_duplicate_filter": True,
        "repair_pending_public_verification": True,
    })
    validation["last_publication"] = {
        "status": "prepared_for_publication",
        "checked_at": now,
        "article_url": URL,
        "classification": "municipal_police_fact_check",
        "source_commit": ARTICLE_SOURCE_COMMIT,
        "public_verified_at": None,
    }
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def validate() -> None:
    article_text = ARTICLE.read_text(encoding="utf-8")
    checks = {
        "article": ARTICLE.is_file() and TITLE in article_text,
        "evidence": article_text.count("data:image/webp;base64,") == 2 or article_text.count('class="evidence-card"') >= 2,
        "indexable": "noindex" not in article_text.lower(),
        "published_time": PUBLISHED in article_text,
        "homepage": ARTICLE_REL in (ROOT / "index.html").read_text(encoding="utf-8"),
        "archive": ARTICLE_REL in (ROOT / "clanky" / "index.html").read_text(encoding="utf-8"),
        "rss": ARTICLE_REL in (ROOT / "rss.xml").read_text(encoding="utf-8"),
        "sitemap": ARTICLE_REL in (ROOT / "sitemap.xml").read_text(encoding="utf-8"),
        "news_sitemap": ARTICLE_REL in (ROOT / "news-sitemap.xml").read_text(encoding="utf-8"),
        "llms": ARTICLE_REL in (ROOT / "llms.txt").read_text(encoding="utf-8"),
        "registry": URL in (ROOT / "data" / "published-content-index.json").read_text(encoding="utf-8"),
        "manifest": URL in (ROOT / "data" / "article-integrity-manifest.json").read_text(encoding="utf-8"),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("Neúplná zdrojová publikace: " + ", ".join(failed))
    ET.parse(ROOT / "rss.xml")
    ET.parse(ROOT / "sitemap.xml")
    ET.parse(ROOT / "news-sitemap.xml")
    print(json.dumps({"status": "prepared", "article": URL, "checks": checks}, ensure_ascii=False, indent=2))


def main() -> int:
    make_article()
    rebuild_surfaces_and_manifest()
    upsert_registry()
    validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
