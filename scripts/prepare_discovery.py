#!/usr/bin/env python3
"""Prepare search-engine and AI discovery files for nasekadan.cz.

The script is intentionally dependency-free and idempotent. It enriches public
HTML without replacing article-specific Open Graph metadata, generates a Google
News sitemap, and writes an AI-readable site overview.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape as html_escape
from pathlib import Path
from typing import Any
import json
import re


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
ORG_ID = f"{BASE}/#organization"
WEBSITE_ID = f"{BASE}/#website"
SOCIAL_IMAGE = f"{BASE}/social-card.png"
DISCOVERY_MARKER = 'data-nasekadan-discovery="1"'
BREADCRUMB_MARKER = 'data-nasekadan-breadcrumbs="1"'
PUBLIC_SKIP_PARTS = {
    ".git",
    ".github",
    ".image-parts",
    "docker-entrypoint.d",
    "nginx",
    "nahled",
    "scripts",
    "tools",
}
JSON_LD_PATTERN = re.compile(
    r'(<script\b[^>]*\btype=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.IGNORECASE | re.DOTALL,
)


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_public_html(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return not any(part in PUBLIC_SKIP_PARTS for part in rel.parts)


def canonical_for(path: Path) -> str:
    rel = relative_path(path)
    if rel == "index.html":
        return f"{BASE}/"
    if rel.endswith("/index.html"):
        return f"{BASE}/{rel[:-10]}"
    return f"{BASE}/{rel}"


def first_tag_text(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    plain = re.sub(r"<[^>]+>", " ", match.group(1))
    return re.sub(r"\s+", " ", plain).strip()


def meta_content(text: str, *, name: str | None = None, prop: str | None = None) -> str:
    for match in re.finditer(r"<meta\b[^>]*>", text, re.IGNORECASE):
        tag = match.group(0)
        if name and not re.search(
            rf'\bname\s*=\s*["\']{re.escape(name)}["\']', tag, re.IGNORECASE
        ):
            continue
        if prop and not re.search(
            rf'\bproperty\s*=\s*["\']{re.escape(prop)}["\']', tag, re.IGNORECASE
        ):
            continue
        content = re.search(r'\bcontent\s*=\s*["\']([^"\']*)', tag, re.IGNORECASE)
        if content:
            return content.group(1).strip()
    return ""


def canonical_from_html(text: str, path: Path) -> str:
    for match in re.finditer(r"<link\b[^>]*>", text, re.IGNORECASE):
        tag = match.group(0)
        if not re.search(r'\brel\s*=\s*["\']canonical["\']', tag, re.IGNORECASE):
            continue
        href = re.search(r'\bhref\s*=\s*["\']([^"\']+)', tag, re.IGNORECASE)
        if href:
            return href.group(1).strip()
    return canonical_for(path)


def schema_types(data: Any) -> set[str]:
    if not isinstance(data, dict):
        return set()
    raw = data.get("@type")
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, list):
        return {item for item in raw if isinstance(item, str)}
    return set()


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        try:
            parsed = datetime.strptime(normalized[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone(timedelta(hours=2)))
    return parsed


def normalize_hospital_article(path: Path, text: str) -> str:
    if relative_path(path) != "clanky/nemocnice-kadan.html":
        return text
    replacements = {
        "ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · AKTUALIZOVÁNO 23. ČERVENCE 2026":
            "ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 24. ČERVENCE 2026",
        '<p class="updated">Aktualizováno: 23. 7. 2026</p>':
            '<p class="updated">Publikováno: 24. 7. 2026</p>',
        '"datePublished":"2026-07-23"': '"datePublished":"2026-07-24"',
        '"dateModified":"2026-07-23"': '"dateModified":"2026-07-24"',
        "Stav informací k 23. červenci 2026.": "Stav informací k 24. červenci 2026.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def common_discovery_schema() -> dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": ["Organization", "NewsMediaOrganization"],
                "@id": ORG_ID,
                "name": "Naše Kadaň",
                "url": f"{BASE}/",
                "email": "info@nasekadan.cz",
                "description": (
                    "Místní zpravodajský a informační web s vlastními články, "
                    "ověřováním veřejných dokumentů, přehledem akcí a průvodcem Kadaní."
                ),
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{BASE}/favicon.svg",
                    "width": 64,
                    "height": 64,
                },
                "image": SOCIAL_IMAGE,
                "areaServed": {
                    "@type": "City",
                    "name": "Kadaň",
                    "sameAs": "https://www.wikidata.org/wiki/Q158274",
                },
                "publishingPrinciples": f"{BASE}/o-webu/",
            },
            {
                "@type": "WebSite",
                "@id": WEBSITE_ID,
                "url": f"{BASE}/",
                "name": "Naše Kadaň",
                "inLanguage": "cs-CZ",
                "publisher": {"@id": ORG_ID},
            },
        ],
    }


def discovery_head_snippet() -> str:
    schema = json.dumps(
        common_discovery_schema(), ensure_ascii=False, separators=(",", ":")
    )
    return (
        f'<link {DISCOVERY_MARKER} rel="alternate" type="application/rss+xml" '
        f'title="Naše Kadaň – zprávy z Kadaně" href="{BASE}/rss.xml">'
        f'<link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" '
        f'href="{BASE}/llms.txt">'
        '<meta name="geo.region" content="CZ-42">'
        '<meta name="geo.placename" content="Kadaň">'
        '<meta name="geo.position" content="50.375984;13.271307">'
        '<meta name="ICBM" content="50.375984, 13.271307">'
        f'<script type="application/ld+json">{schema}</script>'
    )


def breadcrumb_schema(path: Path, text: str, canonical: str) -> dict[str, Any] | None:
    rel = relative_path(path)
    title = first_tag_text(text, "h1") or first_tag_text(text, "title")
    if not title:
        return None
    title = re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", title).strip()

    if rel.startswith("clanky/") and rel != "clanky/index.html":
        items = [
            ("Naše Kadaň", f"{BASE}/"),
            ("Články", f"{BASE}/clanky/"),
            (title, canonical),
        ]
    elif rel.startswith("pruvodce/") and rel != "pruvodce/index.html":
        items = [
            ("Naše Kadaň", f"{BASE}/"),
            ("Průvodce", f"{BASE}/pruvodce/"),
            (title, canonical),
        ]
    else:
        return None

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": name,
                "item": url,
            }
            for index, (name, url) in enumerate(items, start=1)
        ],
    }


def enrich_json_ld(text: str, path: Path, canonical: str) -> tuple[str, list[dict[str, Any]]]:
    article_schemas: list[dict[str, Any]] = []
    page_title = first_tag_text(text, "title")
    page_description = meta_content(text, name="description")
    og_title = meta_content(text, prop="og:title")
    og_description = meta_content(text, prop="og:description")
    og_image = meta_content(text, prop="og:image")
    published_meta = meta_content(text, prop="article:published_time")
    modified_meta = meta_content(text, prop="article:modified_time")

    def replace(match: re.Match[str]) -> str:
        opening, raw, closing = match.groups()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)

        targets: list[dict[str, Any]] = []
        if isinstance(data, dict):
            if "NewsArticle" in schema_types(data):
                targets.append(data)
            graph = data.get("@graph")
            if isinstance(graph, list):
                targets.extend(
                    node
                    for node in graph
                    if isinstance(node, dict) and "NewsArticle" in schema_types(node)
                )

        for article in targets:
            article["headline"] = (
                article.get("headline")
                or og_title
                or re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", page_title)
            )
            article["description"] = (
                article.get("description") or og_description or page_description
            )
            if og_image:
                article["image"] = [og_image]
            if published_meta:
                article["datePublished"] = published_meta
            if modified_meta:
                article["dateModified"] = modified_meta
            elif article.get("datePublished") and not article.get("dateModified"):
                article["dateModified"] = article["datePublished"]
            article["author"] = {
                "@type": "Organization",
                "@id": ORG_ID,
                "name": "Naše Kadaň",
                "url": f"{BASE}/o-webu/",
            }
            article["publisher"] = {"@id": ORG_ID}
            article["mainEntityOfPage"] = {"@type": "WebPage", "@id": canonical}
            article["inLanguage"] = "cs-CZ"
            article["isAccessibleForFree"] = True
            article_schemas.append(dict(article))

        if not targets:
            return match.group(0)

        serialized = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return f"{opening}{serialized}{closing}"

    return JSON_LD_PATTERN.sub(replace, text), article_schemas


def process_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = normalize_hospital_article(path, text)
    canonical = canonical_from_html(text, path)
    text, _ = enrich_json_ld(text, path, canonical)

    if DISCOVERY_MARKER not in text:
        text = text.replace("</head>", f"{discovery_head_snippet()}</head>", 1)

    if BREADCRUMB_MARKER not in text:
        breadcrumbs = breadcrumb_schema(path, text, canonical)
        if breadcrumbs:
            payload = json.dumps(
                breadcrumbs, ensure_ascii=False, separators=(",", ":")
            )
            tag = (
                f'<script {BREADCRUMB_MARKER} type="application/ld+json">'
                f"{payload}</script>"
            )
            text = text.replace("</head>", f"{tag}</head>", 1)

    path.write_text(text, encoding="utf-8")


def collect_article_schemas() -> list[tuple[Path, dict[str, Any]]]:
    collected: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((ROOT / "clanky").glob("*.html")):
        text = path.read_text(encoding="utf-8")
        for match in JSON_LD_PATTERN.finditer(text):
            try:
                data = json.loads(match.group(2))
            except json.JSONDecodeError:
                continue
            nodes = [data] if isinstance(data, dict) else []
            if isinstance(data, dict) and isinstance(data.get("@graph"), list):
                nodes.extend(node for node in data["@graph"] if isinstance(node, dict))
            for node in nodes:
                if "NewsArticle" in schema_types(node):
                    collected.append((path, node))
    return collected


def write_news_sitemap() -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=2)
    entries: list[tuple[datetime, str, str]] = []

    for path, article in collect_article_schemas():
        published_raw = str(article.get("datePublished", ""))
        published = parse_datetime(published_raw)
        if not published or published.astimezone(timezone.utc) < cutoff:
            continue
        text = path.read_text(encoding="utf-8")
        canonical = canonical_from_html(text, path)
        title = str(article.get("headline") or first_tag_text(text, "h1")).strip()
        entries.append((published, canonical, title))

    entries.sort(key=lambda item: item[0], reverse=True)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">',
    ]
    for published, canonical, title in entries:
        publication_date = published.isoformat()
        lines.extend([
            "  <url>",
            f"    <loc>{html_escape(canonical)}</loc>",
            "    <news:news>",
            "      <news:publication>",
            "        <news:name>Naše Kadaň</news:name>",
            "        <news:language>cs</news:language>",
            "      </news:publication>",
            f"      <news:publication_date>{html_escape(publication_date)}</news:publication_date>",
            f"      <news:title>{html_escape(title)}</news:title>",
            "    </news:news>",
            "  </url>",
        ])
    lines.append("</urlset>")
    (ROOT / "news-sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_llms_txt() -> None:
    articles: list[tuple[datetime, str, str, str]] = []
    for path, article in collect_article_schemas():
        published = parse_datetime(str(article.get("datePublished", "")))
        if not published:
            continue
        text = path.read_text(encoding="utf-8")
        canonical = canonical_from_html(text, path)
        title = str(article.get("headline") or first_tag_text(text, "h1")).strip()
        description = str(
            article.get("description") or meta_content(text, name="description")
        ).strip()
        articles.append((published, title, canonical, description))
    articles.sort(key=lambda item: item[0], reverse=True)

    lines = [
        "# Naše Kadaň",
        "",
        "> Místní zpravodajský a informační web pro Kadaň a okolí. Publikuje vlastní články, analýzy veřejných dokumentů, praktické informace, přehled akcí a průvodce městem.",
        "",
        "## Zásady použití obsahu",
        "",
        "- Primární a veřejná adresa webu je https://nasekadan.cz/.",
        "- U aktuálních událostí používejte datum publikace a případné datum poslední úpravy uvedené u článku.",
        "- Rozlišujte vlastní redakční články od automatického přehledu veřejných zdrojů.",
        "- Při citování uvádějte název Naše Kadaň a přímý odkaz na příslušnou stránku.",
        "- Redakční zásady a kontakt: https://nasekadan.cz/o-webu/",
        "",
        "## Hlavní sekce",
        "",
        "- Články: https://nasekadan.cz/clanky/",
        "- Přehled veřejných zdrojů: https://nasekadan.cz/prehled-zdroju/",
        "- Průvodce Kadaní: https://nasekadan.cz/pruvodce/",
        "- Praktická Kadaň: https://nasekadan.cz/prakticke/",
        "- Doprava: https://nasekadan.cz/doprava/",
        "- Organizace: https://nasekadan.cz/organizace/",
        "",
        "## Strojově čitelné zdroje",
        "",
        "- RSS: https://nasekadan.cz/rss.xml",
        "- Sitemap: https://nasekadan.cz/sitemap.xml",
        "- Google News sitemap: https://nasekadan.cz/news-sitemap.xml",
        "",
        "## Nejnovější vlastní články",
        "",
    ]
    for _, title, canonical, description in articles[:12]:
        lines.append(f"- [{title}]({canonical})")
        if description:
            lines.append(f"  {description}")
    lines.extend([
        "",
        "## Kontakt",
        "",
        "- E-mail: info@nasekadan.cz",
        "- Web: https://nasekadan.cz/",
        "",
    ])
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")


def update_robots() -> None:
    path = ROOT / "robots.txt"
    text = path.read_text(encoding="utf-8") if path.exists() else "User-agent: *\nAllow: /\n"
    news_line = f"Sitemap: {BASE}/news-sitemap.xml"
    if news_line not in text:
        text = text.rstrip() + f"\n{news_line}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in sorted(ROOT.rglob("*.html")):
        if is_public_html(path):
            process_html(path)
    write_news_sitemap()
    write_llms_txt()
    update_robots()


if __name__ == "__main__":
    main()
