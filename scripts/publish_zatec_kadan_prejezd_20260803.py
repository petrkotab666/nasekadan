#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from html import escape
import json
import re
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SLUG = "silnice-zatec-kadan-prejezd-uzavirka-srpen-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
SOCIAL = ROOT / "social" / "silnice-zatec-kadan-prejezd-uzavirka-20260803.png"
URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
REL = f"/clanky/{SLUG}.html"
TITLE = "Dva přejezdy, dva termíny: silnice Žatec–Kadaň se zavře už 4. srpna"
DESC = "Úplná uzavírka silnice II/225 u přejezdu za odbočkou na Žabokliky začne 4. srpna. Druhý termín 11.–28. srpna patří jinému přejezdu."
PUBLISHED = "2026-08-03T18:35:00+02:00"
MODIFIED = "2026-08-03T21:55:00+02:00"
RSS_DATE = "Mon, 03 Aug 2026 18:35:00 +0200"
IMAGE_URL = f"https://nasekadan.cz/social/{SOCIAL.name}"
CITY_SOURCE = "https://www.mesto-zatec.cz/mesto/aktualne/zacne-tydenni-uzavirka-silnice-ii-225-u-zeleznicniho-prejezdu-smerem-na-kadan-5020cs.html"
DUK_SOURCE = "https://provoz.kr-ustecky.cz/TMD/LockoutsCTO/Get?pdsei=0"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def article_html() -> str:
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
        "image": [IMAGE_URL],
        "inLanguage": "cs-CZ",
        "isAccessibleForFree": True,
    }
    return f'''<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escape(TITLE)} | Naše Kadaň</title>
  <meta name="description" content="{escape(DESC)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <link rel="canonical" href="{URL}">
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
  <meta property="og:locale" content="cs_CZ">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="{escape(TITLE)}">
  <meta property="og:description" content="{escape(DESC)}">
  <meta property="og:url" content="{URL}">
  <meta property="og:image" content="{IMAGE_URL}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(TITLE)}">
  <meta name="twitter:description" content="{escape(DESC)}">
  <meta name="twitter:image" content="{IMAGE_URL}">
  <meta property="article:published_time" content="{PUBLISHED}">
  <meta property="article:modified_time" content="{MODIFIED}">
  <meta name="theme-color" content="#9f2626">
  <style>
    .article-shell{{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}}
    .article h1{{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}}
    .article h2{{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}}
    .article h3{{font:800 25px/1.2 Georgia,serif;margin:30px 0 10px}}
    .article p,.article li{{font-size:18px;line-height:1.7}}
    .article a{{color:#9f2626;text-decoration:underline;text-underline-offset:3px}}
    .leadtext{{font-size:23px!important;color:#465862;line-height:1.55!important}}
    .updated-note{{background:#fff4dc;border:1px solid #ead19a;border-radius:12px;padding:12px 15px;font-size:15px!important;color:#674b13}}
    .facts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:30px 0}}
    .fact{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:21px;box-shadow:0 8px 25px #16242d0a}}
    .fact b{{display:block;color:#9f2626;font:800 30px Georgia,serif;margin-bottom:5px}}
    .fact span{{font-size:14px;color:#667780;line-height:1.45}}
    .callout{{border-left:6px solid #9f2626;background:#f7f1e7;padding:22px 26px;border-radius:0 16px 16px 0;margin:30px 0}}
    .callout strong{{display:block;font:800 24px Georgia,serif;margin-bottom:7px}}
    .callout p{{margin:0}}
    .info-box{{background:#eef4f6;border:1px solid #d7e1e5;border-radius:18px;padding:23px 25px;margin:28px 0}}
    .comparison{{width:100%;border-collapse:separate;border-spacing:0;margin:26px 0;background:#fff;border:1px solid #dce3e6;border-radius:18px;overflow:hidden;box-shadow:0 10px 30px #16242d0d}}
    .comparison th,.comparison td{{padding:14px 15px;border-bottom:1px solid #dce3e6;text-align:left;vertical-align:top;font-size:16px;line-height:1.5}}
    .comparison th{{color:#153b51;background:#f1f5f6}}
    .comparison tr:last-child th,.comparison tr:last-child td{{border-bottom:0}}
    .checklist{{background:#eef3f5;border-radius:18px;padding:24px 28px;margin:28px 0}}
    .checklist li{{margin-bottom:9px}}
    .source-list{{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}}
    .source-list li{{font-size:15px;margin-bottom:8px;line-height:1.5}}
    .sticky{{position:sticky;top:100px}}
    .sidebox{{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}}
    .sidebox h3{{font:800 23px Georgia,serif;margin:0 0 12px}}
    .sidebox p,.sidebox li{{font-size:14px;line-height:1.5}}
    @media(max-width:980px){{.article-shell{{grid-template-columns:1fr}}.sticky{{position:static}}.facts{{grid-template-columns:1fr}}}}
    @media(max-width:700px){{.article h1{{font-size:42px}}.leadtext{{font-size:20px!important}}.comparison th,.comparison td{{display:block;width:auto}}.comparison th{{padding-bottom:5px}}.comparison td{{padding-top:5px}}}}
  </style>
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
<header data-site-header="v1">
  <div class="wrap head">
    <a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
    <nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav>
  </div>
</header>
<main class="wrap article-shell" data-article-template="unified-v1">
<article class="article">
  <p class="tag">DOPRAVA · ŽATEC–KADAŇ · 3. SRPNA 2026 · 18:35</p>
  <h1>{escape(TITLE)}</h1>
  <p class="leadtext"><strong>Úplná uzavírka silnice II/225 za Žatcem začne v úterý 4. srpna v 7 hodin a skončit má 11. srpna v 6 hodin. Kraj současně eviduje další přejezd označený jako Žabokliky, který bude uzavřen od 11. do 28. srpna. Právě dvě různá místa způsobila zmatek v termínech.</strong></p>
  <p class="updated-note"><strong>Aktualizováno 3. srpna ve 21:55:</strong> Město Žatec zveřejnilo přesné objízdné trasy pro vozidla do 3,5 tuny a nad 3,5 tuny. Článek jsme podle oficiálního oznámení doplnili.</p>

  <div class="facts">
    <div class="fact"><b>4. srpna</b><span>Začátek úplné uzavírky hlavní silnice II/225 směrem na Kadaň.</span></div>
    <div class="fact"><b>11. srpna</b><span>V 6:00 má první uzavírka skončit; v 7:00 začne uzavírka jiného přejezdu.</span></div>
    <div class="fact"><b>Linka 415</b><span>Pojede objížďkou přes Břežany a podle kraje obslouží všechny své zastávky.</span></div>
    <div class="fact"><b>Dva přejezdy</b><span>Nejde o jeden termín prodloužený do 28. srpna, ale o dvě samostatné akce.</span></div>
  </div>

  <p>Řidiči jedoucí ze Žatce směrem na Kadaň musí od úterního rána počítat s úplnou uzavírkou železničního přejezdu na silnici II/225. Město Žatec upřesňuje, že se přejezd nachází za křižovatkou na Žabokliky ve směru na Kadaň.</p>

  <p>Odbor dopravně správních agend Městského úřadu Žatec povolil uzavírku od <strong>4. srpna 2026 v 7:00</strong> do <strong>11. srpna 2026 v 6:00</strong>. Stejný interval uvádí také informační systém Dopravy Ústeckého kraje, který tuto událost vede pod názvem <strong>Nové Sedlo – uzavírka železničního přejezdu</strong>.</p>

  <p>Důvodem omezení je podle města <strong>výstavba nového přejezdového systému</strong>, která má zvýšit bezpečnost silniční i železniční dopravy.</p>

  <div class="callout">
    <strong>Kde vznikl zmatek</strong>
    <p>V krajském systému je současně druhá událost nazvaná „Žabokliky – uzavírka železničního přejezdu“. Ta má začít až 11. srpna a skončit 28. srpna. Jde však o jiný přejezd, nikoli o prodloužení uzavírky hlavní silnice II/225.</p>
  </div>

  <h2>Dva přejezdy vedle sebe v kalendáři</h2>
  <table class="comparison">
    <tr><th>Uzavírka hlavní silnice II/225</th><td><strong>4. 8. od 7:00 – 11. 8. do 6:00</strong><br>Přejezd za odbočkou na Žabokliky ve směru ze Žatce na Kadaň. Kraj jej v dopravním systému označuje jako Nové Sedlo.</td></tr>
    <tr><th>Druhý přejezd označený Žabokliky</th><td><strong>11. 8. od 7:00 – 28. 8. do 14:00</strong><br>Samostatná následná uzavírka. Kraj u ní uvádí, že nebude mít vliv na veřejnou linkovou autobusovou dopravu.</td></tr>
  </table>

  <p>Časově na sebe obě akce téměř navazují. První má skončit 11. srpna v 6 hodin, druhá začít téhož dne v 7 hodin. Podobný název i blízkost míst proto mohou snadno vyvolat dojem, že jde o jedinou uzavírku s rozdílně uváděným termínem.</p>

  <h2>Osobní auta přes Žabokliky, těžší vozidla dlouhou objížďkou</h2>
  <p>Přes uzavřený přejezd na silnici II/225 nebude možné projet. Město Žatec zveřejnilo dvě rozdílné objízdné trasy podle hmotnosti vozidla.</p>

  <div class="info-box">
    <strong>Vozidla do 3,5 tuny:</strong> budou vedena <strong>obousměrně přes Žabokliky</strong>. Tato kratší objížďka se týká zejména osobních aut a lehkých dodávek.
  </div>

  <div class="info-box">
    <strong>Vozidla nad 3,5 tuny:</strong> ve směru ze Žatce pojedou od Kauflandu směrem na Plzeň přes <strong>Radíčeves, Sýrovice, Pšov, Dolánky, Vysoké Třebčice, Široké Třebčice, Račetice a Pětipsy</strong>. V Pětipsech se napojí zpět na silnici II/225.
  </div>

  <p>Pro těžší dopravu jde o výrazně delší trasu vedenou jižně od Nechranické přehrady. Řidiči jedoucí v opačném směru se musí řídit dočasným dopravním značením. Město vyzývá k vyšší opatrnosti a k počítání s delší dobou jízdy.</p>

  <p>Uzavírka začíná už následující ráno. Omezení tak může zasáhnout dojíždění za prací, cesty k lékaři i běžné spojení mezi Kadaní, obcemi na trase a Žatcem.</p>

  <h2>Autobusy linky 415 pojedou přes Břežany</h2>
  <p>Doprava Ústeckého kraje uvádí, že autobusová linka 415 bude kvůli první uzavírce vedena přes Břežany bez zastavení. Přesto mají zůstat obslouženy všechny pravidelné zastávky linky.</p>

  <p>Objízdná trasa autobusu ale automaticky neznamená, že stejná cesta bude určena i pro veškerou individuální dopravu. Řidiči se musí řídit přechodným dopravním značením.</p>

  <div class="info-box">
    <strong>Praktická informace pro cestující:</strong> kraj zatím neohlásil zrušení žádné zastávky linky 415 kvůli přejezdu na II/225. Kvůli objížďce však nelze vyloučit provozní zpoždění.
  </div>

  <h2>Opravy jsou rozdělené do více etap</h2>
  <p>Ve stejném období se opravují také další železniční přejezdy v širším okolí Žatce. Od 4. srpna je v krajském systému vedena uzavírka přejezdu v Kněžicích, která má trvat do 15. srpna. Kraj u ní neuvádí dopad na veřejné autobusy.</p>

  <p>Od 4. do 12. srpna má být uzavřen také přejezd v Čejkovicích. Tam se omezení dotkne autobusové linky 751 a zastávka Libědice, Čejkovice nebude dočasně obsluhována.</p>

  <p>Další přejezd vedený jako Žabokliky naváže 11. srpna. Záznamy tak ukazují postupnou sérii oprav železniční infrastruktury, nikoli jedinou dlouhou uzavírku jednoho místa.</p>

  <h2>Co se zatím z veřejných podkladů nedozvíme</h2>
  <ul class="checklist">
    <li>podrobnou technickou specifikaci nového přejezdového systému,</li>
    <li>cenu prací a jméno dodavatele,</li>
    <li>zda mohou nepředvídané okolnosti ovlivnit konečný termín otevření.</li>
  </ul>

  <p>Naše Kadaň bude kontrolovat případné změny termínů i další informace Dopravy Ústeckého kraje. Pro cestu po II/225 je ale rozhodující už nyní potvrzený údaj: hlavní přejezd směrem z Žatce na Kadaň se zavírá <strong>4. srpna v 7 hodin</strong>.</p>

  <div class="source-list">
    <h2>Zdroje a ověření</h2>
    <ul>
      <li><a href="{CITY_SOURCE}" target="_blank" rel="noopener noreferrer">Město Žatec – oznámení, objízdné trasy a mapa uzavírky silnice II/225</a></li>
      <li><a href="{DUK_SOURCE}" target="_blank" rel="noopener noreferrer">Doprava Ústeckého kraje – aktuální přehled uzavírek přejezdů a změn autobusové dopravy</a></li>
    </ul>
    <p><strong>Metodická poznámka:</strong> článek je samostatným redakčním zpracováním primárních úředních zdrojů. Rozlišuje dvě různé uzavírky a nepřebírá text ani stavbu článku z regionálních médií.</p>
  </div>
</article>
<aside class="sticky">
  <div class="sidebox"><h3>Hlavní uzavírka</h3><ul><li>Silnice II/225</li><li>4. 8. v 7:00</li><li>11. 8. v 6:00</li><li>Úplná uzavírka přejezdu</li></ul></div>
  <div class="sidebox"><h3>Druhý přejezd</h3><ul><li>Označení Žabokliky</li><li>11.–28. srpna</li><li>Jiná samostatná akce</li><li>Bez omezení linkových autobusů</li></ul></div>
  <div class="sidebox"><h3>Objížďky</h3><ul><li>Do 3,5 t přes Žabokliky</li><li>Nad 3,5 t přes Pětipsy a Račetice</li></ul></div>
  <div class="sidebox"><h3>Autobus 415</h3><p>Pojede přes Břežany. Kraj uvádí, že všechny jeho pravidelné zastávky zůstanou obsloužené.</p></div>
  <div data-promos data-context="sidebar"></div>
</aside>
</main>
<footer class="site-footer" data-site-footer="v1">
  <div class="wrap footer-grid">
    <div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div>
    <div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a></div>
    <div class="footer-column"><strong>Praktické a kontakt</strong><a href="/doprava/">Doprava</a><a href="/zapojte-se/">Zapojte se</a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div>
  </div>
  <div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/cookies/">Cookies</a><a href="/provozovatel/">Provozovatel</a></div>
</footer>
<script src="/analytics.js?v=20260801-poll-results-1" defer></script>
<script src="/site.js" defer></script>
<script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script>
<script src="/ad-spacing-guard.js?v=20260730-pojistime-rotation-4" defer></script>
<script src="/reklamy-oprava-obrazku.js?v=20260730-pojistime-rotation-4"></script>
<script src="/obsah-doplnky.js?v=20260730-pojistime-rotation-4"></script>
</body>
</html>'''


def social_image() -> None:
    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 630
    image = Image.new("RGB", (w, h), (18, 39, 49))
    draw = ImageDraw.Draw(image)
    for y in range(h):
        t = y / h
        draw.line([(0, y), (w, y)], fill=(int(18 + 45*t), int(39 + 28*t), int(49 + 25*t)))
    draw.rectangle([0, 0, w, 18], fill=(159, 38, 38))
    draw.rectangle([0, h-18, w, h], fill=(205, 156, 64))
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fb = ImageFont.truetype(bold, 58)
    fm = ImageFont.truetype(bold, 31)
    fs = ImageFont.truetype(regular, 25)
    draw.text((58, 45), "NAŠE KADAŇ", font=ImageFont.truetype(bold, 34), fill="white")
    draw.rounded_rectangle([58, 112, 310, 160], radius=18, fill=(159, 38, 38))
    draw.text((78, 121), "DOPRAVNÍ OMEZENÍ", font=ImageFont.truetype(bold, 22), fill="white")
    y = 202
    for line in ["Dva přejezdy,", "dva termíny"]:
        draw.text((58, y), line, font=fb, fill="white")
        y += 72
    draw.text((60, 362), "II/225 ŽATEC – KADAŇ", font=fm, fill=(244, 210, 140))
    draw.rounded_rectangle([58, 432, 542, 520], radius=20, fill="white")
    draw.text((82, 448), "4. 8. 07:00", font=ImageFont.truetype(bold, 34), fill=(159, 38, 38))
    draw.text((82, 488), "hlavní silnice se uzavírá", font=fs, fill=(30, 45, 54))
    draw.rounded_rectangle([626, 432, 1110, 520], radius=20, outline=(230, 235, 237), width=3)
    draw.text((650, 448), "11.–28. 8.", font=ImageFont.truetype(bold, 34), fill="white")
    draw.text((650, 488), "jiný přejezd u Žaboklik", font=fs, fill=(225, 234, 237))
    # Stylizovaná dopravní značka a koleje
    draw.ellipse([900, 82, 1100, 282], fill=(245, 245, 242), outline=(159, 38, 38), width=18)
    draw.line([(960, 125), (1040, 239)], fill=(159, 38, 38), width=20)
    draw.line([(1040, 125), (960, 239)], fill=(159, 38, 38), width=20)
    draw.line([(760, 270), (1115, 270)], fill=(205, 156, 64), width=12)
    for x in range(770, 1110, 38):
        draw.line([(x, 250), (x, 290)], fill=(235, 235, 228), width=7)
    image.save(SOCIAL, optimize=True)


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{RSS_DATE}</lastBuildDate>", text, count=1, flags=re.S)
    if URL not in text:
        item = f'''    <item>
      <title>{escape(TITLE)}</title>
      <description><![CDATA[{DESC}]]></description>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{RSS_DATE}</pubDate>
      <category>Doprava</category>
      <category>Kadaňsko</category>
      <szn:image><szn:url>{IMAGE_URL}</szn:url></szn:image>
      <geo:lat>50.375984</geo:lat><geo:long>13.271307</geo:long>
    </item>\n\n'''
        pos = text.find("    <item>")
        if pos < 0:
            pos = text.find("</channel>")
        text = text[:pos] + item + text[pos:]
    write(path, text)


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if URL not in text:
        entry = f"  <url><loc>{URL}</loc><lastmod>2026-08-03</lastmod></url>\n"
        text = text.replace("</urlset>", entry + "</urlset>")
    write(path, text)


def validate() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    required = [
        f"<h1>{TITLE}</h1>",
        "4. srpna 2026 v 7:00",
        "11. srpna 2026 v 6:00",
        "Dva přejezdy",
        "data-promos data-context=\"sidebar\"",
        CITY_SOURCE,
        DUK_SOURCE,
    ]
    missing = [value for value in required if value not in article]
    if missing:
        raise SystemExit(f"Článek postrádá: {missing}")
    if "noindex" in article.lower():
        raise SystemExit("Článek nesmí být noindex.")
    for rel in ("index.html", "clanky/index.html", "rss.xml", "sitemap.xml", "news-sitemap.xml", "llms.txt"):
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"Chybí {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        if REL not in text and URL not in text:
            raise SystemExit(f"{rel} neobsahuje článek")
    if not SOCIAL.exists() or SOCIAL.stat().st_size < 10_000:
        raise SystemExit("Sociální obrázek nebyl vytvořen.")


def main() -> None:
    write(ARTICLE, article_html())
    social_image()
    update_rss()
    update_sitemap()
    subprocess.run(["python3", str(ROOT / "scripts" / "enforce_article_visibility.py")], cwd=ROOT, check=True)
    subprocess.run(["python3", str(ROOT / "scripts" / "prepare_discovery.py")], cwd=ROOT, check=True)
    # prepare_discovery může sitemapu přegenerovat; znovu jistíme kanonický záznam.
    update_sitemap()
    validate()
    print(f"Připraveno: {ARTICLE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
