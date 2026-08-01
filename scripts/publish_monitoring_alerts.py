#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MODE_LABELS = {
    "urgent": "RYCHLÝ MONITORING KADAŇ",
    "hourly": "MONITORING KADAŇSKO",
    "daily": "DOKUMENTOVÝ MONITORING KADAŇSKO",
}


def text(value: object) -> str:
    return " ".join(str(value or "").split()).strip()


def issue_body(alert: dict[str, Any], mode: str) -> str:
    source = text(alert.get("sourceName")) or "Zdroj"
    category = text(alert.get("category")) or "Kadaňsko"
    published = text(alert.get("published")) or "neuvedeno"
    description = text(alert.get("description"))
    local = ", ".join(text(x) for x in (alert.get("localMatches") or []) if text(x))
    reason = {
        "new_item": "nová položka",
        "updated_item": "významná aktualizace již známé položky",
        "source_changed": "obsahová změna sledovaného zdroje",
    }.get(text(alert.get("reason")), text(alert.get("reason")) or "nový nález")
    return "\n".join([
        "## Nový ověřovací podnět z jednotného monitoringu",
        "",
        f"- **Vrstva:** {mode}",
        f"- **Zdroj:** {source}",
        f"- **Oblast:** {category}",
        f"- **Závažnost:** {text(alert.get('severity')) or 'medium'}",
        f"- **Důvod upozornění:** {reason}",
        f"- **Publikováno zdrojem:** {published}",
        f"- **Místní shoda:** {local or 'přímý místní nebo organizační zdroj'}",
        "",
        f"### {text(alert.get('title')) or 'Nová informace z Kadaňska'}",
        "",
        description[:3000] if description else "_Zdroj neposkytl samostatný perex._",
        "",
        "### Přímý zdroj",
        f"- [{source}]({text(alert.get('url'))})" if text(alert.get("url")) else f"- {source}",
        "",
        "### Redakční postup",
        "Otevřít přímý zdroj, ověřit datum, místo a význam pro Kadaň nebo okolí. Potom rozhodnout o rychlé zprávě, aktualizaci, hlubší rešerši nebo uložení jako podkladu.",
        "",
        "_Upozornění vytvořil jednotný monitoring Kadaně a Kadaňska._",
    ]) + "\n"


def run_upsert(*, fingerprint: str, title: str, body: str, comment_existing: bool = False) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as handle:
        handle.write(body)
        path = handle.name
    try:
        command = [
            "python3", "scripts/upsert_github_issue.py",
            "--fingerprint", fingerprint,
            "--title", title,
            "--body-file", path,
            "--assignee", "petrkotab666",
        ]
        if comment_existing:
            command.append("--comment-existing")
        subprocess.run(command, check=True)
    finally:
        Path(path).unlink(missing_ok=True)


def digest_body(alerts: list[dict[str, Any]], mode: str, checked_at: str) -> str:
    lines = [
        "## Souhrn méně naléhavých nálezů",
        "",
        f"- **Vrstva:** {mode}",
        f"- **Kontrola:** `{checked_at}`",
        f"- **Počet položek:** {len(alerts)}",
        "",
    ]
    for alert in alerts[:50]:
        title = text(alert.get("title")) or "Nová položka"
        source = text(alert.get("sourceName")) or "Zdroj"
        url = text(alert.get("url"))
        category = text(alert.get("category")) or "Kadaňsko"
        lines.append(f"- **{title}** — {source} / {category}" + (f" — {url}" if url else ""))
    lines += [
        "",
        "Tyto položky nebyly vyhodnoceny jako akutní. Slouží jako jeden přehled pro následnou redakční kontrolu.",
        "",
        "_Jednotný monitoring Kadaně a Kadaňska._",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--mode", required=True, choices=sorted(MODE_LABELS))
    args = parser.parse_args()

    if not (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")):
        raise SystemExit("Chybí GITHUB_TOKEN/GH_TOKEN.")
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    alerts = [x for x in (payload.get("alerts") or []) if isinstance(x, dict)]
    status = payload.get("status") or {}
    checked_at = text(status.get("checkedAt")) or datetime.now(timezone.utc).isoformat()
    label = MODE_LABELS[args.mode]

    important: list[dict[str, Any]] = []
    medium: list[dict[str, Any]] = []
    for alert in alerts:
        if text(alert.get("severity")) in {"urgent", "high"}:
            important.append(alert)
        else:
            medium.append(alert)

    for alert in important:
        fingerprint = f"unified-{args.mode}-{text(alert.get('fingerprint'))}"
        title = text(alert.get("title")) or "Nová informace z Kadaňska"
        run_upsert(
            fingerprint=fingerprint,
            title=f"[{label}] {title[:108]} [{fingerprint}]",
            body=issue_body(alert, args.mode),
        )

    if medium:
        checked = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
        period = checked.strftime("%Y-%m-%d")
        fingerprint = f"unified-digest-{args.mode}-{period}"
        run_upsert(
            fingerprint=fingerprint,
            title=f"[{label}] Denní souhrn méně naléhavých nálezů {period} [{fingerprint}]",
            body=digest_body(medium, args.mode, checked_at),
            comment_existing=True,
        )

    print(json.dumps({
        "ok": True,
        "mode": args.mode,
        "alerts": len(alerts),
        "individual": len(important),
        "digest": len(medium),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
