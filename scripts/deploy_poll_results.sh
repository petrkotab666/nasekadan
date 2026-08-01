#!/usr/bin/env bash
set -euo pipefail

ARTICLE='clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html'
VERSION='20260801-poll-system-v2'
POLL_ID='smr-tusimice-2026'

python3 scripts/install_poll_system_v2.py
python3 -m py_compile newsletter/server.py scripts/install_poll_system_v2.py scripts/test_poll_system_v2.py scripts/prepare_greenery_publication_20260801.py
python3 scripts/test_poll_system_v2.py
grep -Fq '# BEGIN POLL_RESULTS_API' newsletter/server.py
grep -Fq '/api/newsletter/poll/results' site.js
grep -Fq 'Průběžné výsledky' site.js
grep -Fq "/site.js?v=${VERSION}" "$ARTICLE"
grep -Fq 'POLL_SYSTEM_V2' scripts/prepare_greenery_publication_20260801.py

git config user.name 'Naše Kadaň deploy bot'
git config user.email 'info@nasekadan.cz'
git add newsletter/server.py site.js "$ARTICLE" \
  .github/drafts/jaderne-tusimice-smr-voda-doprava-eia-2026.html \
  scripts/install_poll_system_v2.py scripts/test_poll_system_v2.py \
  scripts/enable_poll_results.py scripts/deploy_poll_results.sh \
  scripts/prepare_greenery_publication_20260801.py
if ! git diff --cached --quiet; then
  git commit -m 'Zapnout databázové ankety s veřejnými výsledky [skip ci]'
  for attempt in 1 2 3 4 5; do
    if git pull --rebase origin main && git push origin HEAD:main; then break; fi
    git rebase --abort 2>/dev/null || true
    [ "$attempt" = 5 ] && exit 1
    sleep $((attempt * 4))
  done
fi

sudo -n true
sudo install -m 0644 site.js /var/www/nasekadan/site.js
sudo install -m 0644 "$ARTICLE" "/var/www/nasekadan/$ARTICLE"
sudo install -m 0644 newsletter/server.py /opt/nasekadan/newsletter/server.py
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker cp site.js nasekadan-web:/usr/share/nginx/html/site.js
  sudo docker cp "$ARTICLE" "nasekadan-web:/usr/share/nginx/html/$ARTICLE"
fi
sudo systemctl restart nasekadan-newsletter.service
for attempt in $(seq 1 20); do
  if curl -fsS --max-time 3 http://127.0.0.1:8765/health >/dev/null; then break; fi
  if [ "$attempt" = 20 ]; then
    sudo journalctl -u nasekadan-newsletter.service -n 100 --no-pager
    exit 1
  fi
  sleep 2
done
sudo systemctl is-active --quiet nasekadan-newsletter.service

stamp="${GITHUB_RUN_ID:-manual}-$(date +%s)"
test_poll="healthcheck-${GITHUB_RUN_ID:-manual}-$(date +%s)"
article_url="https://nasekadan.cz/$ARTICLE"
verified=false
actual=''
for attempt in $(seq 1 18); do
  js="$(curl -4 -kfsS --max-time 20 "https://nasekadan.cz/site.js?v=${stamp}-${attempt}" || true)"
  article="$(curl -4 -kfsS --max-time 20 "${article_url}?v=${stamp}-${attempt}" || true)"
  actual="$(curl -4 -kfsS --max-time 20 "https://nasekadan.cz/api/newsletter/poll/results?poll=${POLL_ID}&t=${stamp}-${attempt}" || true)"
  jar="$RUNNER_TEMP/poll-cookie-${attempt}.txt"
  rm -f "$jar"
  first="$(curl -4 -kfsS --max-time 20 -c "$jar" -A 'NaseKadan-Poll-Healthcheck-A' -X POST \
    'https://nasekadan.cz/api/newsletter/poll/vote' -H 'Content-Type: application/json' \
    --data "{\"pollId\":\"${test_poll}\",\"choice\":\"ok\"}" || true)"
  second="$(curl -4 -kfsS --max-time 20 -b "$jar" -A 'NaseKadan-Poll-Healthcheck-B' -X POST \
    'https://nasekadan.cz/api/newsletter/poll/vote' -H 'Content-Type: application/json' \
    --data "{\"pollId\":\"${test_poll}\",\"choice\":\"jiny\"}" || true)"
  test_results="$(curl -4 -kfsS --max-time 20 -b "$jar" "https://nasekadan.cz/api/newsletter/poll/results?poll=${test_poll}&t=${stamp}-${attempt}" || true)"

  if JS="$js" ARTICLE_HTML="$article" ACTUAL="$actual" FIRST="$first" SECOND="$second" TEST_RESULTS="$test_results" python3 - <<'PY'
import json, os, sys
try:
    actual=json.loads(os.environ['ACTUAL']);first=json.loads(os.environ['FIRST']);second=json.loads(os.environ['SECOND']);test=json.loads(os.environ['TEST_RESULTS'])
except Exception:
    raise SystemExit(1)
checks=[
    'Průběžné výsledky' in os.environ['JS'],
    '/api/newsletter/poll/results' in os.environ['JS'],
    '/api/newsletter/poll/vote' in os.environ['JS'],
    'poll-result-value' in os.environ['JS'],
    '/site.js?v=20260801-poll-system-v2' in os.environ['ARTICLE_HTML'],
    actual.get('ok') is True and isinstance(actual.get('counts'),dict) and isinstance(actual.get('percentages'),dict),
    first.get('ok') is True and first.get('accepted') is True and first.get('selected')=='ok',
    second.get('ok') is True and second.get('accepted') is False and second.get('selected')=='ok',
    test.get('total')==1 and test.get('counts',{}).get('ok')==1 and test.get('selected')=='ok',
]
sys.exit(0 if all(checks) else 1)
PY
  then
    verified=true
    break
  fi
  sleep 5
done

mkdir -p .github
ACTUAL_JSON="${actual:-null}" python3 - <<'PY'
import json,os
from datetime import datetime,timezone
from pathlib import Path
try: results=json.loads(os.environ.get('ACTUAL_JSON') or 'null')
except Exception: results=None
payload={'ok':os.environ.get('VERIFIED')=='true','checkedAtUtc':datetime.now(timezone.utc).isoformat(),'pollId':'smr-tusimice-2026','version':'20260801-poll-system-v2','results':results}
Path('.github/poll-results-status.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PY

git add .github/poll-results-status.json
git commit -m 'Zapsat stav databázové ankety [skip ci]' || true
for attempt in 1 2 3 4; do
  if git pull --rebase origin main && git push origin HEAD:main; then break; fi
  git rebase --abort 2>/dev/null || true
  [ "$attempt" = 4 ] && exit 1
  sleep $((attempt * 3))
done

[ "$verified" = true ]
