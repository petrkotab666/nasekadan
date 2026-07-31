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

# Tyto výpisy jsou diagnostické; samotné sestavovací skripty už článek vložily.
printf 'Výskyt článku v titulce: '; grep -Fc "$SLUG" index.html || true
printf 'Výskyt článku v archivu: '; grep -Fc "$SLUG" clanky/index.html || true
printf 'Výskyt článku v RSS: '; grep -Fc "$SLUG" rss.xml || true
printf 'Výskyt článku v sitemapě: '; grep -Fc "$SLUG" sitemap.xml || true

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

sudo install -d -m 0755 /var/www/nasekadan/clanky /var/www/nasekadan/social
sudo cp -a "$tmp/." /var/www/nasekadan/
sudo chmod -R a+rX /var/www/nasekadan

cid=$(sudo docker ps -q --filter publish=3224 | head -n1)
if [[ -z "$cid" ]]; then
  cid=$(sudo docker ps -q --filter name=nasekadan-web | head -n1)
fi
test -n "$cid"
name=$(sudo docker inspect -f '{{.Name}}' "$cid" | sed 's#^/##')
echo "Aktualizuji produkční kontejner $name ($cid)."

sudo docker exec "$cid" mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social
sudo docker cp "$tmp/index.html" "$cid:/usr/share/nginx/html/index.html"
sudo docker cp "$tmp/clanky/index.html" "$cid:/usr/share/nginx/html/clanky/index.html"
sudo docker cp "$tmp/clanky/$SLUG" "$cid:/usr/share/nginx/html/clanky/$SLUG"
sudo docker cp "$tmp/rss.xml" "$cid:/usr/share/nginx/html/rss.xml"
sudo docker cp "$tmp/sitemap.xml" "$cid:/usr/share/nginx/html/sitemap.xml"
sudo docker cp "$tmp/social/." "$cid:/usr/share/nginx/html/social/"

# Statické soubory se projeví okamžitě; reload je pouze pojistka.
sudo docker exec "$cid" nginx -t
sudo docker exec "$cid" nginx -s reload || true

verify_url() {
  local path="$1" marker="$2" output="$3"
  curl -fsS --max-time 25 "http://127.0.0.1:3224${path}?direct=$(date +%s)$RANDOM" -o "$output"
  if ! grep -Fq "$marker" "$output"; then
    echo "Kontrola selhala pro $path; prvních 40 řádků odpovědi:" >&2
    head -n 40 "$output" >&2 || true
    return 1
  fi
}

verify_url "/clanky/$SLUG" "$TITLE" /tmp/direct-article.html
verify_url '/' "$SLUG" /tmp/direct-home.html
verify_url '/clanky/' "$SLUG" /tmp/direct-archive.html
verify_url '/rss.xml' "$SLUG" /tmp/direct-rss.xml
verify_url '/sitemap.xml' "$SLUG" /tmp/direct-sitemap.xml

echo 'Produkční Docker upstream na portu 3224 potvrzuje článek, titulku, archiv, RSS i sitemapu.'
rm -rf "$tmp" /tmp/august-galleries-release.tgz
REMOTE

: > /tmp/august-galleries-deploy-success

# Veřejná CDN může mít krátkou prodlevu; nasazení je už ověřeno přímo proti
# produkčnímu upstreamu. Následující kontrola je informativní a neblokující.
for attempt in $(seq 1 12); do
  if external_live; then
    echo 'Veřejná doména vrací nový článek i všechny přehledy.'
    break
  fi
  sleep 5
done
