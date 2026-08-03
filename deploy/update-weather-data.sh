#!/usr/bin/env bash
set -euo pipefail

ROOT="/var/www/nasekadan"
FORECAST_TARGET="$ROOT/api/pocasi-predpoved.json"
CHMI_DIR="$ROOT/api/chmi-pocasi"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

log() {
  printf '[pocasi] %s\n' "$*"
}

validate_forecast() {
  python3 - "$1" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as handle:
    data = json.load(handle)
series = data.get('properties', {}).get('timeseries', [])
if not isinstance(series, list) or len(series) < 24:
    raise SystemExit('Předpověď neobsahuje alespoň 24 časových kroků.')
PY
}

validate_chmi() {
  python3 - "$1" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as handle:
    data = json.load(handle)
if not isinstance(data, dict) or not data:
    raise SystemExit('Soubor ČHMÚ je prázdný nebo neplatný.')
PY
}

sudo mkdir -p "$CHMI_DIR"

forecast_tmp="$TMP/predpoved.json"
if curl -fLsS --compressed --retry 3 --retry-delay 2 --connect-timeout 15 --max-time 90 \
  -A 'nasekadan.cz info@nasekadan.cz' \
  'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=50.3760&lon=13.2713&altitude=300' \
  -o "$forecast_tmp" && validate_forecast "$forecast_tmp"; then
  sudo install -m 0644 "$forecast_tmp" "$FORECAST_TARGET"
  log 'Bodová předpověď pro Kadaň byla aktualizována.'
else
  if [[ -s "$FORECAST_TARGET" ]] && validate_forecast "$FORECAST_TARGET"; then
    log 'Zdroj předpovědi je nedostupný; ponechávám poslední platnou kopii.'
  else
    echo 'Nelze získat ani zachovat platnou předpověď.' >&2
    exit 41
  fi
fi

chmi_ok=false
for offset in 0 -1; do
  day="$(TZ=Europe/Prague date -d "$offset day" +%Y%m%d)"
  name="10m-0-20000-0-11438-${day}.json"
  tmp_file="$TMP/$name"
  target="$CHMI_DIR/$name"
  if curl -fLsS --compressed --retry 3 --retry-delay 2 --connect-timeout 15 --max-time 90 \
    -A 'nasekadan.cz info@nasekadan.cz' \
    "https://opendata.chmi.cz/meteorology/climate/now/data/$name" \
    -o "$tmp_file" && validate_chmi "$tmp_file"; then
    sudo install -m 0644 "$tmp_file" "$target"
    chmi_ok=true
    log "Měření ČHMÚ Tušimice $day bylo aktualizováno."
  elif [[ -s "$target" ]] && validate_chmi "$target"; then
    chmi_ok=true
    log "Pro $day ponechávám poslední platné měření ČHMÚ."
  fi
done

if [[ "$chmi_ok" != true ]]; then
  echo 'Není dostupná žádná platná kopie měření ČHMÚ Tušimice.' >&2
  exit 42
fi

# Držet pouze několik posledních denních souborů.
sudo find "$CHMI_DIR" -maxdepth 1 -type f -name '10m-0-20000-0-11438-*.json' -mtime +3 -delete

cid="$(sudo docker ps --filter name=^/nasekadan-web$ -q | head -n1)"
if [[ -z "$cid" ]]; then
  cid="$(sudo docker ps --filter publish=3224 -q | head -n1)"
fi
if [[ -z "$cid" ]]; then
  echo 'Běžící kontejner Naše Kadaň nebyl nalezen.' >&2
  exit 43
fi

sudo docker exec "$cid" mkdir -p /usr/share/nginx/html/api/chmi-pocasi
sudo docker cp "$FORECAST_TARGET" "$cid:/usr/share/nginx/html/api/pocasi-predpoved.json"
for file in "$CHMI_DIR"/10m-0-20000-0-11438-*.json; do
  [[ -f "$file" ]] || continue
  sudo docker cp "$file" "$cid:/usr/share/nginx/html/api/chmi-pocasi/$(basename "$file")"
done

sudo docker exec "$cid" test -s /usr/share/nginx/html/api/pocasi-predpoved.json
log 'Statická meteorologická data jsou připravena pro veřejný web.'
