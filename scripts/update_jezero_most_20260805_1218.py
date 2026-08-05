#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = "jezero-most-patrani-dva-lide-bourka-2026"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
PUBLISHED = "2026-08-05T10:50:00+02:00"
MODIFIED = "2026-08-05T12:18:00+02:00"
TITLE = "Na jezeře Most pátrají po dvou lidech. Kvůli bouřce se neměli dostat na břeh"
DESC = (
    "Pátrání po dvou lidech na jezeře Most pokračuje. Podle e-Mostecka se pohřešované "
    "zatím nepodařilo najít. Silná bouřka jim měla zabránit v návratu na břeh."
)
LEAD = (
    "Rozsáhlá pátrací akce na jezeře Most pokračuje. Podle e-Mostecka se pohřešované "
    "zatím nepodařilo najít. Dvojici měla návrat na břeh znemožnit silná bouřka a noční "
    "pátrání podle Mosteckého deníku přerušila tma."
)
EMOSTECKO_GOOGLE_NEWS = (
    "https://news.google.com/rss/articles/"
    "CBMiyAFBVV95cUxNNHplRUFRYUhBTTBONXZmenhqcDh4dEo3aC15MGFVTjRvaTctLXV2dGtXanFVU3J3dExDalRhbHNlTjdmOXJXcVlaS2NqZlRwejJEN05Hb1k2MUJiMHQzM004M1EtVUZoRzFkVkt4SE90YWNBbGY3OXN6azNrajYtUVZjRDBRTk5qUjJqemMzR0pJaFl6a0taVFhSczB3c3ZHTkFSV2JISU5oWFBocmxSbF9peFRzQ3RRRlhNVW4tZVN0U1c0M2ZxMw?oc=5"
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_meta(text: str, attr: str, key: str, value: str) -> str:
    patterns = (
        rf'<meta\s+{attr}="{re.escape(key)}"\s+content="[^"]*"\s*/?>',
        rf'<meta\s+content="[^"]*"\s+{attr}="{re.escape(key)}"\s*/?>',
    )
    replacement = f'<meta {attr}="{key}" content="{escape(value, quote=True)}">'
    for pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            return re.sub(pattern, replacement, text, count=1, flags=re.I)
    return text.replace("</head>", replacement + "\n</head>", 1)


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    text = replace_meta(text, "name", "description", DESC)
    text = replace_meta(text, "property", "og:description", DESC)
    text = replace_meta(text, "name", "twitter:description", DESC)
    text = replace_meta(text, "property", "article:modified_time", MODIFIED)

    def patch_jsonld(match: re.Match[str]) -> str:
        start, raw, end = match.group(1), match.group(2), match.group(3)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            data["description"] = DESC
            data["datePublished"] = PUBLISHED
            data["dateModified"] = MODIFIED
        return start + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + end

    text = re.sub(
        r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        patch_jsonld,
        text,
        flags=re.S,
    )
    text = re.sub(
        r'<p class="tag">.*?</p>',
        '<p class="tag">OD SOUSEDŮ · MOST · AKTUALIZOVÁNO · 5. SRPNA 2026 · 12:18</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p class="leadtext">.*?</p>',
        f'<p class="leadtext"><strong>{escape(LEAD)}</strong></p>',
        text,
        count=1,
        flags=re.S,
    )

    status = (
        '<div class="status-box" data-update-jezero-most="20260805-1218">'
        '<strong>Aktualizace 5. srpna ve 12:18</strong>'
        '<p>e-Mostecko uvádí, že rozsáhlá pátrací akce na jezeře pokračuje a pohřešované '
        'se zatím nepodařilo najít. Redakce k 12:18 nenalezla samostatné veřejné oznámení '
        'Policie ČR nebo hasičů s konečným výsledkem akce. Článek proto dál pracuje s jasně '
        'označenými mediálními informacemi.</p></div>'
    )
    if not re.search(r'<div class="status-box".*?</div>', text, flags=re.S):
        raise RuntimeError("V článku chybí stavový box.")
    text = re.sub(r'<div class="status-box".*?</div>', status, text, count=1, flags=re.S)

    update_paragraph = (
        '<p data-update-jezero-most="20260805-1218"><strong>Nový vývoj:</strong> '
        'e-Mostecko v úterý uvedlo, že pátrání pokračuje v rozsáhlém rozsahu, ale dvojici '
        'se zatím najít nepodařilo. Jde o doplnění původních zpráv CNN Prima NEWS a '
        'Mosteckého deníku.</p>'
    )
    text = re.sub(r'\s*<p data-update-jezero-most="20260805-1218">.*?</p>', '', text, flags=re.S)
    anchor = re.search(r'(<div class="status-box"[^>]*>.*?</div>)', text, flags=re.S)
    if not anchor:
        raise RuntimeError("Aktualizační box nebyl po úpravě nalezen.")
    text = text[: anchor.end()] + "\n" + update_paragraph + text[anchor.end():]

    text = re.sub(
        r'<div class="fact"><strong>Výsledek neznámý</strong><span>.*?</span></div>',
        '<div class="fact"><strong>Pátrání pokračuje</strong><span>podle e-Mostecka se dvojici zatím nepodařilo najít</span></div>',
        text,
        count=1,
        flags=re.S,
    )

    if "pátrání podle e-Mostecka pokračuje" not in text:
        text = text.replace(
            '<li>noční pátrání podle Deníku přerušila tma.</li>',
            '<li>noční pátrání podle Deníku přerušila tma,</li><li>pátrání podle e-Mostecka pokračuje a dvojici se zatím nepodařilo najít.</li>',
            1,
        )

    source_item = (
        f'<li><a href="{EMOSTECKO_GOOGLE_NEWS}" rel="nofollow noopener">'
        'e-Mostecko – Na jezeře Most pokračuje rozsáhlá pátrací akce. '
        'Pohřešované se zatím nepodařilo najít</a></li>'
    )
    if "Na jezeře Most pokračuje rozsáhlá pátrací akce" not in text:
        source_match = re.search(r'(<div class="sources">.*?<ul>)(.*?)(</ul>)', text, flags=re.S)
        if not source_match:
            raise RuntimeError("Nelze najít seznam zdrojů.")
        text = (
            text[: source_match.start(3)]
            + source_item
            + source_match.group(3)
            + text[source_match.end(3):]
        )

    write(ARTICLE, text)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    item_pattern = re.compile(r'<item>.*?' + re.escape(URL) + r'.*?</item>', re.S)
    match = item_pattern.search(text)
    if not match:
        raise RuntimeError("Článek chybí v RSS.")
    item = match.group(0)
    item = re.sub(r'<description><!\[CDATA\[.*?\]\]></description>', f'<description><![CDATA[{DESC}]]></description>', item, count=1, flags=re.S)
    if '<category>Aktualizováno</category>' not in item:
        item = item.replace('</item>', '<category>Aktualizováno</category>\n    </item>', 1)
    text = text[: match.start()] + item + text[match.end():]
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
    pattern = re.compile(r'(\[[^\n]+\]\(' + re.escape(URL) + r'\)\n)\s{2}[^\n]*')
    if not pattern.search(text):
        raise RuntimeError("Článek chybí v llms.txt.")
    text = pattern.sub(r'\1  ' + DESC, text, count=1)
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    article = next((x for x in data.get("articles", []) if isinstance(x, dict) and x.get("url") == URL), None)
    if article is None:
        raise RuntimeError("Článek chybí v kanonickém registru.")
    article["modified_at"] = MODIFIED
    article["source_commit"] = "pending-update-commit"
    topics = article.setdefault("topics", [])
    if "Pokračující pátrání" not in topics:
        topics.append("Pokračující pátrání")
    data["article_count"] = len(data.get("articles", []))
    now = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["repair_pending_public_verification"] = True
    validation["last_consistency_audit"] = {
        "status": "pending_public_verification",
        "checked_at": now,
        "article_count": data["article_count"],
        "updated_url": URL,
        "update_reason": "Pátrání pokračuje; pohřešované se zatím nepodařilo najít.",
    }
    data["generated_at"] = now
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    update_article()
    update_rss()
    update_llms()
    subprocess.run(["python3", str(ROOT / "scripts" / "enforce_all_article_visibility.py")], cwd=ROOT, check=True)
    update_registry()

    required = (
        ARTICLE,
        ROOT / "index.html",
        ROOT / "clanky" / "index.html",
        ROOT / "rss.xml",
        ROOT / "sitemap.xml",
        ROOT / "news-sitemap.xml",
        ROOT / "llms.txt",
        ROOT / "data" / "published-content-index.json",
    )
    for path in required:
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Chybí výstup: {path}")

    article_text = ARTICLE.read_text(encoding="utf-8")
    if MODIFIED not in article_text or "pohřešované se zatím nepodařilo najít" not in article_text:
        raise RuntimeError("Aktualizace se nepropsala do článku.")
    print(f"Aktualizováno: {URL} ({MODIFIED})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
