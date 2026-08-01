#!/usr/bin/env bash
set -euo pipefail

ARTICLE='clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html'
VERSION='20260801-poll-results-1'
POLL_ID='smr-tusimice-2026'

python3 scripts/enable_poll_results.py
python3 -m py_compile newsletter/server.py scripts/enable_poll_results.py
grep -Fq '# BEGIN POLL_RESULTS_API' newsletter/server.py
grep -Fq '/api/newsletter/poll/results' site.js
grep -Fq 'Průběžné výsledky' site.js
grep -Fq "/site.js?v=${VERSION}" "$ARTICLE"

git config user.name 'Naše Kadaň deploy bot'
git config user.email 'info@nasekadan.cz'
git add newsletter/server.py site.js "$ARTICLE" scripts/enable_poll_results.py scripts/deploy_poll_results.sh
if ! git diff --cached --quiet; then
  git commit -m 'Zapnout živé výsledky ankety SMR Tušimice [skip ci]'
  for attempt in 1 2 3 4; do
    if git pull --rebase origin main && git push origin HEAD:main; then break; fi
    git rebase --abort 2>/dev/null || true
    [ "$attempt" = 4 ] && exit 1
    sleep $((attempt * 3))
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
for attempt in $(seq 1 12); do
  js="$(curl -kfsS --max-time 20 "https://nasekadan.cz/site.js?v=${stamp}-${attempt}" || true)"
  article="$(curl -kfsS --max-time 20 "${article_url}?v=${stamp}-${attempt}" || true)"
  actual="$(curl -kfsS --max-time 20 "https://nasekadan.cz/api/newsletter/poll/results?poll=${POLL_ID}&t=${stamp}-${attempt}" || true)"
  first="$(curl -kfsS --max-time 20 -A 'NaseKadan-Poll-Healthcheck' -X POST \
    'https://nasekadan.cz/api/newsletter/poll/vote' -H 'Content-Type: application/json' \
    --data "{\"pollId\":\"${test_poll}\",\"choice\":\"ok\"}" || true)"
  second="$(curl -kfsS --max-time 20 -A 'NaseKadan-Poll-Healthcheck' -X POST \
    'https://nasekadan.cz/api/newsletter/poll/vote' -H 'Content-Type: application/json' \
    --data "{\"pollId\":\"${test_poll}\",\"choice\":\"jiny\"}" || true)"
  test_results="$(curl -kfsS --max-time 20 "https://nasekadan.cz/api/newsletter/poll/results?poll=${test_poll}&t=${stamp}-${attempt}" || true)"

  if JS="$js" ARTICLE_HTML="$article" ACTUAL="$actual" FIRST="$first" SECOND="$second" TEST_RESULTS="$test_results" python3 - <<'PY'
import json, os, sys
try:
    actual = json.loads(os.environ['ACTUAL'])
    first = json.loads(os.environ['FIRST'])
    second = json.loads(os.environ['SECOND'])
    test = json.loads(os.environ['TEST_RESULTS'])
except Exception:
    raise SystemExit(1)
checks = [
    'Průběžné výsledky' in os.environ['JS'],
    '/api/newsletter/poll/results' in os.environ['JS'],
    '/api/newsletter/poll/vote' in os.environ['JS'],
    'Průběžné výsledky se zobrazují hned' in os.environ['ARTICLE_HTML'],
    '/site.js?v=20260801-poll-results-1' in os.environ['ARTICLE_HTML'],
    actual.get('ok') is True and isinstance(actual.get('counts'), dict),
    first.get('ok') is True and first.get('selected') == 'ok',
    second.get('ok') is True and second.get('accepted') is False and second.get('selected') == 'ok',
    test.get('total') == 1 and test.get('counts', {}).get('ok') == 1,
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
printf '{"ok":%s,"run_id":"%s","checked_at":"%s","verified":%s,"poll_id":"%s","version":"%s","results":%s}\n' \
  "$verified" "${GITHUB_RUN_ID:-manual}" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$verified" "$POLL_ID" "$VERSION" "${actual:-null}" \
  > .github/poll-results-status.json

git add .github/poll-results-status.json
git commit -m 'Zapsat stav živých výsledků ankety [skip ci]' || true
for attempt in 1 2 3 4; do
  if git pull --rebase origin main && git push origin HEAD:main; then break; fi
  git rebase --abort 2>/dev/null || true
  [ "$attempt" = 4 ] && exit 1
  sleep $((attempt * 3))
done

[ "$verified" = true ]
