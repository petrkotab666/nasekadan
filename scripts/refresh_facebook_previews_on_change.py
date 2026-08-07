#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import process_facebook_queue as queue
import process_facebook_queue_live as live
import publish_facebook

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_DIR = ROOT / ".github" / "facebook-published"
STATUS_FILE = ROOT / ".github" / "facebook-preview-refresh-status.json"
DEFAULT_TIMEOUT = 1200
FB_UA = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"


def load_changed_paths(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    return {
        line.strip().replace("\\", "/").lstrip("./")
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    }


def same_site_image_path(url: str) -> str | None:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc not in {"nasekadan.cz", "www.nasekadan.cz"}:
        return None
    value = parts.path.lstrip("/")
    return value or None


def local_image_hash(article: dict[str, str]) -> tuple[str | None, str | None]:
    rel = same_site_image_path(article.get("image", ""))
    if not rel:
        return None, None
    path = ROOT / rel
    if not path.is_file():
        return rel, None
    return rel, hashlib.sha256(path.read_bytes()).hexdigest()


def marker_rows() -> list[tuple[Path, dict[str, Any]]]:
    rows: list[tuple[Path, dict[str, Any]]] = []
    if not PUBLISHED_DIR.exists():
        return rows
    for marker in sorted(PUBLISHED_DIR.glob("*.json")):
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            rows.append((marker, data))
    return rows


def detect_candidates(changed: set[str], forced: list[str]) -> list[dict[str, Any]]:
    """Vybere jen publikované články, kterých se právě týká tato změna.

    Historický rozdíl mezi starým markerem a dnešním og:image sám o sobě nesmí
    spustit hromadný rescrape všech starších článků. Rozdíl se zohlední teprve
    tehdy, když je konkrétní článek v aktuálním pushi změněn, změnil se jeho
    aktuální OG soubor, nebo byl článek výslovně vybrán přes --article.
    """
    forced_set = {
        queue.normalize_article_path(value)
        for value in forced
        if value.strip()
    }
    candidates: list[dict[str, Any]] = []

    for marker, data in marker_rows():
        article_path = str(data.get("article_path", "")).strip()
        if not article_path:
            continue
        try:
            article_path = queue.normalize_article_path(article_path)
            article = publish_facebook.parse_article(ROOT / article_path)
        except Exception as exc:
            print(f"Přeskakuji marker {marker.name}: {exc}", file=sys.stderr)
            continue

        is_forced = article_path in forced_set
        article_changed = article_path in changed
        image_rel = same_site_image_path(article.get("image", ""))
        image_changed = bool(image_rel and image_rel in changed)

        # Článek mimo rozsah aktuální změny vůbec neřešíme. Tím staré markery
        # nemohou samy od sebe vyvolat hromadnou obnovu desítek FB náhledů.
        if not (is_forced or article_changed or image_changed):
            continue

        reasons: list[str] = []
        if is_forced:
            reasons.append("manual")
        if article_changed:
            reasons.append("article_changed")
        if image_changed:
            reasons.append("image_changed")

        old_image = str(data.get("og_image", "")).strip()
        new_image = article.get("image", "").strip()
        if old_image != new_image:
            reasons.append("og_image_changed")

        candidates.append(
            {
                "marker": marker,
                "marker_data": data,
                "article_path": article_path,
                "article": article,
                "reasons": sorted(set(reasons)),
            }
        )

    missing_forced = forced_set - {row["article_path"] for row in candidates}
    for article_path in sorted(missing_forced):
        marker = queue.marker_path(article_path)
        if not marker.exists():
            print(
                f"Ruční obnova přeskočena: {article_path} ještě nemá Facebook marker.",
                file=sys.stderr,
            )
    return candidates


def wait_until_exact_live(
    article_path: str,
    article: dict[str, str],
    timeout: int,
) -> dict[str, Any]:
    """Čeká pouze na přesný produkční HTML/OG obrázek.

    Facebook Graph API se zde záměrně nevolá. Chyba rescrape nesmí být zaměněna
    za zpožděný deploy a opakována dvacet minut jako kdyby web ještě nebyl venku.
    """
    queue.validate_source_article(article_path, article)
    expected_title = html.unescape(article["title"]).strip()
    expected_image = article["image"].strip()
    image_rel, expected_hash = local_image_hash(article)
    deadline = time.time() + max(1, timeout)
    last_error = "živý web ještě nebyl zkontrolován"

    while time.time() < deadline:
        try:
            status, _, body = queue.fetch_bytes(article["url"], FB_UA)
            if status != 200:
                raise RuntimeError(f"článek vrací HTTP {status}")

            parser = publish_facebook.MetaParser()
            parser.feed(body.decode("utf-8", errors="replace"))
            live_title = parser.meta.get("og:title") or " ".join(parser.title_parts).strip()
            live_title = html.unescape(live_title).strip()
            live_image = parser.meta.get("og:image", "").strip()

            if expected_title and live_title != expected_title:
                raise RuntimeError(
                    "živá stránka ještě nemá přesný očekávaný og:title"
                )
            if live_image != expected_image:
                raise RuntimeError(
                    f"živá stránka ještě nemá správný OG obrázek: {live_image or 'chybí'}"
                )

            image_status, image_headers, image_data = queue.fetch_bytes(expected_image, FB_UA)
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

            live_hash = hashlib.sha256(image_data).hexdigest()
            if expected_hash and live_hash != expected_hash:
                raise RuntimeError(
                    f"živý OG obrázek {image_rel} ještě neodpovídá souboru v main"
                )

            return {
                "og_image": live_image,
                "image_bytes": len(image_data),
                "image_sha256": live_hash,
                "dimensions": [dimensions[0], dimensions[1]],
            }
        except Exception as exc:
            last_error = str(exc)
            print(
                f"Čekám na přesný produkční náhled {article_path}: {last_error}",
                file=sys.stderr,
            )
            remaining = deadline - time.time()
            if remaining > 0:
                time.sleep(min(20, remaining))

    raise TimeoutError(
        f"Náhled {article_path} nebyl do {timeout} sekund připraven: {last_error}"
    )


def refresh_facebook_once(article_url: str) -> None:
    """Provede jeden explicitní rescrape a při chybě okamžitě selže."""
    live.refresh_facebook_preview(article_url)


def write_status(results: list[dict[str, Any]]) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-file", type=Path)
    parser.add_argument("--article", action="append", default=[])
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("FACEBOOK_WAIT_TIMEOUT", DEFAULT_TIMEOUT)),
    )
    args = parser.parse_args()

    changed = load_changed_paths(args.changed_file)
    candidates = detect_candidates(changed, args.article)
    if not candidates:
        write_status(
            [{"state": "idle", "message": "Žádný publikovaný FB náhled nepotřebuje obnovu."}]
        )
        print("Žádný publikovaný Facebook náhled nepotřebuje obnovu.")
        return 0

    try:
        credentials = publish_facebook.validate_page_access()
        print(
            "Facebook přihlášení je platné pro stránku "
            f"{credentials.get('page_name')} ({credentials.get('page_id')})."
        )
    except Exception as exc:
        error = queue.sanitize_error(exc)
        write_status(
            [
                {
                    "state": "action_required",
                    "article_path": row["article_path"],
                    "reasons": row["reasons"],
                    "error": error,
                }
                for row in candidates
            ]
        )
        print(error, file=sys.stderr)
        return 1

    failed = False
    results: list[dict[str, Any]] = []
    for row in candidates:
        article_path = row["article_path"]
        article = row["article"]
        try:
            live_result = wait_until_exact_live(article_path, article, args.timeout)
            refresh_facebook_once(article["url"])

            refreshed_at = datetime.now(timezone.utc).isoformat()
            marker_data = dict(row["marker_data"])
            marker_data["article_url"] = article["url"]
            marker_data["og_image"] = live_result["og_image"]
            marker_data["preview_refreshed_at"] = refreshed_at
            marker_data["preview_refresh_reason"] = row["reasons"]
            marker_data["preview_image_sha256"] = live_result["image_sha256"]
            marker_data["preview_image_dimensions"] = live_result["dimensions"]
            row["marker"].write_text(
                json.dumps(marker_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            results.append(
                {
                    "state": "preview_refreshed",
                    "article_path": article_path,
                    "article_url": article["url"],
                    "reasons": row["reasons"],
                    "facebook_rescrape": True,
                    "refreshed_at": refreshed_at,
                    **live_result,
                }
            )
            print(
                f"Facebook náhled obnoven: {article_path} -> {live_result['og_image']}"
            )
        except Exception as exc:
            failed = True
            error = queue.sanitize_error(exc)
            results.append(
                {
                    "state": "failed",
                    "article_path": article_path,
                    "reasons": row["reasons"],
                    "error": error,
                }
            )
            print(
                f"Obnova FB náhledu selhala pro {article_path}: {error}",
                file=sys.stderr,
            )

    write_status(results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
