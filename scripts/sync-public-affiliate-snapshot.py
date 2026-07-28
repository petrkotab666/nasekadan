#!/usr/bin/env python3
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("AFFILIATE_REPO_ROOT", ".")).resolve()
CENTRAL_URL = os.environ.get("CENTRAL_URL", "https://pojistime.to/assets/affiliate-database.json")
OVERLAY_URL = os.environ.get("BRAINMARKET_OVERLAY_URL", "https://pojistime.to/assets/ehub-partner-assets/brainmarket.json")


def download(url: str, required: bool = True) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        separator = "&" if "?" in url else "?"
        request = urllib.request.Request(
            f"{url}{separator}sync={int(time.time() * 1_000_000)}-{attempt}",
            headers={
                "User-Agent": "Pojistime-public-affiliate-sync/2.2",
                "Cache-Control": "no-cache, no-store, max-age=0",
                "Pragma": "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except Exception as exc:
            last_error = exc
            print(f"{url}: pokus {attempt}/3 selhal: {exc}")
            if attempt < 3:
                time.sleep(attempt * 5)
    if required:
        raise SystemExit(f"Zdroj se nepodařilo stáhnout: {url}: {last_error}")
    print(f"Volitelný overlay není dostupný: {url}: {last_error}")
    return b""


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def main() -> int:
    config_path = ROOT / "assets" / "affiliate-site-config.json"
    if not config_path.exists():
        raise SystemExit("Chybí assets/affiliate-site-config.json")

    config_raw = config_path.read_bytes()
    config = json.loads(config_raw)
    raw = download(CENTRAL_URL)
    overlay_raw = download(OVERLAY_URL, required=False)
    database = json.loads(raw)
    central_hash = hashlib.sha256(raw + b"\0" + overlay_raw).hexdigest()
    config_hash = hashlib.sha256(config_raw).hexdigest()

    direct = database.get("partners") or []
    inventory_obj = database.get("ehubProgramInventory") or {}
    inventory = inventory_obj.get("programs") or []
    records: list[dict] = []
    for source, items in (("partners", direct), ("inventory", inventory)):
        for item in items:
            if isinstance(item, dict):
                row = dict(item)
                row["_centralLayer"] = source
                records.append(row)

    overlay_sources: list[str] = []
    if overlay_raw:
        try:
            overlay = json.loads(overlay_raw)
            program = overlay.get("program") or {}
            links = overlay.get("links") or []
            default_link_id = str(program.get("defaultLinkId") or "")
            default_link = next((item for item in links if str(item.get("id")) == default_link_id), links[0] if links else {})
            if program.get("name") and default_link_id and default_link.get("clickUrl"):
                records.append(
                    {
                        "order": 81,
                        "id": f"ehub-{default_link_id.lower()}",
                        "name": program.get("name"),
                        "network": "eHUB",
                        "programStatus": program.get("status") or "active",
                        "programCode": program.get("programCode") or "",
                        "defaultLinkId": default_link_id,
                        "baseClickUrl": default_link.get("clickUrl"),
                        "defaultTargetUrl": program.get("defaultTargetUrl") or default_link.get("targetUrl") or "",
                        "linkPolicy": "default_available",
                        "assetsUpdatedAt": overlay.get("updatedAt"),
                        "links": links,
                        "banners": overlay.get("banners") or [],
                        "feeds": overlay.get("feeds") or [],
                        "actions": overlay.get("actions") or [],
                        "recommendedUse": overlay.get("recommendedUse") or [],
                        "sourceNotes": overlay.get("sourceNotes") or [],
                        "approval": overlay.get("approval") or {},
                        "manager": overlay.get("manager") or {},
                        "categories": overlay.get("categories") or [],
                        "role": overlay.get("role"),
                        "commercialTerms": overlay.get("commercialTerms") or {},
                        "restrictions": overlay.get("restrictions") or [],
                        "_centralLayer": "partner-overlay",
                        "_overlaySource": OVERLAY_URL,
                    }
                )
                overlay_sources.append(OVERLAY_URL)
        except Exception as exc:
            raise SystemExit(f"BrainMarket overlay je neplatný: {exc}")

    aliases = [norm(value) for value in config.get("aliases", [])]
    allowed_ids = {norm(value) for value in config.get("allowedPartnerIds", [])}
    blocked_ids = {norm(value) for value in config.get("blockedPartnerIds", [])}
    allowed_categories = {norm(value) for value in config.get("allowedCategories", [])}
    mode = config.get("mode", "filtered")
    site_name = norm(config.get("site"))

    def is_active(row: dict) -> bool:
        status = norm(row.get("programStatus") or row.get("status") or "active")
        if status in {"disabled", "inactive", "rejected", "closed", "paused", "not-approved", "pending"}:
            return False
        approval = row.get("approval") or {}
        approved_sites = {norm(value) for value in approval.get("approvedPublicationSites", [])}
        if approved_sites and site_name not in approved_sites:
            return False
        return bool(row.get("baseClickUrl") or row.get("trackingUrl") or row.get("links"))

    def is_blocked(row: dict) -> bool:
        identifiers = {norm(row.get("id")), norm(row.get("defaultLinkId")), norm(row.get("name"))}
        identifiers.discard("")
        return any(
            blocked and any(blocked == identifier or blocked in identifier or identifier in blocked for identifier in identifiers)
            for blocked in blocked_ids
        )

    def matches(row: dict) -> bool:
        if not is_active(row) or is_blocked(row):
            return False
        if mode == "all_active":
            return True
        row_id = norm(row.get("id") or row.get("defaultLinkId"))
        name = norm(row.get("name"))
        if any(token and (token == row_id or token == name or token in row_id or token in name) for token in allowed_ids):
            return True
        categories = {norm(value) for value in row.get("categories", [])}
        if any(
            allowed and category and (allowed == category or allowed in category or category in allowed)
            for allowed in allowed_categories
            for category in categories
        ):
            return True
        recommended = norm(" ".join(str(value) for value in row.get("recommendedUse", [])))
        return any(alias and alias in recommended for alias in aliases)

    selected: dict[str, dict] = {}
    for row in records:
        if not matches(row):
            continue
        key = norm(row.get("name")) or norm(row.get("defaultLinkId") or row.get("id"))
        if not key:
            continue
        old = selected.get(key)
        score = len(row.get("feeds") or []) * 5 + len(row.get("banners") or []) * 2 + len(row.get("links") or []) * 2 + len(row)
        old_score = -1 if old is None else len(old.get("feeds") or []) * 5 + len(old.get("banners") or []) * 2 + len(old.get("links") or []) * 2 + len(old)
        if score >= old_score:
            selected[key] = row

    partners = sorted(selected.values(), key=lambda item: str(item.get("name") or "").lower())
    payload = {
        "schemaVersion": 2,
        "site": config.get("site"),
        "mode": mode,
        "centralSource": CENTRAL_URL,
        "overlaySources": overlay_sources,
        "centralUpdatedAt": database.get("updatedAt"),
        "centralSha256": central_hash,
        "configSha256": config_hash,
        "generatedAt": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "sourceProgramCount": inventory_obj.get("programCount"),
        "partnerCount": len(partners),
        "feedCount": sum(len(item.get("feeds") or []) for item in partners),
        "bannerCount": sum(len(item.get("banners") or []) for item in partners),
        "autoPublish": bool(config.get("autoPublish", False)),
        "partners": partners,
    }

    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    snapshot_path = assets / "affiliate-site-snapshot.json"
    snapshot_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (assets / "affiliate-site-snapshot.js").write_text(
        "export const affiliateSnapshot=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "site": config.get("site"),
                "centralUpdatedAt": payload["centralUpdatedAt"],
                "centralSha256": central_hash,
                "partnerCount": len(partners),
                "feedCount": payload["feedCount"],
                "bannerCount": payload["bannerCount"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
