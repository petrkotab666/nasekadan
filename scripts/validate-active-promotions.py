#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ROOT / "scripts" / "patch-active-promotions.py"))
PROMOS = MODULE["PROMOS"]
TOWERS = MODULE["TOWERS"]
REPORT = ROOT / "data" / "active-promotions-validation.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/151 Safari/537.36 NaseKadanPromotionAudit/1.2"


def is_tracker_url(raw_url: str) -> bool:
    parsed = urlparse(raw_url)
    return (parsed.hostname or "").lower() in {"ehub.cz", "www.ehub.cz"} and parsed.path.lower().startswith("/system/scripts/click.php")


def client_redirect(body: bytes) -> str:
    text = body[:30000].decode("utf-8", "replace")
    for pattern in (
        r'<meta[^>]+http-equiv=["\']?refresh["\']?[^>]+content=["\'][^"\']*url=([^"\'> ]+)',
        r'(?:window\.)?location(?:\.href)?\s*=\s*["\']([^"\']+)',
        r'location\.replace\(\s*["\']([^"\']+)',
    ):
        match = re.search(pattern, text, re.I)
        if match and match.group(1).startswith(("http://", "https://")):
            return match.group(1)
    return ""


def probe(url: str) -> dict:
    try:
        headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.7", "Cache-Control": "no-cache"}
        response = requests.get(url, headers=headers, timeout=(10, 30), allow_redirects=True)
        body = response.content
        final = response.url
        redirects = len(response.history)
        if is_tracker_url(final):
            next_url = client_redirect(body)
            if next_url:
                response = requests.get(next_url, headers=headers, timeout=(10, 30), allow_redirects=True)
                body = response.content
                final = response.url
                redirects += len(response.history) + 1
        host = (urlparse(final).hostname or "").lower()
        ok = 200 <= response.status_code < 400 and bool(body.strip()) and not is_tracker_url(final)
        return {"url": url, "ok": ok, "status": response.status_code, "finalUrl": final, "finalHost": host, "bytes": len(body), "redirects": redirects}
    except Exception as exc:  # noqa: BLE001
        return {"url": url, "ok": False, "status": None, "finalUrl": "", "finalHost": "", "bytes": 0, "redirects": 0, "error": f"{type(exc).__name__}: {exc}"}


def svg_dimensions(path: Path) -> tuple[int, int] | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<svg[^>]+width="(\d+)"[^>]+height="(\d+)"', text)
    return (int(match.group(1)), int(match.group(2))) if match else None


def active_urls_from_resulting_js(js: str) -> list[str]:
    match = re.search(r"/\* ACTIVE_PROMOTIONS_START \*/(.*?)/\* ACTIVE_PROMOTIONS_END \*/", js, re.S)
    if not match:
        raise ValueError("V reklamy.js chybí blok ACTIVE_PROMOTIONS")
    urls = re.findall(r"\burl:'([^']+)'", match.group(1))
    if not urls:
        raise ValueError("V aktivním reklamním bloku nebyla nalezena žádná URL")
    return list(dict.fromkeys(urls))


def main() -> int:
    errors: list[str] = []
    js = (ROOT / "reklamy.js").read_text(encoding="utf-8")
    try:
        active_urls = active_urls_from_resulting_js(js)
    except ValueError as exc:
        active_urls = []
        errors.append(str(exc))

    probes = [probe(url) for url in active_urls]
    for row in probes:
        if not row["ok"]:
            errors.append(f"Nefunkční odkaz {row['url']} -> {row.get('status')} {row.get('finalUrl')}")

    for item in PROMOS:
        expected = [("wide", 1200, 400), ("square", 800, 800)]
        if item["id"] in TOWERS:
            expected.append(("tower", 300, 600))
        for suffix, width, height in expected:
            path = ROOT / "assets" / "reklamy" / f"{item['id']}-{suffix}.svg"
            if not path.exists():
                errors.append(f"Chybí banner {path.relative_to(ROOT)}")
                continue
            if svg_dimensions(path) != (width, height):
                errors.append(f"Špatný rozměr {path.relative_to(ROOT)}: {svg_dimensions(path)} místo {(width, height)}")

    if "function isPromoActive(item)" not in js:
        errors.append("reklamy.js neobsahuje kontrolu platnosti kampaně")
    for item in PROMOS:
        if f"id:{item['id']!r}" not in js:
            errors.append(f"reklamy.js neobsahuje {item['id']}")

    report = {
        "schemaVersion": 2,
        "source": "resulting-reklamy.js",
        "promotions": len(PROMOS),
        "workingUrls": sum(row["ok"] for row in probes),
        "testedUrls": len(probes),
        "errors": errors,
        "probes": probes,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("promotions", "workingUrls", "testedUrls")}, ensure_ascii=False))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
