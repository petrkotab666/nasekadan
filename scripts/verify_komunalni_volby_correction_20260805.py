#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import ssl
import time
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://nasekadan.cz"
ARTICLE = BASE + "/clanky/komunalni-volby-kadan-kandidaty-lhuta-2026.html"
CTX = ssl._create_unverified_context()


def fetch(url: str, token: str) -> str:
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        url + sep + "v=" + token,
        headers={"User-Agent": "Naše Kadaň public verifier", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=40, context=CTX) as response:
        return response.read().decode("utf-8", errors="replace")


def check_once(attempt: int) -> dict:
    token = f"editorial-correction-{attempt}-{int(time.time())}"
    article = fetch(ARTICLE, token)
    home = fetch(BASE + "/", token)
    archive = fetch(BASE + "/clanky/", token)
    rss = fetch(BASE + "/rss.xml", token)
    sitemap = fetch(BASE + "/sitemap.xml", token)
    registry_text = fetch(BASE + "/data/published-content-index.json", token)
    health = fetch(BASE + "/deployment-health.txt", token)

    assert 'data-editorial-correction="20260805-1523"' in article
    assert "sdružení nezávislých kandidátů s podporou Pirátské strany" in article
    assert "Za chybu se omlouváme" in article
    assert 'article:modified_time" content="2026-08-05T15:23:00+02:00' in article
    assert "Jana Hladová a další veřejně představení kandidáti" not in article
    assert "Piráti ukazují jména, úřední potvrzení teprve přijde" not in article
    assert "další kandidátku tvoří nezávislí s podporou Pirátů" in home
    assert "další kandidátku tvoří nezávislí s podporou Pirátů" in archive
    assert "další kandidátku tvoří nezávislí s podporou Pirátů" in rss
    assert "status=ok" in health

    registry = json.loads(registry_text)
    correction = registry["validation"]["last_editorial_correction"]
    assert correction["classification"] == "political_candidate_list_correction"
    article_record = next(x for x in registry["articles"] if x["url"] == ARTICLE)
    assert article_record["modified_at"] == "2026-08-05T15:23:00+02:00"
    assert "Eliška Hladová" in article_record["persons"]
    assert "Jana Hladová" not in article_record["persons"]

    root = ET.fromstring(sitemap)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [node.text for node in root.findall("s:url/s:loc", ns)]
    duplicates = [url for url, count in Counter(locs).items() if count > 1]
    assert duplicates == []
    assert locs.count(ARTICLE) == 1

    return {
        "status": "success",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "article": ARTICLE,
        "checks": {
            "visible_correction": True,
            "correct_group_type": True,
            "old_candidate_claims_absent": True,
            "homepage": True,
            "archive": True,
            "rss": True,
            "sitemap_unique": True,
            "registry": True,
            "health": True,
        },
    }


def main() -> int:
    last_error: Exception | None = None
    for attempt in range(1, 13):
        try:
            report = check_once(attempt)
            path = Path("reports/komunalni-volby-correction-20260805.json")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("Veřejná oprava ověřena.")
            return 0
        except Exception as exc:
            last_error = exc
            print(f"Kontrola {attempt}/12 zatím neprošla: {exc}")
            time.sleep(10)
    raise SystemExit(f"Veřejná kontrola selhala: {last_error}")


if __name__ == "__main__":
    raise SystemExit(main())
