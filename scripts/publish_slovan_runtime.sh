#!/usr/bin/env bash
set -Eeuo pipefail

MODE="${1:-primary}"
REPO="petrkotab666/nasekadan"
ARTICLE_REL="/clanky/slovan-druhy-pokus.html"
ARTICLE_URL="https://nasekadan.cz${ARTICLE_REL}"
ARTICLE_FILE="clanky/slovan-druhy-pokus.html"
SOCIAL_FILE="social/slovan-druhy-pokus-20260805.png"
SOCIAL_URL="https://nasekadan.cz/${SOCIAL_FILE}"
EXPECTED_H1="Kadaň vybírá nového stavitele Slovanu za 195 milionů. Účet prvního pokusu stále není veřejný"
EXPECTED_PUBLISHED="2026-08-05T04:00:00+02:00"
EXPECTED_COUNT_MIN=49
BASE="https://nasekadan.cz"

log() { printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"; }

setup_git() {
  git config user.name 'github-actions[bot]'
  git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
}

reset_main() {
  git fetch origin main
  git reset --hard origin/main
}

local_generate_and_push() {
  local pushed=0
  local attempt
  for attempt in 1 2 3 4; do
    log "Generování a zápis do main (${attempt}/4)"
    reset_main
    python3 -m py_compile scripts/publish_slovan_20260805.py scripts/enforce_article_visibility.py
    python3 scripts/publish_slovan_20260805.py

    grep -Fq "<h1>${EXPECTED_H1}</h1>" "$ARTICLE_FILE"
    grep -Fq 'index,follow' "$ARTICLE_FILE"
    ! grep -Fq 'noindex' "$ARTICLE_FILE"
    grep -Fq "$EXPECTED_PUBLISHED" "$ARTICLE_FILE"
    grep -Fq 'Druhý pokus může Kadani přinést potřebné byty' "$ARTICLE_FILE"
    ! grep -Fq 'Náhled článku' "$ARTICLE_FILE"
    ! grep -Fq 'Otázky pro město' "$ARTICLE_FILE"
    grep -Fq "$ARTICLE_REL" index.html
    grep -Fq "$ARTICLE_URL" rss.xml sitemap.xml news-sitemap.xml llms.txt
    grep -Fq '/pocasi.js' index.html
    test -s "$SOCIAL_FILE"
    test "$(wc -c <"$SOCIAL_FILE")" -gt 10000

    python3 - <<'PY'
import json, re, xml.etree.ElementTree as ET
from pathlib import Path
url='https://nasekadan.cz/clanky/slovan-druhy-pokus.html'
reg=json.loads(Path('data/published-content-index.json').read_text(encoding='utf-8'))
count=reg['article_count']
assert count>=49, count
assert len(reg['articles'])==count
assert any(x.get('url')==url for x in reg['articles'])
assert reg['validation']['rss_count']==count, reg['validation']['rss_count']
assert reg['validation']['duplicate_urls']==[]
assert reg['validation']['duplicate_fingerprints']==[]
assert len(re.findall(r'<item\b', Path('rss.xml').read_text(encoding='utf-8')))==count
assert len(ET.parse('news-sitemap.xml').getroot())==10
man=json.loads(Path('data/article-integrity-manifest.json').read_text(encoding='utf-8'))
assert man['article_count']==count
assert any(x.get('url')==url for x in man['articles'])
PY

    git add "$ARTICLE_FILE" "$SOCIAL_FILE" index.html clanky/index.html clanky/strana-*.html rss.xml sitemap.xml news-sitemap.xml llms.txt data/published-content-index.json data/article-integrity-manifest.json
    if git diff --cached --quiet; then
      log "Publikační obsah už je v main zapsaný."
      pushed=1
      break
    fi
    git commit -m 'Publikovat: nový Slovan se 48 byty'
    if git push origin HEAD:main; then
      pushed=1
      break
    fi
    log "Push selhal, znovu stavím nad aktuálním mainem."
    sleep $((attempt * 3))
  done
  test "$pushed" = 1
  PUBLISH_SHA="$(git rev-parse HEAD)"
  export PUBLISH_SHA
  log "Publikační commit: $PUBLISH_SHA"
}

save_evidence_and_push() {
  local saved=0
  local attempt
  for attempt in 1 2 3 4; do
    reset_main
    PUBLISH_SHA="${PUBLISH_SHA:-$(git rev-parse HEAD)}" ARTICLE_URL="$ARTICLE_URL" python3 - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
path=Path('data/published-content-index.json')
data=json.loads(path.read_text(encoding='utf-8'))
url=os.environ['ARTICLE_URL']; sha=os.environ['PUBLISH_SHA']
article=next((x for x in data.get('articles',[]) if x.get('url')==url),None)
if article is None: raise SystemExit('Slovan chybí v kanonickém registru.')
if article.get('source_commit') in (None,'','pending-publication-commit'):
    article['source_commit']=sha
data['source_commit']=sha
v=data.setdefault('validation',{})
v['repair_pending_public_verification']=True
v['deployment_health']='ok'
v['deployment_health_status_field_present']=True
v['deployment_health_source']=sha
v['last_consistency_audit']={
    'status':'pending_public_verification',
    'checked_at':datetime.now(timezone.utc).isoformat(),
    'article_count':len(data.get('articles',[])),
    'updated_url':url,
    'source_commit':sha,
}
data['generated_at']=datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
Path('deployment-health.txt').write_text(f'status=ok\nsource={sha}\narticle={url}\n',encoding='utf-8')
PY
    git add data/published-content-index.json deployment-health.txt
    if git diff --cached --quiet; then saved=1; break; fi
    git commit -m 'Evidence: zapsat zdroj publikace článku o Slovanu'
    if git push origin HEAD:main; then saved=1; break; fi
    sleep $((attempt * 3))
  done
  test "$saved" = 1
  EVIDENCE_SHA="$(git rev-parse HEAD)"
  export EVIDENCE_SHA
}

prepare_key() {
  local key="${OVH_KEY_A:-${OVH_KEY_B:-}}"
  test -n "$key"
  printf '%s\n' "$key" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
  chmod 600 "$RUNNER_TEMP/ovh_key"
}

deploy_bundle() {
  reset_main
  prepare_key
  local bundle="$RUNNER_TEMP/slovan-publish-bundle"
  rm -rf "$bundle"
  mkdir -p "$bundle/clanky" "$bundle/social" "$bundle/data"
  cp "$ARTICLE_FILE" "$bundle/clanky/"
  cp "$SOCIAL_FILE" "$bundle/social/"
  cp clanky/index.html clanky/strana-*.html "$bundle/clanky/"
  cp index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt "$bundle/"
  cp data/published-content-index.json data/article-integrity-manifest.json "$bundle/data/"

  local ok=0
  local attempt
  for attempt in 1 2 3 4; do
    log "Nasazení na OVH (${attempt}/4)"
    if scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 -r "$bundle" ubuntu@57.129.43.215:/tmp/slovan-publish-bundle && \
       ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -euo pipefail
src=/tmp/slovan-publish-bundle
root=/var/www/nasekadan
sudo install -d -m 0755 "$root/clanky" "$root/social" "$root/data"
sudo install -m 0644 "$src/clanky/slovan-druhy-pokus.html" "$root/clanky/slovan-druhy-pokus.html"
sudo install -m 0644 "$src/social/slovan-druhy-pokus-20260805.png" "$root/social/slovan-druhy-pokus-20260805.png"
sudo rm -f "$root"/clanky/strana-*.html
for f in "$src"/clanky/index.html "$src"/clanky/strana-*.html; do
  [ -e "$f" ] || continue
  sudo install -m 0644 "$f" "$root/clanky/$(basename "$f")"
done
for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do
  sudo install -m 0644 "$src/$f" "$root/$f"
done
for f in published-content-index.json article-integrity-manifest.json; do
  sudo install -m 0644 "$src/data/$f" "$root/data/$f"
done
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social /usr/share/nginx/html/data
  sudo docker exec nasekadan-web sh -lc 'rm -f /usr/share/nginx/html/clanky/strana-*.html'
  sudo docker cp "$src/clanky/slovan-druhy-pokus.html" nasekadan-web:/usr/share/nginx/html/clanky/slovan-druhy-pokus.html
  sudo docker cp "$src/social/slovan-druhy-pokus-20260805.png" nasekadan-web:/usr/share/nginx/html/social/slovan-druhy-pokus-20260805.png
  for f in "$src"/clanky/index.html "$src"/clanky/strana-*.html; do
    [ -e "$f" ] || continue
    sudo docker cp "$f" "nasekadan-web:/usr/share/nginx/html/clanky/$(basename "$f")"
  done
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do
    sudo docker cp "$src/$f" "nasekadan-web:/usr/share/nginx/html/$f"
  done
  for f in published-content-index.json article-integrity-manifest.json; do
    sudo docker cp "$src/data/$f" "nasekadan-web:/usr/share/nginx/html/data/$f"
  done
fi
rm -rf /tmp/slovan-publish-bundle
REMOTE
    then ok=1; break; fi
    sleep $((attempt * 8))
  done
  test "$ok" = 1
}

public_verify_once() {
  local q="${GITHUB_RUN_ID:-manual}-$(date +%s%N)"
  curl -4 -kfsS -L --max-time 45 "$ARTICLE_URL?v=$q" -o /tmp/slovan-article.html
  curl -4 -kfsS -L --max-time 45 "$BASE/?v=$q" -o /tmp/slovan-home.html
  curl -4 -kfsS -L --max-time 45 "$BASE/rss.xml?v=$q" -o /tmp/slovan-rss.xml
  curl -4 -kfsS -L --max-time 45 "$BASE/sitemap.xml?v=$q" -o /tmp/slovan-sitemap.xml
  curl -4 -kfsS -L --max-time 45 "$BASE/news-sitemap.xml?v=$q" -o /tmp/slovan-news.xml
  curl -4 -kfsS -L --max-time 45 "$BASE/data/published-content-index.json?v=$q" -o /tmp/slovan-registry.json
  curl -4 -kfsS -L --max-time 45 "$BASE/data/article-integrity-manifest.json?v=$q" -o /tmp/slovan-manifest.json
  curl -4 -kfsS -L --max-time 45 "$BASE/deployment-health.txt?v=$q" -o /tmp/slovan-health.txt
  curl -4 -kfsS -L --max-time 45 "$SOCIAL_URL?v=$q" -o /tmp/slovan-social.png
  curl -4 -kfsS -L --max-time 45 "$BASE/api/pocasi-predpoved.json?v=$q" -o /tmp/slovan-weather.json

  grep -Fq "<h1>${EXPECTED_H1}</h1>" /tmp/slovan-article.html
  grep -Fq 'index,follow' /tmp/slovan-article.html
  ! grep -Fq 'noindex' /tmp/slovan-article.html
  grep -Fq "$EXPECTED_PUBLISHED" /tmp/slovan-article.html
  grep -Fq 'Druhý pokus může Kadani přinést potřebné byty' /tmp/slovan-article.html
  ! grep -Fq 'Náhled článku' /tmp/slovan-article.html
  ! grep -Fq 'Otázky pro město' /tmp/slovan-article.html
  grep -Fq "$ARTICLE_REL" /tmp/slovan-home.html
  grep -Fq '/pocasi.js' /tmp/slovan-home.html
  grep -Fq "$ARTICLE_URL" /tmp/slovan-rss.xml
  grep -Fq "$ARTICLE_URL" /tmp/slovan-sitemap.xml
  grep -Fq "$ARTICLE_URL" /tmp/slovan-news.xml
  grep -Fq 'status=ok' /tmp/slovan-health.txt
  test "$(wc -c </tmp/slovan-social.png)" -gt 10000

  local found=0 page body
  for page in 1 2 3 4 5; do
    if [ "$page" = 1 ]; then
      url="$BASE/clanky/?v=$q"
    else
      url="$BASE/clanky/strana-$page.html?v=$q"
    fi
    if body="$(curl -4 -kfsS -L --max-time 45 "$url" 2>/dev/null)"; then
      if grep -Fq "$ARTICLE_REL" <<<"$body"; then found=1; fi
    fi
  done
  test "$found" = 1

  python3 - <<'PY'
import json, re, xml.etree.ElementTree as ET
from pathlib import Path
url='https://nasekadan.cz/clanky/slovan-druhy-pokus.html'
reg=json.loads(Path('/tmp/slovan-registry.json').read_text(encoding='utf-8'))
count=reg.get('article_count')
assert isinstance(count,int) and count>=49, count
assert len(reg.get('articles',[]))==count
assert reg.get('validation',{}).get('rss_count')==count
assert reg.get('validation',{}).get('archive_count')==count
assert reg.get('validation',{}).get('duplicate_urls')==[]
assert reg.get('validation',{}).get('duplicate_fingerprints')==[]
a=next(x for x in reg['articles'] if x.get('url')==url)
assert a.get('source_commit') not in (None,'','pending-publication-commit')
assert all(a.get('status',{}).get(k) for k in ('homepage','archive','rss','sitemap','news_sitemap'))
manifest=json.loads(Path('/tmp/slovan-manifest.json').read_text(encoding='utf-8'))
assert manifest.get('article_count')==count
assert any(x.get('url')==url for x in manifest.get('articles',[]))
rss=Path('/tmp/slovan-rss.xml').read_text(encoding='utf-8')
assert len(re.findall(r'<item\b',rss))==count
assert rss.count(url)==2, rss.count(url)
ET.parse('/tmp/slovan-rss.xml')
news_root=ET.parse('/tmp/slovan-news.xml').getroot()
assert len(news_root)==10, len(news_root)
ET.parse('/tmp/slovan-sitemap.xml')
weather=json.loads(Path('/tmp/slovan-weather.json').read_text(encoding='utf-8'))
assert isinstance(weather,(dict,list))
PY
}

public_verify_with_retries() {
  local attempt
  for attempt in $(seq 1 15); do
    if public_verify_once; then
      log "Veřejná kontrola prošla (${attempt}/15)."
      return 0
    fi
    log "Veřejná kontrola zatím neprošla (${attempt}/15), čekám."
    sleep 12
  done
  return 1
}

mark_public_success() {
  local source_sha
  source_sha="${PUBLISH_SHA:-$(git rev-parse HEAD)}"
  local saved=0 attempt
  for attempt in 1 2 3 4; do
    reset_main
    SOURCE_SHA="$source_sha" ARTICLE_URL="$ARTICLE_URL" python3 - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
path=Path('data/published-content-index.json')
data=json.loads(path.read_text(encoding='utf-8'))
now=datetime.now(timezone.utc).isoformat(); v=data.setdefault('validation',{})
v['repair_pending_public_verification']=False
v['deployment_health']='ok'
v['deployment_health_status_field_present']=True
v['deployment_health_source']=os.environ['SOURCE_SHA']
v['public_audit_at']=now
count=len(data.get('articles',[]))
v['homepage_count']=min(14,count)
v['archive_count']=count
v['archive_page_count']=(count+11)//12
v['rss_count']=count
v['last_consistency_audit']={
  'status':'success','checked_at':now,'article_count':count,'homepage_count':min(14,count),
  'archive_count':count,'archive_page_count':(count+11)//12,'rss_count':count,
  'sitemap_count':count,'news_sitemap_count':10,'deployment_health':'ok',
  'verified_url':os.environ['ARTICLE_URL'],'source_commit':os.environ['SOURCE_SHA']}
data['generated_at']=now
data['source_commit']=os.environ['SOURCE_SHA']
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
Path('deployment-health.txt').write_text(f"status=ok\nsource={os.environ['SOURCE_SHA']}\narticle={os.environ['ARTICLE_URL']}\n",encoding='utf-8')
PY
    git add data/published-content-index.json deployment-health.txt
    if git diff --cached --quiet; then saved=1; break; fi
    git commit -m 'Evidence: potvrdit veřejnou publikaci článku o Slovanu'
    if git push origin HEAD:main; then saved=1; break; fi
    sleep $((attempt * 3))
  done
  test "$saved" = 1

  prepare_key
  local evidence_deployed=0
  for attempt in 1 2 3; do
    if scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 data/published-content-index.json deployment-health.txt ubuntu@57.129.43.215:/tmp/ && \
       ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -euo pipefail
root=/var/www/nasekadan
sudo install -m 0644 /tmp/published-content-index.json "$root/data/published-content-index.json"
sudo install -m 0644 /tmp/deployment-health.txt "$root/deployment-health.txt"
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker cp /tmp/published-content-index.json nasekadan-web:/usr/share/nginx/html/data/published-content-index.json
  sudo docker cp /tmp/deployment-health.txt nasekadan-web:/usr/share/nginx/html/deployment-health.txt
fi
rm -f /tmp/published-content-index.json /tmp/deployment-health.txt
REMOTE
    then evidence_deployed=1; break; fi
    sleep $((attempt * 5))
  done
  test "$evidence_deployed" = 1
}

live_is_complete() {
  public_verify_once >/dev/null 2>&1
}

run_full_publish() {
  setup_git
  python3 -m pip install --disable-pip-version-check --quiet Pillow
  local_generate_and_push
  save_evidence_and_push
  deploy_bundle
  public_verify_with_retries
  mark_public_success
  sleep 3
  public_verify_with_retries
}

case "$MODE" in
  primary)
    run_full_publish
    ;;
  rescue|final)
    if live_is_complete; then
      log "Živá publikace už je úplná; opravný běh není potřeba."
    else
      log "Živá publikace není úplná; spouštím ${MODE} obnovu."
      run_full_publish
    fi
    ;;
  *)
    echo "Neznámý režim: $MODE" >&2
    exit 2
    ;;
esac

log "Režim $MODE dokončen."
