#!/usr/bin/env bash
set -euo pipefail

ROOT="${GITHUB_WORKSPACE:-$(pwd)}"
cd "$ROOT"

# Dočasná idempotentní oprava dvou fotografií, které byly dříve omylem
# uloženy jako textový Base64 místo binárního WebP. Běží před každým buildem,
# takže živý web vždy dostane skutečné obrázky, i než se uklidí pomocné soubory.
RAFANDA_DIR="images/clanky/eso-market-rafanda"
NAVOD_PARTS=".github/tmp/rafanda-photo-fix"
PRAVIDLA_B64="tmp/rafanda-candidates/05-4660.bin"
if [[ -d "$NAVOD_PARTS" && -f "$PRAVIDLA_B64" && -f "$RAFANDA_DIR/prodejna-rafanda-24-7.webp" ]]; then
  mkdir -p "$RAFANDA_DIR" social
  cat "$NAVOD_PARTS"/navod.part* | base64 -d > "$RAFANDA_DIR/navod-vstup-nakup-odchod.webp"
  base64 -d "$PRAVIDLA_B64" > "$RAFANDA_DIR/pravidla-platba-kamery.webp"
  cp "$RAFANDA_DIR/prodejna-rafanda-24-7.webp" social/eso-market-rafanda-kadan-24-7.webp
  file "$RAFANDA_DIR"/*.webp social/eso-market-rafanda-kadan-24-7.webp | grep -q 'Web/P image'
  test "$(stat -c %s "$RAFANDA_DIR/prodejna-rafanda-24-7.webp")" -gt 10000
  test "$(stat -c %s "$RAFANDA_DIR/navod-vstup-nakup-odchod.webp")" -gt 10000
  test "$(stat -c %s "$RAFANDA_DIR/pravidla-platba-kamery.webp")" -gt 10000
  echo "Rafanda: tři redakční fotografie byly před buildem ověřeny jako WebP."
fi

ENV_FILE=/etc/nasekadan-newsletter.env
SERVICE=nasekadan-newsletter.service

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Newsletter SMTP: $ENV_FILE neexistuje, oprava se přeskakuje."
else
  sudo python3 - "$ENV_FILE" <<'PY'
from __future__ import annotations

import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
lines = text.splitlines()

required = {
    "NEWSLETTER_BASE_URL": "https://nasekadan.cz",
    "NEWSLETTER_FROM": "info@nasekadan.cz",
    "SMTP_HOST": "smtp.seznam.cz",
    "SMTP_PORT": "465",
    "SMTP_USER": "info@nasekadan.cz",
    "SMTP_TLS": "ssl",
}

seen: set[str] = set()
out: list[str] = []
for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in line:
        out.append(line)
        continue
    key, _ = line.split("=", 1)
    key = key.strip()
    if key in required:
        out.append(f"{key}={required[key]}")
        seen.add(key)
    else:
        # SMTP_PASSWORD a ostatní neveřejné hodnoty zůstávají beze změny.
        out.append(line)

for key, value in required.items():
    if key not in seen:
        out.append(f"{key}={value}")

password_present = False
for line in out:
    if line.startswith("SMTP_PASSWORD=") and line.split("=", 1)[1].strip():
        password_present = True
        break

path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
os.chmod(path, 0o600)
print("Newsletter SMTP: host=smtp.seznam.cz port=465 tls=ssl user=info@nasekadan.cz")
print(f"Newsletter SMTP: heslo_nastaveno={'ano' if password_present else 'ne'}")
PY

  if systemctl list-unit-files "$SERVICE" --no-legend 2>/dev/null | grep -q '^nasekadan-newsletter.service'; then
    sudo systemctl restart "$SERVICE"
    sudo systemctl is-active --quiet "$SERVICE"
    echo "Newsletter SMTP: služba byla restartována a je aktivní."
  else
    echo "Newsletter SMTP: služba $SERVICE není nainstalována, restart se přeskakuje."
  fi
fi

STATS_DIR="${GITHUB_WORKSPACE:-$(pwd)}/.github/scripts/nasekadan-stats"
STATS_INSTALLER="$STATS_DIR/install-stats.sh"
if [[ -f "$STATS_INSTALLER" ]]; then
  echo "Statistiky: instaluji vlastní přihlášení a obnovu hesla přes e-mail."
  sudo env NASEKADAN_STATS_SOURCE_DIR="$STATS_DIR" bash "$STATS_INSTALLER"
else
  echo "Statistiky: instalátor $STATS_INSTALLER nebyl nalezen, krok se přeskakuje."
fi
