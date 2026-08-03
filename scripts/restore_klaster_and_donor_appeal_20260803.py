#!/usr/bin/env python3
"""Restore the monastery article on the homepage and add a donor appeal."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
DONOR = ROOT / "clanky" / "zaregistrovala-se-v-kadani-darovala-krvetvorne-bunky-2026.html"
PUBLISHER = ROOT / "scripts" / "publish_darci_krvetvornych_bunek_20260803.py"
KLASTER_SLUG = "alzbetinsky-klaster-kadan-pacienti-lecebna-1966"
KLASTER_REL = f"/clanky/{KLASTER_SLUG}.html"

KLASTER_CARD = f'''    <article class="article-card hospital" data-auto-article="{KLASTER_SLUG}">
      <div class="visual" style="background:linear-gradient(135deg,#211c32,#594c70 58%,#9d6a22)"><strong>Kam odešli poslední pacienti? Skrytý příběh kadaňského kláštera</strong></div>
      <div class="article-body"><span class="meta">3. 8. 2026 · 04:00 · HISTORIE · VELKÁ REŠERŠE</span><h3>Kam odešli poslední pacienti? Skrytý příběh kadaňského kláštera</h3><p>Staré prameny odhalují nemocnici, lékárnu, sirotčinec i plicní léčebnu v kadaňském klášteře. Proč skončila a kam odešli poslední pacienti?</p><a class="read-more" href="{KLASTER_REL}">Přečíst článek →</a></div>
    </article>'''

APPEAL = '''<div class="appeal-box" data-donor-appeal="1">
<p class="appeal-kicker">MOŽNÁ PRÁVĚ VY BUDETE PRO NĚKOHO POTŘEBNÁ SHODA</p>
<h2>Dejte někomu šanci na další život</h2>
<p>Registrace zabere jen několik minut. Většina zapsaných lidí nikdy k odběru vyzvána nebude. Pro jednoho konkrétního pacienta ale může právě vaše shoda znamenat naději na léčbu, další narozeniny a návrat domů k rodině.</p>
<p><strong>Splňujete podmínky? Přijďte se v Kadani zaregistrovat. Možná se nikdy nikdo neozve. Možná ale jednou zazvoní telefon a vy budete člověkem, který může pomoci zachránit lidský život.</strong></p>
<a class="appeal-button" href="#registrace-v-kadani">Kde a kdy se zaregistrovat →</a>
</div>'''

APPEAL_CSS = (
    ".appeal-box{background:linear-gradient(135deg,#731322,#b51f36);color:#fff;"
    "border-radius:22px;padding:30px 28px;margin:40px 0;box-shadow:0 18px 42px #62101f38}"
    ".appeal-box h2{color:#fff;margin:5px 0 14px}.appeal-box p{color:#fff;margin:0 0 16px}"
    ".appeal-kicker{font-size:12px!important;font-weight:900;letter-spacing:.1em;text-transform:uppercase;opacity:.88}"
    ".appeal-button{display:inline-flex;background:#fff;color:#7a1523!important;text-decoration:none!important;"
    "font-weight:900;padding:13px 18px;border-radius:12px;margin-top:4px}"
)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def patch_home() -> None:
    text = HOME.read_text(encoding="utf-8")
    card_pattern = re.compile(
        rf"\s*<article\b[^>]*data-auto-article=[\"']{re.escape(KLASTER_SLUG)}[\"'][^>]*>.*?</article>\s*",
        re.IGNORECASE | re.DOTALL,
    )
    text = card_pattern.sub("\n", text)
    marker = '<div class="article-list">'
    if marker not in text:
        raise RuntimeError("Na titulní stránce chybí seznam článků.")
    text = text.replace(marker, marker + "\n" + KLASTER_CARD, 1)
    if text.count(f'data-auto-article="{KLASTER_SLUG}"') != 1:
        raise RuntimeError("Karta kláštera nebyla vložena právě jednou.")
    write(HOME, text)


def patch_donor() -> None:
    text = DONOR.read_text(encoding="utf-8")

    if ".appeal-box{" not in text:
        if ".source-list{" in text:
            text = text.replace(".source-list{", APPEAL_CSS + ".source-list{", 1)
        else:
            text = text.replace("</style>", APPEAL_CSS + "\n</style>", 1)

    text = text.replace(
        '<div class="service-box"><h2>Registrace přímo v Kadani</h2>',
        '<div class="service-box" id="registrace-v-kadani"><h2>Registrace přímo v Kadani</h2>',
        1,
    )

    text = re.sub(
        r"\s*<div class=[\"']appeal-box[\"'][^>]*data-donor-appeal=[\"']1[\"'][^>]*>.*?</div>\s*",
        "\n",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    source_heading = re.search(r"<h2\b[^>]*>[^<]*Zdroje[^<]*</h2>", text, flags=re.IGNORECASE)
    if source_heading:
        text = text[: source_heading.start()] + APPEAL + "\n" + text[source_heading.start() :]
    elif "</article>" in text:
        text = text.replace("</article>", APPEAL + "\n</article>", 1)
    else:
        raise RuntimeError("V článku nebylo nalezeno místo pro výzvu.")

    if text.count('data-donor-appeal="1"') != 1:
        raise RuntimeError("Výzva dárcům nebyla vložena právě jednou.")
    if "pomoci zachránit lidský život" not in text:
        raise RuntimeError("Ve výzvě chybí závěrečná věta.")
    write(DONOR, text)


def patch_publisher() -> None:
    text = PUBLISHER.read_text(encoding="utf-8")
    marker = "restore_klaster_and_donor_appeal_20260803.py"
    if marker in text:
        return
    needle = "    update_home()\n"
    command = (
        "    subprocess.run([\"python3\", str(ROOT / \"scripts\" / "
        "\"restore_klaster_and_donor_appeal_20260803.py\")], cwd=ROOT, check=True)\n"
    )
    if needle not in text:
        raise RuntimeError("V publikačním skriptu nebylo nalezeno update_home().")
    text = text.replace(needle, needle + command, 1)
    write(PUBLISHER, text)


def main() -> int:
    patch_home()
    patch_donor()
    patch_publisher()
    print("Klášter vrácen na titulku a výzva dárcům doplněna.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
