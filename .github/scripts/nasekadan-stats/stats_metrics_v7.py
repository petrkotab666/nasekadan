#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import re
from typing import Any

import stats_metrics_v6 as v6

RECENT_LIMIT = 25
MONTHS_CS = {
    "ledna": 1,
    "února": 2,
    "unora": 2,
    "března": 3,
    "brezna": 3,
    "dubna": 4,
    "května": 5,
    "kvetna": 5,
    "června": 6,
    "cervna": 6,
    "července": 7,
    "cervence": 7,
    "srpna": 8,
    "září": 9,
    "zari": 9,
    "října": 10,
    "rijna": 10,
    "listopadu": 11,
    "prosince": 12,
}


def parse_iso_datetime(value: str) -> dt.datetime | None:
    value = html.unescape(value).strip()
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = dt.datetime.combine(dt.date.fromisoformat(value[:10]), dt.time.min)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=v6.TZ)
    return parsed.astimezone(v6.TZ)


def published_from_html(text: str) -> dt.datetime | None:
    patterns = (
        r'<meta\b[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
        r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']',
        r'["\']datePublished["\']\s*:\s*["\']([^"\']+)',
        r'<time\b[^>]*datetime=["\']([^"\']+)',
        r'<meta\b[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)',
    )
    for pattern in patterns:
        found = re.search(pattern, text, re.I | re.S)
        if found:
            parsed = parse_iso_datetime(found.group(1))
            if parsed:
                return parsed

    visible = re.search(
        r'\b(\d{1,2})\.\s*(ledna|února|unora|března|brezna|dubna|května|kvetna|června|cervna|července|cervence|srpna|září|zari|října|rijna|listopadu|prosince)\s+(\d{4})\b',
        text,
        re.I,
    )
    if visible:
        month = MONTHS_CS.get(visible.group(2).lower())
        if month:
            try:
                return dt.datetime(int(visible.group(3)), month, int(visible.group(1)), tzinfo=v6.TZ)
            except ValueError:
                pass
    return None


def latest_published_articles(limit: int = RECENT_LIMIT) -> list[dict[str, Any]]:
    articles: dict[str, dict[str, Any]] = {}
    for root in v6.STATIC_ARTICLE_ROOTS:
        article_dir = root / "clanky"
        if not article_dir.is_dir():
            continue
        for file_path in article_dir.glob("*.html"):
            if file_path.name.lower() == "index.html":
                continue
            path = f"/clanky/{file_path.name}"
            if path in articles or not v6.ARTICLE_RE.match(path):
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            published = published_from_html(text)
            if published is None:
                published = dt.datetime.min.replace(tzinfo=v6.TZ)
            articles[path] = {
                "path": path,
                "title": v6.title_from_file(path),
                "published": published,
            }
    return sorted(
        articles.values(),
        key=lambda item: (item["published"], item["path"]),
        reverse=True,
    )[:limit]


def render_recent_articles() -> str:
    persisted = v6.read_persisted()
    pages = v6.normalize_counter(persisted.get("pages"))
    total_views = int((persisted.get("total") or {}).get("views", 0) or 0)
    recent = latest_published_articles()
    recent_views = sum(pages.get(item["path"], 0) for item in recent)
    average = recent_views / len(recent) if recent else 0

    rows: list[str] = []
    for rank, item in enumerate(recent, 1):
        path = str(item["path"])
        title = str(item["title"])
        published = item["published"]
        views = int(pages.get(path, 0) or 0)
        share_recent = views / recent_views * 100 if recent_views else 0
        share_site = views / total_views * 100 if total_views else 0
        published_text = published.strftime("%d.%m.%Y %H:%M") if published.year > 1 else "datum neuvedeno"
        rows.append(
            '<tr>'
            f'<td class="rank">{rank}</td>'
            f'<td style="white-space:nowrap;color:var(--muted)">{v6.esc(published_text)}</td>'
            f'<td><a href="{v6.esc(path)}" target="_blank" rel="noopener"><b>{v6.esc(title)}</b></a><small>{v6.esc(path)}</small></td>'
            f'<td class="num"><b>{v6.fmt(views)}</b></td>'
            f'<td class="num">{share_recent:.1f} %</td>'
            f'<td class="num">{share_site:.1f} %</td>'
            '</tr>'
        )

    if not rows:
        rows.append('<tr><td colspan="6" class="empty">Na serveru nebyly nalezeny publikované články.</td></tr>')

    return (
        '<section class="panel" id="poslednich-25-clanku">'
        '<h2>Posledních 25 publikovaných článků</h2>'
        '<p class="panel-note">Řazeno od nejnovějšího podle data publikace v článku. Přehled zahrnuje i nové články, které zatím mají nula zobrazení.</p>'
        '<div class="article-tools">'
        f'<span><b>{len(recent)}</b> článků · <b>{v6.fmt(recent_views)}</b> zobrazení · průměr <b>{v6.fmt(average)}</b> na článek</span>'
        '</div>'
        '<div class="table-wrap"><table id="recent-articles">'
        '<thead><tr><th>#</th><th>Publikováno</th><th>Článek</th><th class="num">Zobrazení</th><th class="num">Podíl posledních 25</th><th class="num">Podíl webu</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        '</section>'
    )


def install(base: Any) -> None:
    if getattr(v6, "_recent_articles_v7_installed", False):
        return

    original_render = v6.render

    def render_with_recent_articles(render_base: Any) -> bytes:
        body = original_render(render_base).decode("utf-8", "replace")
        marker = '<section class="panel"><h2>Statistiky jednotlivých článků</h2>'
        section = render_recent_articles()
        if marker in body:
            body = body.replace(marker, section + marker, 1)
        else:
            body = body.replace("</main>", section + "</main>", 1)
        return body.encode("utf-8")

    v6.render = render_with_recent_articles
    v6.CACHE_AT = None
    v6.CACHE_BODY = b""
    v6._recent_articles_v7_installed = True
