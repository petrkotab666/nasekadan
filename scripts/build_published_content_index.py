#!/usr/bin/env python3
"""Build a canonical machine-readable index of Naše Kadaň published content.

The live site is treated as the publication source of truth. Repository HTML is
used for rich metadata and history, while the live homepage, archive, RSS,
sitemap, news sitemap and article URLs determine current public state.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from verify_published_article_set import canonical_articles

BASE_DEFAULT = "https://nasekadan.cz"
ARTICLE_PATH_RE = re.compile(r"/clanky/([^/?#]+\.html)", re.I)
TAG_RE = re.compile(r'<p[^>]+class=["\'][^"\']*\btag\b[^"\']*["\'][^>]*>(.*?)</p>', re.I | re.S)

PLACES = [
    "Kadaň", "Klášterec nad Ohří", "Chomutov", "Žatec", "Podbořany", "Most",
    "Tušimice", "Prunéřov", "Nechranice", "Ústecký kraj", "Karlovarský kraj",
    "Birmingham", "Čáslav", "Jáchymov", "Vejprty", "Jirkov",
]
ORGANIZATIONS = [
    "Město Kadaň", "Městská policie Kadaň", "Nemocnice Kadaň", "FK Tatran Kadaň",
    "PK Slávie Kadaň", "SK Kadaň", "RADKA", "Ústecký kraj", "ČEZ", "ČEZ ESCO",
    "Zdravotnická záchranná služba Ústeckého kraje", "ZZS Ústeckého kraje",
    "Dáme Kadani novou šanci", "ODS", "ANO", "Piráti", "ESO market",
]
TOPIC_MAP = {
    "nemocnic": "nemocnice-a-zdravotnictvi",
    "polici": "mestska-policie-a-bezpecnost",
    "doprav": "doprava",
    "vlak": "zeleznice",
    "hřišt": "hriste-a-sportoviste",
    "hrist": "hriste-a-sportoviste",
    "sport": "sport",
    "hokej": "hokej",
    "plav": "plavani",
    "gymnast": "gymnastika",
    "volb": "komunalni-volby-2026",
    "kandid": "komunalni-volby-2026",
    "slovan": "slovan-bydleni-investice",
    "koupali": "koupaliste",
    "klášter": "klaster-a-historie",
    "klaster": "klaster-a-historie",
    "výluk": "vyluky-a-uzavirky",
    "vyluk": "vyluky-a-uzavirky",
    "požár": "pozary-a-rizika",
    "pozar": "pozary-a-rizika",
    "elektr": "energetika",
    "jader": "energetika",
    "fve": "energetika",
    "bess": "energetika",
    "kultur": "kultura",
    "galeri": "kultura",
    "císař": "historie-kadane",
    "cisar": "historie-kadane",
    "podchod": "verejny-prostor",
    "murál": "verejny-prostor",
    "mural": "verejny-prostor",
}
STOP_PERSON = {
    "Naše Kadaň", "Nase Kadan", "Město Kadaň", "Mestska Policie Kadaň",
    "Ústecký Kraj", "Ustecky Kraj", "Kadaň", "Kadan",
}


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def first_match(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        m = re.search(pattern, text, re.I | re.S)
        if m:
            return strip_tags(m.group(1))
    return None


def extract_title(text: str) -> str:
    title = first_match(text, [r"<title[^>]*>(.*?)</title>"]) or ""
    return re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", title).strip()


def extract_h1(text: str) -> str:
    return first_match(text, [r"<h1\b[^>]*>(.*?)</h1>"]) or ""


def extract_canonical(text: str, fallback: str) -> str:
    value = first_match(text, [
        r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',
        r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']',
    ])
    return value or fallback


def extract_datetime(text: str, kind: str) -> str | None:
    prop = "article:published_time" if kind == "published" else "article:modified_time"
    json_key = "datePublished" if kind == "published" else "dateModified"
    value = first_match(text, [
        rf'<meta\b[^>]*property=["\']{re.escape(prop)}["\'][^>]*content=["\']([^"\']+)',
        rf'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']{re.escape(prop)}["\']',
        rf'["\']{json_key}["\']\s*:\s*["\']([^"\']+)',
    ])
    return value


def extract_tag(text: str) -> str:
    m = TAG_RE.search(text)
    return strip_tags(m.group(1)) if m else ""


def normalize_token(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def find_people(text: str, title: str) -> list[str]:
    sample = strip_tags(title + " " + text[:9000])
    candidates = re.findall(r"\b(?:[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+)(?:\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+){1,2}\b", sample)
    out: list[str] = []
    for value in candidates:
        value = value.strip()
        if value in STOP_PERSON or any(org in value or value in org for org in ORGANIZATIONS):
            continue
        if any(place in value or value in place for place in PLACES):
            continue
        if value not in out:
            out.append(value)
        if len(out) >= 12:
            break
    return out


def classify(text: str, title: str, tag: str) -> tuple[list[str], list[str], list[str], list[str]]:
    plain = strip_tags(text[:16000])
    haystack = f"{title} {tag} {plain}"
    places = [x for x in PLACES if x.lower() in haystack.lower()]
    orgs = [x for x in ORGANIZATIONS if x.lower() in haystack.lower()]
    topics: list[str] = []
    normalized = normalize_token(haystack).replace("-", " ")
    for needle, topic in TOPIC_MAP.items():
        n = normalize_token(needle).replace("-", " ")
        if n and n in normalized and topic not in topics:
            topics.append(topic)
    tag_parts = [strip_tags(x) for x in re.split(r"[·|•]", tag) if strip_tags(x)]
    for item in tag_parts:
        token = normalize_token(item)
        if token and not re.fullmatch(r"\d{1,2}-?\d{0,2}-?\d{0,4}", token) and token not in topics:
            topics.append(token)
    people = find_people(text, title)
    cases: list[str] = []
    for topic in topics:
        if any(key in topic for key in ("volby", "slovan", "nemocnice", "koupaliste", "policie", "energetika")):
            cases.append(topic)
    return people, orgs, places, cases


def fingerprint(title: str, people: list[str], orgs: list[str], places: list[str], topics: list[str], cases: list[str]) -> str:
    terms = [normalize_token(title)] + [normalize_token(x) for x in people + orgs + places + topics + cases]
    payload = "|".join(sorted(set(x for x in terms if x)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def git_value(path: str, fmt: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", f"--format={fmt}", "--", path],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return result or None
    except Exception:
        return None


def fetch(url: str, timeout: int = 18) -> tuple[int | None, str, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "nasekadan-canonical-index/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return response.status, data.decode(charset, errors="replace"), response.headers.get("Content-Type")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return exc.code, body, exc.headers.get("Content-Type") if exc.headers else None
    except Exception:
        return None, "", None


def live_snapshot(base: str) -> dict:
    base = base.rstrip("/")
    endpoints = {
        "homepage": f"{base}/",
        "archive": f"{base}/clanky/",
        "rss": f"{base}/rss.xml",
        "sitemap": f"{base}/sitemap.xml",
        "news_sitemap": f"{base}/news-sitemap.xml",
        "deployment_health": f"{base}/deployment-health.txt",
    }
    result: dict[str, dict] = {}
    for key, url in endpoints.items():
        status, text, content_type = fetch(url)
        result[key] = {"status": status, "text": text, "content_type": content_type}

    archive_text = result["archive"]["text"]
    pages = sorted(set(re.findall(r'href=["\'](?:https?://[^/]+)?(/clanky/strana-\d+\.html)', archive_text, re.I)))
    page_status: dict[str, int | None] = {}
    for path in pages[:30]:
        status, text, _ = fetch(base + path)
        page_status[path] = status
        if status == 200:
            archive_text += "\n" + text
    result["archive"]["text"] = archive_text
    result["archive"]["pages"] = page_status
    return result


def article_names(text: str) -> set[str]:
    return {m.group(1) for m in ARTICLE_PATH_RE.finditer(text or "")}


def current_repo_entries(root: Path, base: str) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for rel in canonical_articles(root):
        path = root / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        title = extract_title(text)
        h1 = extract_h1(text)
        canonical = extract_canonical(text, f"{base.rstrip('/')}/{rel}")
        tag = extract_tag(text)
        people, orgs, places, cases = classify(text, title or h1, tag)
        topics = []
        for item in re.split(r"[·|•]", tag):
            token = normalize_token(strip_tags(item))
            if token and token not in topics and not token.startswith("20"):
                topics.append(token)
        normalized = normalize_token(f"{title} {tag} {strip_tags(text[:12000])}").replace("-", " ")
        for needle, topic in TOPIC_MAP.items():
            if normalize_token(needle).replace("-", " ") in normalized and topic not in topics:
                topics.append(topic)
        published = extract_datetime(text, "published")
        modified = extract_datetime(text, "modified") or published
        entries[path.name] = {
            "slug": path.name,
            "title": title or h1,
            "h1": h1 or title,
            "url": canonical,
            "published_at": published,
            "modified_at": modified,
            "last_change": git_value(rel, "%cI") or modified,
            "persons": people,
            "organizations": orgs,
            "places": places,
            "cases": cases,
            "topics": topics,
            "fingerprint": fingerprint(title or h1, people, orgs, places, topics, cases),
            "source_commit": git_value(rel, "%H"),
            "source_path": rel,
            "source_kind": "repository",
        }
    return entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="data/published-content-index.json")
    parser.add_argument("--live-base", default=BASE_DEFAULT)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = root / args.output
    previous: dict = {}
    if output.is_file():
        try:
            previous = json.loads(output.read_text(encoding="utf-8"))
        except Exception:
            previous = {}

    live = live_snapshot(args.live_base)
    required = ["homepage", "archive", "rss", "sitemap", "news_sitemap", "deployment_health"]
    live_ok = all(live[key]["status"] == 200 for key in required)
    if args.require_live and not live_ok:
        bad = {key: live[key]["status"] for key in required if live[key]["status"] != 200}
        raise SystemExit(f"Live verification failed: {bad}")

    entries = current_repo_entries(root, args.live_base)
    surfaces = {key: article_names(live[key]["text"]) for key in ["homepage", "archive", "rss", "sitemap", "news_sitemap"]}
    observed_live = set().union(*surfaces.values())

    # Preserve historical evidence and discover live-only pages.
    for old in previous.get("articles", []):
        slug = old.get("slug")
        if slug and slug not in entries:
            copy = dict(old)
            copy["source_kind"] = "historical-registry"
            entries[slug] = copy
    for slug in sorted(observed_live):
        if slug in entries:
            continue
        url = f"{args.live_base.rstrip('/')}/clanky/{slug}"
        status, text, _ = fetch(url)
        if status == 200:
            title = extract_title(text)
            h1 = extract_h1(text)
            tag = extract_tag(text)
            people, orgs, places, cases = classify(text, title or h1, tag)
            topics = [normalize_token(x) for x in re.split(r"[·|•]", tag) if normalize_token(x)]
            entries[slug] = {
                "slug": slug, "title": title or h1, "h1": h1 or title, "url": url,
                "published_at": extract_datetime(text, "published"),
                "modified_at": extract_datetime(text, "modified"), "last_change": None,
                "persons": people, "organizations": orgs, "places": places,
                "cases": cases, "topics": topics,
                "fingerprint": fingerprint(title or h1, people, orgs, places, topics, cases),
                "source_commit": None, "source_path": None, "source_kind": "live-only",
            }

    articles: list[dict] = []
    for slug, item in entries.items():
        url = item.get("url") or f"{args.live_base.rstrip('/')}/clanky/{slug}"
        direct_status, direct_text, _ = fetch(url) if live_ok else (None, "", None)
        live_h1 = extract_h1(direct_text) if direct_status == 200 else ""
        h1_match = bool(direct_status == 200 and item.get("h1") and normalize_token(live_h1) == normalize_token(item.get("h1", "")))
        if item.get("source_kind") == "live-only" and direct_status == 200:
            h1_match = True
        surface_state = {
            "direct": direct_status == 200,
            "homepage": slug in surfaces["homepage"],
            "archive": slug in surfaces["archive"],
            "rss": slug in surfaces["rss"],
            "sitemap": slug in surfaces["sitemap"],
            "news_sitemap": slug in surfaces["news_sitemap"],
            "h1_match": h1_match,
        }
        if not live_ok:
            state = "verification-unavailable"
        elif surface_state["direct"] and surface_state["archive"] and surface_state["rss"] and surface_state["sitemap"] and h1_match:
            state = "published-live"
        elif surface_state["direct"]:
            state = "published-live-surface-incomplete"
        elif item.get("source_kind") == "historical-registry":
            state = "historical-not-live"
        else:
            state = "repository-not-live"
        enriched = dict(item)
        enriched["live_state"] = state
        enriched["surfaces"] = surface_state
        enriched["live_h1"] = live_h1 or None
        articles.append(enriched)

    articles.sort(key=lambda x: (x.get("published_at") or "", x.get("slug") or ""), reverse=True)
    by_fp: defaultdict[str, list[str]] = defaultdict(list)
    by_title: defaultdict[str, list[str]] = defaultdict(list)
    for item in articles:
        if item.get("fingerprint"):
            by_fp[item["fingerprint"]].append(item["slug"])
        if item.get("title"):
            by_title[normalize_token(item["title"])].append(item["slug"])
    duplicates = []
    for kind, mapping in (("fingerprint", by_fp), ("title", by_title)):
        for key, slugs in mapping.items():
            if len(slugs) > 1:
                duplicates.append({"kind": kind, "key": key, "slugs": sorted(slugs)})

    health_text = live["deployment_health"]["text"].strip() if live["deployment_health"]["status"] == 200 else None
    payload = {
        "schema": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_base": args.live_base.rstrip("/"),
        "live_verification_ok": live_ok,
        "live_endpoint_status": {key: live[key]["status"] for key in required},
        "deployment_health": health_text,
        "article_count": len(articles),
        "published_live_count": sum(1 for x in articles if x["live_state"].startswith("published-live")),
        "articles": articles,
        "duplicate_candidates": duplicates,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Canonical published-content index: {len(articles)} entries, live_ok={live_ok}, duplicates={len(duplicates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
