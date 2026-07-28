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

# Odstranit starý doplňkový patcher. Konfiguraci nyní spravuje tento instalátor.
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

# Starý hash ponecháváme pouze jako přechodovou možnost do prvního resetu.
# Nové heslo se ukládá jako PBKDF2-SHA256 do /opt/nasekadan-stats/password.json.
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

# Naše Kadaň – soukromé náhledy článků zůstávají chráněné původním Basic Auth.
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
    add_header X-Robots-Tag "noindex, nofollow, noarchive" always;
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
EnvironmentFile=-/etc/nasekadan-newsletter.env
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

echo "HOTOVO: statistiky mají vlastní přihlášení a reset hesla pouze přes petrkotab@seznam.cz."
