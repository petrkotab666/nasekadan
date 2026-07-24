#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/nasekadan"
WEB_DIR="/var/www/nasekadan"
if [[ ! -d "$APP_DIR/.git" ]]; then echo "Chybí $APP_DIR/.git – nejdřív nasaďte repozitář." >&2; exit 1; fi
sudo tee /usr/local/sbin/nasekadan-refresh >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/nasekadan"
WEB_DIR="/var/www/nasekadan"
LOCK="/run/lock/nasekadan-refresh.lock"
exec 9>"$LOCK"
flock -n 9 || exit 0
chown -R ubuntu:ubuntu "$APP_DIR"
su - ubuntu -c "git -C '$APP_DIR' fetch origin && git -C '$APP_DIR' reset --hard origin/main"
python3 "$APP_DIR/scripts/update_events.py"
python3 "$APP_DIR/scripts/update_sports.py"
python3 "$APP_DIR/scripts/update_city_news.py"
python3 "$APP_DIR/scripts/generate_complete_guides.py"
python3 "$APP_DIR/scripts/ensure_favicon.py"
python3 "$APP_DIR/scripts/finalize_site.py"
rsync -a --delete --exclude='.git' --exclude='.github' --exclude='deploy' --exclude='Dockerfile' --exclude='docker-compose.yml' --exclude='nginx' "$APP_DIR/" "$WEB_DIR/"
chown -R www-data:www-data "$WEB_DIR"
nginx -t
systemctl reload nginx
EOF
sudo chmod 755 /usr/local/sbin/nasekadan-refresh
sudo tee /etc/systemd/system/nasekadan-refresh.service >/dev/null <<'EOF'
[Unit]
Description=Aktualizace webu Naše Kadaň
After=network-online.target nginx.service
Wants=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-refresh
User=root
Nice=10
EOF
sudo tee /etc/systemd/system/nasekadan-refresh.timer >/dev/null <<'EOF'
[Unit]
Description=Pravidelná aktualizace Naše Kadaň
[Timer]
OnBootSec=2min
OnUnitActiveSec=30min
RandomizedDelaySec=90
Persistent=true
Unit=nasekadan-refresh.service
[Install]
WantedBy=timers.target
EOF
sudo systemctl daemon-reload
sudo systemctl reset-failed nasekadan-refresh.service || true
sudo systemctl enable --now nasekadan-refresh.timer
sudo systemctl restart nasekadan-refresh.timer
# Dlouhá aktualizace běží mimo deploy; ostré soubory hned poté nasadí finální krok workflow.
sudo systemctl start --no-block nasekadan-refresh.service || true
echo "Automatizace je aktivní každých 30 minut přes Nginx včetně SEO postprocesoru."
