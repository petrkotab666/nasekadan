#!/usr/bin/env bash
set -euo pipefail

ROOT="${GITHUB_WORKSPACE:-$(pwd)}"
cd "$ROOT"

LOCK_FILE=/tmp/nasekadan-production-deploy.lock
# Zámek sdílí ruční nasazení, self-hosted runner i rootovská serverová pojistka.
# Soubor mohl dříve vytvořit root s režimem 0644, takže běžný uživatel jej
# nedokázal otevřít. Oprávnění upravujeme bez mazání souboru, aby se zachovalo
# korektní flock chování i při souběžném běhu.
if command -v sudo >/dev/null 2>&1; then
  sudo touch "$LOCK_FILE"
  sudo chmod a+rw "$LOCK_FILE"
else
  touch "$LOCK_FILE"
  chmod a+rw "$LOCK_FILE"
fi
exec 9>"$LOCK_FILE"
flock -w 900 9

# Vždy nasazovat skutečně nejnovější hlavní větev, i když byl workflow spuštěn
# starším commitem nebo čekal delší dobu ve frontě.
git fetch --prune origin main
git reset --hard origin/main
SOURCE_SHA="$(git rev-parse HEAD)"
SHORT_SHA="${SOURCE_SHA:0:12}"

echo "Nasazuji main @ $SOURCE_SHA"

python3 scripts/ensure_publication_integrity.py
python3 scripts/ensure_newest_article_indexes.py
python3 scripts/ensure_petition_document_details.py
python3 scripts/normalize_footers.py --write --check
python3 scripts/validate_publication_integrity.py

cat > deployment-health.txt <<EOF
site=nasekadan.cz
source=$SOURCE_SHA
generated=$(date -u +%FT%TZ)
mode=canonical-ovh
EOF

# Docker Buildx si standardně ukládá zámky do ~/.docker. Tento adresář mohl
# dříve vytvořit root a ruční nasazení uživatele ubuntu pak končilo chybou
# "permission denied". Každý uživatel proto používá samostatný zapisovatelný
# dočasný konfigurační adresář. Přístup k Docker socketu tím není ovlivněn.
DOCKER_CONFIG="/tmp/nasekadan-docker-config-$(id -u)"
export DOCKER_CONFIG
mkdir -p "$DOCKER_CONFIG/buildx"
chmod -R u+rwX "$DOCKER_CONFIG"
rm -f "$DOCKER_CONFIG/buildx/lock"

IMAGE="nasekadan-web:$SOURCE_SHA"
docker build --pull -t "$IMAGE" .
docker rm -f nasekadan-web 2>/dev/null || true
docker run -d \
  --name nasekadan-web \
  --restart unless-stopped \
  -p 127.0.0.1:3224:80 \
  "$IMAGE" >/dev/null

for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:3224/healthz >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS http://127.0.0.1:3224/healthz >/dev/null

TRAIN='nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html'
WEEKLY='kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html'
EPETICE='epetice-nemocnice-kadan.html'
PETICE='petice-nemocnice-kadan.html'
POOL='pozemky-koupaliste-kadan.html'
PETITION_DETAILS='Petice obsahuje osm požadavků. Rozpracovaná ePetice narazila na limit'

verify_endpoint() {
  local base="$1"
  local prefix="$2"
  local tmp
  tmp="$(mktemp)"

  curl -kfsS --max-time 25 "${base}/?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq "$TRAIN" "$tmp"
  grep -Fq "$WEEKLY" "$tmp"
  grep -Fq "$EPETICE" "$tmp"
  grep -Fq 'data-site-footer="v1"' "$tmp"

  curl -kfsS --max-time 25 "${base}/clanky/?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq "$TRAIN" "$tmp"
  grep -Fq "$WEEKLY" "$tmp"
  grep -Fq "$EPETICE" "$tmp"
  grep -Fq "$POOL" "$tmp"

  curl -kfsS --max-time 25 "${base}/clanky/${TRAIN}?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq 'Noční výluky vlaků zasáhnou Kadaň, Klášterec i Chomutov' "$tmp"

  curl -kfsS --max-time 25 "${base}/clanky/${PETICE}?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq "$PETITION_DETAILS" "$tmp"
  grep -Fq 'Přijetí personálních změn' "$tmp"
  grep -Fq 'Osobní údaje na web nevkládáme' "$tmp"

  curl -kfsS --max-time 25 "${base}/sitemap.xml?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq "$TRAIN" "$tmp"
  grep -Fq "$WEEKLY" "$tmp"
  grep -Fq "$EPETICE" "$tmp"
  grep -Fq "$POOL" "$tmp"

  curl -kfsS --max-time 25 "${base}/rss.xml?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq "$TRAIN" "$tmp"
  grep -Fq "$WEEKLY" "$tmp"
  grep -Fq "$EPETICE" "$tmp"
  grep -Fq "$POOL" "$tmp"

  curl -kfsS --max-time 25 "${base}/deployment-health.txt?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq "source=$SOURCE_SHA" "$tmp"

  rm -f "$tmp"
  echo "Ověřeno: $prefix"
}

# Přesný výstup produkčního kontejneru se použije i pro případný aktivní
# Caddy document root. Nginx proxy i Caddy tak vždy podávají stejnou verzi.
STAGE="/var/www/nasekadan.release-$SOURCE_SHA"
PREVIOUS="/var/www/nasekadan.previous-$SOURCE_SHA"
BUILT="/tmp/nasekadan-built-$SHORT_SHA"
sudo rm -rf "$STAGE" "$PREVIOUS" "$BUILT"
sudo mkdir -p "$STAGE"
docker cp nasekadan-web:/usr/share/nginx/html/. "$BUILT"
sudo cp -a "$BUILT"/. "$STAGE"/
sudo rm -rf "$BUILT"
printf 'site=nasekadan.cz\nsource=%s\ngenerated=%s\nmode=canonical-ovh\n' \
  "$SOURCE_SHA" "$(date -u +%FT%TZ)" | sudo tee "$STAGE/deployment-health.txt" >/dev/null
sudo chmod -R a+rX "$STAGE"

if [ -e /var/www/nasekadan ]; then
  sudo mv /var/www/nasekadan "$PREVIOUS"
fi
sudo mv "$STAGE" /var/www/nasekadan
sudo rm -rf "$PREVIOUS"

# Lokální kontejner je vždy povinný.
verify_endpoint 'http://127.0.0.1:3224' 'produkční kontejner'

# Ověření skutečného HTTPS frontendu na serveru. Funguje pro Caddy i Nginx.
PUBLIC_BASE=''
if curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  "https://nasekadan.cz/deployment-health.txt?deploy=$SOURCE_SHA" \
  | grep -Fq "source=$SOURCE_SHA"; then
  PUBLIC_BASE='https://nasekadan.cz'
  curl_resolve=(--resolve nasekadan.cz:443:127.0.0.1)
elif curl -fsS --max-time 10 --resolve nasekadan.cz:80:127.0.0.1 \
  "http://nasekadan.cz/deployment-health.txt?deploy=$SOURCE_SHA" \
  | grep -Fq "source=$SOURCE_SHA"; then
  PUBLIC_BASE='http://nasekadan.cz'
  curl_resolve=(--resolve nasekadan.cz:80:127.0.0.1)
else
  echo 'Veřejný frontend nepodává právě nasazenou verzi.' >&2
  exit 1
fi

verify_public() {
  local path="$1" needle="$2"
  local tmp
  tmp="$(mktemp)"
  curl -kfsS --max-time 25 "${curl_resolve[@]}" \
    "${PUBLIC_BASE}${path}?deploy=${SOURCE_SHA}" -o "$tmp"
  grep -Fq "$needle" "$tmp"
  rm -f "$tmp"
}

verify_public '/' "$WEEKLY"
verify_public '/' "$TRAIN"
verify_public '/' "$EPETICE"
verify_public '/clanky/' "$TRAIN"
verify_public '/clanky/' "$EPETICE"
verify_public '/clanky/' "$POOL"
verify_public "/clanky/$TRAIN" 'Noční výluky vlaků zasáhnou Kadaň, Klášterec i Chomutov'
verify_public "/clanky/$PETICE" "$PETITION_DETAILS"
verify_public "/clanky/$PETICE" 'Přijetí personálních změn'
verify_public "/clanky/$PETICE" 'Osobní údaje na web nevkládáme'
verify_public '/sitemap.xml' "$TRAIN"
verify_public '/sitemap.xml' "$EPETICE"
verify_public '/sitemap.xml' "$POOL"
verify_public '/rss.xml' "$TRAIN"
verify_public '/rss.xml' "$EPETICE"
verify_public '/rss.xml' "$POOL"
verify_public '/deployment-health.txt' "source=$SOURCE_SHA"

# Po úspěšném ověření obnovit i lokální desetiminutovou pojistku. Ta zajistí,
# že se server sám srovná na aktuální main i při dočasně nedostupném runneru.
if [[ -d /opt/nasekadan/.git ]]; then
  sudo bash deploy/install-automation.sh
else
  echo 'Upozornění: /opt/nasekadan není git checkout; lokální timer nebyl přeinstalován.' >&2
fi

echo "HOTOVO: veřejný web podává main @ $SOURCE_SHA, hlavní článek obsahuje osm požadavků a všechny přehledy jsou kompletní."
