#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
BASE_PATH = ROOT / "scripts" / "publish_zimni_stadion_ochlazeni_kadan_20260803.py"
spec = importlib.util.spec_from_file_location("stadium_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Nelze načíst původní publikační modul.")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

TITLE = "Kadaň se přidala ke Klášterci. Zimní stadion otevřela lidem k ochlazení"
DESC = (
    "Kadaň v horkých dnech zpřístupnila zimní stadion veřejnosti každý den od 8 do 18 hodin. "
    "Vchod je od koupaliště, občerstvení nabízí místní restaurace."
)
PUBLISHED = "2026-08-03T22:05:00+02:00"
MODIFIED = "2026-08-04T13:04:00+02:00"
MODIFIED_HUMAN = "4. SRPNA 2026 · 13:04"
SLUG = base.SLUG
ARTICLE = base.ARTICLE
REL = base.REL
URL = base.URL
SOCIAL_REL = f"/social/{SLUG}-aktualizace-20260804.png"
SOCIAL = ROOT / SOCIAL_REL.lstrip("/")
SOCIAL_URL = f"https://nasekadan.cz{SOCIAL_REL}"

base.TITLE = TITLE
base.DESC = DESC
base.PUBLISHED = PUBLISHED
base.SOCIAL_REL = SOCIAL_REL
base.SOCIAL = SOCIAL
base.SOCIAL_URL = SOCIAL_URL


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_social() -> None:
    from PIL import Image, ImageDraw, ImageFont

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), "#08253a")
    draw = ImageDraw.Draw(image)
    for y in range(630):
        ratio = y / 629
        draw.line(
            (0, y, 1200, y),
            fill=(int(8 + 20 * ratio), int(37 + 70 * ratio), int(58 + 90 * ratio)),
        )

    # Vlastní redakční ilustrace stadionu a chladného prostoru.
    draw.rounded_rectangle((690, 62, 1145, 568), radius=36, fill="#e9f9ff", outline="#ffffff", width=7)
    draw.rounded_rectangle((725, 132, 1110, 492), radius=150, fill="#fbfeff", outline="#71bddf", width=11)
    draw.line((918, 138, 918, 488), fill="#b32632", width=9)
    draw.arc((800, 208, 1036, 444), 180, 360, fill="#b32632", width=13)
    draw.rounded_rectangle((813, 286, 1018, 424), radius=17, outline="#c72e3b", width=11)
    for x in range(829, 1012, 28):
        draw.line((x, 294, x, 417), fill="#c72e3b", width=2)
    for y in range(302, 418, 24):
        draw.line((820, y, 1012, y), fill="#c72e3b", width=2)
    draw.ellipse((760, 448, 822, 478), fill="#121a21")

    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = ImageFont.truetype(bold_path, 57)
    medium = ImageFont.truetype(bold_path, 31)
    small = ImageFont.truetype(regular_path, 25)
    tiny = ImageFont.truetype(bold_path, 21)

    draw.rounded_rectangle((58, 48, 382, 104), radius=27, fill="#a9232b")
    draw.text((83, 66), "NAŠE KADAŇ · AKTUALIZACE", font=tiny, fill="white")
    for index, line in enumerate(("Kadaň otevřela", "zimák k ochlazení")):
        draw.text((61, 145 + index * 73), line, font=bold, fill="white")
    draw.text((64, 334), "DENNĚ 8:00–18:00", font=medium, fill="#ffe39c")
    draw.text((64, 386), "Vstup od koupaliště", font=medium, fill="#e8f8ff")
    draw.text((64, 435), "Posezení, chládek a možnost sledovat trénink", font=small, fill="#e8f8ff")
    draw.text((64, 477), "krasobruslařek. Občerstvení v restauraci.", font=small, fill="#e8f8ff")
    draw.text((64, 570), "NASEKADAN.CZ", font=tiny, fill="white")
    image.save(SOCIAL, format="PNG", optimize=True)


def article_page() -> str:
    html = base.article_page()
    html = re.sub(
        r'<meta property="article:modified_time" content="[^"]+">',
        f'<meta property="article:modified_time" content="{MODIFIED}">',
        html,
        count=1,
    )
    html = html.replace(f'"dateModified":"{PUBLISHED}"', f'"dateModified":"{MODIFIED}"', 1)
    html = re.sub(
        r'<p class="tag">.*?</p>',
        f'<p class="tag">KADAŇ · KLÁŠTEREC NAD OHŘÍ · VEDRO · PRAKTICKÉ INFORMACE · AKTUALIZOVÁNO {MODIFIED_HUMAN}</p>',
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'<img class="hero-image"[^>]*>',
        f'<img class="hero-image" src="{SOCIAL_REL}" width="1200" height="630" alt="Redakční grafika k otevření kadaňského zimního stadionu veřejnosti během veder">',
        html,
        count=1,
    )

    body = '''
<p><strong>Aktualizace 4. srpna ve 13:04:</strong> Otázka položená v původním článku už má odpověď. Město Kadaň oznámilo, že v horkých dnech otevírá zimní stadion lidem, kteří si potřebují odpočinout od rozpálených ulic a přehřátých bytů.</p>
<p>Veřejnost může přicházet <strong>každý den od 8:00 do 18:00</strong>. Město doporučuje vzít si knížku nebo noviny a využít chladnější prostředí stadionu k posezení. Nejde o veřejné bruslení ani o vstup na led.</p>
<div class="fact-grid"><div class="fact"><strong>8:00–18:00</strong><span>čas, kdy je stadion v horkých dnech otevřený veřejnosti</span></div><div class="fact"><strong>každý den</strong><span>četnost uvedená v oznámení města</span></div><div class="fact"><strong>od koupaliště</strong><span>připravený vchod naproti vstupu do restaurace</span></div></div>
<div class="clarity"><strong>Kudy dovnitř</strong><p>Vchod pro návštěvníky je připravený ze strany od koupaliště, přímo naproti vstupu do místní restaurace. Nejde tedy o běžný hlavní vstup používaný při zápasech.</p></div>
<h2>Posezení, krasobruslení i občerstvení</h2>
<p>Na stadionu právě probíhá soustředění krasobruslařek. Návštěvníci tak mohou mít při troše štěstí možnost sledovat jejich trénink. Místní restaurace zůstává v provozu a podle města se v ní lze během návštěvy občerstvit nebo si koupit nápoj.</p>
<div class="proposal"><h2>Praktické informace</h2><ul><li>zimní stadion: U Stadionu 2028, Kadaň,</li><li>otevřeno k ochlazení denně od 8:00 do 18:00,</li><li>vstup ze strany od koupaliště, naproti restauraci,</li><li>nejde o veřejné bruslení, ale o možnost posedět v chladu,</li><li>kontakt na stadion: 777 805 290.</li></ul></div>
<h2>Kadaň navázala na sousední Klášterec</h2>
<p>Původní článek vyšel v neděli večer poté, co podobnou možnost nabídl Klášterec nad Ohří. Upozorňoval, že kadaňský stadion už má od srpna sezonní provoz, ale město tehdy veřejný vstup pouze za účelem ochlazení ještě neoznámilo. O několik hodin později se situace změnila a Kadaň stejnou službu spustila.</p>
<p>Klášterecký příklad tak nezůstal pouze námětem. V obou sousedních městech mohou lidé během veder využít chladnější prostředí zimního stadionu, aniž by museli bruslit.</p>
<h2>Co oznámení neupřesňuje</h2>
<p>Město ve zveřejněném příspěvku nestanovilo konečné datum nabídky ani výslovně neuvedlo případné vstupné. Službu popisuje jako opatření pro současné horké dny. Při změně počasí nebo provozu stadionu se proto podmínky mohou změnit.</p>
'''.strip()

    sources = '''<div class="sources"><h2>Zdroje a upřesnění</h2><ul><li>Město Kadaň: oficiální oznámení o zpřístupnění zimního stadionu zveřejněné 4. 8. 2026 na facebookové stránce města.</li><li><a href="https://www.sportkadan.cz/arealy/zimni-stadion" rel="noopener">Sportovní zařízení Kadaň: Zimní stadion – adresa, kontakt, sezona a provozní doba</a>.</li><li><a href="https://www.klasterec.cz/kontakty/tiskove-zpravy/v-extremnich-vedrech-se-muzete-zchladit-na-zimnim-stadione-201cs.html" rel="noopener">Město Klášterec nad Ohří: archivní nabídka ochlazení na stadionu</a>.</li></ul><p>Článek byl 4. srpna 2026 zásadně aktualizován. Původní podnět se změnil v potvrzenou praktickou informaci.</p></div>'''

    pattern = re.compile(r'(<img class="hero-image"[^>]*>\s*).*?(<div class="sources">.*?</div>)(</article>)', re.S)
    match = pattern.search(html)
    if not match:
        raise RuntimeError("Nelze najít obsahový blok původního článku.")
    html = html[:match.start()] + match.group(1) + body + "\n" + sources + match.group(3) + html[match.end():]

    aside = '''<aside class="sticky"><div class="sidebox"><h3>Co nyní platí</h3><ul><li>otevřeno denně 8:00–18:00,</li><li>vchod ze strany od koupaliště,</li><li>posezení v chladnějším prostředí,</li><li>občerstvení v místní restauraci.</li></ul></div><div class="sidebox"><h3>Adresa stadionu</h3><p><strong>U Stadionu 2028, Kadaň</strong><br>kontakt stadionu: 777 805 290</p></div><div data-promos data-context="sidebar"></div></aside>'''
    html, count = re.subn(r'<aside class="sticky">.*?</aside>', aside, html, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Nelze aktualizovat postranní praktický přehled.")
    return html


def update_rss() -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    build_date = format_datetime(datetime.fromisoformat(MODIFIED))
    text = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{build_date}</lastBuildDate>', text, count=1, flags=re.S)
    pattern = re.compile(r'<item>.*?<link>' + re.escape(URL) + r'</link>.*?</item>', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Článek chybí v RSS.")
    item = match.group(0)
    item = re.sub(r'<title>.*?</title>', f'<title>{escape(TITLE)}</title>', item, count=1, flags=re.S)
    item = re.sub(r'<description>.*?</description>', f'<description><![CDATA[{DESC}]]></description>', item, count=1, flags=re.S)
    item = re.sub(r'<szn:url>.*?</szn:url>', f'<szn:url>{SOCIAL_URL}</szn:url>', item, count=1, flags=re.S)
    text = text[:match.start()] + item + text[match.end():]
    write(path, text)


def update_sitemaps() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    pattern = re.compile(r'<url>\s*<loc>' + re.escape(URL) + r'</loc>.*?</url>', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Článek chybí v hlavní sitemapě.")
    node = match.group(0)
    if '<lastmod>' in node:
        node = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{MODIFIED}</lastmod>', node, count=1, flags=re.S)
    else:
        node = node.replace(f'<loc>{URL}</loc>', f'<loc>{URL}</loc><lastmod>{MODIFIED}</lastmod>', 1)
    text = text[:match.start()] + node + text[match.end():]
    write(sitemap, text)

    news = ROOT / "news-sitemap.xml"
    text = news.read_text(encoding="utf-8")
    pattern = re.compile(r'<url>\s*<loc>' + re.escape(URL) + r'</loc>.*?</url>', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Článek chybí v news sitemapě.")
    node = match.group(0)
    node = re.sub(r'<news:title>.*?</news:title>', f'<news:title>{escape(TITLE)}</news:title>', node, count=1, flags=re.S)
    node = node.replace("Klášterec otevřel zimní stadion lidem před vedrem. Mohla by se přidat i Kadaň?", TITLE)
    text = text[:match.start()] + node + text[match.end():]
    write(news, text)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'- \[[^\]]+\]\(' + re.escape(URL) + r'\)\n(?:  .*\n)?')
    replacement = f'- [{TITLE}]({URL})\n  {DESC}\n'
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("Článek chybí v llms.txt.")
    write(path, text)


def update_registry() -> None:
    path = ROOT / "data" / "published-content-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    target = None
    for article in data.get("articles", []):
        if isinstance(article, dict) and article.get("url") == URL:
            target = article
            break
    if target is None:
        raise RuntimeError("Článek chybí v kanonickém registru.")
    target.update({
        "title": TITLE,
        "h1": TITLE,
        "published_at": PUBLISHED,
        "modified_at": MODIFIED,
        "persons": [],
        "organizations": ["Město Kadaň", "Sportovní zařízení Kadaň", "Město Klášterec nad Ohří"],
        "places": ["Kadaň", "Klášterec nad Ohří", "Zimní stadion Kadaň"],
        "cases": ["Ochlazení veřejnosti na kadaňském zimním stadionu během veder"],
        "topics": ["Vedro", "Veřejná služba", "Zimní stadion", "Praktické informace"],
        "status": {"homepage": True, "archive": True, "rss": True, "sitemap": True, "news_sitemap": True},
        "publication_status": "published",
    })
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    validation = data.setdefault("validation", {})
    validation["last_registry_refresh"] = {
        "reason": "Město Kadaň zpřístupnilo zimní stadion veřejnosti k ochlazení; aktualizace existujícího článku bez nové URL",
        "classification": "existing_article_significant_update",
        "updated_url": URL,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    make_social()
    write(ARTICLE, article_page())
    update_rss()
    update_sitemaps()
    update_llms()
    update_registry()

    subprocess.run(["python3", str(ROOT / "scripts" / "enforce_article_visibility.py")], cwd=ROOT, check=True)
    weather_script = ROOT / "scripts" / "ensure_weather_loader.py"
    if weather_script.exists():
        subprocess.run(["python3", str(weather_script)], cwd=ROOT, check=True)

    article = ARTICLE.read_text(encoding="utf-8")
    required_phrases = [
        f'<h1>{TITLE}</h1>',
        "8:00–18:00",
        "ze strany od koupaliště",
        "soustředění krasobruslařek",
        "případné vstupné",
    ]
    for phrase in required_phrases:
        if phrase not in article:
            raise RuntimeError(f"V aktualizovaném článku chybí: {phrase}")
    if "Mohla by se přidat i Kadaň?" in article or 'data-poll-id="ochlazeni-zimni-stadion-kadan-2026"' in article:
        raise RuntimeError("V článku zůstala překonaná otázka nebo anketa.")
    for path in (ROOT / "index.html", ROOT / "clanky/index.html", ROOT / "rss.xml", ROOT / "sitemap.xml", ROOT / "news-sitemap.xml", ROOT / "data/published-content-index.json"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if REL not in text and URL not in text:
            raise RuntimeError(f"Aktualizovaný článek chybí v {path}.")
    if '/pocasi.js' not in (ROOT / "index.html").read_text(encoding="utf-8"):
        raise RuntimeError("Aktualizace by odstranila loader počasí.")
    print(f"Aktualizován článek: {URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
