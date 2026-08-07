#!/usr/bin/env python3
"""Kontrola architektury produkčního zápisu Naše Kadaň.

Smyslem je zabránit návratu historického stavu, kdy několik periodických guardů
samo zapisovalo dílčí HTML/assets přímo do /var/www. Tyto guardy smějí už jen
auditovat. Produkční obsah se nasazuje kompletně přes sync-production.sh.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"

AUDIT_ONLY = [
    "article-visibility-guard.yml",
    "publication-integrity-guard.yml",
    "rss-canonical-order-guard.yml",
    "social-badge-quality-v2.yml",
    "guard-header-brand-visibility.yml",
    "rafanda-direct-live-repair-20260807.yml",
]

FORBIDDEN_IN_AUDITS = (
    "/var/www/nasekadan",
    "57.129.43.215",
    "scp ",
    "docker cp",
    "contents: write",
    "git push",
)


def read(name: str) -> str:
    path = WF / name
    if not path.is_file():
        raise SystemExit(f"Chybí povinný workflow: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for name in AUDIT_ONLY:
        text = read(name)
        for token in FORBIDDEN_IN_AUDITS:
            if token in text:
                errors.append(f"{name}: audit-only workflow znovu obsahuje zakázaný zápis: {token!r}")

    canonical = read("canonical-production-deploy.yml")
    required = (
        "deploy/sync-production.sh",
        "nasekadan-main.tgz",
        "Přenést úplný aktuální main na OVH",
        "prodejna-rafanda-24-7.webp",
        "navod-vstup-nakup-odchod.webp",
        "pravidla-platba-kamery-v2.webp",
        "mestska-policie-kadan-fakta-diskuse-2026.html",
        "gymnastika-kadan-treneri-prosinec-2026.html",
    )
    for token in required:
        if token not in canonical:
            errors.append(f"canonical-production-deploy.yml: chybí povinná ochrana {token!r}")

    legacy_canonical = read("deploy-ovh.yml")
    if "deploy/sync-production.sh" not in legacy_canonical:
        errors.append("deploy-ovh.yml: nesmí používat jinou cestu než deploy/sync-production.sh")

    sync = (ROOT / "deploy" / "sync-production.sh").read_text(encoding="utf-8")
    for token in ("git reset --hard origin/main", "docker build", "/var/www/nasekadan", "deployment-health.txt"):
        if token not in sync:
            errors.append(f"deploy/sync-production.sh: chybí kanonická vlastnost {token!r}")

    if errors:
        print("PORUŠENÍ PUBLIKAČNÍ POLITIKY:")
        for error in errors:
            print("-", error)
        raise SystemExit(1)

    print(
        "OK: periodické guardy jsou audit-only; produkční deploy používá úplný main "
        "a kanonický sync-production.sh včetně kontrol Rafandy."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
