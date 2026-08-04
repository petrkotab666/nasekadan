#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BLOOD_REL='/clanky/nemocnice-kadan-kriticky-nedostatek-krve-0-rh-minus-2026.html'
STEM_REL='/clanky/zaregistrovala-se-v-kadani-darovala-krvetvorne-bunky-2026.html'
BASE='https://nasekadan.cz'

key="${OVH_KEY_A:-${OVH_KEY_B:-}}"
test -n "$key"
printf '%s\n' "$key" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
chmod 600 "$RUNNER_TEMP/ovh_key"

git config user.name 'Naše Kadaň – trvalá pojistka článků'
git config user.email 'info@nasekadan.cz'

pushed=0
for attempt in 1 2 3 4 5; do
  git fetch origin main
  git reset --hard origin/main

  # Pořadí je vždy čistě chronologické podle article:published_time.
  # Aktualizace staršího článku jej dopředu neposune.

  # Odstraň pouze známé jednorázové nástroje, které přepisovaly novější
  # články starším stadionem. Běžné publikační workflow zůstávají nedotčené.
  for file in \
    .github/workflows/repin-stadium-home-20260804.yml \
    .github/workflows/restore-stadium-homepage-pin-20260804-1758.yml \
    .github/workflows/force-stadium-pin-until-20260805.yml \
    scripts/pin_stadium_homepage_20260804.py \
    scripts/apply_stadium_homepage_pin.py; do
    if [[ -e "$file" ]]; then
      git rm -f -- "$file"
    fi
  done

  python3 -m py_compile \
    scripts/enforce_article_visibility.py \
    scripts/enforce_all_article_visibility.py \
    scripts/audit_canonical_content_runtime.py
  python3 scripts/enforce_all_article_visibility.py
  git diff --check

  git add scripts/enforce_article_visibility.py index.html clanky/index.html sitemap.xml
  find clanky -maxdepth 1 -type f -name 'strana-*.html' -print0 | xargs -0 -r git add --
  if ! git diff --cached --quiet; then
    git commit -m 'Automaticky obnovit úplnou viditelnost článků'
  fi
  if git push origin HEAD:main; then
    pushed=1
    break
  fi
  sleep $((attempt * 4))
done
test "$pushed" = 1

git fetch origin main
git reset --hard origin/main
source_sha="$(git rev-parse HEAD)"
read -r article_count latest_rel < <(python3 - <<'PY'
from datetime import datetime, timedelta, timezone
from pathlib import Path
import importlib.util, re
spec = importlib.util.spec_from_file_location('visibility', Path('scripts/enforce_article_visibility.py'))
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
cutoff = datetime.now(timezone.utc) + timedelta(minutes=2)
items = []
for path in Path('clanky').glob('*.html'):
    if path.name == 'index.html' or re.fullmatch(r'strana-\d+\.html', path.name):
        continue
    item = module.article_info(path)
    if not item:
        continue
    dt = item['dt']
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if dt.astimezone(timezone.utc) <= cutoff:
        items.append(item)
items.sort(key=lambda x: x['dt'], reverse=True)
if not items:
    raise SystemExit('Nenalezen žádný publikovaný článek.')
print(len(items), items[0]['href'])
PY
)

bundle="$RUNNER_TEMP/nk-article-integrity-${GITHUB_RUN_ID}"
rm -rf "$bundle"
mkdir -p "$bundle/clanky" "$bundle/data"
cp index.html rss.xml sitemap.xml news-sitemap.xml llms.txt "$bundle/"
cp clanky/*.html "$bundle/clanky/"
cp data/published-content-index.json "$bundle/data/"
cat > "$bundle/deployment-health.txt" <<EOF
status=ok
source=${source_sha}
article_count=${article_count}
latest=${latest_rel}
guard=canonical-all-articles-v3
deployed_at=$(date -u +%FT%TZ)
EOF

tar -C "$bundle" -czf "$RUNNER_TEMP/nk-article-integrity.tgz" .
remote="/tmp/nk-article-integrity-${GITHUB_RUN_ID}"
scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 \
  "$RUNNER_TEMP/nk-article-integrity.tgz" "ubuntu@57.129.43.215:${remote}.tgz"
ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 \
  ubuntu@57.129.43.215 "RUN_ID='${GITHUB_RUN_ID}' bash -s" <<'REMOTE'
set -euo pipefail
src="/tmp/nk-article-integrity-${RUN_ID}"
rm -rf "$src"
mkdir -p "$src"
tar -xzf "${src}.tgz" -C "$src"
sudo install -m 0666 /dev/null /var/lock/nasekadan-content.lock
exec 9>/var/lock/nasekadan-content.lock
flock -x 9
root=/var/www/nasekadan
sudo install -d -m 0755 "$root/clanky" "$root/data"
for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do
  sudo install -m 0644 "$src/$f" "$root/$f"
done
for f in "$src"/clanky/*.html; do
  sudo install -m 0644 "$f" "$root/clanky/$(basename "$f")"
done
sudo install -m 0644 "$src/data/published-content-index.json" "$root/data/published-content-index.json"
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/data
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do
    sudo docker cp "$src/$f" "nasekadan-web:/usr/share/nginx/html/$f"
  done
  sudo docker cp "$src/clanky/." nasekadan-web:/usr/share/nginx/html/clanky/
  sudo docker cp "$src/data/published-content-index.json" nasekadan-web:/usr/share/nginx/html/data/published-content-index.json
fi
rm -rf "$src" "${src}.tgz"
REMOTE

# Pokud main mezitím posunula jiná legitimní publikace, nevytvářej falešný
# incident. Její push okamžitě spustí nejnovější běh téže pojistky.
current_main="$(git ls-remote origin refs/heads/main | awk '{print $1}')"
if [[ "$current_main" != "$source_sha" ]]; then
  echo "Main se posunul z $source_sha na $current_main; kontrolu převezme novější běh."
  exit 0
fi

success=0
for attempt in $(seq 1 12); do
  current_main="$(git ls-remote origin refs/heads/main | awk '{print $1}')"
  if [[ "$current_main" != "$source_sha" ]]; then
    echo "Main se během veřejného ověření posunul; novější běh pokračuje."
    exit 0
  fi
  q="${GITHUB_RUN_ID}-$(date +%s)-${attempt}"
  home="$(curl -4 -kfsSL --max-time 40 "$BASE/?integrity=$q" || true)"
  archive="$(curl -4 -kfsSL --max-time 40 "$BASE/clanky/?integrity=$q" || true)"
  rss="$(curl -4 -kfsSL --max-time 40 "$BASE/rss.xml?integrity=$q" || true)"
  sitemap="$(curl -4 -kfsSL --max-time 40 "$BASE/sitemap.xml?integrity=$q" || true)"
  health="$(curl -4 -kfsSL --max-time 40 "$BASE/deployment-health.txt?integrity=$q" || true)"
  blood="$(curl -4 -kfsSL --max-time 40 "$BASE$BLOOD_REL?integrity=$q" || true)"
  stem="$(curl -4 -kfsSL --max-time 40 "$BASE$STEM_REL?integrity=$q" || true)"

  if grep -Fq "source=$source_sha" <<<"$health" \
    && grep -Fq "$latest_rel" <<<"$home" \
    && grep -Fq "$BLOOD_REL" <<<"$archive" \
    && grep -Fq "${BASE}${BLOOD_REL}" <<<"$rss" \
    && grep -Fq "${BASE}${BLOOD_REL}" <<<"$sitemap" \
    && grep -Fq 'Kriticky chybí krev skupiny 0 Rh−' <<<"$blood" \
    && grep -Fq "$STEM_REL" <<<"$archive" \
    && grep -Fq "${BASE}${STEM_REL}" <<<"$rss" \
    && grep -Fq "${BASE}${STEM_REL}" <<<"$sitemap" \
    && grep -Fq 'darovala krvetvorné buňky' <<<"$stem"; then
    if python3 scripts/audit_canonical_content_runtime.py; then
      success=1
      break
    fi
  fi
  sleep 10
done

if [[ "$success" != 1 ]]; then
  echo "Veřejná kontrola po 12 pokusech neprošla." >&2
  exit 1
fi

if [[ -n "${GH_TOKEN:-}" ]]; then
  issue="$(gh issue list --state open --search '[incident] Viditelnost článků Naše Kadaň in:title' --json number --jq '.[0].number // empty')"
  if [[ -n "$issue" ]]; then
    gh issue comment "$issue" --body "Úplná kanonická kontrola prošla. Ověřeno ${article_count} článků, celý archiv, RSS, sitemap, news-sitemap, registr, oba články o dárcovství a deployment-health. Run ${GITHUB_RUN_ID}."
    gh issue close "$issue" --reason completed
  fi
fi

echo "Pojistka prošla: ${article_count} článků, nejnovější ${latest_rel}, zdroj ${source_sha}."
