#!/usr/bin/env bash
set -euo pipefail

ARTICLE_URL='https://nasekadan.cz/clanky/jak-se-kadan-stara-o-hriste-2026.html'
ARTICLE_REL='/clanky/jak-se-kadan-stara-o-hriste-2026.html'
EXPECTED_H1='Jak se Kadaň stará o svá hřiště? Nové prvky, opravy i velké rekonstrukce'
BASE='https://nasekadan.cz'
ISSUE=724

if [[ "${GITHUB_EVENT_NAME:-}" == "schedule" && "$(date -u +%F)" != "2026-08-06" ]]; then
  echo 'Jednorázové publikační okno už není aktivní.'
  exit 0
fi

public_ok() {
  local q article home archive rss sitemap news health registry
  q="hriste-preflight-$(date +%s)"
  article="$(curl -4 -kfsS -L --max-time 25 "$ARTICLE_URL?v=$q" 2>/dev/null || true)"
  home="$(curl -4 -kfsS -L --max-time 25 "$BASE/?v=$q" 2>/dev/null || true)"
  archive="$(curl -4 -kfsS -L --max-time 25 "$BASE/clanky/?v=$q" 2>/dev/null || true)"
  rss="$(curl -4 -kfsS -L --max-time 25 "$BASE/rss.xml?v=$q" 2>/dev/null || true)"
  sitemap="$(curl -4 -kfsS -L --max-time 25 "$BASE/sitemap.xml?v=$q" 2>/dev/null || true)"
  news="$(curl -4 -kfsS -L --max-time 25 "$BASE/news-sitemap.xml?v=$q" 2>/dev/null || true)"
  health="$(curl -4 -kfsS -L --max-time 25 "$BASE/deployment-health.txt?v=$q" 2>/dev/null || true)"
  registry="$(curl -4 -kfsS -L --max-time 25 "$BASE/data/published-content-index.json?v=$q" 2>/dev/null || true)"
  grep -Fq "<h1>${EXPECTED_H1}</h1>" <<<"$article" &&
  grep -Fq '5.4 · Chomutovská u čp. 1229' <<<"$article" &&
  grep -Fq "$ARTICLE_REL" <<<"$home" && grep -Fq "$ARTICLE_REL" <<<"$archive" &&
  grep -Fq "$ARTICLE_URL" <<<"$rss" && grep -Fq "$ARTICLE_URL" <<<"$sitemap" &&
  grep -Fq "$ARTICLE_URL" <<<"$news" && grep -Fq 'status=ok' <<<"$health" &&
  grep -Fq "$ARTICLE_URL" <<<"$registry"
}

if public_ok; then
  gh issue comment "$ISSUE" --body "Záložní kontrola potvrdila, že článek a všechny publikační povrchy jsou v pořádku: ${ARTICLE_URL}." || true
  gh issue close "$ISSUE" --reason completed || true
  exit 0
fi

python3 - <<'PY'
from pathlib import Path
src=Path('scripts/run_publish_jezero_most_20260805.sh').read_text(encoding='utf-8')
replacements={
'jezero-most-patrani-dva-lide-bourka-2026':'jak-se-kadan-stara-o-hriste-2026',
'publish_jezero_most_20260805.py':'publish_kadanska_hriste_20260806.py',
'Na jezeře Most pátrají po dvou lidech. Kvůli bouřce se neměli dostat na břeh':'Jak se Kadaň stará o svá hřiště? Nové prvky, opravy i velké rekonstrukce',
'Proč zprávu přinášíme i v Kadani':'5.4 · Chomutovská u čp. 1229',
'Výsledek pátrání nebyl v době vydání veřejně potvrzen':'4.1 · centrální hřiště na sídlišti E',
'gh issue comment 690':'gh issue comment 724',
'gh issue close 690':'gh issue close 724',
'jezero-most-bundle':'kadanska-hriste-bundle',
'jezero-most.png':'kadanska-hriste.png',
'článku o jezeře Most':'článku o kadaňských hřištích',
'pátrání po dvou lidech na jezeře Most':'přehled kadaňských hřišť a sportovišť',
'Zpráva byla publikována jako samostatný článek s vazbou na čtenáře z Kadaně':'Přehled kadaňských hřišť a sportovišť byl publikován',
}
for old,new in replacements.items():
    src=src.replace(old,new)
Path('/tmp/run-kadanska-hriste.sh').write_text(src,encoding='utf-8')
PY
chmod +x /tmp/run-kadanska-hriste.sh
bash -n /tmp/run-kadanska-hriste.sh
exec /tmp/run-kadanska-hriste.sh
