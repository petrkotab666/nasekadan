#!/usr/bin/env python3
"""Bezpečný závěrečný krok lokální aktualizace webu Naše Kadaň.

Tento vstupní bod nesmí vracet veřejný web na historickou šablonu. Spouští jen
současné idempotentní publikační a kontrolní kroky. Hlavní serverová pojistka už
používá plný kanonický Docker build; tento soubor zůstává druhou ochranou pro
starší servisní volání.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*parts: str) -> None:
    command = [PYTHON, *parts]
    print("Spouštím:", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def on_production_vps() -> bool:
    return ROOT == Path("/opt/nasekadan")


def repair_newsletter_smtp() -> None:
    repair_script = ROOT / "deploy" / "repair-newsletter-smtp.sh"
    env_file = Path("/etc/nasekadan-newsletter.env")
    if not on_production_vps() or not env_file.exists() or not repair_script.exists():
        print("Newsletter SMTP: nejde o produkční VPS, oprava se přeskakuje.")
        return
    try:
        subprocess.run(
            ["sudo", "-n", "bash", str(repair_script)],
            cwd=ROOT,
            check=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"Upozornění: oprava SMTP newsletteru nebyla dokončena: {exc}", file=sys.stderr)


def recover_github_runner() -> None:
    if not on_production_vps():
        return
    script = r"""
set -euo pipefail
mapfile -t services < <(systemctl list-unit-files --type=service --no-legend 'actions.runner*' 2>/dev/null | awk '{print $1}' | sort -u)
for service in "${services[@]}"; do
  if ! systemctl is-active --quiet "$service"; then
    systemctl reset-failed "$service" || true
    systemctl restart "$service"
    systemctl is-active --quiet "$service"
  fi
done
"""
    try:
        subprocess.run(
            ["sudo", "-n", "bash", "-lc", script],
            cwd=ROOT,
            check=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"Upozornění: GitHub runner se nepodařilo obnovit: {exc}", file=sys.stderr)


def main() -> int:
    repair_newsletter_smtp()
    recover_github_runner()

    run("scripts/ensure_publication_integrity.py")
    run("scripts/ensure_newest_article_indexes.py")
    run("scripts/publish_avies_article.py")
    run("scripts/ensure_avies_publication_assets.py")

    # Tyto dva kroky jsou zásadní: syrový článek v repozitáři je historický
    # základ, ale veřejná verze musí vždy obsahovat spuštěnou soukromou petici,
    # dva ověřené podpisy při kontrole a shodu všech osmi požadavků.
    run("scripts/update_online_petition_status.py")
    run("scripts/update_petition_verified_details.py")

    run("scripts/ensure_petition_document_details.py")
    run("scripts/link_hospital_series.py")
    run("scripts/normalize_footers.py", "--write", "--check")
    run("scripts/validate_publication_integrity.py")

    print("Finální kontrola webu je v pořádku; stará verze článku o petici se nemůže vrátit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
