#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="/opt/nasekadan-stats"
APP_DIR="/usr/local/lib/nasekadan-stats"
SERVICE_FILE="/etc/systemd/system/nasekadan-stats-web.service"
BACKUP_DIR="$BASE_DIR/backups"

set +e
bash "$SCRIPT_DIR/install-stats-v2.sh" "$@"
base_code=$?
set -e

required=(stats_server.py stats_server_v5.py stats_metrics_v5.py stats_server_v6.py stats_metrics_v6.py)
for file in "${required[@]}"; do
  if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
    echo "Chybí $SCRIPT_DIR/$file" >&2
    exit "${base_code:-1}"
  fi
done

install -d -o www-data -g www-data -m 0750 "$BASE_DIR"
install -d -o root -g root -m 0750 "$BACKUP_DIR"
install -d -o root -g root -m 0755 "$APP_DIR"
for file in "${required[@]}"; do
  install -o root -g root -m 0755 "$SCRIPT_DIR/$file" "$APP_DIR/$file"
done
python3 -m py_compile "${required[@]/#/$APP_DIR/}"

if [[ ! -f "$SERVICE_FILE" ]]; then
  echo "Chybí služba $SERVICE_FILE" >&2
  exit 1
fi
sed -Ei \
  's#^ExecStart=/usr/bin/python3 /usr/local/lib/nasekadan-stats/stats_server(_v[0-9]+)?\.py$#ExecStart=/usr/bin/python3 /usr/local/lib/nasekadan-stats/stats_server_v6.py#' \
  "$SERVICE_FILE"
if ! grep -Fq 'ReadWritePaths=/opt/nasekadan-stats' "$SERVICE_FILE"; then
  sed -i '/^ProtectSystem=strict$/a ReadWritePaths=/opt/nasekadan-stats' "$SERVICE_FILE"
fi

cat > /usr/local/sbin/nasekadan-stats-snapshot <<'SCRIPT'
#!/usr/bin/env bash
set -Eeuo pipefail
cd /usr/local/lib/nasekadan-stats
exec sudo -u www-data /usr/bin/python3 - <<'PY'
import json
import sqlite3
import stats_metrics_v5
import stats_metrics_v6
import stats_server as base

stats_metrics_v5.install(base)
stats_metrics_v6.install(base)
body = base.render_dashboard().decode('utf-8', 'replace')
data = stats_metrics_v5.aggregate(base)
for marker in ('Statistiky jednotlivých článků', 'SQLite záloha aktivní', 'Články v přehledu'):
    assert marker in body, marker
assert int(data['total']['views']) >= 2553, data['total']
con = sqlite3.connect('/opt/nasekadan-stats/stats-v6.sqlite3')
assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
article_count = con.execute("SELECT COUNT(*) FROM counters WHERE category='pages' AND label LIKE '/clanky/%.html'").fetchone()[0]
snapshot_count = con.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0]
con.close()
assert article_count > 0, article_count
print(json.dumps({'ok': True, 'total': data['total'], 'articles': article_count, 'snapshots': snapshot_count}, ensure_ascii=False))
PY
SCRIPT
chmod 0755 /usr/local/sbin/nasekadan-stats-snapshot

cat > /usr/local/sbin/nasekadan-stats-backup <<'SCRIPT'
#!/usr/bin/env bash
set -Eeuo pipefail
DB=/opt/nasekadan-stats/stats-v6.sqlite3
DEST=/opt/nasekadan-stats/backups
[[ -s "$DB" ]] || exit 0
install -d -o root -g root -m 0750 "$DEST"
stamp="$(date -u +%Y%m%d-%H%M%S)"
python3 - "$DB" "$DEST/stats-v6-$stamp.sqlite3" <<'PY'
import sqlite3, sys
source, target = sys.argv[1:]
src = sqlite3.connect(f'file:{source}?mode=ro', uri=True)
dst = sqlite3.connect(target)
src.backup(dst)
assert dst.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
dst.close(); src.close()
PY
chmod 0640 "$DEST/stats-v6-$stamp.sqlite3"
find "$DEST" -maxdepth 1 -type f -name 'stats-v6-*.sqlite3' -mtime +180 -delete
SCRIPT
chmod 0755 /usr/local/sbin/nasekadan-stats-backup

cat > /usr/local/sbin/nasekadan-stats-watchdog <<'SCRIPT'
#!/usr/bin/env bash
set -Eeuo pipefail
ok=1
systemctl is-active --quiet nasekadan-stats-web.service || ok=0
curl -fsS --max-time 4 http://127.0.0.1:3225/healthz | grep -Fq '"ok": true' || ok=0
grep -Fq 'reverse_proxy 127.0.0.1:3225' /etc/caddy/sites-enabled/nasekadan.caddy || ok=0
curl -kfsS --max-time 8 --resolve nasekadan.cz:443:127.0.0.1 https://nasekadan.cz/statistiky/ | grep -Fq 'Přihlášení ke statistikám' || ok=0
/usr/local/sbin/nasekadan-stats-snapshot >/tmp/nasekadan-stats-snapshot.json 2>&1 || ok=0
if [[ "$ok" = 1 ]]; then
  exit 0
fi
logger -t nasekadan-stats-watchdog 'Statistiky neprošly kontrolou; spouštím samoopravu.'
cd /opt/nasekadan
git fetch --prune origin main
git reset --hard origin/main
timeout 240 bash .github/scripts/nasekadan-stats/install-stats.sh
SCRIPT
chmod 0755 /usr/local/sbin/nasekadan-stats-watchdog

cat > /etc/systemd/system/nasekadan-stats-snapshot.service <<'UNIT'
[Unit]
Description=Uložit pětiminutový snímek statistik Naše Kadaň
After=nasekadan-stats-web.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-stats-snapshot
Nice=10
UNIT

cat > /etc/systemd/system/nasekadan-stats-snapshot.timer <<'UNIT'
[Unit]
Description=Pravidelný snímek statistik Naše Kadaň

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
AccuracySec=20s
Persistent=true

[Install]
WantedBy=timers.target
UNIT

cat > /etc/systemd/system/nasekadan-stats-backup.service <<'UNIT'
[Unit]
Description=Záloha databáze statistik Naše Kadaň

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-stats-backup
Nice=15
UNIT

cat > /etc/systemd/system/nasekadan-stats-backup.timer <<'UNIT'
[Unit]
Description=Denní záloha databáze statistik Naše Kadaň

[Timer]
OnCalendar=*-*-* 02:15:00
RandomizedDelaySec=10min
Persistent=true

[Install]
WantedBy=timers.target
UNIT

cat > /etc/systemd/system/nasekadan-stats-watchdog.service <<'UNIT'
[Unit]
Description=Samoopravná kontrola statistik Naše Kadaň
After=network-online.target caddy.service nasekadan-stats-web.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/nasekadan-stats-watchdog
Nice=10
UNIT

cat > /etc/systemd/system/nasekadan-stats-watchdog.timer <<'UNIT'
[Unit]
Description=Pravidelná samoopravná kontrola statistik Naše Kadaň

[Timer]
OnBootSec=4min
OnUnitActiveSec=10min
AccuracySec=30s
Persistent=true

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable nasekadan-stats-web.service >/dev/null
systemctl restart nasekadan-stats-web.service
systemctl enable --now \
  nasekadan-stats-snapshot.timer \
  nasekadan-stats-backup.timer \
  nasekadan-stats-watchdog.timer >/dev/null

for _ in $(seq 1 40); do
  if curl -fsS --max-time 3 http://127.0.0.1:3225/healthz >/tmp/nasekadan-stats-health.json 2>/dev/null; then
    break
  fi
  sleep 0.4
done
curl -fsS --max-time 5 http://127.0.0.1:3225/healthz | grep -Fq '"ok": true'

before="$(stat -c %s /var/log/caddy/nasekadan.access.log 2>/dev/null || echo 0)"
curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 \
  -A 'Mozilla/5.0 (compatible; NaseKadanStatsVerification/6.0)' \
  'https://nasekadan.cz/?stats-verification=v6' >/dev/null
sleep 1
after="$(stat -c %s /var/log/caddy/nasekadan.access.log 2>/dev/null || echo 0)"
[[ "$after" -gt "$before" ]] || {
  echo "Kontrolní návštěva se nezapsala do Caddy logu." >&2
  exit 1
}

snapshot_json="$(/usr/local/sbin/nasekadan-stats-snapshot)"
/usr/local/sbin/nasekadan-stats-backup
login="$(curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 https://nasekadan.cz/statistiky/)"
forgot="$(curl -kfsS --max-time 10 --resolve nasekadan.cz:443:127.0.0.1 https://nasekadan.cz/statistiky/zapomenute-heslo)"
grep -Fq 'Zapomenuté heslo' <<<"$login"
grep -Fq 'petrkotab@seznam.cz' <<<"$forgot"

python3 - <<'PY'
import sqlite3
from pathlib import Path
p=Path('/opt/nasekadan-stats/stats-v6.sqlite3')
assert p.stat().st_size > 0
con=sqlite3.connect(p)
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert con.execute("SELECT COUNT(*) FROM counters WHERE category='pages' AND label LIKE '/clanky/%.html'").fetchone()[0] > 0
assert con.execute('SELECT COUNT(*) FROM daily').fetchone()[0] >= 5
con.close()
assert any(Path('/opt/nasekadan-stats/backups').glob('stats-v6-*.sqlite3'))
PY

echo "HOTOVO: trvalé statistiky v6, článkový přehled, pětiminutové snímky, denní zálohy a samoopravný dohled jsou aktivní."
echo "$snapshot_json"
systemctl list-timers --all --no-pager | grep -E 'nasekadan-stats-(snapshot|backup|watchdog)' || true
exit 0
