#!/usr/bin/env python3
"""Propaguje nejnovější týdenní přehled na titulku, do archivu, RSS a sitemap.

Skript je idempotentní a používá metadata přímo z článku. Díky tomu se při
každém produkčním sestavení automaticky zveřejní nejnovější soubor
clanky/kam-v-kadani-a-okoli-*.html bez ručního přepisování několika míst.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://nasekadan.cz"
START = "<!-- WEEKLY-EVENTS-START -->"
END = "<!-- WEEKLY-EVENTS-END -->"


def meta(text: str, *, name: str | None = None, prop: str | None = None) -> str:
    for tag in re.findall(r"<meta\b[^>]*>", text, re.I):
        key = "name" if name else "property"
        value = name or prop or ""
        if not re.search(rf'\b{key}=["\']{re.escape(value)}["\']', tag, re.I):
            continue
        found = re.search(r'\bcontent=["\']([^"\']*)', tag, re.I)
        if found:
            return found.group(1).strip()
    return ""


def tag_text(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(1))).strip()


def latest_article() -> tuple[Path, str, dict[str, str]]:
    candidates: list[tuple[datetime, Path, str, dict[str, str]]] = []
    for path in (ROOT / "clanky").glob("kam-v-kadani-a-okoli-*.html"):
        text = path.read_text(encoding="utf-8")
        published_raw = meta(text, prop="article:published_time")
        try:
            published = datetime.fromisoformat(published_raw)
        except ValueError:
            published = datetime.fromtimestamp(path.stat().st_mtime)
        title = meta(text, prop="og:title") or tag_text(text, "h1")
        description = meta(text, prop="og:description") or meta(text, name="description")
        image = meta(text, prop="og:image") or f"{BASE}/social-card.png"
        canonical = meta(text, prop="og:url") or f"{BASE}/clanky/{path.name}"
        candidates.append((published, path, text, {
            "title": title,
            "description": description,
            "image": image,
            "canonical": canonical,
            "published": published_raw or published.isoformat(),
        }))
    if not candidates:
        raise SystemExit("Nebyl nalezen týdenní přehled akcí.")
    _, path, text, data = max(candidates, key=lambda item: item[0])
    return path, text, data


def strip_managed(text: str) -> str:
    return re.sub(rf"\s*{re.escape(START)}.*?{re.escape(END)}\s*", "\n", text, flags=re.S)


def update_home(data: dict[str, str], filename: str) -> None:
    path = ROOT / "index.html"
    text = strip_managed(path.read_text(encoding="utf-8"))
    href = f"/clanky/{filename}"
    title = escape(data["title"])
    description = escape(data["description"])
    published = datetime.fromisoformat(data["published"])
    date_label = published.strftime("%d. %m. %Y · %H:%M")

    hero = f'''<article class="lead" data-weekly-events-hero>
        <div class="photo" style="background:linear-gradient(135deg,#143342,#39748a 58%,#b58b25)"><span>TÝDENNÍ PŘEHLED</span><strong>27/7–2/8</strong></div>
        <div class="copy">
          <small>KULTURA · VOLNÝ ČAS · {date_label}</small>
          <h1>{title}</h1>
          <p>{description}</p>
          <a class="btn" href="{href}">Otevřít celý přehled →</a>
        </div>
      </article>'''
    text, count = re.subn(r'<article class="lead"[^>]*>.*?</article>', hero, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("Na titulce se nepodařilo najít hlavní článek.")

    card = f'''\n      {START}
      <article class="article-card events" data-weekly-events-card>
        <div class="visual" style="background:linear-gradient(135deg,#143342,#39748a 58%,#b58b25)"><strong>Kam příští týden</strong></div>
        <div class="article-body">
          <span class="meta">{date_label} · Kultura a volný čas</span>
          <h3>{title}</h3>
          <p>{description}</p>
          <a class="read-more" href="{href}">Otevřít celý přehled →</a>
        </div>
      </article>
      {END}\n'''
    text, count = re.subn(r'(<div class="article-list">)', r'\1' + card, text, count=1)
    if count != 1:
        raise SystemExit("Na titulce se nepodařilo najít seznam článků.")
    path.write_text(text, encoding="utf-8")


def update_archive(data: dict[str, str], filename: str) -> None:
    path = ROOT / "clanky" / "index.html"
    text = strip_managed(path.read_text(encoding="utf-8"))
    href = f"/clanky/{filename}"
    title = escape(data["title"])
    description = escape(data["description"])
    published = datetime.fromisoformat(data["published"])
    date_label = published.strftime("%d. %m. %Y v %H:%M")
    item = f'''\n    {START}
    <article class="archive-item events" data-weekly-events-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#143342,#39748a 58%,#b58b25)"><strong>Kam příští týden</strong></div>
      <div class="archive-body">
        <span class="archive-meta">{date_label} · Kultura a volný čas</span>
        <h2>{title}</h2>
        <p>{description}</p>
        <a href="{href}">Otevřít celý přehled →</a>
      </div>
    </article>
    {END}\n'''
    text, count = re.subn(r'(<section class="archive-list"[^>]*>)', r'\1' + item, text, count=1)
    if count != 1:
        raise SystemExit("V archivu se nepodařilo najít seznam článků.")

    script_pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S | re.I)
    def replace_schema(match: re.Match[str]) -> str:
        try:
            data_json = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        graph = data_json.get("@graph", []) if isinstance(data_json, dict) else []
        for node in graph:
            if isinstance(node, dict) and node.get("@type") == "ItemList":
                items = [item for item in node.get("itemListElement", []) if item.get("url") != data["canonical"]]
                items.insert(0, {"@type": "ListItem", "position": 1, "url": data["canonical"], "name": data["title"]})
                for position, entry in enumerate(items, start=1):
                    entry["position"] = position
                node["itemListElement"] = items
                node["numberOfItems"] = len(items)
        return match.group(1) + json.dumps(data_json, ensure_ascii=False, indent=2) + match.group(3)
    text = script_pattern.sub(replace_schema, text, count=1)
    path.write_text(text, encoding="utf-8")


def update_rss(data: dict[str, str]) -> None:
    path = ROOT / "rss.xml"
    text = strip_managed(path.read_text(encoding="utf-8"))
    published = datetime.fromisoformat(data["published"])
    pub_date = published.strftime("%a, %d %b %Y %H:%M:%S %z")
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{pub_date}</lastBuildDate>", text, count=1)
    item = f'''\n    {START}
    <item>
      <title>{xml_escape(data['title'])}</title>
      <description><![CDATA[{data['description']}]]></description>
      <link>{data['canonical']}</link>
      <guid isPermaLink="true">{data['canonical']}</guid>
      <pubDate>{pub_date}</pubDate>
      <category>Kultura</category>
      <category>Volný čas</category>
      <category>Kadaň</category>
      <category>Akce v okolí</category>
      <szn:image><szn:url>{data['image']}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>
    {END}\n'''
    anchor = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if anchor not in text:
        raise SystemExit("V RSS nebyl nalezen vkládací bod.")
    text = text.replace(anchor, anchor + item, 1)
    path.write_text(text, encoding="utf-8")


def update_sitemap(data: dict[str, str]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    canonical = data["canonical"]
    if canonical not in text:
        entry = f"  <url><loc>{canonical}</loc><lastmod>{data['published'][:10]}</lastmod></url>\n"
        text = text.replace("</urlset>", entry + "</urlset>", 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    article_path, _, data = latest_article()
    update_home(data, article_path.name)
    update_archive(data, article_path.name)
    update_rss(data)
    update_sitemap(data)
    print(f"Propagován týdenní přehled: {article_path.name}")


if __name__ == "__main__":
    main()
