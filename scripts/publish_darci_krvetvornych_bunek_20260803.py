#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = "zaregistrovala-se-v-kadani-darovala-krvetvorne-bunky-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
URL = f"https://nasekadan.cz{REL}"
TITLE = "Zaregistrovala se v Kadani. O rok později darovala krvetvorné buňky konkrétnímu pacientovi"
DESC = (
    "Andrea Reifová se zapsala do registru přímo v Nemocnici Kadaň. "
    "Přibližně po roce se našla shoda a skutečně darovala krvetvorné buňky. "
    "Registrace je v Kadani dostupná od úterý do čtvrtka."
)
PUBLISHED = "2026-08-03T12:22:00+02:00"
PUBLISHED_HUMAN = "3. SRPNA 2026 · 12:22"
IMAGE_URL = "https://nasekadan.cz/social-preview.png"
HOSPITAL_SOURCE = "https://www.nemkadan.cz/pro-verejnost/verejnost/aktuality/rozhovor-s-osobnosti-950cs.html"
REGISTRY_SOURCE = "https://www.darujzivot.cz/pro-darce/podminky-vstupu"
REGISTRATION_SOURCE = "https://www.darujzivot.cz/pro-darce/prihlaska-do-registru"
TRANSFUSION_SOURCE = "https://www.nemkadan.cz/neluzkova-odd/transfuzni-oc/zakladni-informace/"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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
        "image": [IMAGE_URL],
        "inLanguage": "cs-CZ",
        "isAccessibleForFree": True,
        "about": [
            {"@type": "Organization", "name": "Nemocnice Kadaň"},
            {"@type": "Thing", "name": "Český registr dárců krvetvorných buněk"},
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
<meta name="description" content="{escape(DESC)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{URL}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
<meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň"><meta property="og:title" content="{escape(TITLE)}"><meta property="og:description" content="{escape(DESC)}"><meta property="og:url" content="{URL}"><meta property="og:image" content="{IMAGE_URL}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(TITLE)}"><meta name="twitter:description" content="{escape(DESC)}"><meta name="twitter:image" content="{IMAGE_URL}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
<link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml"><link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt"><meta name="theme-color" content="#9f2626">
<style>
.article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}}.article h1{{font:800 clamp(38px,6vw,64px)/1.03 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}}.article h2{{font:800 34px/1.15 Georgia,serif;margin:45px 0 14px}}.article p,.article li{{font-size:18px;line-height:1.7}}.article a{{color:#9f2626;text-decoration:underline;text-underline-offset:3px}}.leadtext{{font-size:23px!important;color:#465862;line-height:1.55!important}}.story-hero{{position:relative;overflow:hidden;min-height:330px;margin:30px 0;border-radius:24px;background:linear-gradient(135deg,#071d34,#0f5890 55%,#b51f36);display:flex;align-items:flex-end;padding:34px;color:#fff}}.story-hero:before,.story-hero:after{{content:'';position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ff8a92,#b40020 55%,#65000d);box-shadow:0 22px 50px #0004}}.story-hero:before{{width:190px;height:190px;right:70px;top:42px}}.story-hero:after{{width:110px;height:110px;right:245px;top:135px}}.story-hero strong{{position:relative;z-index:2;max-width:580px;font:800 36px/1.12 Georgia,serif}}.service-box{{background:#eef7fb;border:1px solid #c9dfe9;border-left:7px solid #1976a3;border-radius:0 18px 18px 0;padding:23px 25px;margin:30px 0}}.service-box h2{{margin:0 0 12px;color:#124e6a}}.service-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}.service-item{{background:#fff;border-radius:14px;padding:16px}}.service-item strong{{display:block;color:#124e6a;margin-bottom:4px}}.quote-box{{background:#fff7ec;border:1px solid #ead4af;border-radius:18px;padding:23px 25px;margin:28px 0}}.quote-box strong{{font:800 24px Georgia,serif;color:#70430f}}.source-list{{background:#eef3f5;border-radius:18px;padding:24px}}.sticky{{position:sticky;top:100px}}.sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}.sidebox h3{{font:800 23px Georgia,serif;margin:0 0 12px}}.sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}@media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}}}@media(max-width:700px){{.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.story-hero{{min-height:260px;padding:24px}}.story-hero strong{{font-size:29px;max-width:75%}}.story-hero:before{{width:140px;height:140px;right:-25px;top:35px}}.story-hero:after{{width:75px;height:75px;right:90px;top:130px}}.service-grid{{grid-template-columns:1fr}}}}
</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script><script data-nasekadan-breadcrumbs="1" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False, separators=(',', ':'))}</script></head>
<body><header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1"><article class="article"><p class="tag">NEMOCNICE KADAŇ · DÁRCOVSTVÍ · PRAKTICKÉ INFORMACE · {PUBLISHED_HUMAN}</p><h1>{escape(TITLE)}</h1><p class="leadtext"><strong>{escape(DESC)}</strong></p>
<div class="story-hero" role="img" aria-label="Symbolické znázornění krvetvorných buněk"><strong>Několik minut při registraci může jednou znamenat šanci na život pro konkrétního pacienta.</strong></div>
<p>Referentka Nemocnice Kadaň Andrea Reifová se do Českého registru dárců krvetvorných buněk při IKEM zapsala přímo v kadaňské nemocnici. Vyplnila zdravotní dotazník a zdravotníci jí odebrali jednu zkumavku krve. V té chvíli ještě netušila, že se vhodný pacient najde už přibližně za rok.</p>
<p>Po oznámení možné shody následovaly další krevní testy, vyšetření HLA znaků a podrobné předodběrové kontroly. Celá příprava trvala několik měsíců. Nakonec se ukázalo, že právě ona je pro konkrétního pacienta nejvhodnější dárkyní.</p>
<h2>Samotný odběr proběhl ze krve</h2>
<p>V jejím případě nebylo potřeba odebírat kostní dřeň z pánevní kosti. Několik dní před odběrem si aplikovala přípravné injekce a krvetvorné buňky byly následně odebrány pomocí separátoru z krve. Odběr trval přibližně čtyři hodiny a probíhal pod dohledem zdravotníků.</p>
<p>Po několika dnech odpočinku se vrátila k běžnému životu. Nemocnice její zkušenost zveřejnila jako připomínku, že do registru se mohou zapojit i lidé, kteří nejsou zdravotníky. Samotná registrace ještě neznamená, že člověk bude určitě darovat; k odběru dochází až tehdy, když se najde potřebná shoda s konkrétním pacientem.</p>
<div class="quote-box"><strong>Nejde o nově zavedenou službu</strong><p>Nemocnice registraci nabízela už dříve. Aktuální je příběh dárkyně, která se zaregistrovala v Kadani a později skutečně darovala krvetvorné buňky, a nové připomenutí pravidelných registračních časů.</p></div>
<div class="service-box"><h2>Registrace přímo v Kadani</h2><div class="service-grid"><div class="service-item"><strong>Kdy přijít</strong>Úterý až čtvrtek, 6:30–8:30</div><div class="service-item"><strong>Kam</strong>Transfúzní odběrové centrum Nemocnice Kadaň</div><div class="service-item"><strong>Co s sebou</strong>Průkaz totožnosti a kartičku zdravotní pojišťovny</div><div class="service-item"><strong>Kontakt</strong>474 944 387<br>transfuze@nemkadan.cz</div></div></div>
<h2>Kdo může do registru vstoupit</h2><p>Český registr dárců krvetvorných buněk uvádí zejména tyto základní podmínky:</p><ul><li>věk od 18 do 40 let, tedy do 41. narozenin,</li><li>výborný zdravotní stav,</li><li>hmotnost více než 50 kilogramů,</li><li>bez trvalé medikace a léčby; výjimkou je hormonální antikoncepce,</li><li>platné veřejné zdravotní pojištění v České republice,</li><li>ochota podstoupit další vyšetření a případně darovat konkrétnímu pacientovi.</li></ul>
<p>Lehká alergie bez trvalé medikace podle aktuálního nemocničního příspěvku registraci sama o sobě nevylučuje. Konečné posouzení zdravotního stavu ale vždy náleží registru a zdravotníkům.</p>
<h2>Co se děje při registraci</h2><p>Zájemce vyplní krátký zdravotní dotazník, podepíše souhlas a poskytne vzorek pro určení tkáňových znaků. V kadaňském centru jde podle nemocnice o malý odběr krve. Registr nabízí také možnost domácího stěru z úst po předchozí konzultaci.</p>
<p>Údaje zůstávají v registru a člověk se stává potenciálním dárcem. Může se stát, že nebude osloven nikdy. Když se ale objeví pacient s odpovídajícími tkáňovými znaky, následují další testy a teprve poté rozhodnutí o skutečném darování.</p>
<h2>Zdroje</h2><ul class="source-list"><li><a href="{HOSPITAL_SOURCE}" rel="noopener">Nemocnice Kadaň: rozhovor s Andreou Reifovou</a></li><li><a href="{REGISTRY_SOURCE}" rel="noopener">Český registr dárců krvetvorných buněk: podmínky vstupu</a></li><li><a href="{REGISTRATION_SOURCE}" rel="noopener">Český registr: jak registrace probíhá</a></li><li><a href="{TRANSFUSION_SOURCE}" rel="noopener">Transfúzní odběrové centrum Nemocnice Kadaň</a></li></ul></article>
<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>Út–Čt 6:30–8:30</li><li>věk 18–40 let</li><li>hmotnost nad 50 kg</li><li>dobrý zdravotní stav</li><li>doklad a kartička pojišťovny</li></ul></div><div class="sidebox"><h3>Kontakt v Kadani</h3><p><strong>474 944 387</strong><br><a href="mailto:transfuze@nemkadan.cz">transfuze@nemkadan.cz</a></p></div><div data-promos data-context="sidebar"></div></aside></main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div><div class="footer-column"><strong>Kontakt</strong><a href="/o-webu/">O webu</a><a href="/zapojte-se/">Poslat tip</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a></div></footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script><script src="/site.js" defer></script><script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script><script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script><script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script><script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script><script src="/navigation.js?v=20260726-unified-footer-1" defer></script><script src="/upoutavky.js?v=20260726-home-fix-1" defer></script></body></html>'''


def update_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    hero = f'''<section class="wrap hero" id="clanky" data-auto-latest-hero="1" data-latest-article-href="{REL}">
    <article class="lead">
      <div class="photo" style="background:linear-gradient(135deg,#071d34,#0f5890 55%,#b51f36)"><span>NEMOCNICE KADAŇ · DÁRCOVSTVÍ · PRAKTICKÉ INFORMACE · {PUBLISHED_HUMAN}</span><strong>3. 8. 2026</strong></div>
      <div class="copy"><small>NEMOCNICE KADAŇ · DÁRCOVSTVÍ · {PUBLISHED_HUMAN}</small><h1>{escape(TITLE)}</h1><p>{escape(DESC)}</p><a class="btn" href="{REL}">Přečíst nejnovější článek →</a></div>
    </article>
    <aside class="current-aside"><p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p><p class="aside-date">3. 8. 2026 v 10:30</p><h2>ČEZ chce u Kadaně postavit solární park s bateriemi</h2><p>Přesný výkon a kapacita baterií, investiční cena ani výše plateb městu ve veřejných dokumentech nejsou.</p><a class="aside-button" href="/clanky/fve-epr-letiste-bess-kadan-2026.html">Přečíst článek →</a><div class="aside-links"><a href="/clanky/">Všechny články podle data</a></div></aside>
  </section>'''
    text, count = re.subn(r'<section class="wrap hero"\b.*?</section>', hero, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Na titulce nebyla nalezena hlavní sekce hero.")
    write(path, text)


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    if REL not in text:
        card = f'''\n    <article class="article-card hospital" data-auto-article="{SLUG}"><div class="visual" style="background:linear-gradient(135deg,#071d34,#0f5890 55%,#b51f36)"><strong>{escape(TITLE)}</strong></div><div class="article-body"><span class="meta">3. 8. 2026 · 12:22 · NEMOCNICE KADAŇ · DÁRCOVSTVÍ · PRAKTICKÉ INFORMACE</span><h3>{escape(TITLE)}</h3><p>{escape(DESC)}</p><a class="read-more" href="{REL}">Přečíst článek →</a></div></article>\n'''
        text = text.replace('<div class="archive-list">', '<div class="archive-list">' + card, 1)

    pattern = re.compile(r'(<script type="application/ld\+json">\s*)(\{.*?\})(\s*</script>)', re.S)
    for match in list(pattern.finditer(text)):
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph") if isinstance(data, dict) else None
        if not isinstance(graph, list):
            continue
        itemlist = next((node for node in graph if isinstance(node, dict) and node.get("@type") == "ItemList"), None)
        if not itemlist:
            continue
        items = itemlist.setdefault("itemListElement", [])
        if not any(isinstance(item, dict) and item.get("url") == URL for item in items):
            items.insert(0, {"@type": "ListItem", "position": 1, "url": URL, "name": TITLE})
        for pos, item in enumerate(items, 1):
            if isinstance(item, dict):
                item["position"] = pos
        itemlist["numberOfItems"] = len(items)
        replacement = match.group(1) + json.dumps(data, ensure_ascii=False, indent=2) + match.group(3)
        text = text[:match.start()] + replacement + text[match.end():]
        break
    write(path, text)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    rss_date = format_datetime(datetime.fromisoformat(PUBLISHED))
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{rss_date}</lastBuildDate>', text, count=1)
    if URL not in text:
        item = f'''<item><title>{escape(TITLE)}</title><description><![CDATA[{DESC}]]></description><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{rss_date}</pubDate><category>Nemocnice Kadaň</category><category>Dárcovství</category><category>Praktické informace</category><szn:image><szn:url>{IMAGE_URL}</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>\n\n    '''
        text = text.replace('<item>', item + '<item>', 1)
    write(path, text)


def update_sitemaps() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    if URL not in text:
        text = text.replace('</urlset>', f'  <url><loc>{URL}</loc></url>\n</urlset>', 1)
    write(sitemap, text)

    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    if URL not in text:
        node = f'''  <url>\n    <loc>{URL}</loc>\n    <news:news>\n      <news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication>\n      <news:publication_date>{PUBLISHED}</news:publication_date>\n      <news:title>{escape(TITLE)}</news:title>\n    </news:news>\n  </url>\n'''
        text = text.replace('>', '>\n' + node, 1) if '<urlset' in text and '<url>' not in text else text.replace('  <url>', node + '  <url>', 1)
        if URL not in text:
            text = text.replace('</urlset>', node + '</urlset>', 1)
    write(news, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        entry = f'- [{TITLE}]({URL})\n  {DESC}\n'
        marker = '## Nejnovější vlastní články\n\n'
        text = text.replace(marker, marker + entry, 1)
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    if not any(item.get("url") == URL for item in articles if isinstance(item, dict)):
        try:
            source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        except Exception:
            source_commit = ""
        articles.insert(0, {
            "title": TITLE,
            "h1": TITLE,
            "url": URL,
            "published_at": PUBLISHED,
            "modified_at": PUBLISHED,
            "persons": ["Andrea Reifová"],
            "organizations": ["Nemocnice Kadaň", "Český registr dárců krvetvorných buněk", "IKEM"],
            "places": ["Kadaň", "Praha"],
            "cases": ["Registrace dárců krvetvorných buněk v Kadani"],
            "topics": ["Zdravotnictví", "Dárcovství", "Praktické informace"],
            "fingerprint": sha256(URL.encode()).hexdigest()[:24],
            "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
            "source_path": f"clanky/{SLUG}.html",
            "publication_status": "published",
            "source_commit": source_commit,
        })
    data["article_count"] = len(articles)
    validation = data.setdefault("validation", {})
    validation["homepage_count"] = len(articles)
    validation["archive_count"] = len(articles)
    validation["rss_count"] = len(articles)
    validation["news_sitemap_recent_count"] = int(validation.get("news_sitemap_recent_count", 0)) + 1
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    write(ARTICLE, article_page())
    update_home()
    update_archive()
    update_rss()
    update_sitemaps()
    update_llms()
    update_registry()
    subprocess.run(["python3", str(ROOT / "scripts" / "ensure_weather_loader.py")], cwd=ROOT, check=True)
    required = [ARTICLE, ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "llms.txt"]
    for path in required:
        text = path.read_text(encoding="utf-8", errors="replace")
        if path == ARTICLE and f'<h1>{TITLE}</h1>' not in text:
            raise RuntimeError("V článku chybí očekávaný H1.")
        if path != ARTICLE and REL not in text and path.name != "llms.txt":
            raise RuntimeError(f"V souboru {path} chybí odkaz na článek.")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if '/pocasi.js' not in home:
        raise RuntimeError("Publikace by odstranila loader počasí.")
    print(f"Připraveno k publikaci: {URL}")


if __name__ == "__main__":
    main()
