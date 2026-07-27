#!/usr/bin/env python3
"""Bezpečný závěrečný krok lokální aktualizace webu Naše Kadaň.

Historická verze tohoto skriptu znovu přepisovala hlavičky, metadata, sitemapu
a části konstrukce stránek podle staré šablony. Proto mohla pravidelná serverová
aktualizace po správném nasazení vrátit web do staršího stavu. Tento kompatibilní
vstupní bod už obsah nepřestavuje. Pouze spustí současné idempotentní ochrany.
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
    """Na produkčním VPS srovná SMTP a restartuje newsletterovou službu."""

    repair_script = ROOT / "deploy" / "repair-newsletter-smtp.sh"
    env_file = Path("/etc/nasekadan-newsletter.env")
    if not on_production_vps() or not env_file.exists() or not repair_script.exists():
        print("Newsletter SMTP: nejde o produkční VPS, oprava se přeskakuje.")
        return

    command = ["sudo", "-n", "bash", str(repair_script)]
    print("Spouštím bezpečnou opravu SMTP newsletteru na produkčním VPS.")
    try:
        subprocess.run(command, cwd=ROOT, check=True, timeout=60)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        # Dočasná chyba newsletteru nesmí zablokovat zveřejnění již hotového webu.
        print(f"Upozornění: oprava SMTP newsletteru nebyla dokončena: {exc}", file=sys.stderr)


def recover_github_runner() -> None:
    """Je-li self-hosted runner nainstalovaný, ale neběží, znovu jej spustí."""

    if not on_production_vps():
        return

    script = r"""
set -euo pipefail
mapfile -t services < <(systemctl list-unit-files --type=service --no-legend 'actions.runner*' 2>/dev/null | awk '{print $1}' | sort -u)
if [ "${#services[@]}" -eq 0 ]; then
  echo 'GitHub runner: žádná služba actions.runner nebyla nalezena.'
  exit 0
fi
for service in "${services[@]}"; do
  if systemctl is-active --quiet "$service"; then
    echo "GitHub runner: $service je aktivní."
  else
    echo "GitHub runner: obnovuji $service."
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
    # Serverová desetiminutová pojistka tento soubor spouští po každém git pullu.
    # Díky tomu se servisní opravy dostanou na VPS i při nedostupném runneru.
    repair_newsletter_smtp()
    recover_github_runner()

    # Obnovit známé vazby článku o nočních výlukách.
    run("scripts/ensure_publication_integrity.py")

    # Doplnit také všechny novější články, které vznikly až po původní
    # ochraně publikace, zejména ePetici.
    run("scripts/ensure_newest_article_indexes.py")

    # Schválený článek AVIES musí vzniknout a zařadit se také při lokální
    # desetiminutové serverové aktualizaci, nikoli jen v Docker/GitHub buildu.
    # Skript je idempotentní a zachová již publikovanou verzi.
    run("scripts/publish_avies_article.py")

    # Ověřené znění osmi požadavků musí být přímo v hlavním článku o petici,
    # nikoli pouze v samostatném vysvětlení pravidel ePetice.
    run("scripts/ensure_petition_document_details.py")

    # Série o nemocnici se udržuje z jednoho zdroje a nesmí se rozpadnout při
    # serverové aktualizaci.
    run("scripts/link_hospital_series.py")

    # Všechny veřejné stránky dostanou identickou statickou patičku a jeden
    # společný stylesheet. Staré varianty se odstraní.
    run("scripts/normalize_footers.py", "--write", "--check")

    # Závěrečná kontrola je blokující: neúplný web se nesmí překopírovat do
    # veřejného document rootu.
    run("scripts/validate_publication_integrity.py")

    print("Finální kontrola webu je v pořádku; žádná stará šablona nebyla použita.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
