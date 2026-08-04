#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape, unescape
from pathlib import Path
from hashlib import sha256
import json
import re
import subprocess
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
SLUG = "klasterec-ochlazeni-zimni-stadion-kadan-2026"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
SOCIAL_REL = f"/social/{SLUG}-kadan-open-20260804.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
OLD_TITLE = "Klášterec otevřel zimní stadion lidem před vedrem. Mohla by se přidat i Kadaň?"
TITLE = "Kadaň otevřela zimní stadion lidem před vedrem. Přijít lze denně od 8 do 18 hodin"
DESC = (
    "Město Kadaň potvrdilo, že lidé mohou v horkých dnech využít zimní stadion k ochlazení. "
    "Vchod je od koupaliště naproti restauraci a na místě je možné se občerstvit."
)
PUBLISHED = "2026-08-03T22:05:00+02:00"
MODIFIED = "2026-08-04T13:10:00+02:00"
MODIFIED_HUMAN = "4. SRPNA 2026 · 13:10"
RSS_DATE = format_datetime(datetime.fromisoformat(MODIFIED))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def replace_meta(text: str, attr: str, key: str, value: str) -> str:
    patterns = [
        rf'<meta\s+{attr}="{re.escape(key)}"\s+content="[^"]*"\s*/?>',
        rf'<meta\s+content="[^"]*"\s+{attr}="{re.escape(key)}"\s*/?>',
    ]
    replacement = f'<meta {attr}="{key}" content="{escape(value, quote=True)}">'
    for pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            return re.sub(pattern, replacement, text, count=1, flags=re.I)
    return text.replace("</head>", replacement + "\n</head>", 1)


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#08263b")
    draw = ImageDraw.Draw(image)
    for y in range(630):
        ratio = y / 629
        draw.line(
            (0, y, 1200, y),
            fill=(int(8 + 14 * ratio), int(38 + 70 * ratio), int(59 + 78 * ratio)),
        )

    draw.rounded_rectangle((680, 64, 1145, 565), radius=38, fill="#e7f8ff", outline="#ffffff", width=7)
    draw.rounded_rectangle((718, 122, 1107, 510), radius=150, fill="#fbfeff", outline="#73bfe1", width=10)
    draw.line((912, 126, 912, 506), fill="#b72d3b", width=9)
    draw.arc((790, 195, 1035, 440), 180, 360, fill="#b72d3b", width=13)
    draw.rounded_rectangle((820, 290, 1010, 420), radius=18, outline="#c62e3d", width=11)
    for x in range(835, 1000, 28):
        draw.line((x, 300, x, 410), fill="#c62e3d", width=2)
    for y in range(306, 412, 23):
        draw.line((829, y, 1002, y), fill="#c62e3d", width=2)
    draw.ellipse((770, 445, 830, 475), fill="#111820")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 58)
    medium = ImageFont.truetype(bold_path, 31)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 21)

    draw.rounded_rectangle((58, 48, 430, 103), radius=27, fill="#a9232b")
    draw.text((84, 65), "NAŠE KADAŇ · AKTUALIZOVÁNO", font=tiny, fill="white")
    for index, line in enumerate(("Kadaň otevřela", "zimní stadion", "lidem před vedrem")):
        draw.text((60, 140 + index * 72), line, font=bold, fill="white")
    draw.text((64, 381), "Každý den od 8:00 do 18:00", font=medium, fill="#ffe29a")
    draw.text((64, 431), "Vchod od koupaliště naproti restauraci", font=small, fill="#e9f8ff")
    draw.text((64, 476), "Posezení, chládek a občerstvení na místě", font=small, fill="#e9f8ff")
    draw.text((64, 570), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def update_article() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    text = re.sub(r"<title>.*?</title>", f"<title>{escape(TITLE)} | Naše Kadaň</title>", text, count=1, flags=re.S)
    text = replace_meta(text, "name", "description", DESC)
    text = replace_meta(text, "property", "og:title", TITLE)
    text = replace_meta(text, "property", "og:description", DESC)
    text = replace_meta(text, "property", "og:image", SOCIAL_URL)
    text = replace_meta(text, "name", "twitter:title", TITLE)
    text = replace_meta(text, "name", "twitter:description", DESC)
    text = replace_meta(text, "name", "twitter:image", SOCIAL_URL)
    text = replace_meta(text, "property", "article:modified_time", MODIFIED)

    def patch_schema(match: re.Match[str]) -> str:
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            data["headline"] = TITLE
            data["description"] = DESC
            data["datePublished"] = PUBLISHED
            data["dateModified"] = MODIFIED
            data["image"] = [SOCIAL_URL]
        elif isinstance(data, dict) and data.get("@type") == "BreadcrumbList":
            items = data.get("itemListElement")
            if isinstance(items, list) and items:
                items[-1]["name"] = TITLE
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"

    text = re.sub(r'<script(?:\s+data-nasekadan-breadcrumbs="1")?\s+type="application/ld\+json">(.*?)</script>', patch_schema, text, flags=re.S)
    text = re.sub(r'<p class="tag">.*?</p>', f'<p class="tag">KADAŇ · VEDRO · PRAKTICKÉ INFORMACE · AKTUALIZOVÁNO · {MODIFIED_HUMAN}</p>', text, count=1, flags=re.S)
    text = re.sub(r'<h1>.*?</h1>', f'<h1>{escape(TITLE)}</h1>', text, count=1, flags=re.S)
    text = re.sub(r'<p class="leadtext">.*?</p>', f'<p class="leadtext"><strong>{escape(DESC)}</strong></p>', text, count=1, flags=re.S)
    text = re.sub(
        r'<img class="hero-image"[^>]*>',
        f'<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k otevření kadaňského zimního stadionu jako místa pro ochlazení během veder">',
        text,
        count=1,
        flags=re.S,
    )

    body = f'''
<div class="clarity"><strong>Aktualizace 4. srpna ve 13:10</strong><p>Otázka položená v původním článku je zodpovězená. Město Kadaň v úterý zveřejnilo, že zimní stadion mohou lidé v horkých dnech využívat k ochlazení.</p></div>
<p>Kadaňský zimní stadion je podle oznámení města otevřený veřejnosti <strong>každý den od 8:00 do 18:00</strong>. Lidé si mohou přinést knihu nebo noviny, posedět v chladnějším prostředí a na čas uniknout z rozpálených ulic či přehřátých bytů.</p>
<div class="fact-grid"><div class="fact"><strong>8:00–18:00</strong><span>každodenní čas určený pro návštěvníky</span></div><div class="fact"><strong>od koupaliště</strong><span>vchod naproti vstupu do místní restaurace</span></div><div class="fact"><strong>občerstvení</strong><span>restaurace je podle města návštěvníkům k dispozici</span></div></div>
<h2>Kudy se na stadion dostat</h2>
<p>Vstup je připravený <strong>ze strany od koupaliště, přímo naproti vstupu do restaurace</strong>. Město doporučuje přijít si do chladnějšího prostředí odpočinout. Při troše štěstí mohou návštěvníci sledovat také trénink krasobruslařek, které mají na stadionu soustředění.</p>
<div class="proposal"><h2>Praktické informace</h2><ul><li>otevřeno je každý den od 8:00 do 18:00,</li><li>nejde o veřejné bruslení, ale o možnost posedět v chladnějším prostoru,</li><li>vchod je od koupaliště naproti restauraci,</li><li>občerstvení zajišťuje místní restaurace,</li><li>město v příspěvku neuvedlo konečné datum nabídky ani samostatné vstupné.</li></ul></div>
<h2>Kadaň následovala příklad sousedního Klášterce</h2>
<p>Původní článek Naší Kadaně vznikl poté, co stejnou možnost nabídlo sousední město Klášterec nad Ohří. V pondělí 3. srpna jsme proto popsali klášterecký příklad a položili otázku, zda se může přidat také Kadaň. O den později město veřejnou nabídku potvrdilo.</p>
<p>Klášterecký nápad přitom není nový. Město podobné opatření využilo už během mimořádně horkého srpna 2015. Obě sousední města tak nyní ukazují jednoduchý způsob, jak v době veder zpřístupnit lidem prostor, který je díky běžnému provozu stadionu přirozeně chladnější.</p>
<p><strong>Návštěvníci by měli respektovat pokyny obsluhy stadionu a probíhající sportovní provoz.</strong></p>
'''
    pattern = re.compile(r'(<img class="hero-image"[^>]*>\s*)(.*?)(<div class="sources">)', re.S)
    if not pattern.search(text):
        raise RuntimeError("Nelze najít tělo článku mezi hlavním obrázkem a zdroji.")
    text = pattern.sub(r"\1" + body + r"\3", text, count=1)

    sources = '''<div class="sources"><h2>Zdroje a upřesnění</h2><ul><li>Oficiální facebooková stránka Města Kadaň: oznámení „Račtež se zchladit. Dovalte na zimák!“, zveřejněné 4. srpna 2026 krátce před 13. hodinou.</li><li><a href="https://www.sportkadan.cz/arealy/zimni-stadion" rel="noopener">Sportovní zařízení Kadaň: Zimní stadion</a>.</li><li><a href="https://www.klasterec.cz/kontakty/tiskove-zpravy/v-extremnich-vedrech-se-muzete-zchladit-na-zimnim-stadione-201cs.html" rel="noopener">Město Klášterec nad Ohří: archivní nabídka ochlazení na stadionu z roku 2015</a>.</li></ul><p>Článek byl původně zveřejněn 3. srpna 2026 jako podnět. Dne 4. srpna byl zásadně aktualizován po oficiálním potvrzení Města Kadaň.</p></div></article>'''
    text = re.sub(r'<div class="sources">.*?</div></article>', sources, text, count=1, flags=re.S)

    aside = '''<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>každý den 8:00–18:00,</li><li>vchod ze strany od koupaliště,</li><li>naproti vstupu do restaurace,</li><li>možnost občerstvení,</li><li>nejde o veřejné bruslení.</li></ul></div><div class="sidebox"><h3>Adresa stadionu</h3><p><strong>U Stadionu 2028, Kadaň</strong><br>kontakt stadionu: 777 805 290</p></div><div data-promos data-context="sidebar"></div></aside>'''
    text = re.sub(r'<aside class="sticky">.*?</aside>', aside, text, count=1, flags=re.S)
    write(ARTICLE, text)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    item_pattern = re.compile(r'<item>.*?' + re.escape(URL) + r'.*?</item>', re.S)
    item = (
        f'<item><title>{xml_escape(TITLE)}</title><description><![CDATA[{DESC}]]></description>'
        f'<link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{RSS_DATE}</pubDate>'
        '<category>Kadaň</category><category>Vedro</category><category>Praktické informace</category><category>Aktualizováno</category>'
        f'<szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>'
    )
    if item_pattern.search(text):
        text = item_pattern.sub(item, text, count=1)
    else:
        text = text.replace('<item>', item + '\n    <item>', 1)
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{RSS_DATE}</lastBuildDate>', text, count=1)
    write(path, text)


def update_sitemaps() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    node_pattern = re.compile(r'<url>\s*<loc>' + re.escape(URL) + r'</loc>(.*?)</url>', re.S)
    if node_pattern.search(text):
        def repl(match: re.Match[str]) -> str:
            inner = match.group(1)
            if '<lastmod>' in inner:
                inner = re.sub(r'<lastmod>.*?</lastmod>', '<lastmod>2026-08-04</lastmod>', inner, count=1)
            else:
                inner += '<lastmod>2026-08-04</lastmod>'
            return f'<url><loc>{URL}</loc>{inner}</url>'
        text = node_pattern.sub(repl, text, count=1)
    else:
        text = text.replace('</urlset>', f'  <url><loc>{URL}</loc><lastmod>2026-08-04</lastmod></url>\n</urlset>', 1)
    write(path, text)

    path = ROOT / "news-sitemap.xml"
    text = path.read_text(encoding="utf-8")
    node_pattern = re.compile(r'(<url>\s*<loc>' + re.escape(URL) + r'</loc>.*?<news:title>).*?(</news:title>.*?</url>)', re.S)
    if node_pattern.search(text):
        text = node_pattern.sub(r'\1' + xml_escape(TITLE) + r'\2', text, count=1)
    write(path, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'- \[[^\]]+\]\(' + re.escape(URL) + r'\)\n(?:  .*\n)?')
    entry = f'- [{TITLE}]({URL})\n  {DESC}\n'
    if pattern.search(text):
        text = pattern.sub(entry, text, count=1)
    else:
        marker = '## Nejnovější vlastní články\n\n'
        text = text.replace(marker, marker + entry, 1) if marker in text else entry + '\n' + text
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    found = False
    for article in data.get("articles", []):
        if isinstance(article, dict) and article.get("url") == URL:
            article.update({
                "title": TITLE,
                "h1": TITLE,
                "published_at": PUBLISHED,
                "modified_at": MODIFIED,
                "organizations": ["Město Kadaň", "Sportovní zařízení Kadaň", "Město Klášterec nad Ohří"],
                "places": ["Kadaň", "Klášterec nad Ohří"],
                "cases": ["Ochlazení veřejnosti na zimním stadionu během veder"],
                "topics": ["Vedro", "Veřejná služba", "Zimní stadion", "Praktické informace", "Aktualizace"],
                "fingerprint": sha256("kadan-klasterec-zimni-stadion-ochlazeni-vedra-2026".encode()).hexdigest()[:24],
                "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
                "publication_status": "published",
            })
            found = True
            break
    if not found:
        raise RuntimeError("Aktualizovaný článek chybí v kanonickém registru.")
    data["article_count"] = len(data.get("articles", []))
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["canonical_duplicate_filter"] = True
    validation["live_update_existing_article"] = True
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def promote_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'<section class="wrap hero" id="clanky".*?</section>', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Na titulce chybí hlavní hero sekce.")
    current = match.group(0)
    current_href = re.search(r'data-latest-article-href="([^"]+)"', current)
    current_title = re.search(r'<div class="copy">.*?<h1>(.*?)</h1>', current, re.S)
    current_desc = re.search(r'<div class="copy">.*?<p>(.*?)</p>', current, re.S)
    aside_href = current_href.group(1) if current_href and current_href.group(1) != REL else "/clanky/"
    aside_title = clean(current_title.group(1)) if current_title else "Další aktuální články"
    aside_desc = clean(current_desc.group(1)) if current_desc else "Přečtěte si další aktuální zprávy."
    hero = f'''<section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{REL}">
    <article class="lead"><div class="photo" style="background-image:linear-gradient(90deg,rgba(7,23,34,.76),rgba(7,23,34,.14) 72%),url('{SOCIAL_URL}');background-color:#0b202b;background-size:cover;background-position:center;background-repeat:no-repeat"><span>KADAŇ · VEDRO · AKTUALIZOVÁNO</span><strong>4. 8. 2026</strong></div><div class="copy"><small>KADAŇ · VEDRO · PRAKTICKÉ INFORMACE · AKTUALIZOVÁNO 4. 8. 2026 · 13:10</small><h1>{escape(TITLE)}</h1><p>{escape(DESC)}</p><a class="btn" href="{REL}">Přečíst aktualizovaný článek →</a></div></article>
    <aside class="current-aside"><p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p><p class="aside-date">Nejnovější původní publikace</p><h2>{escape(aside_title)}</h2><p>{escape(aside_desc)}</p><a class="aside-button" href="{escape(aside_href)}">Přečíst článek →</a><div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div></aside>
  </section>'''
    text = text[:match.start()] + hero + text[match.end():]
    write(path, text)


def promote_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    card_pattern = re.compile(r'\s*<article class="article-card[^"]*" data-auto-article="' + re.escape(SLUG) + r'">.*?</article>', re.S)
    match = card_pattern.search(text)
    if not match:
        raise RuntimeError("Aktualizovaný článek chybí na první stránce archivu.")
    card = match.group(0).strip()
    card = re.sub(r'<span class="meta">.*?</span>', '<span class="meta">AKTUALIZOVÁNO 4. 8. 2026 · 13:10 · KADAŇ · VEDRO · PRAKTICKÉ INFORMACE</span>', card, count=1, flags=re.S)
    text = text[:match.start()] + text[match.end():]
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    text = text.replace(marker, marker + '\n    ' + card, 1)

    schema_pattern = re.compile(r'<script data-nk-archive-schema="1" type="application/ld\+json">(.*?)</script>', re.S)
    schema_match = schema_pattern.search(text)
    if schema_match:
        data = json.loads(schema_match.group(1))
        items = data.get("itemListElement", [])
        items = [item for item in items if item.get("url") != URL]
        items.insert(0, {"@type": "ListItem", "position": 1, "url": URL, "name": TITLE})
        for pos, item in enumerate(items, 1):
            item["position"] = pos
        data["itemListElement"] = items
        text = text[:schema_match.start(1)] + json.dumps(data, ensure_ascii=False) + text[schema_match.end(1):]

    graph_pattern = re.compile(r'<script type="application/ld\+json">(\{.*?"@graph".*?\})</script>', re.S)
    graph_match = graph_pattern.search(text)
    if graph_match:
        try:
            data = json.loads(graph_match.group(1))
            itemlist = next((x for x in data.get("@graph", []) if isinstance(x, dict) and x.get("@type") == "ItemList"), None)
            if itemlist:
                items = [item for item in itemlist.get("itemListElement", []) if item.get("url") != URL]
                items.insert(0, {"@type": "ListItem", "position": 1, "url": URL, "name": TITLE})
                for pos, item in enumerate(items, 1):
                    item["position"] = pos
                itemlist["itemListElement"] = items
                itemlist["numberOfItems"] = len(items)
                text = text[:graph_match.start(1)] + json.dumps(data, ensure_ascii=False, indent=2) + text[graph_match.end(1):]
        except (json.JSONDecodeError, StopIteration):
            pass
    write(path, text)


def validate() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    if f"<h1>{TITLE}</h1>" not in article or "8:00 do 18:00" not in article or OLD_TITLE in article:
        raise RuntimeError("Článek nebyl úplně aktualizován.")
    for path in (ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "llms.txt", ROOT / "data/published-content-index.json"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if URL not in text and REL not in text:
            raise RuntimeError(f"Aktualizovaný článek chybí v {path}.")
    if TITLE not in (ROOT / "index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Nový titulek chybí na titulní stránce.")
    if TITLE not in (ROOT / "clanky/index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Nový titulek chybí v archivu.")
    if '/pocasi.js' not in (ROOT / "index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Aktualizace by odstranila počasí.")


def main() -> int:
    make_social()
    update_article()
    update_registry()
    subprocess.run(["python3", "scripts/enforce_article_visibility.py"], cwd=ROOT, check=True)
    update_rss()
    update_sitemaps()
    update_llms()
    promote_home()
    promote_archive()
    validate()
    print(f"Aktualizováno: {URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
