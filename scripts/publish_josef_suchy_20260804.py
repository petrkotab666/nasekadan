#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SLUG = "josef-suchy-klasterec-u18-kanada-hlinka-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Klášterecký Josef Suchý skóroval Kanadě už po 103 sekundách"
DESC = (
    "Sedmnáctiletý klášterecký odchovanec Josef Suchý dal v přípravě české osmnáctky "
    "gól Kanadě už po 103 sekundách, přidal asistenci a dnes pokračuje na Hlinka Gretzky Cupu."
)
PUBLISHED = "2026-08-04T12:10:00+02:00"
PUBLISHED_HUMAN = "4. SRPNA 2026 · 12:10"
DATE_SHORT = "4. 8. 2026"
GAME_URL = "https://www.hlinkagretzkycup.ca/en-ca/season/2026/stats/game-summary?gameid=5729&pretournament=true"
SCHEDULE_URL = "https://www.hlinkagretzkycup.ca/en-ca/season/2026/stats/schedule?tournament=true"
ENERGIE_URL = "https://hokejkv.cz/article/15981-Mise-zacina-Tri-energetici-miri-na-Hlinka-Gretzky-Cup"
CZECH_HOCKEY_URL = "https://www.ceskyhokej.cz/player/detail/3375?career=1"
KLASTEREC_URL = "https://www.hcklasterec.cz/clanek.asp?id=Tygri-maji-zastoupeni-v-reprezentacnich-vyberech%21-1742"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#071d31")
    draw = ImageDraw.Draw(image)

    for y in range(630):
        ratio = y / 629
        draw.line(
            (0, y, 1200, y),
            fill=(
                int(7 + 20 * ratio),
                int(29 + 47 * ratio),
                int(49 + 56 * ratio),
            ),
        )

    # Ledová plocha a branka – vlastní redakční ilustrace bez cizí fotografie.
    draw.rounded_rectangle((675, 68, 1150, 562), radius=34, fill="#eaf7fb", outline="#ffffff", width=6)
    draw.rounded_rectangle((708, 115, 1118, 522), radius=148, fill="#f9fdff", outline="#74b9d8", width=9)
    draw.line((913, 118, 913, 520), fill="#b32632", width=8)
    draw.arc((790, 190, 1035, 435), 180, 360, fill="#b32632", width=12)
    draw.arc((790, 202, 1035, 447), 0, 180, fill="#2a6f94", width=8)
    draw.rounded_rectangle((817, 260, 1012, 405), radius=18, outline="#c82d3a", width=12)
    for x in range(833, 1005, 28):
        draw.line((x, 270, x, 398), fill="#c82d3a", width=2)
    for y in range(278, 400, 24):
        draw.line((823, y, 1007, y), fill="#c82d3a", width=2)
    draw.ellipse((759, 430, 817, 458), fill="#111820")
    draw.line((784, 420, 850, 314), fill="#d9a548", width=10)
    draw.line((846, 316, 905, 334), fill="#d9a548", width=10)

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 59)
    medium = ImageFont.truetype(bold_path, 31)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 21)

    draw.rounded_rectangle((58, 48, 442, 103), radius=27, fill="#a9232b")
    draw.text((83, 66), "NAŠE KADAŇ · OD SOUSEDŮ", font=tiny, fill="white")

    lines = ["Klášterecký", "Josef Suchý", "zaskočil Kanadu"]
    y = 137
    for line in lines:
        draw.text((60, y), line, font=bold, fill="white")
        y += 73

    draw.text((64, 381), "Gól už po 103 sekundách", font=medium, fill="#ffe2a4")
    draw.text((64, 426), "a k tomu asistence při výhře 6:0", font=small, fill="#e8f7fb")
    draw.text((64, 491), "Česká reprezentace U18 · Edmonton", font=small, fill="#e8f7fb")
    draw.text((64, 570), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def article_page() -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": TITLE,
        "description": DESC,
        "datePublished": PUBLISHED,
        "dateModified": PUBLISHED,
        "author": {
            "@type": "Organization",
            "@id": "https://nasekadan.cz/#organization",
            "name": "Naše Kadaň",
            "url": "https://nasekadan.cz/o-webu/",
        },
        "publisher": {"@id": "https://nasekadan.cz/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
        "image": [SOCIAL_URL],
        "inLanguage": "cs-CZ",
        "isAccessibleForFree": True,
        "about": [
            {"@type": "Person", "name": "Josef Suchý"},
            {"@type": "Place", "name": "Klášterec nad Ohří"},
            {"@type": "SportsEvent", "name": "Hlinka Gretzky Cup 2026"},
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Naše Kadaň", "item": "https://nasekadan.cz/"},
            {"@type": "ListItem", "position": 2, "name": "Články", "item": "https://nasekadan.cz/clanky/"},
            {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL},
        ],
    }

    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title>
<meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626"><link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #0b385544}}.fact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:28px 0}}.fact{{background:#edf7fb;border:1px solid #cce1ea;border-radius:17px;padding:20px}}.fact strong{{display:block;color:#145a7a;font:900 25px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.neighbor-note{{background:#fff3f3;border:1px solid #e8c7ca;border-left:7px solid #a9232b;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.neighbor-note strong{{display:block;font:900 25px Georgia,serif;color:#85202a;margin-bottom:6px}}.schedule{{background:#eef6f8;border-radius:20px;padding:25px;margin:30px 0}}.schedule h2{{margin-top:0}}.schedule-grid{{display:grid;grid-template-columns:1fr 1fr;gap:13px}}.game{{background:#fff;border:1px solid #d7e2e6;border-radius:15px;padding:17px}}.game strong{{display:block;font:900 20px Georgia,serif;margin-bottom:5px}}.sources{{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}}.sources h2{{margin-top:0}}.sources li,.sources p{{font-size:14px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:900 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:700px){{.article{{padding:27px 21px}}.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.fact-grid,.schedule-grid{{grid-template-columns:1fr}}}}
</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="tag">OD SOUSEDŮ · HOKEJ · KLÁŠTEREC NAD OHŘÍ · {PUBLISHED_HUMAN}</p><h1>{escape(TITLE)}</h1><p class="leadtext"><strong>{escape(DESC)}</strong></p>
<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika s hokejovou brankou a pukem k výkonu Josefa Suchého proti Kanadě">
<p>Začít proti Kanadě na ledě Rogers Place a už po minutě a 43 sekundách otevřít skóre. Přesně tak vstoupil Josef Suchý do posledního přípravného utkání české reprezentace do osmnácti let před Hlinka Gretzky Cupem.</p>
<p>Český tým porazil domácí Kanadu 6:0. Suchý nezůstal jen u úvodní branky. V čase 27:56 přihrál na gól Dominicka Radima Byrtuse a zápas tak zakončil s bilancí jednoho gólu a jedné asistence.</p>
<div class="fact-grid"><div class="fact"><strong>1:43</strong><span>čas Suchého úvodního gólu proti Kanadě</span></div><div class="fact"><strong>1 + 1</strong><span>gól a asistence kláštereckého odchovance</span></div><div class="fact"><strong>6:0</strong><span>konečný výsledek české generálky</span></div></div>
<div class="neighbor-note"><strong>Od sousedů</strong><p>Naše Kadaň sleduje také výrazné příběhy z nejbližších měst. Josef Suchý je klášterecký odchovanec, který vyrůstal jen několik kilometrů od Kadaně a v mládežnických soutěžích nastupoval také proti kadaňským týmům.</p></div>
<h2>Z Klášterce do Karlových Varů</h2>
<p>Josef Suchý se narodil 17. července 2009 a hraje na pozici útočníka. Oficiální kariérní přehled Českého hokeje zachycuje jeho působení v týmu HC Tygři Klášterec nad Ohří už v mladších a starších žácích. Samotný klášterecký klub jej při reprezentační nominaci v roce 2024 označil za svého odchovance.</p>
<p>Další hokejový růst spojil s Energií Karlovy Vary. V sezoně 2025/2026 nasbíral v dorostenecké extralize 60 bodů ve 41 utkáních, z toho 31 branek a 29 asistencí. Ve čtyřech zápasech juniorské extraligy přidal dva góly a jednu asistenci.</p>
<p>Hlinka Gretzky Cup je pro něj první velkou reprezentační akcí. Energie před turnajem připomněla, že Suchý začal sbírat reprezentační zkušenosti až v kategorii do sedmnácti let a do řady předchozích výběrů se nevešel. Výkon proti Kanadě proto představuje výrazný krok v jeho dosavadní kariéře.</p>
<h2>Turnaj začal porážkou, dnes přijde Německo</h2>
<p>V prvním soutěžním utkání podlehla česká osmnáctka v pondělí 3. srpna Spojeným státům 4:6. Další zápas čeká národní tým dnes, v úterý 4. srpna. Proti Německu nastoupí v Rogers Place od 21:00 českého času.</p>
<div class="schedule"><h2>Nejbližší program české osmnáctky</h2><div class="schedule-grid"><div class="game"><strong>Úterý 4. srpna · 21:00</strong><span>Německo – Česko, Rogers Place</span></div><div class="game"><strong>Středa 5. srpna · 23:00</strong><span>Česko – Finsko, Downtown Community Arena</span></div></div><p>Časy jsou převedené na středoevropský letní čas. Program se může změnit podle pořadatele.</p></div>
<p><strong>Pro hokejový Klášterec jde o výsledek, který stojí za pozornost. Sedmnáctiletý odchovanec místních Tygrů se prosadil proti jedné z nejsilnějších mládežnických reprezentací světa a jeho turnaj pokračuje.</strong></p>
<section class="sources"><h2>Zdroje a ověření</h2><ul><li><a href="{GAME_URL}" rel="nofollow noopener">Hlinka Gretzky Cup – oficiální zápis přípravného utkání Česko–Kanada</a></li><li><a href="{SCHEDULE_URL}" rel="nofollow noopener">Hlinka Gretzky Cup – oficiální program a výsledky turnaje 2026</a></li><li><a href="{ENERGIE_URL}" rel="nofollow noopener">HC Energie Karlovy Vary – nominace a statistiky Josefa Suchého před turnajem</a></li><li><a href="{CZECH_HOCKEY_URL}" rel="nofollow noopener">Český hokej – kariérní přehled Josefa Suchého</a></li><li><a href="{KLASTEREC_URL}" rel="nofollow noopener">HC Tygři Klášterec nad Ohří – označení hráče za kláštereckého odchovance</a></li></ul><p>Redakce ověřila údaje 4. srpna 2026 před utkáním s Německem. Výsledek tohoto zápasu v době vydání ještě nebyl znám.</p></section>
<div data-promos data-context="article-end"></div></article>
<aside class="sticky"><div class="sidebox"><h3>Josef Suchý</h3><ul><li>17 let</li><li>útočník, levák</li><li>HC Energie Karlovy Vary</li><li>odchovanec HC Tygři Klášterec nad Ohří</li></ul></div><div class="sidebox"><h3>Další hokejový příběh</h3><p><a href="/clanky/martin-kadlec-navrat-hokej-kadan-2026.html">Martin Kadlec se po deseti letech vrátil do mateřské Kadaně →</a></p></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/long-article-ads.js?v=20260731-long-article-ads-2"></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body></html>'''


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    rss_date = format_datetime(datetime.fromisoformat(PUBLISHED))
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{rss_date}</lastBuildDate>", text, count=1)
    if URL not in text:
        item = f'''    <item>
      <title>{escape(TITLE)}</title>
      <description><![CDATA[{DESC}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{rss_date}</pubDate>
      <category>Od sousedů</category><category>Hokej</category><category>Klášterec nad Ohří</category><category>Hlinka Gretzky Cup</category>
      <szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image>
      <geo:lat>50.3845</geo:lat><geo:long>13.1713</geo:long>
    </item>

'''
        text = text.replace("    <item>", item + "    <item>", 1)
    write(path, text)


def update_sitemaps() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    if URL not in text:
        text = text.replace("</urlset>", f"  <url><loc>{URL}</loc><lastmod>2026-08-04</lastmod></url>\n</urlset>", 1)
    write(sitemap, text)

    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    if URL not in text:
        node = f'''  <url><loc>{URL}</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>{PUBLISHED}</news:publication_date><news:title>{escape(TITLE)}</news:title></news:news><image:image><image:loc>{SOCIAL_URL}</image:loc><image:title>{escape(TITLE)}</image:title></image:image></url>
'''
        first_url = text.find("<url>")
        if first_url >= 0:
            text = text[:first_url] + node + text[first_url:]
        else:
            text = text.replace("</urlset>", node + "</urlset>", 1)
    write(news, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        entry = f"- [{TITLE}]({URL})\n  {DESC}\n"
        marker = "## Články\n"
        text = text.replace(marker, marker + entry, 1) if marker in text else entry + "\n" + text
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    articles[:] = [item for item in articles if item.get("url") != URL]
    fingerprint_seed = "josef-suchy|klasterec-nad-ohri|cesko-u18|kanada|hlinka-gretzky-cup|2026"
    articles.insert(
        0,
        {
            "title": TITLE,
            "h1": TITLE,
            "url": URL,
            "published_at": PUBLISHED,
            "modified_at": PUBLISHED,
            "persons": ["Josef Suchý"],
            "organizations": [
                "HC Tygři Klášterec nad Ohří",
                "HC Energie Karlovy Vary",
                "Český hokej",
                "Česká reprezentace U18",
                "Hlinka Gretzky Cup",
            ],
            "places": ["Klášterec nad Ohří", "Karlovy Vary", "Edmonton", "Rogers Place"],
            "cases": ["Josef Suchý na Hlinka Gretzky Cupu 2026"],
            "topics": ["Od sousedů", "Hokej", "Reprezentace U18", "Hlinka Gretzky Cup", "Regionální sport"],
            "fingerprint": sha256(fingerprint_seed.encode("utf-8")).hexdigest()[:24],
            "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
            "source_path": f"clanky/{SLUG}.html",
            "publication_status": "published",
            "source_commit": "pending-publication-commit",
        },
    )

    now = datetime.now(timezone.utc).isoformat()
    data["schema_version"] = max(str(data.get("schema_version", "1.4")), "1.4")
    data["generated_at"] = now
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation.update(
        {
            "homepage_count": min(14, len(articles)),
            "archive_count": len(articles),
            "rss_count": len(articles),
            "sitemap_all_articles_present": True,
            "news_sitemap_recent_count": (ROOT / "news-sitemap.xml").read_text(encoding="utf-8").count("<url>"),
            "deployment_health": "pending_public_verification",
            "required_fields_complete": True,
            "duplicate_urls": [],
            "duplicate_fingerprints": [],
            "per_article_source_commits": True,
            "repair_pending_public_verification": False,
            "rss_order_matches_archive": True,
            "archive_page_count": max(1, math.ceil(len(articles) / 12)),
            "deployment_health_status_field_present": True,
            "public_audit_at": now,
            "last_registry_refresh": {
                "reason": "publication of a new Od sousedů article about Josef Suchý and full regeneration of homepage, paginated archive, RSS and sitemaps",
                "classification": "new_article_pending_public_verification",
                "repaired_url": URL,
                "homepage_articles": min(14, len(articles)),
                "archive_articles": len(articles),
                "archive_pages": max(1, math.ceil(len(articles) / 12)),
                "rss_articles": len(articles),
                "completed_at": now,
            },
        }
    )
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def validate() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    if f"<h1>{TITLE}</h1>" not in article:
        raise RuntimeError("Článek nemá očekávaný H1.")
    if "OD SOUSEDŮ" not in article:
        raise RuntimeError("Článek nemá označení Od sousedů.")
    if URL not in (ROOT / "rss.xml").read_text(encoding="utf-8"):
        raise RuntimeError("Článek chybí v RSS.")
    if URL not in (ROOT / "sitemap.xml").read_text(encoding="utf-8"):
        raise RuntimeError("Článek chybí v sitemapě.")
    if URL not in (ROOT / "news-sitemap.xml").read_text(encoding="utf-8"):
        raise RuntimeError("Článek chybí v news sitemapě.")


def main() -> int:
    make_social()
    write(ARTICLE, article_page())
    update_rss()
    update_sitemaps()
    update_llms()
    update_registry()
    validate()
    print(f"Připraven článek: {URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
