#!/usr/bin/env bash
set -euo pipefail

ARTICLE='clanky/sekani-travniku-kadan-spravci-vysky-2026.html'
NUCLEAR_ARTICLE='clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html'
VERSION='20260801-poll-system-v3'

python3 scripts/fix_poll_stale_browser_state.py
python3 -m py_compile scripts/fix_poll_stale_browser_state.py scripts/install_poll_system_v2.py scripts/prepare_greenery_publication_20260801.py
node --check site.js
npm install --no-save --no-package-lock jsdom@24 >/dev/null
node scripts/test_poll_stale_browser_state.mjs
grep -Fq 'POLL_SERVER_AUTHORITATIVE_V3' site.js
grep -Fq 'localStorage.removeItem(storageKey)' site.js
grep -Fq "/site.js?v=${VERSION}" "$ARTICLE"
! grep -Fq "if(saved){setLocked(saved)" site.js

git config user.name 'Naše Kadaň – oprava ankety'
git config user.email 'info@nasekadan.cz'
git add site.js "$ARTICLE" "$NUCLEAR_ARTICLE" \
  .github/drafts/jaderne-tusimice-smr-voda-doprava-eia-2026.html \
  scripts/install_poll_system_v2.py scripts/prepare_greenery_publication_20260801.py \
  scripts/fix_poll_stale_browser_state.py scripts/test_poll_stale_browser_state.mjs scripts/run_greenery_poll_hotfix.sh
if ! git diff --cached --quiet; then
  git commit -m 'Opravit hlasování po starém lokálním záznamu [skip ci]'
  for attempt in 1 2 3 4 5; do
    if git pull --rebase origin main && git push origin HEAD:main; then break; fi
    git rebase --abort 2>/dev/null || true
    [[ "$attempt" == 5 ]] && exit 1
    sleep $((attempt * 4))
  done
fi

git fetch origin main
git reset --hard origin/main
python3 scripts/fix_poll_stale_browser_state.py
node --check site.js

if [[ -n "${KEY1:-}" ]]; then
  printf '%s\n' "$KEY1" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
elif [[ -n "${KEY2:-}" ]]; then
  printf '%s\n' "$KEY2" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
else
  echo 'Chybí SSH klíč pro OVH.' >&2
  exit 1
fi
chmod 600 "$RUNNER_TEMP/ovh_key"

bundle="$RUNNER_TEMP/nk-poll-hotfix"
rm -rf "$bundle"
mkdir -p "$bundle/clanky" "$bundle/newsletter"
cp site.js "$bundle/site.js"
cp "$ARTICLE" "$bundle/clanky/"
cp "$NUCLEAR_ARTICLE" "$bundle/clanky/"
cp newsletter/server.py "$bundle/newsletter/server.py"
scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 -r "$bundle" ubuntu@57.129.43.215:/tmp/nk-poll-hotfix
ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -euo pipefail
sudo -n true
sudo install -m 0644 /tmp/nk-poll-hotfix/site.js /var/www/nasekadan/site.js
sudo install -m 0644 /tmp/nk-poll-hotfix/clanky/sekani-travniku-kadan-spravci-vysky-2026.html /var/www/nasekadan/clanky/
sudo install -m 0644 /tmp/nk-poll-hotfix/clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html /var/www/nasekadan/clanky/
sudo install -m 0644 /tmp/nk-poll-hotfix/newsletter/server.py /opt/nasekadan/newsletter/server.py
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker cp /tmp/nk-poll-hotfix/site.js nasekadan-web:/usr/share/nginx/html/site.js
  sudo docker cp /tmp/nk-poll-hotfix/clanky/sekani-travniku-kadan-spravci-vysky-2026.html nasekadan-web:/usr/share/nginx/html/clanky/
  sudo docker cp /tmp/nk-poll-hotfix/clanky/jaderne-tusimice-smr-voda-doprava-eia-2026.html nasekadan-web:/usr/share/nginx/html/clanky/
fi
sudo systemctl restart nasekadan-newsletter.service
for attempt in $(seq 1 20); do
  curl -fsS --max-time 3 http://127.0.0.1:8765/health >/dev/null && break
  [[ "$attempt" == 20 ]] && { sudo journalctl -u nasekadan-newsletter.service -n 100 --no-pager; exit 1; }
  sleep 2
done
sudo systemctl is-active --quiet nasekadan-newsletter.service
grep -Fq 'POLL_SERVER_AUTHORITATIVE_V3' /var/www/nasekadan/site.js
grep -Fq '/site.js?v=20260801-poll-system-v3' /var/www/nasekadan/clanky/sekani-travniku-kadan-spravci-vysky-2026.html
rm -rf /tmp/nk-poll-hotfix
REMOTE

stamp="${GITHUB_RUN_ID:-manual}-$(date +%s)"
verified=false
for attempt in $(seq 1 18); do
  article="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/$ARTICLE?v=${stamp}-${attempt}" || true)"
  js="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/site.js?v=${stamp}-${attempt}" || true)"
  api="$(curl -4 -kfsS --max-time 25 "https://nasekadan.cz/api/newsletter/poll/results?poll=sekani-travniku-kadan-2026&t=${stamp}-${attempt}" || true)"
  if ARTICLE_HTML="$article" SITE_JS="$js" API_JSON="$api" node <<'NODE'
const article=process.env.ARTICLE_HTML||'';
const js=process.env.SITE_JS||'';
let api;try{api=JSON.parse(process.env.API_JSON||'');}catch{process.exit(1)}
const ok=article.includes('/site.js?v=20260801-poll-system-v3') && article.includes('data-poll-id="sekani-travniku-kadan-2026"') && js.includes('POLL_SERVER_AUTHORITATIVE_V3') && js.includes('localStorage.removeItem(storageKey)') && !js.includes("if(saved){setLocked(saved)") && api.ok===true && typeof api.total==='number' && api.counts && api.percentages;
process.exit(ok?0:1);
NODE
  then
    export LIVE_ARTICLE="$article" LIVE_JS="$js"
    node <<'NODE'
const {JSDOM}=await import('jsdom');
let html=process.env.LIVE_ARTICLE;
const pollId='healthcheck-greenery-stale-'+Date.now();
html=html.replace('data-poll-id="sekani-travniku-kadan-2026"',`data-poll-id="${pollId}"`);
const dom=new JSDOM(html,{url:'https://nasekadan.cz/clanky/sekani-travniku-kadan-spravci-vysky-2026.html',runScripts:'outside-only',pretendToBeVisual:true});
const w=dom.window;
w.localStorage.setItem(`nk-poll-${pollId}`,'mene-casto-vyse');
let cookie='';let postCount=0;
w.fetch=async(input,options={})=>{const url=new URL(String(input),'https://nasekadan.cz').href;const headers=new Headers(options.headers||{});if(cookie)headers.set('Cookie',cookie);const response=await fetch(url,{...options,headers});const setCookie=response.headers.get('set-cookie');if(setCookie)cookie=setCookie.split(';')[0];if(String(options.method||'GET').toUpperCase()==='POST')postCount++;return response;};
w.eval(process.env.LIVE_JS);
w.document.dispatchEvent(new w.Event('DOMContentLoaded',{bubbles:true}));
await new Promise(r=>setTimeout(r,1200));
const button=w.document.querySelector('[data-poll-vote="soucasny-rezim"]');
if(!button||button.disabled)throw new Error('Starý localStorage stále blokuje živé tlačítko.');
if(w.localStorage.getItem(`nk-poll-${pollId}`))throw new Error('Starý localStorage nebyl odstraněn.');
button.click();await new Promise(r=>setTimeout(r,1200));
const text=w.document.querySelector('.poll-results')?.textContent||'';
if(postCount!==1||!button.disabled||!text.includes('1 hlas')||!text.includes('100 %'))throw new Error('Živý DOM neukázal uložený hlas a procenta: '+text);
console.log('Živý test prošel:',text.replace(/\s+/g,' ').trim());
w.close();process.exit(0);
NODE
    verified=true
    break
  fi
  sleep 6
done
[[ "$verified" == true ]]

python3 - <<'PY'
import json,os
from datetime import datetime,timezone
from pathlib import Path
payload={
  'status':'passed',
  'checkedAtUtc':datetime.now(timezone.utc).isoformat(),
  'runId':os.environ.get('GITHUB_RUN_ID','manual'),
  'staleLocalStorageCleared':True,
  'realVoteStored':True,
  'visibleCountsAndPercentages':True,
  'article':'https://nasekadan.cz/clanky/sekani-travniku-kadan-spravci-vysky-2026.html',
  'version':'20260801-poll-system-v3',
}
Path('.github/greenery-poll-hotfix-status.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PY

git add .github/greenery-poll-hotfix-status.json
git commit -m 'Zapsat opravu ankety článku o sečení: passed [skip ci]' || true
for attempt in 1 2 3 4 5; do
  if git pull --rebase origin main && git push origin HEAD:main; then break; fi
  git rebase --abort 2>/dev/null || true
  [[ "$attempt" == 5 ]] && exit 1
  sleep $((attempt * 3))
done
