#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import time
import urllib.parse

from publish_facebook import (
    build_message,
    graph_endpoint,
    live_page_ready,
    parse_article,
    request_json,
    resolve_page_credentials,
    validate_page_access,
)

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky/kulturni-zarizeni-kadan.html"
MARKER = ROOT / ".github/facebook-published/kulturni-zarizeni-kadan-d406d029f9.json"
BASE_URL = "https://nasekadan.cz/clanky/kulturni-zarizeni-kadan.html"
SHARE_URL = BASE_URL + "?fb=20260802v2"
NEW_IMAGE = "https://nasekadan.cz/social/kzk-kultura-strelnice-klaster-20260802-v2.png"


def force_scrape(url: str) -> dict:
    app_id = os.environ.get("FACEBOOK_APP_ID", "").strip()
    app_secret = os.environ.get("FACEBOOK_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise RuntimeError("Chybí FACEBOOK_APP_ID nebo FACEBOOK_APP_SECRET pro nové načtení odkazu.")
    return request_json(
        graph_endpoint(""),
        params={
            "id": url,
            "scrape": "true",
            "access_token": f"{app_id}|{app_secret}",
        },
        method="POST",
        timeout=60,
    )


def create_post(article: dict[str, str]) -> str:
    page_id, token, _ = resolve_page_credentials()
    result = request_json(
        graph_endpoint(f"{urllib.parse.quote(page_id)}/feed"),
        params={
            "message": build_message(article),
            "link": SHARE_URL,
            "access_token": token,
        },
        method="POST",
        timeout=60,
    )
    post_id = str(result.get("id", "")).strip()
    if not post_id:
        raise RuntimeError(f"Facebook nevrátil ID opraveného příspěvku: {result}")
    return post_id


def verify_post(post_id: str) -> dict:
    _, token, _ = resolve_page_credentials()
    last: dict = {}
    for attempt in range(8):
        last = request_json(
            graph_endpoint(urllib.parse.quote(post_id, safe="_")),
            params={
                "fields": "id,permalink_url,full_picture,attachments{url,unshimmed_url,target,media_type}",
                "access_token": token,
            },
            timeout=60,
        )
        if str(last.get("id", "")) == post_id and last.get("full_picture"):
            return last
        time.sleep(5 + attempt * 2)
    raise RuntimeError(f"Opravený příspěvek nevytvořil obrazový náhled: {last}")


def delete_post(post_id: str) -> None:
    _, token, _ = resolve_page_credentials()
    result = request_json(
        graph_endpoint(urllib.parse.quote(post_id, safe="_")),
        params={"access_token": token},
        method="DELETE",
        timeout=60,
    )
    if result.get("success") is not True:
        raise RuntimeError(f"Facebook nepotvrdil odstranění starého příspěvku: {result}")


def main() -> None:
    if not ARTICLE.exists() or not MARKER.exists():
        raise SystemExit("Chybí článek nebo záznam původního facebookového příspěvku.")

    marker = json.loads(MARKER.read_text(encoding="utf-8"))
    old_post_id = str(marker.get("facebook_post_id", "")).strip()
    if not old_post_id:
        raise SystemExit("Záznam neobsahuje ID původního facebookového příspěvku.")

    article = parse_article(ARTICLE)
    if article.get("image") != NEW_IMAGE:
        raise SystemExit(f"Článek ještě nepoužívá nový obrázek: {article.get('image')}")

    validate_page_access()
    live_page_ready(article, timeout=300)

    # Meta má samostatnou cache pro každou URL. Načteme hlavní i cache-busting adresu.
    scrape_base = force_scrape(BASE_URL)
    scrape_share = force_scrape(SHARE_URL)
    time.sleep(4)

    # Nejdřív vytvořit a ověřit opravený příspěvek; teprve potom odstranit chybný.
    new_post_id = create_post(article)
    new_post = verify_post(new_post_id)
    delete_post(old_post_id)

    marker.update({
        "article_path": "clanky/kulturni-zarizeni-kadan.html",
        "article_url": SHARE_URL,
        "canonical_article_url": BASE_URL,
        "og_image": NEW_IMAGE,
        "facebook_post_id": new_post_id,
        "replaced_facebook_post_id": old_post_id,
        "facebook_permalink_url": str(new_post.get("permalink_url", "")),
        "facebook_full_picture": str(new_post.get("full_picture", "")),
        "existing_post_detected": False,
        "republished_at": datetime.now(timezone.utc).isoformat(),
        "scrape_base_keys": sorted(scrape_base.keys()),
        "scrape_share_keys": sorted(scrape_share.keys()),
    })
    MARKER.write_text(json.dumps(marker, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "old_post_id": old_post_id,
        "new_post_id": new_post_id,
        "permalink_url": new_post.get("permalink_url", ""),
        "full_picture": bool(new_post.get("full_picture")),
        "share_url": SHARE_URL,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
