#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "mve-hradiste-nova-vodni-elektrarna-2026"
ARTICLE = ROOT / "clanky" / f"{SLUG}.html"
SOCIAL = ROOT / "social" / f"{SLUG}.png"
TITLE = "U Hradiště má vzniknout nová malá vodní elektrárna. Vodu přivede potrubí dlouhé 520 metrů"
DESC = "Kadaňský odbor životního prostředí souhlasil s projektem nové malé vodní elektrárny na Hradišťském potoce. Přehled stavby, podmínek a toho, co zatím není rozhodnuto."
URL = f"https://nasekadan.cz/clanky/{SLUG}.html"
IMAGE = f"https://nasekadan.cz/social/{SLUG}.png"
PUBLISHED = "2026-07-31T14:50:00+02:00"
DETAIL_URL = "https://www.mesto-kadan.cz/redakce/index.php?as4uOriginalDomain=www.mesto-kadan.cz&as4u_protocol=https&clanek=274670&detail_claim=295345&lanG=cs&slozka=219380"
PDF_URL = "https://www.mesto-kadan.cz/filemanager/files/file.php?file=5122960"


def font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def make_social() -> None:
    from PIL import Image, ImageDraw

    width, height = 1200, 630
    image = Image.new("RGB", (width, height), "#102b35")
    draw = ImageDraw.Draw(image)

    # Les a obloha.
    for y in range(height):
        ratio = y / height
        draw.line((0, y, width, y), fill=(16 + int(20 * ratio), 43 + int(35 * ratio), 53 + int(25 * ratio)))
    draw.polygon([(520, 0), (1200, 0), (1200, 630), (650, 630)], fill="#cfb46d")
    draw.polygon([(565, 0), (1200, 0), (1200, 425), (690, 520)], fill="#dbe2d2")

    # Stromy v pozadí.
    for x, top, base in [(705, 80, 500), (790, 35, 495), (890, 95, 520), (990, 42, 510), (1090, 85, 520), (1160, 30, 530)]:
        draw.rectangle((x - 7, top + 80, x + 7, base), fill="#4b4a32")
        draw.polygon([(x - 75, top + 150), (x, top), (x + 75, top + 150)], fill="#315238")
        draw.polygon([(x - 65, top + 235), (x, top + 85), (x + 65, top + 235)], fill="#3d6543")

    # Potok, přivaděč a strojovna.
    draw.polygon([(590, 455), (730, 400), (900, 450), (1060, 405), (1200, 445), (1200, 630), (560, 630)], fill="#5d6f62")
    draw.polygon([(610, 530), (760, 470), (920, 520), (1090, 475), (1200, 500), (1200, 630), (590, 630)], fill="#2f7488")
    draw.line((650, 425, 1040, 575), fill="#d7d7cf", width=34)
    draw.line((650, 425, 1040, 575), fill="#6c787c", width=18)
    draw.rounded_rectangle((930, 345, 1130, 510), radius=15, fill="#e2ddd0", outline="#213a42", width=7)
    draw.polygon([(910, 360), (1030, 270), (1150, 360)], fill="#6f2f2f")
    draw.rectangle((986, 408, 1070, 510), fill="#2d4a55")
    draw.arc((820, 365, 960, 505), 185, 350, fill="#f4f0dc", width=10)

    # Tmavý redakční panel.
    draw.polygon([(0, 0), (690, 0), (610, 630), (0, 630)], fill="#071d2a")
    draw.polygon([(0, 38), (280, 38), (315, 74), (280, 110), (0, 110)], fill="#a9232b")
    draw.text((36, 53), "Naše Kadaň", font=font(36, True), fill="white")

    draw.text((42, 150), "U Hradiště má vzniknout", font=font(52, True), fill="white")
    draw.text((42, 214), "nová malá vodní", font=font(56, True), fill="white")
    draw.text((42, 282), "elektrárna", font=font(64, True), fill="#f2cc68")
    draw.rectangle((43, 365, 585, 371), fill="#a9232b")
    draw.text((43, 395), "Potrubí má měřit 520 metrů", font=font(34, True), fill="white")
    draw.text((43, 445), "Součástí bude i rybí přechod", font=font(30, True), fill="#d8e5e8")

    draw.rounded_rectangle((42, 520, 590, 586), radius=13, fill="#a9232b")
    draw.text((67, 536), "Souhlasné stanovisko, ne stavební povolení", font=font(23, True), fill="white")

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image.save(SOCIAL, "PNG", optimize=True, compress_level=9)

    with Image.open(SOCIAL) as check:
        assert check.size == (1200, 630)
        assert check.format == "PNG"


def article_html() -> str:
    style = """
.article-shell{display:grid;grid-template-columns:minmax(0,820px) 300px;gap:36px;align-items:start;padding:56px 0}
.article h1{font:800 clamp(38px,6vw,64px)/1.02 Georgia,serif;letter-spacing:-.035em;margin:.25em 0}
.article h2{font:800 34px/1.15 Georgia,serif;margin:48px 0 14px}
.article p,.article li{font-size:18px;line-height:1.7}.leadtext{font-size:23px!important;color:#465862;line-height:1.55!important}
.article a{color:#9f2626;text-decoration:underline;text-underline-offset:3px}
.article-photo{margin:30px 0}.article-photo img{display:block;width:100%;height:auto;border-radius:24px;box-shadow:0 14px 38px #16242d1c}.article-photo figcaption{font-size:14px;color:#677780;margin-top:9px}
.facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:30px 0}.fact{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:21px;box-shadow:0 8px 25px #16242d0a}.fact b{display:block;color:#9f2626;font:800 27px Georgia,serif;margin-bottom:5px}.fact span{font-size:14px;color:#667780;line-height:1.45}
.callout{border-left:6px solid #9f2626;background:#f7f1e7;padding:22px 26px;border-radius:0 16px 16px 0;margin:30px 0}.callout strong{display:block;font:800 24px Georgia,serif;margin-bottom:7px}.callout p{margin:0}
.source-list{background:#eef3f5;padding:24px;border-radius:18px;margin-top:44px}.source-list li{font-size:15px;margin-bottom:8px}.sticky{position:sticky;top:100px}.sidebox{background:#fff;border:1px solid #dce3e6;border-radius:18px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px #16242d0d}.sidebox h3{font:800 23px Georgia,serif;margin:0 0 12px}.sidebox p,.sidebox li{font-size:14px;line-height:1.5}
@media(max-width:980px){.article-shell{grid-template-columns:1fr}.sticky{position:static}.facts{grid-template-columns:1fr}}@media(max-width:700px){.article h1{font-size:42px}.leadtext{font-size:20px!important}}
""".strip()

    news_json = (
        '{"@context":"https://schema.org","@type":"NewsArticle","headline":"' + TITLE + '",'
        '"description":"' + DESC + '","datePublished":"' + PUBLISHED + '","dateModified":"' + PUBLISHED + '",'
        '"author":{"@type":"Organization","@id":"https://nasekadan.cz/#organization","name":"Naše Kadaň","url":"https://nasekadan.cz/o-webu/"},'
        '"publisher":{"@id":"https://nasekadan.cz/#organization"},'
        '"mainEntityOfPage":{"@type":"WebPage","@id":"' + URL + '"},"inLanguage":"cs-CZ",'
        '"image":["' + IMAGE + '"],"isAccessibleForFree":true}'
    )
    crumbs_json = (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Naše Kadaň","item":"https://nasekadan.cz/"},'
        '{"@type":"ListItem","position":2,"name":"Články","item":"https://nasekadan.cz/clanky/"},'
        '{"@type":"ListItem","position":3,"name":"' + TITLE + '","item":"' + URL + '"}]}'
    )

    return f'''<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{TITLE} | Naše Kadaň</title>
  <meta name="description" content="{DESC}">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../style.css">
  <link rel="canonical" href="{URL}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta property="og:locale" content="cs_CZ"><meta property="og:type" content="article"><meta property="og:site_name" content="Naše Kadaň">
  <meta property="og:title" content="{TITLE}"><meta property="og:description" content="{DESC}"><meta property="og:url" content="{URL}">
  <meta property="og:image" content="{IMAGE}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
  <meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{PUBLISHED}">
  <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{TITLE}"><meta name="twitter:description" content="{DESC}"><meta name="twitter:image" content="{IMAGE}">
  <style>{style}</style>
  <script type="application/ld+json">{news_json}</script>
  <script data-nasekadan-breadcrumbs="1" type="application/ld+json">{crumbs_json}</script>
  <link data-nasekadan-discovery="1" rel="alternate" type="application/rss+xml" title="Naše Kadaň – zprávy z Kadaně" href="https://nasekadan.cz/rss.xml">
  <link rel="alternate" type="text/plain" title="Naše Kadaň pro AI" href="https://nasekadan.cz/llms.txt">
  <meta name="geo.region" content="CZ-42"><meta name="geo.placename" content="Hradiště u Vernéřova"><meta name="geo.position" content="50.3900;13.1730"><meta name="ICBM" content="50.3900, 13.1730">
  <link rel="stylesheet" href="/footer.css?v=20260726-event-hotfix-2">
</head>
<body>
<header data-site-header="v1"><div class="wrap head"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><nav aria-label="Hlavní navigace"><a href="/clanky/">Články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/zapojte-se/">Poslat tip</a></nav></div></header>
<main class="wrap article-shell" data-article-template="unified-v1">
<article class="article">
  <p class="tag">REGION · ŽIVOTNÍ PROSTŘEDÍ · ENERGETIKA · 31. ČERVENCE 2026</p>
  <h1>{TITLE}</h1>
  <p class="leadtext"><strong>Na Hradišťském potoce mezi Hradištěm a Vernéřovem se připravuje výstavba nové malé vodní elektrárny. Kadaňský odbor životního prostředí pro projekt vydal souhlasné jednotné environmentální stanovisko. Nejde však ještě o konečné stavební povolení.</strong></p>

  <figure class="article-photo"><img src="../social/{SLUG}.png" width="1200" height="630" loading="eager" fetchpriority="high" alt="Ilustrační redakční grafika nové malé vodní elektrárny na Hradišťském potoce"><figcaption>Projekt počítá s odběrným objektem, tlakovým přivaděčem, strojovnou a rybím přechodem. Ilustrační grafika: Naše Kadaň</figcaption></figure>

  <p>Závazné stanovisko vydal Městský úřad Kadaň 27. července 2026 pod číslem jednacím <strong>MUKK/32659/2026</strong>. Na úřední desce bylo zveřejněno 30. července. Úřad označil záměr za přípustný z hlediska všech posuzovaných složek životního prostředí, stanovil ale řadu podmínek pro ochranu toku, lesa i živočichů.</p>

  <div class="facts"><div class="fact"><b>520 m</b><span>Přibližná délka tlakového přivaděče vedeného převážně po současné lesní cestě.</span></div><div class="fact"><b>20 m</b><span>Přibližný výškový rozdíl, jehož energii má nová elektrárna využívat.</span></div><div class="fact"><b>34 l/s</b><span>Minimální zůstatkový průtok, který musí zůstat v Hradišťském potoce.</span></div></div>

  <h2>Nová elektrárna, nikoli rekonstrukce</h2>
  <p>Dokument výslovně popisuje <strong>novou derivační malou vodní elektrárnu</strong>. Voda má být zachycena odběrným objektem na Hradišťském potoce a tlakovým potrubím přivedena k turbíně v samostatné strojovně. Po využití spádu se má vrátit odpadním korytem zpět do potoka.</p>
  <p>Stavba má čtyři hlavní části: odběrný objekt a vzdouvací stupeň, tlakový přivaděč, vlastní objekt MVE a zpevnění lesní cesty. Elektrická přípojka má být vedena částečně pod zemí a částečně po sloupech veřejného osvětlení.</p>

  <h2>Součástí bude rybí přechod</h2>
  <p>Na toku má vzniknout nový jez nebo vzdouvací objekt, odběr vody, rybí přechod, odpadní kanál a břehové opevnění. Přímý zásah do významného krajinného prvku vodního toku je v dokumentu vyčíslen přibližně na 500 metrů čtverečních.</p>
  <p>Kadaňský úřad hodnotí rybí přechod jako přínos. V místě se už nyní nachází migrační překážka a nový přechod má vodním živočichům zpřístupnit delší část Hradišťského potoka. Většina viditelných vodních staveb má být provedena z lomového kamene, aby navázala na stávající opevnění.</p>

  <h2>Roční zkušební provoz a minimální průtok</h2>
  <p>Pod odběrným objektem musí zůstat minimálně <strong>0,034 metru krychlového vody za sekundu</strong>, tedy 34 litrů za sekundu. Povodí Ohře požaduje před trvalým uvedením elektrárny do provozu nejméně roční zkušební provoz MVE i všech souvisejících objektů.</p>
  <p>Pro dobu stavby musí vzniknout havarijní a povodňový plán. Pro provoz elektrárny bude nutné zpracovat provozní a manipulační řád, který musí projít vyjádřením Povodí Ohře a následným schválením vodoprávního úřadu.</p>

  <h2>Práce na toku budou časově omezené</h2>
  <p>Stavební práce přímo v Hradišťském potoce, včetně budování vzdouvacího objektu a strojovny, jsou omezeny na období od <strong>16. srpna do 30. listopadu</strong>. Výkopové práce pro přivaděč mohou probíhat od 16. srpna do 31. března.</p>
  <p>Po celou dobu přípravy a realizace musí být zajištěn odborný biologický dozor. Otevřené výkopy bude nutné zakrývat, aby se do nich nedostali obojživelníci, plazi a další živočichové. Na odběrném objektu mají být jemné česle a elektronická odpuzující zábrana.</p>

  <h2>Zásah do lesa a kácení</h2>
  <p>Kvůli potrubí a přípojkám má být dočasně vyňato z lesního půdního fondu celkem <strong>1 582 metrů čtverečních</strong>. Dokument stanoví dobu od 1. března 2027 do 31. prosince 2028, tedy 22 měsíců. Trvalé odnětí se týká 43 metrů čtverečních. Předpokládaný poplatek za odnětí je přibližně 29 544 korun.</p>
  <p>Povoleno je také pokácení jedné olše lepkavé a dvou černých bezů. Kácení může proběhnout pouze při realizaci projektu a v období od 16. srpna do 31. března.</p>

  <h2>Kdo projekt připravil</h2>
  <p>Žádost podal v listopadu 2025 Ivo Frýdl. Projektovou dokumentaci zpracovala společnost <strong>Intensys s.r.o.</strong> a jako projektant je uveden rovněž Ivo Frýdl. Žádost musela být doplněna; úplné podklady úřad obdržel 2. června 2026.</p>

  <div class="callout"><strong>Co zatím veřejný dokument neříká</strong><p>Stanovisko neuvádí konečnou cenu projektu, instalovaný výkon nové elektrárny, stavebního dodavatele ani potvrzený termín zahájení. Ivo Frýdl je v dokumentu označen jako žadatel a projektant; jméno investora není výslovně uvedeno.</p></div>

  <h2>Souhlas není stavební povolení</h2>
  <p>Jednotné environmentální stanovisko není samostatným rozhodnutím o povolení stavby. Je závazným podkladem pro navazující povolovací řízení. Platí pět let a na žádost může být prodlouženo.</p>
  <p>Město Klášterec nad Ohří obdrželo dokument na vědomí jako obec, jejíž území může být záměrem dotčeno. Naše Kadaň bude sledovat navazující stavební řízení, zveřejnění výkonu elektrárny, investora, ceny a termínu realizace.</p>

  <section class="source-list"><h2>Zdroje</h2><ul><li><a href="{DETAIL_URL}" target="_blank" rel="noopener noreferrer">Úřední deska města Kadaň – MUKK/32659/2026</a>, vyvěšeno 30. července 2026.</li><li><a href="{PDF_URL}" target="_blank" rel="noopener noreferrer">Jednotné environmentální stanovisko MVE Hradiště</a>, vydáno 27. července 2026.</li></ul><p><small>Primární dokument ověřen 31. července 2026.</small></p></section>
</article>
<aside class="sticky"><div class="sidebox"><h3>Rychlý přehled</h3><ul><li>Nová MVE na Hradišťském potoce</li><li>Tlakový přivaděč přibližně 520 metrů</li><li>Spád přibližně 20 metrů</li><li>Rybí přechod a nový odběrný objekt</li><li>Minimální průtok 34 litrů za sekundu</li><li>Nejméně roční zkušební provoz</li><li>Zatím bez konečného stavebního povolení</li></ul></div><div data-promos data-context="sidebar"></div></aside>
</main>
<footer class="site-footer" data-site-footer="v1"><div class="wrap footer-grid"><div class="footer-brand"><a class="logo" href="/"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a><p>Nezávislé informace, události a příběhy města.</p></div><div class="footer-column"><strong>Obsah webu</strong><a href="/">Úvod</a><a href="/clanky/">Naše články</a><a href="/#akce">Akce</a><a href="/pruvodce/">Průvodce</a><a href="/prehled-zdroju/">Přehled zdrojů</a></div><div class="footer-column"><strong>Praktické a kontakt</strong><a href="/prakticke/">Praktická Kadaň</a><a href="/doprava/">Doprava</a><a href="/organizace/">Organizace</a><a href="/zapojte-se/">Zapojte se</a><a href="/inzerce/"><b>Inzerce a ceník</b></a><a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a></div></div><div class="footer-legal"><span>© 2026 Naše Kadaň</span><a href="/o-webu/">O webu</a><a href="/inzerce/">Inzerce</a><a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a><a href="/navstevnost/">Návštěvnost</a><a href="/o-webu/#provozovatel">Provozovatel</a><a href="mailto:info@nasekadan.cz">Kontakt</a></div></footer>
<script src="/site.js" defer></script><script src="/reklamy.js"></script><script src="/reklamy-oprava-obrazku.js"></script><script src="/obsah-doplnky.js"></script><script src="/horko-feed.js"></script><script src="/analytics.js" defer></script>
</body></html>'''


def run(script: str) -> None:
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)


def main() -> int:
    make_social()
    ARTICLE.parent.mkdir(parents=True, exist_ok=True)
    ARTICLE.write_text(article_html(), encoding="utf-8", newline="\n")

    run("scripts/enforce_current_article_order.py")
    run("scripts/finalize_launch.py")
    run("scripts/enforce_current_article_order.py")

    html = ARTICLE.read_text(encoding="utf-8")
    required = [TITLE, IMAGE, PUBLISHED, "MUKK/32659/2026", "520 metrů", "0,034"]
    assert all(item in html for item in required)

    href = f"/clanky/{SLUG}.html"
    absolute = "https://nasekadan.cz" + href
    assert href in (ROOT / "index.html").read_text(encoding="utf-8")
    assert href in (ROOT / "clanky" / "index.html").read_text(encoding="utf-8")
    assert absolute in (ROOT / "rss.xml").read_text(encoding="utf-8")
    assert absolute in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert absolute in (ROOT / "news-sitemap.xml").read_text(encoding="utf-8")
    print("Článek MVE Hradiště, sociální obrázek a všechny veřejné přehledy jsou připravené.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
