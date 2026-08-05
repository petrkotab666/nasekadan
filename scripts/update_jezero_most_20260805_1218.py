#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SLUG = "jezero-most-patrani-dva-lide-bourka-2026"
URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
PUBLISHED = "2026-08-05T10:50:00+02:00"
EMOSTECKO_GOOGLE_NEWS = (
    "https://news.google.com/rss/articles/"
    "CBMiyAFBVV95cUxNNHplRUFRYUhBTTBONXZmenhqcDh4dEo3aC15MGFVTjRvaTctLXV2dGtXanFVU3J3dExDalRhbHNlTjdmOXJXcVlaS2NqZlRwejJEN05Hb1k2MUJiMHQzM004M1EtVUZoRzFkVkt4SE90YWNBbGY3OXN6azNrajYtUVZjRDBRTk5qUjJqemMzR0pJaFl6a0taVFhSczB3c3ZHTkFSV2JISU5oWFBocmxSbF9peFRzQ3RRRlhNVW4tZVN0U1c0M2ZxMw?oc=5"
)
SOURCE_LABEL = (
    "e-Mostecko – Na jezeře Most pokračuje rozsáhlá pátrací akce. "
    "Pohřešované se zatím nepodařilo najít"
)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    source_item = (
        f'<li><a href="{EMOSTECKO_GOOGLE_NEWS}" rel="nofollow noopener">'
        f'{SOURCE_LABEL}</a></li>'
    )

    if SOURCE_LABEL not in text:
        match = re.search(r'(<section class="sources">.*?<ul>)(.*?)(</ul>)', text, flags=re.S)
        if not match:
            raise RuntimeError("Nelze najít seznam zdrojů v článku.")
        text = text[: match.start(3)] + source_item + match.group(3) + text[match.end(3):]

    note = (
        '<p data-source-enrichment="emostecko-20260805">'
        'Redakce stav ověřila 5. srpna 2026 v 10:50. e-Mostecko bylo ve 12:18 doplněno '
        'jako další potvrzující zdroj. Jeho zpráva byla zveřejněna už v 8:15, tedy před '
        'vydáním tohoto článku, a nepředstavuje pozdější vývoj. V době vydání nebyl '
        'veřejně známý výsledek pátrání.</p>'
    )
    text = re.sub(r'<p data-source-enrichment="emostecko-20260805">.*?</p>', '', text, flags=re.S)
    text = re.sub(
        r'<section class="sources">(.*?)<p>Redakce stav ověřila.*?</p></section>',
        lambda m: '<section class="sources">' + m.group(1) + note + '</section>',
        text,
        count=1,
        flags=re.S,
    )
    if 'data-source-enrichment="emostecko-20260805"' not in text:
        raise RuntimeError("Poznámka o doplnění zdroje se nepodařila vložit.")

    if f'article:published_time" content="{PUBLISHED}' not in text:
        raise RuntimeError("Původní čas vydání článku se změnil.")
    if f'article:modified_time" content="{PUBLISHED}' not in text:
        raise RuntimeError("Drobné doplnění zdroje nesmí posunout datum obsahové aktualizace.")

    write(ARTICLE, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    article = next((x for x in data.get("articles", []) if isinstance(x, dict) and x.get("url") == URL), None)
    if article is None:
        raise RuntimeError("Článek chybí v kanonickém registru.")
    if article.get("modified_at") != PUBLISHED:
        raise RuntimeError("Registry modified_at neodpovídá původnímu vydání.")
    article["source_commit"] = "pending-source-enrichment-commit"
    now = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["repair_pending_public_verification"] = True
    validation["last_source_enrichment"] = {
        "status": "pending_public_verification",
        "checked_at": now,
        "article_url": URL,
        "source": "e-Mostecko",
        "source_published_at": "2026-08-05T08:15:00+02:00",
        "classification": "supporting_source_published_before_article",
        "content_update_required": False,
    }
    data["generated_at"] = now
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    update_article()
    update_registry()
    text = ARTICLE.read_text(encoding="utf-8")
    if SOURCE_LABEL not in text or 'data-source-enrichment="emostecko-20260805"' not in text:
        raise RuntimeError("Zdrojové doplnění článku není úplné.")
    print(f"Doplněn potvrzující zdroj bez změny publikace: {URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
