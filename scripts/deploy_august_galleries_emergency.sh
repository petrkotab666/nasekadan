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

echo 'Veřejné soubory jsou sestavené. Pokračuje přímý přenos na OVH.'

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
tar -czf "$RELEASE" \
  index.html clanky/index.html "$ARTICLE_REL" \
  rss.xml sitemap.xml social

scp -i "$KEY_FILE" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 \
  "$RELEASE" ubuntu@57.129.43.215:/tmp/august-galleries-release.tgz

ssh -i "$KEY_FILE" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 \
  ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -Eeuo pipefail
tmp=$(mktemp -d)
tar -xzf /tmp/august-galleries-release.tgz -C "$tmp"

sudo install -d -m 0755 /var/www/nasekadan/clanky /var/www/nasekadan/social
sudo install -m 0644 "$tmp/index.html" /var/www/nasekadan/index.html
sudo install -m 0644 "$tmp/clanky/index.html" /var/www/nasekadan/clanky/index.html
sudo install -m 0644 "$tmp/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html" /var/www/nasekadan/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html
sudo install -m 0644 "$tmp/rss.xml" /var/www/nasekadan/rss.xml
sudo install -m 0644 "$tmp/sitemap.xml" /var/www/nasekadan/sitemap.xml
sudo cp -a "$tmp/social/." /var/www/nasekadan/social/
sudo chmod -R a+rX /var/www/nasekadan

if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social
  sudo docker cp "$tmp/index.html" nasekadan-web:/usr/share/nginx/html/index.html
  sudo docker cp "$tmp/clanky/index.html" nasekadan-web:/usr/share/nginx/html/clanky/index.html
  sudo docker cp "$tmp/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html" nasekadan-web:/usr/share/nginx/html/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html
  sudo docker cp "$tmp/rss.xml" nasekadan-web:/usr/share/nginx/html/rss.xml
  sudo docker cp "$tmp/sitemap.xml" nasekadan-web:/usr/share/nginx/html/sitemap.xml
  sudo docker cp "$tmp/social/." nasekadan-web:/usr/share/nginx/html/social/
fi

sudo nginx -t
sudo systemctl reload nginx

# Ověření přímo proti lokálnímu produkčnímu virtuálnímu hostu, bez CDN.
check_local() {
  local path="$1" marker="$2"
  curl -kfsS --max-time 25 --resolve nasekadan.cz:443:127.0.0.1 "https://nasekadan.cz${path}?local=$(date +%s)$RANDOM" | grep -Fq "$marker"
}
check_local '/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html' 'Srpen v kadaňských galeriích nabídne houby'
check_local '/' 'srpen-kadanske-galerie-vystavy-workshop-2026.html'
check_local '/clanky/' 'srpen-kadanske-galerie-vystavy-workshop-2026.html'
check_local '/rss.xml' 'srpen-kadanske-galerie-vystavy-workshop-2026.html'
check_local '/sitemap.xml' 'srpen-kadanske-galerie-vystavy-workshop-2026.html'

rm -rf "$tmp" /tmp/august-galleries-release.tgz
REMOTE

: > /tmp/august-galleries-deploy-success

echo 'Serverová produkce článek, titulku, archiv, RSS a sitemapu potvrzuje.'

# Veřejná CDN kontrola je doplňková; výpadek spojení z GitHub runneru nesmí
# označit už lokálně ověřené produkční nasazení za neúspěšné.
for attempt in $(seq 1 12); do
  if external_live; then
    echo 'Veřejná doména už vrací nový článek i všechny přehledy.'
    break
  fi
  sleep 5
done
