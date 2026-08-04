#!/usr/bin/env python3
"""Zajistí správný hlavní blok titulní stránky.

Běžně zobrazuje nejnovější publikovaný článek. Pokud má hlavní blok platné
časově omezené redakční připnutí v atributu ``data-editorial-pin``, zachová je
až do uvedeného času. Po vypršení připnutí se automaticky vrátí k běžnému
chronologickému řazení. Budoucí naplánované články se před časem publikace
nezobrazují.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from html import escape, unescape
from pathlib import Path
from zoneinfo import ZoneInfo
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "clanky" / "index.html"
PRAGUE = ZoneInfo("Europe/Prague")
HERO_RE = re.compile(
    r'  <section\b[^>]*class=["\'][^"\']*\bhero\b[^"\']*["\'][^>]*\bid=["\']clanky["\'][^>]*>.*?</section>',
    re.I | re.S,
)
LEAD_RE = re.compile(
    r'<article\b[^>]*class=["\'][^"\']*\blead\b[^"\']*["\'][^>]*>.*?</article>',
    re.I | re.S,
)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first(patterns: tuple[str, ...], text: str, default: str = "") -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return clean(match.group(1))
    return default


def article_info(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
        return None
    raw = first(
        (
            r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:published_time["\']',
            r'"datePublished"\s*:\s*"([^"]+)"',
        ),
        text,
    )
    if not raw:
        return None
    try:
        published = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    if published.astimezone(timezone.utc) > datetime.now(timezone.utc) + timedelta(minutes=2):
        return None
    title = first((r'<h1\b[^>]*>(.*?)</h1>', r'<title>(.*?)</title>'), text, path.stem)
    title = re.sub(r'\s*\|\s*Naše Kadaň\s*$', '', title)
    description = first(
        (
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
            r'<p[^>]+class=["\'][^"\']*leadtext[^"\']*["\'][^>]*>(.*?)</p>',
        ),
        text,
        "",
    )
    tag = first(
        (r'<p[^>]+class=["\'][^"\']*tag[^"\']*["\'][^>]*>(.*?)</p>',),
        text,
        "AKTUÁLNĚ",
    )
    return {
        "path": path,
        "href": "/clanky/" + path.name,
        "published": published,
        "title": title,
        "description": description,
        "tag": tag,
    }


def markerize(section: str, href: str, *, preserve_editorial_pin: bool) -> str:
    opening = re.match(r'<section\b[^>]*>', section.strip(), re.I | re.S)
    if not opening:
        raise RuntimeError("Hlavní blok nemá platnou značku section.")
    tag = opening.group(0)
    tag = re.sub(r'\s+data-auto-latest-hero=["\'][^"\']*["\']', '', tag, flags=re.I)
    tag = re.sub(r'\s+data-latest-article-href=["\'][^"\']*["\']', '', tag, flags=re.I)
    if not preserve_editorial_pin:
        tag = re.sub(r'\s+data-editorial-pin=["\'][^"\']*["\']', '', tag, flags=re.I)
    tag = tag[:-1] + (
        f' data-auto-latest-hero="1" '
        f'data-latest-article-href="{escape(href, quote=True)}">'
    )
    return section.replace(opening.group(0), tag, 1)


def active_editorial_pin(section: str, articles: list[dict]) -> tuple[str, datetime] | None:
    opening = re.match(r'<section\b[^>]*>', section.strip(), re.I | re.S)
    if not opening:
        return None
    tag = opening.group(0)
    pin_match = re.search(r'data-editorial-pin=["\']([^"\']+)["\']', tag, re.I)
    href_match = re.search(r'data-latest-article-href=["\']([^"\']+)["\']', tag, re.I)
    if not pin_match or not href_match:
        return None

    expiry_match = re.search(r'-(\d{8})-(\d{4})$', pin_match.group(1))
    if not expiry_match:
        raise RuntimeError("Redakční připnutí nemá rozpoznatelný čas vypršení.")
    expiry = datetime.strptime(
        expiry_match.group(1) + expiry_match.group(2), "%Y%m%d%H%M"
    ).replace(tzinfo=PRAGUE)
    if datetime.now(PRAGUE) >= expiry:
        return None

    href = unescape(href_match.group(1))
    if not any(article["href"] == href for article in articles):
        raise RuntimeError(f"Připnutý článek není mezi publikovanými články: {href}")
    lead = LEAD_RE.search(section)
    if not lead or href not in lead.group(0):
        raise RuntimeError("Připnutý odkaz neodpovídá hlavnímu článku v hero bloku.")
    return href, expiry


def build_hero(latest, second) -> str:
    dt = latest["published"]
    aside = ""
    if second:
        sd = second["published"]
        aside = f'''    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">{sd.day}. {sd.month}. {sd.year} v {sd.strftime('%H:%M')}</p>
      <h2>{escape(second['title'])}</h2>
      <p>{escape(second['description'])}</p>
      <a class="aside-button" href="{escape(second['href'], quote=True)}">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div>
    </aside>'''
    return f'''  <section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{escape(latest['href'], quote=True)}">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(135deg,#10242e,#22606b 55%,#9d222a)"><span>NEJNOVĚJŠÍ ČLÁNEK</span><strong>{dt.day}. {dt.month}. {dt.year}</strong></div>
      <div class="copy">
        <small>{escape(latest['tag'])} · {dt.day}. {dt.month}. {dt.year} · {dt.strftime('%H:%M')}</small>
        <h1>{escape(latest['title'])}</h1>
        <p>{escape(latest['description'])}</p>
        <a class="btn" href="{escape(latest['href'], quote=True)}">Přečíst nejnovější článek →</a>
      </div>
    </article>
{aside}
  </section>'''


def main() -> int:
    articles = []
    for path in sorted((ROOT / "clanky").glob("*.html")):
        if path.name == "index.html":
            continue
        info = article_info(path)
        if info:
            articles.append(info)
    articles.sort(key=lambda item: item["published"], reverse=True)
    if not articles:
        raise RuntimeError("Nebyl nalezen žádný aktuálně publikovaný článek.")

    latest = articles[0]
    home = HOME.read_text(encoding="utf-8")
    archive = ARCHIVE.read_text(encoding="utf-8")
    archive_list = archive.split('<section class="archive-list"', 1)[-1]
    if latest["href"] not in archive_list:
        raise RuntimeError(f"Nejnovější článek chybí v archivu: {latest['href']}")

    match = HERO_RE.search(home)
    if not match:
        raise RuntimeError("Na titulní stránce nebyl nalezen hlavní blok.")
    current = match.group(0)
    pin = active_editorial_pin(current, articles)

    if pin:
        expected_href, expiry = pin
        replacement = markerize(
            current, expected_href, preserve_editorial_pin=True
        )
        action = f"redakčně připnut do {expiry.isoformat()}"
    else:
        expected_href = latest["href"]
        lead = LEAD_RE.search(current)
        if lead and latest["href"] in lead.group(0):
            replacement = markerize(
                current, latest["href"], preserve_editorial_pin=False
            )
            action = "zachován"
        else:
            replacement = build_hero(
                latest, articles[1] if len(articles) > 1 else None
            )
            action = "opraven"

    home = home[:match.start()] + replacement + home[match.end():]
    HOME.write_text(home, encoding="utf-8", newline="\n")

    check = HOME.read_text(encoding="utf-8")
    hero = HERO_RE.search(check)
    if (
        not hero
        or expected_href not in hero.group(0)
        or 'data-auto-latest-hero="1"' not in hero.group(0)
    ):
        raise RuntimeError("Kontrola hlavního článku neprošla.")
    print(f"Hlavní článek {action}: {expected_href}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
