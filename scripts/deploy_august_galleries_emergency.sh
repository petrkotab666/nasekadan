#!/usr/bin/env bash
set -Eeuo pipefail

ARTICLE_REL='clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html'
ARTICLE_URL='https://nasekadan.cz/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html'
SLUG='srpen-kadanske-galerie-vystavy-workshop-2026.html'
TITLE_MARKER='Srpen v kadaňských galeriích nabídne houby'
ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

test -f "$ARTICLE_REL"

external_live() {
  local token="${GITHUB_RUN_ID:-manual}-$(date +%s)-$RANDOM"
  curl -fsS --max-time 20 "$ARTICLE_URL?emergency=$token" -o /tmp/gallery-article.html || true
  curl -fsS --max-time 20 "https://nasekadan.cz/?emergency=$token" -o /tmp/gallery-home.html || true
  curl -fsS --max-time 20 "https://nasekadan.cz/clanky/?emergency=$token" -o /tmp/gallery-archive.html || true
  curl -fsS --max-time 20 "https://nasekadan.cz/rss.xml?emergency=$token" -o /tmp/gallery-rss.xml || true
  curl -fsS --max-time 20 "https://nasekadan.cz/sitemap.xml?emergency=$token" -o /tmp/gallery-sitemap.xml || true
  grep -Fq "$TITLE_MARKER" /tmp/gallery-article.html \
    && grep -Fq "$SLUG" /tmp/gallery-home.html \
    && grep -Fq "$SLUG" /tmp/gallery-archive.html \
    && grep -Fq "$SLUG" /tmp/gallery-rss.xml \
    && grep -Fq "$SLUG" /tmp/gallery-sitemap.xml
}

if external_live; then
  echo 'Článek už je kompletně živý.'
  : > /tmp/august-galleries-deploy-success
  exit 0
fi

python3 -m pip install --quiet Pillow
python3 scripts/normalize_articles.py --write --check
python3 scripts/normalize_footers.py --write --check
python3 scripts/generate_social_cards.py --write --check
python3 scripts/enforce_article_visibility.py
python3 scripts/ensure_all_published_articles_in_rss.py
python3 scripts/sort_articles_chronologically.py
python3 scripts/enforce_latest_homepage_hero.py
python3 scripts/prepare_discovery.py
python3 scripts/clean_sitemap_technical_entries.py

test -f index.html
test -f clanky/index.html
test -f rss.xml
test -f sitemap.xml
test -d social
grep -Fq "$TITLE_MARKER" "$ARTICLE_REL"

umask 077
KEY_FILE="${RUNNER_TEMP:-/tmp}/nasekadan_august_gallery_key"
SELECTED=''
for name in KEY_OVH_SSH_KEY KEY_OVH_SSH_PRIVATE_KEY KEY_SSH_PRIVATE_KEY KEY_VPS_SSH_KEY KEY_VPS_SSH_PRIVATE_KEY KEY_DEPLOY_SSH_KEY KEY_SERVER_SSH_KEY KEY_SSH_KEY; do
  value="${!name:-}"
  if [[ -n "$value" ]]; then
    printf '%s\n' "$value" | tr -d '\r' > "$KEY_FILE"
    SELECTED="$name"
    break
  fi
done
test -n "$SELECTED"
test -s "$KEY_FILE"
chmod 600 "$KEY_FILE"
echo "Použit SSH klíč: $SELECTED"

RELEASE="${RUNNER_TEMP:-/tmp}/august-galleries-release.tgz"
tar -czf "$RELEASE" index.html clanky/index.html "$ARTICLE_REL" rss.xml sitemap.xml social

scp -i "$KEY_FILE" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 \
  "$RELEASE" ubuntu@57.129.43.215:/tmp/august-galleries-release.tgz

ssh -i "$KEY_FILE" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 \
  ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -Eeuo pipefail
SLUG='srpen-kadanske-galerie-vystavy-workshop-2026.html'
TITLE='Srpen v kadaňských galeriích nabídne houby'
tmp=$(mktemp -d)
tar -xzf /tmp/august-galleries-release.tgz -C "$tmp"

# Záložní hostitelská kopie.
sudo install -d -m 0755 /var/www/nasekadan/clanky /var/www/nasekadan/social
sudo install -m 0644 "$tmp/index.html" /var/www/nasekadan/index.html
sudo install -m 0644 "$tmp/clanky/index.html" /var/www/nasekadan/clanky/index.html
sudo install -m 0644 "$tmp/clanky/$SLUG" "/var/www/nasekadan/clanky/$SLUG"
sudo install -m 0644 "$tmp/rss.xml" /var/www/nasekadan/rss.xml
sudo install -m 0644 "$tmp/sitemap.xml" /var/www/nasekadan/sitemap.xml
sudo cp -a "$tmp/social/." /var/www/nasekadan/social/
sudo chmod -R a+rX /var/www/nasekadan

echo 'Běžící kontejnery:'
sudo docker ps --format '  {{.ID}} {{.Names}} {{.Image}} {{.Ports}}' || true

# Najít všechny možné kontejnery Naše Kadaň. Produkční název se může po
# přestavbě změnit, rozhodující je publikovaný port nebo existující webový kořen.
declare -a candidates=()
while IFS= read -r cid; do
  [[ -n "$cid" ]] && candidates+=("$cid")
done < <(sudo docker ps -q --filter publish=3224 2>/dev/null || true)

for cid in $(sudo docker ps -q 2>/dev/null || true); do
  name=$(sudo docker inspect -f '{{.Name}}' "$cid" 2>/dev/null | sed 's#^/##' || true)
  image=$(sudo docker inspect -f '{{.Config.Image}}' "$cid" 2>/dev/null || true)
  if [[ "$name $image" == *nasekadan* ]]; then candidates+=("$cid"); fi
  if sudo docker exec "$cid" sh -c "test -f /usr/share/nginx/html/index.html && grep -qi 'NAŠE.*KADAŇ\|Naše Kadaň' /usr/share/nginx/html/index.html" 2>/dev/null; then
    candidates+=("$cid")
  fi
done

# Odstranit duplicity.
mapfile -t candidates < <(printf '%s\n' "${candidates[@]:-}" | awk 'NF&&!seen[$0]++')
test "${#candidates[@]}" -gt 0

updated=0
for cid in "${candidates[@]}"; do
  name=$(sudo docker inspect -f '{{.Name}}' "$cid" | sed 's#^/##')
  if ! sudo docker exec "$cid" sh -c 'test -d /usr/share/nginx/html'; then
    continue
  fi
  echo "Aktualizuji produkční kontejner: $name ($cid)"
  sudo docker exec "$cid" mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social
  sudo docker cp "$tmp/index.html" "$cid:/usr/share/nginx/html/index.html"
  sudo docker cp "$tmp/clanky/index.html" "$cid:/usr/share/nginx/html/clanky/index.html"
  sudo docker cp "$tmp/clanky/$SLUG" "$cid:/usr/share/nginx/html/clanky/$SLUG"
  sudo docker cp "$tmp/rss.xml" "$cid:/usr/share/nginx/html/rss.xml"
  sudo docker cp "$tmp/sitemap.xml" "$cid:/usr/share/nginx/html/sitemap.xml"
  sudo docker cp "$tmp/social/." "$cid:/usr/share/nginx/html/social/"
  sudo docker exec "$cid" sh -c "grep -Fq '$TITLE' '/usr/share/nginx/html/clanky/$SLUG'"
  sudo docker exec "$cid" sh -c "grep -Fq '$SLUG' /usr/share/nginx/html/index.html"
  sudo docker exec "$cid" sh -c "grep -Fq '$SLUG' /usr/share/nginx/html/clanky/index.html"
  sudo docker exec "$cid" sh -c "grep -Fq '$SLUG' /usr/share/nginx/html/rss.xml"
  sudo docker exec "$cid" sh -c "grep -Fq '$SLUG' /usr/share/nginx/html/sitemap.xml"
  sudo docker exec "$cid" nginx -t
  sudo docker exec "$cid" nginx -s reload || sudo docker restart "$cid"
  updated=$((updated+1))
done
test "$updated" -gt 0

# Přímá kontrola upstreamu používaného hostitelským Nginxem.
for port in 3224 80; do
  if curl -fsS --max-time 20 "http://127.0.0.1:${port}/clanky/$SLUG?local=$(date +%s)" -o /tmp/local-article.html 2>/dev/null \
    && grep -Fq "$TITLE" /tmp/local-article.html; then
    curl -fsS --max-time 20 "http://127.0.0.1:${port}/?local=$(date +%s)" | grep -Fq "$SLUG"
    curl -fsS --max-time 20 "http://127.0.0.1:${port}/clanky/?local=$(date +%s)" | grep -Fq "$SLUG"
    curl -fsS --max-time 20 "http://127.0.0.1:${port}/rss.xml?local=$(date +%s)" | grep -Fq "$SLUG"
    curl -fsS --max-time 20 "http://127.0.0.1:${port}/sitemap.xml?local=$(date +%s)" | grep -Fq "$SLUG"
    echo "Interní produkční upstream na portu $port je aktualizovaný."
    rm -rf "$tmp" /tmp/august-galleries-release.tgz
    exit 0
  fi
done

echo 'Soubory jsou v produkčním kontejneru, ale interní HTTP upstream je nenalezl.' >&2
exit 1
REMOTE

: > /tmp/august-galleries-deploy-success
echo 'Produkční kontejner i interní upstream potvrzují článek a všechny přehledy.'

for attempt in $(seq 1 12); do
  if external_live; then
    echo 'Veřejná doména vrací nový článek i všechny přehledy.'
    break
  fi
  sleep 5
done
