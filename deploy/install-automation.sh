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

# Okamžitá ochrana proti starému paralelnímu deployi. Sleduje hlavní publikační
# plochy; při každé změně porovná nejnovější kanonický článek z origin/main se
# skutečně podávaným document rootem. Pokud někdo nahraje starší snapshot,
# okamžitě spustí jediný kanonický refresh aktuálního main.
sudo tee /usr/local/sbin/nasekadan-regression-check >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nasekadan"
ROOT="/var/www/nasekadan"
CHECK_LOCK="/run/lock/nasekadan-regression-check.lock"

exec 8>"$CHECK_LOCK"
flock -n 8 || exit 0

[[ -d "$APP_DIR/.git" ]] || exit 0
[[ -s "$ROOT/index.html" ]] || exit 0

chown -R ubuntu:ubuntu "$APP_DIR"
su - ubuntu -c "git -C '$APP_DIR' fetch --prune origin main" >/dev/null

expected_href="$(git -C "$APP_DIR" show origin/main:index.html \
  | grep -o 'data-latest-article-href="[^"]*"' \
  | head -n1 \
  | cut -d'"' -f2)"
[[ -n "$expected_href" ]] || exit 1
expected_file="$(basename "$expected_href")"

ok=1
grep -Fq "data-latest-article-href=\"$expected_href\"" "$ROOT/index.html" || ok=0
grep -Fq "$expected_href" "$ROOT/clanky/index.html" || ok=0
grep -Fq "$expected_file" "$ROOT/rss.xml" || ok=0

if [[ "$ok" == 1 ]]; then
  echo "Publikační plochy odpovídají origin/main: $expected_file"
  exit 0
fi

echo "Zachycen starý nebo neúplný snapshot; očekáváno $expected_file. Spouštím kanonickou obnovu." >&2
/usr/local/sbin/nasekadan-refresh
EOF

sudo chmod 755 /usr/local/sbin/nasekadan-regression-check

sudo tee /etc/systemd/system/nasekadan-content-regression.service >/dev/null <<'EOF'
[Unit]
Description=Ochrana Naše Kadaň proti návratu starého publikačního snapshotu
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-regression-check
User=root
TimeoutStartSec=35min
EOF

sudo tee /etc/systemd/system/nasekadan-content-regression.path >/dev/null <<'EOF'
[Unit]
Description=Sledování regresí titulky, archivu a RSS Naše Kadaň

[Path]
PathChanged=/var/www/nasekadan/index.html
PathChanged=/var/www/nasekadan/clanky/index.html
PathChanged=/var/www/nasekadan/rss.xml
Unit=nasekadan-content-regression.service

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl reset-failed nasekadan-refresh.service nasekadan-content-regression.service || true
sudo systemctl enable --now nasekadan-refresh.timer
sudo systemctl restart nasekadan-refresh.timer
sudo systemctl enable --now nasekadan-content-regression.path
sudo systemctl restart nasekadan-content-regression.path

# Jednorázově ověřit právě instalovanou ochranu; pokud je produkce už aktuální,
# skončí bez deploye. Pokud mezitím někdo nahrál starší verzi, sama ji opraví.
sudo /usr/local/sbin/nasekadan-regression-check

echo "Serverová pojistka běží každých 10 minut a navíc okamžitě hlídá změny titulky, archivu a RSS proti origin/main."
