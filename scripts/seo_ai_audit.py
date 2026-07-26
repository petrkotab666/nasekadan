#!/usr/bin/env python3
"""SEO and AI-readiness audit for nasekadan.cz.

The audit is dependency-free and designed for both a complete report and a
strict gate for newly created or changed public pages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from html import unescape
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
SKIP_DIRS = {
    ".git", ".github", ".image-parts", "deploy", "docker-entrypoint.d",
    "newsletter", "nginx", "scripts", "tools", "nahled", "sdilet", "lms-rescue",
}
ARTICLE_DIR = ROOT / "clanky"
HTML_TAG_RE = re.compile(r"<[^>]+>", re.S)
JSON_LD_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.I | re.S,
)
LINK_RE = re.compile(r"<a\b[^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>", re.I)
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
WORD_RE = re.compile(r"\b[\wÀ-ž][\wÀ-ž–—'-]*\b", re.U)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def expected_url(path: Path) -> str:
    name = rel(path)
    if name == "index.html":
        return f"{BASE}/"
    if name.endswith("/index.html"):
        return f"{BASE}/{name[:-10]}"
    return f"{BASE}/{name}"


def public_html_files() -> list[Path]:
    result = []
    for path in ROOT.rglob("*.html"):
        parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        result.append(path)
    return sorted(result)


def attr(tag: str, name: str) -> str:
    match = re.search(
        rf"\b{re.escape(name)}\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S
    )
    return unescape(match.group(2).strip()) if match else ""


def tag_text(text: str, tag: str) -> list[str]:
    values = []
    for match in re.finditer(
        rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, re.I | re.S
    ):
        plain = unescape(HTML_TAG_RE.sub(" ", match.group(1)))
        values.append(re.sub(r"\s+", " ", plain).strip())
    return values


def meta(text: str, *, name: str | None = None, prop: str | None = None) -> str:
    for match in re.finditer(r"<meta\b[^>]*>", text, re.I):
        tag = match.group(0)
        if name and attr(tag, "name").lower() != name.lower():
            continue
        if prop and attr(tag, "property").lower() != prop.lower():
            continue
        return attr(tag, "content")
    return ""


def link_rel(text: str, wanted: str) -> str:
    for match in re.finditer(r"<link\b[^>]*>", text, re.I):
        tag = match.group(0)
        rel_values = {part.lower() for part in attr(tag, "rel").split()}
        if wanted.lower() in rel_values:
            return attr(tag, "href")
    return ""


def robots_tokens(text: str) -> set[str]:
    return {
        token.strip().lower()
        for token in meta(text, name="robots").split(",")
        if token.strip()
    }


def is_noindex(text: str) -> bool:
    return "noindex" in robots_tokens(text)


def visible_text(text: str) -> str:
    cleaned = re.sub(r"<script\b.*?</script>", " ", text, flags=re.I | re.S)
    cleaned = re.sub(r"<style\b.*?</style>", " ", cleaned, flags=re.I | re.S)
    cleaned = HTML_TAG_RE.sub(" ", cleaned)
    return re.sub(r"\s+", " ", unescape(cleaned)).strip()


def json_ld_nodes(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    nodes: list[dict[str, Any]] = []
    errors: list[str] = []
    for raw in JSON_LD_RE.findall(text):
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError as exc:
            errors.append(str(exc))
            continue
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            nodes.append(candidate)
            graph = candidate.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
    return nodes, errors


def schema_types(node: dict[str, Any]) -> set[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def has_schema(nodes: Iterable[dict[str, Any]], wanted: str) -> bool:
    return any(wanted in schema_types(node) for node in nodes)


def local_target(href: str, source_url: str) -> Path | None:
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    absolute = urljoin(source_url, href)
    parsed = urlparse(absolute)
    if parsed.netloc and parsed.netloc not in {"nasekadan.cz", "www.nasekadan.cz"}:
        return None
    path = parsed.path or "/"
    if path.startswith(("/api/", "/statistiky/")):
        return None
    relative = path.lstrip("/")
    candidates: list[Path]
    if not relative:
        candidates = [ROOT / "index.html"]
    elif relative.endswith("/"):
        candidates = [ROOT / relative / "index.html"]
    elif Path(relative).suffix:
        candidates = [ROOT / relative]
    else:
        candidates = [ROOT / relative, ROOT / f"{relative}.html", ROOT / relative / "index.html"]
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


def add(findings: list[Finding], severity: str, code: str, path: Path | str, message: str) -> None:
    findings.append(Finding(severity, code, rel(path) if isinstance(path, Path) else path, message))


def audit_page(path: Path, findings: list[Finding]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    page = rel(path)
    noindex = is_noindex(text)
    titles = tag_text(text, "title")
    h1s = tag_text(text, "h1")
    description = meta(text, name="description")
    canonical = link_rel(text, "canonical")
    nodes, json_errors = json_ld_nodes(text)
    source_url = canonical or expected_url(path)

    if len(titles) != 1 or not titles[0]:
        add(findings, "error", "title-count", path, "Stránka musí mít právě jeden neprázdný <title>.")
    else:
        if len(titles[0]) < 18:
            add(findings, "warning", "title-short", path, f"Title je velmi krátký ({len(titles[0])} znaků).")
        if len(titles[0]) > 70:
            add(findings, "warning", "title-long", path, f"Title je dlouhý ({len(titles[0])} znaků).")

    if len(h1s) != 1 or not h1s[0]:
        add(findings, "error", "h1-count", path, "Indexovatelná stránka musí mít právě jeden neprázdný H1." if not noindex else "Stránka má chybějící nebo vícenásobný H1.")
    if not description:
        add(findings, "error" if not noindex else "warning", "description-missing", path, "Chybí meta description.")
    elif len(description) < 70:
        add(findings, "warning", "description-short", path, f"Meta description je krátký ({len(description)} znaků).")
    elif len(description) > 190:
        add(findings, "warning", "description-long", path, f"Meta description je dlouhý ({len(description)} znaků).")

    if not noindex:
        if not canonical:
            add(findings, "error", "canonical-missing", path, "Chybí canonical URL.")
        elif canonical != expected_url(path):
            add(findings, "error", "canonical-mismatch", path, f"Canonical {canonical!r} neodpovídá očekávané adrese {expected_url(path)!r}.")
        if "index" not in robots_tokens(text):
            add(findings, "warning", "robots-index-implicit", path, "Indexace je povolená pouze implicitně; doporučen je explicitní robots=index,follow.")

    if page == "404.html" and not noindex:
        add(findings, "error", "404-indexable", path, "Chybová stránka 404 nesmí být indexovatelná.")

    for prop in ("og:title", "og:description", "og:url", "og:image"):
        if not meta(text, prop=prop):
            add(findings, "warning", f"{prop}-missing", path, f"Chybí {prop}.")
    if not meta(text, name="twitter:card"):
        add(findings, "warning", "twitter-card-missing", path, "Chybí twitter:card.")

    for error in json_errors:
        add(findings, "error", "jsonld-invalid", path, f"Neplatný JSON-LD: {error}")
    if not noindex and not nodes:
        add(findings, "warning", "schema-missing", path, "Chybí strukturovaná data JSON-LD.")

    lang_match = re.search(r"<html\b[^>]*>", text, re.I)
    if not lang_match or not attr(lang_match.group(0), "lang"):
        add(findings, "warning", "lang-missing", path, "Kořenový element HTML nemá atribut lang.")

    for image in IMG_RE.findall(text):
        if not attr(image, "alt"):
            add(findings, "warning", "image-alt-missing", path, "Obrázek <img> nemá neprázdný alt.")
        if not attr(image, "width") or not attr(image, "height"):
            add(findings, "info", "image-dimensions-missing", path, "Obrázek <img> nemá oba rozměry width/height.")

    for href in LINK_RE.findall(text):
        target = local_target(href, source_url)
        if target is not None and not target.exists():
            add(findings, "error", "broken-internal-link", path, f"Interní odkaz {href!r} nevede na existující soubor.")

    is_article = path.parent == ARTICLE_DIR and path.name != "index.html"
    if is_article and not noindex:
        article_nodes = [node for node in nodes if "NewsArticle" in schema_types(node) or "Article" in schema_types(node)]
        if not article_nodes:
            add(findings, "error", "article-schema-missing", path, "Veřejný článek nemá NewsArticle/Article schema.")
        else:
            article = article_nodes[0]
            required = ("headline", "description", "datePublished", "dateModified", "author", "publisher", "mainEntityOfPage", "image")
            for key in required:
                if not article.get(key):
                    add(findings, "error", f"article-{key}-missing", path, f"Ve schema článku chybí {key}.")
            if article.get("inLanguage") not in {"cs", "cs-CZ"}:
                add(findings, "warning", "article-language", path, "Schema článku nemá inLanguage cs-CZ.")
        if meta(text, prop="og:type") != "article":
            add(findings, "error", "og-type-article", path, "Veřejný článek musí mít og:type=article.")
        if not meta(text, prop="article:published_time"):
            add(findings, "warning", "published-meta-missing", path, "Chybí article:published_time.")
        if not meta(text, prop="article:modified_time"):
            add(findings, "warning", "modified-meta-missing", path, "Chybí article:modified_time.")
        words = len(WORD_RE.findall(visible_text(text)))
        if words < 350:
            add(findings, "warning", "article-thin", path, f"Článek má přibližně jen {words} slov.")
        internal_article_links = sum(1 for href in LINK_RE.findall(text) if "/clanky/" in urljoin(source_url, href))
        if internal_article_links < 1:
            add(findings, "warning", "article-internal-links", path, "Článek neodkazuje na žádný další vlastní článek.")
        lowered = visible_text(text).lower()
        if not any(term in lowered for term in ("zdroj", "zdroje", "podklady", "dokument")):
            add(findings, "warning", "article-sources", path, "Článek nemá snadno rozpoznatelnou část o zdrojích nebo podkladech.")
        if not has_schema(nodes, "BreadcrumbList"):
            add(findings, "warning", "breadcrumbs-missing", path, "Článek nemá BreadcrumbList.")

    return {
        "path": page,
        "indexable": not noindex,
        "canonical": canonical,
        "title": titles[0] if len(titles) == 1 else "",
        "description": description,
    }


def parse_sitemap(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return set()
    return {
        (node.text or "").strip()
        for node in root.iter()
        if node.tag.endswith("loc") and (node.text or "").strip()
    }


def audit_site(selected_paths: set[str] | None = None) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    pages: list[dict[str, Any]] = []
    for path in public_html_files():
        if selected_paths is not None and rel(path) not in selected_paths:
            continue
        pages.append(audit_page(path, findings))

    if selected_paths is None:
        for field, code in (("canonical", "duplicate-canonical"), ("title", "duplicate-title")):
            groups: dict[str, list[str]] = defaultdict(list)
            for page in pages:
                if page[field] and page["indexable"]:
                    groups[page[field]].append(page["path"])
            for value, paths in groups.items():
                if len(paths) > 1:
                    add(findings, "error" if field == "canonical" else "warning", code, ", ".join(paths), f"Duplicitní {field}: {value!r}")

        sitemap = parse_sitemap(ROOT / "sitemap.xml")
        indexable_urls = {page["canonical"] or expected_url(ROOT / page["path"]) for page in pages if page["indexable"] and page["path"] != "404.html"}
        for url in sorted(indexable_urls - sitemap):
            add(findings, "error", "sitemap-missing-url", "sitemap.xml", f"V sitemapě chybí {url}.")
        for url in sorted(sitemap - indexable_urls):
            add(findings, "error", "sitemap-extra-url", "sitemap.xml", f"Sitemap obsahuje neexistující nebo neindexovatelnou URL {url}.")

        robots = (ROOT / "robots.txt").read_text(encoding="utf-8", errors="replace") if (ROOT / "robots.txt").exists() else ""
        for required in (
            "User-agent: OAI-SearchBot",
            f"Sitemap: {BASE}/sitemap.xml",
            f"Sitemap: {BASE}/news-sitemap.xml",
        ):
            if required not in robots:
                add(findings, "error", "robots-discovery", "robots.txt", f"Chybí řádek: {required}")
        if not (ROOT / "llms.txt").exists():
            add(findings, "error", "llms-missing", "llms.txt", "Chybí llms.txt.")
        if not (ROOT / "rss.xml").exists():
            add(findings, "error", "rss-missing", "rss.xml", "Chybí RSS.")
        if not (ROOT / "news-sitemap.xml").exists():
            add(findings, "error", "news-sitemap-missing", "news-sitemap.xml", "Chybí news sitemap.")
        key_files = list(ROOT.glob("[0-9a-f]" * 32 + ".txt"))
        if not key_files:
            add(findings, "warning", "indexnow-key-missing", ".", "V kořeni nebyl nalezen 32znakový IndexNow klíč.")

    summary = {
        "pages_audited": len(pages),
        "indexable_pages": sum(1 for page in pages if page["indexable"]),
        "findings": dict(Counter(item.severity for item in findings)),
    }
    return sorted(findings, key=lambda item: ({"error": 0, "warning": 1, "info": 2}[item.severity], item.path, item.code)), summary


def markdown_report(findings: list[Finding], summary: dict[str, Any]) -> str:
    lines = [
        "# SEO a AI audit – Naše Kadaň",
        "",
        f"- Zkontrolované HTML stránky: **{summary['pages_audited']}**",
        f"- Indexovatelné stránky: **{summary['indexable_pages']}**",
        f"- Chyby: **{summary['findings'].get('error', 0)}**",
        f"- Varování: **{summary['findings'].get('warning', 0)}**",
        f"- Informace: **{summary['findings'].get('info', 0)}**",
        "",
        "Audit kontroluje technickou indexovatelnost, metadata, canonical adresy, interní odkazy, sitemapu, robots.txt, strukturovaná data a základní připravenost článků pro vyhledávače a odpovědi AI.",
        "",
    ]
    for severity, heading in (("error", "Kritické chyby"), ("warning", "Varování"), ("info", "Doporučení")):
        items = [item for item in findings if item.severity == severity]
        lines += [f"## {heading}", ""]
        if not items:
            lines += ["Bez nálezů.", ""]
            continue
        current = None
        for item in items:
            if item.path != current:
                current = item.path
                lines += [f"### `{current}`", ""]
            lines.append(f"- **{item.code}:** {item.message}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def path_selection(args: argparse.Namespace) -> set[str] | None:
    values = list(args.paths or [])
    if args.paths_file:
        values.extend(
            line.strip()
            for line in Path(args.paths_file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    selected = {
        value.replace("\\", "/").lstrip("./")
        for value in values
        if value.lower().endswith(".html")
    }
    return selected or (set() if values else None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Write Markdown report.")
    parser.add_argument("--json", dest="json_path", help="Write machine-readable JSON report.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when audited pages contain errors.")
    parser.add_argument("--paths", nargs="*", default=[])
    parser.add_argument("--paths-file")
    args = parser.parse_args()

    selected = path_selection(args)
    findings, summary = audit_site(selected)

    if args.report:
        Path(args.report).write_text(markdown_report(findings, summary), encoding="utf-8")
    payload = {"summary": summary, "findings": [asdict(item) for item in findings]}
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(markdown_report(findings, summary))
    if args.strict and any(item.severity == "error" for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
