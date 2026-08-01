#!/usr/bin/env bash
set -euo pipefail

SLUG='sekani-travniku-kadan-spravci-vysky-2026'
ARTICLE="clanky/${SLUG}.html"
PUBLIC_URL="https://nasekadan.cz/${ARTICLE}"
POLL_ID='sekani-travniku-kadan-2026'
POLL_VERSION='20260801-poll-system-v2'
EXPECTED_TEXT='Sedm centimetrů je smluvní minimum jedné konkrétní lokality'

python3 -m pip install --disable-pip-version-check --quiet Pillow
python3 scripts/install_poll_system_v2.py
python3 scripts/prepare_greenery_publication_20260801.py
python3 scripts/test_poll_system_v2.py

test -s .github/greenery-publication-bundle.json
readarray -t BUNDLE < <(python3 - <<'PY'
import json
from pathlib import Path
p=json.loads(Path('.github/greenery-publication-bundle.json').read_text(encoding='utf-8'))
print(p['socialFile'])
print(p['socialUrl'])
PY
)
SOCIAL_FILE="${BUNDLE[0]}"
SOCIAL_URL="${BUNDLE[1]}"

test -s "$ARTICLE"
test -s "$SOCIAL_FILE"
grep -Fq "$EXPECTED_TEXT" "$ARTICLE"
grep -Fq "data-poll-id=\"${POLL_ID}\"" "$ARTICLE"
grep -Fq "/site.js?v=${POLL_VERSION}" "$ARTICLE"
! grep -Fq '/api/analytics/pageview' "$ARTICLE"
grep -Fq 'index,follow' "$ARTICLE"
! grep -Fq 'noindex,nofollow' "$ARTICLE"
for file in index.html clanky/index.html rss.xml sitemap.xml news-sitemap.xml; do
  grep -Fq "$PUBLIC_URL" "$file" || grep -Fq "/clanky/${SLUG}.html" "$file"
done

# Uložit pouze veřejné výstupy článku. Normalizační pipeline může změnit další
# pracovní soubory; po commitu je bezpečně zahodíme, aby rebase nebyl blokován.
git config user.name 'Naše Kadaň publikační oprava'
git config user.email 'info@nasekadan.cz'
git add -A -- \
  newsletter/server.py site.js "$ARTICLE" "$SOCIAL_FILE" \
  index.html clanky/index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt \
  .github/facebook-publish-trigger.txt .github/greenery-publication-bundle.json \
  scripts/install_poll_system_v2.py scripts/prepare_greenery_publication_20260801.py
if ! git diff --cached --quiet; then
  git commit -m 'Publikovat: sečení trávníků s ověřenou databázovou anketou'
fi
git reset --hard HEAD
git clean -fd
for attempt in 1 2 3 4 5; do
  if git pull --rebase origin main && git push origin HEAD:main; then
    break
  fi
  git rebase --abort 2>/dev/null || true
  [[ "$attempt" == 5 ]] && exit 1
  sleep $((attempt * 6))
done

git fetch origin main
git reset --hard origin/main
SOCIAL_FILE="$(python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('.github/greenery-publication-bundle.json').read_text(encoding='utf-8'))['socialFile'])
PY
)"
SOCIAL_URL="$(python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('.github/greenery-publication-bundle.json').read_text(encoding='utf-8'))['socialUrl'])
PY
)"

# Přímé nasazení na OVH a do aktivního kontejneru.
if [[ -n "${KEY1:-}" ]]; then
  printf '%s\n' "$KEY1" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
elif [[ -n "${KEY2:-}" ]]; then
  printf '%s\n' "$KEY2" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
else
  echo 'Chybí SSH klíč pro OVH.' >&2
  exit 1
fi
chmod 600 "$RUNNER_TEMP/ovh_key"

bundle="$RUNNER_TEMP/nk-greenery-repair"
rm -rf "$bundle"
mkdir -p "$bundle/clanky" "$bundle/social" "$bundle/newsletter"
cp "$ARTICLE" "$bundle/clanky/"
cp clanky/index.html "$bundle/clanky/index.html"
cp "$SOCIAL_FILE" "$bundle/social/"
cp newsletter/server.py "$bundle/newsletter/server.py"
cp site.js index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt "$bundle/"

for attempt in 1 2 3; do
  if scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 -r "$bundle" ubuntu@57.129.43.215:/tmp/nk-greenery-repair; then
    break
  fi
  [[ "$attempt" == 3 ]] && exit 1
  sleep $((attempt * 8))
done

ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -euo pipefail
sudo -n true
sudo install -d -m 0755 /var/www/nasekadan/clanky /var/www/nasekadan/social /opt/nasekadan/newsletter
sudo install -m 0644 /tmp/nk-greenery-repair/newsletter/server.py /opt/nasekadan/newsletter/server.py
sudo install -m 0644 /tmp/nk-greenery-repair/site.js /var/www/nasekadan/site.js
sudo install -m 0644 /tmp/nk-greenery-repair/clanky/sekani-travniku-kadan-spravci-vysky-2026.html /var/www/nasekadan/clanky/
sudo install -m 0644 /tmp/nk-greenery-repair/clanky/index.html /var/www/nasekadan/clanky/index.html
find /tmp/nk-greenery-repair/social -maxdepth 1 -type f -exec sudo install -m 0644 {} /var/www/nasekadan/social/ \;
for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt; do
  sudo install -m 0644 "/tmp/nk-greenery-repair/$f" "/var/www/nasekadan/$f"
done
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social
  sudo docker cp /tmp/nk-greenery-repair/site.js nasekadan-web:/usr/share/nginx/html/site.js
  sudo docker cp /tmp/nk-greenery-repair/clanky/sekani-travniku-kadan-spravci-vysky-2026.html nasekadan-web:/usr/share/nginx/html/clanky/
  sudo docker cp /tmp/nk-greenery-repair/clanky/index.html nasekadan-web:/usr/share/nginx/html/clanky/index.html
  for f in /tmp/nk-greenery-repair/social/*; do sudo docker cp "$f" nasekadan-web:/usr/share/nginx/html/social/; done
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt; do
    sudo docker cp "/tmp/nk-greenery-repair/$f" "nasekadan-web:/usr/share/nginx/html/$f"
  done
fi
sudo systemctl restart nasekadan-newsletter.service
for attempt in $(seq 1 25); do
  curl -fsS --max-time 4 http://127.0.0.1:8765/health >/dev/null && break
  [[ "$attempt" == 25 ]] && { sudo journalctl -u nasekadan-newsletter.service -n 100 --no-pager; exit 1; }
  sleep 2
done
sudo systemctl is-active --quiet nasekadan-newsletter.service
grep -Fq '# BEGIN POLL_RESULTS_API' /opt/nasekadan/newsletter/server.py
grep -Fq 'Sedm centimetrů je smluvní minimum jedné konkrétní lokality' /var/www/nasekadan/clanky/sekani-travniku-kadan-spravci-vysky-2026.html
rm -rf /tmp/nk-greenery-repair
REMOTE

# Veřejná integrační kontrola včetně skutečného prohlížeče.
browser="$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
[[ -n "$browser" ]] || { echo 'Na runneru chybí Chromium/Chrome.' >&2; exit 1; }
stamp="${GITHUB_RUN_ID:-manual}-$(date +%s)"
test_poll="healthcheck-greenery-${GITHUB_RUN_ID:-manual}-$(date +%s)"
verified=false
actual=''
for attempt in $(seq 1 24); do
  article="$(curl -4 -kfsS --max-time 25 "${PUBLIC_URL}?v=${stamp}-${attempt}" 2>/dev/null || true)"
  home="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/?v=${stamp}-${attempt}" 2>/dev/null || true)"
  archive="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/clanky/?v=${stamp}-${attempt}" 2>/dev/null || true)"
  rss="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/rss.xml?v=${stamp}-${attempt}" 2>/dev/null || true)"
  sitemap="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/sitemap.xml?v=${stamp}-${attempt}" 2>/dev/null || true)"
  news="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/news-sitemap.xml?v=${stamp}-${attempt}" 2>/dev/null || true)"
  js="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/site.js?v=${stamp}-${attempt}" 2>/dev/null || true)"
  actual="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/api/newsletter/poll/results?poll=${POLL_ID}&t=${stamp}-${attempt}" 2>/dev/null || true)"
  jar="$RUNNER_TEMP/greenery-cookie-${attempt}.txt"
  rm -f "$jar"
  first="$(curl -4 -kfsS --max-time 25 -c "$jar" -A 'GreeneryRepair-A' -X POST 'https://nasekadan.cz/api/newsletter/poll/vote' -H 'Content-Type: application/json' --data "{\"pollId\":\"${test_poll}\",\"choice\":\"vyssi\"}" 2>/dev/null || true)"
  second="$(curl -4 -kfsS --max-time 25 -b "$jar" -c "$jar" -A 'GreeneryRepair-B' -X POST 'https://nasekadan.cz/api/newsletter/poll/vote' -H 'Content-Type: application/json' --data "{\"pollId\":\"${test_poll}\",\"choice\":\"jiny\"}" 2>/dev/null || true)"
  reload="$(curl -4 -kfsS --max-time 25 -b "$jar" "https://nasekadan.cz/api/newsletter/poll/results?poll=${test_poll}&t=${stamp}-${attempt}" 2>/dev/null || true)"
  image="$RUNNER_TEMP/greenery-social-${attempt}.png"
  curl -4 -kfsS --max-time 25 "${SOCIAL_URL}?v=${stamp}-${attempt}" -o "$image" 2>/dev/null || true
  dom="$RUNNER_TEMP/greenery-dom-${attempt}.html"
  "$browser" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage --ignore-certificate-errors --virtual-time-budget=10000 --dump-dom "${PUBLIC_URL}?browser=${stamp}-${attempt}" > "$dom" 2>/dev/null || true

  if ARTICLE_HTML="$article" HOME_HTML="$home" ARCHIVE_HTML="$archive" RSS_XML="$rss" SITEMAP_XML="$sitemap" NEWS_XML="$news" JS_TEXT="$js" ACTUAL="$actual" FIRST="$first" SECOND="$second" RELOAD="$reload" DOM_FILE="$dom" IMAGE_FILE="$image" SOCIAL_URL="$SOCIAL_URL" PUBLIC_URL="$PUBLIC_URL" python3 - <<'PY'
import json, os, sys
from pathlib import Path
from PIL import Image
try:
    actual=json.loads(os.environ['ACTUAL'])
    first=json.loads(os.environ['FIRST'])
    second=json.loads(os.environ['SECOND'])
    reload=json.loads(os.environ['RELOAD'])
    dom=Path(os.environ['DOM_FILE']).read_text(encoding='utf-8',errors='replace')
    with Image.open(os.environ['IMAGE_FILE']) as im:
        image_ok=im.format=='PNG' and im.size==(1200,630)
except Exception:
    raise SystemExit(1)
url=os.environ['PUBLIC_URL']
article=os.environ['ARTICLE_HTML']
checks=[
    'Sedm centimetrů je smluvní minimum jedné konkrétní lokality' in article,
    'index,follow' in article and 'noindex,nofollow' not in article,
    'data-poll-id="sekani-travniku-kadan-2026"' in article,
    '/site.js?v=20260801-poll-system-v2' in article,
    '/clanky/sekani-travniku-kadan-spravci-vysky-2026.html' in os.environ['HOME_HTML'],
    '/clanky/sekani-travniku-kadan-spravci-vysky-2026.html' in os.environ['ARCHIVE_HTML'],
    url in os.environ['RSS_XML'], url in os.environ['SITEMAP_XML'], url in os.environ['NEWS_XML'],
    'Průběžné výsledky' in os.environ['JS_TEXT'] and 'poll-result-value' in os.environ['JS_TEXT'],
    actual.get('ok') is True and isinstance(actual.get('total'),int) and isinstance(actual.get('counts'),dict) and isinstance(actual.get('percentages'),dict),
    first.get('ok') is True and first.get('accepted') is True and first.get('selected')=='vyssi',
    second.get('ok') is True and second.get('accepted') is False and second.get('selected')=='vyssi',
    reload.get('total')==1 and reload.get('counts',{}).get('vyssi')==1 and reload.get('selected')=='vyssi',
    'Průběžné výsledky' in dom and 'poll-results-total' in dom and 'poll-result-value' in dom and '%' in dom and 'hlas' in dom,
    image_ok,
]
if not all(checks):
    print(json.dumps({'checks':checks,'actual':actual,'first':first,'second':second,'reload':reload},ensure_ascii=False),file=sys.stderr)
    raise SystemExit(1)
PY
  then
    verified=true
    break
  fi
  sleep 7
done
[[ "$verified" == true ]] || exit 1

# Zveřejnit na Facebooku přímo a uložit potvrzovací marker.
export FACEBOOK_WAIT_TIMEOUT='300'
python3 scripts/process_facebook_queue_live.py "$ARTICLE"

git config user.name 'Naše Kadaň Facebook oprava'
git config user.email 'info@nasekadan.cz'
[[ -f .github/facebook-publish-pending.txt ]] && git add -A -- .github/facebook-publish-pending.txt
[[ -f .github/facebook-last-status.json ]] && git add -A -- .github/facebook-last-status.json
[[ -d .github/facebook-published ]] && git add -A -- .github/facebook-published
if ! git diff --cached --quiet; then
  git commit -m 'Potvrdit Facebook publikaci článku o sečení [skip ci]'
fi
git reset --hard HEAD
git clean -fd
for attempt in 1 2 3 4 5; do
  if git pull --rebase origin main && git push origin HEAD:main; then break; fi
  git rebase --abort 2>/dev/null || true
  [[ "$attempt" == 5 ]] && exit 1
  sleep $((attempt * 5))
done

marker="$(python3 - <<'PY'
import hashlib
from pathlib import Path
article='clanky/sekani-travniku-kadan-spravci-vysky-2026.html'
print(f'.github/facebook-published/{Path(article).stem}-{hashlib.sha256(article.encode()).hexdigest()[:10]}.json')
PY
)"
git fetch origin main
git show "origin/main:${marker}" > "$RUNNER_TEMP/facebook-marker.json"
python3 - "$RUNNER_TEMP/facebook-marker.json" <<'PY'
import json,sys
p=json.load(open(sys.argv[1],encoding='utf-8'))
assert p['article_path']=='clanky/sekani-travniku-kadan-spravci-vysky-2026.html'
assert p.get('facebook_post_id')
print(json.dumps(p,ensure_ascii=False))
PY

echo 'HOTOVO: článek, anketa, přehledy, obrázek i Facebook jsou veřejně ověřené.'
