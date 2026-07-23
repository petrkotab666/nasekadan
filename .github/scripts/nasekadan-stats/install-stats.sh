#!/usr/bin/env bash
set -Eeuo pipefail

BASE_DIR="/opt/nasekadan-stats"
APP_DIR="/usr/local/lib/nasekadan-stats"
LOG_FILE="/var/log/nginx/nasekadan.access.log"
GLOBAL_CONF="/etc/nginx/conf.d/00-nasekadan-statistiky.conf"
SNIPPET="/etc/nginx/snippets/nasekadan-statistiky-server.conf"
AUTH_FILE="/etc/nginx/.nasekadan-stats.htpasswd"
SERVICE_FILE="/etc/systemd/system/nasekadan-stats-web.service"
LOGROTATE_CONF="/etc/logrotate.d/nasekadan-statistiky"

if [[ $(id -u) -ne 0 ]]; then
  echo "Instalace statistik musí běžet přes sudo/root." >&2
  exit 1
fi

for cmd in nginx python3 systemctl curl; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "Na serveru chybí příkaz: $cmd" >&2
    exit 1
  }
done

# Odstranit předchozí nefunkční hlídač konfigurace. Nově je konfigurace
# součástí běžného nasazení webu, takže se už nic dodatečně nevkládá.
systemctl disable --now nasekadan-stats-patch.path >/dev/null 2>&1 || true
systemctl disable --now nasekadan-stats-patch.timer >/dev/null 2>&1 || true
systemctl stop nasekadan-stats-patch.service >/dev/null 2>&1 || true
rm -f \
  /etc/systemd/system/nasekadan-stats-patch.path \
  /etc/systemd/system/nasekadan-stats-patch.timer \
  /etc/systemd/system/nasekadan-stats-patch.service \
  /usr/local/sbin/nasekadan-stats-patch-nginx \
  /usr/local/lib/nasekadan-stats/patch_nginx.py

install -d -m 0755 "$BASE_DIR" "$APP_DIR" /etc/nginx/snippets
if [[ ! -s "$BASE_DIR/secret-salt" ]]; then
  umask 077
  python3 - <<'PY' > "$BASE_DIR/secret-salt"
import secrets
print(secrets.token_hex(32))
PY
fi
chmod 0600 "$BASE_DIR/secret-salt"

cat > "$APP_DIR/stats_server.py" <<'PY'
#!/usr/bin/env python3
from __future__ import annotations

import collections
import datetime as dt
import glob
import gzip
import hashlib
import html
import json
import re
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Prague")
except Exception:
    TZ = dt.timezone(dt.timedelta(hours=2))

HOST = "127.0.0.1"
PORT = 3225
LOG_GLOB = "/var/log/nginx/nasekadan.access.log*"
SALT_FILE = Path("/opt/nasekadan-stats/secret-salt")
BOT = re.compile(
    r"bot\b|crawler|spider|slurp|googleinspection|facebookexternalhit|facebot|"
    r"twitterbot|linkedinbot|pinterestbot|whatsapp|telegrambot|discordbot|"
    r"semrush|ahrefs|mj12|dotbot|blexbot|gptbot|chatgpt|claudebot|anthropic|"
    r"perplexity|uptime|monitor|statuscake|pingdom|headless|lighthouse|pagespeed|"
    r"curl/|wget/|python-requests|go-http-client|nasekadanstatsselftest",
    re.I,
)
STATIC = re.compile(
    r"\.(?:css|js|mjs|jpg|jpeg|png|webp|gif|svg|ico|woff2?|ttf|eot|map|xml|txt)$",
    re.I,
)
CACHE_LOCK = threading.Lock()
CACHE_AT = 0.0
CACHE_BODY = b""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def n(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def read_salt() -> str:
    try:
        return SALT_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "nasekadan"


def iter_lines():
    paths = []
    for name in glob.glob(LOG_GLOB):
        path = Path(name)
        if path.is_file():
            try:
                paths.append((path.stat().st_mtime, path))
            except OSError:
                pass
    for _, path in sorted(paths):
        opener = gzip.open if path.suffix == ".gz" else open
        try:
            with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
                yield from handle
        except (OSError, EOFError):
            continue


def source_name(ref: str) -> str:
    if not ref or ref == "-":
        return "Přímá návštěva"
    try:
        host = (urllib.parse.urlsplit(ref).hostname or "").lower()
    except ValueError:
        return "Ostatní odkazy"
    if host in {"nasekadan.cz", "www.nasekadan.cz"}:
        return "Vnitřní odkazy"
    if "google." in host:
        return "Google"
    if "facebook." in host or host in {"fb.com", "l.facebook.com", "lm.facebook.com"}:
        return "Facebook"
    if "seznam." in host:
        return "Seznam"
    if "bing." in host:
        return "Bing"
    return host.removeprefix("www.") or "Ostatní odkazy"


def device_name(ua: str) -> str:
    low = ua.lower()
    if any(x in low for x in ("ipad", "tablet", "kindle", "silk/")):
        return "Tablet"
    if any(x in low for x in ("mobile", "iphone", "ipod", "android", "windows phone")):
        return "Mobil"
    return "Počítač"


def browser_name(ua: str) -> str:
    low = ua.lower()
    if "edg/" in low:
        return "Edge"
    if "opr/" in low or "opera" in low:
        return "Opera"
    if "firefox/" in low:
        return "Firefox"
    if "chrome/" in low or "crios/" in low:
        return "Chrome"
    if "safari/" in low:
        return "Safari"
    return "Jiný"


def page_name(path: str) -> str:
    if path == "/":
        return "Úvodní stránka"
    text = urllib.parse.unquote(path, errors="replace").strip("/")
    text = text.rsplit("/", 1)[-1].replace("-", " ").replace("_", " ")
    return text[:1].upper() + text[1:] if text else path


def load_records():
    salt = read_salt()
    visits = []
    errors = []
    raw = parsed = 0
    for line in iter_lines():
        raw += 1
        try:
            data = json.loads(line)
            when = dt.datetime.fromisoformat(str(data.get("ts", "")).replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=TZ)
            when = when.astimezone(TZ)
            method = str(data.get("method", "")).upper()
            ip = str(data.get("ip", ""))
            ua = str(data.get("ua", ""))
            target = str(data.get("uri", "/"))
            status = int(data.get("status", 0))
            ref = str(data.get("ref", ""))
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
        parsed += 1
        if method not in {"GET", "HEAD"} or not ip or ip in {"127.0.0.1", "::1"} or BOT.search(ua):
            continue
        try:
            path = urllib.parse.urlsplit(target).path or "/"
        except ValueError:
            path = "/"
        if path != "/":
            path = path.rstrip("/") or "/"
        decoded = urllib.parse.unquote(path, errors="replace")
        if decoded == "/healthz" or decoded.startswith("/statistiky") or STATIC.search(decoded):
            continue
        visitor = hashlib.sha256(f"{salt}\0{ip}\0{ua}".encode("utf-8", "replace")).hexdigest()[:24]
        row = (when, visitor, decoded, status, source_name(ref), device_name(ua), browser_name(ua))
        if 200 <= status < 300 or status == 304:
            visits.append(row)
        elif status >= 400:
            errors.append(row)
    return visits, errors, raw, parsed


def top_rows(counter, total: int, limit: int = 10, page: bool = False) -> str:
    if not counter:
        return '<p class="empty">Zatím nejsou žádná data.</p>'
    out = []
    for label, count in counter.most_common(limit):
        pct = count * 100 / total if total else 0
        shown = page_name(label) if page else label
        extra = f'<small>{esc(label)}</small>' if page and shown != label else ""
        out.append(
            '<div class="barrow">'
            f'<div class="label" title="{esc(label)}"><b>{esc(shown)}</b>{extra}</div>'
            f'<div class="track"><span style="width:{max(2.0, pct):.1f}%"></span></div>'
            f'<div class="num">{n(count)}</div></div>'
        )
    return "".join(out)


def render() -> bytes:
    visits, errors, raw, parsed = load_records()
    now = dt.datetime.now(TZ)
    today = now.date()
    start7 = today - dt.timedelta(days=6)
    start30 = today - dt.timedelta(days=29)
    recent30 = now - dt.timedelta(minutes=30)

    def unique(rows):
        return len({r[1] for r in rows})

    today_rows = [r for r in visits if r[0].date() == today]
    rows7 = [r for r in visits if r[0].date() >= start7]
    rows30 = [r for r in visits if r[0].date() >= start30]
    active = unique([r for r in visits if r[0] >= recent30])
    first = min((r[0] for r in visits), default=None)

    pages = collections.Counter(r[2] for r in rows30)
    sources = collections.Counter(r[4] for r in rows30)
    devices = collections.Counter(r[5] for r in rows30)
    browsers = collections.Counter(r[6] for r in rows30)
    error_counts = collections.Counter((r[3], r[2]) for r in errors if r[0].date() >= start30)

    days = []
    daily = collections.Counter(r[0].date() for r in rows30)
    daily_visitors = collections.defaultdict(set)
    for r in rows30:
        daily_visitors[r[0].date()].add(r[1])
    maximum = max((daily[d] for d in (start30 + dt.timedelta(days=i) for i in range(30))), default=1) or 1
    for i in range(30):
        day = start30 + dt.timedelta(days=i)
        views = daily[day]
        visitors = len(daily_visitors[day])
        height = max(2, round(views * 100 / maximum)) if views else 1
        days.append(
            f'<div class="day" title="{day.strftime("%d.%m.%Y")}: {views} zobrazení, {visitors} návštěvníků">'
            f'<span style="height:{height}%"></span><small>{day.day}</small></div>'
        )

    error_html = "".join(
        f'<tr><td><b>{status}</b></td><td>{esc(path)}</td><td>{n(count)}</td></tr>'
        for (status, path), count in error_counts.most_common(8)
    ) or '<tr><td colspan="3" class="empty">Žádné časté chyby.</td></tr>'

    html_doc = f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Statistiky – Naše Kadaň</title>
<style>
:root{{--bg:#f4f1eb;--card:#fff;--text:#20252a;--muted:#6d757d;--accent:#9d3c2d;--line:#e4ded5;--soft:#f8f6f2}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1180px;margin:auto;padding:28px 18px 50px}}header{{display:flex;justify-content:space-between;gap:18px;align-items:end;margin-bottom:22px}}
h1{{margin:0;font-size:30px}}header p{{margin:5px 0 0;color:var(--muted)}}.live{{background:#e6f3e8;color:#236b32;padding:7px 11px;border-radius:999px;font-weight:700;white-space:nowrap}}
.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}.card,.panel{{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:0 4px 18px #4233230a}}
.card{{padding:17px}}.card small{{color:var(--muted);display:block}}.card strong{{display:block;font-size:28px;margin-top:3px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}}
.panel{{padding:20px}}h2{{font-size:18px;margin:0 0 16px}}.chart{{height:190px;display:flex;align-items:end;gap:4px;border-bottom:1px solid var(--line);padding-top:10px}}
.day{{height:100%;flex:1;display:flex;flex-direction:column;justify-content:end;align-items:center;min-width:0}}.day span{{width:100%;max-width:20px;background:var(--accent);border-radius:4px 4px 0 0;opacity:.82}}.day small{{font-size:9px;color:var(--muted);margin-top:5px}}
.barrow{{display:grid;grid-template-columns:minmax(130px,1.3fr) minmax(90px,2fr) 46px;align-items:center;gap:10px;margin:12px 0}}.label{{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.label small{{display:block;color:var(--muted);overflow:hidden;text-overflow:ellipsis}}
.track{{height:9px;background:#eee9e2;border-radius:99px;overflow:hidden}}.track span{{display:block;height:100%;background:var(--accent);border-radius:99px}}.num{{text-align:right;color:var(--muted)}}
table{{width:100%;border-collapse:collapse}}td{{border-top:1px solid var(--line);padding:9px 6px}}td:last-child{{text-align:right}}.empty{{color:var(--muted)}}footer{{margin-top:18px;color:var(--muted);font-size:13px}}
@media(max-width:850px){{.cards{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}}}@media(max-width:480px){{header{{align-items:start;flex-direction:column}}.cards{{grid-template-columns:1fr 1fr}}.card strong{{font-size:23px}}.barrow{{grid-template-columns:minmax(95px,1fr) minmax(65px,1fr) 38px}}}}
</style></head><body><main>
<header><div><h1>Naše Kadaň – návštěvnost</h1><p>Soukromý přehled ze serverových záznamů, bez analytických cookies.</p></div><div class="live">● právě měří</div></header>
<section class="cards">
<div class="card"><small>Návštěvníci dnes</small><strong>{n(unique(today_rows))}</strong></div>
<div class="card"><small>Zobrazení dnes</small><strong>{n(len(today_rows))}</strong></div>
<div class="card"><small>Návštěvníci za 7 dní</small><strong>{n(unique(rows7))}</strong></div>
<div class="card"><small>Návštěvníci za 30 dní</small><strong>{n(unique(rows30))}</strong></div>
<div class="card"><small>Aktivní za 30 minut</small><strong>{n(active)}</strong></div>
<div class="card"><small>Celkem návštěvníků</small><strong>{n(unique(visits))}</strong></div>
<div class="card"><small>Celkem zobrazení</small><strong>{n(len(visits))}</strong></div>
<div class="card"><small>Měření od</small><strong style="font-size:20px">{first.strftime("%d.%m.%Y") if first else "dneška"}</strong></div>
</section>
<section class="panel" style="margin-top:16px"><h2>Zobrazení stránek – posledních 30 dní</h2><div class="chart">{''.join(days)}</div></section>
<section class="grid"><div class="panel"><h2>Nejčtenější stránky</h2>{top_rows(pages, len(rows30), page=True)}</div><div class="panel"><h2>Odkud návštěvníci přišli</h2>{top_rows(sources, len(rows30))}</div></section>
<section class="grid"><div class="panel"><h2>Zařízení</h2>{top_rows(devices, len(rows30))}</div><div class="panel"><h2>Prohlížeče</h2>{top_rows(browsers, len(rows30))}</div></section>
<section class="panel" style="margin-top:16px"><h2>Nejčastější chyby za 30 dní</h2><table><tbody>{error_html}</tbody></table></section>
<footer>Aktualizováno {now.strftime("%d.%m.%Y %H:%M:%S")} · zpracováno {n(parsed)} z {n(raw)} záznamů · roboti, technické soubory a stránka statistik se nezapočítávají.</footer>
</main></body></html>'''
    return html_doc.encode("utf-8")


def dashboard() -> bytes:
    global CACHE_AT, CACHE_BODY
    now = time.monotonic()
    with CACHE_LOCK:
        if CACHE_BODY and now - CACHE_AT < 3:
            return CACHE_BODY
        CACHE_BODY = render()
        CACHE_AT = now
        return CACHE_BODY


class Handler(BaseHTTPRequestHandler):
    server_version = "NaseKadanStats/3.0"

    def do_HEAD(self):
        self.respond(False)

    def do_GET(self):
        self.respond(True)

    def respond(self, body: bool):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/healthz":
            code, ctype, payload = 200, "text/plain; charset=utf-8", b"ok\n"
        elif path in {"/", "/index.html"}:
            try:
                code, ctype, payload = 200, "text/html; charset=utf-8", dashboard()
            except Exception as exc:
                code, ctype, payload = 500, "text/plain; charset=utf-8", f"Chyba statistik: {exc}\n".encode()
        else:
            code, ctype, payload = 404, "text/plain; charset=utf-8", b"Nenalezeno\n"
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("X-Robots-Tag", "noindex, nofollow,noarchive")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if body:
            self.wfile.write(payload)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
PY
chmod 0755 "$APP_DIR/stats_server.py"
python3 -m py_compile "$APP_DIR/stats_server.py"

# Ve veřejném repozitáři je jen jednosměrný otisk silného hesla.
cat > "$AUTH_FILE" <<'AUTH'
petr:$6$0fYivzmVKD4frCS.$b.4N1tRkqzCtlApstFsa5/jKW8zr7t2cGb90U8hGXJwu9MsuvJ1/uVY0eC7ahYGdlOJDWxPx9fiA48dTRPYPQ/
AUTH
chown root:www-data "$AUTH_FILE"
chmod 0640 "$AUTH_FILE"

cat > "$GLOBAL_CONF" <<'NGINX'
# Naše Kadaň – samostatný JSON log pro soukromé statistiky.
# Kompatibilita se staršími vhosty, které logují přes if=$nasekadan_stats_loggable.
map $request_uri $nasekadan_stats_loggable {
    default 1;
}

log_format nasekadan_stats escape=json
    '{"ts":"$time_iso8601","ip":"$remote_addr","method":"$request_method",'
    '"uri":"$request_uri","status":$status,"bytes":$body_bytes_sent,'
    '"ref":"$http_referer","ua":"$http_user_agent"}';
NGINX

cat > "$SNIPPET" <<'NGINX'
# Naše Kadaň – sběr návštěvnosti a chráněný přehled.
# Zapisujeme všechny požadavky; dashboard následně vyřadí roboty,
# technické soubory, lokální kontroly i samotnou stránku statistik.
access_log /var/log/nginx/nasekadan.access.log nasekadan_stats;

location = /statistiky {
    return 301 /statistiky/;
}

location ^~ /statistiky/ {
    auth_basic "Naše Kadaň – statistiky";
    auth_basic_user_file /etc/nginx/.nasekadan-stats.htpasswd;
    access_log off;
    proxy_pass http://127.0.0.1:3225/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    add_header Cache-Control "no-store, no-cache, must-revalidate" always;
    add_header Pragma "no-cache" always;
    add_header X-Robots-Tag "noindex, nofollow, noarchive" always;
    add_header X-Content-Type-Options "nosniff" always;
}
NGINX

if [[ ! -e "$LOG_FILE" ]]; then
  install -o www-data -g adm -m 0640 /dev/null "$LOG_FILE" 2>/dev/null || {
    touch "$LOG_FILE"
  }
fi
chown www-data:adm "$LOG_FILE" 2>/dev/null || chown www-data:www-data "$LOG_FILE"
chmod 0640 "$LOG_FILE"

cat > "$LOGROTATE_CONF" <<'LOGROTATE'
/var/log/nginx/nasekadan.access.log {
    daily
    rotate 180
    maxsize 20M
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        if [ -s /run/nginx.pid ]; then
            kill -USR1 "$(cat /run/nginx.pid)" 2>/dev/null || true
        fi
    endscript
}
LOGROTATE

cat > "$SERVICE_FILE" <<'UNIT'
[Unit]
Description=Soukromé statistiky webu Naše Kadaň
After=network.target nginx.service
Wants=nginx.service

[Service]
Type=simple
User=www-data
Group=www-data
ExecStart=/usr/bin/python3 /usr/local/lib/nasekadan-stats/stats_server.py
Restart=on-failure
RestartSec=2
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectHome=true
ProtectSystem=strict
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable nasekadan-stats-web.service >/dev/null
systemctl restart nasekadan-stats-web.service

for _ in $(seq 1 30); do
  if curl -fsS --max-time 2 http://127.0.0.1:3225/healthz >/dev/null 2>&1; then
    exit 0
  fi
  sleep 0.3
done

systemctl status nasekadan-stats-web.service --no-pager >&2 || true
journalctl -u nasekadan-stats-web.service -n 40 --no-pager >&2 || true
echo "Služba statistik se nespustila." >&2
exit 1
