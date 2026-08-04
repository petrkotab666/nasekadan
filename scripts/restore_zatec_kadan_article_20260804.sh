#!/usr/bin/env bash
set -euo pipefail

SLUG='silnice-zatec-kadan-prejezd-uzavirka-srpen-2026'
ARTICLE_FILE="clanky/${SLUG}.html"
ARTICLE_URL="https://nasekadan.cz/clanky/${SLUG}.html"
SOCIAL_FILE='social/silnice-zatec-kadan-prejezd-uzavirka-srpen-2026-ce0241987f.png'
EXPECTED_H1='Dva přejezdy, dva termíny: silnice Žatec–Kadaň se zavře už 4. srpna'

configure_git() {
  git config user.name 'github-actions[bot]'
  git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
}

patch_sources() {
  python3 <<'PY'
from pathlib import Path

slug = 'silnice-zatec-kadan-prejezd-uzavirka-srpen-2026'
href = f'/clanky/{slug}.html'
title = 'Dva přejezdy, dva termíny: silnice Žatec–Kadaň se zavře už 4. srpna'
desc = 'Úplná uzavírka silnice II/225 začne 4. srpna. Osobní auta pojedou přes Žabokliky, těžší vozidla dlouhou objížďkou přes Pětipsy.'
image = 'https://nasekadan.cz/social/silnice-zatec-kadan-prejezd-uzavirka-srpen-2026-ce0241987f.png'

home = Path('index.html')
text = home.read_text(encoding='utf-8')
marker = f'data-auto-article="{slug}"'
card = f'''    <article class="article-card transport" data-auto-article="{slug}">
      <div class="visual" role="img" aria-label="{title}" style="background-image:linear-gradient(rgba(7,23,34,.04),rgba(7,23,34,.18)),url('{image}');background-color:#0b202b;background-size:contain;background-position:center;background-repeat:no-repeat"></div>
      <div class="article-body"><span class="meta">3. 8. 2026 · 18:35 · DOPRAVA · ŽATEC–KADAŇ</span><h3>{title}</h3><p>{desc}</p><a class="read-more" href="{href}">Přečíst článek →</a></div>
    </article>
'''
if marker not in text:
    anchor = '    <div class="article-list">\n'
    if anchor not in text:
        raise SystemExit('Na titulní stránce chybí seznam článků.')
    text = text.replace(anchor, anchor + card, 1)
    home.write_text(text, encoding='utf-8', newline='\n')

traffic = Path('doprava/index.html')
text = traffic.read_text(encoding='utf-8')
if href not in text:
    block = f'''<section aria-labelledby="aktualni-dopravni-omezeni" style="margin:36px 0"><h2 id="aktualni-dopravni-omezeni" style="font:800 34px/1.15 Georgia,serif">Aktuální dopravní omezení</h2><div class="grid"><article class="card"><p class="tag">ŽATEC–KADAŇ · OD 4. SRPNA 2026</p><h2>{title}</h2><p>{desc}</p><a href="{href}">Přečíst celý článek →</a></article></div></section>'''
    anchor = '<section class="promo-wrap" data-promos data-context="local"></section>'
    if anchor not in text:
        raise SystemExit('Na dopravní stránce chybí bod pro vložení aktuálního článku.')
    text = text.replace(anchor, block + anchor, 1)
    traffic.write_text(text, encoding='utf-8', newline='\n')

required = [
    Path('clanky') / f'{slug}.html',
    Path('clanky/index.html'), Path('rss.xml'), Path('sitemap.xml'),
    Path('news-sitemap.xml'), Path('llms.txt'), Path('data/published-content-index.json')
]
for path in required:
    data = path.read_text(encoding='utf-8')
    if href not in data and f'https://nasekadan.cz{href}' not in data:
        raise SystemExit(f'{path} neobsahuje odkaz na dopravní článek.')
PY
}

configure_git
pushed=0
for attempt in 1 2 3 4 5; do
  git fetch origin main
  git reset --hard origin/main
  patch_sources
  grep -Fq "<h1>${EXPECTED_H1}</h1>" "$ARTICLE_FILE"
  grep -Fq "/clanky/${SLUG}.html" index.html clanky/index.html doprava/index.html
  grep -Fq '/clanky/cisarsky-den-kadan-historie-2026.html' index.html clanky/index.html
  grep -Fq '/pocasi.js' index.html
  test -s "$SOCIAL_FILE"
  git add index.html doprava/index.html
  if git diff --cached --quiet; then
    pushed=1
    break
  fi
  git commit -m 'Vrátit dopravní článek na titulku a do přehledu [skip ci]'
  if git push origin HEAD:main; then
    pushed=1
    break
  fi
  [[ "$attempt" == 5 ]] && exit 1
  sleep $((attempt * 6))
done
test "$pushed" = 1

git fetch origin main
git reset --hard origin/main

key="${OVH_KEY_A:-${OVH_KEY_B:-}}"
test -n "$key"
printf '%s\n' "$key" | tr -d '\r' > "$RUNNER_TEMP/ovh_key"
chmod 600 "$RUNNER_TEMP/ovh_key"

sha="$(git rev-parse HEAD)"
bundle="$RUNNER_TEMP/zatec-kadan-restore"
rm -rf "$bundle"
mkdir -p "$bundle/clanky" "$bundle/doprava" "$bundle/social" "$bundle/data"
cp "$ARTICLE_FILE" "$bundle/clanky/"
cp clanky/index.html "$bundle/clanky/index.html"
cp doprava/index.html "$bundle/doprava/index.html"
cp "$SOCIAL_FILE" "$bundle/social/"
cp index.html rss.xml sitemap.xml news-sitemap.xml llms.txt "$bundle/"
cp data/published-content-index.json "$bundle/data/"
printf 'status=ok\nsource=%s\ndeployer=restore-zatec-kadan-closure-article\narticle=%s\n' "$sha" "$ARTICLE_URL" > "$bundle/deployment-health.txt"

scp -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 -r "$bundle" ubuntu@57.129.43.215:/tmp/zatec-kadan-restore
ssh -i "$RUNNER_TEMP/ovh_key" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 ubuntu@57.129.43.215 'bash -s' <<'REMOTE'
set -euo pipefail
src=/tmp/zatec-kadan-restore
root=/var/www/nasekadan
sudo install -d -m 0755 "$root/clanky" "$root/doprava" "$root/social" "$root/data"
sudo install -m 0644 "$src/clanky/silnice-zatec-kadan-prejezd-uzavirka-srpen-2026.html" "$root/clanky/"
sudo install -m 0644 "$src/clanky/index.html" "$root/clanky/index.html"
sudo install -m 0644 "$src/doprava/index.html" "$root/doprava/index.html"
sudo install -m 0644 "$src/social/silnice-zatec-kadan-prejezd-uzavirka-srpen-2026-ce0241987f.png" "$root/social/"
sudo install -m 0644 "$src/data/published-content-index.json" "$root/data/published-content-index.json"
for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do sudo install -m 0644 "$src/$f" "$root/$f"; done
if sudo docker inspect nasekadan-web >/dev/null 2>&1; then
  sudo docker exec nasekadan-web mkdir -p /usr/share/nginx/html/clanky /usr/share/nginx/html/doprava /usr/share/nginx/html/social /usr/share/nginx/html/data
  sudo docker cp "$src/clanky/silnice-zatec-kadan-prejezd-uzavirka-srpen-2026.html" nasekadan-web:/usr/share/nginx/html/clanky/
  sudo docker cp "$src/clanky/index.html" nasekadan-web:/usr/share/nginx/html/clanky/index.html
  sudo docker cp "$src/doprava/index.html" nasekadan-web:/usr/share/nginx/html/doprava/index.html
  sudo docker cp "$src/social/silnice-zatec-kadan-prejezd-uzavirka-srpen-2026-ce0241987f.png" nasekadan-web:/usr/share/nginx/html/social/
  sudo docker cp "$src/data/published-content-index.json" nasekadan-web:/usr/share/nginx/html/data/published-content-index.json
  for f in index.html rss.xml sitemap.xml news-sitemap.xml llms.txt deployment-health.txt; do sudo docker cp "$src/$f" "nasekadan-web:/usr/share/nginx/html/$f"; done
fi
rm -rf "$src"
REMOTE

stamp="${GITHUB_RUN_ID:-manual}-$(date +%s)"
success=false
for attempt in $(seq 1 20); do
  article="$(curl -4 -kfsS -L --max-time 35 "$ARTICLE_URL?v=$stamp-$attempt" 2>/dev/null || true)"
  home="$(curl -4 -kfsS -L --max-time 35 "https://nasekadan.cz/?v=$stamp-$attempt" 2>/dev/null || true)"
  archive="$(curl -4 -kfsS -L --max-time 35 "https://nasekadan.cz/clanky/?v=$stamp-$attempt" 2>/dev/null || true)"
  traffic="$(curl -4 -kfsS -L --max-time 35 "https://nasekadan.cz/doprava/?v=$stamp-$attempt" 2>/dev/null || true)"
  rss="$(curl -4 -kfsS -L --max-time 35 "https://nasekadan.cz/rss.xml?v=$stamp-$attempt" 2>/dev/null || true)"
  sitemap="$(curl -4 -kfsS -L --max-time 35 "https://nasekadan.cz/sitemap.xml?v=$stamp-$attempt" 2>/dev/null || true)"
  news="$(curl -4 -kfsS -L --max-time 35 "https://nasekadan.cz/news-sitemap.xml?v=$stamp-$attempt" 2>/dev/null || true)"
  if grep -Fq "<h1>${EXPECTED_H1}</h1>" <<<"$article" \
    && ! grep -Fqi 'noindex' <<<"$article" \
    && grep -Fq "/clanky/${SLUG}.html" <<<"$home" \
    && grep -Fq '/clanky/cisarsky-den-kadan-historie-2026.html' <<<"$home" \
    && grep -Fq "/clanky/${SLUG}.html" <<<"$archive" \
    && grep -Fq "/clanky/${SLUG}.html" <<<"$traffic" \
    && grep -Fq "$ARTICLE_URL" <<<"$rss" \
    && grep -Fq "$ARTICLE_URL" <<<"$sitemap" \
    && grep -Fq "$ARTICLE_URL" <<<"$news"; then
    success=true
    break
  fi
  sleep 6
done
test "$success" = true

echo 'Dopravní článek je veřejně dostupný na titulce, v archivu i v sekci Doprava.'
