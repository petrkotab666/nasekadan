#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="${NASEKADAN_STATS_SOURCE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
BASE_DIR="/opt/nasekadan-stats"
APP_DIR="/usr/local/lib/nasekadan-stats"
LOG_FILE="/var/log/nginx/nasekadan.access.log"
GLOBAL_CONF="/etc/nginx/conf.d/00-nasekadan-statistiky.conf"
SNIPPET="/etc/nginx/snippets/nasekadan-statistiky-server.conf"
AUTH_FILE="/etc/nginx/.nasekadan-stats.htpasswd"
SERVICE_FILE="/etc/systemd/system/nasekadan-stats-web.service"
LOGROTATE_CONF="/etc/logrotate.d/nasekadan-statistiky"
CADDY_SITE="/etc/caddy/sites-enabled/nasekadan.caddy"

if [[ $(id -u) -ne 0 ]]; then
  echo "Instalace statistik musí běžet přes sudo/root." >&2
  exit 1
fi

for cmd in nginx python3 systemctl curl; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "Na serveru chybí příkaz: $cmd" >&2
    exit 1
  }
done

if [[ ! -f "$SCRIPT_DIR/stats_server.py" ]]; then
  echo "Chybí $SCRIPT_DIR/stats_server.py" >&2
  exit 1
fi

# Odstranit starý nefunkční Nginx patcher. Ochranu Caddy zajišťuje přímo tento
# instalátor a později také bezpečný instalátor newsletteru.
systemctl disable --now nasekadan-stats-patch.path >/dev/null 2>&1 || true
systemctl disable --now nasekadan-stats-patch.timer >/dev/null 2>&1 || true
systemctl stop nasekadan-stats-patch.service >/dev/null 2>&1 || true
rm -f \
  /etc/systemd/system/nasekadan-stats-patch.path \
  /etc/systemd/system/nasekadan-stats-patch.timer \
  /etc/systemd/system/nasekadan-stats-patch.service \
  /usr/local/sbin/nasekadan-stats-patch-nginx \
  /usr/local/lib/nasekadan-stats/patch_nginx.py

install -d -o www-data -g www-data -m 0750 "$BASE_DIR"
install -d -o root -g root -m 0755 "$APP_DIR" /etc/nginx/snippets

# Statistiky musí umět přečíst jak starší Nginx logy, tak nové Caddy logy.
# Soubory ani jejich rotované kopie se zde nemažou ani nevynulují.
for group in adm caddy; do
  if getent group "$group" >/dev/null 2>&1; then
    usermod -a -G "$group" www-data >/dev/null 2>&1 || true
  fi
done
if id caddy >/dev/null 2>&1; then
  install -d -o caddy -g caddy -m 0750 /var/log/caddy
else
  install -d -o root -g adm -m 0750 /var/log/caddy
fi

if [[ ! -s "$BASE_DIR/secret-salt" ]]; then
  umask 077
  python3 - <<'PY' > "$BASE_DIR/secret-salt"
import secrets
print(secrets.token_hex(32))
PY
fi
chown www-data:www-data "$BASE_DIR/secret-salt"
chmod 0600 "$BASE_DIR/secret-salt"

install -o root -g root -m 0755 "$SCRIPT_DIR/stats_server.py" "$APP_DIR/stats_server.py"
python3 -m py_compile "$APP_DIR/stats_server.py"

if [[ ! -s "$AUTH_FILE" ]]; then
  cat > "$AUTH_FILE" <<'AUTH'
petr:$6$0fYivzmVKD4frCS.$b.4N1tRkqzCtlApstFsa5/jKW8zr7t2cGb90U8hGXJwu9MsuvJ1/uVY0eC7ahYGdlOJDWxPx9fiA48dTRPYPQ/
AUTH
fi
chown root:www-data "$AUTH_FILE"
chmod 0640 "$AUTH_FILE"

cat > "$GLOBAL_CONF" <<'NGINX'
# Naše Kadaň – samostatný JSON log pro soukromé statistiky.
map $request_uri $nasekadan_stats_loggable {
    default 1;
}

log_format nasekadan_stats escape=json
    '{"ts":"$time_iso8601","ip":"$remote_addr","method":"$request_method",'
    '"uri":"$request_uri","status":$status,"bytes":$body_bytes_sent,'
    '"ref":"$http_referer","ua":"$http_user_agent"}';
NGINX

cat > "$SNIPPET" <<'NGINX'
# Naše Kadaň – sběr návštěvnosti a vlastní přihlášení ke statistikám.
access_log /var/log/nginx/nasekadan.access.log nasekadan_stats;

location = /statistiky {
    return 301 /statistiky/;
}

location ^~ /statistiky/ {
    access_log off;
    proxy_pass http://127.0.0.1:3225/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    add_header Cache-Control "no-store, no-cache, must-revalidate" always;
    add_header Pragma "no-cache" always;
    add_header X-Robots-Tag "noindex, nofollow, noarchive" always;
    add_header X-Content-Type-Options "nosniff" always;
}

# Naše Kadaň – soukromé náhledy článků zůstávají oddělené od statistik.
location = /nahled {
    return 301 /nahled/;
}

location ^~ /nahled/ {
    auth_basic "Naše Kadaň – soukromý náhled";
    auth_basic_user_file /etc/nginx/.nasekadan-stats.htpasswd;
    access_log off;
    proxy_pass http://127.0.0.1:3224/nahled/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    add_header Cache-Control "no-store, no-cache, must-revalidate" always;
    add_header Pragma "no-cache" always;
    add_header X-Robots-Tag "noindex, nofollow,noarchive" always;
    add_header X-Content-Type-Options "nosniff" always;
}
NGINX

if [[ ! -e "$LOG_FILE" ]]; then
  install -o www-data -g adm -m 0640 /dev/null "$LOG_FILE" 2>/dev/null || touch "$LOG_FILE"
fi
chown www-data:adm "$LOG_FILE" 2>/dev/null || chown www-data:www-data "$LOG_FILE"
chmod 0640 "$LOG_FILE"

cat > "$LOGROTATE_CONF" <<'LOGROTATE'
/var/log/nginx/nasekadan.access.log {
    daily
    rotate 180
    maxsize 20M
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        if [ -s /run/nginx.pid ]; then
            kill -USR1 "$(cat /run/nginx.pid)" 2>/dev/null || true
        fi
    endscript
}
LOGROTATE

cat > "$SERVICE_FILE" <<'UNIT'
[Unit]
Description=Soukromé statistiky webu Naše Kadaň
After=network.target nginx.service
Wants=nginx.service

[Service]
Type=simple
User=www-data
Group=www-data
# Obecná newsletterová konfigurace je načtena první. Oddělená konfigurace
# statistik ji může bezpečně přepsat, aniž by měnila newsletter.
EnvironmentFile=-/etc/nasekadan-newsletter.env
EnvironmentFile=-/etc/nasekadan-stats-email.env
ExecStart=/usr/bin/python3 /usr/local/lib/nasekadan-stats/stats_server.py
Restart=on-failure
RestartSec=2
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/opt/nasekadan-stats
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable nasekadan-stats-web.service >/dev/null
systemctl restart nasekadan-stats-web.service

for _ in $(seq 1 30); do
  if curl -fsS --max-time 2 http://127.0.0.1:3225/healthz >/tmp/nasekadan-stats-health.json 2>/dev/null; then
    break
  fi
  sleep 0.3
done
curl -fsS --max-time 3 http://127.0.0.1:3225/healthz | grep -Fq '"ok": true'
curl -fsS --max-time 3 http://127.0.0.1:3225/ | grep -Fq 'Zapomenuté heslo'

nginx -t
systemctl reload nginx

# Caddy je veřejná vstupní vrstva webu. Původní instalátor pouze upravoval
# již existující blok, a po jeho přepsání newsletterem proto vznikla 404.
# Nově trasu i měřicí log bezpečně doplníme, pokud chybějí, a vše ostatní
# v konfiguraci (newsletter, web, další služby) ponecháme beze změny.
if [[ -f "$CADDY_SITE" ]] && command -v caddy >/dev/null 2>&1; then
  python3 - "$CADDY_SITE" <<'PY'
from __future__ import annotations

import datetime as dt
import re
import shutil
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
original = text
lines = text.splitlines(keepends=True)
out: list[str] = []
i = 0
in_stats = False
stats_depth = 0
removed_auth = 0

# Odstranit jen případný starý Caddy Basic Auth uvnitř statistik. Vlastní
# přihlášení zajišťuje aplikace na portu 3225; ochrany jiných cest se nedotýkáme.
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    if not in_stats and re.match(r"^handle_path\s+/statistiky/\*\s*\{\s*$", stripped):
        in_stats = True
        stats_depth = line.count("{") - line.count("}")
        out.append(line)
        i += 1
        continue
    if in_stats and re.match(r"^basic_auth\s*\{\s*$", stripped):
        depth = line.count("{") - line.count("}")
        i += 1
        while i < len(lines) and depth > 0:
            depth += lines[i].count("{") - lines[i].count("}")
            i += 1
        removed_auth += 1
        continue
    out.append(line)
    if in_stats:
        stats_depth += line.count("{") - line.count("}")
        if stats_depth <= 0:
            in_stats = False
    i += 1

text = "".join(out)
site = re.search(r"(?m)^(?P<indent>\s*)nasekadan\.cz\s*,\s*www\.nasekadan\.cz\s*\{\s*$", text)
if not site:
    raise SystemExit("Caddy: nebyl nalezen blok nasekadan.cz, konfigurace nebyla změněna.")

parts: list[str] = []
if not re.search(r"(?m)^\s*handle_path\s+/statistiky/\*\s*\{", text):
    parts.append('''
    # BEGIN NASEKADAN_STATS_ROUTE_V4
    redir /statistiky /statistiky/ 308

    handle_path /statistiky/* {
        header {
            Cache-Control "no-store, no-cache, must-revalidate"
            Pragma "no-cache"
            X-Robots-Tag "noindex, nofollow, noarchive"
            X-Content-Type-Options "nosniff"
        }
        reverse_proxy 127.0.0.1:3225
    }
    # END NASEKADAN_STATS_ROUTE_V4
''')

if not re.search(r"(?m)^\s*log\s+nk_counter\s*\{", text):
    parts.append('''
    # BEGIN NASEKADAN_STATS_LOG_V4
    log nk_counter {
        output file /var/log/caddy/nasekadan.access.log {
            mode 0640
            roll_size 20MiB
            roll_keep 180
            roll_keep_for 4320h
        }
    }
    # END NASEKADAN_STATS_LOG_V4
''')

if parts:
    insert_at = site.end()
    text = text[:insert_at] + "\n" + "".join(parts) + text[insert_at:]

if text != original:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(path.name + f".bak-{stamp}")
    shutil.copy2(path, backup)
    path.write_text(text, encoding="utf-8")
    print(f"Caddy: obnovena/potvrzena trasa statistik, záloha {backup}; odstraněné staré auth bloky: {removed_auth}.")
else:
    print("Caddy: trasa statistik i měřicí log jsou už správně nastavené; bez změny.")
PY
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
  systemctl reload caddy
fi

curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  https://nasekadan.cz/statistiky/ | grep -Fq 'Zapomenuté heslo'
curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  https://nasekadan.cz/statistiky/zapomenute-heslo | grep -Fq 'petrkotab@seznam.cz'

preview_status="$(curl -kisS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  https://nasekadan.cz/nahled/ | awk 'NR==1 {print $2}')"
if [[ ! "$preview_status" =~ ^(401|404|502|503)$ ]]; then
  echo "Neočekávaný veřejný stav /nahled/: $preview_status" >&2
  exit 1
fi

echo "Datové soubory statistik (pouze velikosti a data, obsah se nevypisuje):"
find /var/log/nginx /var/log/caddy -maxdepth 1 -type f \
  \( -name 'nasekadan.access.log' -o -name 'nasekadan.access.log.*' -o -name 'nasekadan.access.log-*.gz' \) \
  -printf '%p | %s B | %TY-%Tm-%Td %TH:%TM:%TS\n' 2>/dev/null | sort || true

echo "HOTOVO: statistiky mají obnovenou veřejnou trasu, pokračující měření a vlastní přihlášení s resetem pouze přes petrkotab@seznam.cz."