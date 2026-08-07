#!/usr/bin/env bash
set -euo pipefail

ROOT="${GITHUB_WORKSPACE:-$(pwd)}"
cd "$ROOT"

LOCK_FILE=/tmp/nasekadan-production-deploy.lock
if command -v sudo >/dev/null 2>&1; then
  sudo touch "$LOCK_FILE"
  sudo chmod a+rw "$LOCK_FILE"
else
  touch "$LOCK_FILE"
  chmod a+rw "$LOCK_FILE"
fi
exec 9>"$LOCK_FILE"
flock -w 900 9

# Vždy pracovat s nejnovější hlavní větví. Statusové commity jsou součástí
# zdrojové verze stejně jako obsahové změny, takže deployment-health může přesně
# potvrdit, jaký commit veřejný web skutečně podává.
git fetch --prune origin main
git reset --hard origin/main
SOURCE_SHA="$(git rev-parse HEAD)"
SHORT_SHA="${SOURCE_SHA:0:12}"

echo "Nasazuji main @ $SOURCE_SHA"

if [[ -f deploy/repair-newsletter-smtp.sh ]]; then
  chmod +x deploy/repair-newsletter-smtp.sh
  bash deploy/repair-newsletter-smtp.sh
fi

# Předprodukční ochrany. Jde o stejné idempotentní kroky pro ruční deploy,
# GitHub workflow i desetiminutovou serverovou pojistku.
python3 scripts/ensure_publication_integrity.py
python3 scripts/ensure_newest_article_indexes.py
python3 scripts/publish_avies_article.py
python3 scripts/ensure_petition_document_details.py
python3 scripts/finalize_launch.py
python3 scripts/normalize_footers.py --write --check
# Sjednotit také článek, sidebar a společný balík dynamických reklam ještě před
# blokující integritní kontrolou. Docker build stejný krok zopakuje idempotentně,
# ale syrový main nesmí selhat dříve jen kvůli chybějícímu site.js.
python3 scripts/normalize_articles.py --write --check
python3 scripts/enable_heat_feed.py
python3 scripts/sort_articles_chronologically.py
python3 scripts/validate_publication_integrity.py

KTK_PATH='/clanky/vypadek-internetu-kadan-kradez-kabelu.html'
KTK_FILE="clanky/vypadek-internetu-kadan-kradez-kabelu.html"
KTK_TITLE="$(python3 - <<'PY'
from html import unescape
from pathlib import Path
import re
text = Path('clanky/vypadek-internetu-kadan-kradez-kabelu.html').read_text(encoding='utf-8')
match = re.search(r'<h1\b[^>]*>(.*?)</h1>', text, re.I | re.S)
if not match:
    raise SystemExit('Článek KTK nemá nadpis H1.')
plain = re.sub(r'<[^>]+>', ' ', match.group(1))
print(re.sub(r'\s+', ' ', unescape(plain)).strip())
PY
)"
KTK_MODIFIED="$(python3 - <<'PY'
from pathlib import Path
import json
import re
text = Path('clanky/vypadek-internetu-kadan-kradez-kabelu.html').read_text(encoding='utf-8')
pattern = r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
value = ''
for raw in re.findall(pattern, text, re.I | re.S):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        continue
    nodes = [data] if isinstance(data, dict) else []
    if isinstance(data, dict) and isinstance(data.get('@graph'), list):
        nodes.extend(node for node in data['@graph'] if isinstance(node, dict))
    for node in nodes:
        kind = node.get('@type')
        kinds = {kind} if isinstance(kind, str) else set(kind or [])
        if 'NewsArticle' in kinds:
            value = str(node.get('dateModified', ''))
            break
    if value:
        break
print(value)
PY
)"
# Archiv je stránkovaný, proto už nelze předpokládat, že starší kontrolní článek
# musí být na první stránce /clanky/. Určíme jeho skutečnou kanonickou stránku
# přímo ze zdrojového archivu a tu pak ověříme v kontejneru i na veřejném webu.
KTK_ARCHIVE_PATH="$(python3 - <<'PY'
from pathlib import Path
import re

target = 'clanky/vypadek-internetu-kadan-kradez-kabelu.html'
root = Path('clanky')
paths = [root / 'index.html']
numbered = []
for path in root.glob('strana-*.html'):
    match = re.fullmatch(r'strana-(\d+)\.html', path.name)
    if match:
        numbered.append((int(match.group(1)), path))
paths.extend(path for _, path in sorted(numbered))
for path in paths:
    if target in path.read_text(encoding='utf-8'):
        print('/clanky/' if path.name == 'index.html' else f'/clanky/{path.name}')
        break
else:
    raise SystemExit('Článek KTK nebyl nalezen v žádné stránce kanonického archivu.')
PY
)"
test -n "$KTK_TITLE"
test -n "$KTK_ARCHIVE_PATH"

cat > deployment-health.txt <<EOF
site=nasekadan.cz
source=$SOURCE_SHA
generated=$(date -u +%FT%TZ)
mode=canonical-ovh
EOF

DOCKER_CONFIG="/tmp/nasekadan-docker-config-$(id -u)"
export DOCKER_CONFIG
mkdir -p "$DOCKER_CONFIG/buildx"
chmod -R u+rwX "$DOCKER_CONFIG"
rm -f "$DOCKER_CONFIG/buildx/lock"

IMAGE="nasekadan-web:$SOURCE_SHA"
docker build --pull -t "$IMAGE" .
docker rm -f nasekadan-web 2>/dev/null || true
docker run -d \
  --name nasekadan-web \
  --restart unless-stopped \
  -p 127.0.0.1:3224:80 \
  "$IMAGE" >/dev/null

for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:3224/healthz >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS http://127.0.0.1:3224/healthz >/dev/null

# Veřejný nginx obsluhuje statický document root, zatímco meteorologická data
# poskytuje interní kontejner. Instalace je idempotentní a proběhne také při
# desetiminutové serverové pojistce, takže počasí nezávisí na GitHub runneru.
if [[ -f deploy/install-weather-proxy.sh ]]; then
  chmod +x deploy/install-weather-proxy.sh
  sudo bash deploy/install-weather-proxy.sh
fi

verify_contains() {
  local url="$1"
  local needle="$2"
  local label="$3"
  local tmp
  tmp="$(mktemp)"
  if ! curl -kfsS --max-time 25 "$url" -o "$tmp"; then
    echo "Kontrola selhala: nelze načíst $label ($url)." >&2
    rm -f "$tmp"
    return 1
  fi
  if ! grep -Fq "$needle" "$tmp"; then
    echo "Kontrola selhala: $label neobsahuje očekávanou aktuální hodnotu: $needle" >&2
    rm -f "$tmp"
    return 1
  fi
  rm -f "$tmp"
}

verify_current_site() {
  local base="$1"
  local label="$2"
  local suffix="?deploy=$SOURCE_SHA"

  # Titulní strana se ověřuje jako funkční stránka současného webu. Starší článek
  # KTK na ní nemusí zůstat navždy, jakmile jej chronologicky odsunou nové texty.
  verify_contains "${base}/${suffix}" 'data-site-footer="v1"' "$label – titulní stránka"

  # Archiv je stránkovaný. Ověříme navigaci z první stránky a KTK na té stránce,
  # na které se podle aktuálního kanonického zdroje skutečně nachází.
  if [[ -f clanky/strana-2.html ]]; then
    verify_contains "${base}/clanky/${suffix}" 'href="/clanky/strana-2.html"' "$label – navigace stránkování archivu"
  fi
  verify_contains "${base}${KTK_ARCHIVE_PATH}${suffix}" "$KTK_FILE" "$label – stránkovaný archiv"
  verify_contains "${base}${KTK_PATH}${suffix}" "$KTK_TITLE" "$label – článek KTK / H1"
  if [[ -n "$KTK_MODIFIED" ]]; then
    verify_contains "${base}${KTK_PATH}${suffix}" "$KTK_MODIFIED" "$label – článek KTK / dateModified"
  fi
  verify_contains "${base}/sitemap.xml${suffix}" "$KTK_FILE" "$label – sitemap"
  verify_contains "${base}/rss.xml${suffix}" "$KTK_FILE" "$label – RSS"
  verify_contains "${base}/deployment-health.txt${suffix}" "source=$SOURCE_SHA" "$label – deployment-health"

  echo "Ověřeno: $label; stránkování archivu, KTK H1/dateModified, RSS, sitemap a source commit jsou aktuální."
}

# Nejdřív ověřit právě sestavený kontejner. Vadný build nesmí vstoupit do
# aktivního document rootu.
verify_current_site 'http://127.0.0.1:3224' 'produkční kontejner'

STAGE="/var/www/nasekadan.release-$SOURCE_SHA"
PREVIOUS="/var/www/nasekadan.previous-$SOURCE_SHA"
BUILT="/tmp/nasekadan-built-$SHORT_SHA"
sudo rm -rf "$STAGE" "$PREVIOUS" "$BUILT"
sudo mkdir -p "$STAGE"
docker cp nasekadan-web:/usr/share/nginx/html/. "$BUILT"
sudo cp -a "$BUILT"/. "$STAGE"/
sudo rm -rf "$BUILT"
printf 'site=nasekadan.cz\nsource=%s\ngenerated=%s\nmode=canonical-ovh\n' \
  "$SOURCE_SHA" "$(date -u +%FT%TZ)" | sudo tee "$STAGE/deployment-health.txt" >/dev/null
sudo chmod -R a+rX "$STAGE"

if [[ -e /var/www/nasekadan ]]; then
  sudo mv /var/www/nasekadan "$PREVIOUS"
fi
sudo mv "$STAGE" /var/www/nasekadan

rollback() {
  local code=$?
  if [[ $code -ne 0 && -e "$PREVIOUS" ]]; then
    echo 'Veřejná kontrola selhala; vracím předchozí ověřený document root.' >&2
    sudo rm -rf /var/www/nasekadan
    sudo mv "$PREVIOUS" /var/www/nasekadan
  fi
  exit "$code"
}
trap rollback EXIT

PUBLIC_BASE=''
if curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  "https://nasekadan.cz/deployment-health.txt?deploy=$SOURCE_SHA" \
  | grep -Fq "source=$SOURCE_SHA"; then
  PUBLIC_BASE='https://nasekadan.cz'
  CURL_RESOLVE=(--resolve nasekadan.cz:443:127.0.0.1)
elif curl -fsS --max-time 10 --resolve nasekadan.cz:80:127.0.0.1 \
  "http://nasekadan.cz/deployment-health.txt?deploy=$SOURCE_SHA" \
  | grep -Fq "source=$SOURCE_SHA"; then
  PUBLIC_BASE='http://nasekadan.cz'
  CURL_RESOLVE=(--resolve nasekadan.cz:80:127.0.0.1)
else
  echo 'Veřejný frontend nepodává právě nasazenou verzi.' >&2
  exit 1
fi

verify_public_contains() {
  local path="$1"
  local needle="$2"
  local label="$3"
  local tmp
  tmp="$(mktemp)"
  if ! curl -kfsS --max-time 25 "${CURL_RESOLVE[@]}" \
    "${PUBLIC_BASE}${path}?deploy=${SOURCE_SHA}" -o "$tmp"; then
    echo "Veřejná kontrola selhala: nelze načíst $label." >&2
    rm -f "$tmp"
    return 1
  fi
  if ! grep -Fq "$needle" "$tmp"; then
    echo "Veřejná kontrola selhala: $label neobsahuje očekávanou aktuální hodnotu: $needle" >&2
    rm -f "$tmp"
    return 1
  fi
  rm -f "$tmp"
}

verify_public_contains '/' 'data-site-footer="v1"' 'titulní stránka'
if [[ -f clanky/strana-2.html ]]; then
  verify_public_contains '/clanky/' 'href="/clanky/strana-2.html"' 'navigace stránkování archivu'
fi
verify_public_contains "$KTK_ARCHIVE_PATH" "$KTK_FILE" 'stránkovaný archiv článků'
verify_public_contains "$KTK_PATH" "$KTK_TITLE" 'článek KTK / H1'
if [[ -n "$KTK_MODIFIED" ]]; then
  verify_public_contains "$KTK_PATH" "$KTK_MODIFIED" 'článek KTK / dateModified'
fi
verify_public_contains '/sitemap.xml' "$KTK_FILE" 'sitemap'
verify_public_contains '/rss.xml' "$KTK_FILE" 'RSS'
verify_public_contains '/deployment-health.txt' "source=$SOURCE_SHA" 'deployment-health'

sudo rm -rf "$PREVIOUS"
trap - EXIT

if [[ "${NASEKADAN_SKIP_AUTOMATION_INSTALL:-0}" != "1" ]]; then
  if [[ -d /opt/nasekadan/.git ]]; then
    sudo bash deploy/install-automation.sh
  else
    echo 'Upozornění: /opt/nasekadan není git checkout; lokální timer nebyl přeinstalován.' >&2
  fi
else
  echo 'Instalace serverového timeru přeskočena: tento deploy spustila samotná serverová pojistka.'
fi

echo "HOTOVO: veřejný web podává main @ $SOURCE_SHA; stránkování archivu, KTK H1/dateModified, RSS, sitemap a deployment-health jsou ověřené."
