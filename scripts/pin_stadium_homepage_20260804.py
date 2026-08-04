#!/usr/bin/env python3
from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARTICLE = ROOT / "clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html"
TARGET_HREF = "/clanky/klasterec-ochlazeni-zimni-stadion-kadan-2026.html"
TARGET_TITLE = "Kadaň otevřela zimní stadion lidem před vedrem. Přijít lze denně od 8 do 18 hodin"
TARGET_DESC = (
    "Město Kadaň potvrdilo, že lidé mohou v horkých dnech využít zimní stadion k ochlazení. "
    "Vchod je od koupaliště naproti restauraci a na místě je možné se občerstvit."
)
TARGET_IMAGE = "https://nasekadan.cz/social/klasterec-ochlazeni-zimni-stadion-kadan-2026-kadan-open-20260804.png"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def extract(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.I | re.S)
    return clean(match.group(1)) if match else default


def main() -> int:
    article = ARTICLE.read_text(encoding="utf-8")
    if 'article:published_time" content="2026-08-03T22:05:00+02:00' not in article:
        raise SystemExit("Původní datum článku se změnilo; připnutí zastaveno.")

    home = HOME.read_text(encoding="utf-8")
    hero_match = re.search(r'  <section class="wrap hero" id="clanky".*?</section>', home, flags=re.S)
    if not hero_match:
        raise SystemExit("Na titulce chybí hlavní hero sekce.")

    old = hero_match.group(0)
    current_href = extract(r'data-latest-article-href="([^"]+)"', old, "/clanky/")
    current_title = extract(r'<article class="lead">.*?<h1>(.*?)</h1>', old, "Další aktuální článek")
    current_desc = extract(r'<article class="lead">.*?<div class="copy">.*?<p>(.*?)</p>', old, "Přečtěte si další aktuální článek.")

    if current_href == TARGET_HREF:
        # Již připnuto; pouze ověř konzistenci.
        if f"<h1>{TARGET_TITLE}</h1>" not in old:
            raise SystemExit("Cílový článek je připnutý s neočekávaným titulkem.")
        print("Titulní článek je již správně připnutý.")
        return 0

    aside = f'''    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">Nejnovější původní publikace</p>
      <h2>{escape(current_title)}</h2>
      <p>{escape(current_desc)}</p>
      <a class="aside-button" href="{escape(current_href, quote=True)}">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div>
    </aside>'''

    hero = f'''  <section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{TARGET_HREF}" data-editorial-pin="stadium-cooling-20260805-1800">
    <article class="lead"><div class="photo" style="background-image:linear-gradient(90deg,rgba(7,23,34,.76),rgba(7,23,34,.14) 72%),url('{TARGET_IMAGE}');background-color:#0b202b;background-size:cover;background-position:center;background-repeat:no-repeat"><span>KADAŇ · VEDRO · AKTUALIZOVÁNO</span><strong>4. 8. 2026</strong></div><div class="copy"><small>KADAŇ · VEDRO · PRAKTICKÉ INFORMACE · AKTUALIZOVÁNO 4. 8. 2026</small><h1>{TARGET_TITLE}</h1><p>{TARGET_DESC}</p><a class="btn" href="{TARGET_HREF}">Přečíst aktualizovaný článek →</a></div></article>
{aside}
  </section>'''

    updated = home[:hero_match.start()] + hero + home[hero_match.end():]
    if updated == home:
        raise SystemExit("Připnutí neprovedlo žádnou změnu.")
    if f'data-latest-article-href="{TARGET_HREF}"' not in updated:
        raise SystemExit("Připnutí se nepodařilo vložit.")
    if current_href not in updated:
        raise SystemExit("Původní nejnovější článek se nezachoval v bočním bloku.")
    HOME.write_text(updated, encoding="utf-8", newline="\n")
    print(f"Připnuto; boční článek: {current_title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
