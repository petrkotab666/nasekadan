#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_monitoring_registry import ROOT, read_json

MAX_AGE_MINUTES = {"urgent": 45, "hourly": 150, "daily": 36 * 60}


def parse_time(value: object) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--json-output")
    parser.add_argument("--workflow-runs")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    registry = read_json(ROOT / "data/monitoring-registry.json")
    workflow_runs = read_json(Path(args.workflow_runs)) if args.workflow_runs else {}
    coverage = registry.get("coverage") or {}
    problems: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []

    if not registry.get("sources"):
        problems.append("Jednotný registr zdrojů chybí nebo je prázdný.")
    if coverage.get("organizationsWithoutUrl"):
        problems.append(f"Organizace bez sledovatelné URL: {', '.join(coverage['organizationsWithoutUrl'])}")
    if coverage.get("missingMunicipalities"):
        problems.append(f"Obce bez oficiálního zdroje: {', '.join(coverage['missingMunicipalities'])}")
    if coverage.get("missingMandatoryCategories"):
        problems.append(f"Chybějící oblasti: {', '.join(coverage['missingMandatoryCategories'])}")

    for mode in ("urgent", "hourly", "daily"):
        status = read_json(ROOT / f"data/monitoring-status-{mode}.json")
        run_info = workflow_runs.get(mode) if isinstance(workflow_runs.get(mode), dict) else {}
        run_time = run_info.get("updatedAt") or run_info.get("createdAt")
        checked = parse_time(run_time) or parse_time(status.get("checkedAt"))
        age = None if checked is None else int((now - checked).total_seconds() // 60)
        required_failed = int(status.get("requiredFailedSources") or 0)
        failed = int(status.get("failedSources") or 0)
        total = int(status.get("sourceCount") or 0)
        checked_sources = int(status.get("checkedSources") or 0)
        rows.append({
            "mode": mode,
            "checkedAt": run_time or status.get("checkedAt"),
            "workflowConclusion": run_info.get("conclusion"),
            "ageMinutes": age,
            "checkedSources": checked_sources,
            "sourceCount": total,
            "failedSources": failed,
            "requiredFailedSources": required_failed,
            "itemsParsed": status.get("itemsParsed"),
            "relevantItems": status.get("relevantItems"),
            "newAlerts": status.get("newAlerts"),
        })
        if run_info and run_info.get("conclusion") not in {None, "success"}:
            problems.append(f"Vrstva {mode}: poslední workflow skončilo stavem {run_info.get('conclusion')}. ")
        if not status:
            problems.append(f"Vrstva {mode} zatím nemá stavový soubor.")
            continue
        if age is None or age > MAX_AGE_MINUTES[mode]:
            problems.append(f"Vrstva {mode} je zastaralá: {age if age is not None else 'neznámé'} minut.")
        if required_failed:
            problems.append(f"Vrstva {mode}: {required_failed} povinných zdrojů je nedostupných.")
        if total and failed / total > 0.20:
            problems.append(f"Vrstva {mode}: selhává {failed}/{total} zdrojů.")
        elif failed:
            warnings.append(f"Vrstva {mode}: dočasně selhává {failed}/{total} nepovinných zdrojů.")

    healthy = not problems
    lines = [
        "## Jednotný zdravotní stav monitoringu Kadaně a Kadaňska",
        "",
        f"- Kontrola: `{now.isoformat()}`",
        f"- Stav: **{'v pořádku' if healthy else 'vyžaduje zásah'}**",
        f"- Registrované zdroje: **{coverage.get('registeredSources', '?')}**",
        f"- Monitorovatelné zdroje: **{coverage.get('monitorableSources', '?')}**",
        f"- Evidované organizace: **{coverage.get('canonicalOrganizations', '?')}**",
        f"- Pokryté obce: **{len(coverage.get('monitoredMunicipalities') or [])}/{len(coverage.get('scopeMunicipalities') or [])}**",
        "",
        "### Stav vrstev",
    ]
    for row in rows:
        lines.append(
            f"- **{row['mode']}** — {row['checkedSources']}/{row['sourceCount']} zdrojů, "
            f"stáří {row['ageMinutes'] if row['ageMinutes'] is not None else 'neznámé'} min, "
            f"nových upozornění {row['newAlerts'] if row['newAlerts'] is not None else '?'}"
        )
    if problems:
        lines += ["", "### Problémy"] + [f"- {item}" for item in problems]
    if warnings:
        lines += ["", "### Upozornění"] + [f"- {item}" for item in warnings]
    if not problems and not warnings:
        lines += ["", "Všechny vrstvy jsou čerstvé a povinné zdroje jsou dostupné."]
    lines += [
        "",
        "Veřejné profily Facebooku a Instagramu jsou evidované v registru, ale bez oficiálního API slouží pouze ke kontrole dostupnosti. Jejich neveřejný obsah nelze spolehlivě automaticky číst.",
        "",
        "_Jeden souhrnný technický záznam pro celý monitoring._",
    ]
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = {"healthy": healthy, "problems": problems, "warnings": warnings, "rows": rows, "coverage": coverage}
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "healthy": healthy, "problems": len(problems), "warnings": len(warnings)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
