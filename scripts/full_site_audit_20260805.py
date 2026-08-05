#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import ssl
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
REGISTRY = ROOT / "data" / "published-content-index.json"
DEFAULT_STATIC_REPORT = ROOT / "reports" / "full-site-audit-static-20260805.json"
DEFAULT_LIVE_REPORT = ROOT / "reports" / "full-site-audit-live-20260805.json"
PUBLIC_TOP_LEVEL = {
    "clanky", "pruvodce", "prakticke", "doprava", "organizace", "magazin",
    "recepty", "prirodni-lekarna", "slevy", "herna", "hry", "data", "social",
    "assets", "api", "inzerce", "o-webu", "zapojte-se", "cookies",
    "ochrana-osobnich-udaju", "provozovatel", "prehled-zdroju", "nahled",
}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
ARTICLE_URL_RE = re.compile(r"https://nasekadan\.cz/clanky/[^\"'<>\s?#]+\.html")
ATTR_RE = re.compile(r"\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
SRCSET_RE = re.compile(r"\bsrcset\s*=\s*[\"']([^\"']+)[\"']", re.I)
CSS_URL_RE = re.compile(r"url\(\s*([\"']?)([^)\"']+)\1\s*\)", re.I)
META_RE = re.compile(r"<meta\b([^>]+)>", re.I)
JSONLD_RE = re.compile(r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.I | re.S)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def normalize_url(value: str, base: str = BASE + "/") -> str | None:
    value = unescape(value.strip().strip("'\""))
    if not value or value.startswith("#") or value.lower().startswith(SKIP_SCHEMES):
        return None
    absolute = urljoin(base, value)
    parts = urlsplit(absolute)
    if parts.netloc.lower() not in {"nasekadan.cz", "www.nasekadan.cz"}:
        return None
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    return urlunsplit(("https", "nasekadan.cz", path, "", ""))


def repo_path_for_url(url: str) -> Path | None:
    parts = urlsplit(url)
    path = parts.path
    if path == "/":
        return ROOT / "index.html"
    rel = path.lstrip("/")
    if path.endswith("/"):
        rel += "index.html"
    candidate = ROOT / rel
    if candidate.exists():
        return candidate
    return None


def public_html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if rel.parts[0] in {"research", "node_modules", "vendor", "reports"}:
            continue
        if len(rel.parts) == 1 or rel.parts[0] in PUBLIC_TOP_LEVEL:
            files.append(path)
    return sorted(files)


def attrs(tag_attrs: str) -> dict[str, str]:
    return {
        key.lower(): unescape(value)
        for key, _, value in re.findall(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", tag_attrs, re.S)
    }


def meta_value(text: str, key: str, attr_name: str = "property") -> str:
    for raw in META_RE.findall(text):
        data = attrs(raw)
        if data.get(attr_name, "").lower() == key.lower():
            return data.get("content", "").strip()
    return ""


def exact_h1(text: str) -> str:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.S)
    return clean_text(match.group(1)) if match else ""


def title_value(text: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", text, re.I | re.S)
    return clean_text(match.group(1)) if match else ""


def local_references(text: str, base_url: str) -> set[str]:
    values = set(ATTR_RE.findall(text))
    for srcset in SRCSET_RE.findall(text):
        for part in srcset.split(","):
            values.add(part.strip().split()[0])
    values.update(match[1] for match in CSS_URL_RE.findall(text))
    result: set[str] = set()
    for value in values:
        normalized = normalize_url(value, base_url)
        if normalized:
            result.add(normalized)
    return result


def image_candidates(text: str) -> list[str]:
    found: list[str] = []
    for value in (
        meta_value(text, "og:image", "property"),
        meta_value(text, "twitter:image", "name"),
    ):
        normalized = normalize_url(value)
        if normalized and normalized not in found:
            found.append(normalized)
    for raw in JSONLD_RE.findall(text):
        try:
            data = json.loads(raw)
        except Exception:
            continue
        nodes: list[dict] = []
        if isinstance(data, dict):
            nodes.append(data)
            graph = data.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
        for node in nodes:
            kind = node.get("@type")
            kinds = {kind} if isinstance(kind, str) else set(kind or [])
            if "NewsArticle" not in kinds and "Article" not in kinds:
                continue
            image = node.get("image")
            values = image if isinstance(image, list) else [image]
            for value in values:
                if isinstance(value, dict):
                    value = value.get("url")
                if isinstance(value, str):
                    normalized = normalize_url(value)
                    if normalized and normalized not in found:
                        found.append(normalized)
    for value in re.findall(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", text, re.I):
        normalized = normalize_url(value)
        if normalized and normalized not in found:
            found.append(normalized)
    return found


def load_registry() -> tuple[dict, list[dict]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = data.get("articles") or data.get("entries") or []
    if not isinstance(entries, list):
        raise RuntimeError("Neplatný kanonický registr článků.")
    return data, entries


def published_entries(entries: list[dict]) -> list[dict]:
    now = datetime.now(timezone.utc)
    result: list[tuple[datetime, dict]] = []
    for entry in entries:
        state = entry.get("publication_status")
        if not isinstance(state, str):
            legacy = entry.get("status")
            state = legacy if isinstance(legacy, str) else "published"
        if state in {"draft", "scheduled", "removed"}:
            continue
        value = entry.get("published_at") or entry.get("date_published") or entry.get("published")
        url = entry.get("canonical_url") or entry.get("url")
        if not value or not url:
            continue
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
        if dt <= now:
            result.append((dt, entry))
    result.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in result]


def repair_missing_article_images() -> list[dict]:
    repairs: list[dict] = []
    for path in sorted((ROOT / "clanky").glob("*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "article:published_time" not in text and '"datePublished"' not in text:
            continue
        candidates = image_candidates(text)
        missing = [url for url in candidates if repo_path_for_url(url) is None]
        if not missing:
            continue
        existing = [url for url in candidates if repo_path_for_url(url) is not None]
        fallback = existing[0] if existing else BASE + "/social-card.png"
        fallback_path = repo_path_for_url(fallback)
        if fallback_path is None:
            continue
        original = text
        for missing_url in missing:
            text = text.replace(missing_url, fallback)
            text = text.replace(urlsplit(missing_url).path, urlsplit(fallback).path)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            repairs.append({"file": str(path.relative_to(ROOT)), "missing": missing, "replacement": fallback})
    return repairs


def run_static_audit(repair: bool, report_path: Path) -> dict:
    if repair:
        repairs = repair_missing_article_images()
        subprocess.run([sys.executable, "scripts/enforce_all_article_visibility.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/sort_articles_chronologically.py"], cwd=ROOT, check=True)
    else:
        repairs = []

    data, entries = load_registry()
    published = published_entries(entries)
    expected_urls = {
        normalize_url(entry.get("canonical_url") or entry.get("url") or "")
        for entry in published
    }
    expected_urls.discard(None)

    errors: list[dict] = []
    warnings: list[dict] = []
    html_files = public_html_files()
    local_ref_count = 0
    for path in html_files:
        rel = path.relative_to(ROOT)
        url = BASE + ("/" if rel == Path("index.html") else "/" + str(rel).replace("\\", "/"))
        text = path.read_text(encoding="utf-8", errors="replace")
        refs = local_references(text, url)
        local_ref_count += len(refs)
        for ref in refs:
            ref_path = repo_path_for_url(ref)
            suffix = Path(urlsplit(ref).path).suffix.lower()
            if ref_path is None and suffix in {".html", ".css", ".js", ".json", ".xml", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico", ".woff", ".woff2"}:
                errors.append({"type": "missing_local_reference", "source": str(rel), "target": ref})

        if rel.parts and rel.parts[0] == "clanky" and rel.name not in {"index.html"} and not rel.name.startswith("strana-"):
            h1 = exact_h1(text)
            canonical = meta_value(text, "og:url", "property") or re.search(r'<link\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)', text, re.I)
            if isinstance(canonical, re.Match):
                canonical = canonical.group(1)
            if not h1:
                errors.append({"type": "missing_h1", "file": str(rel)})
            if "noindex" in text.lower():
                errors.append({"type": "published_article_noindex", "file": str(rel)})
            images = image_candidates(text)
            if not images:
                errors.append({"type": "missing_article_image_metadata", "file": str(rel)})
            missing_images = [image for image in images if repo_path_for_url(image) is None]
            if missing_images:
                errors.append({"type": "missing_article_image_file", "file": str(rel), "images": missing_images})
            if len(set(images[:3])) > 1:
                warnings.append({"type": "article_image_metadata_mismatch", "file": str(rel), "images": images[:3]})
            news_count = 0
            breadcrumb_count = 0
            for raw in JSONLD_RE.findall(text):
                try:
                    payload = json.loads(raw)
                except Exception:
                    warnings.append({"type": "invalid_jsonld", "file": str(rel)})
                    continue
                nodes = [payload] if isinstance(payload, dict) else []
                if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
                    nodes.extend(node for node in payload["@graph"] if isinstance(node, dict))
                for node in nodes:
                    kind = node.get("@type") if isinstance(node, dict) else None
                    kinds = {kind} if isinstance(kind, str) else set(kind or [])
                    news_count += int(bool(kinds & {"NewsArticle", "Article"}))
                    breadcrumb_count += int("BreadcrumbList" in kinds)
            if news_count != 1:
                warnings.append({"type": "article_schema_count", "file": str(rel), "count": news_count})
            if breadcrumb_count != 1:
                warnings.append({"type": "breadcrumb_schema_count", "file": str(rel), "count": breadcrumb_count})

    archive_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((ROOT / "clanky").glob("*.html"))
        if path.name == "index.html" or path.name.startswith("strana-")
    )
    archive_urls = {normalize_url(value) for value in re.findall(r'href=[\"']([^\"']*?/clanky/[^\"']+\.html)', archive_text, re.I)}
    archive_urls.discard(None)
    missing_archive = sorted(expected_urls - archive_urls)
    if missing_archive:
        errors.append({"type": "missing_from_archive", "urls": missing_archive})

    rss = (ROOT / "rss.xml").read_text(encoding="utf-8", errors="replace")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8", errors="replace")
    rss_urls = [normalize_url(value) for value in re.findall(r"<link>\s*(https://nasekadan\.cz/clanky/[^<]+\.html)\s*</link>", rss)]
    sitemap_urls = [normalize_url(value) for value in ARTICLE_URL_RE.findall(sitemap)]
    rss_set = {url for url in rss_urls if url}
    sitemap_set = {url for url in sitemap_urls if url}
    if len(rss_urls) != len(rss_set):
        errors.append({"type": "duplicate_rss_urls", "count": len(rss_urls) - len(rss_set)})
    if len(sitemap_urls) != len(sitemap_set):
        errors.append({"type": "duplicate_sitemap_urls", "count": len(sitemap_urls) - len(sitemap_set)})
    if expected_urls - rss_set:
        errors.append({"type": "missing_from_rss", "urls": sorted(expected_urls - rss_set)})
    if expected_urls - sitemap_set:
        errors.append({"type": "missing_from_sitemap", "urls": sorted(expected_urls - sitemap_set)})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "static-repair" if repair else "static",
        "status": "failed" if errors else "passed",
        "article_count": len(expected_urls),
        "html_files_checked": len(html_files),
        "local_references_checked": local_ref_count,
        "repairs": repairs,
        "errors": errors,
        "warnings": warnings,
        "registry_article_count": data.get("article_count"),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def cache_bust(url: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}full_audit={int(time.time() * 1000)}"


def fetch_url(url: str) -> dict:
    request = Request(cache_bust(url), headers={"User-Agent": "NaseKadan-full-site-audit/1.0", "Cache-Control": "no-cache"})
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        with urlopen(request, timeout=35, context=context) as response:
            data = response.read()
            return {
                "url": url,
                "status": response.status,
                "content_type": response.headers.get_content_type(),
                "bytes": len(data),
                "data": data,
                "error": None,
            }
    except Exception as exc:
        return {"url": url, "status": 0, "content_type": "", "bytes": 0, "data": b"", "error": str(exc)}


def batch_fetch(urls: set[str], workers: int = 24) -> dict[str, dict]:
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {executor.submit(fetch_url, url): url for url in sorted(urls)}
        for future in as_completed(future_map):
            result = future.result()
            results[result["url"]] = result
    return results


def parse_xml_urls(text: str) -> list[str]:
    root = ET.fromstring(text)
    values: list[str] = []
    for node in root.iter():
        if node.tag.endswith("loc") and node.text:
            normalized = normalize_url(node.text.strip())
            if normalized:
                values.append(normalized)
    return values


def card_blocks(text: str) -> list[str]:
    return re.findall(r'<article\b[^>]*class=[\"'][^\"']*\barticle-card\b[^\"']*[\"'][^>]*>.*?</article>', text, re.I | re.S)


def run_live_audit(report_path: Path) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    core_urls = {
        BASE + "/", BASE + "/clanky/", BASE + "/rss.xml", BASE + "/sitemap.xml",
        BASE + "/news-sitemap.xml", BASE + "/llms.txt", BASE + "/deployment-health.txt",
        BASE + "/data/published-content-index.json",
    }
    core = batch_fetch(core_urls, workers=8)
    for url, result in core.items():
        if result["status"] != 200:
            errors.append({"type": "core_url_unavailable", "url": url, "error": result["error"]})
    if errors:
        report = {"generated_at": datetime.now(timezone.utc).isoformat(), "mode": "live", "status": "failed", "errors": errors, "warnings": warnings}
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    sitemap_text = core[BASE + "/sitemap.xml"]["data"].decode("utf-8", "replace")
    rss_text = core[BASE + "/rss.xml"]["data"].decode("utf-8", "replace")
    news_text = core[BASE + "/news-sitemap.xml"]["data"].decode("utf-8", "replace")
    home_text = core[BASE + "/"]["data"].decode("utf-8", "replace")
    archive_first = core[BASE + "/clanky/"]["data"].decode("utf-8", "replace")
    registry_data = json.loads(core[BASE + "/data/published-content-index.json"]["data"].decode("utf-8", "replace"))
    entries = registry_data.get("articles") or registry_data.get("entries") or []
    published = published_entries(entries)
    expected_urls = {
        normalize_url(entry.get("canonical_url") or entry.get("url") or "")
        for entry in published
    }
    expected_urls.discard(None)

    try:
        sitemap_urls_list = parse_xml_urls(sitemap_text)
        rss_root = ET.fromstring(rss_text)
        news_urls_list = parse_xml_urls(news_text)
    except Exception as exc:
        errors.append({"type": "invalid_xml", "error": str(exc)})
        sitemap_urls_list = []
        news_urls_list = []
        rss_root = None

    sitemap_urls = set(sitemap_urls_list)
    article_sitemap_list = [url for url in sitemap_urls_list if "/clanky/" in url and not "/strana-" in url]
    if len(article_sitemap_list) != len(set(article_sitemap_list)):
        errors.append({"type": "duplicate_live_sitemap_article_urls", "count": len(article_sitemap_list) - len(set(article_sitemap_list))})
    if len(news_urls_list) != len(set(news_urls_list)):
        errors.append({"type": "duplicate_live_news_urls", "count": len(news_urls_list) - len(set(news_urls_list))})

    rss_urls: list[str] = []
    if rss_root is not None:
        for item in rss_root.findall("./channel/item"):
            link = item.findtext("link")
            normalized = normalize_url(link or "")
            if normalized:
                rss_urls.append(normalized)
    if len(rss_urls) != len(set(rss_urls)):
        errors.append({"type": "duplicate_live_rss_urls", "count": len(rss_urls) - len(set(rss_urls))})

    missing_channels = {
        "sitemap": sorted(expected_urls - set(article_sitemap_list)),
        "rss": sorted(expected_urls - set(rss_urls)),
    }
    for channel, missing in missing_channels.items():
        if missing:
            errors.append({"type": f"missing_live_{channel}", "urls": missing})

    archive_pages = {BASE + "/clanky/"}
    for value in re.findall(r'href=[\"'](/clanky/strana-\d+\.html)[\"']', archive_first, re.I):
        archive_pages.add(BASE + value)

    page_urls = set(sitemap_urls) | archive_pages | {BASE + "/"}
    page_results = batch_fetch(page_urls)
    html_pages: dict[str, str] = {}
    all_refs: set[str] = set()
    for url, result in page_results.items():
        if result["status"] != 200:
            errors.append({"type": "public_page_unavailable", "url": url, "error": result["error"]})
            continue
        ctype = result["content_type"]
        path = urlsplit(url).path
        if ctype in {"text/html", "application/xhtml+xml"} or path.endswith(".html") or path.endswith("/"):
            text = result["data"].decode("utf-8", "replace")
            html_pages[url] = text
            all_refs |= local_references(text, url)

    # Ověřit všechny interní odkazy a assety nalezené ve veřejném HTML.
    ref_results = batch_fetch(all_refs)
    css_refs: set[str] = set()
    for url, result in ref_results.items():
        if result["status"] != 200:
            errors.append({"type": "broken_internal_reference", "url": url, "error": result["error"]})
            continue
        if result["content_type"] == "text/css" or urlsplit(url).path.endswith(".css"):
            text = result["data"].decode("utf-8", "replace")
            css_refs |= local_references(text, url)
        suffix = Path(urlsplit(url).path).suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"}:
            if result["bytes"] < 128:
                errors.append({"type": "empty_or_tiny_image", "url": url, "bytes": result["bytes"]})
    if css_refs:
        css_results = batch_fetch(css_refs)
        for url, result in css_results.items():
            if result["status"] != 200:
                errors.append({"type": "broken_css_reference", "url": url, "error": result["error"]})

    # Přímé ověření všech publikovaných článků proti registru.
    direct_article_results = {url: page_results.get(url) or ref_results.get(url) for url in expected_urls}
    missing_direct = {url for url, result in direct_article_results.items() if not result or result["status"] != 200}
    if missing_direct:
        extra = batch_fetch(missing_direct)
        direct_article_results.update(extra)

    article_h1: dict[str, str] = {}
    article_image_urls: set[str] = set()
    for entry in published:
        url = normalize_url(entry.get("canonical_url") or entry.get("url") or "")
        if not url:
            continue
        result = direct_article_results.get(url)
        if not result or result["status"] != 200:
            errors.append({"type": "published_article_unavailable", "url": url, "error": result.get("error") if result else "not fetched"})
            continue
        text = result["data"].decode("utf-8", "replace")
        h1 = exact_h1(text)
        article_h1[url] = h1
        expected_h1 = entry.get("h1") or entry.get("title") or entry.get("headline")
        if expected_h1 and h1 != expected_h1:
            errors.append({"type": "article_h1_mismatch", "url": url, "actual": h1, "expected": expected_h1})
        if "noindex" in text.lower():
            errors.append({"type": "live_article_noindex", "url": url})
        canonical_match = re.search(r'<link\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)', text, re.I)
        canonical = normalize_url(canonical_match.group(1), url) if canonical_match else None
        if canonical != url:
            errors.append({"type": "canonical_mismatch", "url": url, "canonical": canonical})
        if 'data-site-header="v1"' not in text:
            warnings.append({"type": "article_nonstandard_header", "url": url})
        if 'data-site-footer="v1"' not in text:
            warnings.append({"type": "article_nonstandard_footer", "url": url})
        images = image_candidates(text)
        if not images:
            errors.append({"type": "live_article_missing_image_metadata", "url": url})
        article_image_urls.update(images)
        if len(set(images[:3])) > 1:
            warnings.append({"type": "live_article_image_metadata_mismatch", "url": url, "images": images[:3]})

    image_results = batch_fetch(article_image_urls)
    for url, result in image_results.items():
        if result["status"] != 200:
            errors.append({"type": "article_image_unavailable", "url": url, "error": result["error"]})
        elif result["bytes"] < 1000:
            errors.append({"type": "article_image_too_small", "url": url, "bytes": result["bytes"]})

    # Titulka a archiv: karta musí směřovat na článek se stejným H1 a její obrázek musí být dostupný.
    card_pages = {BASE + "/": home_text}
    for url in archive_pages:
        result = page_results.get(url) or core.get(url)
        if result and result["status"] == 200:
            card_pages[url] = result["data"].decode("utf-8", "replace")
    cards_checked = 0
    card_images: set[str] = set()
    archive_article_urls: set[str] = set()
    for page_url, text in card_pages.items():
        for block in card_blocks(text):
            cards_checked += 1
            h3_match = re.search(r"<h3\b[^>]*>(.*?)</h3>", block, re.I | re.S)
            href_match = re.search(r'<a\b[^>]*class=[\"'][^\"']*\bread-more\b[^\"']*[\"'][^>]*href=[\"']([^\"']+)', block, re.I)
            title = clean_text(h3_match.group(1)) if h3_match else ""
            target = normalize_url(href_match.group(1), page_url) if href_match else None
            if not target:
                errors.append({"type": "article_card_missing_link", "page": page_url, "title": title})
                continue
            archive_article_urls.add(target)
            target_h1 = article_h1.get(target)
            if target_h1 is None:
                target_result = ref_results.get(target) or page_results.get(target)
                if target_result and target_result["status"] == 200:
                    target_h1 = exact_h1(target_result["data"].decode("utf-8", "replace"))
            if target_h1 and title != target_h1:
                errors.append({"type": "article_card_link_title_mismatch", "page": page_url, "title": title, "target": target, "target_h1": target_h1})
            for _, image in CSS_URL_RE.findall(block):
                normalized = normalize_url(image, page_url)
                if normalized:
                    card_images.add(normalized)
    card_image_results = batch_fetch(card_images)
    for url, result in card_image_results.items():
        if result["status"] != 200:
            errors.append({"type": "card_image_unavailable", "url": url, "error": result["error"]})
        elif result["bytes"] < 1000:
            errors.append({"type": "card_image_too_small", "url": url, "bytes": result["bytes"]})

    missing_archive = sorted(expected_urls - archive_article_urls)
    if missing_archive:
        errors.append({"type": "published_article_missing_from_live_archive", "urls": missing_archive})
    latest = normalize_url((published[0].get("canonical_url") or published[0].get("url")) if published else "")
    home_links = {normalize_url(value, BASE + "/") for value in re.findall(r'href=[\"']([^\"']+)', home_text, re.I)}
    if latest and latest not in home_links:
        errors.append({"type": "latest_article_missing_from_home", "url": latest})

    health_text = core[BASE + "/deployment-health.txt"]["data"].decode("utf-8", "replace")
    if "status=ok" not in health_text and "source=" not in health_text:
        errors.append({"type": "invalid_deployment_health", "content": health_text[:300]})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live",
        "status": "failed" if errors else "passed",
        "article_count": len(expected_urls),
        "sitemap_urls_checked": len(page_urls),
        "html_pages_checked": len(html_pages),
        "internal_references_checked": len(ref_results),
        "article_images_checked": len(image_results),
        "card_images_checked": len(card_image_results),
        "cards_checked": cards_checked,
        "archive_pages_checked": len(archive_pages),
        "rss_items": len(rss_urls),
        "news_urls": len(news_urls_list),
        "errors": errors,
        "warnings": warnings,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--static-report", type=Path, default=DEFAULT_STATIC_REPORT)
    parser.add_argument("--live-report", type=Path, default=DEFAULT_LIVE_REPORT)
    args = parser.parse_args()
    if not args.static and not args.live:
        args.static = True
        args.live = True

    failed = False
    if args.static:
        report = run_static_audit(args.repair, args.static_report)
        failed |= report["status"] != "passed"
    if args.live:
        report = run_live_audit(args.live_report)
        failed |= report["status"] != "passed"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
