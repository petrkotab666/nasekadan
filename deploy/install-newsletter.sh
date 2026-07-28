#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/nasekadan
ENV_FILE=/etc/nasekadan-newsletter.env
CADDY_SITE=/etc/caddy/sites-enabled/nasekadan.caddy

sudo install -d -m 750 -o www-data -g www-data /var/lib/nasekadan-newsletter
sudo tee /etc/systemd/system/nasekadan-newsletter.service >/dev/null <<'EOF'
[Unit]
Description=Newsletter Naše Kadaň
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=www-data
Group=www-data
EnvironmentFile=-/etc/nasekadan-newsletter.env
ExecStart=/usr/bin/python3 /opt/nasekadan/newsletter/server.py
Restart=on-failure
RestartSec=5
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/nasekadan-newsletter
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

if [[ ! -f "$ENV_FILE" ]]; then
  sudo tee "$ENV_FILE" >/dev/null <<'EOF'
NEWSLETTER_BASE_URL=https://nasekadan.cz
NEWSLETTER_FROM=info@nasekadan.cz
NEWSLETTER_DB=/var/lib/nasekadan-newsletter/newsletter.sqlite3
SMTP_HOST=smtp.seznam.cz
SMTP_PORT=465
SMTP_USER=info@nasekadan.cz
SMTP_PASSWORD=
SMTP_TLS=ssl
EOF
  sudo chmod 600 "$ENV_FILE"
fi

# Nikdy už nepřepisovat celý Caddy soubor. Předchozí verze tím odstranila
# /statistiky/, jejich měřicí log i další případné služby. Nově se pouze
# idempotentně doplní newsletterová trasa a vše ostatní se zachová.
sudo install -d -m 0755 /etc/caddy/sites-enabled
if [[ ! -f "$CADDY_SITE" ]]; then
  sudo tee "$CADDY_SITE" >/dev/null <<'EOF'
nasekadan.cz, www.nasekadan.cz {
    handle_path /api/newsletter/* {
        reverse_proxy 127.0.0.1:8765
    }

    handle {
        root * /var/www/nasekadan
        file_server
        encode gzip zstd
    }
}
EOF
else
  sudo python3 - "$CADDY_SITE" <<'PY'
from __future__ import annotations

import datetime as dt
import re
import shutil
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
if re.search(r"(?m)^\s*handle_path\s+/api/newsletter/\*\s*\{", text):
    print("Caddy: newsletterová trasa už existuje; ostatní konfigurace zůstala beze změny.")
    raise SystemExit(0)

site = re.search(r"(?m)^\s*nasekadan\.cz\s*,\s*www\.nasekadan\.cz\s*\{\s*$", text)
if not site:
    raise SystemExit("Caddy: blok nasekadan.cz nebyl nalezen; bezpečnostní zastavení bez přepsání souboru.")

block = '''
    # BEGIN NASEKADAN_NEWSLETTER_ROUTE
    handle_path /api/newsletter/* {
        reverse_proxy 127.0.0.1:8765
    }
    # END NASEKADAN_NEWSLETTER_ROUTE
'''
new_text = text[:site.end()] + "\n" + block + text[site.end():]
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
backup = path.with_name(path.name + f".bak-{stamp}")
shutil.copy2(path, backup)
path.write_text(new_text, encoding="utf-8")
print(f"Caddy: doplněna pouze newsletterová trasa; záloha {backup}.")
PY
fi

sudo systemctl daemon-reload
sudo systemctl enable --now nasekadan-newsletter.service
sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
sudo systemctl reload caddy

echo "Newsletter backend nainstalován bez přepsání statistik. Doplňte pouze SMTP_PASSWORD v $ENV_FILE a spusťte: sudo systemctl restart nasekadan-newsletter"