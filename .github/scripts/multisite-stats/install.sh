#!/usr/bin/env bash
set -Eeuo pipefail

BASE_DIR=/opt/multisite-stats
APP_DIR=/usr/local/lib/multisite-stats
LOG_FILE=/var/log/nginx/multisite-stats.access.log
GLOBAL_CONF=/etc/nginx/conf.d/00-multisite-statistiky-log.conf
SNIPPET=/etc/nginx/snippets/multisite-statistiky-server.conf
HTPASSWD=$BASE_DIR/.htpasswd
SERVICE=/etc/systemd/system/multisite-stats.service
ENSURE_SERVICE=/etc/systemd/system/multisite-stats-ensure.service
ENSURE_TIMER=/etc/systemd/system/multisite-stats-ensure.timer
BACKUP_SERVICE=/etc/systemd/system/multisite-stats-backup.service
BACKUP_TIMER=/etc/systemd/system/multisite-stats-backup.timer
LOGROTATE=/etc/logrotate.d/multisite-statistiky

if [[ $(id -u) -ne 0 ]]; then
  echo 'Instalace musí běžet jako root.' >&2
  exit 1
fi
for cmd in nginx python3 systemctl curl; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Chybí příkaz $cmd" >&2; exit 1; }
done

install -d -o www-data -g www-data -m 0750 "$BASE_DIR" "$BASE_DIR/backups"
install -d -o root -g root -m 0755 "$APP_DIR" /etc/nginx/snippets
install -o root -g root -m 0755 /tmp/multisite_stats.py "$APP_DIR/multisite_stats.py"
install -o root -g root -m 0755 /tmp/patch_nginx.py "$APP_DIR/patch_nginx.py"
python3 -m py_compile "$APP_DIR/multisite_stats.py" "$APP_DIR/patch_nginx.py"

if [[ ! -s "$BASE_DIR/secret-salt" ]]; then
  umask 077
  python3 - <<'PY' > "$BASE_DIR/secret-salt"
import secrets
print(secrets.token_hex(32))
PY
fi
chown www-data:www-data "$BASE_DIR/secret-salt"
chmod 0640 "$BASE_DIR/secret-salt"

AUTH_USER=''
AUTH_PASS=''
AUTH_SOURCE=''
if [[ -s /opt/nasekadan-stats/access.txt ]]; then
  line=$(sed -n '1{s/\r$//;p;}' /opt/nasekadan-stats/access.txt)
  if [[ "$line" == *:* ]]; then
    AUTH_USER=${line%%:*}
    AUTH_PASS=${line#*:}
    AUTH_USER=$(printf '%s' "$AUTH_USER" | xargs)
    AUTH_PASS=$(printf '%s' "$AUTH_PASS" | sed 's/^[[:space:]]*//')
    [[ -n "$AUTH_USER" && -n "$AUTH_PASS" ]] && AUTH_SOURCE='nasekadan-access'
  fi
fi
if [[ -z "$AUTH_SOURCE" && -s /opt/nasekadan-stats/login.txt ]]; then
  AUTH_USER=$(sed -n -E 's/^Uzivatel:[[:space:]]*//p' /opt/nasekadan-stats/login.txt | head -n1 | tr -d '\r')
  AUTH_PASS=$(sed -n -E 's/^Heslo:[[:space:]]*//p' /opt/nasekadan-stats/login.txt | head -n1 | tr -d '\r')
  [[ -n "$AUTH_USER" && -n "$AUTH_PASS" ]] && AUTH_SOURCE='nasekadan-login'
fi
if [[ -z "$AUTH_SOURCE" ]]; then
  AUTH_USER='petr'
  AUTH_PASS=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(18))
PY
)
  AUTH_SOURCE='generated-server-only'
  umask 077
  printf 'Adresa: https://DOMENA/statistiky/\nUzivatel: %s\nHeslo: %s\n' "$AUTH_USER" "$AUTH_PASS" > /root/multisite-stats-login.txt
fi

AUTH_USER="$AUTH_USER" AUTH_PASS="$AUTH_PASS" python3 - <<'PY' > "$HTPASSWD"
import base64, hashlib, os
user=os.environ['AUTH_USER']
password=os.environ['AUTH_PASS']
digest=base64.b64encode(hashlib.sha1(password.encode('utf-8')).digest()).decode('ascii')
print(f"{user}:{{SHA}}{digest}")
PY
chown root:www-data "$HTPASSWD"
chmod 0640 "$HTPASSWD"

cat > "$GLOBAL_CONF" <<'NGINX'
log_format multisite_stats_json escape=json
  '{"ts":"$time_iso8601","host":"$host","ip":"$remote_addr",'
  '"method":"$request_method","uri":"$request_uri","status":$status,'
  '"ref":"$http_referer","ua":"$http_user_agent"}';
NGINX

cat > "$SNIPPET" <<'NGINX'
access_log /var/log/nginx/multisite-stats.access.log multisite_stats_json;

location = /statistiky {
  return 301 /statistiky/;
}

location ^~ /statistiky/ {
  auth_basic "Soukrome statistiky webu";
  auth_basic_user_file /opt/multisite-stats/.htpasswd;

  proxy_http_version 1.1;
  proxy_set_header Host $host;
  proxy_set_header X-Stats-Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_pass http://127.0.0.1:3226/;
}
NGINX

install -o www-data -g adm -m 0640 /dev/null "$LOG_FILE" 2>/dev/null || {
  touch "$LOG_FILE"
  chown www-data:adm "$LOG_FILE"
  chmod 0640 "$LOG_FILE"
}

cat > "$SERVICE" <<'UNIT'
[Unit]
Description=Soukrome statistiky vsech webu
After=network.target nginx.service
Wants=nginx.service

[Service]
Type=simple
User=www-data
Group=www-data
SupplementaryGroups=adm
WorkingDirectory=/usr/local/lib/multisite-stats
ExecStart=/usr/bin/python3 /usr/local/lib/multisite-stats/multisite_stats.py
Restart=always
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=full
ReadWritePaths=/opt/multisite-stats /var/log/nginx

[Install]
WantedBy=multi-user.target
UNIT

cat > "$ENSURE_SERVICE" <<'UNIT'
[Unit]
Description=Obnovit zapojeni statistik do vsech Nginx webu
After=nginx.service

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/lib/multisite-stats/patch_nginx.py --reload
UNIT

cat > "$ENSURE_TIMER" <<'UNIT'
[Unit]
Description=Pravidelna kontrola statistik vsech webu

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
AccuracySec=30s
Persistent=true

[Install]
WantedBy=timers.target
UNIT

cat > "$BACKUP_SERVICE" <<'UNIT'
[Unit]
Description=Zaloha databaze statistik vsech webu

[Service]
Type=oneshot
User=www-data
Group=www-data
ExecStart=/bin/bash -c '/usr/bin/python3 -c "import sqlite3,datetime,pathlib; s=sqlite3.connect(\"/opt/multisite-stats/stats.sqlite3\"); p=pathlib.Path(\"/opt/multisite-stats/backups\")/(\"stats-\"+datetime.datetime.now().strftime(\"%%Y%%m%%d-%%H%%M%%S\")+\".sqlite3\"); d=sqlite3.connect(p); s.backup(d); d.close(); s.close()"; find /opt/multisite-stats/backups -type f -name "stats-*.sqlite3" -mtime +60 -delete'
UNIT

cat > "$BACKUP_TIMER" <<'UNIT'
[Unit]
Description=Denni zaloha statistik vsech webu

[Timer]
OnCalendar=*-*-* 03:40:00
Persistent=true
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
UNIT

cat > "$LOGROTATE" <<'ROTATE'
/var/log/nginx/multisite-stats.access.log {
  daily
  rotate 365
  size 20M
  missingok
  notifempty
  compress
  delaycompress
  create 0640 www-data adm
  sharedscripts
  postrotate
    test ! -s /run/nginx.pid || kill -USR1 $(cat /run/nginx.pid)
  endscript
}
ROTATE

systemctl daemon-reload
systemctl enable --now multisite-stats.service
systemctl enable --now multisite-stats-ensure.timer multisite-stats-backup.timer

PATCH_JSON=$(python3 "$APP_DIR/patch_nginx.py" --reload --json)
echo "$PATCH_JSON" > "$BASE_DIR/last-patch.json"
chown www-data:www-data "$BASE_DIR/last-patch.json"
chmod 0640 "$BASE_DIR/last-patch.json"

for _ in $(seq 1 30); do
  curl -fsS --max-time 3 http://127.0.0.1:3226/healthz >/dev/null 2>&1 && break
  sleep 0.5
done
curl -fsS --max-time 3 http://127.0.0.1:3226/healthz >/dev/null

FIRST_DOMAIN=$(printf '%s' "$PATCH_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print((d.get("domains") or [""])[0])')
DOMAIN_COUNT=$(printf '%s' "$PATCH_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("count",0))')
DOMAINS=$(printf '%s' "$PATCH_JSON" | python3 -c 'import json,sys; print(", ".join(json.load(sys.stdin).get("domains",[])))')

if [[ -n "$FIRST_DOMAIN" ]]; then
  NOW=$(date --iso-8601=seconds)
  printf '{"ts":"%s","host":"%s","ip":"203.0.113.42","method":"GET","uri":"/multisite-statistiky-selftest","status":200,"ref":"-","ua":"Mozilla/5.0 MultisiteStatsHumanTest/1.0"}\n' "$NOW" "$FIRST_DOMAIN" >> "$LOG_FILE"
  for _ in $(seq 1 20); do
    curl -fsS --max-time 5 -H "X-Stats-Host: $FIRST_DOMAIN" http://127.0.0.1:3226/ | grep -q "Statistiky webu $FIRST_DOMAIN" && break
    sleep 0.5
  done
  curl -fsS --max-time 5 -H "X-Stats-Host: $FIRST_DOMAIN" http://127.0.0.1:3226/ | grep -q 'pages-200'
fi

FAILED=''
mapfile -t DOMAIN_ARRAY < <(printf '%s' "$PATCH_JSON" | python3 -c 'import json,sys; print("\n".join(json.load(sys.stdin).get("domains",[])))')
for domain in "${DOMAIN_ARRAY[@]}"; do
  [[ -n "$domain" ]] || continue
  code=$(curl -kLsS --max-time 12 \
    --resolve "$domain:80:127.0.0.1" --resolve "$domain:443:127.0.0.1" \
    -u "$AUTH_USER:$AUTH_PASS" -o /tmp/multisite-stats-check.html -w '%{http_code}' \
    "https://$domain/statistiky/" 2>/dev/null || true)
  if [[ "$code" != '200' ]] || ! grep -q "Statistiky webu $domain" /tmp/multisite-stats-check.html; then
    code=$(curl -kLsS --max-time 12 \
      --resolve "$domain:80:127.0.0.1" --resolve "$domain:443:127.0.0.1" \
      -u "$AUTH_USER:$AUTH_PASS" -o /tmp/multisite-stats-check.html -w '%{http_code}' \
      "http://$domain/statistiky/" 2>/dev/null || true)
  fi
  if [[ "$code" != '200' ]] || ! grep -q "Statistiky webu $domain" /tmp/multisite-stats-check.html; then
    FAILED+="$domain($code) "
  fi
done

nginx -t
systemctl is-active --quiet multisite-stats.service
systemctl is-active --quiet multisite-stats-ensure.timer
systemctl is-active --quiet multisite-stats-backup.timer

echo "AUTH_SOURCE=$AUTH_SOURCE"
echo "DOMAIN_COUNT=$DOMAIN_COUNT"
echo "DOMAINS=$DOMAINS"
if [[ -n "$FAILED" ]]; then
  echo "FAILED_DOMAINS=$FAILED" >&2
  exit 1
fi
echo 'OVERENO: statistiky jsou zapojene a prihlasena stranka funguje na vsech nalezenych webech.'
