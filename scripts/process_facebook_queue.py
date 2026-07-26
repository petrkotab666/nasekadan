#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import publish_facebook

ROOT = Path(__file__).resolve().parents[1]
PENDING_FILE = ROOT / ".github" / "facebook-publish-pending.txt"
PUBLISHED_DIR = ROOT / ".github" / "facebook-published"
STATUS_FILE = ROOT / ".github" / "facebook-last-status.json"
CONFIG_FILE = ROOT / ".github" / "facebook-publisher-config.json"
DEFAULT_TIMEOUT = 1200
GENERIC_IMAGES = {
    "https://nasekadan.cz/social-card.png",
    "https://www.nasekadan.cz/social-card.png",
}
JSON_LD_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.I | re.S,
)


def normalize_article_path(raw: str) -> str:
    value = raw.strip().replace("\\", "/").lstrip("./")
    if not re.fullmatch(r"clanky/[^/]+\.html", value):
        raise ValueError(f"Nepovolená cesta článku: {raw!r}")
    path = ROOT / value
    if not path.is_file():
        raise FileNotFoundError(path)
    return value


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = list(dict.fromkeys(values))
    content = "".join(f"{value}\n" for value in unique)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def marker_path(article_path: str) -> Path:
    digest = hashlib.sha256(article_path.encode("utf-8")).hexdigest()[:10]
    slug = Path(article_path).stem
    return PUBLISHED_DIR / f"{slug}-{digest}.json"


def load_config() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "auto_discover": False,
        "auto_discover_since": "",
        "max_posts_per_run": 1,
    }
    if not CONFIG_FILE.exists():
        return defaults
    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{CONFIG_FILE} není platný JSON.") from exc
    if isinstance(raw, dict):
        defaults.update(raw)
    return defaults


def parse_datetime(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def schema_types(node: dict[str, Any]) -> set[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def article_published_at(path: Path) -> datetime | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw in JSON_LD_RE.findall(text):
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue
        nodes: list[dict[str, Any]] = []
        if isinstance(data, dict):
            nodes.append(data)
            graph = data.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
        elif isinstance(data, list):
            nodes.extend(node for node in data if isinstance(node, dict))
        for node in nodes:
            if schema_types(node) & {"NewsArticle", "Article"}:
                return parse_datetime(str(node.get("datePublished", "")))
    return None


def discover_recent_articles(config: dict[str, Any]) -> list[str]:
    if not bool(config.get("auto_discover")):
        return []
    since = parse_datetime(str(config.get("auto_discover_since", "")))
    if since is None:
        raise RuntimeError(
            "Automatické dohledávání je zapnuté, ale auto_discover_since není platné ISO datum."
        )

    found: list[tuple[datetime, str]] = []
    for path in sorted((ROOT / "clanky").glob("*.html")):
        if path.name == "index.html":
            continue
        article_path = path.relative_to(ROOT).as_posix()
        if marker_path(article_path).exists():
            continue
        published = article_published_at(path)
        if published is None or published < since:
            continue
        found.append((published, article_path))
    found.sort(key=lambda item: (item[0], item[1]))
    return [article_path for _, article_path in found]


def cache_busted_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    query.append(("facebook_check", str(int(time.time()))))
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query), parts.fragment)
    )


def fetch_bytes(url: str, user_agent: str) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(
        cache_busted_url(url),
        headers={
            "User-Agent": user_agent,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return response.status, headers, response.read()


def png_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) >= 24 and data.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", data[16:24])
    return None


def validate_source_article(article_path: str, article: dict[str, str]) -> None:
    image = article.get("image", "").strip()
    if not image:
        raise RuntimeError(f"{article_path} nemá og:image.")
    if image in GENERIC_IMAGES or image.endswith("/social-card.png"):
        raise RuntimeError(
            f"{article_path} stále používá obecný obrázek social-card.png."
        )
    if not image.startswith("https://nasekadan.cz/"):
        raise RuntimeError(
            f"{article_path} používá neočekávanou adresu OG obrázku: {image}"
        )
    if not article.get("url", "").startswith("https://nasekadan.cz/clanky/"):
        raise RuntimeError(
            f"{article_path} má neočekávanou canonical URL: {article.get('url', '')}"
        )


def wait_until_live(article_path: str, article: dict[str, str], timeout: int) -> None:
    deadline = time.time() + timeout
    expected_title = article["title"]
    expected_image = article["image"]
    last_error = "živá stránka dosud nebyla zkontrolována"

    while time.time() < deadline:
        try:
            status, _, body = fetch_bytes(
                article["url"],
                "NaseKadanFacebookPublisher/4.0",
            )
            if status != 200:
                raise RuntimeError(f"článek vrací HTTP {status}")

            parser = publish_facebook.MetaParser()
            parser.feed(body.decode("utf-8", errors="replace"))
            live_title = parser.meta.get("og:title") or " ".join(
                parser.title_parts
            ).strip()
            live_image = parser.meta.get("og:image", "").strip()

            if expected_title[:70] not in live_title:
                raise RuntimeError("živá stránka ještě nemá očekávaný titulek")
            if live_image != expected_image:
                raise RuntimeError(
                    f"živá stránka ještě nemá správný OG obrázek: {live_image or 'chybí'}"
                )

            image_status, image_headers, image_data = fetch_bytes(
                expected_image,
                "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            )
            if image_status != 200:
                raise RuntimeError(f"OG obrázek vrací HTTP {image_status}")
            content_type = (
                image_headers.get("content-type", "")
                .split(";", 1)[0]
                .strip()
                .lower()
            )
            if content_type != "image/png":
                raise RuntimeError(
                    f"OG obrázek má Content-Type {content_type or 'neuveden'}"
                )
            dimensions = png_dimensions(image_data)
            if dimensions != (1200, 630):
                raise RuntimeError(
                    f"OG obrázek má rozměry {dimensions}, očekáváno 1200 × 630"
                )
            if len(image_data) < 10_000:
                raise RuntimeError(
                    f"OG obrázek je podezřele malý: {len(image_data)} B"
                )

            print(
                f"Připraveno pro Facebook: {article_path}, "
                f"OG obrázek {dimensions[0]} × {dimensions[1]}, {len(image_data)} B"
            )
            return
        except Exception as exc:
            last_error = str(exc)
            print(
                f"Čekám na správné nasazení {article_path}: {last_error}",
                file=sys.stderr,
            )
            time.sleep(20)

    raise TimeoutError(
        f"Článek nebyl do {timeout} sekund připraven pro Facebook: {last_error}"
    )


def sanitize_error(exc: Exception) -> str:
    text = str(exc).replace("\n", " ").strip()
    lowered = text.lower()
    if "access token vypršel" in lowered or (
        "error validating access token" in lowered and "expired" in lowered
    ):
        return (
            "Facebook access token vypršel. Spusťte tools/nastavit-facebook.ps1 "
            "a uložte nový dlouhodobý Page Access Token."
        )
    if "facebook_page_access_token" in lowered and "chybí" in lowered:
        return "Chybí přihlašovací údaje Facebook stránky v GitHub Secrets."
    text = re.sub(r"[A-Za-z0-9_\-]{32,}", "[redacted]", text)
    return text[:500] or exc.__class__.__name__


def save_status(results: list[dict[str, Any]]) -> bool:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if STATUS_FILE.exists():
        try:
            existing = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        if isinstance(existing, dict) and existing.get("results") == results:
            print("Facebook stav se nezměnil; soubor se nepřepisuje.")
            return False

    STATUS_FILE.write_text(
        json.dumps(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("articles", nargs="*")
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("FACEBOOK_WAIT_TIMEOUT", DEFAULT_TIMEOUT)),
    )
    parser.add_argument("--discover-only", action="store_true")
    args = parser.parse_args()

    config = load_config()
    discovered = discover_recent_articles(config)
    if args.discover_only:
        print("\n".join(discovered))
        return 0

    pending: list[str] = []
    for raw in read_lines(PENDING_FILE) + discovered + args.articles:
        try:
            normalized = normalize_article_path(raw)
        except Exception as exc:
            print(
                f"Přeskakuji neplatnou položku fronty {raw!r}: {exc}",
                file=sys.stderr,
            )
            continue
        if not marker_path(normalized).exists() and normalized not in pending:
            pending.append(normalized)

    write_lines(PENDING_FILE, pending)
    if not pending:
        save_status([{"state": "idle", "message": "Fronta je prázdná."}])
        print("Facebook fronta je prázdná.")
        return 0

    try:
        credentials = publish_facebook.validate_page_access()
        print(
            "Facebook přihlášení je platné pro stránku "
            f"{credentials.get('page_name')} ({credentials.get('page_id')})."
        )
    except Exception as exc:
        error = sanitize_error(exc)
        results = [
            {
                "state": "action_required",
                "article_path": article_path,
                "error": error,
            }
            for article_path in pending
        ]
        save_status(results)
        print(error, file=sys.stderr)
        return 1

    max_posts = max(1, int(config.get("max_posts_per_run", 1) or 1))
    results: list[dict[str, Any]] = []
    remaining: list[str] = []
    failed = False
    attempted = 0

    for article_path in pending:
        if attempted >= max_posts:
            remaining.append(article_path)
            continue
        attempted += 1
        try:
            article = publish_facebook.parse_article(ROOT / article_path)
            validate_source_article(article_path, article)
            wait_until_live(article_path, article, args.timeout)
            published = publish_facebook.publish(article)

            marker = marker_path(article_path)
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(
                json.dumps(
                    {
                        "article_path": article_path,
                        "article_url": article["url"],
                        "og_image": article["image"],
                        "facebook_post_id": published["post_id"],
                        "facebook_page_id": published["page_id"],
                        "facebook_page_name": published["page_name"],
                        "existing_post_detected": published.get("existing") == "true",
                        "published_at": datetime.now(timezone.utc).isoformat(),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            state = (
                "already_published"
                if published.get("existing") == "true"
                else "published"
            )
            results.append(
                {
                    "state": state,
                    "article_path": article_path,
                    "article_url": article["url"],
                    "facebook_post_id": published["post_id"],
                }
            )
            print(
                f"Facebook hotovo: {article_path} -> {published['post_id']} ({state})"
            )
        except Exception as exc:
            failed = True
            remaining.append(article_path)
            error = sanitize_error(exc)
            results.append(
                {
                    "state": "failed",
                    "article_path": article_path,
                    "error": error,
                }
            )
            print(
                f"Publikování selhalo pro {article_path}: {error}",
                file=sys.stderr,
            )

    write_lines(PENDING_FILE, remaining)
    save_status(results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
