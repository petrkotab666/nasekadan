#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "avies-nemocnice-kadan.html"
DRAFT = ROOT / ".github" / "drafts" / "avies-nemocnice-kadan.html"
URL = "https://nasekadan.cz/clanky/avies-nemocnice-kadan.html"
TITLE = "Kdo nastavil nákupy léčiv od AVIES? Nemocnice za sedm let zaplatila téměř 170 milionů"
DESCRIPTION = (
    "Nemocnice Kadaň zaplatila AVIES v letech 2019 až 2025 téměř 170 milionů korun. "
    "Rekonstruujeme historii vztahu a hledáme chybějící dokument pro rok 2024."
)
PUBLISHED = "2026-07-27T05:00:00+02:00"


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def ensure_article() -> None:
    if not ARTICLE.exists():
        if not DRAFT.exists():
            raise FileNotFoundError(DRAFT)
        ARTICLE.parent.mkdir(parents=True, exist_ok=True)
        ARTICLE.write_bytes(DRAFT.read_bytes())

    text = ARTICLE.read_text(encoding="utf-8")
    text = text.replace(
        "noindex,nofollow",
        "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1",
    )
    text = text.replace("../../", "../")
    text = text.replace("PŘIPRAVOVANÝ ČLÁNEK", "27. ČERVENCE 2026")
    text = re.sub(
        r'<div class="sidebox preview-note">.*?</div>',
        "",
        text,
        count=1,
        flags=re.S,
    )

    if "article:published_time" not in text:
        metadata = (
            f'<meta property="article:published_time" content="{PUBLISHED}">'
            f'<meta property="article:modified_time" content="{PUBLISHED}">'
            '<script type="application/ld+json">'
            + json.dumps(
                {
                    "@context": "https://schema.org",
                    "@type": "NewsArticle",
                    "headline": TITLE,
                    "description": DESCRIPTION,
                    "datePublished": PUBLISHED,
                    "dateModified": PUBLISHED,
                    "author": {"@type": "Organization", "name": "Naše Kadaň"},
                    "publisher": {"@type": "Organization", "name": "Naše Kadaň"},
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "</script>"
        )
        text = text.replace("</head>", metadata + "</head>", 1)
    write(ARTICLE, text)


def update_previous_teaser() -> None:
    path = ROOT / "clanky" / "nemocnice-kadan-software-kyberbezpecnost.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    scheduled = (
        '<span data-avies-teaser-state="scheduled" style="display:inline-block;padding:10px 14px;'
        'border:1px solid rgba(255,255,255,.4);border-radius:999px;color:#fff;font-weight:900">'
        'Vyjde v pondělí 27. 7. v 5:00</span>'
    )
    published = (
        '<a href="/clanky/avies-nemocnice-kadan.html" data-avies-teaser-state="published" '
        'style="display:inline-flex;padding:13px 18px;border-radius:10px;background:#fff;'
        'color:#8f2027;font-weight:900;text-decoration:none">Přečíst navazující článek →</a>'
    )
    if scheduled in text:
        write(path, text.replace(scheduled, published, 1))


def article_image() -> str:
    text = ARTICLE.read_text(encoding="utf-8")
    match = re.search(
        r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)',
        text,
        flags=re.I,
    )
    return match.group(1) if match else "https://nasekadan.cz/social-card.png"


def latest_article_is_avies() -> bool:
    newest: tuple[datetime, str] | None = None
    for path in (ROOT / "clanky").glob("*.html"):
        if path.name == "index.html":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(
            r'(?:article:published_time["\'][^>]*content=["\']|["\']datePublished["\']\s*:\s*["\'])([^"\']+)',
            text,
            flags=re.I,
        )
        if not match:
            continue
        raw = match.group(1).replace("Z", "+00:00")
        try:
            value = datetime.fromisoformat(raw)
        except ValueError:
            continue
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        key = (value.astimezone(timezone.utc), path.name)
        if newest is None or key > newest:
            newest = key
    return newest is None or newest[1] == ARTICLE.name


def update_home() -> None:
    path = ROOT / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if latest_article_is_avies():
        hero = '''<article class="lead" data-avies-hero>
        <div class="photo" style="background:radial-gradient(circle at 78% 18%,rgba(255,255,255,.15),transparent 27%),linear-gradient(135deg,#121f27,#334f5e 55%,#9d222a)"><span>NOVÁ ANALÝZA</span><strong>169,8 MIL.</strong></div>
        <div class="copy">
          <small>NEMOCNICE KADAŇ · VEŘEJNÉ PENÍZE · 27. 07. 2026 · 5:00</small>
          <h1>Kdo nastavil nákupy léčiv od AVIES?</h1>
          <p>Nemocnice za sedm let zaplatila téměř 170 milionů. Rekonstruujeme historii vztahu a hledáme chybějící dokument pro rok 2024.</p>
          <a class="btn" href="/clanky/avies-nemocnice-kadan.html">Přečíst celou analýzu →</a>
        </div>
      </article>'''
        text = re.sub(
            r'<article class="lead"[^>]*>.*?</article>',
            hero,
            text,
            count=1,
            flags=re.S,
        )
    if "data-avies-card" not in text:
        card = '''
      <article class="article-card hospital" data-avies-card>
        <div class="visual"><strong>AVIES a nemocnice</strong></div>
        <div class="article-body">
          <span class="meta">27. 7. 2026 · 5:00 · Zdravotnictví a veřejné peníze</span>
          <h3>Sedm let plateb, téměř 170 milionů a chybějící dokument</h3>
          <p>Co je doložené, kdo dlouhodobý systém převzal a proč zůstává klíčový rok 2024.</p>
          <a class="read-more" href="/clanky/avies-nemocnice-kadan.html">Přečíst analýzu →</a>
        </div>
      </article>
'''
        marker = '<div class="article-list">'
        if marker in text:
            text = text.replace(marker, marker + card, 1)
    write(path, text)


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        text,
        flags=re.S,
    )
    if match:
        try:
            data = json.loads(match.group(1))
            graph = data.get("@graph", [])
            itemlist = next((item for item in graph if item.get("@type") == "ItemList"), None)
            if itemlist is not None:
                existing = [
                    item
                    for item in itemlist.get("itemListElement", [])
                    if item.get("url") != URL
                ]
                elements = [{"@type": "ListItem", "position": 1, "url": URL, "name": TITLE}]
                for position, item in enumerate(existing, start=2):
                    item["position"] = position
                    elements.append(item)
                itemlist["itemListElement"] = elements
                itemlist["numberOfItems"] = len(elements)
                replacement = (
                    '<script type="application/ld+json">\n'
                    + json.dumps(data, ensure_ascii=False, indent=2)
                    + "\n  </script>"
                )
                text = text[: match.start()] + replacement + text[match.end() :]
        except (ValueError, TypeError):
            pass

    if "data-avies-card" not in text:
        item = '''
    <article class="archive-item hospital" data-avies-card>
      <div class="archive-visual"><strong>AVIES a nemocnice</strong></div>
      <div class="archive-body">
        <span class="archive-meta">27. července 2026 v 5:00 · Zdravotnictví a veřejné peníze</span>
        <h2>Kdo nastavil nákupy léčiv od AVIES? Nemocnice za sedm let zaplatila téměř 170 milionů</h2>
        <p>Analýza sedmi let plateb, vývoje smluvního vztahu, role jednotlivých vedení a veřejné dokumentační mezery roku 2024.</p>
        <a href="/clanky/avies-nemocnice-kadan.html">Přečíst celou analýzu →</a>
      </div>
    </article>
'''
        marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
        if marker in text:
            text = text.replace(marker, marker + item, 1)
    write(path, text)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    image = article_image()
    item = f'''    <item>
      <title>{TITLE}</title>
      <description><![CDATA[{DESCRIPTION}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>Mon, 27 Jul 2026 05:00:00 +0200</pubDate>
      <category>Nemocnice Kadaň</category>
      <category>Veřejné peníze</category>
      <category>AVIES</category>
      <szn:image><szn:url>{image}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>'''
    pattern = rf'\s*<item>(?:(?!</item>).)*?{re.escape(URL)}(?:(?!</item>).)*?</item>'
    if re.search(pattern, text, flags=re.S):
        text = re.sub(pattern, "\n" + item, text, count=1, flags=re.S)
    else:
        marker = "    <item>"
        if marker in text:
            text = text.replace(marker, item + "\n\n" + marker, 1)
    text = re.sub(
        r"<lastBuildDate>.*?</lastBuildDate>",
        "<lastBuildDate>Mon, 27 Jul 2026 05:00:00 +0200</lastBuildDate>",
        text,
        count=1,
    )
    write(path, text)


def main() -> int:
    ensure_article()
    update_previous_teaser()
    update_home()
    update_archive()
    update_rss()
    print("Článek AVIES byl připraven jako veřejný a zařazen do webu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
