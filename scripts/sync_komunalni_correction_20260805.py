#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
SLUG = "komunalni-volby-kadan-kandidaty-lhuta-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
ARTICLE_URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
MODIFIED = "2026-08-05T15:23:00+02:00"
DESC = (
    "Podávání kandidátek do komunálních voleb skončilo. ODS a Dáme Kadani novou šanci "
    "zveřejnily sestavy, ANO oznámilo podání a další kandidátku tvoří nezávislí s podporou Pirátů."
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def normalize_generated_whitespace() -> None:
    paths = [
        ROOT / "index.html",
        ROOT / "clanky" / "index.html",
        ROOT / "sitemap.xml",
    ] + sorted((ROOT / "clanky").glob("strana-*.html"))
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
        write(path, normalized)


def verify_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    required = (
        'data-editorial-correction="20260805-1523"',
        "sdružení nezávislých kandidátů s podporou Pirátské strany",
        "Za chybu se omlouváme",
        'article:modified_time" content="2026-08-05T15:23:00+02:00',
        "Elišky Hladové",
    )
    for value in required:
        if value not in text:
            raise RuntimeError(f"V opraveném článku chybí: {value}")
    forbidden = (
        "Jana Hladová a další veřejně představení kandidáti",
        "Piráti ukazují jména, úřední potvrzení teprve přijde",
        "Piráti rovněž veřejně představují svůj tým",
    )
    for value in forbidden:
        if value in text:
            raise RuntimeError(f"V článku zůstala stará formulace: {value}")


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'<item>.*?' + re.escape(ARTICLE_URL) + r'.*?</item>', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Opravený článek chybí v RSS.")
    item = match.group(0)
    item = re.sub(
        r'<description><!\[CDATA\[.*?\]\]></description>',
        f'<description><![CDATA[{DESC}]]></description>',
        item,
        count=1,
        flags=re.S,
    )
    if '<category>Oprava</category>' not in item:
        item = item.replace('</item>', '<category>Oprava</category>\n    </item>', 1)
    text = text[:match.start()] + item + text[match.end():]
    text = re.sub(
        r'<lastBuildDate>.*?</lastBuildDate>',
        f'<lastBuildDate>{format_datetime(datetime.fromisoformat(MODIFIED))}</lastBuildDate>',
        text,
        count=1,
        flags=re.S,
    )
    write(path, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'(\[[^\n]+\]\(' + re.escape(ARTICLE_URL) + r'\)\n)\s{2}[^\n]*')
    if not pattern.search(text):
        raise RuntimeError("Opravený článek chybí v llms.txt.")
    write(path, pattern.sub(r'\1  ' + DESC, text, count=1))


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    article = next(
        (item for item in data.get("articles", []) if isinstance(item, dict) and item.get("url") == ARTICLE_URL),
        None,
    )
    if article is None:
        raise RuntimeError("Opravený článek chybí v registru.")

    article["modified_at"] = MODIFIED
    article["source_commit"] = "pending-editorial-correction-sync"
    article["persons"] = [
        name for name in article.get("persons", [])
        if name not in {"Jana Hladová", "Miloslava Karfilátová"}
    ]
    if "Eliška Hladová" not in article["persons"]:
        article["persons"].append("Eliška Hladová")

    article["organizations"] = [
        name for name in article.get("organizations", []) if name != "Piráti Kadaň"
    ]
    for name in (
        "Sdružení nezávislých kandidátů s podporou Pirátů",
        "Česká pirátská strana",
    ):
        if name not in article["organizations"]:
            article["organizations"].append(name)

    article["topics"] = [name for name in article.get("topics", []) if name != "Piráti"]
    for name in ("Nezávislí s podporou Pirátů", "Oprava článku"):
        if name not in article["topics"]:
            article["topics"].append(name)

    cases = article.setdefault("cases", [])
    case = "Oprava nesprávného označení kandidujícího uskupení a kandidátů"
    if case not in cases:
        cases.append(case)

    now = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["repair_pending_public_verification"] = True
    validation["last_editorial_correction"] = {
        "status": "pending_public_verification",
        "checked_at": now,
        "article_url": ARTICLE_URL,
        "modified_at": MODIFIED,
        "classification": "political_candidate_list_correction",
        "corrected_claims": [
            "Kandiduje sdružení nezávislých kandidátů s podporou Pirátské strany, nikoli Pirátská strana.",
            "Miloslava Karfilátová byla nesprávně převzata z kandidátky 2022 a není uváděna jako kandidátka 2026.",
        ],
        "primary_correction_source": "Písemné vyjádření kandidátky Elišky Hladové ze dne 5. srpna 2026",
    }
    data["generated_at"] = now
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def validate_outputs() -> None:
    ET.parse(ROOT / "rss.xml")
    ET.parse(ROOT / "sitemap.xml")
    ET.parse(ROOT / "news-sitemap.xml")

    root = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [node.text for node in root.findall("s:url/s:loc", ns)]
    duplicates = [url for url, count in Counter(locs).items() if count > 1]
    if duplicates:
        raise RuntimeError(f"Sitemap obsahuje duplicitní URL: {duplicates}")
    if locs.count(ARTICLE_URL) != 1:
        raise RuntimeError("Opravený článek není v sitemapě právě jednou.")

    pages = [ROOT / "clanky" / "index.html"] + sorted((ROOT / "clanky").glob("strana-*.html"))
    if len(pages) != 5:
        raise RuntimeError(f"Neočekávaný počet archivních stran: {len(pages)}")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if text.count('data-nk-archive-schema="1"') != 1:
            raise RuntimeError(f"Archivní strana {page.name} nemá právě jeden ItemList.")
        if '"@type": "CollectionPage"' in text:
            raise RuntimeError(f"Archivní strana {page.name} obsahuje starý CollectionPage blok.")

    rss = (ROOT / "rss.xml").read_text(encoding="utf-8")
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    archive = (ROOT / "clanky" / "index.html").read_text(encoding="utf-8")
    for text, name in ((rss, "RSS"), (llms, "llms.txt"), (home, "titulka"), (archive, "archiv")):
        if DESC not in text:
            raise RuntimeError(f"Opravený popis chybí v {name}.")

    data = json.loads((ROOT / "data" / "published-content-index.json").read_text(encoding="utf-8"))
    article = next(item for item in data["articles"] if item["url"] == ARTICLE_URL)
    if article["modified_at"] != MODIFIED:
        raise RuntimeError("Registr nemá správné datum opravy.")
    if "Eliška Hladová" not in article["persons"] or "Jana Hladová" in article["persons"]:
        raise RuntimeError("Registr nemá správně opravené osoby.")


def main() -> int:
    verify_article()
    update_rss()
    update_llms()
    subprocess.run(
        ["python3", str(ROOT / "scripts" / "enforce_all_article_visibility.py")],
        cwd=ROOT,
        check=True,
    )
    normalize_generated_whitespace()
    update_registry()
    validate_outputs()
    print(f"Synchronizována oprava: {ARTICLE_URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
