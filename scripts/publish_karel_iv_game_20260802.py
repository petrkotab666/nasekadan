#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'hry/prijezd-karla-iv/index.html'
GAME_JS = ROOT / 'hry/prijezd-karla-iv/game.js'
GAME_CSS = ROOT / 'hry/prijezd-karla-iv/game.css'
GAMES_INDEX = ROOT / 'hry/index.html'
SOCIAL = ROOT / 'social/hra-prijezd-karla-iv-1367.png'
HOME = ROOT / 'index.html'
SITEMAP = ROOT / 'sitemap.xml'
KZK = ROOT / 'clanky/kulturni-zarizeni-kadan.html'

GAME_URL = 'https://nasekadan.cz/hry/prijezd-karla-iv/'
GAMES_URL = 'https://nasekadan.cz/hry/'


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def font(size: int, bold: bool = False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/dejavu/DejaVuSans.ttf',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def build_social_card() -> None:
    width, height = 1200, 630
    image = Image.new('RGB', (width, height), (15, 38, 49))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(1, height - 1)
        draw.line((0, y, width, y), fill=(
            int(15 + 84 * ratio),
            int(38 + 9 * ratio),
            int(49 + 2 * ratio),
        ))

    draw.ellipse((780, -180, 1320, 360), fill=(127, 29, 37))
    draw.ellipse((880, -80, 1200, 240), fill=(201, 164, 90))
    draw.rectangle((0, 0, 18, height), fill=(201, 164, 90))

    # Silueta města.
    skyline = [
        (0, 520, 1200, 630),
        (40, 470, 125, 630), (70, 415, 95, 470),
        (145, 440, 240, 630), (180, 385, 208, 440),
        (275, 490, 360, 630), (305, 440, 335, 490),
        (405, 400, 505, 630), (440, 330, 470, 400),
        (550, 470, 650, 630), (590, 420, 620, 470),
        (700, 445, 790, 630), (735, 395, 760, 445),
        (835, 480, 930, 630), (870, 430, 900, 480),
        (975, 420, 1080, 630), (1015, 350, 1040, 420),
        (1100, 475, 1200, 630),
    ]
    for box in skyline:
        draw.rectangle(box, fill=(7, 23, 31))
    draw.polygon([(405, 400), (455, 340), (505, 400)], fill=(7, 23, 31))
    draw.polygon([(975, 420), (1027, 350), (1080, 420)], fill=(7, 23, 31))

    draw.text((64, 50), 'NAŠE KADAŇ · ONLINE HRA', font=font(28, True), fill='white')
    draw.rounded_rectangle((64, 108, 300, 154), radius=12, fill=(127, 29, 37))
    draw.text((84, 118), 'KADAŇ 1367', font=font(22, True), fill='white')
    draw.text((62, 190), 'PŘÍJEZD', font=font(78, True), fill='white')
    draw.text((62, 274), 'CÍSAŘE', font=font(78, True), fill=(244, 222, 170))
    draw.text((66, 375), 'Dokážeš připravit město na návštěvu Karla IV.?', font=font(27, False), fill=(232, 239, 242))
    draw.rounded_rectangle((66, 442, 690, 496), radius=16, fill='white')
    draw.text((88, 455), '8 KAPITOL · 3 OBTÍŽNOSTI · HISTORICKÉ STOPY', font=font(19, True), fill=(20, 40, 50))

    draw.ellipse((930, 65, 1138, 273), outline='white', width=5)
    draw.ellipse((945, 80, 1123, 258), outline=(201, 164, 90), width=4)
    draw.text((975, 112), '1367', font=font(54, True), fill='white')
    draw.text((983, 185), 'KADAŇ', font=font(24, True), fill=(244, 222, 170))

    SOCIAL.parent.mkdir(parents=True, exist_ok=True)
    image.save(SOCIAL, 'PNG', optimize=True)


def patch_game_js() -> None:
    text = GAME_JS.read_text(encoding='utf-8')
    marker = "    elements.effectList.innerHTML = '';\n"
    cleanup = "    elements.consequence.querySelectorAll('.consequence__event').forEach((node) => node.remove());\n"
    if cleanup not in text:
        if marker not in text:
            raise SystemExit('V game.js chybí místo pro vyčištění náhodné události.')
        text = text.replace(marker, marker + cleanup, 1)
    write(GAME_JS, text)


def update_sitemap() -> None:
    text = SITEMAP.read_text(encoding='utf-8')
    entries = [
        f'  <url><loc>{GAMES_URL}</loc><lastmod>2026-08-02</lastmod></url>\n',
        f'  <url><loc>{GAME_URL}</loc><lastmod>2026-08-02</lastmod></url>\n',
    ]
    for entry, url in zip(entries, (GAMES_URL, GAME_URL)):
        if f'<loc>{url}</loc>' not in text:
            text = text.replace('</urlset>', entry + '</urlset>', 1)
    write(SITEMAP, text)


def update_home() -> None:
    text = HOME.read_text(encoding='utf-8')

    if 'data-karel-game-promo-style' not in text:
        style = '''\n  <style data-karel-game-promo-style>\n    .karel-game-promo{margin:44px auto 76px;padding:34px;border-radius:25px;display:grid;grid-template-columns:minmax(0,1fr) 310px;gap:30px;align-items:center;color:#fff;background:radial-gradient(circle at 84% 12%,rgba(255,221,148,.28),transparent 26%),linear-gradient(145deg,#122c38,#315d70 58%,#7f1d25);box-shadow:0 22px 60px rgba(18,38,48,.18)}\n    .karel-game-promo .tag{color:#f2d89a}.karel-game-promo h2{margin:.18em 0;font:850 clamp(34px,4vw,53px)/1.04 Georgia,serif}.karel-game-promo p{max-width:720px;color:#e7eef1;font-size:18px}.karel-game-promo .btn{background:#fff;color:#172e39}.karel-game-seal{width:230px;height:230px;margin:auto;border:4px double rgba(255,255,255,.82);border-radius:50%;display:grid;place-content:center;text-align:center;background:rgba(127,29,37,.52);box-shadow:inset 0 0 0 12px rgba(201,164,90,.22)}.karel-game-seal strong{font:900 56px/1 Georgia,serif}.karel-game-seal span{margin-top:8px;font-weight:900;letter-spacing:.16em}\n    @media(max-width:850px){.karel-game-promo{grid-template-columns:1fr}.karel-game-seal{display:none}}\n  </style>\n'''
        text = text.replace('</head>', style + '</head>', 1)

    promo = '''\n  <section class="wrap karel-game-promo" data-karel-game-promo>\n    <div><p class="tag">NOVINKA · ONLINE HRA</p><h2>Příjezd císaře: Kadaň 1367</h2><p>Připravte královské město na návštěvu Karla IV. Rozhodujte o trhu, zásobách, branách, požáru i městské spravedlnosti a zjistěte, jak byste obstáli jako správce Kadaně.</p><a class="btn" href="/hry/prijezd-karla-iv/">Spustit hru →</a></div>\n    <div class="karel-game-seal" aria-hidden="true"><strong>1367</strong><span>KADAŇ</span></div>\n  </section>\n'''
    if 'data-karel-game-promo' not in text:
        text = text.replace('</main>', promo + '</main>', 1)

    text = text.replace('<a href="/clanky/">Články</a><a href="/#akce">Akce</a>', '<a href="/clanky/">Články</a><a href="/hry/">Hry</a><a href="/#akce">Akce</a>', 1)
    write(HOME, text)


def update_kzk_article() -> None:
    text = KZK.read_text(encoding='utf-8')
    text = text.replace('<a href="/clanky/">Články</a><a href="/#akce">Akce</a>', '<a href="/clanky/">Články</a><a href="/hry/">Hry</a><a href="/#akce">Akce</a>', 1)

    callout = '''\n    <div class="cta-panel" data-karel-game-link>\n      <p class="tag">NOVÁ ONLINE HRA</p>\n      <h2>Dokázali byste připravit Kadaň na příjezd Karla IV.?</h2>\n      <p>V rozhodovací hře spravujete pokladnu, zásoby, pořádek, spokojenost obyvatel a přízeň císaře. Každá volba odemyká krátké historické vysvětlení.</p>\n      <div class="cta-buttons"><a class="cta-button" href="/hry/prijezd-karla-iv/">Spustit hru Příjezd císaře →</a></div>\n    </div>\n'''
    if 'data-karel-game-link' not in text:
        marker = '<div class="source-list"'
        if marker not in text:
            raise SystemExit('V článku KZK chybí seznam zdrojů pro vložení hry.')
        text = text.replace(marker, callout + '\n    ' + marker, 1)
    write(KZK, text)


def validate() -> None:
    for path in (GAME, GAME_JS, GAME_CSS, GAMES_INDEX):
        if not path.is_file() or path.stat().st_size < 500:
            raise SystemExit(f'Chybí nebo je příliš malý soubor: {path}')
    game = GAME.read_text(encoding='utf-8')
    js = GAME_JS.read_text(encoding='utf-8')
    if 'Příjezd císaře' not in game or 'SCENES = [' not in js:
        raise SystemExit('Herní soubory neobsahují očekávaný obsah.')
    if js.count("chapter:") != 8:
        raise SystemExit('Hra musí mít přesně osm kapitol.')


def main() -> None:
    validate()
    patch_game_js()
    build_social_card()
    update_sitemap()
    update_home()
    update_kzk_article()
    print('Hra Příjezd císaře byla připravena k nasazení.')


if __name__ == '__main__':
    main()
