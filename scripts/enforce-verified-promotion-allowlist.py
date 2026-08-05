#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "reklamy.js"
ASSETS = ROOT / "assets" / "reklamy"
REALITY_ID = "owned-realitykadan-banner"
REALITY_URL = "https://realitykadan.cz/"


def validate_reality() -> None:
    response = requests.get(REALITY_URL, headers={"User-Agent": "Mozilla/5.0 PromotionAllowlist/1.0", "Cache-Control": "no-cache"}, timeout=(10, 25), allow_redirects=True)
    if response.status_code >= 400 or not response.content.strip():
        raise SystemExit(f"RealityKadan.cz neprošel kontrolou: HTTP {response.status_code}")


def reality_svg(width: int, height: int, fmt: str) -> str:
    wide = fmt == "wide"
    title_size = 58 if wide else 48
    sub_size = 24 if wide else 22
    x = 72 if wide else width / 2
    anchor = "start" if wide else "middle"
    title_y = 155 if wide else 200
    gap = title_size * 1.05
    sub_y = title_y + gap * 2 + 24
    icon_size = 210 if wide else 230
    icon_x = width - icon_size - 78 if wide else (width - icon_size) / 2
    icon_y = 78 if wide else height * .56
    button_w = 285 if wide else width * .72
    button_h = 54
    button_x = 72 if wide else (width - button_w) / 2
    button_y = height - button_h - (40 if wide else 50)
    house = f'''<g transform="translate({icon_x} {icon_y})" fill="none" stroke="#fbbf24" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><path d="M{icon_size*.10} {icon_size*.48}L{icon_size*.50} {icon_size*.14}L{icon_size*.90} {icon_size*.48}"/><path d="M{icon_size*.20} {icon_size*.42}v{icon_size*.42}h{icon_size*.60}v-{icon_size*.42}"/><rect x="{icon_size*.42}" y="{icon_size*.58}" width="{icon_size*.16}" height="{icon_size*.26}"/></g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="RealityKadan.cz – prodej nemovitostí v Kadani a okolí"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#172554"/><stop offset="1" stop-color="#1d4ed8"/></linearGradient><radialGradient id="r"><stop offset="0" stop-color="#fbbf24" stop-opacity=".26"/><stop offset="1" stop-color="#fbbf24" stop-opacity="0"/></radialGradient></defs><rect width="{width}" height="{height}" rx="28" fill="url(#g)"/><circle cx="{width*.87 if wide else width*.5}" cy="{height*.53 if wide else height*.70}" r="{height*.66 if wide else width*.58}" fill="url(#r)"/><rect x="{72 if wide else width*.08}" y="{38 if wide else 42}" width="{300 if wide else width*.84}" height="42" rx="21" fill="#fbbf24" fill-opacity=".18" stroke="#fbbf24" stroke-opacity=".55"/><text x="{90 if wide else width/2}" y="{66 if wide else 70}" text-anchor="{'start' if wide else 'middle'}" fill="#fff" font-size="17" font-weight="850" letter-spacing="1.1">NAŠE MÍSTNÍ SLUŽBA</text><text x="{x}" y="{title_y}" text-anchor="{anchor}" fill="#fff" font-size="{title_size}" font-weight="900">PRODÁVÁTE NEMOVITOST?</text><text x="{x}" y="{title_y+gap}" text-anchor="{anchor}" fill="#fff" font-size="{title_size}" font-weight="900">KADAŇ A OKOLÍ</text><text x="{x}" y="{sub_y}" text-anchor="{anchor}" fill="#dbeafe" font-size="{sub_size}" font-weight="650">Byty, domy, garáže a pozemky</text><text x="{x}" y="{sub_y+sub_size*1.35}" text-anchor="{anchor}" fill="#dbeafe" font-size="{sub_size}" font-weight="650">Rychlá a nezávazná nabídka</text>{house}<rect x="{button_x}" y="{button_y}" width="{button_w}" height="{button_h}" rx="27" fill="#fbbf24"/><text x="{button_x+button_w/2}" y="{button_y+36}" text-anchor="middle" fill="#172554" font-size="19" font-weight="900">ZJISTIT MOŽNOSTI</text></svg>'''


def patch_active_block(text: str) -> str:
    match = re.search(r"(/\* ACTIVE_PROMOTIONS_START \*/)(.*?)(/\* ACTIVE_PROMOTIONS_END \*/)", text, re.S)
    if not match:
        raise SystemExit("Chybí blok ACTIVE_PROMOTIONS")
    block = match.group(2)
    block = re.sub(r"fullBleed:true(?!,runtimeVerified:true)", "fullBleed:true,runtimeVerified:true", block)
    if f"id:'{REALITY_ID}'" not in block:
        reality = (
            "\n  {id:'owned-realitykadan-banner',title:'RealityKadan.cz',"
            "text:'Prodej bytů, domů, garáží a pozemků v Kadani a okolí. Rychlá a nezávazná nabídka.',"
            "url:'https://realitykadan.cz/',banner:'/assets/reklamy/owned-realitykadan-banner-square.svg',"
            "wideBanner:'/assets/reklamy/owned-realitykadan-banner-wide.svg',tag:'Naše místní služba',"
            "contexts:['home','local','sidebar','general','finance'],weight:8,fullBleed:true,runtimeVerified:true},\n"
        )
        block += reality
    return text[:match.start()] + match.group(1) + block + match.group(3) + text[match.end():]


def patch_tower_block(text: str) -> str:
    match = re.search(r"(/\* ACTIVE_TOWERS_START \*/)(.*?)(/\* ACTIVE_TOWERS_END \*/)", text, re.S)
    if not match:
        raise SystemExit("Chybí blok ACTIVE_TOWERS")
    block = match.group(2)
    block = re.sub(r"(weight:\d+)(?!,runtimeVerified:true)", r"\1,runtimeVerified:true", block)
    return text[:match.start()] + match.group(1) + block + match.group(3) + text[match.end():]


def enforce_filters(text: str) -> str:
    text = text.replace("const active=promoItems.filter(isPromoActive);", "const active=promoItems.filter(isPromoActive).filter(item=>item.runtimeVerified===true);")
    text = text.replace("const active=towerCreativeItems.filter(isPromoActive);", "const active=towerCreativeItems.filter(isPromoActive).filter(item=>item.runtimeVerified===true);")
    if "runtimeVerified===true" not in text:
        raise SystemExit("Nepodařilo se vložit allowlist filtr")
    return text


def main() -> None:
    validate_reality()
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "owned-realitykadan-banner-wide.svg").write_text(reality_svg(1200, 400, "wide"), encoding="utf-8")
    (ASSETS / "owned-realitykadan-banner-square.svg").write_text(reality_svg(800, 800, "square"), encoding="utf-8")
    text = JS.read_text(encoding="utf-8")
    text = patch_active_block(text)
    text = patch_tower_block(text)
    text = enforce_filters(text)
    JS.write_text(text, encoding="utf-8")
    print("Veřejná rotace je uzamčena na runtimeVerified allowlist.")


if __name__ == "__main__":
    main()
