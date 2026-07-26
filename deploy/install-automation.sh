#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nasekadan"
WEB_DIR="/var/www/nasekadan"

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "Chybí $APP_DIR/.git – nejdřív nasaďte repozitář." >&2
  exit 1
fi

# Lokální serverová pojistka je nezávislá na dostupnosti GitHub runneru.
# Každých deset minut načte aktuální main, spustí blokující kontrolu článků
# a teprve poté atomicky synchronizuje veřejný document root.
sudo tee /usr/local/sbin/nasekadan-refresh >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nasekadan"
WEB_DIR="/var/www/nasekadan"
REFRESH_LOCK="/run/lock/nasekadan-refresh.lock"
PRODUCTION_LOCK="/tmp/nasekadan-production-deploy.lock"
exec 9>"$REFRESH_LOCK"
flock -n 9 || exit 0
exec 8>"$PRODUCTION_LOCK"
flock -w 900 8

chown -R ubuntu:ubuntu "$APP_DIR"
su - ubuntu -c "git -C '$APP_DIR' fetch --prune origin main"
su - ubuntu -c "git -C '$APP_DIR' reset --hard origin/main"

# Datové přehledy se obnovují nejlepším úsilím. Jejich dočasný výpadek nesmí
# zabránit opravě a zveřejnění již hotových článků.
for script in update_events.py update_sports.py update_city_news.py generate_complete_guides.py ensure_favicon.py; do
  if [[ -f "$APP_DIR/scripts/$script" ]]; then
    timeout 180 su - ubuntu -c "cd '$APP_DIR' && python3 'scripts/$script'" \
      || echo "Upozornění: $script se tentokrát nepodařilo dokončit." >&2
  fi
done

# Tento krok už nepoužívá historickou šablonu. Opraví vazby, sjednotí patičku
# a zastaví publikaci, pokud by kterýkoli veřejný článek chyběl v archivu,
# sitemapě, RSS nebo mezi nejnovějšími články na titulní stránce.
su - ubuntu -c "cd '$APP_DIR' && python3 scripts/finalize_site.py"

STAGE="${WEB_DIR}.refresh-$$"
PREVIOUS="${WEB_DIR}.previous-$$"
rm -rf "$STAGE" "$PREVIOUS"
mkdir -p "$STAGE"
rsync -a --delete \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='.image-parts' \
  --exclude='deploy' \
  --exclude='scripts' \
  --exclude='nginx' \
  --exclude='docker-entrypoint.d' \
  --exclude='Dockerfile' \
  --exclude='docker-compose.yml' \
  "$APP_DIR/" "$STAGE/"

SOURCE_SHA="$(git -C "$APP_DIR" rev-parse HEAD)"
printf 'site=nasekadan.cz\nsource=%s\ngenerated=%s\nmode=server-refresh\n' \
  "$SOURCE_SHA" "$(date -u +%FT%TZ)" > "$STAGE/deployment-health.txt"
chown -R www-data:www-data "$STAGE"
chmod -R a+rX "$STAGE"

if [[ -e "$WEB_DIR" ]]; then mv "$WEB_DIR" "$PREVIOUS"; fi
mv "$STAGE" "$WEB_DIR"
rm -rf "$PREVIOUS"

TRAIN='nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html'
grep -Fq "$TRAIN" "$WEB_DIR/index.html"
grep -Fq "$TRAIN" "$WEB_DIR/clanky/index.html"
grep -Fq "$TRAIN" "$WEB_DIR/sitemap.xml"
grep -Fq "$TRAIN" "$WEB_DIR/rss.xml"
grep -Fq 'data-site-footer="v1"' "$WEB_DIR/index.html"

if command -v nginx >/dev/null 2>&1; then
  nginx -t
  systemctl reload nginx
fi
if systemctl is-active --quiet caddy 2>/dev/null; then
  systemctl reload caddy || true
fi

echo "Naše Kadaň aktualizována na $SOURCE_SHA; články a přehledy ověřeny."
EOF

sudo chmod 755 /usr/local/sbin/nasekadan-refresh

sudo tee /etc/systemd/system/nasekadan-refresh.service >/dev/null <<'EOF'
[Unit]
Description=Bezpečná aktualizace webu Naše Kadaň
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-refresh
User=root
Nice=10
TimeoutStartSec=12min
EOF

sudo tee /etc/systemd/system/nasekadan-refresh.timer >/dev/null <<'EOF'
[Unit]
Description=Pravidelná bezpečná aktualizace Naše Kadaň

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

echo "Serverová pojistka je aktivní každých 10 minut a před zveřejněním kontroluje všechny články."
