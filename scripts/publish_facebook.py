#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict

SITE_ROOT = "https://nasekadan.cz"
DEFAULT_PAGE_KEY = "nasekadan"


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: Dict[str, str] = {}
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        values = {str(k).lower(): str(v) for k, v in attrs if k and v is not None}
        if tag.lower() == "meta":
            key = values.get("property") or values.get("name")
            content = values.get("content")
            if key and content:
                self.meta[key.lower()] = content.strip()
        elif tag.lower() == "link" and values.get("rel", "").lower() == "canonical":
            href = values.get("href")
            if href:
                self.meta["canonical"] = href.strip()
        elif tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def parse_article(path: Path) -> dict[str, str]:
    parser = MetaParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    title = parser.meta.get("og:title") or " ".join(parser.title_parts).strip()
    description = parser.meta.get("og:description") or parser.meta.get("description", "")
    canonical = parser.meta.get("canonical") or parser.meta.get("og:url")
    if not canonical:
        canonical = f"{SITE_ROOT}/{path.as_posix().lstrip('./')}"
    image = parser.meta.get("og:image", "")
    return {
        "title": html.unescape(title).strip(),
        "description": html.unescape(description).strip(),
        "url": canonical.strip(),
        "image": image.strip(),
    }


def live_page_ready(article: dict[str, str], timeout: int = 900) -> None:
    deadline = time.time() + timeout
    expected_title = article["title"][:70]
    while time.time() < deadline:
        try:
            request = urllib.request.Request(
                article["url"],
                headers={"User-Agent": "NaseKadanFacebookPublisher/2.1"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8", errors="replace")
                if response.status == 200 and expected_title and expected_title in html.unescape(body):
                    if article["image"]:
                        image_request = urllib.request.Request(
                            article["image"],
                            headers={"User-Agent": "NaseKadanFacebookPublisher/2.1"},
                        )
                        with urllib.request.urlopen(image_request, timeout=20) as image_response:
                            if image_response.status != 200:
                                raise RuntimeError("OG obrázek zatím není veřejně dostupný")
                    return
        except Exception as exc:
            print(f"Čekám na nasazení článku: {exc}", file=sys.stderr)
        time.sleep(20)
    raise TimeoutError(f"Článek se do {timeout} sekund neobjevil na živém webu: {article['url']}")


def build_message(article: dict[str, str]) -> str:
    lines = [f"NOVÝ ČLÁNEK | {article['title']}"]
    if article["description"]:
        lines.extend(["", article["description"]])
    lines.extend(["", "Celý článek najdete na Naše Kadaň:"])
    return "\n".join(lines)


def normalize_key(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")


def resolve_page_credentials() -> tuple[str, str, str]:
    registry_raw = os.environ.get("FACEBOOK_PAGES_JSON", "").strip().lstrip("\ufeff")
    requested_key = normalize_key(os.environ.get("FACEBOOK_PAGE_KEY", DEFAULT_PAGE_KEY))

    if registry_raw:
        try:
            registry = json.loads(registry_raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FACEBOOK_PAGES_JSON není platný JSON") from exc

        pages = registry.get("pages") if isinstance(registry, dict) else None
        if not isinstance(pages, dict):
            raise RuntimeError("FACEBOOK_PAGES_JSON musí obsahovat objekt pages")

        page = pages.get(requested_key)
        if not isinstance(page, dict):
            available = ", ".join(sorted(pages)) or "žádné"
            raise RuntimeError(
                f"V registru není Facebook stránka s klíčem '{requested_key}'. Dostupné klíče: {available}"
            )

        page_id = str(page.get("id", "")).strip()
        token = str(page.get("access_token", "")).strip()
        page_name = str(page.get("name", requested_key)).strip() or requested_key
        if not page_id or not token:
            raise RuntimeError(f"Stránka '{requested_key}' nemá id nebo access_token")
        return page_id, token, page_name

    page_id = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
    token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
    if not page_id or not token:
        raise RuntimeError(
            "Chybí FACEBOOK_PAGES_JSON nebo starší dvojice FACEBOOK_PAGE_ID/FACEBOOK_PAGE_ACCESS_TOKEN"
        )
    return page_id, token, requested_key


def publish(article: dict[str, str]) -> dict[str, str]:
    page_id, token, page_name = resolve_page_credentials()
    graph_version = os.environ.get("FACEBOOK_GRAPH_VERSION", "").strip().strip("/")
    prefix = f"/{graph_version}" if graph_version else ""
    endpoint = f"https://graph.facebook.com{prefix}/{urllib.parse.quote(page_id)}/feed"
    payload = urllib.parse.urlencode(
        {
            "message": build_message(article),
            "link": article["url"],
            "access_token": token,
        }
    ).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Facebook Graph API vrátil HTTP {exc.code}: {detail}") from exc
    post_id = str(result.get("id", ""))
    if not post_id:
        raise RuntimeError(f"Facebook nevrátil ID příspěvku: {result}")
    return {"post_id": post_id, "page_id": page_id, "page_name": page_name}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("articles", nargs="+", help="Cesty k nově publikovaným HTML článkům")
    parser.add_argument("--skip-wait", action="store_true")
    args = parser.parse_args()

    for raw_path in args.articles:
        path = Path(raw_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        article = parse_article(path)
        if not article["title"] or not article["url"]:
            raise RuntimeError(f"Článek nemá platný title nebo canonical URL: {path}")
        if not args.skip_wait:
            live_page_ready(article)
        published = publish(article)
        print(
            json.dumps(
                {
                    "article": article["url"],
                    "facebook_post_id": published["post_id"],
                    "facebook_page_id": published["page_id"],
                    "facebook_page_name": published["page_name"],
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
