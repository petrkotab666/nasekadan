#!/usr/bin/env python3
from __future__ import annotations

import collections
import datetime as dt
import html
import re
import sqlite3
import threading
from pathlib import Path
from typing import Any

import stats_metrics_v5 as legacy

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Prague")
except Exception:
    TZ = dt.timezone(dt.timedelta(hours=2))

DB_PATH = Path("/opt/nasekadan-stats/stats-v6.sqlite3")
DB_LOCK = threading.RLock()
CACHE_LOCK = threading.RLock()
CACHE_AT: dt.datetime | None = None
CACHE_BODY: bytes = b""
CACHE_SECONDS = 20
ARTICLE_RE = re.compile(r"^/clanky/(?!parts/)([^/]+\.html)$", re.I)
STATIC_ARTICLE_ROOTS = (Path("/var/www/nasekadan"), Path("/opt/nasekadan"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}".replace(",", " ").replace(".", ",")
    return f"{int(value):,}".replace(",", " ")


def now_local() -> dt.datetime:
    return dt.datetime.now(TZ)


def normalize_counter(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, int] = {}
    for key, count in value.items():
        try:
            out[str(key)] = max(0, int(count))
        except (TypeError, ValueError):
            continue
    return out


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=20)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=FULL")
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS totals (
            key TEXT PRIMARY KEY,
            value INTEGER NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS daily (
            day TEXT PRIMARY KEY,
            views INTEGER NOT NULL,
            visits INTEGER NOT NULL,
            visitors INTEGER NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS counters (
            category TEXT NOT NULL,
            label TEXT NOT NULL,
            value INTEGER NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(category, label)
        );
        CREATE TABLE IF NOT EXISTS article_titles (
            path TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS snapshots (
            bucket TEXT PRIMARY KEY,
            captured_at TEXT NOT NULL,
            views INTEGER NOT NULL,
            visits INTEGER NOT NULL,
            visitors INTEGER NOT NULL,
            online INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_counters_category_value
            ON counters(category, value DESC);
        CREATE INDEX IF NOT EXISTS idx_snapshots_captured
            ON snapshots(captured_at DESC);
        """
    )
    return con


def upsert_max(con: sqlite3.Connection, table: str, keys: dict[str, object], values: dict[str, int], updated_at: str) -> None:
    columns = [*keys.keys(), *values.keys(), "updated_at"]
    placeholders = ",".join("?" for _ in columns)
    conflict = ",".join(keys.keys())
    assignments = ",".join(
        [f"{name}=MAX({table}.{name}, excluded.{name})" for name in values]
        + ["updated_at=excluded.updated_at"]
    )
    sql = (
        f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders}) "
        f"ON CONFLICT({conflict}) DO UPDATE SET {assignments}"
    )
    con.execute(sql, [*keys.values(), *values.values(), updated_at])


def persist_current(current: dict[str, Any]) -> None:
    stamp = now_local().isoformat()
    total = current.get("total") or {}
    daily = current.get("daily") or {}
    counters = {
        "pages": normalize_counter(current.get("top_pages")),
        "sources": normalize_counter(current.get("sources")),
        "devices": normalize_counter(current.get("devices")),
        "browsers": normalize_counter(current.get("browsers")),
        "errors": normalize_counter(current.get("errors")),
    }
    with DB_LOCK, connect() as con:
        for key in ("views", "visits", "visitors"):
            try:
                value = max(0, int(total.get(key, 0)))
            except (TypeError, ValueError):
                value = 0
            upsert_max(con, "totals", {"key": key}, {"value": value}, stamp)

        if isinstance(daily, dict):
            for day, metrics in daily.items():
                if not isinstance(metrics, dict) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(day)):
                    continue
                values = {}
                for key in ("views", "visits", "visitors"):
                    try:
                        values[key] = max(0, int(metrics.get(key, 0)))
                    except (TypeError, ValueError):
                        values[key] = 0
                upsert_max(con, "daily", {"day": str(day)}, values, stamp)

        for category, data in counters.items():
            for label, value in data.items():
                upsert_max(
                    con,
                    "counters",
                    {"category": category, "label": label},
                    {"value": value},
                    stamp,
                )

        moment = now_local()
        bucket = moment.replace(minute=(moment.minute // 5) * 5, second=0, microsecond=0)
        con.execute(
            """
            INSERT INTO snapshots(bucket, captured_at, views, visits, visitors, online)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(bucket) DO UPDATE SET
              captured_at=excluded.captured_at,
              views=MAX(snapshots.views, excluded.views),
              visits=MAX(snapshots.visits, excluded.visits),
              visitors=MAX(snapshots.visitors, excluded.visitors),
              online=excluded.online
            """,
            (
                bucket.isoformat(), stamp,
                int(total.get("views", 0) or 0),
                int(total.get("visits", 0) or 0),
                int(total.get("visitors", 0) or 0),
                int(current.get("online", 0) or 0),
            ),
        )
        con.execute("DELETE FROM snapshots WHERE captured_at < ?", ((moment - dt.timedelta(days=400)).isoformat(),))
        con.commit()


def read_persisted() -> dict[str, Any]:
    with DB_LOCK, connect() as con:
        totals = {row["key"]: int(row["value"]) for row in con.execute("SELECT key,value FROM totals")}
        daily = {
            row["day"]: {"views": int(row["views"]), "visits": int(row["visits"]), "visitors": int(row["visitors"])}
            for row in con.execute("SELECT day,views,visits,visitors FROM daily ORDER BY day")
        }
        counters: dict[str, dict[str, int]] = collections.defaultdict(dict)
        for row in con.execute("SELECT category,label,value FROM counters"):
            counters[str(row["category"])][str(row["label"])] = int(row["value"])
        snapshots = [dict(row) for row in con.execute(
            "SELECT captured_at,views,visits,visitors,online FROM snapshots ORDER BY captured_at DESC LIMIT 288"
        )]
        snapshot_count = con.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    return {
        "total": totals,
        "daily": daily,
        **counters,
        "snapshots": snapshots,
        "snapshot_count": int(snapshot_count),
    }


def merge_current(current: dict[str, Any], persisted: dict[str, Any]) -> dict[str, Any]:
    result = dict(current)
    current_total = current.get("total") or {}
    result["total"] = {
        key: max(int(current_total.get(key, 0) or 0), int((persisted.get("total") or {}).get(key, 0) or 0))
        for key in ("views", "visits", "visitors")
    }

    merged_daily: dict[str, dict[str, int]] = {}
    for source in (persisted.get("daily") or {}, current.get("daily") or {}):
        if not isinstance(source, dict):
            continue
        for day, values in source.items():
            if not isinstance(values, dict):
                continue
            target = merged_daily.setdefault(str(day), {"views": 0, "visits": 0, "visitors": 0})
            for key in target:
                try:
                    target[key] = max(target[key], int(values.get(key, 0) or 0))
                except (TypeError, ValueError):
                    pass
    result["daily"] = merged_daily

    mapping = {"top_pages": "pages", "sources": "sources", "devices": "devices", "browsers": "browsers", "errors": "errors"}
    for current_key, persisted_key in mapping.items():
        merged = normalize_counter(persisted.get(persisted_key))
        for label, value in normalize_counter(current.get(current_key)).items():
            merged[label] = max(merged.get(label, 0), value)
        result[current_key] = merged
    result["snapshots"] = persisted.get("snapshots") or []
    result["snapshot_count"] = int(persisted.get("snapshot_count", 0) or 0)
    return result


def title_from_file(path: str) -> str:
    match = ARTICLE_RE.match(path)
    if not match:
        return path
    relative = Path("clanky") / match.group(1)
    for root in STATIC_ARTICLE_ROOTS:
        file_path = root / relative
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern in (
            r"<h1\b[^>]*>(.*?)</h1>",
            r"<meta\b[^>]*property=[\"']og:title[\"'][^>]*content=[\"']([^\"']+)",
            r"<title\b[^>]*>(.*?)</title>",
        ):
            found = re.search(pattern, text, re.I | re.S)
            if found:
                value = re.sub(r"<[^>]+>", " ", found.group(1))
                value = html.unescape(re.sub(r"\s+", " ", value)).strip()
                value = re.sub(r"\s*[|–-]\s*Naše Kadaň\s*$", "", value, flags=re.I)
                if value:
                    return value[:240]
    slug = match.group(1).removesuffix(".html").replace("-", " ")
    return slug[:1].upper() + slug[1:]


def resolve_article_titles(paths: list[str]) -> dict[str, str]:
    stamp = now_local().isoformat()
    with DB_LOCK, connect() as con:
        cached = {row["path"]: row["title"] for row in con.execute("SELECT path,title FROM article_titles")}
        for path in paths:
            title = title_from_file(path)
            if title and cached.get(path) != title:
                con.execute(
                    "INSERT INTO article_titles(path,title,updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(path) DO UPDATE SET title=excluded.title, updated_at=excluded.updated_at",
                    (path, title, stamp),
                )
                cached[path] = title
        con.commit()
    return {path: cached.get(path) or title_from_file(path) for path in paths}


def metric_card(label: str, value: int, note: str) -> str:
    return (
        '<div class="metric">'
        f'<div class="metric-label">{esc(label)}</div>'
        f'<div class="metric-value">{fmt(value)}</div>'
        f'<div class="metric-note">{esc(note)}</div>'
        '</div>'
    )


def bar_rows(counter: dict[str, int], limit: int = 10) -> str:
    if not counter:
        return '<p class="empty">Zatím nejsou data.</p>'
    maximum = max(counter.values(), default=1) or 1
    out = []
    for label, value in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        width = max(2.0, value / maximum * 100.0)
        out.append(
            '<div class="bar-row">'
            f'<div class="bar-label" title="{esc(label)}">{esc(label)}</div>'
            f'<div class="bar-track"><span style="width:{width:.1f}%"></span></div>'
            f'<div class="bar-value">{fmt(value)}</div>'
            '</div>'
        )
    return "".join(out)


def render_daily(daily: dict[str, dict[str, int]]) -> str:
    today = now_local().date()
    days = [today - dt.timedelta(days=i) for i in range(29, -1, -1)]
    max_views = max((int(daily.get(day.isoformat(), {}).get("views", 0)) for day in days), default=1) or 1
    bars = []
    for day in days:
        values = daily.get(day.isoformat(), {})
        views = int(values.get("views", 0) or 0)
        visits = int(values.get("visits", 0) or 0)
        visitors = int(values.get("visitors", 0) or 0)
        height = max(1.0, views / max_views * 100.0) if views else 0.0
        bars.append(
            f'<div class="day" title="{day.strftime("%d.%m.%Y")}: {fmt(views)} zobrazení, {fmt(visits)} návštěv, {fmt(visitors)} návštěvníků">'
            f'<span class="day-number">{fmt(views)}</span><span class="day-bar" style="height:{height:.1f}%"></span>'
            f'<span class="day-label">{day.day}</span></div>'
        )
    return "".join(bars)


def render_articles(pages: dict[str, int], total_views: int) -> tuple[str, int, int]:
    articles = [(path, views) for path, views in pages.items() if ARTICLE_RE.match(path)]
    articles.sort(key=lambda item: (-item[1], item[0]))
    titles = resolve_article_titles([path for path, _ in articles])
    article_views = sum(value for _, value in articles)
    rows = []
    for rank, (path, views) in enumerate(articles, 1):
        share_articles = views / article_views * 100 if article_views else 0
        share_site = views / total_views * 100 if total_views else 0
        rows.append(
            f'<tr data-search="{esc((titles[path] + " " + path).lower())}">'
            f'<td class="rank">{rank}</td>'
            f'<td><a href="{esc(path)}" target="_blank" rel="noopener"><b>{esc(titles[path])}</b></a><small>{esc(path)}</small></td>'
            f'<td class="num"><b>{fmt(views)}</b></td>'
            f'<td class="num">{share_articles:.1f} %</td>'
            f'<td class="num">{share_site:.1f} %</td>'
            '</tr>'
        )
    if not rows:
        rows.append('<tr><td colspan="5" class="empty">Zatím nebyl zaznamenán žádný článek.</td></tr>')
    return "".join(rows), len(articles), article_views


def render_snapshots(snapshots: list[dict[str, Any]]) -> str:
    if len(snapshots) < 2:
        return '<p class="empty">Trend se začne zobrazovat po druhém pětiminutovém snímku.</p>'
    ordered = list(reversed(snapshots[:72]))
    first = int(ordered[0].get("views", 0))
    last = int(ordered[-1].get("views", 0))
    delta = max(0, last - first)
    first_time = str(ordered[0].get("captured_at", ""))[11:16]
    last_time = str(ordered[-1].get("captured_at", ""))[11:16]
    return (
        '<div class="trend-summary">'
        f'<strong>+{fmt(delta)}</strong><span>nových zobrazení mezi {esc(first_time)} a {esc(last_time)}</span>'
        '</div>'
    )


def render(base: Any) -> bytes:
    current = legacy.aggregate(base)
    persist_current(current)
    persisted = read_persisted()
    data = merge_current(current, persisted)

    total = data["total"]
    daily = data["daily"]
    today = daily.get(now_local().date().isoformat(), {"views": 0, "visits": 0, "visitors": 0})
    start7 = now_local().date() - dt.timedelta(days=6)
    last7 = {"views": 0, "visits": 0, "visitors": 0}
    for day, values in daily.items():
        try:
            date = dt.date.fromisoformat(day)
        except ValueError:
            continue
        if date >= start7:
            for key in last7:
                last7[key] += int(values.get(key, 0) or 0)

    article_rows, article_count, article_views = render_articles(data.get("top_pages") or {}, total["views"])
    diag = current.get("diag") or {}
    first = diag.get("first")
    latest = diag.get("latest")
    first_text = first.strftime("%d.%m.%Y %H:%M") if hasattr(first, "strftime") else "neuvedeno"
    latest_text = latest.strftime("%d.%m.%Y %H:%M") if hasattr(latest, "strftime") else "neuvedeno"
    updated = now_local().strftime("%d.%m.%Y %H:%M:%S")

    document = f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Statistiky – Naše Kadaň</title>
<style>
:root{{--bg:#f4f1eb;--card:#fff;--text:#20252a;--muted:#6b737b;--accent:#9d3c2d;--accent2:#d9905b;--line:#e4ded5;--ok:#246b38;--soft:#f8f6f2}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}}
a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}main{{max-width:1280px;margin:auto;padding:26px 18px 60px}}
header{{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin-bottom:20px}}h1{{margin:0;font-size:30px}}header p{{margin:5px 0 0;color:var(--muted)}}
.badges{{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}}.badge{{padding:7px 11px;border-radius:999px;background:#e6f3e8;color:var(--ok);font-weight:750;white-space:nowrap}}.badge.neutral{{background:#eee9e2;color:#5f5a53}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}}.metric,.panel{{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:0 4px 18px #4233230a}}
.metric{{padding:17px}}.metric-label{{color:var(--muted);font-size:13px}}.metric-value{{font-size:29px;font-weight:800;margin-top:2px}}.metric-note{{color:var(--muted);font-size:12px;margin-top:2px}}
.panel{{padding:20px;margin-top:16px}}.panel h2{{font-size:19px;margin:0 0 4px}}.panel-note{{color:var(--muted);margin:0 0 16px;font-size:13px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.chart{{height:225px;display:flex;gap:4px;align-items:flex-end;border-bottom:1px solid var(--line);overflow:hidden;padding-top:32px}}
.day{{height:100%;flex:1;min-width:0;display:flex;align-items:center;flex-direction:column;justify-content:flex-end;position:relative}}.day-bar{{display:block;width:100%;max-width:20px;background:linear-gradient(var(--accent2),var(--accent));border-radius:4px 4px 0 0;min-height:1px}}.day-label{{font-size:9px;color:var(--muted);margin-top:5px}}.day-number{{font-size:8px;color:var(--muted);position:absolute;top:-22px;transform:rotate(-45deg);display:none}}.day:hover .day-number{{display:block}}
.bar-row{{display:grid;grid-template-columns:minmax(115px,1.2fr) minmax(80px,2fr) 55px;gap:10px;align-items:center;margin:11px 0}}.bar-label{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.bar-track{{height:9px;background:#eee9e2;border-radius:999px;overflow:hidden}}.bar-track span{{display:block;height:100%;background:var(--accent);border-radius:999px}}.bar-value{{text-align:right;color:var(--muted)}}
.article-tools{{display:flex;justify-content:space-between;gap:12px;align-items:center;margin:12px 0}}input[type=search]{{width:min(420px,100%);padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;font:inherit}}
.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px}}table{{width:100%;border-collapse:collapse;min-width:760px}}th{{text-align:left;background:var(--soft);font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);padding:10px}}td{{padding:11px 10px;border-top:1px solid var(--line);vertical-align:top}}td small{{display:block;color:var(--muted);font-size:11px;margin-top:3px}}.num{{text-align:right;white-space:nowrap}}.rank{{width:45px;color:var(--muted)}}.empty{{color:var(--muted)}}
.trend-summary{{display:flex;align-items:baseline;gap:10px}}.trend-summary strong{{font-size:30px}}.trend-summary span{{color:var(--muted)}}.diagnostics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}.diag{{padding:12px;background:var(--soft);border-radius:10px}}.diag b{{display:block;font-size:17px}}.diag small{{color:var(--muted)}}footer{{margin-top:18px;color:var(--muted);font-size:12px}}
@media(max-width:950px){{.metrics{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}.diagnostics{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:560px){{header{{align-items:flex-start;flex-direction:column}}.badges{{justify-content:flex-start}}.metrics{{grid-template-columns:1fr 1fr}}.metric-value{{font-size:24px}}.article-tools{{align-items:stretch;flex-direction:column}}.diagnostics{{grid-template-columns:1fr 1fr}}}}
</style></head><body><main>
<header><div><h1>Naše Kadaň · návštěvnost</h1><p>Trvalý soukromý přehled ze serverových logů, bez analytických cookies.</p></div><div class="badges"><span class="badge">● Počítadlo běží</span><span class="badge neutral">SQLite záloha aktivní</span></div></header>
<section class="metrics">
{metric_card('Dnes – zobrazení', today['views'], f"{fmt(today['visits'])} návštěv · {fmt(today['visitors'])} návštěvníků")}
{metric_card('Posledních 7 dní', last7['views'], f"{fmt(last7['visits'])} návštěv · {fmt(last7['visitors'])} návštěvníků")}
{metric_card('Celkem – zobrazení', total['views'], f"{fmt(total['visits'])} návštěv · {fmt(total['visitors'])} návštěvníků")}
{metric_card('Online za 5 minut', int(data.get('online', 0) or 0), 'aktivní anonymní návštěvníci')}
{metric_card('Články v přehledu', article_count, f"{fmt(article_views)} zobrazení článků")}
{metric_card('Facebook', int((data.get('sources') or {}).get('Facebook', 0)), 'příchody z Facebooku')}
{metric_card('Google', int((data.get('sources') or {}).get('Google', 0)), 'příchody z vyhledávání')}
{metric_card('Uložené snímky', int(data.get('snapshot_count', 0)), 'pětiminutová historie v databázi')}
</section>
<section class="panel"><h2>Vývoj za posledních 30 dní</h2><p class="panel-note">Zobrazení, návštěvy a návštěvníci zůstávají uložené i po rotaci nebo ztrátě logu.</p><div class="chart">{render_daily(daily)}</div></section>
<section class="panel"><h2>Statistiky jednotlivých článků</h2><p class="panel-note">Kompletní pořadí všech článků, které mají zaznamenané zobrazení. Hodnoty se ukládají jako nikdy neklesající souhrny.</p><div class="article-tools"><input id="article-search" type="search" placeholder="Hledat článek podle názvu nebo adresy…"><span><b>{article_count}</b> článků · <b>{fmt(article_views)}</b> zobrazení</span></div><div class="table-wrap"><table id="articles"><thead><tr><th>#</th><th>Článek</th><th class="num">Zobrazení</th><th class="num">Podíl článků</th><th class="num">Podíl webu</th></tr></thead><tbody>{article_rows}</tbody></table></div></section>
<section class="grid"><div class="panel"><h2>Odkud lidé přicházejí</h2><p class="panel-note">Externí i přímé zdroje.</p>{bar_rows(data.get('sources') or {},12)}</div><div class="panel"><h2>Zařízení</h2><p class="panel-note">Rozdělení načtených stránek.</p>{bar_rows(data.get('devices') or {},8)}</div></section>
<section class="grid"><div class="panel"><h2>Prohlížeče</h2>{bar_rows(data.get('browsers') or {},8)}</div><div class="panel"><h2>Krátkodobý trend</h2>{render_snapshots(data.get('snapshots') or [])}</div></section>
<section class="panel"><h2>Stav měření a ochrany dat</h2><div class="diagnostics"><div class="diag"><b>{fmt(int(diag.get('files',0) or 0))}</b><small>načtených logů</small></div><div class="diag"><b>{esc(first_text)}</b><small>nejstarší dostupný záznam</small></div><div class="diag"><b>{esc(latest_text)}</b><small>nejnovější záznam</small></div><div class="diag"><b>{esc(DB_PATH.name)}</b><small>trvalá databáze mimo webový deploy</small></div></div></section>
<footer>Aktualizováno {esc(updated)} · databáze je uložena mimo document root a instalátor ji nemaže · při výpadku logu se poslední ověřené souhrny zachovají.</footer>
<script>document.getElementById('article-search').addEventListener('input',function(){{const q=this.value.trim().toLowerCase();document.querySelectorAll('#articles tbody tr').forEach(r=>{{r.hidden=q&&!r.dataset.search.includes(q)}})}});</script>
</main></body></html>'''
    return document.encode("utf-8")


def install(base: Any) -> None:
    global CACHE_AT, CACHE_BODY
    fallback = getattr(base, "render_dashboard", None)

    def render_dashboard() -> bytes:
        global CACHE_AT, CACHE_BODY
        moment = now_local()
        with CACHE_LOCK:
            if CACHE_BODY and CACHE_AT and (moment - CACHE_AT).total_seconds() < CACHE_SECONDS:
                return CACHE_BODY
        try:
            body = render(base)
        except Exception:
            if callable(fallback):
                return fallback()
            raise
        with CACHE_LOCK:
            CACHE_AT = moment
            CACHE_BODY = body
        return body

    base.render_dashboard = render_dashboard
