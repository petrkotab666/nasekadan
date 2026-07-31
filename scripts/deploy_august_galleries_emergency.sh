#!/usr/bin/env bash
set -Eeuo pipefail

ARTICLE_REL='clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html'
ARTICLE_URL='https://nasekadan.cz/clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html'
SLUG='srpen-kadanske-galerie-vystavy-workshop-2026.html'
TITLE_MARKER='Srpen v kadaňských galeriích nabídne houby'
ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

test -f "$ARTICLE_REL"

is_live() {
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

if is_live; then
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

for file in index.html clanky/index.html rss.xml sitemap.xml news-sitemap.xml; do
  test -f "$file"
  grep -Fq "$SLUG" "$file"
done
grep -Fq "$TITLE_MARKER" "$ARTICLE_REL"

SOCIAL_FILE=$(python3 - <<'PY'
import re
from pathlib import Path
text=Path('clanky/srpen-kadanske-galerie-vystavy-workshop-2026.html').read_text(encoding='utf-8')
match=re.search(r'https://nasekadan\.cz/(social/[^"\']+)',text)
if not match:
    raise SystemExit('V článku chybí sociální obrázek')
print(match.group(1))
PY
)
test -f "$SOCIAL_FILE"

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
  rss.xml sitemap.xml news-sitemap.xml "$SOCIAL_FILE" llms.txt llms-full.txt

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
sudo install -m 0644 "$tmp/news-sitemap.xml" /var/www/nasekadan/news-sitemap.xml
sudo install -m 0644 "$tmp/llms.txt" /var/www/nasekadan/llms.txt
sudo install -m 0644 "$tmp/llms-full.txt" /var/www/nasekadan/llms-full.txt
sudo cp -a "$tmp/social/." /var/www/nasekadan/social/
sudo chmod -R a+rX /var/www/nasekadan
sudo nginx -t
sudo systemctl reload nginx
rm -rf "$tmp" /tmp/august-galleries-release.tgz
REMOTE

success=false
for attempt in $(seq 1 36); do
  if is_live; then
    success=true
    break
  fi
  sleep 8
done
test "$success" = true
: > /tmp/august-galleries-deploy-success

# Udržet zdrojový repozitář co nejblíže právě nasazenému webu. Konflikt při
# souběžné redakční práci nesmí zneplatnit již ověřené produkční nasazení.
git config user.name 'Naše Kadaň – nouzové nasazení galerií'
git config user.email 'info@nasekadan.cz'
git add index.html clanky/index.html "$ARTICLE_REL" rss.xml sitemap.xml news-sitemap.xml llms.txt llms-full.txt "$SOCIAL_FILE" 2>/dev/null || true
if ! git diff --cached --quiet; then
  git commit -m 'Zařadit srpnový program galerií do veřejných přehledů'
  git reset --hard HEAD
  git clean -fd
  pushed=false
  for attempt in 1 2 3 4; do
    if git pull --rebase origin main && git push origin HEAD:main; then
      pushed=true
      break
    fi
    git rebase --abort 2>/dev/null || true
    sleep 4
  done
  echo "Uložení sestavených přehledů do main: $pushed"
fi
