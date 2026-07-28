#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("NASEKADAN_ROOT", Path(__file__).resolve().parents[1]))
SLUG = "prakticti-lekari-nemocnice-kadan-srpen-2026"
ARTICLE_PATH = ROOT / "clanky" / f"{SLUG}.html"
ARTICLE_URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
ARTICLE_HREF = f"/clanky/{SLUG}.html"
PUBLISHED = "2026-07-28T19:45:00+02:00"
TITLE = "V srpnu omezí provoz více ordinací v Kadani a okolí. Přehled termínů a zástupů"
DESC = "Ambulance MUDr. Barbory Suchecké bude zavřená od 3. do 14. srpna. MUDr. Roman Šindelář má dovolenou od 10. do 21. srpna; překryv nastane 10.–14. srpna."

ARTICLE = '''<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>V srpnu omezí provoz více ordinací v Kadani a okolí | Naše Kadaň</title>
  <meta name="description" content="Ambulance MUDr. Barbory Suchecké bude zavřená od 3. do 14. srpna. MUDr. Roman Šindelář má dovolenou od 10. do 21. srpna; překryv nastane 10.–14. srpna.">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../style.css">
  <link rel="canonical" href="https://nasekadan.cz/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#a9232b">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="V srpnu omezí provoz více ordinací v Kadani a okolí">
  <meta property="og:description" content="Od 10. do 14. srpna se překryjí dovolené dvou praktických lékařů. Nemocnice zveřejnila režim pro akutní případy.">
  <meta property="og:url" content="https://nasekadan.cz/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">
  <meta property="og:image" content="https://nasekadan.cz/social-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta property="article:published_time" content="2026-07-28T19:45:00+02:00">
  <meta property="article:modified_time" content="2026-07-28T19:45:00+02:00">
  <style>
    .article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}
    .article h1{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}
    .article h2{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}
    .article p,.article li{font-size:18px}.article .leadtext{font-size:23px;color:#465862;line-height:1.55}
    .article a{color:#9f2626;text-decoration:underline;text-underline-offset:3px}
    .hero-visual{min-height:340px;border-radius:24px;background:radial-gradient(circle at 82% 18%,#ffffff22,transparent 27%),linear-gradient(135deg,#173240,#496d7c 58%,#9f2626);display:flex;align-items:flex-end;padding:30px;color:#fff;box-shadow:var(--shadow);margin:30px 0;position:relative;overflow:hidden}
    .hero-visual:after{content:'3.–21. SRPNA';position:absolute;right:-18px;top:24px;font:900 62px/1 Arial;color:#ffffff12;white-space:nowrap}
    .hero-visual strong{font:800 31px Georgia,serif;max-width:680px;position:relative;z-index:1;text-shadow:0 2px 16px #000}
    .dates{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:30px 0}.dates div{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 8px 25px #16242d0a}.dates b{display:block;color:var(--red);font-size:28px}.dates span{font-size:15px;color:var(--muted)}
    .callout{border-left:6px solid var(--red);background:var(--cream);margin:34px 0;padding:22px 26px;border-radius:0 16px 16px 0}.callout strong{font:800 24px Georgia,serif;display:block;margin-bottom:6px}
    .source-list{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}.source-list li{font-size:15px;margin-bottom:8px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px}
    @media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}}@media(max-width:700px){.dates{grid-template-columns:1fr}.hero-visual{min-height:270px}.hero-visual:after{font-size:36px}.article h1{font-size:42px}.article .leadtext{font-size:20px}}
  </style>
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"V srpnu omezí provoz více ordinací v Kadani a okolí. Přehled termínů a zástupů","description":"Ambulance MUDr. Barbory Suchecké bude zavřená od 3. do 14. srpna. MUDr. Roman Šindelář má dovolenou od 10. do 21. srpna; překryv nastane 10.–14. srpna.","datePublished":"2026-07-28T19:45:00+02:00","dateModified":"2026-07-28T19:45:00+02:00","author":{"@type":"Organization","name":"Naše Kadaň"},"publisher":{"@type":"Organization","name":"Naše Kadaň"},"mainEntityOfPage":"https://nasekadan.cz/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html","inLanguage":"cs-CZ"}</script>
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
</head>
<body>
<header><div class="wrap head"><a class="logo" href="../index.html"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav><a href="../index.html">Úvod</a><a href="/clanky/">Články</a><a href="../index.html#akce">Akce</a><a href="../pruvodce/">Průvodce</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1">
<article class="article">
  <p class="tag">PRAKTICKÉ INFORMACE · ZDRAVOTNICTVÍ · 28. ČERVENCE 2026</p>
  <h1>V srpnu omezí provoz více ordinací v Kadani a okolí. Přehled termínů a zástupů</h1>
  <p class="leadtext"><strong>Pacienti dvou ambulancí praktických lékařů v Nemocnici Kadaň by si měli včas zajistit recepty, objednání a neakutní konzultace. Ambulance MUDr. Barbory Suchecké bude zavřená od 3. do 14. srpna a MUDr. Roman Šindelář má zveřejněnou dovolenou od 10. do 21. srpna.</strong></p>
  <div class="hero-visual"><strong>Nejvýraznější omezení nastane od pondělí 10. do pátku 14. srpna, kdy se termíny obou lékařů překryjí.</strong></div>
  <div class="dates"><div><b>3.–14. 8.</b><span>uzavřená ambulance MUDr. Suchecké</span></div><div><b>10.–21. 8.</b><span>dovolená MUDr. Šindeláře</span></div><div><b>10.–14. 8.</b><span>překryv obou omezení</span></div></div>
  <h2>Jaký režim nemocnice zveřejnila</h2>
  <p>Oficiální stránka praktických lékařů uvádí, že od 3. do 7. srpna bude akutní případy pacientů MUDr. Suchecké zastupovat MUDr. Roman Šindelář. Od 10. do 14. srpna pak nemocnice pro akutní případy uvádí pohotovost od 17 hodin.</p>
  <p>Na stejné stránce je současně uvedeno, že akutní stavy řeší nepřetržitě centrální příjem nemocnice. Tato informace se týká akutních zdravotních potíží; nenahrazuje běžné objednávání, předepisování pravidelných léků ani plánované kontroly u praktického lékaře.</p>
  <div class="callout"><strong>Co je vhodné vyřídit předem</strong><p>Pacienti, kteří budou v první polovině srpna potřebovat pravidelný recept, potvrzení, plánovanou kontrolu nebo neakutní konzultaci, by měli kontaktovat svou ambulanci ještě před začátkem uzavření. Nemocnice výslovně žádá pacienty MUDr. Suchecké o objednávání a konzultace e-mailem.</p></div>
  <h2>Kontakty na obě ambulance</h2>
  <p><strong>MUDr. Barbora Suchecká:</strong> poliklinika, III. patro, telefon 474 944 397, e-mail <a href="mailto:suchecka@nemkadan.cz">suchecka@nemkadan.cz</a>. Sestra Šárka Hubačová: <a href="mailto:hubacova@nemkadan.cz">hubacova@nemkadan.cz</a>.</p>
  <p><strong>MUDr. Roman Šindelář:</strong> poliklinika, I. patro, telefon 474 944 427, e-mail <a href="mailto:sindelar@nemkadan.cz">sindelar@nemkadan.cz</a>. Pro objednání léků nemocnice uvádí kontakt na sestru Lenku Šimkovou: <a href="mailto:simkova@nemkadan.cz">simkova@nemkadan.cz</a>.</p>
  <h2>Co zatím není uvedeno</h2>
  <p>Nemocnice na stránce neurčuje dalšího konkrétního denního zástupce pro období 10.–14. srpna. Nelze proto automaticky předpokládat, že jiná ambulance uvedená na stejné stránce přebírá běžnou péči těchto pacientů. Před cestou je vhodné ověřit aktuální režim přímo u nemocnice na ústředně 474 944 111.</p>
  <div class="source-list"><h2>Zdroje a stav informace</h2><ul><li><a href="https://www.nemkadan.cz/ambulance-1/prakticky-lekar-pro-dospele/" target="_blank" rel="noopener noreferrer">Nemocnice Kadaň – Praktický lékař pro dospělé</a>: termíny dovolených, režim akutních případů, kontakty a ordinační údaje. Stránka uvádí poslední aktualizaci 10. července 2026.</li></ul><p><small>Stav ověřen 28. července 2026 v 19:45. Při změně nemocničního oznámení článek aktualizujeme.</small></p></div>
</article>
<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>MUDr. Suchecká: zavřeno 3.–14. 8.</li><li>MUDr. Šindelář: dovolená 10.–21. 8.</li><li>Překryv: 10.–14. 8.</li><li>Akutní stavy: centrální příjem</li><li>Ústředna: 474 944 111</li></ul></div><div data-promos data-context="sidebar"></div></aside>
</main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/o-webu/#provozovatel">Provozovatel</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/site.js" defer></script>
<script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script>
<script src="/reklamy-oprava-obrazku.js"></script>
<script src="/obsah-doplnky.js"></script>
</body></html>
'''

HERO_SECTION = '''  <section class="wrap hero" id="clanky">
    <article class="lead" data-gp-august-hero>
      <div class="photo" style="background:linear-gradient(135deg,#173240,#496d7c 58%,#9f2626)"><span>PRAKTICKÉ INFORMACE</span><strong>10.–14. SRPNA</strong></div>
      <div class="copy">
        <small>NEMOCNICE KADAŇ · 28. 07. 2026 · 19:45</small>
        <h1>V srpnu omezí provoz více ordinací v Kadani a okolí</h1>
        <p>Ambulance MUDr. Suchecké bude zavřená od 3. do 14. srpna. MUDr. Šindelář má dovolenou od 10. do 21. srpna.</p>
        <a class="btn" href="/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">Přečíst praktické informace →</a>
      </div>
    </article>
    <aside class="current-aside">
      <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
      <p class="aside-date">28. 7. 2026 v 11:30</p>
      <h2>Odstávky elektřiny omezí provoz restaurace v Autokempu Prunéřov</h2>
      <p>Ve dvou termínech otevře restaurace po 18. hodině, potřetí po 16. hodině.</p>
      <a class="aside-button" href="/clanky/odstavky-elektriny-autokemp-prunerov-srpen-2026.html">Přečíst článek →</a>
      <div class="aside-links"><a href="/clanky/arc-med-nemocnice-kadan.html">ARC-MED za 16 milionů</a><a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kulturní přehled na tento týden</a><a href="/clanky/">Všechny články podle data</a></div>
    </aside>
  </section>'''

HOME_CARD = '''    <article class="article-card hospital" data-gp-august-card>
      <div class="visual" style="background:linear-gradient(135deg,#173240,#496d7c 58%,#9f2626)"><strong>Omezení ordinací v srpnu</strong></div>
      <div class="article-body"><span class="meta">28. 7. 2026 · 19:45 · Praktické informace</span><h3>Srpnová omezení se týkají více ordinací a ambulancí</h3><p>Nemocnice zveřejnila termíny uzavření a režim pro akutní případy.</p><a class="read-more" href="/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">Přečíst článek →</a></div>
    </article>'''

ARCHIVE_CARD = '''    <article class="archive-item hospital" data-gp-august-card>
      <div class="archive-visual" style="background:linear-gradient(135deg,#173240,#496d7c 58%,#9f2626)"><strong>Omezení ordinací v srpnu</strong></div>
      <div class="archive-body"><span class="archive-meta">28. července 2026 v 19:45 · Praktické informace · Nemocnice Kadaň</span><h2>V srpnu omezí provoz více ordinací v Kadani a okolí. Přehled termínů a zástupů</h2><p>Přehled zahrnuje praktické lékaře, neurologii, ORL, očkovací centrum, internu a související regionální omezení.</p><a href="/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html">Přečíst praktické informace →</a></div>
    </article>'''

RSS_ITEM = '''    <item><title>V srpnu omezí provoz více ordinací v Kadani a okolí</title><description><![CDATA[Ambulance MUDr. Barbory Suchecké bude zavřená od 3. do 14. srpna. MUDr. Roman Šindelář má dovolenou od 10. do 21. srpna; překryv nastane 10.–14. srpna.]]></description><link>https://nasekadan.cz/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html</link><guid isPermaLink="true">https://nasekadan.cz/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html</guid><pubDate>Tue, 28 Jul 2026 19:45:00 +0200</pubDate><category>Praktické informace</category><category>Nemocnice Kadaň</category><category>Zdravotnictví</category><szn:image><szn:url>https://nasekadan.cz/social-card.png</szn:url></szn:image><geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long></item>
'''

NEWS_URL = '''  <url><loc>https://nasekadan.cz/clanky/prakticti-lekari-nemocnice-kadan-srpen-2026.html</loc><news:news><news:publication><news:name>Naše Kadaň</news:name><news:language>cs</news:language></news:publication><news:publication_date>2026-07-28T19:45:00+02:00</news:publication_date><news:title>V srpnu omezí provoz více ordinací v Kadani a okolí</news:title></news:news></url>
'''


def replace_home() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(r'  <section class="wrap hero" id="clanky">.*?</section>', HERO_SECTION, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Nenalezena hero sekce titulní stránky")
    text = re.sub(r'\s*<article\b[^>]*data-gp-august-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
    marker = '<div class="article-list">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam článků na titulní stránce")
    text = text.replace(marker, marker + "\n" + HOME_CARD, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_archive() -> None:
    path = ROOT / "clanky" / "index.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<article\b[^>]*data-gp-august-card[^>]*>.*?</article>\s*', '\n', text, flags=re.S)
    marker = '<section class="archive-list" aria-label="Chronologický přehled článků">'
    if marker not in text:
        raise RuntimeError("Nenalezen seznam archivu")
    text = text.replace(marker, marker + "\n" + ARCHIVE_CARD, 1)
    for match in list(re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)):
        try:
            data = json.loads(match.group(1))
        except Exception:
            continue
        itemlist = next((x for x in data.get("@graph", []) if x.get("@type") == "ItemList"), None) if isinstance(data, dict) else None
        if not itemlist:
            continue
        existing = [x for x in itemlist.get("itemListElement", []) if x.get("url") != ARTICLE_URL]
        existing.insert(0, {"@type": "ListItem", "url": ARTICLE_URL, "name": TITLE})
        for pos, item in enumerate(existing, 1):
            item["position"] = pos
        itemlist["itemListElement"] = existing
        itemlist["numberOfItems"] = len(existing)
        replacement = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + '</script>'
        text = text[:match.start()] + replacement + text[match.end():]
        break
    path.write_text(text, encoding="utf-8", newline="\n")


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<item>.*?<link>' + re.escape(ARTICLE_URL) + r'</link>.*?</item>\s*', '\n', text, flags=re.S)
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', '<lastBuildDate>Tue, 28 Jul 2026 19:45:00 +0200</lastBuildDate>', text, count=1)
    marker = '<atom:link href="https://nasekadan.cz/rss.xml" rel="self" type="application/rss+xml" />'
    if marker not in text:
        raise RuntimeError("Nenalezen RSS marker")
    text = text.replace(marker, marker + "\n" + RSS_ITEM, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_sitemaps() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url><loc>' + re.escape(ARTICLE_URL) + r'</loc>.*?</url>\s*', '\n', text, flags=re.S)
    text = re.sub(r'(<loc>https://nasekadan\.cz/</loc><lastmod>)[^<]+', r'\g<1>2026-07-28', text, count=1)
    text = re.sub(r'(<loc>https://nasekadan\.cz/clanky/</loc><lastmod>)[^<]+', r'\g<1>2026-07-28', text, count=1)
    text = text.replace('</urlset>', f'  <url><loc>{ARTICLE_URL}</loc><lastmod>2026-07-28</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n</urlset>')
    path.write_text(text, encoding="utf-8", newline="\n")
    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url>\s*<loc>' + re.escape(ARTICLE_URL) + r'</loc>.*?</url>\s*', '\n', text, flags=re.S)
    text = text.replace('>', '>\n' + NEWS_URL, 1) if '<urlset' in text else text
    news.write_text(text, encoding="utf-8", newline="\n")


def update_manifest() -> None:
    path = ROOT / "production-content-manifest.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    items = [x for x in data.get("required_articles", []) if x.get("path") != f"clanky/{SLUG}.html"]
    items.insert(0, {"path": f"clanky/{SLUG}.html", "needle": "V srpnu omezí provoz více ordinací v Kadani a okolí", "must_be_on_home": True, "must_be_in_archive": True})
    data["required_articles"] = items
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def protect_old_order_scripts() -> None:
    scripts = ROOT / "scripts"
    if not scripts.exists():
        return
    for name in ("ensure_kolobezky_order.py", "enforce_production_article_order.py", "enforce_homepage_latest_order.py"):
        path = scripts / name
        if not path.exists() or name == "enforce_homepage_latest_order.py":
            continue
        text = path.read_text(encoding="utf-8")
        token = "LATEST_GP_AUGUST_GUARD"
        if token in text:
            continue
        marker = "ROOT = Path(__file__).resolve().parents[1]"
        guard = marker + f'''\n# LATEST_GP_AUGUST_GUARD: staré pořadí nesmí přepsat novější praktickou zprávu.\nif (ROOT / "clanky" / "{SLUG}.html").exists():\n    print("Novější praktická zpráva o srpnovém provozu ambulancí je publikována; staré pořadí se nepoužije.")\n    raise SystemExit(0)'''
        if marker in text:
            path.write_text(text.replace(marker, guard, 1), encoding="utf-8", newline="\n")


def rewrite_latest_enforcer() -> None:
    path = ROOT / "scripts" / "enforce_homepage_latest_order.py"
    if not path.parent.exists():
        return
    content = f'''#!/usr/bin/env python3\nfrom pathlib import Path\nimport re\nROOT=Path(__file__).resolve().parents[1]\nHOME=ROOT/"index.html"\nARTICLE=ROOT/"clanky"/"{SLUG}.html"\nHERO={HERO_SECTION!r}\nCARD={HOME_CARD!r}\nif not ARTICLE.exists(): raise SystemExit("Chybí nejnovější praktická zpráva")\ntext=HOME.read_text(encoding="utf-8")\ntext,count=re.subn(r'  <section class="wrap hero" id="clanky">.*?</section>',HERO,text,count=1,flags=re.S)\nif count!=1: raise SystemExit("Nenalezena hero sekce")\ntext=re.sub(r'\\s*<article\\b[^>]*data-gp-august-card[^>]*>.*?</article>\\s*','\\n',text,flags=re.S)\nmarker='<div class="article-list">'\nif marker not in text: raise SystemExit("Nenalezen seznam článků")\ntext=text.replace(marker,marker+'\\n'+CARD,1)\nHOME.write_text(text,encoding="utf-8",newline="\\n")\nprint("Titulní stránka zachovává nejnovější praktickou zprávu o ambulancích.")\n'''
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    ARTICLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not ARTICLE_PATH.exists():
        ARTICLE_PATH.write_text(ARTICLE, encoding="utf-8", newline="\n")
    else:
        print("Existující rozšířená redakční verze článku se zachovává.")
    replace_home()
    update_archive()
    update_rss()
    update_sitemaps()
    update_manifest()
    protect_old_order_scripts()
    rewrite_latest_enforcer()
    print("Praktická zpráva o srpnovém provozu ambulancí je připravena.")


if __name__ == "__main__":
    main()
