#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "komunalni-volby-kadan-kandidaty-lhuta-2026.html"
GENERATOR = ROOT / "scripts" / "publish_kadan_election_deadline_20260804.py"
REGISTRY = ROOT / "data" / "published-content-index.json"
URL = "https://nasekadan.cz/clanky/komunalni-volby-kadan-kandidaty-lhuta-2026.html"
MODIFIED = "2026-08-04T19:06:00+02:00"

OLD_TIMING = "zveřejnil v den uzávěrky krátké video, kterým oznámil podání kandidátky."
NEW_TIMING = "zveřejnil krátké video už několik dní před uzávěrkou, nikoli 4. srpna."
OLD_FOLLOW = "Kopii videa má redakce k dispozici. Z veřejně zachyceného příspěvku"
NEW_FOLLOW = "Kopii videa má redakce k dispozici. Facebook u příspěvku v době redakční kontroly zobrazoval údaj „před 4 dny“. Z veřejně zachyceného příspěvku"
OLD_SOURCE = "Veřejné video profilu „ANO, tohle je Kadaň“ ze 4. srpna 2026; obrazový záznam poskytl redakci čtenář."
NEW_SOURCE = "Veřejné video profilu „ANO, tohle je Kadaň“ zveřejněné několik dní před 4. srpnem 2026; obrazový záznam poskytl redakci čtenář."
NOTE = '<div class="update-box" data-correction="ano-video-timing"><strong>Upřesnění redakce</strong><p>Po zveřejnění článku jsme opravili časové zařazení videa ANO. Facebook u něj zobrazoval údaj „před 4 dny“; nebylo tedy zveřejněno 4. srpna v den uzávěrky.</p></div>'


def update_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if OLD_TIMING not in text:
        if NEW_TIMING not in text:
            raise RuntimeError(f"V {path} nebyla nalezena původní ani opravená věta o videu ANO.")
    else:
        text = text.replace(OLD_TIMING, NEW_TIMING)
    if OLD_FOLLOW in text:
        text = text.replace(OLD_FOLLOW, NEW_FOLLOW)
    elif NEW_FOLLOW not in text:
        raise RuntimeError(f"V {path} nebyla nalezena navazující věta o videu ANO.")
    if OLD_SOURCE in text:
        text = text.replace(OLD_SOURCE, NEW_SOURCE)
    elif NEW_SOURCE not in text:
        raise RuntimeError(f"V {path} nebyla nalezena zdrojová poznámka k videu ANO.")

    if path == ARTICLE:
        text = re.sub(
            r'<meta property="article:modified_time" content="[^"]+">',
            f'<meta property="article:modified_time" content="{MODIFIED}">',
            text,
            count=1,
        )
        text = re.sub(
            r'"dateModified":"[^"]+"',
            f'"dateModified":"{MODIFIED}"',
            text,
            count=1,
        )
        if 'data-correction="ano-video-timing"' not in text:
            marker = '<h2>Piráti ukazují jména, úřední potvrzení teprve přijde</h2>'
            if marker not in text:
                raise RuntimeError("V článku chybí místo pro redakční upřesnění.")
            text = text.replace(marker, NOTE + "\n" + marker, 1)
    else:
        if 'MODIFIED = "2026-08-04T19:06:00+02:00"' not in text:
            text = text.replace(
                'PUBLISHED = "2026-08-04T18:46:00+02:00"\n',
                'PUBLISHED = "2026-08-04T18:46:00+02:00"\nMODIFIED = "2026-08-04T19:06:00+02:00"\n',
                1,
            )
        text = text.replace('"dateModified": PUBLISHED,', '"dateModified": MODIFIED,')
        text = text.replace(
            '<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">',
            '<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{MODIFIED}">',
        )
        text = text.replace('"modified_at": PUBLISHED,', '"modified_at": MODIFIED,')
        text = text.replace('"modified_at": PUBLISHED, "publication_status"', '"modified_at": MODIFIED, "publication_status"')
        if 'data-correction="ano-video-timing"' not in text:
            marker = '<h2>Piráti ukazují jména, úřední potvrzení teprve přijde</h2>'
            if marker not in text:
                raise RuntimeError("V generátoru chybí místo pro redakční upřesnění.")
            text = text.replace(marker, NOTE + "\n" + marker, 1)

    path.write_text(text, encoding="utf-8", newline="\n")


def update_registry() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    article = next((item for item in data.get("articles", []) if item.get("url") == URL), None)
    if not article:
        raise RuntimeError("V kanonickém registru chybí volební článek.")
    article["modified_at"] = MODIFIED
    validation = data.setdefault("validation", {})
    validation["last_consistency_repair"] = {
        "classification": "incorrect_source_publication_timing",
        "reason": "Video ANO bylo původně nesprávně popsáno jako zveřejněné v den uzávěrky; snímek Facebooku ukazuje údaj před 4 dny.",
        "updated_url": URL,
        "old_claim": "Video bylo zveřejněno v den uzávěrky 4. srpna 2026.",
        "new_claim": "Video bylo zveřejněno několik dní před uzávěrkou; Facebook zobrazoval údaj před 4 dny.",
        "status": "pending_public_verification",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    REGISTRY.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    update_text(ARTICLE)
    update_text(GENERATOR)
    update_registry()
    article = ARTICLE.read_text(encoding="utf-8")
    if "zveřejnil v den uzávěrky" in article or "ze 4. srpna 2026" in article:
        raise RuntimeError("V článku zůstalo chybné časové zařazení videa ANO.")
    if "před 4 dny" not in article or 'data-correction="ano-video-timing"' not in article:
        raise RuntimeError("Oprava videa ANO není v článku úplná.")
    print("Opraveno časové zařazení videa ANO v článku, generátoru a registru.")


if __name__ == "__main__":
    main()
