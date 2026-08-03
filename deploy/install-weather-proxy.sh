#!/usr/bin/env bash
set -euo pipefail

SITE_CONF="/etc/nginx/sites-available/nasekadan.cz"
SNIPPET="/etc/nginx/snippets/nasekadan-weather.conf"

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

if ! sudo grep -Fq 'include /etc/nginx/snippets/nasekadan-weather.conf;' "$SITE_CONF"; then
  sudo python3 - "$SITE_CONF" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
lines = text.splitlines(keepends=True)
include_path = 'include /etc/nginx/snippets/nasekadan-weather.conf;'

blocks = []
i = 0
while i < len(lines):
    if not re.match(r'^\s*server\s*\{', lines[i]):
        i += 1
        continue
    start = i
    depth = 0
    while i < len(lines):
        code = lines[i].split('#', 1)[0]
        depth += code.count('{') - code.count('}')
        i += 1
        if depth == 0:
            break
    blocks.append((start, i))

candidates = []
for start, end in blocks:
    block = ''.join(lines[start:end])
    if 'nasekadan.cz' in block or '/var/www/nasekadan' in block:
        candidates.append((start, end))

if not candidates:
    raise SystemExit(f'V {path} nebyl nalezen serverový blok pro nasekadan.cz.')

offset = 0
for start, end in candidates:
    adjusted_start = start + offset
    block = ''.join(lines[adjusted_start:end + offset])
    if include_path in block:
        continue
    match = re.match(r'^(\s*)server\s*\{', lines[adjusted_start])
    indent = (match.group(1) if match else '') + '    '
    lines.insert(adjusted_start + 1, f'{indent}{include_path}\n')
    offset += 1

path.write_text(''.join(lines), encoding='utf-8')
PY
fi

sudo nginx -t
sudo systemctl reload nginx

echo "Veřejná proxy počasí je aktivní přes $SNIPPET."
