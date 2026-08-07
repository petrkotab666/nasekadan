#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nasekadan"
ROOT="/var/www/nasekadan"
PRODUCTION_LOCK="/tmp/nasekadan-production-deploy.lock"

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "Chybí $APP_DIR/.git – nejdřív nasaďte repozitář." >&2
  exit 1
fi

# Všechny serverové zásahy používají STEJNÝ zámek jako deploy/sync-production.sh.
# Tím se nemůže kanonický deploy, oprava článku a automatická obnova překrýt a
# navzájem si přepisovat git checkout nebo document root.
sudo touch "$PRODUCTION_LOCK"
sudo chmod a+rw "$PRODUCTION_LOCK"

sudo tee /usr/local/sbin/nasekadan-static-restore >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/nasekadan"
ROOT="/var/www/nasekadan"
LOCK_FILE="/tmp/nasekadan-production-deploy.lock"

exec 9>"$LOCK_FILE"
flock -w 300 9

[[ -d "$APP_DIR/.git" ]] || { echo "Chybí $APP_DIR/.git" >&2; exit 1; }
chown -R ubuntu:ubuntu "$APP_DIR"
# index.lock se smí odstranit až po získání společného produkčního zámku.
rm -f "$APP_DIR/.git/index.lock"
su - ubuntu -c "git -C '$APP_DIR' fetch --prune origin main"
su - ubuntu -c "git -C '$APP_DIR' reset --hard origin/main"
su - ubuntu -c "git -C '$APP_DIR' clean -fd"
cd "$APP_DIR"
SOURCE_SHA="$(git rev-parse HEAD)"

# Přehledy se vždy staví ze skutečných článkových souborů, nikoli ze staré titulky.
python3 scripts/enforce_all_article_visibility.py
python3 scripts/ensure_all_published_articles_in_rss.py
python3 scripts/sort_articles_chronologically.py
python3 scripts/enforce_latest_homepage_hero.py

# Facebook/OG karta je povinná pro každý článek. Pokud je na serveru Pillow,
# vzniknou zároveň lokální jedinečné 1200x630 karty. Bez Pillow se obsahová obnova
# nezastaví; kanonický Docker build má tuto kontrolu povinnou vždy.
if python3 -c 'import PIL' >/dev/null 2>&1; then
  python3 scripts/generate_social_cards.py --write --check
fi

# Finalizace už audituje pouze skutečné vstupní články; zde obnovujeme povrchy.
NASEKADAN_AUDIT_PATHS='' python3 scripts/finalize_launch.py
python3 scripts/verify_published_article_set.py \
  --source "$APP_DIR" --target "$APP_DIR" \
  --write-manifest "$APP_DIR/published-articles-manifest.json"

install -d -m 0755 "$ROOT" "$ROOT/clanky"
# Nikdy nemažeme starší článek jen proto, že jej některý historický deploy nezná.
# Přepisujeme/obnovujeme všechny kanonické články z aktuálního main.
for f in clanky/*.html; do
  [[ -f "$f" ]] && install -m 0644 "$f" "$ROOT/clanky/$(basename "$f")"
done
for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt published-articles-manifest.json; do
  [[ -f "$f" ]] && install -m 0644 "$f" "$ROOT/$f"
done
for f in ./*.css ./*.js ./*.svg ./*.png ./*.webp ./*.ico; do
  [[ -f "$f" ]] && install -m 0644 "$f" "$ROOT/$(basename "$f")"
done
for dir in social images; do
  if [[ -d "$dir" ]]; then
    mkdir -p "$ROOT/$dir"
    cp -a "$dir"/. "$ROOT/$dir"/
  fi
done

cat > "$ROOT/deployment-health.txt" <<HEALTH
site=nasekadan.cz
status=ok
source=$SOURCE_SHA
generated=$(date -u +%FT%TZ)
mode=monotonic-static-restore
HEALTH
chmod 0644 "$ROOT/deployment-health.txt"

# Blokující kontrola: document root musí obsahovat úplnou množinu článků z main.
python3 scripts/verify_published_article_set.py --source "$APP_DIR" --target "$ROOT"

# Pokud některý interní nginx kontejner stále drží vlastní statickou kopii, dostane
# stejný úplný obsah. Veřejný document root zůstává zdrojem pravdy.
if docker inspect nasekadan-web >/dev/null 2>&1; then
  docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social /usr/share/nginx/html/images || true
  docker cp clanky/. nasekadan-web:/usr/share/nginx/html/clanky/ || true
  [[ -d social ]] && docker cp social/. nasekadan-web:/usr/share/nginx/html/social/ || true
  [[ -d images ]] && docker cp images/. nasekadan-web:/usr/share/nginx/html/images/ || true
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt published-articles-manifest.json deployment-health.txt; do
    [[ -f "$ROOT/$f" ]] && docker cp "$ROOT/$f" "nasekadan-web:/usr/share/nginx/html/$f" || true
  done
fi

echo "Monotónní obnova hotova: main @ $SOURCE_SHA; žádný kanonický článek nechybí."
EOF
sudo chmod 755 /usr/local/sbin/nasekadan-static-restore

# Kontrola neporovnává pouze nejnovější kartu. Očekávanou množinu bere přímo z
# clanky/*.html v origin/main. Jakmile chybí jediný již publikovaný soubor nebo
# jeho stopa v archivu/RSS/sitemapě, spustí úplnou statickou obnovu z aktuálního main.
sudo tee /usr/local/sbin/nasekadan-regression-check >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/nasekadan"
ROOT="/var/www/nasekadan"
CHECK_LOCK="/run/lock/nasekadan-regression-check.lock"

exec 8>"$CHECK_LOCK"
flock -n 8 || exit 0
[[ -d "$APP_DIR/.git" ]] || exit 0

chown -R ubuntu:ubuntu "$APP_DIR"
su - ubuntu -c "git -C '$APP_DIR' fetch --prune origin main" >/dev/null

mapfile -t expected < <(
  git -C "$APP_DIR" ls-tree -r --name-only origin/main -- clanky \
    | grep -E '^clanky/[^/]+\.html$' \
    | grep -Ev '^clanky/(index|strana-[0-9]+)\.html$' \
    | sort -u
)
[[ ${#expected[@]} -gt 0 ]] || { echo "Kanonický main neobsahuje články." >&2; exit 1; }

archive=''
for f in "$ROOT"/clanky/index.html "$ROOT"/clanky/strana-*.html; do
  [[ -f "$f" ]] && archive+="$(cat "$f")"$'\n'
done
rss="$(cat "$ROOT/rss.xml" 2>/dev/null || true)"
sitemap="$(cat "$ROOT/sitemap.xml" 2>/dev/null || true)"

missing=0
for rel in "${expected[@]}"; do
  name="$(basename "$rel")"
  [[ -s "$ROOT/$rel" ]] || { echo "CHYBÍ soubor $rel" >&2; missing=1; }
  grep -Fq "$name" <<<"$archive" || { echo "CHYBÍ v archivu $rel" >&2; missing=1; }
  grep -Fq "$name" <<<"$rss" || { echo "CHYBÍ v RSS $rel" >&2; missing=1; }
  grep -Fq "$name" <<<"$sitemap" || { echo "CHYBÍ v sitemapě $rel" >&2; missing=1; }
done

if [[ "$missing" == 0 ]]; then
  echo "Monotónní kontrola OK: ${#expected[@]} článků z origin/main je veřejně zachováno."
  exit 0
fi

echo "Zachycena publikační regrese. Obnovuji všechny články z aktuálního origin/main." >&2
/usr/local/sbin/nasekadan-static-restore
EOF
sudo chmod 755 /usr/local/sbin/nasekadan-regression-check

# Pravidelná obnova je rychlá a bez Docker buildu. Docker se nadále nasazuje jen
# kanonickým produkčním deployem; ochrana článků na něm není závislá.
sudo tee /usr/local/sbin/nasekadan-refresh >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
/usr/local/sbin/nasekadan-static-restore
EOF
sudo chmod 755 /usr/local/sbin/nasekadan-refresh

sudo tee /etc/systemd/system/nasekadan-refresh.service >/dev/null <<'EOF'
[Unit]
Description=Monotónní obnova publikovaného obsahu Naše Kadaň
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-refresh
User=root
TimeoutStartSec=10min
EOF

sudo tee /etc/systemd/system/nasekadan-refresh.timer >/dev/null <<'EOF'
[Unit]
Description=Pravidelná pojistka úplnosti článků Naše Kadaň
[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
RandomizedDelaySec=15
Persistent=true
Unit=nasekadan-refresh.service
[Install]
WantedBy=timers.target
EOF

sudo tee /etc/systemd/system/nasekadan-content-regression.service >/dev/null <<'EOF'
[Unit]
Description=Okamžitá ochrana Naše Kadaň proti zmizení publikovaných článků
After=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-regression-check
User=root
TimeoutStartSec=10min
EOF

sudo tee /etc/systemd/system/nasekadan-content-regression.path >/dev/null <<'EOF'
[Unit]
Description=Sledování všech publikačních ploch Naše Kadaň
[Path]
PathChanged=/var/www/nasekadan/index.html
PathChanged=/var/www/nasekadan/clanky
PathChanged=/var/www/nasekadan/clanky/index.html
PathChanged=/var/www/nasekadan/rss.xml
PathChanged=/var/www/nasekadan/sitemap.xml
PathChanged=/var/www/nasekadan/news-sitemap.xml
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

# Instalace zároveň okamžitě opraví případný současný rollback.
sudo /usr/local/sbin/nasekadan-static-restore
sudo /usr/local/sbin/nasekadan-regression-check

echo "Monotónní ochrana aktivní: všechny články z origin/main jsou hlídány okamžitě i periodicky."
