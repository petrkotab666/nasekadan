#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=/etc/nasekadan-newsletter.env
SERVICE=nasekadan-newsletter.service

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Newsletter SMTP: $ENV_FILE neexistuje, oprava se přeskakuje."
  exit 0
fi

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
