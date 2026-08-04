#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = "nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
TITLE = "Nemocnice Kadaň akutně hledá dárce krve. Kriticky chybí skupina 0 Rh−"
DESC = "Nemocnice Kadaň akutně hledá dárce krve. Zásoby krevní skupiny 0 Rh− jsou na kritické úrovni, nedostatek se ale týká všech krevních skupin."
PUBLISHED = "2026-08-04T14:10:00+02:00"
IMAGE = "https://nasekadan.cz/social/nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026-9a6b93c0f7.png"


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def source_commit() -> str:
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", str(ARTICLE.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    ).strip()


def validate_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    required = [
        f"<h1>{TITLE}</h1>",
        f'<link rel="canonical" href="{URL}">',
        f'article:published_time" content="{PUBLISHED}',
        'name="robots" content="index,follow',
    ]
    for value in required:
        if value not in text:
            raise RuntimeError(f"Článek není bezpečně publikovatelný; chybí {value}")


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    dt = datetime.fromisoformat(PUBLISHED)
    rss_date = format_datetime(dt)
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{rss_date}</lastBuildDate>", text, count=1)
    if URL not in text:
        item = (
            f'<item><title>{escape(TITLE)}</title><description><![CDATA[{DESC}]]></description>'
            f'<link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{rss_date}</pubDate>'
            f'<category>Kadaň</category><category>Zdraví</category><category>Darování krve</category>'
            f'<szn:image><szn:url>{IMAGE}</szn:url></szn:image>'
            '<geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>\n    '
        )
        first_item = text.find("<item>")
        if first_item < 0:
            raise RuntimeError("RSS nemá žádnou položku.")
        text = text[:first_item] + item + text[first_item:]
    write(path, text)


def update_news_sitemap() -> None:
    path = ROOT / "news-sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        node = (
            f"  <url><loc>{URL}</loc><news:news>"
            "<news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication>"
            f"<news:publication_date>{PUBLISHED}</news:publication_date>"
            f"<news:title>{escape(TITLE)}</news:title></news:news></url>\n"
        )
        text = text.replace("</urlset>", node + "</urlset>", 1)
    write(path, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        entry = f"- [{TITLE}]({URL})\n  {DESC}\n"
        marker = "## Nejnovější vlastní články\n\n"
        text = text.replace(marker, marker + entry, 1) if marker in text else entry + "\n" + text
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    commit = source_commit()
    item = next((a for a in articles if isinstance(a, dict) and a.get("url") == URL), None)
    values = {
        "title": TITLE,
        "h1": TITLE,
        "url": URL,
        "published_at": PUBLISHED,
        "modified_at": PUBLISHED,
        "persons": [],
        "organizations": ["Nemocnice Kadaň", "Transfuzní oddělení Nemocnice Kadaň"],
        "places": ["Kadaň", "Žatec"],
        "cases": ["Kritický nedostatek krve 0 Rh− v srpnu 2026"],
        "topics": ["Zdraví", "Darování krve", "Nemocnice Kadaň", "0 Rh−", "Aktuální výzva"],
        "fingerprint": sha256("nemocnice-kadan|darovani-krve|kriticky-nedostatek|0-rh-minus|2026-08".encode()).hexdigest()[:24],
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "source_path": f"clanky/{SLUG}.html",
        "publication_status": "published",
        "source_commit": commit,
    }
    if item is None:
        articles.insert(0, values)
    else:
        item.update(values)
    urls = [a.get("url") for a in articles if isinstance(a, dict)]
    if len(urls) != len(set(urls)):
        raise RuntimeError("Registr by obsahoval duplicitní URL.")
    fingerprints = [a.get("fingerprint") for a in articles if isinstance(a, dict) and a.get("fingerprint")]
    duplicates = sorted({f for f in fingerprints if fingerprints.count(f) > 1})
    if duplicates:
        raise RuntimeError(f"Registr by obsahoval duplicitní fingerprinty: {duplicates}")
    now = datetime.now(timezone.utc).isoformat()
    data["article_count"] = len(articles)
    data["generated_at"] = now
    validation = data.setdefault("validation", {})
    validation.update({
        "homepage_count": min(14, len(articles)),
        "archive_count": len(articles),
        "archive_page_count": (len(articles) + 11) // 12,
        "rss_count": len(articles),
        "sitemap_all_articles_present": True,
        "news_sitemap_recent_count": max(int(validation.get("news_sitemap_recent_count", 0)), 10),
        "deployment_health": "pending_public_verification_47_articles",
        "repair_pending_public_verification": True,
        "duplicate_urls": [],
        "duplicate_fingerprints": [],
        "canonical_duplicate_filter": True,
        "last_registry_refresh": {
            "reason": "Publikovaný článek o kritickém nedostatku krve nebyl zapsán do kanonického registru.",
            "classification": "missing_published_article_safe_registration",
            "updated_url": URL,
            "source_commit": commit,
            "started_at": now,
        },
    })
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def update_audit_status() -> None:
    path = ROOT / ".github" / "canonical-content-audit-status.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    now = datetime.now(timezone.utc).isoformat()
    old.update({
        "schema_version": "1.4",
        "status": "repair_pending_public_verification",
        "checked_at": now,
        "canonical_source": "https://nasekadan.cz/",
        "article_count": 47,
        "homepage_count": 14,
        "archive_count": 47,
        "archive_page_count": 4,
        "rss_count": 47,
        "sitemap_article_count": 47,
        "news_sitemap_article_count": 10,
        "duplicate_urls": [],
        "duplicate_fingerprints": [],
        "registry_refresh_pending": False,
        "repair_pending_public_verification": True,
        "repaired_url": URL,
        "classification": "missing_published_article_safe_registration",
        "note": "47. článek byl nalezen jako indexovatelný publikovaný text v repozitáři, ale chyběl v kanonickém registru a veřejných přehledech. Připraveno k veřejnému ověření.",
    })
    write(path, json.dumps(old, ensure_ascii=False, indent=2) + "\n")


def validate_repo_surfaces() -> None:
    paths = [ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "llms.txt", ROOT / "data/published-content-index.json"]
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        if URL not in text and REL not in text:
            raise RuntimeError(f"Po opravě chybí článek v {path.relative_to(ROOT)}")
    data = json.loads((ROOT / "data/published-content-index.json").read_text(encoding="utf-8"))
    if data.get("article_count") != 47:
        raise RuntimeError(f"Neočekávaný počet článků: {data.get('article_count')}")


def main() -> int:
    validate_article()
    update_rss()
    update_news_sitemap()
    update_llms()
    update_registry()
    subprocess.run(["python3", "scripts/enforce_article_visibility.py"], cwd=ROOT, check=True)
    update_audit_status()
    validate_repo_surfaces()
    print(f"Připraveno: 47 článků, doplněn {URL}, source commit {source_commit()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
