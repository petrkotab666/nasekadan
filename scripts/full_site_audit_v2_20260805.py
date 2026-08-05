#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
REGISTRY = ROOT / "data" / "published-content-index.json"
PUBLIC_DIRS = {
    "clanky", "pruvodce", "prakticke", "doprava", "organizace", "magazin",
    "recepty", "prirodni-lekarna", "slevy", "herna", "hry", "data", "social",
    "assets", "images", "img", "api", "inzerce", "o-webu", "zapojte-se",
    "cookies", "ochrana-osobnich-udaju", "provozovatel", "prehled-zdroju", "nahled",
}
CHECK_SUFFIXES = {
    ".html", ".htm", ".css", ".js", ".json", ".xml", ".txt", ".png", ".jpg",
    ".jpeg", ".webp", ".gif", ".svg", ".ico", ".woff", ".woff2", ".pdf",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"}
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)


def normalize_url(value: str | None, base: str = BASE + "/") -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value or value.startswith("#") or value.lower().startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    absolute = urljoin(base, value)
    parts = urlsplit(absolute)
    if parts.netloc.lower() not in {"nasekadan.cz", "www.nasekadan.cz"}:
        return None
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    return urlunsplit(("https", "nasekadan.cz", path, "", ""))


def repo_path_for_url(url: str) -> Path | None:
    path = urlsplit(url).path
    if path == "/":
        candidate = ROOT / "index.html"
    elif path.endswith("/"):
        candidate = ROOT / path.lstrip("/") / "index.html"
    else:
        candidate = ROOT / path.lstrip("/")
    return candidate if candidate.is_file() else None


def public_html_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if rel.parts[0] in {"research", "reports", "node_modules", "vendor"}:
            continue
        if len(rel.parts) == 1 or rel.parts[0] in PUBLIC_DIRS:
            result.append(path)
    return sorted(result)


class PageParser(HTMLParser):
    def __init__(self, page_url: str):
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.refs: set[str] = set()
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.h3_parts: list[str] = []
        self.in_title = False
        self.in_h1 = False
        self.in_h3 = False
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None
        self.jsonld: list[str] = []
        self.in_jsonld = False
        self.jsonld_parts: list[str] = []
        self.cards: list[dict] = []
        self.card_depth = 0
        self.current_card: dict | None = None
        self.has_header_v1 = False
        self.has_footer_v1 = False

    @staticmethod
    def attr_map(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {str(k).lower(): (v or "") for k, v in attrs}

    def add_ref(self, value: str | None) -> None:
        normalized = normalize_url(value, self.page_url)
        if normalized:
            self.refs.add(normalized)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = self.attr_map(attrs)
        classes = set(data.get("class", "").split())
        if tag == "header" and data.get("data-site-header") == "v1":
            self.has_header_v1 = True
        if tag == "footer" and data.get("data-site-footer") == "v1":
            self.has_footer_v1 = True

        for key in ("href", "src", "poster"):
            if key in data:
                self.add_ref(data[key])
        if data.get("srcset"):
            for item in data["srcset"].split(","):
                self.add_ref(item.strip().split()[0])
        if data.get("style"):
            for value in CSS_URL_RE.findall(data["style"]):
                self.add_ref(value)
                if self.current_card is not None:
                    image = normalize_url(value, self.page_url)
                    if image:
                        self.current_card.setdefault("images", []).append(image)

        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.in_h1 = True
        if tag == "h3":
            self.in_h3 = True
            self.h3_parts = []

        if tag == "meta":
            key = data.get("property") or data.get("name")
            if key:
                self.meta[key.lower()] = data.get("content", "").strip()
        if tag == "link" and "canonical" in data.get("rel", "").lower():
            self.canonical = normalize_url(data.get("href"), self.page_url)
        if tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.jsonld_parts = []

        if tag == "article" and "article-card" in classes and self.current_card is None:
            self.current_card = {"title": "", "href": None, "images": []}
            self.card_depth = 1
        elif self.current_card is not None:
            self.card_depth += 1

        if self.current_card is not None and tag == "a" and "read-more" in classes:
            self.current_card["href"] = normalize_url(data.get("href"), self.page_url)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
        if tag == "h3":
            self.in_h3 = False
            if self.current_card is not None:
                self.current_card["title"] = " ".join("".join(self.h3_parts).split())
        if tag == "script" and self.in_jsonld:
            self.in_jsonld = False
            self.jsonld.append("".join(self.jsonld_parts).strip())
        if self.current_card is not None:
            self.card_depth -= 1
            if self.card_depth == 0:
                self.cards.append(self.current_card)
                self.current_card = None

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.h1_parts.append(data)
        if self.in_h3:
            self.h3_parts.append(data)
        if self.in_jsonld:
            self.jsonld_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def h1(self) -> str:
        return " ".join("".join(self.h1_parts).split())

    def schema_counts(self) -> tuple[int, int, int]:
        articles = 0
        breadcrumbs = 0
        invalid = 0
        for raw in self.jsonld:
            if not raw:
                continue
            try:
                value = json.loads(raw)
            except Exception:
                invalid += 1
                continue
            stack = [value]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    kind = node.get("@type")
                    kinds = {kind} if isinstance(kind, str) else set(kind or [])
                    if kinds & {"Article", "NewsArticle"}:
                        articles += 1
                    if "BreadcrumbList" in kinds:
                        breadcrumbs += 1
                    stack.extend(node.values())
                elif isinstance(node, list):
                    stack.extend(node)
        return articles, breadcrumbs, invalid

    def article_images(self) -> list[str]:
        values: list[str] = []
        for key in ("og:image", "twitter:image"):
            image = normalize_url(self.meta.get(key), self.page_url)
            if image and image not in values:
                values.append(image)
        for raw in self.jsonld:
            try:
                value = json.loads(raw)
            except Exception:
                continue
            stack = [value]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    kind = node.get("@type")
                    kinds = {kind} if isinstance(kind, str) else set(kind or [])
                    if kinds & {"Article", "NewsArticle"}:
                        image = node.get("image")
                        image_values = image if isinstance(image, list) else [image]
                        for item in image_values:
                            if isinstance(item, dict):
                                item = item.get("url")
                            if isinstance(item, str):
                                normalized = normalize_url(item, self.page_url)
                                if normalized and normalized not in values:
                                    values.append(normalized)
                    stack.extend(node.values())
                elif isinstance(node, list):
                    stack.extend(node)
        return values


def parse_html(text: str, url: str) -> PageParser:
    parser = PageParser(url)
    parser.feed(text)
    parser.close()
    return parser


def load_published_entries(data: dict) -> list[dict]:
    raw = data.get("articles") or data.get("entries") or []
    now = datetime.now(timezone.utc)
    found: list[tuple[datetime, dict]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        state = item.get("publication_status")
        if not isinstance(state, str):
            legacy = item.get("status")
            state = legacy if isinstance(legacy, str) else "published"
        if state in {"draft", "scheduled", "removed"}:
            continue
        url = normalize_url(item.get("canonical_url") or item.get("url"))
        published = item.get("published_at") or item.get("date_published") or item.get("published")
        if not url or not published:
            continue
        try:
            dt = datetime.fromisoformat(str(published).replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
        if dt <= now:
            copy = dict(item)
            copy["_url"] = url
            copy["_dt"] = dt
            found.append((dt, copy))
    found.sort(key=lambda row: row[0], reverse=True)
    return [item for _, item in found]


def article_files() -> list[Path]:
    return [
        path for path in sorted((ROOT / "clanky").glob("*.html"))
        if path.name != "index.html" and not re.fullmatch(r"strana-\d+\.html", path.name)
    ]


def archive_files() -> list[Path]:
    result = [ROOT / "clanky" / "index.html"]
    result.extend(sorted((ROOT / "clanky").glob("strana-*.html"), key=lambda p: int(re.search(r"\d+", p.stem).group())))
    return [path for path in result if path.is_file()]


def parse_xml_locs(text: str) -> list[str]:
    root = ET.fromstring(text)
    values: list[str] = []
    for node in root.iter():
        if node.tag.endswith("loc") and node.text:
            url = normalize_url(node.text)
            if url:
                values.append(url)
    return values


def static_audit(report_path: Path) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = load_published_entries(registry)
    expected = {item["_url"] for item in entries}
    entry_by_url = {item["_url"]: item for item in entries}

    parsers: dict[str, PageParser] = {}
    references_checked = 0
    for path in public_html_files():
        rel = path.relative_to(ROOT).as_posix()
        url = BASE + ("/" if rel == "index.html" else "/" + rel)
        parser = parse_html(path.read_text(encoding="utf-8", errors="replace"), url)
        parsers[url] = parser
        for ref in parser.refs:
            suffix = Path(urlsplit(ref).path).suffix.lower()
            if urlsplit(ref).path.endswith("/") or suffix in CHECK_SUFFIXES:
                references_checked += 1
                if repo_path_for_url(ref) is None:
                    errors.append({"type": "missing_local_reference", "source": rel, "target": ref})

    article_parsers: dict[str, PageParser] = {}
    for path in article_files():
        url = BASE + "/clanky/" + path.name
        parser = parsers.get(url) or parse_html(path.read_text(encoding="utf-8", errors="replace"), url)
        article_parsers[url] = parser
        if url not in expected:
            warnings.append({"type": "article_file_not_in_registry", "url": url})
        if not parser.h1:
            errors.append({"type": "missing_h1", "url": url})
        robots = parser.meta.get("robots", "").lower()
        if "noindex" in robots:
            errors.append({"type": "published_article_noindex", "url": url})
        if parser.canonical != url:
            errors.append({"type": "canonical_mismatch", "url": url, "canonical": parser.canonical})
        images = parser.article_images()
        if not images:
            errors.append({"type": "missing_article_image_metadata", "url": url})
        for image in images:
            if repo_path_for_url(image) is None:
                errors.append({"type": "missing_article_image_file", "url": url, "image": image})
        schema_articles, breadcrumbs, invalid = parser.schema_counts()
        if schema_articles != 1:
            warnings.append({"type": "article_schema_count", "url": url, "count": schema_articles})
        if breadcrumbs != 1:
            warnings.append({"type": "breadcrumb_schema_count", "url": url, "count": breadcrumbs})
        if invalid:
            warnings.append({"type": "invalid_jsonld", "url": url, "count": invalid})

    missing_files = sorted(expected - set(article_parsers))
    if missing_files:
        errors.append({"type": "registry_articles_missing_file", "urls": missing_files})

    archive_urls: list[str] = []
    cards_checked = 0
    for path in archive_files():
        url = BASE + ("/clanky/" if path.name == "index.html" else "/clanky/" + path.name)
        parser = parsers.get(url) or parse_html(path.read_text(encoding="utf-8", errors="replace"), url)
        for card in parser.cards:
            cards_checked += 1
            target = card.get("href")
            title = card.get("title")
            if not target:
                errors.append({"type": "card_missing_link", "page": url, "title": title})
                continue
            archive_urls.append(target)
            target_parser = article_parsers.get(target)
            if target_parser and title != target_parser.h1:
                errors.append({"type": "card_title_target_mismatch", "page": url, "title": title, "target": target, "target_h1": target_parser.h1})
            for image in card.get("images", []):
                if repo_path_for_url(image) is None:
                    errors.append({"type": "card_image_missing_file", "page": url, "target": target, "image": image})
    if archive_urls != [item["_url"] for item in entries]:
        missing = sorted(expected - set(archive_urls))
        extra = sorted(set(archive_urls) - expected)
        errors.append({"type": "archive_order_or_coverage_mismatch", "missing": missing, "extra": extra, "archive_count": len(archive_urls), "registry_count": len(entries)})

    home_parser = parsers.get(BASE + "/")
    if home_parser and entries:
        home_targets = {card.get("href") for card in home_parser.cards if card.get("href")}
        latest = entries[0]["_url"]
        all_home_refs = set(home_parser.refs)
        if latest not in home_targets and latest not in all_home_refs:
            errors.append({"type": "latest_article_missing_from_home", "url": latest})

    rss_text = (ROOT / "rss.xml").read_text(encoding="utf-8", errors="replace")
    sitemap_text = (ROOT / "sitemap.xml").read_text(encoding="utf-8", errors="replace")
    news_text = (ROOT / "news-sitemap.xml").read_text(encoding="utf-8", errors="replace")
    try:
        rss_root = ET.fromstring(rss_text)
        rss_urls = [normalize_url(item.findtext("link")) for item in rss_root.findall("./channel/item")]
        rss_urls = [url for url in rss_urls if url]
    except Exception as exc:
        rss_urls = []
        errors.append({"type": "invalid_rss_xml", "error": str(exc)})
    try:
        sitemap_urls = [url for url in parse_xml_locs(sitemap_text) if "/clanky/" in url and "/strana-" not in url and url.endswith(".html")]
    except Exception as exc:
        sitemap_urls = []
        errors.append({"type": "invalid_sitemap_xml", "error": str(exc)})
    try:
        news_urls = parse_xml_locs(news_text)
    except Exception as exc:
        news_urls = []
        errors.append({"type": "invalid_news_sitemap_xml", "error": str(exc)})

    if len(rss_urls) != len(set(rss_urls)):
        errors.append({"type": "duplicate_rss_urls", "duplicates": len(rss_urls) - len(set(rss_urls))})
    if len(sitemap_urls) != len(set(sitemap_urls)):
        errors.append({"type": "duplicate_sitemap_urls", "duplicates": len(sitemap_urls) - len(set(sitemap_urls))})
    if expected - set(rss_urls):
        errors.append({"type": "missing_from_rss", "urls": sorted(expected - set(rss_urls))})
    if expected - set(sitemap_urls):
        errors.append({"type": "missing_from_sitemap", "urls": sorted(expected - set(sitemap_urls))})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "static",
        "status": "failed" if errors else "passed",
        "article_count": len(entries),
        "html_files_checked": len(parsers),
        "local_references_checked": references_checked,
        "cards_checked": cards_checked,
        "archive_pages_checked": len(archive_files()),
        "rss_items": len(rss_urls),
        "news_urls": len(news_urls),
        "errors": errors,
        "warnings": warnings,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def cache_bust(url: str) -> str:
    return url + ("&" if "?" in url else "?") + "full_audit_v2=" + str(time.time_ns())


def fetch_one(url: str) -> dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    request = Request(cache_bust(url), headers={"User-Agent": "NaseKadan-full-site-audit-v2/1.0", "Cache-Control": "no-cache"})
    try:
        with urlopen(request, timeout=40, context=ctx) as response:
            data = response.read()
            return {"url": url, "status": response.status, "type": response.headers.get_content_type(), "data": data, "bytes": len(data), "error": None}
    except Exception as exc:
        return {"url": url, "status": 0, "type": "", "data": b"", "bytes": 0, "error": str(exc)}


def fetch_many(urls: set[str], workers: int = 24) -> dict[str, dict]:
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_one, url): url for url in sorted(urls)}
        for future in as_completed(futures):
            result = future.result()
            results[result["url"]] = result
    return results


def live_audit(report_path: Path) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    core_urls = {
        BASE + "/", BASE + "/clanky/", BASE + "/rss.xml", BASE + "/sitemap.xml",
        BASE + "/news-sitemap.xml", BASE + "/llms.txt", BASE + "/deployment-health.txt",
        BASE + "/data/published-content-index.json",
    }
    core = fetch_many(core_urls, workers=8)
    for url, result in core.items():
        if result["status"] != 200:
            errors.append({"type": "core_url_unavailable", "url": url, "error": result["error"]})
    if errors:
        report = {"generated_at": datetime.now(timezone.utc).isoformat(), "mode": "live", "status": "failed", "errors": errors, "warnings": warnings}
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    registry = json.loads(core[BASE + "/data/published-content-index.json"]["data"].decode("utf-8", "replace"))
    entries = load_published_entries(registry)
    expected = {item["_url"] for item in entries}
    expected_order = [item["_url"] for item in entries]

    sitemap_text = core[BASE + "/sitemap.xml"]["data"].decode("utf-8", "replace")
    rss_text = core[BASE + "/rss.xml"]["data"].decode("utf-8", "replace")
    news_text = core[BASE + "/news-sitemap.xml"]["data"].decode("utf-8", "replace")
    try:
        sitemap_all = parse_xml_locs(sitemap_text)
        sitemap_articles = [url for url in sitemap_all if "/clanky/" in url and "/strana-" not in url and url.endswith(".html")]
    except Exception as exc:
        sitemap_all = []
        sitemap_articles = []
        errors.append({"type": "invalid_live_sitemap", "error": str(exc)})
    try:
        rss_root = ET.fromstring(rss_text)
        rss_urls = [normalize_url(item.findtext("link")) for item in rss_root.findall("./channel/item")]
        rss_urls = [url for url in rss_urls if url]
    except Exception as exc:
        rss_urls = []
        errors.append({"type": "invalid_live_rss", "error": str(exc)})
    try:
        news_urls = parse_xml_locs(news_text)
    except Exception as exc:
        news_urls = []
        errors.append({"type": "invalid_live_news_sitemap", "error": str(exc)})

    if len(sitemap_articles) != len(set(sitemap_articles)):
        errors.append({"type": "duplicate_live_sitemap_urls", "duplicates": len(sitemap_articles) - len(set(sitemap_articles))})
    if len(rss_urls) != len(set(rss_urls)):
        errors.append({"type": "duplicate_live_rss_urls", "duplicates": len(rss_urls) - len(set(rss_urls))})
    if len(news_urls) != len(set(news_urls)):
        errors.append({"type": "duplicate_live_news_urls", "duplicates": len(news_urls) - len(set(news_urls))})
    if expected - set(sitemap_articles):
        errors.append({"type": "missing_live_sitemap", "urls": sorted(expected - set(sitemap_articles))})
    if expected - set(rss_urls):
        errors.append({"type": "missing_live_rss", "urls": sorted(expected - set(rss_urls))})

    archive_urls = {BASE + "/clanky/"}
    archive_first = core[BASE + "/clanky/"]["data"].decode("utf-8", "replace")
    first_parser = parse_html(archive_first, BASE + "/clanky/")
    for ref in first_parser.refs:
        if re.fullmatch(r"https://nasekadan\.cz/clanky/strana-\d+\.html", ref):
            archive_urls.add(ref)

    page_urls = set(expected) | archive_urls | {BASE + "/"}
    page_results = fetch_many(page_urls)
    parsers: dict[str, PageParser] = {}
    all_refs: set[str] = set()
    article_images: set[str] = set()
    for url, result in page_results.items():
        if result["status"] != 200:
            errors.append({"type": "public_page_unavailable", "url": url, "error": result["error"]})
            continue
        text = result["data"].decode("utf-8", "replace")
        parser = parse_html(text, url)
        parsers[url] = parser
        for ref in parser.refs:
            path = urlsplit(ref).path
            suffix = Path(path).suffix.lower()
            if path.endswith("/") or suffix in CHECK_SUFFIXES:
                all_refs.add(ref)
        if url in expected:
            entry = next(item for item in entries if item["_url"] == url)
            expected_h1 = entry.get("h1") or entry.get("title") or entry.get("headline")
            if expected_h1 and parser.h1 != expected_h1:
                errors.append({"type": "live_h1_mismatch", "url": url, "actual": parser.h1, "expected": expected_h1})
            if "noindex" in parser.meta.get("robots", "").lower():
                errors.append({"type": "live_article_noindex", "url": url})
            if parser.canonical != url:
                errors.append({"type": "live_canonical_mismatch", "url": url, "canonical": parser.canonical})
            images = parser.article_images()
            if not images:
                errors.append({"type": "live_missing_article_image_metadata", "url": url})
            article_images.update(images)
            article_schema, breadcrumbs, invalid = parser.schema_counts()
            if article_schema != 1:
                warnings.append({"type": "live_article_schema_count", "url": url, "count": article_schema})
            if breadcrumbs != 1:
                warnings.append({"type": "live_breadcrumb_schema_count", "url": url, "count": breadcrumbs})
            if invalid:
                warnings.append({"type": "live_invalid_jsonld", "url": url, "count": invalid})
            if not parser.has_header_v1:
                warnings.append({"type": "live_nonstandard_header", "url": url})
            if not parser.has_footer_v1:
                warnings.append({"type": "live_nonstandard_footer", "url": url})

    ref_results = fetch_many(all_refs)
    css_extra: set[str] = set()
    for url, result in ref_results.items():
        if result["status"] != 200:
            errors.append({"type": "broken_internal_reference", "url": url, "error": result["error"]})
            continue
        suffix = Path(urlsplit(url).path).suffix.lower()
        if suffix in IMAGE_SUFFIXES and result["bytes"] < 128:
            errors.append({"type": "empty_image", "url": url, "bytes": result["bytes"]})
        if suffix == ".css":
            text = result["data"].decode("utf-8", "replace")
            for value in CSS_URL_RE.findall(text):
                normalized = normalize_url(value, url)
                if normalized:
                    css_extra.add(normalized)
    if css_extra:
        css_results = fetch_many(css_extra)
        for url, result in css_results.items():
            if result["status"] != 200:
                errors.append({"type": "broken_css_reference", "url": url, "error": result["error"]})

    image_results = fetch_many(article_images)
    for url, result in image_results.items():
        if result["status"] != 200:
            errors.append({"type": "article_image_unavailable", "url": url, "error": result["error"]})
        elif result["bytes"] < 1000:
            errors.append({"type": "article_image_too_small", "url": url, "bytes": result["bytes"]})
        elif not result["type"].startswith("image/"):
            errors.append({"type": "article_image_wrong_content_type", "url": url, "content_type": result["type"]})

    archive_order: list[str] = []
    cards_checked = 0
    card_images: set[str] = set()
    for url in sorted(archive_urls, key=lambda value: (value != BASE + "/clanky/", value)):
        parser = parsers.get(url)
        if not parser:
            continue
        for card in parser.cards:
            cards_checked += 1
            target = card.get("href")
            title = card.get("title")
            if not target:
                errors.append({"type": "live_card_missing_link", "page": url, "title": title})
                continue
            archive_order.append(target)
            target_parser = parsers.get(target)
            if target_parser and title != target_parser.h1:
                errors.append({"type": "live_card_title_target_mismatch", "page": url, "title": title, "target": target, "target_h1": target_parser.h1})
            card_images.update(card.get("images", []))
    if archive_order != expected_order:
        errors.append({"type": "live_archive_order_or_coverage_mismatch", "missing": sorted(expected - set(archive_order)), "extra": sorted(set(archive_order) - expected), "archive_count": len(archive_order), "registry_count": len(expected_order)})

    card_image_results = fetch_many(card_images)
    for url, result in card_image_results.items():
        if result["status"] != 200:
            errors.append({"type": "live_card_image_unavailable", "url": url, "error": result["error"]})
        elif result["bytes"] < 1000:
            errors.append({"type": "live_card_image_too_small", "url": url, "bytes": result["bytes"]})

    home_parser = parsers.get(BASE + "/")
    if home_parser and entries:
        latest = entries[0]["_url"]
        home_links = {card.get("href") for card in home_parser.cards if card.get("href")} | home_parser.refs
        if latest not in home_links:
            errors.append({"type": "latest_article_missing_from_live_home", "url": latest})

    health = core[BASE + "/deployment-health.txt"]["data"].decode("utf-8", "replace")
    if "status=ok" not in health:
        errors.append({"type": "deployment_health_not_ok", "content": health[:500]})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live",
        "status": "failed" if errors else "passed",
        "article_count": len(entries),
        "sitemap_urls_checked": len(sitemap_all),
        "html_pages_checked": len(parsers),
        "internal_references_checked": len(ref_results),
        "article_images_checked": len(image_results),
        "card_images_checked": len(card_image_results),
        "cards_checked": cards_checked,
        "archive_pages_checked": len(archive_urls),
        "rss_items": len(rss_urls),
        "news_urls": len(news_urls),
        "errors": errors,
        "warnings": warnings,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--static-report", type=Path, default=Path("/tmp/full-site-static-v2.json"))
    parser.add_argument("--live-report", type=Path, default=Path("/tmp/full-site-live-v2.json"))
    args = parser.parse_args()
    if not args.static and not args.live:
        args.static = True
        args.live = True
    failed = False
    if args.static:
        failed |= static_audit(args.static_report)["status"] != "passed"
    if args.live:
        failed |= live_audit(args.live_report)["status"] != "passed"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
