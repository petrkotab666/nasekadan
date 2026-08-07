#!/usr/bin/env bash
set -euo pipefail

ARTICLE_REL='/clanky/zzs-kadan-garaz-mycka-2026.html'
ARTICLE_URL='https://nasekadan.cz/clanky/zzs-kadan-garaz-mycka-2026.html'
ARTICLE_FILE='clanky/zzs-kadan-garaz-mycka-2026.html'
SOCIAL_FILE='social/zzs-kadan-garaz-mycka-2026.png'
EXPECTED_H1='Kadaňská záchranka dostane novou garáž a myčku. Kraj stanovil strop 16,5 milionu'
BASE='https://nasekadan.cz'

python -m pip install --disable-pip-version-check --quiet Pillow
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'

pushed=0
for attempt in 1 2 3 4; do
  git fetch origin main
  git reset --hard origin/main
  python3 -m py_compile scripts/publish_zzs_kadan_garaz_mycka_20260807.py
  python3 scripts/publish_zzs_kadan_garaz_mycka_20260807.py

  grep -Fq "<h1>${EXPECTED_H1}</h1>" "$ARTICLE_FILE"
  grep -Fq '16,5 milionu korun bez DPH' "$ARTICLE_FILE"
  grep -Fq 'Design &amp; Build' "$ARTICLE_FILE"
  grep -Fq '049/45R/2026' "$ARTICLE_FILE"
  ! grep -Eiq 'fulltext|OCR|způsob ověření|způsob dohledávání|bez textové vrstvy' "$ARTICLE_FILE"
  grep -Fq "$ARTICLE_REL" index.html clanky/index.html
  grep -Fq "$ARTICLE_URL" rss.xml sitemap.xml news-sitemap.xml llms.txt data/published-content-index.json
  test -s "$SOCIAL_FILE"
  test "$(wc -c <"$SOCIAL_FILE")" -gt 10000
  python3 - <<'PY'
import json, xml.etree.ElementTree as ET
from pathlib import Path
ET.parse('rss.xml')
ET.parse('sitemap.xml')
ET.parse('news-sitemap.xml')
data=json.loads(Path('data/published-content-index.json').read_text(encoding='utf-8'))
assert data['validation']['duplicate_urls'] == []
assert data['validation']['duplicate_fingerprints'] == []
PY
  git diff --check

  git add "$ARTICLE_FILE" "$SOCIAL_FILE" index.html clanky/index.html clanky/strana-*.html rss.xml sitemap.xml news-sitemap.xml llms.txt data/published-content-index.json
  if ! git diff --cached --quiet; then
    git commit -m 'Publikovat: nové zázemí ZZS v Kadani'
  fi
  if git push origin HEAD:main; then
    pushed=1
    break
  fi
  sleep $((attempt * 3))
done
test "$pushed" = 1
publish_sha="$(git rev-parse HEAD)"

saved=0
for attempt in 1 2 3 4; do
  git fetch origin main
  git reset --hard origin/main
  PUBLISH_SHA="$publish_sha" ARTICLE_URL="$ARTICLE_URL" python3 - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
path=Path('data/published-content-index.json')
data=json.loads(path.read_text(encoding='utf-8'))
article=next((x for x in data.get('articles',[]) if x.get('url')==os.environ['ARTICLE_URL']),None)
if article is None:
    raise SystemExit('Článek chybí v registru.')
article['source_commit']=os.environ['PUBLISH_SHA']
data['source_commit']=os.environ['PUBLISH_SHA']
now=datetime.now(timezone.utc).isoformat()
validation=data.setdefault('validation',{})
validation['repair_pending_public_verification']=True
validation['last_consistency_audit']={'status':'pending_public_verification','checked_at':now,'article_count':len(data.get('articles',[])),'updated_url':os.environ['ARTICLE_URL'],'source_commit':os.environ['PUBLISH_SHA']}
data['generated_at']=now
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PY
  printf 'status=ok\nsource=%s\narticle=%s\n' "$publish_sha" "$ARTICLE_URL" > deployment-health.txt
  git add data/published-content-index.json deployment-health.txt
  if ! git diff --cached --quiet; then
    git commit -m 'Evidence: zapsat zdroj publikace článku o ZZS Kadaň'
  fi
  if git push origin HEAD:main; then
    saved=1
    break
  fi
  sleep $((attempt * 3))
done
test "$saved" = 1

git fetch origin main
git reset --hard origin/main
key="${OVH_KEY_A:-${OVH_KEY_B:-}}"
test -n "$key"
printf '%s\n' "$key" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
chmod 600 "$RUNNER_TEMP/ovh_key"

bundle="$RUNNER_TEMP/zzs-kadan-bundle"
rm -rf "$bundle"
mkdir -p "$bundle/clanky" "$bundle/social" "$bundle/data"
cp "$ARTICLE_FILE" "$bundle/clanky/"
cp clanky/index.html clanky/strana-*.html "$bundle/clanky/"
cp "$SOCIAL_FILE" "$bundle/social/"
cp index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt "$bundle/"
cp data/published-content-index.json "$bundle/data/"
tar -C "$bundle" -czf "$RUNNER_TEMP/zzs-kadan-bundle.tgz" .

scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 "$RUNNER_TEMP/zzs-kadan-bundle.tgz" ubuntu@57.129.43.215:/tmp/zzs-kadan-bundle.tgz
ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -euo pipefail
rm -rf /tmp/zzs-kadan-bundle
mkdir -p /tmp/zzs-kadan-bundle
tar -xzf /tmp/zzs-kadan-bundle.tgz -C /tmp/zzs-kadan-bundle
src=/tmp/zzs-kadan-bundle
root=/var/www/nasekadan
sudo install -m 0666 /dev/null /var/lock/nasekadan-content.lock
exec 9>/var/lock/nasekadan-content.lock
flock -x 9
sudo install -d -m 0755 "$root/clanky" "$root/social" "$root/data"
sudo install -m 0644 "$src/clanky/zzs-kadan-garaz-mycka-2026.html" "$root/clanky/zzs-kadan-garaz-mycka-2026.html"
sudo install -m 0644 "$src/social/zzs-kadan-garaz-mycka-2026.png" "$root/social/zzs-kadan-garaz-mycka-2026.png"
sudo rm -f "$root"/clanky/strana-*.html
for f in "$src"/clanky/index.html "$src"/clanky/strana-*.html; do sudo install -m 0644 "$f" "$root/clanky/$(basename "$f")"; done
for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do sudo install -m 0644 "$src/$f" "$root/$f"; done
sudo install -m 0644 "$src/data/published-content-index.json" "$root/data/published-content-index.json"
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social /usr/share/nginx/html/data
  sudo docker cp "$src/clanky/zzs-kadan-garaz-mycka-2026.html" nasekadan-web:/usr/share/nginx/html/clanky/zzs-kadan-garaz-mycka-2026.html
  sudo docker cp "$src/social/zzs-kadan-garaz-mycka-2026.png" nasekadan-web:/usr/share/nginx/html/social/zzs-kadan-garaz-mycka-2026.png
  sudo docker exec nasekadan-web sh -lc 'rm -f /usr/share/nginx/html/clanky/strana-*.html'
  for f in "$src"/clanky/index.html "$src"/clanky/strana-*.html; do sudo docker cp "$f" "nasekadan-web:/usr/share/nginx/html/clanky/$(basename "$f")"; done
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do sudo docker cp "$src/$f" "nasekadan-web:/usr/share/nginx/html/$f"; done
  sudo docker cp "$src/data/published-content-index.json" nasekadan-web:/usr/share/nginx/html/data/published-content-index.json
fi
rm -rf /tmp/zzs-kadan-bundle /tmp/zzs-kadan-bundle.tgz
REMOTE

sleep 6
q="${GITHUB_RUN_ID:-manual}-$(date +%s)"
article="$(curl -4 -kfsS -L --max-time 40 "$ARTICLE_URL?v=$q")"
home="$(curl -4 -kfsS -L --max-time 40 "$BASE/?v=$q")"
archive="$(curl -4 -kfsS -L --max-time 40 "$BASE/clanky/?v=$q")"
rss="$(curl -4 -kfsS -L --max-time 40 "$BASE/rss.xml?v=$q")"
sitemap="$(curl -4 -kfsS -L --max-time 40 "$BASE/sitemap.xml?v=$q")"
news="$(curl -4 -kfsS -L --max-time 40 "$BASE/news-sitemap.xml?v=$q")"
health="$(curl -4 -kfsS -L --max-time 40 "$BASE/deployment-health.txt?v=$q")"
registry="$(curl -4 -kfsS -L --max-time 40 "$BASE/data/published-content-index.json?v=$q")"

grep -Fq "<h1>${EXPECTED_H1}</h1>" <<<"$article"
grep -Fq '16,5 milionu korun bez DPH' <<<"$article"
grep -Fq 'Design &amp; Build' <<<"$article"
! grep -Eiq 'fulltext|OCR|způsob ověření|způsob dohledávání|bez textové vrstvy' <<<"$article"
grep -Fq "$ARTICLE_REL" <<<"$home"
grep -Fq "$ARTICLE_REL" <<<"$archive"
grep -Fq "$ARTICLE_URL" <<<"$rss"
grep -Fq "$ARTICLE_URL" <<<"$sitemap"
grep -Fq "$ARTICLE_URL" <<<"$news"
grep -Fq 'status=ok' <<<"$health"
printf '%s' "$registry" > /tmp/registry.json
ARTICLE_URL="$ARTICLE_URL" python3 - <<'PY'
import json, os
from pathlib import Path
data=json.loads(Path('/tmp/registry.json').read_text(encoding='utf-8'))
assert data.get('validation',{}).get('duplicate_urls') == []
assert data.get('validation',{}).get('duplicate_fingerprints') == []
article=next(x for x in data['articles'] if x.get('url')==os.environ['ARTICLE_URL'])
assert article.get('source_commit') not in (None,'pending-publication-commit')
assert all(article.get('status',{}).get(k) for k in ('homepage','archive','rss','sitemap','news_sitemap'))
PY
curl -4 -kfsS -L --max-time 40 "$BASE/$SOCIAL_FILE?v=$q" -o /tmp/zzs-kadan.png
test "$(wc -c </tmp/zzs-kadan.png)" -gt 10000

finalized=0
for attempt in 1 2 3 4; do
  git fetch origin main
  git reset --hard origin/main
  SOURCE_SHA="$publish_sha" ARTICLE_URL="$ARTICLE_URL" python3 - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
path=Path('data/published-content-index.json')
data=json.loads(path.read_text(encoding='utf-8'))
now=datetime.now(timezone.utc).isoformat()
validation=data.setdefault('validation',{})
validation['repair_pending_public_verification']=False
validation['deployment_health']='ok'
validation['deployment_health_source']=os.environ['SOURCE_SHA']
validation['public_audit_at']=now
validation['last_consistency_audit']={'status':'success','checked_at':now,'article_count':len(data.get('articles',[])),'homepage_count':validation.get('homepage_count'),'archive_count':validation.get('archive_count'),'archive_page_count':validation.get('archive_page_count'),'rss_count':validation.get('rss_count'),'news_sitemap_count':validation.get('news_sitemap_recent_count'),'deployment_health':'ok','verified_url':os.environ['ARTICLE_URL'],'source_commit':os.environ['SOURCE_SHA']}
data['generated_at']=now
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PY
  git add data/published-content-index.json
  if ! git diff --cached --quiet; then
    git commit -m 'Evidence: potvrdit veřejnou publikaci článku o ZZS Kadaň'
  fi
  if git push origin HEAD:main; then
    finalized=1
    break
  fi
  sleep $((attempt * 3))
done
test "$finalized" = 1

scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 data/published-content-index.json ubuntu@57.129.43.215:/tmp/published-content-index.json
ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 ubuntu@57.129.43.215 'sudo install -m 0644 /tmp/published-content-index.json /var/www/nasekadan/data/published-content-index.json; if sudo docker inspect nasekadan-web >/dev/null 2>&1; then sudo docker cp /tmp/published-content-index.json nasekadan-web:/usr/share/nginx/html/data/published-content-index.json; fi; rm -f /tmp/published-content-index.json'

echo "Článek o ZZS Kadaň byl publikován a veřejně ověřen: $ARTICLE_URL"
