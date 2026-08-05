#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "reklamy.js"
ASSETS = ROOT / "assets" / "reklamy"
URL = "https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=aface625&desturl=https%3A%2F%2Fwww.vodafone.cz%2Finternet%2F"
TITLE = "Vodafone: až 53 % sleva na pevný internet"
TEXT = "Dočasná sleva na prvních šest měsíců u vybraných tarifů pevného internetu. Aktivace nabídky do 31. srpna 2026; dostupnost a podmínky se ověřují podle adresy."


def client_redirect(body: bytes) -> str:
    text = body[:30000].decode("utf-8", "replace")
    for pattern in (
        r'<meta[^>]+http-equiv=["\']?refresh["\']?[^>]+content=["\'][^"\']*url=([^"\'> ]+)',
        r'(?:window\.)?location(?:\.href)?\s*=\s*["\']([^"\']+)',
        r'location\.replace\(\s*["\']([^"\']+)',
    ):
        match = re.search(pattern, text, re.I)
        if match and match.group(1).startswith(("http://", "https://")):
            return match.group(1)
    return ""


def validate_url() -> None:
    headers = {"User-Agent": "Mozilla/5.0 Chrome/151 VodafonePromotionAudit/1.0", "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Cache-Control": "no-cache"}
    response = requests.get(URL, headers=headers, timeout=(10, 30), allow_redirects=True)
    body = response.content
    if (urlparse(response.url).hostname or "").lower() in {"ehub.cz", "www.ehub.cz"}:
        next_url = client_redirect(body)
        if next_url:
            response = requests.get(next_url, headers=headers, timeout=(10, 30), allow_redirects=True)
            body = response.content
    host = (urlparse(response.url).hostname or "").lower()
    if response.status_code >= 400 or not body.strip() or host in {"ehub.cz", "www.ehub.cz"}:
        raise SystemExit(f"Vodafone affiliate cíl neprošel: HTTP {response.status_code}, {response.url}")
    if host not in {"vodafone.cz", "www.vodafone.cz"}:
        raise SystemExit(f"Vodafone affiliate cíl vede na neočekávaný host: {host}")
    print(f"Vodafone affiliate OK: {response.url}")


def svg(width: int, height: int, fmt: str) -> str:
    wide = fmt == "wide"
    square = fmt == "square"
    title_size = 61 if wide else 50 if square else 31
    sub_size = 23 if wide else 22 if square else 16
    x = 72 if wide else width / 2
    anchor = "start" if wide else "middle"
    title_y = 158 if wide else 198 if square else 112
    title_gap = title_size * 1.04
    sub_y = title_y + title_gap * 2 + (18 if wide else 28)
    icon_size = 210 if wide else 220 if square else 150
    icon_x = width - icon_size - 78 if wide else (width - icon_size) / 2
    icon_y = 80 if wide else height * .55
    button_w = 280 if wide else width * .72
    button_h = 54 if wide else 52
    button_x = 72 if wide else (width - button_w) / 2
    button_y = height - button_h - (40 if wide else 48)
    subtitles = ["Dočasná sleva na prvních 6 měsíců", "Aktivace do 31. srpna 2026"]
    subtitle_svg = "".join(f'<text x="{x}" y="{sub_y+i*sub_size*1.35}" text-anchor="{anchor}" fill="#fee2e2" font-size="{sub_size}" font-weight="650">{html.escape(line)}</text>' for i, line in enumerate(subtitles))
    signal = f'''<g transform="translate({icon_x} {icon_y})" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round"><circle cx="{icon_size*.5}" cy="{icon_size*.77}" r="{icon_size*.055}" fill="#ffffff"/><path d="M{icon_size*.34} {icon_size*.62}q{icon_size*.16}-{icon_size*.17} {icon_size*.32} 0"/><path d="M{icon_size*.23} {icon_size*.50}q{icon_size*.27}-{icon_size*.29} {icon_size*.54} 0"/><path d="M{icon_size*.12} {icon_size*.38}q{icon_size*.38}-{icon_size*.41} {icon_size*.76} 0"/></g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(TITLE)}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#450a0a"/><stop offset="1" stop-color="#e60000"/></linearGradient><radialGradient id="r"><stop offset="0" stop-color="#fff" stop-opacity=".24"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs><rect width="{width}" height="{height}" rx="28" fill="url(#g)"/><circle cx="{width*.87 if wide else width*.5}" cy="{height*.52 if wide else height*.70}" r="{height*.66 if wide else width*.58}" fill="url(#r)"/><rect x="{72 if wide else width*.08}" y="{38 if wide else 42}" width="{355 if wide else width*.84}" height="42" rx="21" fill="#fff" fill-opacity=".17" stroke="#fff" stroke-opacity=".55"/><text x="{90 if wide else width/2}" y="{66 if wide else 70}" text-anchor="{'start' if wide else 'middle'}" fill="#fff" font-size="17" font-weight="850" letter-spacing="1.1">VODAFONE · DO 31. SRPNA</text><text x="{x}" y="{title_y}" text-anchor="{anchor}" fill="#fff" font-size="{title_size}" font-weight="900">AŽ 53 % SLEVA</text><text x="{x}" y="{title_y+title_gap}" text-anchor="{anchor}" fill="#fff" font-size="{title_size}" font-weight="900">NA PEVNÝ INTERNET</text>{subtitle_svg}{signal}<rect x="{button_x}" y="{button_y}" width="{button_w}" height="{button_h}" rx="{button_h/2}" fill="#fff"/><text x="{button_x+button_w/2}" y="{button_y+button_h*.67}" text-anchor="middle" fill="#991b1b" font-size="{19 if wide else 17}" font-weight="900">OVĚŘIT DOSTUPNOST</text></svg>'''


def patch_js() -> None:
    text = JS.read_text(encoding="utf-8")
    replacement = "{id:'vodafone-current-offers',title:%r,text:%r,url:%r,banner:'/assets/reklamy/vodafone-current-offers-square.svg',wideBanner:'/assets/reklamy/vodafone-current-offers-wide.svg',tag:'Až 53 %% sleva na internet',contexts:['internet','home','sidebar','general'],weight:7,validFrom:'2026-02-02',validTo:'2026-08-31',fullBleed:true}" % (TITLE, TEXT, URL)
    text, count = re.subn(r"\{id:'vodafone-current-offers',.*?fullBleed:true\}", replacement, text, count=1)
    if count != 1:
        raise SystemExit("V reklamy.js nebyla nalezena hlavní položka vodafone-current-offers")
    tower_replacement = "{id:'vodafone-current-offers-tower',title:%r,url:%r,image:'/assets/reklamy/vodafone-current-offers-tower.svg',width:300,height:600,contexts:['internet','home','sidebar','general'],weight:4,validFrom:'2026-02-02',validTo:'2026-08-31'}" % (TITLE, URL)
    text, count = re.subn(r"\{id:'vodafone-current-offers-tower',.*?\}", tower_replacement, text, count=1)
    if count != 1:
        raise SystemExit("V reklamy.js nebyla nalezena svislá položka vodafone-current-offers-tower")
    JS.write_text(text, encoding="utf-8")


def main() -> None:
    validate_url()
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "vodafone-current-offers-wide.svg").write_text(svg(1200, 400, "wide"), encoding="utf-8")
    (ASSETS / "vodafone-current-offers-square.svg").write_text(svg(800, 800, "square"), encoding="utf-8")
    (ASSETS / "vodafone-current-offers-tower.svg").write_text(svg(300, 600, "tower"), encoding="utf-8")
    patch_js()


if __name__ == "__main__":
    main()
