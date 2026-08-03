#!/usr/bin/env bash
set -euo pipefail

SITE_CONF="/etc/nginx/sites-available/nasekadan.cz"
SNIPPET="/etc/nginx/snippets/nasekadan-weather.conf"
INCLUDE_LINE="    include /etc/nginx/snippets/nasekadan-weather.conf;"

if [[ ! -f "$SITE_CONF" ]]; then
  echo "Chybí veřejná konfigurace $SITE_CONF." >&2
  exit 1
fi

sudo mkdir -p /etc/nginx/snippets
sudo tee "$SNIPPET" >/dev/null <<'NGINX'
# Živá meteorologická data obsluhuje interní kontejner Naše Kadaň.
# Veřejný nginx předává jen dvě pevně omezené cesty; ostatní web zůstává statický.
location = /api/pocasi-predpoved.json {
    proxy_pass http://127.0.0.1:3224;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_connect_timeout 5s;
    proxy_read_timeout 20s;
}

location ^~ /api/chmi-pocasi/ {
    proxy_pass http://127.0.0.1:3224;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_connect_timeout 5s;
    proxy_read_timeout 20s;
}
NGINX

if ! sudo grep -Fq "$INCLUDE_LINE" "$SITE_CONF"; then
  sudo python3 - "$SITE_CONF" "$INCLUDE_LINE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
include_line = sys.argv[2]
text = path.read_text(encoding="utf-8")
marker = "    root /var/www/nasekadan;"
if marker not in text:
    raise SystemExit(f"V {path} chybí očekávaný document root.")
text = text.replace(marker, marker + "\n" + include_line, 1)
path.write_text(text, encoding="utf-8")
PY
fi

sudo nginx -t
sudo systemctl reload nginx

echo "Veřejná proxy počasí je aktivní přes $SNIPPET."
