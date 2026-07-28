#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/usr/local/lib/nasekadan-stats"
SERVICE_FILE="/etc/systemd/system/nasekadan-stats-web.service"

set +e
bash "$SCRIPT_DIR/install-stats-v2.sh" "$@"
base_code=$?
set -e

# Vlastní přihlášení a obnova hesla zůstávají v ověřeném serveru. Tato vrstva
# vrací původní podobu přehledu, načítá všechny Caddy rotace a zachovává přesný
# poslední ověřený stav z 25. 7. 2026 jako migrační základ.
if [[ -f "$SCRIPT_DIR/stats_server_v5.py" && -f "$SCRIPT_DIR/stats_metrics_v5.py" ]]; then
  install -d -o root -g root -m 0755 "$APP_DIR"
  install -o root -g root -m 0755 "$SCRIPT_DIR/stats_server.py" "$APP_DIR/stats_server.py"
  install -o root -g root -m 0755 "$SCRIPT_DIR/stats_server_v5.py" "$APP_DIR/stats_server_v5.py"
  install -o root -g root -m 0755 "$SCRIPT_DIR/stats_metrics_v5.py" "$APP_DIR/stats_metrics_v5.py"
  python3 -m py_compile \
    "$APP_DIR/stats_server.py" \
    "$APP_DIR/stats_server_v5.py" \
    "$APP_DIR/stats_metrics_v5.py"

  if [[ -f "$SERVICE_FILE" ]]; then
    sed -i \
      's#^ExecStart=/usr/bin/python3 /usr/local/lib/nasekadan-stats/stats_server\.py$#ExecStart=/usr/bin/python3 /usr/local/lib/nasekadan-stats/stats_server_v5.py#' \
      "$SERVICE_FILE"
  fi

  systemctl daemon-reload
  systemctl restart nasekadan-stats-web.service

  for _ in $(seq 1 40); do
    if curl -fsS --max-time 3 http://127.0.0.1:3225/healthz >/tmp/nasekadan-stats-health.json 2>/dev/null; then
      break
    fi
    sleep 0.4
  done

  cd "$APP_DIR"
  sudo -u www-data python3 - <<'PY'
import json
import stats_metrics_v5
import stats_server as base

stats_metrics_v5.install(base)
data = stats_metrics_v5.aggregate(base)
body = base.render_dashboard().decode("utf-8", "replace")
total = data["total"]
diag = data["diag"]
assert total["views"] >= 2553, total
assert total["visits"] >= 1032, total
assert total["visitors"] >= 915, total
assert diag["files"] >= 5, diag
assert diag["first"] is not None and diag["first"].date().isoformat() == "2026-07-24", diag
for expected in (
    "Počítadlo běží",
    "Online za 5 minut",
    "Načtené logy",
    "Dnešní návštěvnost",
    "Posledních 7 dní",
    "Posledních 30 dní",
    "Celkem v dostupných logách",
    "zobrazení",
    "návštěv",
    "návštěvníků",
):
    assert expected in body, expected
print(json.dumps({
    "ok": True,
    "total": total,
    "loaded_logs": diag["files"],
    "first_record": diag["first"].isoformat(),
    "latest_record": diag["latest"].isoformat() if diag["latest"] else None,
}, ensure_ascii=False))
PY

  health="$(curl -fsS --max-time 5 http://127.0.0.1:3225/healthz 2>/dev/null || true)"
  login="$(curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
    https://nasekadan.cz/statistiky/ 2>/dev/null || true)"
  forgot="$(curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
    https://nasekadan.cz/statistiky/zapomenute-heslo 2>/dev/null || true)"

  if grep -Fq '"ok": true' <<<"$health" \
    && grep -Fq '"auth": "application"' <<<"$health" \
    && grep -Fq 'Zapomenuté heslo' <<<"$login" \
    && grep -Fq 'petrkotab@seznam.cz' <<<"$forgot"; then
    echo "HOTOVO: původní přehled, historický základ, všechny Caddy rotace, přihlášení i obnova hesla jsou ověřené."
    find /var/log/caddy -maxdepth 1 -type f -name 'nasekadan.access*' \
      -printf '%p | %s B | %TY-%Tm-%Td %TH:%TM:%TS\n' 2>/dev/null | sort || true
    exit 0
  fi
fi

health="$(curl -fsS --max-time 5 http://127.0.0.1:3225/healthz 2>/dev/null || true)"
login="$(curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  https://nasekadan.cz/statistiky/ 2>/dev/null || true)"
forgot="$(curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  https://nasekadan.cz/statistiky/zapomenute-heslo 2>/dev/null || true)"
preview_status="$(curl -kisS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  https://nasekadan.cz/nahled/ 2>/dev/null | awk 'NR==1 {print $2}')"

if grep -Fq '"ok": true' <<<"$health" \
  && grep -Fq '"auth": "application"' <<<"$health" \
  && grep -Fq 'Zapomenuté heslo' <<<"$login" \
  && grep -Fq 'petrkotab@seznam.cz' <<<"$forgot" \
  && [[ "$preview_status" =~ ^(401|404|502|503)$ ]]; then
  echo "Základní služba funguje, ale obnovená historická vrstva nebyla potvrzena." >&2
fi

exit "${base_code:-1}"
