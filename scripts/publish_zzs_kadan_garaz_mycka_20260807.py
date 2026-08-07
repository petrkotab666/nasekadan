#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import importlib.util
import json
from math import ceil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "scripts" / "publish_jezero_most_20260805.py"
spec = importlib.util.spec_from_file_location("nk_publish_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Nelze načíst publikační základ.")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

SLUG = "zzs-kadan-garaz-mycka-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
SOCIAL_REL = f"/social/{SLUG}.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"
TITLE = "Kadaňská záchranka dostane novou garáž a myčku. Kraj stanovil strop 16,5 milionu"
DESC = (
    "Ústecký kraj soutěží nové zázemí výjezdové základny ZZS v Golovinově ulici. "
    "Zakázka má maximální nabídkovou cenu 16,5 milionu Kč bez DPH a realizace se předpokládá od listopadu 2026 do března 2028."
)
PUBLISHED = "2026-08-07T17:00:00+02:00"
MODIFIED = PUBLISHED
RSS_DATE = "Fri, 07 Aug 2026 17:00:00 +0200"
FINGERPRINT = sha256(
    "zzs-uk|kadan|golovinova|garaz|mycka|design-build|16500000|2026-2028".encode("utf-8")
).hexdigest()[:24]

for key, value in {
    "SLUG": SLUG, "ARTICLE": ARTICLE, "REL": REL, "URL": URL,
    "SOCIAL_REL": SOCIAL_REL, "SOCIAL": SOCIAL, "SOCIAL_URL": SOCIAL_URL,
    "TITLE": TITLE, "DESC": DESC, "PUBLISHED": PUBLISHED,
    "MODIFIED": MODIFIED, "RSS_DATE": RSS_DATE, "FINGERPRINT": FINGERPRINT,
}.items():
    setattr(base, key, value)


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#eef3f5")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1200, 630), fill="#eef3f5")
    draw.rectangle((0, 460, 1200, 630), fill="#d9e1e4")
    draw.rectangle((700, 140, 1140, 465), fill="#d4dadd", outline="#44545d", width=8)
    draw.polygon([(680, 140), (920, 55), (1160, 140)], fill="#a8b4ba", outline="#44545d")
    draw.rectangle((745, 240, 905, 465), fill="#4d5c64")
    draw.rectangle((935, 240, 1095, 465), fill="#4d5c64")
    draw.rectangle((770, 275, 880, 450), fill="#f8fafb")
    draw.rectangle((960, 275, 1070, 450), fill="#f8fafb")
    draw.rounded_rectangle((715, 350, 920, 500), radius=20, fill="white", outline="#26333a", width=6)
    draw.rectangle((785, 315, 890, 390), fill="white", outline="#26333a", width=6)
    draw.rectangle((805, 330, 870, 375), fill="#b9dce8")
    draw.rectangle((735, 385, 900, 425), fill="#d62e3a")
    draw.rectangle((795, 365, 820, 445), fill="#d62e3a")
    draw.ellipse((750, 470, 805, 525), fill="#26333a")
    draw.ellipse((845, 470, 900, 525), fill="#26333a")
    draw.ellipse((765, 485, 790, 510), fill="#d9e1e4")
    draw.ellipse((860, 485, 885, 510), fill="#d9e1e4")
    draw.rectangle((835, 300, 865, 320), fill="#2e7fbc")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 50)
    medium = ImageFont.truetype(bold_path, 28)
    small = ImageFont.truetype(regular_path, 23)
    tiny = ImageFont.truetype(bold_path, 20)
    draw.rounded_rectangle((55, 45, 405, 100), radius=27, fill="#9f2626")
    draw.text((80, 62), "NAŠE KADAŇ · ZDRAVOTNICTVÍ", font=tiny, fill="white")
    y = 145
    for line in ["Nové zázemí", "záchranky", "v Kadani"]:
        draw.text((58, y), line, font=bold, fill="#17313d")
        y += 67
    draw.text((62, 370), "GARÁŽE · MYČKA · ZÁLOŽNÍ ZDROJ", font=medium, fill="#9f2626")
    draw.text((62, 520), "MAX. NABÍDKOVÁ CENA 16,5 MIL. KČ BEZ DPH", font=small, fill="#26333a")
    draw.text((62, 565), "PŘEDPOKLAD REALIZACE 11/2026–3/2028", font=small, fill="#26333a")
    draw.text((62, 597), "NASEKADAN.CZ", font=tiny, fill="#26333a")
    image.save(SOCIAL, format="PNG", optimize=True)


def article_page() -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": TITLE,
        "description": DESC,
        "datePublished": PUBLISHED,
        "dateModified": MODIFIED,
        "author": {"@type": "Organization", "@id": "https://nasekadan.cz/#organization", "name": "Naše Kadaň", "url": "https://nasekadan.cz/o-webu/"},
        "publisher": {"@id": "https://nasekadan.cz/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
        "image": [SOCIAL_URL],
        "inLanguage": "cs-CZ",
        "isAccessibleForFree": True,
        "about": [
            {"@type": "Place", "name": "Kadaň"},
            {"@type": "Organization", "name": "Zdravotnická záchranná služba Ústeckého kraje"},
            {"@type": "Thing", "name": "Výjezdová základna ZZS Kadaň"},
            {"@type": "Thing", "name": "Garáž a myčka sanitních vozidel"},
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
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE, quote=True)}"><meta name="twitter:description" content="{escape(DESC, quote=True)}"><meta name="twitter:image" content="{SOCIAL_URL}">
<meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{MODIFIED}">
<link data-nasekadan-favicon="primary" rel="icon" href="/favicon.svg?v=20260801-2" type="image/svg+xml" sizes="any"><meta name="theme-color" content="#9f2626"><link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
<script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script>
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,840px) 300px;gap:36px;align-items:start;padding:54px 0 72px}}.article{{background:#fff;border:1px solid #e1e6e8;border-radius:26px;padding:38px 42px 48px;box-shadow:0 18px 44px #14232d18}}.article h1{{font:900 clamp(40px,6vw,66px)/1.02 Georgia,serif;letter-spacing:-.04em;margin:.22em 0 .3em}}.article h2{{font:900 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article h3{{font:900 23px/1.25 Georgia,serif;margin:0 0 8px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-underline-offset:3px}}.tag{{font-weight:900;color:#9f2626;letter-spacing:.065em;font-size:13px;text-transform:uppercase}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.52!important}}.hero-image{{width:100%;height:auto;border-radius:23px;margin:28px 0 32px;display:block;box-shadow:0 17px 38px #29472933}}.fact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:28px 0}}.fact{{background:#edf4f7;border:1px solid #cfdee4;border-radius:17px;padding:20px}}.fact strong{{display:block;color:#8b272d;font:900 28px Georgia,serif;margin-bottom:6px}}.fact span{{font-size:14px;line-height:1.4}}.note{{background:#fff6dc;border:1px solid #e6cb82;border-left:7px solid #b37a14;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.note strong{{display:block;font:900 25px Georgia,serif;color:#77530e;margin-bottom:6px}}.question{{background:#fff1f1;border:1px solid #e5c4c6;border-left:7px solid #9f2626;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.question strong{{display:block;font:900 24px Georgia,serif;color:#81232a;margin-bottom:6px}}.sources{{background:#eef3f5;border-radius:18px;padding:24px;margin-top:44px}}.sources h2{{margin-top:0}}.sources li,.sources p{{font-size:14px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:900 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:700px){{.article{{padding:27px 21px}}.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.fact-grid{{grid-template-columns:1fr}}}}
</style></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article">
<p class="tag">KADAŇ · ZDRAVOTNICTVÍ · INVESTICE · 7. SRPNA 2026 · 17:00</p>
<h1>{escape(TITLE)}</h1>
<p class="leadtext"><strong>Výjezdovou základnu zdravotnické záchranné služby v Golovinově ulici čeká rozšíření. Ústecký kraj soutěží stavbu nového zázemí s garážemi pro sanitní vozidla, mycím boxem a záložním zdrojem elektřiny. Maximální nabídková cena je stanovena na 16,5 milionu korun bez DPH.</strong></p>
<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika Naší Kadaně k plánovanému novému zázemí záchranné služby v Kadani">
<div class="fact-grid"><div class="fact"><strong>16,5 mil. Kč</strong><span>maximální a nepřekročitelná nabídková cena bez DPH</span></div><div class="fact"><strong>11/2026–3/2028</strong><span>předpokládané období realizace uvedené krajem</span></div><div class="fact"><strong>Design &amp; Build</strong><span>dodavatel zajistí také dokumentaci potřebnou pro povolení záměru</span></div></div>
<h2>Dva garážové boxy, myčka a záložní zdroj</h2>
<p>Příprava projektu běží nejméně od konce roku 2025. Ústecký kraj tehdy uzavřel smlouvu na dokumentaci pro stavbu nazvanou „ZZS ÚK – Realizace garáže a myčky výjezdové základny ZZS ÚK v Kadani“. Výjezdová základna sídlí v Golovinově ulici 1983.</p>
<p>Přípravné podklady počítají s přístavbou ke stávající základně. Součástí mají být dva garážové boxy pro sanitní vozidla, prostor pro ruční mytí sanitek, stacionární záložní zdroj elektřiny a potřebné napojení na energie a kanalizaci.</p>
<h2>16,5 milionu není konečná cena</h2>
<div class="note"><strong>Jde o cenový strop soutěže</strong><p>Částka 16,5 milionu korun bez DPH není oznámenou konečnou cenou stavby. Kraj v zadávacím řízení stanovil tuto částku jako maximální a nepřekročitelnou nabídkovou cenu. Skutečná smluvní cena bude známá až po vyhodnocení soutěže a podpisu smlouvy s vítězným dodavatelem.</p></div>
<p>Investice má být podle písemné odpovědi investičního odboru financována z rozpočtu Ústeckého kraje. Kraj zároveň potvrdil, že kadaňský projekt a obdobná akce v Žatci jsou dvě samostatné veřejné zakázky, byť obě slouží jedné příspěvkové organizaci – Zdravotnické záchranné službě Ústeckého kraje.</p>
<h2>Stavět se má metodou Design &amp; Build</h2>
<p>Kraj zvolil model Design &amp; Build. Vítězný dodavatel tedy nemá pouze samotnou stavbu provést, ale zpracuje také dokumentaci potřebnou pro povolení záměru. Z toho důvodu nyní ještě není hotové finální stavební povolení v podobě, jaká by byla obvyklá u zakázky soutěžené až po úplném dokončení projektové dokumentace.</p>
<p>Předpokládané období realizace je ve výzvě stanoveno od listopadu 2026 do března 2028. Přesný termín zahájení a dokončení bude podle kraje znám až po ukončení zadávacího řízení a podpisu smlouvy. Harmonogram prací má následně vítězný dodavatel předložit do dvou dnů od předání staveniště.</p>
<h2>Investici schválila krajská rada</h2>
<p>Projekt projednala Rada Ústeckého kraje. Investiční odbor nám potvrdil usnesení č. 049/45R/2026 ze dne 21. července 2026. Zadávací dokumentace je zveřejněna na profilu zadavatele v Tender areně.</p>
<p>Samotná přípravná smlouva byla uzavřena už 8. prosince 2025. Ústecký kraj za zpracování dokumentace ve stupni přípravy zakázky a návrhu řešení sjednal 110 tisíc korun bez DPH.</p>
<h2>Jak bude během stavby fungovat výjezdová základna?</h2>
<div class="question"><strong>Na odpověď záchranky ještě čekáme</strong><p>Na otázku, jak bude během stavby zajištěn nepřetržitý provoz výjezdové základny a neomezené výjezdy sanitek, nás investiční odbor Ústeckého kraje odkázal přímo na ZZS ÚK. Stejně tak má záchranka doplnit praktické důvody, které nové garáže a mycí zázemí řeší. Jakmile odpověď dorazí, doplníme ji do tohoto článku.</p></div>
<p>To je pro Kadaň podstatná část projektu. Výjezdová základna musí plnit svou funkci i v průběhu stavebních prací a organizace provozu může ovlivnit postup a etapizaci celé realizace.</p>
<h2>Co zatím víme jistě</h2>
<ul><li>stavba se týká výjezdové základny ZZS ÚK v Golovinově ulici v Kadani,</li><li>kraj soutěží kadaňskou a žateckou akci odděleně,</li><li>cenový strop kadaňské zakázky je 16,5 milionu Kč bez DPH,</li><li>zakázka je řešena metodou Design &amp; Build,</li><li>předpokládaná realizace je od listopadu 2026 do března 2028,</li><li>investici schválila Rada Ústeckého kraje usnesením 049/45R/2026.</li></ul>
<section class="sources"><h2>Zdroje</h2><ul>
<li>Písemné vyjádření odboru investičního Krajského úřadu Ústeckého kraje pro Naše Kadaň, 7. srpna 2026.</li>
<li><a href="https://zadavatel.tenderarena.cz/evidence/zakazka/specifikace/zakladniudaje/detail.jsf?id=906488" rel="nofollow noopener">Profil zadavatele – veřejná zakázka na garáž a myčku ZZS v Kadani</a></li>
<li><a href="https://smlouvy.gov.cz/smlouva/36012497" rel="nofollow noopener">Registr smluv – smlouva 25/SML003858/SoD/INV ze dne 8. prosince 2025</a></li>
<li><a href="https://www.kr-ustecky.cz/usneseni-z-45-rady-usteckeho-kraje-vii-volebni-obdobi-2024-2028-konane-21-7-2026" rel="nofollow noopener">Ústecký kraj – usnesení z 45. schůze Rady ÚK dne 21. července 2026</a></li>
<li><a href="https://www.zzsuk.cz/vyjezdove-zakladny/" rel="nofollow noopener">ZZS Ústeckého kraje – výjezdové základny</a></li>
</ul></section>
<div data-promos data-context="article-end"></div></article>
<aside class="sticky"><div class="sidebox"><h3>Výjezdová základna Kadaň</h3><ul><li>Golovinova 1983</li><li>oblastní středisko Chomutov</li><li>ZZS Ústeckého kraje</li></ul></div><div class="sidebox"><h3>Další krok</h3><p>Čekáme na odpověď ZZS ÚK k organizaci provozu během stavby a k tomu, jaké konkrétní provozní problémy nové zázemí vyřeší.</p></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/" aria-label="Naše Kadaň – úvodní stránka"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a><a href="/provozovatel/">Provozovatel</a><a href="/cookies/#nastaveni" data-open-privacy-settings>Nastavení soukromí</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/long-article-ads.js?v=20260731-long-article-ads-2"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script>
</body></html>'''


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    import re
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{RSS_DATE}</lastBuildDate>", text, count=1)
    if URL in text:
        path.write_text(text, encoding="utf-8", newline="\n")
        return
    item = f'''    <item>\n      <title>{escape(TITLE)}</title>\n      <description><![CDATA[{DESC}]]></description>\n      <link>{URL}</link>\n      <guid isPermaLink="true">{URL}</guid>\n      <pubDate>{RSS_DATE}</pubDate>\n      <category>Kadaň</category><category>Zdravotnictví</category><category>ZZS ÚK</category><category>Investice</category>\n      <szn:image><szn:url>{SOCIAL_URL}</szn:url></szn:image>\n    </item>\n\n'''
    marker = "    <item>"
    if marker not in text:
        raise RuntimeError("RSS neobsahuje první položku.")
    path.write_text(text.replace(marker, item + marker, 1), encoding="utf-8", newline="\n")


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = [x for x in data.get("articles", []) if isinstance(x, dict) and x.get("url") != URL]
    articles.append({
        "title": TITLE,
        "h1": TITLE,
        "url": URL,
        "published_at": PUBLISHED,
        "modified_at": MODIFIED,
        "persons": ["Žaneta Veselá"],
        "organizations": ["Ústecký kraj", "Zdravotnická záchranná služba Ústeckého kraje"],
        "places": ["Kadaň", "Golovinova ulice", "Ústecký kraj", "Žatec"],
        "cases": ["ZZS ÚK – Realizace garáže a myčky výjezdové základny ZZS ÚK v Kadani"],
        "topics": ["Zdravotnictví", "Záchranná služba", "Veřejná zakázka", "Investice", "Design & Build"],
        "fingerprint": FINGERPRINT,
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "source_path": f"clanky/{SLUG}.html",
        "publication_status": "published",
        "source_commit": "pending-publication-commit",
    })
    articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    data["articles"] = articles
    data["article_count"] = len(articles)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["homepage_count"] = min(14, len(articles))
    validation["archive_count"] = len(articles)
    validation["archive_page_count"] = ceil(len(articles) / 12)
    validation["rss_count"] = len(articles)
    validation["sitemap_all_articles_present"] = True
    validation["news_sitemap_recent_count"] = min(10, len(articles))
    urls = [x.get("url") for x in articles]
    fps = [x.get("fingerprint") for x in articles]
    validation["duplicate_urls"] = sorted({x for x in urls if x and urls.count(x) > 1})
    validation["duplicate_fingerprints"] = sorted({x for x in fps if x and fps.count(x) > 1})
    validation["repair_pending_public_verification"] = True
    validation["last_consistency_audit"] = {"status": "pending_public_verification", "checked_at": datetime.now(timezone.utc).isoformat(), "article_count": len(articles), "updated_url": URL, "source_commit": "pending-publication-commit"}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


base.make_social = make_social
base.article_page = article_page
base.update_rss = update_rss
base.update_registry = update_registry

if __name__ == "__main__":
    raise SystemExit(base.main())
