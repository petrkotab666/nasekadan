#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

import process_facebook_queue as queue
import publish_facebook


def refresh_facebook_preview(article_url: str) -> None:
    """Před zveřejněním přinutí Facebook znovu načíst aktuální OG metadata."""
    _, token, _ = publish_facebook.resolve_page_credentials()
    response = publish_facebook.request_json(
        publish_facebook.graph_endpoint(""),
        params={
            "id": article_url,
            "scrape": "true",
            "access_token": token,
        },
        method="POST",
    )
    if response.get("error"):
        raise RuntimeError(f"Facebook odmítl obnovení náhledu: {response['error']}")
    print(f"Facebook cache odkazu obnovena před publikací: {article_url}")


def wait_until_live(article_path: str, article: dict[str, str], timeout: int) -> None:
    """Ověří živou stránku, její přesný OG obrázek a obnoví cache Facebooku.

    Rozhodující je skutečný obrázek uvedený na živé stránce: musí patřit webu
    Naše Kadaň, nesmí být generický, musí vracet HTTP 200 jako image/png a mít
    rozměry 1200 × 630. Až potom se Facebooku odešle scrape=true a příspěvek se
    smí zveřejnit.
    """
    deadline = time.time() + timeout
    expected_title = article["title"]
    last_error = "živá stránka dosud nebyla zkontrolována"

    while time.time() < deadline:
        try:
            status, _, body = queue.fetch_bytes(
                article["url"],
                "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
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
            if not live_image:
                raise RuntimeError("živá stránka nemá OG obrázek")
            if live_image in queue.GENERIC_IMAGES or live_image.endswith("/social-card.png"):
                raise RuntimeError("živá stránka stále používá obecný social-card.png")
            if not live_image.startswith("https://nasekadan.cz/"):
                raise RuntimeError(f"živá stránka používá cizí OG obrázek: {live_image}")

            image_status, image_headers, image_data = queue.fetch_bytes(
                live_image,
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
            dimensions = queue.png_dimensions(image_data)
            if dimensions != (1200, 630):
                raise RuntimeError(
                    f"OG obrázek má rozměry {dimensions}, očekáváno 1200 × 630"
                )
            if len(image_data) < 10_000:
                raise RuntimeError(
                    f"OG obrázek je podezřele malý: {len(image_data)} B"
                )

            article["image"] = live_image
            refresh_facebook_preview(article["url"])
            print(
                f"Připraveno pro Facebook: {article_path}, živý OG obrázek "
                f"{dimensions[0]} × {dimensions[1]}, {len(image_data)} B"
            )
            return
        except Exception as exc:
            last_error = str(exc)
            print(
                f"Čekám na správné nasazení a Facebook náhled {article_path}: {last_error}",
                file=sys.stderr,
            )
            time.sleep(20)

    raise TimeoutError(
        f"Článek nebyl do {timeout} sekund připraven pro Facebook: {last_error}"
    )


queue.wait_until_live = wait_until_live

if __name__ == "__main__":
    raise SystemExit(queue.main())
