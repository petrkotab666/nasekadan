#!/usr/bin/env python3
"""Ensure the scheduled Tušimice article is present at the top of rss.xml."""
from __future__ import annotations

import html
import re
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path

SLUG = "jaderne-tusimice-smr-voda-doprava-eia-2026"
URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
ARTICLE = Path("clanky") / f"{SLUG}.html"
RSS = Path("rss.xml")

article = ARTICLE.read_text(encoding="utf-8")
rss = RSS.read_text(encoding="utf-8")

if URL in rss:
    print("RSS už článek obsahuje.")
    raise SystemExit(0)

def meta(name: str, *, prop: bool = False) -> str:
    attr = "property" if prop else "name"
    pattern = rf'<meta\s+{attr}=["\']{re.escape(name)}["\']\s+content=["\']([^"\']+)["\']'
    match = re.search(pattern, article, re.IGNORECASE)
    if not match:
        raise SystemExit(f"V článku chybí meta {name}")
    return html.unescape(match.group(1)).strip()

title_match = re.search(r"<h1[^>]*>(.*?)</h1>", article, re.IGNORECASE | re.DOTALL)
if not title_match:
    raise SystemExit("V článku chybí H1")
title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
description = meta("description")
image = meta("og:image", prop=True)
published = meta("article:published_time", prop=True)
dt = datetime.fromisoformat(published)
pub_date = format_datetime(dt)

item = f'''    <item>
      <title>{html.escape(title)}</title>
      <description><![CDATA[{description.replace("]]>", "]]&gt;")}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{pub_date}</pubDate>
      <category>ENERGETIKA</category>
      <category>ŽIVOTNÍ PROSTŘEDÍ</category>
      <category>DOPRAVA</category>
      <szn:image><szn:url>{html.escape(image)}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat>
      <geo:long>13.271307</geo:long>
    </item>

'''

anchor = re.search(r'^(\s*<atom:link[^>]+/>\s*)$', rss, re.MULTILINE)
if not anchor:
    raise SystemExit("V RSS chybí atom:link kotva")
rss = rss[: anchor.end()] + "\n" + item + rss[anchor.end() :]
rss = re.sub(
    r"<lastBuildDate>.*?</lastBuildDate>",
    f"<lastBuildDate>{pub_date}</lastBuildDate>",
    rss,
    count=1,
    flags=re.DOTALL,
)
RSS.write_text(rss, encoding="utf-8")
print(f"RSS doplněno: {URL}")
