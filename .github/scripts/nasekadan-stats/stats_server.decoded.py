#!/usr/bin/env python3
from __future__ import annotations

import base64
import collections
import datetime as dt
import glob
import gzip
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import smtplib
import threading
import time
import urllib.parse
from email.message import EmailMessage
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Prague")
except Exception:
    TZ = dt.timezone(dt.timedelta(hours=2))

HOST = "127.0.0.1"
PORT = 3225
BASE_URL = "https://nasekadan.cz/statistiky"
RESET_EMAIL = "petrkotab@seznam.cz"
USERNAME = "petr"
LOG_GLOB = "/var/log/nginx/nasekadan.access.log*"
BASE_DIR = Path("/opt/nasekadan-stats")
SALT_FILE = BASE_DIR / "secret-salt"
PASSWORD_FILE = BASE_DIR / "password.json"
RESET_FILE = BASE_DIR / "reset-token.json"
LEGACY_AUTH_FILE = Path("/etc/nginx/.nasekadan-stats.htpasswd")
SESSION_SECONDS = 12 * 60 * 60
RESET_SECONDS = 20 * 60
RESET_COOLDOWN_SECONDS = 5 * 60
PBKDF2_ITERATIONS = 600_000
MAX_BODY = 16_384

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_MODE = os.environ.get("SMTP_TLS", "ssl").strip().lower()
MAIL_FROM = os.environ.get("NEWSLETTER_FROM", SMTP_USER or "info@nasekadan.cz")

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
LOGIN_LOCK = threading.Lock()
LOGIN_ATTEMPTS: dict[str, collections.deque[float]] = collections.defaultdict(collections.deque)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def n(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def read_secret() -> bytes:
    try:
        value = SALT_FILE.read_text(encoding="utf-8").strip()
        if value:
            return value.encode("utf-8")
    except OSError:
        pass
    return b"nasekadan-stats-fallback"


def b64e(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def atomic_json(path: Path, data: dict) -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def read_json_file(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def hash_password(password: str, salt: bytes | None = None) -> dict:
    raw_salt = salt or secrets.token_bytes(24)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw_salt, PBKDF2_ITERATIONS)
    return {
        "version": 1,
        "algorithm": "pbkdf2-sha256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": b64e(raw_salt),
        "hash": b64e(digest),
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def verify_password(password: str) -> bool:
    data = read_json_file(PASSWORD_FILE)
    try:
        if data.get("algorithm") == "pbkdf2-sha256":
            iterations = int(data.get("iterations", PBKDF2_ITERATIONS))
            salt = b64d(str(data["salt"]))
            expected = b64d(str(data["hash"]))
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
            return hmac.compare_digest(actual, expected)
    except (KeyError, ValueError, TypeError):
        return False

    # Zachování dosavadního hesla do prvního resetu. Na Ubuntu 24.04 je modul
    # crypt dostupný; když není, stále funguje bezpečný reset přes e-mail.
    try:
        import crypt  # type: ignore[import-not-found]
        line = LEGACY_AUTH_FILE.read_text(encoding="utf-8").splitlines()[0]
        user, stored = line.split(":", 1)
        return user == USERNAME and hmac.compare_digest(crypt.crypt(password, stored), stored)
    except Exception:
        return False


def save_password(password: str) -> None:
    atomic_json(PASSWORD_FILE, hash_password(password))


def session_token() -> str:
    expires = int(time.time()) + SESSION_SECONDS
    nonce = secrets.token_urlsafe(18)
    payload = f"{expires}.{nonce}"
    signature = hmac.new(read_secret(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def valid_session(value: str) -> bool:
    try:
        expires_text, nonce, signature = value.split(".", 2)
        if int(expires_text) < int(time.time()) or len(nonce) < 12:
            return False
        payload = f"{expires_text}.{nonce}"
        expected = hmac.new(read_secret(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
    except (ValueError, TypeError):
        return False


def client_ip(headers, address: tuple[str, int]) -> str:
    forwarded = headers.get("X-Forwarded-For", "").split(",", 1)[0].strip()
    return forwarded or address[0]


def login_allowed(ip: str) -> bool:
    now = time.monotonic()
    with LOGIN_LOCK:
        attempts = LOGIN_ATTEMPTS[ip]
        while attempts and attempts[0] < now - 15 * 60:
            attempts.popleft()
        return len(attempts) < 10


def note_failed_login(ip: str) -> None:
    with LOGIN_LOCK:
        LOGIN_ATTEMPTS[ip].append(time.monotonic())


def clear_failed_logins(ip: str) -> None:
    with LOGIN_LOCK:
        LOGIN_ATTEMPTS.pop(ip, None)


def send_reset_email(token: str) -> None:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        raise RuntimeError("SMTP není nastavené")
    link = f"{BASE_URL}/obnovit-heslo?token={urllib.parse.quote(token)}"
    message = EmailMessage()
    message["From"] = MAIL_FROM
    message["To"] = RESET_EMAIL
    message["Subject"] = "Obnovení hesla ke statistikám Naše Kadaň"
    message.set_content(
        "Byla vyžádána změna hesla ke statistikám webu Naše Kadaň.\n\n"
        f"Nové heslo nastavíte zde:\n{link}\n\n"
        "Odkaz platí 20 minut a lze jej použít pouze jednou. "
        "Pokud jste o změnu nežádal, tento e-mail ignorujte."
    )
    if SMTP_MODE in {"ssl", "smtps", "465"}:
        connection = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
    else:
        connection = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
    with connection as smtp:
        if SMTP_MODE in {"1", "true", "yes", "starttls", "tls"}:
            smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(message)


def issue_reset_token() -> bool:
    now = int(time.time())
    old = read_json_file(RESET_FILE)
    try:
        if now - int(old.get("requested_at", 0)) < RESET_COOLDOWN_SECONDS:
            return False
    except (ValueError, TypeError):
        pass
    token = secrets.token_urlsafe(40)
    data = {
        "token_hash": hashlib.sha256(token.encode("utf-8")).hexdigest(),
        "expires_at": now + RESET_SECONDS,
        "requested_at": now,
    }
    atomic_json(RESET_FILE, data)
    try:
        send_reset_email(token)
    except Exception:
        try:
            RESET_FILE.unlink()
        except OSError:
            pass
        raise
    return True


def valid_reset_token(token: str, consume: bool = False) -> bool:
    data = read_json_file(RESET_FILE)
    try:
        valid = (
            bool(token)
            and int(data.get("expires_at", 0)) >= int(time.time())
            and hmac.compare_digest(
                str(data.get("token_hash", "")),
                hashlib.sha256(token.encode("utf-8")).hexdigest(),
            )
        )
    except (ValueError, TypeError):
        valid = False
    if valid and consume:
        try:
            RESET_FILE.unlink()
        except OSError:
            pass
    return valid


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
    salt = read_secret().decode("utf-8", "replace")
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


COMMON_STYLE = """
:root{--bg:#f4f1eb;--card:#fff;--text:#20252a;--muted:#6d757d;--accent:#9d3c2d;--line:#e4ded5;--soft:#f8f6f2}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--accent)}button,.btn{border:0;border-radius:10px;background:var(--accent);color:#fff;padding:11px 16px;font:inherit;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
input{width:100%;border:1px solid var(--line);border-radius:10px;padding:11px 12px;font:inherit}.muted{color:var(--muted)}.error{background:#fbe8e5;color:#8d251c;padding:11px 13px;border-radius:10px}.ok{background:#e6f3e8;color:#236b32;padding:11px 13px;border-radius:10px}
"""


def page(title: str, body: str, extra_style: str = "") -> bytes:
    return f'''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>{esc(title)}</title><style>{COMMON_STYLE}{extra_style}</style></head><body>{body}</body></html>'''.encode("utf-8")


def login_page(message: str = "", error: bool = False) -> bytes:
    notice = f'<p class="{"error" if error else "ok"}">{esc(message)}</p>' if message else ""
    body = f'''<main style="max-width:440px;margin:8vh auto;padding:20px"><section style="background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:0 8px 30px #42332312"><h1 style="margin-top:0">Přihlášení ke statistikám</h1><p class="muted">Soukromý přehled návštěvnosti webu Naše Kadaň.</p>{notice}<form method="post" action="/statistiky/prihlasit"><label>Uživatelské jméno<input name="username" autocomplete="username" required value="petr"></label><label style="display:block;margin-top:14px">Heslo<input type="password" name="password" autocomplete="current-password" required></label><button style="margin-top:18px;width:100%" type="submit">Přihlásit se</button></form><p style="margin:18px 0 0;text-align:center"><a href="/statistiky/zapomenute-heslo">Zapomenuté heslo</a></p></section></main>'''
    return page("Přihlášení – statistiky Naše Kadaň", body)


def forgot_page(message: str = "", error: bool = False) -> bytes:
    notice = f'<p class="{"error" if error else "ok"}">{esc(message)}</p>' if message else ""
    body = f'''<main style="max-width:500px;margin:8vh auto;padding:20px"><section style="background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:0 8px 30px #42332312"><h1 style="margin-top:0">Obnovení hesla</h1><p>Odkaz pro nastavení nového hesla bude odeslán výhradně na <strong>{esc(RESET_EMAIL)}</strong>.</p>{notice}<form method="post" action="/statistiky/zapomenute-heslo"><button type="submit">Poslat obnovovací odkaz</button></form><p><a href="/statistiky/">Zpět k přihlášení</a></p></section></main>'''
    return page("Obnovení hesla – Naše Kadaň", body)


def reset_page(token: str, message: str = "", error: bool = False) -> bytes:
    if not valid_reset_token(token):
        body = '''<main style="max-width:500px;margin:8vh auto;padding:20px"><section style="background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px"><h1>Odkaz není platný</h1><p>Odkaz mohl vypršet nebo už byl použit.</p><p><a class="btn" href="/statistiky/zapomenute-heslo">Poslat nový odkaz</a></p></section></main>'''
        return page("Neplatný odkaz – Naše Kadaň", body)
    notice = f'<p class="{"error" if error else "ok"}">{esc(message)}</p>' if message else ""
    body = f'''<main style="max-width:500px;margin:8vh auto;padding:20px"><section style="background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px"><h1 style="margin-top:0">Nastavit nové heslo</h1><p class="muted">Použijte alespoň 12 znaků.</p>{notice}<form method="post" action="/statistiky/obnovit-heslo"><input type="hidden" name="token" value="{esc(token)}"><label>Nové heslo<input type="password" name="password" minlength="12" autocomplete="new-password" required></label><label style="display:block;margin-top:14px">Nové heslo znovu<input type="password" name="password_confirm" minlength="12" autocomplete="new-password" required></label><button style="margin-top:18px" type="submit">Změnit heslo</button></form></section></main>'''
    return page("Nové heslo – Naše Kadaň", body)


def render_dashboard() -> bytes:
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
    for row in rows30:
        daily_visitors[row[0].date()].add(row[1])
    maximum = max((daily[start30 + dt.timedelta(days=i)] for i in range(30)), default=1) or 1
    for i in range(30):
        day = start30 + dt.timedelta(days=i)
        views = daily[day]
        visitors = len(daily_visitors[day])
        height = max(2, round(views * 100 / maximum)) if views else 1
        days.append(f'<div class="day" title="{day.strftime("%d.%m.%Y")}: {views} zobrazení, {visitors} návštěvníků"><span style="height:{height}%"></span><small>{day.day}</small></div>')
    error_html = "".join(f'<tr><td><b>{status}</b></td><td>{esc(path)}</td><td>{n(count)}</td></tr>' for (status, path), count in error_counts.most_common(8)) or '<tr><td colspan="3" class="empty">Žádné časté chyby.</td></tr>'
    extra_style = """
main{max-width:1180px;margin:auto;padding:28px 18px 50px}header{display:flex;justify-content:space-between;gap:18px;align-items:end;margin-bottom:22px}h1{margin:0;font-size:30px}header p{margin:5px 0 0;color:var(--muted)}.actions{display:flex;gap:10px;align-items:center}.live{background:#e6f3e8;color:#236b32;padding:7px 11px;border-radius:999px;font-weight:700;white-space:nowrap}.logout{background:#fff;color:var(--accent);border:1px solid var(--line);padding:7px 11px}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card,.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:0 4px 18px #4233230a}.card{padding:17px}.card small{color:var(--muted);display:block}.card strong{display:block;font-size:28px;margin-top:3px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}.panel{padding:20px}h2{font-size:18px;margin:0 0 16px}.chart{height:190px;display:flex;align-items:end;gap:4px;border-bottom:1px solid var(--line);padding-top:10px}.day{height:100%;flex:1;display:flex;flex-direction:column;justify-content:end;align-items:center;min-width:0}.day span{width:100%;max-width:20px;background:var(--accent);border-radius:4px 4px 0 0;opacity:.82}.day small{font-size:9px;color:var(--muted);margin-top:5px}.barrow{display:grid;grid-template-columns:minmax(130px,1.3fr) minmax(90px,2fr) 46px;align-items:center;gap:10px;margin:12px 0}.label{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.label small{display:block;color:var(--muted);overflow:hidden;text-overflow:ellipsis}.track{height:9px;background:#eee9e2;border-radius:99px;overflow:hidden}.track span{display:block;height:100%;background:var(--accent);border-radius:99px}.num{text-align:right;color:var(--muted)}table{width:100%;border-collapse:collapse}td{border-top:1px solid var(--line);padding:9px 6px}td:last-child{text-align:right}.empty{color:var(--muted)}footer{margin-top:18px;color:var(--muted);font-size:13px}@media(max-width:850px){.cards{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}@media(max-width:520px){header{align-items:start;flex-direction:column}.actions{width:100%;justify-content:space-between}.cards{grid-template-columns:1fr 1fr}.card strong{font-size:23px}.barrow{grid-template-columns:minmax(95px,1fr) minmax(65px,1fr) 38px}}
"""
    body = f'''<main><header><div><h1>Naše Kadaň – návštěvnost</h1><p>Soukromý přehled ze serverových záznamů, bez analytických cookies.</p></div><div class="actions"><div class="live">● právě měří</div><a class="btn logout" href="/statistiky/odhlasit">Odhlásit</a></div></header><section class="cards"><div class="card"><small>Návštěvníci dnes</small><strong>{n(unique(today_rows))}</strong></div><div class="card"><small>Zobrazení dnes</small><strong>{n(len(today_rows))}</strong></div><div class="card"><small>Návštěvníci za 7 dní</small><strong>{n(unique(rows7))}</strong></div><div class="card"><small>Návštěvníci za 30 dní</small><strong>{n(unique(rows30))}</strong></div><div class="card"><small>Aktivní za 30 minut</small><strong>{n(active)}</strong></div><div class="card"><small>Celkem návštěvníků</small><strong>{n(unique(visits))}</strong></div><div class="card"><small>Celkem zobrazení</small><strong>{n(len(visits))}</strong></div><div class="card"><small>Měření od</small><strong style="font-size:20px">{first.strftime("%d.%m.%Y") if first else "dneška"}</strong></div></section><section class="panel" style="margin-top:16px"><h2>Zobrazení stránek – posledních 30 dní</h2><div class="chart">{''.join(days)}</div></section><section class="grid"><div class="panel"><h2>Nejčtenější stránky</h2>{top_rows(pages, len(rows30), page=True)}</div><div class="panel"><h2>Odkud návštěvníci přišli</h2>{top_rows(sources, len(rows30))}</div></section><section class="grid"><div class="panel"><h2>Zařízení</h2>{top_rows(devices, len(rows30))}</div><div class="panel"><h2>Prohlížeče</h2>{top_rows(browsers, len(rows30))}</div></section><section class="panel" style="margin-top:16px"><h2>Nejčastější chyby za 30 dní</h2><table><tbody>{error_html}</tbody></table></section><footer>Aktualizováno {now.strftime("%d.%m.%Y %H:%M:%S")} · zpracováno {n(parsed)} z {n(raw)} záznamů · roboti, technické soubory a stránka statistik se nezapočítávají.</footer></main>'''
    return page("Statistiky – Naše Kadaň", body, extra_style)


def dashboard() -> bytes:
    global CACHE_AT, CACHE_BODY
    now = time.monotonic()
    with CACHE_LOCK:
        if CACHE_BODY and now - CACHE_AT < 3:
            return CACHE_BODY
        CACHE_BODY = render_dashboard()
        CACHE_AT = now
        return CACHE_BODY


class Handler(BaseHTTPRequestHandler):
    server_version = "NaseKadanStats/4.0"

    def do_HEAD(self):
        self.handle_request(False)

    def do_GET(self):
        self.handle_request(True)

    def do_POST(self):
        self.handle_request(True)

    def parse_form(self) -> dict[str, str]:
        try:
            length = min(int(self.headers.get("Content-Length", "0")), MAX_BODY)
        except ValueError:
            length = 0
        raw = self.rfile.read(length).decode("utf-8", "replace")
        values = urllib.parse.parse_qs(raw, keep_blank_values=True)
        return {key: items[0] if items else "" for key, items in values.items()}

    def session(self) -> bool:
        jar = cookies.SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
            morsel = jar.get("nkstats_session")
            return bool(morsel and valid_session(morsel.value))
        except cookies.CookieError:
            return False

    def send(self, code: int, ctype: str, payload: bytes, body: bool = True, extra: list[tuple[str, str]] | None = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Robots-Tag", "noindex, nofollow, noarchive")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        if extra:
            for key, value in extra:
                self.send_header(key, value)
        self.end_headers()
        if body:
            self.wfile.write(payload)

    def redirect(self, location: str, cookie: str | None = None):
        headers = [("Location", location)]
        if cookie:
            headers.append(("Set-Cookie", cookie))
        self.send(303, "text/plain; charset=utf-8", b"Presmerovani", True, headers)

    def handle_request(self, body: bool):
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path
        method = self.command

        if path == "/healthz":
            payload = json.dumps({"ok": True, "smtpConfigured": bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD), "auth": "application"}).encode("utf-8")
            return self.send(200, "application/json; charset=utf-8", payload, body)

        if path in {"/logout", "/odhlasit"}:
            cookie = "nkstats_session=; Path=/statistiky/; Max-Age=0; HttpOnly; Secure; SameSite=Strict"
            return self.redirect("/statistiky/", cookie)

        if path in {"/login", "/prihlasit"} and method == "POST":
            ip = client_ip(self.headers, self.client_address)
            if not login_allowed(ip):
                return self.send(429, "text/html; charset=utf-8", login_page("Příliš mnoho neúspěšných pokusů. Zkuste to později.", True), body)
            form = self.parse_form()
            username = form.get("username", "").strip()
            password = form.get("password", "")
            if username == USERNAME and verify_password(password):
                clear_failed_logins(ip)
                cookie = f"nkstats_session={session_token()}; Path=/statistiky/; Max-Age={SESSION_SECONDS}; HttpOnly; Secure; SameSite=Strict"
                return self.redirect("/statistiky/", cookie)
            note_failed_login(ip)
            time.sleep(0.6)
            return self.send(401, "text/html; charset=utf-8", login_page("Přihlašovací údaje nejsou správné.", True), body)

        if path in {"/forgot", "/zapomenute-heslo"}:
            if method == "POST":
                try:
                    sent = issue_reset_token()
                    message = "Obnovovací odkaz byl odeslán na petrkotab@seznam.cz." if sent else "Obnovovací odkaz už byl nedávno odeslán. Zkontrolujte svou schránku."
                    return self.send(200, "text/html; charset=utf-8", forgot_page(message), body)
                except Exception as exc:
                    print(f"reset email error: {type(exc).__name__}: {exc}", flush=True)
                    return self.send(502, "text/html; charset=utf-8", forgot_page("E-mail se nepodařilo odeslat. Zkontrolujte nastavení odesílací schránky.", True), body)
            return self.send(200, "text/html; charset=utf-8", forgot_page(), body)

        if path in {"/reset", "/obnovit-heslo"}:
            query_token = urllib.parse.parse_qs(parsed.query).get("token", [""])[0]
            if method == "POST":
                form = self.parse_form()
                token = form.get("token", "")
                password = form.get("password", "")
                confirm = form.get("password_confirm", "")
                if not valid_reset_token(token):
                    return self.send(400, "text/html; charset=utf-8", reset_page(""), body)
                if len(password) < 12:
                    return self.send(400, "text/html; charset=utf-8", reset_page(token, "Heslo musí mít alespoň 12 znaků.", True), body)
                if password != confirm:
                    return self.send(400, "text/html; charset=utf-8", reset_page(token, "Zadaná hesla se neshodují.", True), body)
                save_password(password)
                valid_reset_token(token, consume=True)
                cookie = f"nkstats_session={session_token()}; Path=/statistiky/; Max-Age={SESSION_SECONDS}; HttpOnly; Secure; SameSite=Strict"
                return self.redirect("/statistiky/", cookie)
            return self.send(200, "text/html; charset=utf-8", reset_page(query_token), body)

        if path in {"/", "/index.html"}:
            if self.session():
                try:
                    return self.send(200, "text/html; charset=utf-8", dashboard(), body)
                except Exception as exc:
                    return self.send(500, "text/plain; charset=utf-8", f"Chyba statistik: {exc}\n".encode("utf-8"), body)
            return self.send(200, "text/html; charset=utf-8", login_page(), body)

        return self.send(404, "text/plain; charset=utf-8", b"Nenalezeno\n", body)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
