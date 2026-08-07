#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/nasekadan"
ROOT="/var/www/nasekadan"
PRODUCTION_LOCK="/tmp/nasekadan-production-deploy.lock"

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "Chybí $APP_DIR/.git – nejdřív nasaďte repozitář." >&2
  exit 1
fi

sudo touch "$PRODUCTION_LOCK"
sudo chmod a+rw "$PRODUCTION_LOCK"

# ---------------------------------------------------------------------------
# ÚPLNÁ STATICKÁ OBNOVA Z AKTUÁLNÍHO MAIN
# ---------------------------------------------------------------------------
# Jediný účel: veřejný web nesmí přijít o článek, který je v aktuálním main
# skutečně publikovaný. Budoucí a výslovně neveřejné texty se nekopírují.
sudo tee /usr/local/sbin/nasekadan-static-restore >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/nasekadan"
ROOT="/var/www/nasekadan"
LOCK_FILE="/tmp/nasekadan-production-deploy.lock"

exec 9>"$LOCK_FILE"
flock -w 600 9

[[ -d "$APP_DIR/.git" ]] || { echo "Chybí $APP_DIR/.git" >&2; exit 1; }
chown -R ubuntu:ubuntu "$APP_DIR"
rm -f "$APP_DIR/.git/index.lock"
su - ubuntu -c "git -C '$APP_DIR' fetch --prune origin main"
su - ubuntu -c "git -C '$APP_DIR' reset --hard origin/main"
su - ubuntu -c "git -C '$APP_DIR' clean -fd"
cd "$APP_DIR"
SOURCE_SHA="$(git rev-parse HEAD)"

# Explicitně neveřejné soubory se nejdřív odstraní. Následující manifest navíc
# ignoruje noindex a budoucí publication_time, takže je obnova nemůže zveřejnit.
python3 scripts/remove_unpublished_articles.py

# Všechny přehledy se vždy znovu generují ze skutečných článkových souborů.
python3 scripts/enforce_all_article_visibility.py
python3 scripts/ensure_all_published_articles_in_rss.py
python3 scripts/sort_articles_chronologically.py
python3 scripts/enforce_latest_homepage_hero.py

# Když je Pillow dostupný, zároveň se obnoví jedinečné lokální Facebook karty.
# Pokud není, už existující karty z main se stejně kopírují; Docker build má
# generování i kontrolu karet povinné.
if python3 -c 'import PIL' >/dev/null 2>&1; then
  python3 scripts/generate_social_cards.py --write --check
fi

# Statická záchranná obnova nesmí být blokovaná starými SEO nálezy jiných článků.
NASEKADAN_AUDIT_PATHS='clanky/__none__.html' python3 scripts/finalize_launch.py

# Vytvořit kanonický manifest právě publikovaných článků a ověřit zdrojové plochy.
python3 scripts/verify_published_article_set.py \
  --source "$APP_DIR" --target "$APP_DIR" \
  --write-manifest "$APP_DIR/published-articles-manifest.json"

install -d -m 0755 "$ROOT" "$ROOT/clanky"

# Do veřejného document rootu kopírovat POUZE články z manifestu. Tím se při
# opravě nemůže předčasně objevit budoucí článek ani výslovně neveřejný soubor.
python3 - "$APP_DIR" "$ROOT" <<'PY'
from __future__ import annotations
import json, shutil, sys
from pathlib import Path
src = Path(sys.argv[1])
dst = Path(sys.argv[2])
data = json.loads((src / 'published-articles-manifest.json').read_text(encoding='utf-8'))
articles = data['articles']
keep = {Path(rel).name for rel in articles}
(dst / 'clanky').mkdir(parents=True, exist_ok=True)
for old in (dst / 'clanky').glob('*.html'):
    if old.name == 'index.html' or old.name.startswith('strana-'):
        continue
    if old.name not in keep:
        old.unlink(missing_ok=True)
for rel in articles:
    source = src / rel
    target = dst / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
PY

# Archivní stránky vždy kompletně nahradit aktuálně vygenerovanými stránkami.
rm -f "$ROOT"/clanky/strana-*.html
for f in clanky/index.html clanky/strana-*.html; do
  [[ -f "$f" ]] && install -m 0644 "$f" "$ROOT/clanky/$(basename "$f")"
done

for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt published-articles-manifest.json; do
  [[ -f "$f" ]] && install -m 0644 "$f" "$ROOT/$f"
done
for f in ./*.css ./*.js ./*.svg ./*.png ./*.webp ./*.ico; do
  [[ -f "$f" ]] && install -m 0644 "$f" "$ROOT/$(basename "$f")"
done
for dir in social images; do
  if [[ -d "$dir" ]]; then
    mkdir -p "$ROOT/$dir"
    cp -a "$dir"/. "$ROOT/$dir"/
  fi
done

cat > "$ROOT/deployment-health.txt" <<HEALTH
site=nasekadan.cz
status=ok
source=$SOURCE_SHA
generated=$(date -u +%FT%TZ)
mode=monotonic-static-restore
HEALTH
chmod 0644 "$ROOT/deployment-health.txt"

# Blokující kontrola po zápisu. Jediný chybějící článek = neúspěch obnovy.
python3 scripts/verify_published_article_set.py \
  --target "$ROOT" --manifest "$APP_DIR/published-articles-manifest.json"

# Pokud interní nginx kontejner stále drží vlastní statickou kopii, synchronizovat
# do něj stejnou úplnou množinu. Veřejný /var/www root zůstává zdrojem pravdy.
if docker inspect nasekadan-web >/dev/null 2>&1; then
  docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/social /usr/share/nginx/html/images || true
  docker exec nasekadan-web sh -lc 'rm -f /usr/share/nginx/html/clanky/*.html' || true
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    docker cp "$rel" "nasekadan-web:/usr/share/nginx/html/$rel" || true
  done < <(python3 - <<'PY'
import json
print('\n'.join(json.load(open('published-articles-manifest.json', encoding='utf-8'))['articles']))
PY
  )
  for f in clanky/index.html clanky/strana-*.html; do
    [[ -f "$f" ]] && docker cp "$f" "nasekadan-web:/usr/share/nginx/html/clanky/$(basename "$f")" || true
  done
  [[ -d social ]] && docker cp social/. nasekadan-web:/usr/share/nginx/html/social/ || true
  [[ -d images ]] && docker cp images/. nasekadan-web:/usr/share/nginx/html/images/ || true
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt robots.txt published-articles-manifest.json; do
    [[ -f "$f" ]] && docker cp "$f" "nasekadan-web:/usr/share/nginx/html/$f" || true
  done
  docker cp "$ROOT/deployment-health.txt" nasekadan-web:/usr/share/nginx/html/deployment-health.txt || true
fi

echo "Monotónní obnova hotova: main @ $SOURCE_SHA; úplná publikovaná množina zachována."
EOF
sudo chmod 755 /usr/local/sbin/nasekadan-static-restore

# ---------------------------------------------------------------------------
# OKAMŽITÁ REGRESNÍ KONTROLA
# ---------------------------------------------------------------------------
# Očekávaný seznam se čte přímo z origin/main a filtruje se stejnými pravidly:
# noindex a budoucí texty nejsou publikované. Kontrola tedy nepracuje se starou
# titulní stránkou ani se starým ručně udržovaným seznamem.
sudo tee /usr/local/sbin/nasekadan-regression-check >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/nasekadan"
ROOT="/var/www/nasekadan"
CHECK_LOCK="/run/lock/nasekadan-regression-check.lock"
PRODUCTION_LOCK="/tmp/nasekadan-production-deploy.lock"
EXPECTED="/tmp/nasekadan-expected-published.json"

exec 8>"$CHECK_LOCK"
flock -n 8 || exit 0
[[ -d "$APP_DIR/.git" ]] || exit 0

# Git fetch a výpočet očekávaného seznamu proběhne pod stejným produkčním zámkem.
exec 9>"$PRODUCTION_LOCK"
flock -w 120 9
chown -R ubuntu:ubuntu "$APP_DIR"
su - ubuntu -c "git -C '$APP_DIR' fetch --prune origin main" >/dev/null
python3 - "$APP_DIR" "$EXPECTED" <<'PY'
from __future__ import annotations
import json, re, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
repo = Path(sys.argv[1])
out = Path(sys.argv[2])
paths = subprocess.check_output(
    ['git','-C',str(repo),'ls-tree','-r','--name-only','origin/main','--','clanky'],
    text=True,
).splitlines()
now = datetime.now(timezone.utc)
articles=[]
for rel in paths:
    name=Path(rel).name
    if not re.fullmatch(r'clanky/[^/]+\.html', rel):
        continue
    if name == 'index.html' or re.fullmatch(r'strana-\d+\.html', name):
        continue
    try:
        text=subprocess.check_output(['git','-C',str(repo),'show',f'origin/main:{rel}'],text=True)
    except subprocess.CalledProcessError:
        continue
    if 'name="robots"' in text and re.search(r'<meta\b(?=[^>]*name=["\']robots["\'])(?=[^>]*content=["\'][^"\']*noindex)',text,re.I):
        continue
    # Stejný explicitní neveřejný soubor jako remove_unpublished_articles.py.
    if name == 'pozemky-koupaliste-kadan.html':
        continue
    values=[]
    for pat in (
        r'article:published_time["\']\s+content=["\']([^"\']+)',
        r'["\']datePublished["\']\s*:\s*["\']([^"\']+)',
    ):
        m=re.search(pat,text,re.I)
        if m: values.append(m.group(1)); break
    if values:
        try:
            dt=datetime.fromisoformat(values[0].replace('Z','+00:00'))
            if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
            if dt.astimezone(timezone.utc) > now + timedelta(minutes=10):
                continue
        except ValueError:
            pass
    articles.append(rel)
out.write_text(json.dumps({'schema':1,'article_count':len(articles),'articles':sorted(articles)},ensure_ascii=False),encoding='utf-8')
PY
flock -u 9

archive=''
for f in "$ROOT"/clanky/index.html "$ROOT"/clanky/strana-*.html; do
  [[ -f "$f" ]] && archive+="$(cat "$f")"$'\n'
done
rss="$(cat "$ROOT/rss.xml" 2>/dev/null || true)"
sitemap="$(cat "$ROOT/sitemap.xml" 2>/dev/null || true)"

missing=0
while IFS= read -r rel; do
  [[ -n "$rel" ]] || continue
  name="$(basename "$rel")"
  [[ -s "$ROOT/$rel" ]] || { echo "CHYBÍ soubor $rel" >&2; missing=1; }
  grep -Fq "$name" <<<"$archive" || { echo "CHYBÍ v archivu $rel" >&2; missing=1; }
  grep -Fq "$name" <<<"$rss" || { echo "CHYBÍ v RSS $rel" >&2; missing=1; }
  grep -Fq "$name" <<<"$sitemap" || { echo "CHYBÍ v sitemapě $rel" >&2; missing=1; }
done < <(python3 - "$EXPECTED" <<'PY'
import json,sys
print('\n'.join(json.load(open(sys.argv[1],encoding='utf-8'))['articles']))
PY
)

expected_count="$(python3 - "$EXPECTED" <<'PY'
import json,sys
print(json.load(open(sys.argv[1],encoding='utf-8'))['article_count'])
PY
)"

if [[ "$missing" == 0 ]]; then
  echo "Monotónní kontrola OK: $expected_count publikovaných článků z origin/main je zachováno."
  exit 0
fi

echo "Zachycena publikační regrese. Obnovuji úplný aktuální stav z origin/main." >&2
/usr/local/sbin/nasekadan-static-restore
EOF
sudo chmod 755 /usr/local/sbin/nasekadan-regression-check

sudo tee /usr/local/sbin/nasekadan-refresh >/dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
/usr/local/sbin/nasekadan-regression-check
EOF
sudo chmod 755 /usr/local/sbin/nasekadan-refresh

sudo tee /etc/systemd/system/nasekadan-refresh.service >/dev/null <<'EOF'
[Unit]
Description=Periodická kontrola úplnosti článků Naše Kadaň
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-refresh
User=root
TimeoutStartSec=10min
EOF

sudo tee /etc/systemd/system/nasekadan-refresh.timer >/dev/null <<'EOF'
[Unit]
Description=Pravidelná pojistka úplnosti článků Naše Kadaň
[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
RandomizedDelaySec=15
Persistent=true
Unit=nasekadan-refresh.service
[Install]
WantedBy=timers.target
EOF

sudo tee /etc/systemd/system/nasekadan-content-regression.service >/dev/null <<'EOF'
[Unit]
Description=Okamžitá ochrana Naše Kadaň proti zmizení publikovaných článků
After=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-regression-check
User=root
TimeoutStartSec=10min
EOF

sudo tee /etc/systemd/system/nasekadan-content-regression.path >/dev/null <<'EOF'
[Unit]
Description=Sledování publikačních ploch Naše Kadaň
[Path]
PathChanged=/var/www/nasekadan/index.html
PathChanged=/var/www/nasekadan/clanky
PathChanged=/var/www/nasekadan/rss.xml
PathChanged=/var/www/nasekadan/sitemap.xml
PathChanged=/var/www/nasekadan/news-sitemap.xml
Unit=nasekadan-content-regression.service
[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl reset-failed nasekadan-refresh.service nasekadan-content-regression.service || true
sudo systemctl enable --now nasekadan-refresh.timer
sudo systemctl restart nasekadan-refresh.timer
sudo systemctl enable --now nasekadan-content-regression.path
sudo systemctl restart nasekadan-content-regression.path

# Instalace současně okamžitě opraví aktuální rollback a ověří výsledek.
sudo /usr/local/sbin/nasekadan-static-restore
sudo /usr/local/sbin/nasekadan-regression-check

echo "Monotónní ochrana aktivní: publikované články jsou hlídány okamžitě i každých pět minut."
