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
from typing import Any, Dict

SITE_ROOT = "https://nasekadan.cz"
DEFAULT_PAGE_KEY = "nasekadan"
DEFAULT_GRAPH_VERSION = "v25.0"


class FacebookCredentialError(RuntimeError):
    pass


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


def graph_version() -> str:
    value = os.environ.get("FACEBOOK_GRAPH_VERSION", DEFAULT_GRAPH_VERSION).strip().strip("/")
    return value or DEFAULT_GRAPH_VERSION


def graph_endpoint(path: str) -> str:
    return f"https://graph.facebook.com/{graph_version()}/{path.lstrip('/')}"


def normalize_key(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")


def resolve_page_credentials() -> tuple[str, str, str]:
    requested_key = normalize_key(os.environ.get("FACEBOOK_PAGE_KEY", DEFAULT_PAGE_KEY))
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
    token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
    if page_id and token:
        return page_id, token, requested_key

    registry_raw = os.environ.get("FACEBOOK_PAGES_JSON", "").strip().lstrip("\ufeff")
    if registry_raw:
        try:
            registry = json.loads(registry_raw)
        except json.JSONDecodeError as exc:
            raise FacebookCredentialError("FACEBOOK_PAGES_JSON není platný JSON.") from exc
        pages = registry.get("pages") if isinstance(registry, dict) else None
        if not isinstance(pages, dict):
            raise FacebookCredentialError("FACEBOOK_PAGES_JSON musí obsahovat objekt pages.")
        page = pages.get(requested_key)
        if not isinstance(page, dict):
            available = ", ".join(sorted(pages)) or "žádné"
            raise FacebookCredentialError(
                f"V registru není Facebook stránka s klíčem '{requested_key}'. Dostupné klíče: {available}."
            )
        page_id = str(page.get("id", "")).strip()
        token = str(page.get("access_token", "")).strip()
        page_name = str(page.get("name", requested_key)).strip() or requested_key
        if not page_id or not token:
            raise FacebookCredentialError(f"Stránka '{requested_key}' nemá id nebo access_token.")
        return page_id, token, page_name

    raise FacebookCredentialError(
        "Chybí FACEBOOK_PAGE_ID/FACEBOOK_PAGE_ACCESS_TOKEN nebo FACEBOOK_PAGES_JSON."
    )


def stable_graph_error(detail: str, http_code: int) -> str:
    try:
        payload = json.loads(detail)
    except json.JSONDecodeError:
        payload = {}
    error = payload.get("error") if isinstance(payload, dict) else None
    error = error if isinstance(error, dict) else {}
    message = str(error.get("message", "")).strip()
    code = int(error.get("code", 0) or 0)
    subcode = int(error.get("error_subcode", 0) or 0)

    if code == 190 and subcode in {463, 467}:
        return (
            "Facebook access token vypršel. Spusťte znovu "
            "tools/nastavit-facebook.ps1 a uložte nový dlouhodobý Page Access Token."
        )
    if code == 190:
        return (
            "Facebook access token je neplatný. Spusťte znovu "
            "tools/nastavit-facebook.ps1."
        )
    if code == 200:
        return (
            "Facebook token nemá oprávnění publikovat. Jsou potřeba "
            "pages_show_list, pages_read_engagement a pages_manage_posts."
        )
    if message:
        return f"Facebook Graph API odmítlo požadavek (HTTP {http_code}, kód {code or 'neuveden'}): {message}"
    return f"Facebook Graph API vrátilo HTTP {http_code}."


def request_json(
    endpoint: str,
    *,
    params: dict[str, str],
    method: str = "GET",
    timeout: int = 45,
) -> dict[str, Any]:
    encoded = urllib.parse.urlencode(params)
    if method == "GET":
        request = urllib.request.Request(f"{endpoint}?{encoded}", method="GET")
    else:
        request = urllib.request.Request(
            endpoint,
            data=encoded.encode("utf-8"),
            method=method,
        )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise FacebookCredentialError(stable_graph_error(detail, exc.code)) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Facebook Graph API není dostupné: {exc.reason}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Facebook Graph API vrátilo neočekávanou odpověď.")
    return data


def validate_page_access() -> dict[str, Any]:
    page_id, token, configured_name = resolve_page_credentials()
    page = request_json(
        graph_endpoint(page_id),
        params={"fields": "id,name", "access_token": token},
    )
    returned_id = str(page.get("id", "")).strip()
    if returned_id != page_id:
        raise FacebookCredentialError(
            f"Facebook token patří jiné stránce: očekáváno {page_id}, vráceno {returned_id or 'nic'}."
        )
    result: dict[str, Any] = {
        "page_id": page_id,
        "page_name": str(page.get("name", configured_name)).strip() or configured_name,
        "graph_version": graph_version(),
    }

    app_id = os.environ.get("FACEBOOK_APP_ID", "").strip()
    app_secret = os.environ.get("FACEBOOK_APP_SECRET", "").strip()
    if app_id and app_secret:
        debug = request_json(
            graph_endpoint("debug_token"),
            params={
                "input_token": token,
                "access_token": f"{app_id}|{app_secret}",
            },
        )
        data = debug.get("data")
        if isinstance(data, dict):
            if data.get("is_valid") is False:
                raise FacebookCredentialError("Facebook token je podle debug_token neplatný.")
            result["expires_at"] = int(data.get("expires_at", 0) or 0)
            result["data_access_expires_at"] = int(data.get("data_access_expires_at", 0) or 0)
            scopes = data.get("scopes")
            if isinstance(scopes, list):
                result["scopes"] = [str(scope) for scope in scopes]
    return result


def live_page_ready(article: dict[str, str], timeout: int = 900) -> None:
    deadline = time.time() + timeout
    expected_title = article["title"][:70]
    while time.time() < deadline:
        try:
            request = urllib.request.Request(
                article["url"],
                headers={"User-Agent": "NaseKadanFacebookPublisher/4.0"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8", errors="replace")
                if response.status == 200 and expected_title and expected_title in html.unescape(body):
                    if article["image"]:
                        image_request = urllib.request.Request(
                            article["image"],
                            headers={"User-Agent": "facebookexternalhit/1.1"},
                        )
                        with urllib.request.urlopen(image_request, timeout=20) as image_response:
                            if image_response.status != 200:
                                raise RuntimeError("OG obrázek zatím není veřejně dostupný.")
                    return
        except Exception as exc:
            print(f"Čekám na nasazení článku: {exc}", file=sys.stderr)
        time.sleep(20)
    raise TimeoutError(
        f"Článek se do {timeout} sekund neobjevil na živém webu: {article['url']}"
    )


def build_message(article: dict[str, str]) -> str:
    lines = [f"NOVÝ ČLÁNEK | {article['title']}"]
    if article["description"]:
        lines.extend(["", article["description"]])
    lines.extend(["", "Celý článek najdete na Naše Kadaň:"])
    return "\n".join(lines)


def _contains_url(value: Any, wanted_url: str) -> bool:
    normalized_wanted = wanted_url.rstrip("/")
    if isinstance(value, str):
        return normalized_wanted in html.unescape(value).rstrip("/")
    if isinstance(value, dict):
        return any(_contains_url(item, wanted_url) for item in value.values())
    if isinstance(value, list):
        return any(_contains_url(item, wanted_url) for item in value)
    return False


def find_existing_post(article_url: str) -> dict[str, str] | None:
    page_id, token, page_name = resolve_page_credentials()
    try:
        response = request_json(
            graph_endpoint(f"{page_id}/posts"),
            params={
                "fields": "id,message,permalink_url,attachments{url,unshimmed_url,target}",
                "limit": "100",
                "access_token": token,
            },
        )
    except Exception as exc:
        print(f"Kontrola duplicitního Facebook příspěvku nebyla dostupná: {exc}", file=sys.stderr)
        return None

    rows = response.get("data")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and _contains_url(row, article_url):
            post_id = str(row.get("id", "")).strip()
            if post_id:
                return {
                    "post_id": post_id,
                    "page_id": page_id,
                    "page_name": page_name,
                    "existing": "true",
                }
    return None


def publish(article: dict[str, str]) -> dict[str, str]:
    existing = find_existing_post(article["url"])
    if existing:
        return existing

    page_id, token, page_name = resolve_page_credentials()
    result = request_json(
        graph_endpoint(f"{urllib.parse.quote(page_id)}/feed"),
        params={
            "message": build_message(article),
            "link": article["url"],
            "access_token": token,
        },
        method="POST",
    )
    post_id = str(result.get("id", ""))
    if not post_id:
        raise RuntimeError(f"Facebook nevrátil ID příspěvku: {result}")
    return {
        "post_id": post_id,
        "page_id": page_id,
        "page_name": page_name,
        "existing": "false",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("articles", nargs="*", help="Cesty k nově publikovaným HTML článkům")
    parser.add_argument("--skip-wait", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    if args.check_only:
        print(json.dumps(validate_page_access(), ensure_ascii=False, sort_keys=True))
        return 0

    if not args.articles:
        parser.error("Zadejte alespoň jeden článek nebo použijte --check-only.")

    validate_page_access()
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
                    "existing_post": published.get("existing") == "true",
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
