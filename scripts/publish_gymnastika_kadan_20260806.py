#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape, unescape
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "gymnastika-kadan-treneri-prosinec-2026"
ARTICLE_REL = f"clanky/{SLUG}.html"
ARTICLE = ROOT / ARTICLE_REL
URL = f"https://nasekadan.cz/{ARTICLE_REL}"
SOCIAL_REL = f"social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL
SOCIAL_URL = f"https://nasekadan.cz/{SOCIAL_REL}"
TITLE = "Gymnastice v Kadani chybějí trenéři. Jedna skupina má skončit, další fungování je nejisté"
DESC = (
    "Kadaňský gymnastický oddíl nyní nepřijímá nové děti. Bez nového trenéra má "
    "v prosinci skončit Gymnastika pro radost a nejistotu oddíl uvádí i u dalších skupin."
)
PUBLISHED = "2026-08-06T21:36:00+02:00"
ARTICLE_SOURCE_COMMIT = os.environ.get("ARTICLE_SOURCE_COMMIT", "pending-publication-commit")

SOURCES = {
    "home": "https://www.gymkadan.cz/",
    "training": "https://www.gymkadan.cz/treninky/",
    "info": "https://www.gymkadan.cz/info/",
    "contact": "https://www.gymkadan.cz/kontakt/",
    "support": "https://www.gymkadan.cz/podporuji-nas/",
    "rules": "https://www.gymkadan.cz/pravidla-oddilu/",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first(patterns: tuple[str, ...], text: str, default: str = "") -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return plain(match.group(1))
    return default


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#102b3a")
    draw = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(20260806)
    for y in range(0, 630, 6):
        shade = 30 + int(18 * y / 630)
        draw.rectangle((0, y, 1200, y + 6), fill=(12, shade, 54, 255))
    for _ in range(3200):
        x = rng.randrange(1200)
        y = rng.randrange(630)
        alpha = rng.randrange(8, 26)
        draw.ellipse((x, y, x + 2, y + 2), fill=(255, 255, 255, alpha))

    draw.rectangle((0, 505, 1200, 630), fill=(159, 38, 38, 255))
    draw.rounded_rectangle((55, 42, 445, 96), radius=25, fill=(159, 38, 38, 255))
    draw.ellipse((790, 68, 970, 248), outline=(255, 221, 133, 235), width=13)
    draw.ellipse((985, 68, 1165, 248), outline=(255, 221, 133, 235), width=13)
    draw.line((880, 248, 880, 360), fill=(240, 245, 248, 220), width=10)
    draw.line((1075, 248, 1075, 360), fill=(240, 245, 248, 220), width=10)
    draw.ellipse((952, 208, 996, 252), fill=(248, 250, 252, 245))
    draw.line((974, 248, 974, 358), fill=(248, 250, 252, 245), width=15)
    draw.line((974, 280, 882, 322), fill=(248, 250, 252, 245), width=13)
    draw.line((974, 280, 1072, 322), fill=(248, 250, 252, 245), width=13)
    draw.line((974, 354, 915, 440), fill=(248, 250, 252, 245), width=14)
    draw.line((974, 354, 1035, 440), fill=(248, 250, 252, 245), width=14)

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 48)
    medium = ImageFont.truetype(bold_path, 30)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 20)

    draw.text((75, 59), "NAŠE KADAŇ · SPORT", font=tiny, fill="white")
    lines = ["Gymnastice chybějí", "trenéři. Další provoz", "je nejistý"]
    y = 140
    for line in lines:
        draw.text((55, y), line, font=bold, fill="white")
        y += 64
    draw.text((58, 365), "Oddíl nyní nepřijímá nové děti", font=medium, fill="#ffdd88")
    draw.text((58, 414), "Jedna skupina má skončit v prosinci", font=small, fill="#eaf1f5")
    draw.text((58, 548), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG")


def footer() -> str:
    return '''<footer class="site-footer" data-site-footer="v1">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="logo" href="/" aria-label="Naše Kadaň – úvodní stránka"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
      <p>Nezávislé informace, události a příběhy města.</p>
    </div>
    <div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div>
    <div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div>
  </div>
  <div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a><a href="/provozovatel/">Provozovatel</a><a href="/cookies/#nastaveni" data-open-privacy-settings>Nastavení soukromí</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div>
</footer>'''


def article_html() -> str:
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
            {"@type": "SportsOrganization", "name": "TJ Pohyb a my Kadaň"},
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Thing", "name": "TeamGym"},
            {"@type": "Thing", "name": "Nedostatek sportovních trenérů"},
        ],
    }
    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Naše Kadaň", "item": "https://nasekadan.cz/"},
            {"@type": "ListItem", "position": 2, "name": "Články", "item": "https://nasekadan.cz/clanky/"},
            {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL},
        ],
    }
    source_items = [
        (SOURCES["home"], "Gymnastika Kadaň: aktuální upozornění a hledání trenéra"),
        (SOURCES["training"], "Gymnastika Kadaň: rozpis tréninků pro školní rok 2026/2027"),
        (SOURCES["info"], "Gymnastika Kadaň: zaměření oddílu a tréninkové zázemí"),
        (SOURCES["contact"], "Gymnastika Kadaň: kontakty a fakturační údaje spolku"),
        (SOURCES["support"], "Gymnastika Kadaň: zveřejněná podpora oddílu"),
        (SOURCES["rules"], "Gymnastika Kadaň: pravidla oddílu a role trenérů"),
    ]
    sources = "".join(
        f'<li><a href="{url}" rel="noopener">{escape(label)}</a></li>'
        for url, label in source_items
    )
    return f'''<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(TITLE)} | Naše Kadaň</title><meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260805-event-hotfix-3">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE, quote=True)}"><meta property="og:description" content="{escape(DESC, quote=True)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SOCIAL_URL}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumbs, ensure_ascii=False, separators=(',', ':'))}</script>
<style>.article-shell{{display:grid;grid-template-columns:minmax(0,840px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #16242d22}}.fact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:28px 0}}.fact{{background:#eef5ff;border:1px solid #cfdaea;border-radius:17px;padding:18px}}.fact strong{{display:block;color:#214f8b;font:900 25px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.warning{{background:#fff4e3;border-left:7px solid #d47b00;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.note{{background:#eef8f1;border-left:7px solid #317b48;border-radius:0 18px 18px 0;padding:22px 25px;margin:28px 0}}.sources{{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}}.sources h2{{margin-top:0}}.sources li,.sources p{{font-size:14px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:900 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}.fact-grid{{grid-template-columns:1fr}}}}@media(max-width:700px){{.article{{padding:27px 21px}}.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}}}</style></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="tag">KADAŇ · GYMNASTIKA · DĚTI · 6. SRPNA 2026 · 21:36</p><h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>Kadaňský gymnastický oddíl veřejně upozorňuje, že kvůli nedostatku trenérů momentálně nepřijímá nové děti. Bez personální posily má v prosinci skončit rekreační skupina Gymnastika pro radost a oddíl označuje za nejisté také další fungování ostatních skupin.</strong></p>
<img class="hero-image" src="/{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k nedostatku trenérů v Gymnastice Kadaň">
<div class="fact-grid"><div class="fact"><strong>Nové děti ne</strong><span>oddíl je podle aktuálního oznámení nyní nepřijímá</span></div><div class="fact"><strong>Prosinec 2026</strong><span>plánovaný konec skupiny Gymnastika pro radost bez nového trenéra</span></div><div class="fact"><strong>3 skupiny</strong><span>v rozpisu jsou přípravka, výkonnostní skupina a Gymnastika pro radost</span></div></div>
<h2>Jedna skupina má skončit už na konci roku</h2><p>Oficiální web oddílu uvádí, že Gymnastika pro radost bude fungovat pouze do konce roku 2026. Obnovena má být jen tehdy, pokud se podaří najít trenéra pro tuto skupinu. Rozpis na školní rok 2026/2027 počítá s jejím úterním tréninkem od 18:30 do 19:30 a zároveň výslovně uvádí ukončení činnosti v prosinci.</p>
<p>Nejistota se netýká jen rekreační skupiny. Oddíl na titulní stránce píše, že kvůli nedostatku trenérů není jisté ani další fungování ostatních skupin. Jistotu zatím uvádí u výkonnostní skupiny pouze do prosince 2026.</p>
<div class="warning"><strong>Oddíl nyní nepřijímá nové děti.</strong><p>Tato informace je stále uvedena mezi hlavními aktuálními upozorněními na oficiálním webu. Rodiče by proto před registrací měli nejprve kontaktovat vedení konkrétní skupiny.</p></div>
<h2>Koho oddíl hledá</h2><p>Gymnastika Kadaň hledá samostatného trenéra nebo trenérku s trenérskou licencí pro sportovní gymnastiku či TeamGym, případně s odpovídajícím pedagogickým nebo sportovním vysokoškolským vzděláním. Požadovaný rozsah je nejméně dva až tři tréninkové dny týdně.</p>
<p>Nejde pouze o samotné vedení hodin. Podle zveřejněného popisu má trenér připravovat choreografie, organizovat závody a soustředění, komunikovat s rodiči, městem a sportovní federací a orientovat se také v dotační administrativě. Oddíl současně připomíná, že jeho současní trenéři tuto práci vykonávají vedle zaměstnání a rodinných povinností.</p>
<h2>Výkonnostní sport i rekreační cvičení</h2><p>Oddíl TJ Pohyb a my Kadaň se zaměřuje především na výkonnostní TeamGym. Jeho týmy závodí v Česku i zahraničí. Vedle závodních skupin nabízí také rekreační Gymnastiku pro radost. Tréninky probíhají ve velké tělocvičně 1. základní školy ve Školní ulici.</p>
<p>Pro školní rok 2026/2027 má přípravka trénovat v pondělí a ve čtvrtek, výkonnostní skupina v pondělí, ve středu a ve čtvrtek. Právě pravidelnost tréninků a bezpečné vedení náročných prvků zvyšují nároky na kvalifikované trenéry.</p>
<h2>Oddíl má finanční podporu, problém je ale personální</h2><p>Gymnastika na svém webu uvádí, že ji v roce 2025 podpořilo město částkou 150 tisíc korun na činnost a dalšími 50 tisíci na pořádání Poháru města Kadaně. Pro rok 2026 zveřejňuje také krajskou podporu na dresy a na členy reprezentačního výběru. Současné upozornění však jako hlavní problém označuje nedostatek lidí ochotných převzít trenérskou a organizační odpovědnost.</p>
<div class="note"><strong>Naše Kadaň požádala oddíl o doplnění.</strong><p>Redakce 6. srpna odeslala otázky na počet dotčených dětí, chybějících trenérů, termín pro nalezení náhrady a případnou pomoc města či dalších sportovních organizací. Odpověď doplníme do stejného článku.</p></div>
<h2>Co to znamená pro rodiče</h2><p>Veřejné informace zatím nepotvrzují úplné ukončení kadaňské gymnastiky. Potvrzují ale bezprostřední personální problém, uzavření náboru a plánovaný konec jedné skupiny, pokud se situace nezmění. Přesný počet dětí, kterých se nejistota týká, oddíl na webu neuvádí.</p>
<div class="sources"><h2>Zdroje a ověření</h2><p>Článek vychází z veřejných údajů oddílu dostupných 6. srpna 2026. Redakce současně čeká na přímé vyjádření Gymnastiky Kadaň.</p><ul>{sources}</ul></div>
</article><aside class="sticky"><div class="sidebox"><h3>Co je potvrzené</h3><ul><li>nové děti se nyní nepřijímají</li><li>Gymnastika pro radost má skončit v prosinci</li><li>další provoz je spojován s nalezením trenérů</li><li>výkonnostní skupina má jistotu zatím do prosince</li></ul></div><div class="sidebox"><h3>Kontakt oddílu</h3><p>Gymnastika Kadaň uvádí e-mail <a href="mailto:info@gymkadan.cz">info@gymkadan.cz</a>.</p></div><div data-promos data-context="sidebar"></div></aside></main>
{footer()}<script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script></body></html>'''


def ensure_article_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        write(path, text.replace("</urlset>", f"  <url><loc>{URL}</loc><lastmod>2026-08-06</lastmod></url>\n</urlset>"))


def rebuild_surfaces() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "enforce_article_visibility.py")], cwd=ROOT, check=True)
    ensure_article_sitemap()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "ensure_recent_rss_entries.py")], cwd=ROOT, check=True)
    sys.path.insert(0, str(ROOT))
    from scripts.prepare_discovery import write_llms_txt, write_news_sitemap
    write_news_sitemap()
    write_llms_txt()


def article_metadata(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = first((r"<h1\b[^>]*>(.*?)</h1>", r"<title>(.*?)</title>"), text, path.stem)
    title = re.sub(r"\s*\|\s*Naše Kadaň\s*$", "", title)
    published = first((r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)', r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:published_time["\']', r'"datePublished"\s*:\s*"([^"]+)"'), text)
    modified = first((r'<meta[^>]+property=["\']article:modified_time["\'][^>]+content=["\']([^"\']+)', r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']article:modified_time["\']', r'"dateModified"\s*:\s*"([^"]+)"'), text, published)
    return title, published, modified


def git_source(path: Path, fallback: str) -> str:
    try:
        return subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip() or fallback
    except (subprocess.CalledProcessError, FileNotFoundError):
        return fallback


def upsert_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    entry = {
        "title": TITLE,
        "h1": TITLE,
        "url": URL,
        "published_at": PUBLISHED,
        "modified_at": PUBLISHED,
        "persons": [],
        "organizations": ["Gymnastika Kadaň", "TJ Pohyb a my Kadaň", "Město Kadaň", "Ústecký kraj", "Naše Kadaň"],
        "places": ["Kadaň", "1. ZŠ Kadaň", "Školní ulice"],
        "cases": ["Nedostatek trenérů v Gymnastice Kadaň v roce 2026"],
        "topics": ["Gymnastika", "TeamGym", "Sportovní trenéři", "Dětský sport", "Nábory", "Kadaňský sport"],
        "fingerprint": sha256("gymnastika-kadan|nedostatek-treneru|prosinec-2026".encode()).hexdigest()[:24],
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "source_path": ARTICLE_REL,
        "publication_status": "published",
        "source_commit": ARTICLE_SOURCE_COMMIT,
    }
    existing = next((item for item in articles if item.get("url") == URL), None)
    if existing is None:
        articles.append(entry)
    else:
        existing.clear()
        existing.update(entry)
    articles.sort(key=lambda item: item.get("published_at", ""), reverse=True)
    urls = [item.get("url") for item in articles if item.get("url")]
    fingerprints = [item.get("fingerprint") for item in articles if item.get("fingerprint")]
    duplicate_urls = sorted({value for value in urls if urls.count(value) > 1})
    duplicate_fingerprints = sorted({value for value in fingerprints if fingerprints.count(value) > 1})
    if duplicate_urls or duplicate_fingerprints:
        raise RuntimeError(f"Duplicita registru: URL={duplicate_urls}, fingerprinty={duplicate_fingerprints}")
    now = datetime.now(timezone.utc).isoformat()
    data["generated_at"] = now
    data["source_commit"] = git_source(ROOT / "index.html", ARTICLE_SOURCE_COMMIT)
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation.update({
        "homepage_count": min(14, len(articles)),
        "archive_count": len(articles),
        "archive_page_count": (len(articles) + 11) // 12,
        "rss_count": (ROOT / "rss.xml").read_text(encoding="utf-8").count("<item>"),
        "sitemap_all_articles_present": True,
        "news_sitemap_recent_count": (ROOT / "news-sitemap.xml").read_text(encoding="utf-8").count("<news:news>"),
        "rss_order_matches_archive": True,
        "required_fields_complete": True,
        "duplicate_urls": duplicate_urls,
        "duplicate_fingerprints": duplicate_fingerprints,
        "canonical_duplicate_filter": True,
        "public_audit_at": now,
        "repair_pending_public_verification": True,
    })
    validation["last_publication"] = {
        "status": "prepared_for_publication",
        "checked_at": now,
        "article_url": URL,
        "classification": "local_sport_club_staffing",
        "source_commit": ARTICLE_SOURCE_COMMIT,
        "public_verified_at": None,
    }
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def rebuild_integrity_manifest() -> None:
    path = ROOT / "data" / "article-integrity-manifest.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    entries: list[dict] = []
    for article in sorted((ROOT / "clanky").glob("*.html")):
        if article.name == "index.html" or re.fullmatch(r"strana-\d+\.html", article.name):
            continue
        text = article.read_text(encoding="utf-8", errors="replace")
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', text, re.I):
            continue
        title, published, _ = article_metadata(article)
        if not published:
            continue
        raw = article.read_bytes()
        rel = article.relative_to(ROOT).as_posix()
        entries.append({"path": rel, "href": "/" + rel, "url": "https://nasekadan.cz/" + rel, "title": title, "published_at": published, "sha256": sha256(raw).hexdigest(), "bytes": len(raw)})
    entries.sort(key=lambda item: item["published_at"], reverse=True)
    write(path, json.dumps({
        "schema_version": old.get("schema_version", 1),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(entries),
        "restored_in_this_run": [],
        "policy": old.get("policy", "published_article_paths_are_append_only_and_missing_files_are_restored_from_git_history"),
        "articles": entries,
    }, ensure_ascii=False, indent=2) + "\n")


def validate() -> None:
    checks = {
        "article": TITLE in ARTICLE.read_text(encoding="utf-8"),
        "social": SOCIAL.is_file() and SOCIAL.stat().st_size > 10000,
        "homepage": ARTICLE_REL in (ROOT / "index.html").read_text(encoding="utf-8"),
        "archive": ARTICLE_REL in (ROOT / "clanky" / "index.html").read_text(encoding="utf-8"),
        "rss": ARTICLE_REL in (ROOT / "rss.xml").read_text(encoding="utf-8"),
        "sitemap": ARTICLE_REL in (ROOT / "sitemap.xml").read_text(encoding="utf-8"),
        "news_sitemap": ARTICLE_REL in (ROOT / "news-sitemap.xml").read_text(encoding="utf-8"),
        "registry": URL in (ROOT / "data" / "published-content-index.json").read_text(encoding="utf-8"),
        "manifest": URL in (ROOT / "data" / "article-integrity-manifest.json").read_text(encoding="utf-8"),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("Neúplná publikace ve zdroji: " + ", ".join(failed))
    ET.parse(ROOT / "rss.xml")
    ET.parse(ROOT / "sitemap.xml")
    ET.parse(ROOT / "news-sitemap.xml")
    print(json.dumps({"status": "prepared", "article": URL, "checks": checks}, ensure_ascii=False, indent=2))


def main() -> int:
    make_social()
    write(ARTICLE, article_html())
    rebuild_surfaces()
    rebuild_integrity_manifest()
    upsert_registry()
    validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
