#!/usr/bin/env python3
from __future__ import annotations

import collections
import csv
import datetime as dt
import hashlib
import html
import io
import json
import os
import re
import sqlite3
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
PORT = 3226
BASE_DIR = Path("/opt/multisite-stats")
DB_PATH = BASE_DIR / "stats.sqlite3"
SALT_PATH = BASE_DIR / "secret-salt"
LOG_PATH = Path("/var/log/nginx/multisite-stats.access.log")
STATE_PATH = BASE_DIR / "collector-state.json"

BOT = re.compile(
    r"bot\b|crawler|spider|slurp|googleinspection|facebookexternalhit|facebot|"
    r"twitterbot|linkedinbot|pinterestbot|whatsapp|telegrambot|discordbot|"
    r"semrush|ahrefs|mj12|dotbot|blexbot|gptbot|chatgpt|claudebot|anthropic|"
    r"perplexity|uptime|monitor|statuscake|pingdom|headless|lighthouse|pagespeed|"
    r"curl/|wget/|python-requests|go-http-client|multisitestatsselftest",
    re.I,
)
STATIC = re.compile(
    r"\.(?:css|js|mjs|jpg|jpeg|png|webp|gif|svg|ico|woff2?|ttf|eot|map|xml|txt|pdf|zip|gz)$",
    re.I,
)
HOST_RE = re.compile(r"^[a-z0-9.-]+(?::\d+)?$", re.I)
DB_LOCK = threading.RLock()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt_num(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def normalize_host(value: str) -> str:
    host = (value or "").strip().lower().split(",", 1)[0].strip()
    if not HOST_RE.match(host):
        return ""
    host = host.split(":", 1)[0].rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    if host in {"localhost", "127.0.0.1", "::1", "_"} or "." not in host:
        return ""
    return host


def read_salt() -> str:
    try:
        return SALT_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return "multisite-stats"


def source_name(ref: str, site_host: str) -> str:
    if not ref or ref == "-":
        return "Přímá návštěva"
    try:
        host = (urllib.parse.urlsplit(ref).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return "Ostatní odkazy"
    if not host:
        return "Ostatní odkazy"
    if host == site_host:
        return "Vnitřní odkazy"
    if "google." in host:
        return "Google"
    if "facebook." in host or host in {"fb.com", "l.facebook.com", "lm.facebook.com"}:
        return "Facebook"
    if "seznam." in host:
        return "Seznam"
    if "bing." in host:
        return "Bing"
    if "instagram." in host:
        return "Instagram"
    return host[:90]


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
    text = text.rsplit("/", 1)[-1]
    text = re.sub(r"\.(?:html?|php)$", "", text, flags=re.I)
    text = text.replace("-", " ").replace("_", " ").strip()
    return text[:1].upper() + text[1:] if text else path


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, timeout=20)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA busy_timeout=20000")
    return con


def init_db() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with DB_LOCK, connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS hits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                host TEXT NOT NULL,
                visitor TEXT NOT NULL,
                path TEXT NOT NULL,
                status INTEGER NOT NULL,
                source TEXT NOT NULL,
                device TEXT NOT NULL,
                browser TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_hits_host_ts ON hits(host, ts);
            CREATE INDEX IF NOT EXISTS idx_hits_host_path_ts ON hits(host, path, ts);
            CREATE INDEX IF NOT EXISTS idx_hits_host_visitor_ts ON hits(host, visitor, ts);
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )


def load_state() -> dict:
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, STATE_PATH)


def parse_line(line: str, salt: str):
    try:
        data = json.loads(line)
        site_host = normalize_host(str(data.get("host", "")))
        method = str(data.get("method", "")).upper()
        ip = str(data.get("ip", ""))
        ua = str(data.get("ua", ""))
        target = str(data.get("uri", "/"))
        status = int(data.get("status", 0))
        ref = str(data.get("ref", ""))
        when = dt.datetime.fromisoformat(str(data.get("ts", "")).replace("Z", "+00:00"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return None
    if not site_host or method not in {"GET", "HEAD"} or not ip:
        return None
    if ip in {"127.0.0.1", "::1"} or BOT.search(ua):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=TZ)
    when = when.astimezone(TZ)
    try:
        path = urllib.parse.urlsplit(target).path or "/"
    except ValueError:
        path = "/"
    path = urllib.parse.unquote(path, errors="replace")
    if path != "/":
        path = path.rstrip("/") or "/"
    if path == "/healthz" or path.startswith("/statistiky") or STATIC.search(path):
        return None
    visitor = hashlib.sha256(f"{salt}\0{ip}\0{ua}".encode("utf-8", "replace")).hexdigest()[:24]
    return (
        int(when.timestamp()),
        site_host,
        visitor,
        path[:1000],
        status,
        source_name(ref, site_host),
        device_name(ua),
        browser_name(ua),
    )


def collector_loop() -> None:
    salt = read_salt()
    state = load_state()
    while True:
        try:
            if not LOG_PATH.exists():
                time.sleep(2)
                continue
            stat = LOG_PATH.stat()
            inode = int(stat.st_ino)
            size = int(stat.st_size)
            old_inode = int(state.get("inode", 0) or 0)
            offset = int(state.get("offset", 0) or 0)
            if inode != old_inode or offset > size:
                offset = 0
            rows = []
            with LOG_PATH.open("r", encoding="utf-8", errors="replace") as handle:
                handle.seek(offset)
                for line in handle:
                    row = parse_line(line, salt)
                    if row:
                        rows.append(row)
                offset = handle.tell()
            if rows:
                with DB_LOCK, connect() as con:
                    con.executemany(
                        "INSERT INTO hits(ts,host,visitor,path,status,source,device,browser) VALUES(?,?,?,?,?,?,?,?)",
                        rows,
                    )
            state = {"inode": inode, "offset": offset, "updated": int(time.time())}
            save_state(state)
        except Exception as exc:
            try:
                (BASE_DIR / "collector-error.log").write_text(
                    f"{dt.datetime.now(TZ).isoformat()} {type(exc).__name__}: {exc}\n",
                    encoding="utf-8",
                )
            except OSError:
                pass
        time.sleep(2)


def period_start(period: str) -> int:
    now = dt.datetime.now(TZ)
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "7":
        start = now - dt.timedelta(days=7)
    elif period == "30":
        start = now - dt.timedelta(days=30)
    elif period == "90":
        start = now - dt.timedelta(days=90)
    else:
        return 0
    return int(start.timestamp())


def metric(con: sqlite3.Connection, sql: str, args: tuple) -> int:
    row = con.execute(sql, args).fetchone()
    return int(row[0] or 0) if row else 0


def rows_counter(con: sqlite3.Connection, field: str, host: str, since: int, limit: int = 12):
    allowed = {"path", "source", "device", "browser", "status"}
    if field not in allowed:
        raise ValueError("unsupported field")
    status_clause = "status IN (200,201,202,203,204,205,206,304)" if field != "status" else "status >= 400"
    return con.execute(
        f"SELECT {field} AS label, COUNT(*) AS amount FROM hits "
        f"WHERE host=? AND ts>=? AND {status_clause} GROUP BY {field} ORDER BY amount DESC LIMIT ?",
        (host, since, limit),
    ).fetchall()


def bars(rows, total: int, pages: bool = False) -> str:
    if not rows:
        return '<p class="empty">Zatím nejsou žádná data.</p>'
    out = []
    for row in rows:
        label = str(row["label"])
        amount = int(row["amount"])
        pct = amount * 100 / total if total else 0
        shown = page_name(label) if pages else label
        small = f"<small>{esc(label)}</small>" if pages and shown != label else ""
        out.append(
            '<div class="barrow">'
            f'<div class="label" title="{esc(label)}"><b>{esc(shown)}</b>{small}</div>'
            f'<div class="track"><span style="width:{max(2.0,pct):.1f}%"></span></div>'
            f'<div class="num">{fmt_num(amount)}</div></div>'
        )
    return "".join(out)


def render_dashboard(host: str) -> bytes:
    now = dt.datetime.now(TZ)
    today_start = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    start7 = int((now - dt.timedelta(days=7)).timestamp())
    start30 = int((now - dt.timedelta(days=30)).timestamp())
    active_start = int((now - dt.timedelta(minutes=30)).timestamp())
    with DB_LOCK, connect() as con:
        ok = "status IN (200,201,202,203,204,205,206,304)"
        total_views = metric(con, f"SELECT COUNT(*) FROM hits WHERE host=? AND {ok}", (host,))
        total_people = metric(con, f"SELECT COUNT(DISTINCT visitor) FROM hits WHERE host=? AND {ok}", (host,))
        today_views = metric(con, f"SELECT COUNT(*) FROM hits WHERE host=? AND ts>=? AND {ok}", (host, today_start))
        today_people = metric(con, f"SELECT COUNT(DISTINCT visitor) FROM hits WHERE host=? AND ts>=? AND {ok}", (host, today_start))
        views7 = metric(con, f"SELECT COUNT(*) FROM hits WHERE host=? AND ts>=? AND {ok}", (host, start7))
        people7 = metric(con, f"SELECT COUNT(DISTINCT visitor) FROM hits WHERE host=? AND ts>=? AND {ok}", (host, start7))
        views30 = metric(con, f"SELECT COUNT(*) FROM hits WHERE host=? AND ts>=? AND {ok}", (host, start30))
        people30 = metric(con, f"SELECT COUNT(DISTINCT visitor) FROM hits WHERE host=? AND ts>=? AND {ok}", (host, start30))
        active = metric(con, f"SELECT COUNT(DISTINCT visitor) FROM hits WHERE host=? AND ts>=? AND {ok}", (host, active_start))
        first_row = con.execute("SELECT MIN(ts) FROM hits WHERE host=?", (host,)).fetchone()
        first = dt.datetime.fromtimestamp(first_row[0], TZ).strftime("%d.%m.%Y") if first_row and first_row[0] else "od dnešního nasazení"

        page_rows = rows_counter(con, "path", host, start30, 12)
        source_rows = rows_counter(con, "source", host, start30, 12)
        device_rows = rows_counter(con, "device", host, start30, 8)
        browser_rows = rows_counter(con, "browser", host, start30, 8)
        error_rows = con.execute(
            "SELECT status, path, COUNT(*) AS amount FROM hits WHERE host=? AND ts>=? AND status>=400 "
            "GROUP BY status,path ORDER BY amount DESC LIMIT 10",
            (host, start30),
        ).fetchall()

        day_rows = con.execute(
            f"SELECT date(ts,'unixepoch','localtime') AS day, COUNT(*) AS views, COUNT(DISTINCT visitor) AS people "
            f"FROM hits WHERE host=? AND ts>=? AND {ok} GROUP BY day ORDER BY day",
            (host, start30),
        ).fetchall()
        daily = {str(r["day"]): (int(r["views"]), int(r["people"])) for r in day_rows}

        latest = con.execute(
            f"SELECT path, COUNT(*) AS views, COUNT(DISTINCT visitor) AS people, MAX(ts) AS last_ts "
            f"FROM hits WHERE host=? AND {ok} GROUP BY path ORDER BY last_ts DESC LIMIT 200",
            (host,),
        ).fetchall()

    maximum = max((v[0] for v in daily.values()), default=1) or 1
    day_html = []
    for i in range(30):
        day = (now.date() - dt.timedelta(days=29-i))
        views, people = daily.get(day.isoformat(), (0, 0))
        height = max(2, round(views * 100 / maximum)) if views else 1
        day_html.append(
            f'<div class="day" title="{day.strftime("%d.%m.%Y")}: {views} zobrazení, {people} návštěvníků">'
            f'<span style="height:{height}%"></span><small>{day.day}</small></div>'
        )

    errors_html = "".join(
        f"<tr><td><b>{int(r['status'])}</b></td><td>{esc(r['path'])}</td><td>{fmt_num(int(r['amount']))}</td></tr>"
        for r in error_rows
    ) or '<tr><td colspan="3" class="empty">Žádné časté chyby.</td></tr>'

    latest_html = "".join(
        f'<tr data-path="{esc(r["path"])}" data-views="{int(r["views"])}" data-people="{int(r["people"])}" data-last="{int(r["last_ts"])}">'
        f'<td><b>{esc(page_name(str(r["path"])))}</b><small>{esc(r["path"])}</small></td>'
        f'<td>{fmt_num(int(r["views"]))}</td><td>{fmt_num(int(r["people"]))}</td>'
        f'<td>{dt.datetime.fromtimestamp(int(r["last_ts"]),TZ).strftime("%d.%m. %H:%M")}</td></tr>'
        for r in latest
    ) or '<tr><td colspan="4" class="empty">Zatím nejsou žádné navštívené stránky.</td></tr>'

    doc = f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Statistiky – {esc(host)}</title>
<style>
:root{{--bg:#f4f1eb;--card:#fff;--text:#20252a;--muted:#6d757d;--accent:#9d3c2d;--line:#e4ded5;--soft:#f8f6f2;--good:#236b32}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1220px;margin:auto;padding:28px 18px 50px}}header{{display:flex;justify-content:space-between;gap:18px;align-items:end;margin-bottom:22px}}
h1{{margin:0;font-size:30px}}header p{{margin:5px 0 0;color:var(--muted)}}.live{{background:#e6f3e8;color:var(--good);padding:7px 11px;border-radius:999px;font-weight:700;white-space:nowrap}}
.cards{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}}.card,.panel{{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:0 4px 18px #4233230a}}
.card{{padding:17px}}.card small{{color:var(--muted);display:block}}.card strong{{display:block;font-size:27px;margin-top:3px}}.card em{{font-style:normal;color:var(--muted);font-size:12px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}}.panel{{padding:20px}}h2{{font-size:18px;margin:0 0 16px}}.chart{{height:190px;display:flex;align-items:end;gap:4px;border-bottom:1px solid var(--line);padding-top:10px}}
.day{{height:100%;flex:1;display:flex;flex-direction:column;justify-content:end;align-items:center;min-width:3px}}.day span{{display:block;width:100%;background:var(--accent);border-radius:4px 4px 0 0;min-height:1px}}.day small{{font-size:9px;color:var(--muted);height:18px;padding-top:3px}}
.barrow{{display:grid;grid-template-columns:minmax(150px,1.5fr) 2fr 56px;gap:10px;align-items:center;margin:10px 0}}.label{{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.label small,td small{{display:block;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.track{{height:8px;background:var(--soft);border-radius:99px;overflow:hidden}}.track span{{display:block;height:100%;background:var(--accent);border-radius:99px}}.num{{text-align:right;font-weight:700}}.empty{{color:var(--muted)}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:10px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}td:nth-child(n+2),th:nth-child(n+2){{text-align:right}}
.toolbar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:-4px 0 14px}}button,select{{border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 10px;font:inherit;cursor:pointer}}button.active{{background:var(--text);color:#fff;border-color:var(--text)}}.wide{{grid-column:1/-1}}footer{{color:var(--muted);margin-top:18px;text-align:center;font-size:13px}}
@media(max-width:900px){{.cards{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}.wide{{grid-column:auto}}}}@media(max-width:520px){{header{{align-items:start;flex-direction:column}}.cards{{grid-template-columns:1fr}}.barrow{{grid-template-columns:minmax(110px,1.2fr) 1fr 45px}}main{{padding:18px 10px 35px}}.panel{{padding:15px}}}}
</style></head><body><main>
<header><div><h1>Statistiky webu {esc(host)}</h1><p>Soukromý přehled návštěvnosti · data od {esc(first)}</p></div><div class="live">● {active} aktivních za 30 min</div></header>
<section class="cards">
<div class="card"><small>Dnes</small><strong>{fmt_num(today_views)}</strong><em>{fmt_num(today_people)} návštěvníků</em></div>
<div class="card"><small>Posledních 7 dní</small><strong>{fmt_num(views7)}</strong><em>{fmt_num(people7)} návštěvníků</em></div>
<div class="card"><small>Posledních 30 dní</small><strong>{fmt_num(views30)}</strong><em>{fmt_num(people30)} návštěvníků</em></div>
<div class="card"><small>Celkem zobrazení</small><strong>{fmt_num(total_views)}</strong><em>od začátku měření</em></div>
<div class="card"><small>Celkem návštěvníků</small><strong>{fmt_num(total_people)}</strong><em>anonymizovaně</em></div>
</section>
<section class="grid">
<div class="panel wide"><h2>Vývoj za posledních 30 dní</h2><div class="chart">{''.join(day_html)}</div></div>
<div class="panel"><h2>Nejnavštěvovanější stránky</h2>{bars(page_rows,views30,True)}</div>
<div class="panel"><h2>Zdroje návštěv</h2>{bars(source_rows,views30)}</div>
<div class="panel"><h2>Zařízení</h2>{bars(device_rows,views30)}</div>
<div class="panel"><h2>Prohlížeče</h2>{bars(browser_rows,views30)}</div>
<div class="panel wide"><h2>Posledních až 200 navštívených stránek</h2>
<div class="toolbar"><button data-limit="25">25</button><button data-limit="50">50</button><button data-limit="100">100</button><button data-limit="200" class="active">200</button>
<select id="page-sort"><option value="last">Nejnovější aktivita</option><option value="views">Nejvíce zobrazení</option><option value="people">Nejvíce návštěvníků</option><option value="name">Název A–Z</option></select>
<button id="page-export">Export CSV</button></div>
<div style="overflow:auto"><table id="pages-200"><thead><tr><th>Stránka</th><th>Zobrazení</th><th>Návštěvníci</th><th>Naposledy</th></tr></thead><tbody>{latest_html}</tbody></table></div></div>
<div class="panel wide"><h2>Nejčastější chyby za 30 dní</h2><div style="overflow:auto"><table><thead><tr><th>Kód</th><th>Adresa</th><th>Počet</th></tr></thead><tbody>{errors_html}</tbody></table></div></div>
</section><footer>Data neobsahují uložené IP adresy. Roboti a technické soubory se nezapočítávají.</footer>
</main><script>
(()=>{{const tbody=document.querySelector('#pages-200 tbody');if(!tbody)return;let limit=200;
const apply=()=>{{const rows=[...tbody.querySelectorAll('tr[data-path]')];const sort=document.querySelector('#page-sort').value;rows.sort((a,b)=>{{if(sort==='name')return a.dataset.path.localeCompare(b.dataset.path,'cs');return Number(b.dataset[sort])-Number(a.dataset[sort]);}});rows.forEach((r,i)=>{{tbody.appendChild(r);r.style.display=i<limit?'':'none';}});}};
document.querySelectorAll('[data-limit]').forEach(b=>b.onclick=()=>{{limit=Number(b.dataset.limit);document.querySelectorAll('[data-limit]').forEach(x=>x.classList.toggle('active',x===b));apply();}});document.querySelector('#page-sort').onchange=apply;
document.querySelector('#page-export').onclick=()=>{{const lines=[['Stránka','Zobrazení','Návštěvníci','Poslední aktivita']];[...tbody.querySelectorAll('tr[data-path]')].filter(r=>r.style.display!=='none').forEach(r=>lines.push([r.dataset.path,r.dataset.views,r.dataset.people,new Date(Number(r.dataset.last)*1000).toISOString()]));const csv=lines.map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(';')).join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\ufeff'+csv],{{type:'text/csv;charset=utf-8'}}));a.download='{esc(host)}-statistiky.csv';a.click();URL.revokeObjectURL(a.href);}};apply();}})();
</script></body></html>'''
    return doc.encode("utf-8")


def export_csv(host: str, period: str) -> bytes:
    since = period_start(period)
    with DB_LOCK, connect() as con:
        rows = con.execute(
            "SELECT datetime(ts,'unixepoch','localtime') AS cas,path,status,source,device,browser "
            "FROM hits WHERE host=? AND ts>=? ORDER BY ts DESC LIMIT 100000",
            (host, since),
        ).fetchall()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Čas", "Stránka", "Stav", "Zdroj", "Zařízení", "Prohlížeč"])
    for row in rows:
        writer.writerow([row["cas"], row["path"], row["status"], row["source"], row["device"], row["browser"]])
    return ("\ufeff" + output.getvalue()).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "MultisiteStats/1.0"

    def log_message(self, fmt: str, *args) -> None:
        return

    def site_host(self) -> str:
        return normalize_host(self.headers.get("X-Stats-Host", ""))

    def send_bytes(self, code: int, body: bytes, content_type: str, extra: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, private")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("X-Content-Type-Options", "nosniff")
        if extra:
            for key, value in extra.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/healthz":
            self.send_bytes(200, b"ok\n", "text/plain; charset=utf-8")
            return
        host = self.site_host()
        if not host:
            self.send_bytes(400, b"Chybi domena webu.\n", "text/plain; charset=utf-8")
            return
        if parsed.path == "/export.csv":
            period = urllib.parse.parse_qs(parsed.query).get("period", ["all"])[0]
            body = export_csv(host, period)
            self.send_bytes(200, body, "text/csv; charset=utf-8", {"Content-Disposition": f'attachment; filename="{host}-statistiky.csv"'})
            return
        if parsed.path not in {"/", ""}:
            self.send_bytes(404, b"Nenalezeno.\n", "text/plain; charset=utf-8")
            return
        self.send_bytes(200, render_dashboard(host), "text/html; charset=utf-8")


def main() -> None:
    init_db()
    threading.Thread(target=collector_loop, name="collector", daemon=True).start()
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
