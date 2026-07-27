#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nasekadan"

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "Chybí $APP_DIR/.git – nejdřív nasaďte repozitář." >&2
  exit 1
fi

# Lokální serverová pojistka je nezávislá na dostupnosti GitHub runneru.
# Každých deset minut stáhne aktuální main a spustí ÚPLNĚ STEJNÝ kanonický
# Docker build jako běžné produkční nasazení. Nikdy nekopíruje syrové HTML
# přímo z repozitáře do /var/www/nasekadan.
sudo tee /usr/local/sbin/nasekadan-refresh >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nasekadan"
REFRESH_LOCK="/run/lock/nasekadan-refresh.lock"

exec 9>"$REFRESH_LOCK"
flock -n 9 || exit 0

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "Chybí $APP_DIR/.git – serverová pojistka nemůže pokračovat." >&2
  exit 1
fi

chown -R ubuntu:ubuntu "$APP_DIR"
su - ubuntu -c "git -C '$APP_DIR' fetch --prune origin main"
su - ubuntu -c "git -C '$APP_DIR' reset --hard origin/main"
su - ubuntu -c "git -C '$APP_DIR' clean -fd"

# sync-production.sh vlastní produkční zámek, sestaví Docker obraz, provede
# všechny publikační transformace, SEO audit, atomické přepnutí document rootu
# a ověření veřejného HTTPS webu. Přepínač zabrání tomu, aby běh z timeru
# znovu instaloval právě běžící timer.
env \
  GITHUB_WORKSPACE="$APP_DIR" \
  NASEKADAN_SKIP_AUTOMATION_INSTALL=1 \
  bash "$APP_DIR/deploy/sync-production.sh"

SOURCE_SHA="$(git -C "$APP_DIR" rev-parse HEAD)"
echo "Naše Kadaň kanonicky aktualizována na $SOURCE_SHA; Docker, Caddy, články a feedy ověřeny."
EOF

sudo chmod 755 /usr/local/sbin/nasekadan-refresh

sudo tee /etc/systemd/system/nasekadan-refresh.service >/dev/null <<'EOF'
[Unit]
Description=Kanonická aktualizace webu Naše Kadaň
After=network-online.target docker.service
Wants=network-online.target docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-refresh
User=root
Nice=10
TimeoutStartSec=30min
EOF

sudo tee /etc/systemd/system/nasekadan-refresh.timer >/dev/null <<'EOF'
[Unit]
Description=Pravidelná kanonická aktualizace Naše Kadaň

[Timer]
OnBootSec=2min
OnUnitActiveSec=10min
RandomizedDelaySec=30
Persistent=true
Unit=nasekadan-refresh.service

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl reset-failed nasekadan-refresh.service || true
sudo systemctl enable --now nasekadan-refresh.timer
sudo systemctl restart nasekadan-refresh.timer
sudo systemctl start --no-block nasekadan-refresh.service || true

echo "Serverová pojistka je aktivní každých 10 minut a používá jediný kanonický produkční build."
