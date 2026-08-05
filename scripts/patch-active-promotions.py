#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "reklamy.js"
ASSETS = ROOT / "assets" / "reklamy"

PROMOS = [
    {"id":"season-concept-fans","title":"Vedro? Ventilátory Concept","text":"Stolní, stojanové i sloupové ventilátory pro rychlejší proudění vzduchu.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b23975b5&desturl=https%3A%2F%2Fwww.concept.cz%2Fventilatory_c3392989.html","tag":"Vedro a ochlazení","contexts":["home","local","sidebar","general","health"],"weight":12,"validTo":"2026-09-15","theme":("#082f49","#0284c7","#a5f3fc"),"lines":["VEDRO?","VENTILÁTORY CONCEPT"],"sub":["Stolní, stojanové i sloupové modely","Ověřený affiliate odkaz"],"code":"","icon":"fan"},
    {"id":"season-proalergiky-aircon","title":"Mobilní klimatizace Meaco Cool","text":"Chlazení, ventilace, odvlhčování a ovládání přes mobilní aplikaci.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=abc25217&desturl=https%3A%2F%2Fwww.proalergiky.cz%2Feshop%2Fmobilni-klimatizace-meaco-cool-9000-pro","tag":"Klimatizace","contexts":["home","local","sidebar","general","health"],"weight":11,"validTo":"2026-09-15","theme":("#0c4a6e","#0891b2","#cffafe"),"lines":["MOBILNÍ KLIMATIZACE","RYCHLÉ OCHLAZENÍ"],"sub":["Chlazení, ventilace a odvlhčování","Nabídka Proalergiky.cz"],"code":"","icon":"fan"},
    {"id":"owned-vaseuklizecka","title":"VašeUklízečka.cz","text":"Úklid domácností, firem, bytových domů, koberců a sedaček na Kadaňsku.","url":"https://vaseuklizecka.cz/","tag":"Naše místní služba","contexts":["home","local","sidebar","general","health"],"weight":8,"theme":("#052e2b","#0f766e","#facc15"),"lines":["ÚKLID A ČIŠTĚNÍ","NA KADAŇSKU"],"sub":["Domácnosti, firmy, koberce a sedačky","Objednávky 603 206 308"],"code":"","icon":"cleaning"},
    {"id":"owned-vyklidime-banner","title":"VYKLIDIME.TO","text":"Vyklízení bytů, domů, sklepů a pozůstalostí. Odnos, odvoz i úklid.","url":"https://vyklidime.to/","tag":"Naše místní služba","contexts":["home","local","sidebar","general"],"weight":8,"theme":("#3f1d12","#c2410c","#fde047"),"lines":["VYKLÍZENÍ BEZ STAROSTÍ","KADAŇ A OKOLÍ"],"sub":["Byty, domy, sklepy a pozůstalosti","Odnos, odvoz i závěrečný úklid"],"code":"","icon":"clearance"},
    {"id":"owned-pojistime-banner","title":"Pojistime.to","text":"Pojištění auta, domácnosti, cestování, odpovědnosti i další možnosti na jednom místě.","url":"https://pojistime.to/","tag":"Náš web","contexts":["finance","auto","home","travel","sidebar","general"],"weight":6,"theme":("#111827","#0369a1","#67e8f9"),"lines":["POJIŠTĚNÍ A FINANCE","PŘEHLEDNĚ"],"sub":["Auto, domácnost, cestování i energie","Srovnání možností na jednom místě"],"code":"","icon":"shield"},
    {"id":"coupon-concept-leto30","title":"Concept: 30 % na malé spotřebiče","text":"Kupón LETO30 na vybrané malé spotřebiče v letním úklidu skladu. Platí do 31. srpna.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b23975b5&desturl=https%3A%2F%2Fwww.concept.cz%2F","tag":"Kupón LETO30","contexts":["home","sidebar","general","local"],"weight":10,"validTo":"2026-08-31","theme":("#312e81","#7c3aed","#fde047"),"lines":["30 % SLEVA","KÓD LETO30"],"sub":["Vybrané malé spotřebiče Concept","Platí do 31. srpna 2026"],"code":"LETO30","icon":"plus"},
    {"id":"coupon-concept-vyprodej30","title":"Concept: 30 % na velké spotřebiče","text":"Kupón VYPRODEJ30 na vybrané velké spotřebiče. Platí do 31. srpna.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b23975b5&desturl=https%3A%2F%2Fwww.concept.cz%2F","tag":"Kupón VYPRODEJ30","contexts":["home","sidebar","general","local"],"weight":10,"validTo":"2026-08-31","theme":("#1e1b4b","#4338ca","#fef08a"),"lines":["30 % SLEVA","KÓD VYPRODEJ30"],"sub":["Vybrané velké spotřebiče Concept","Platí do 31. srpna 2026"],"code":"VYPRODEJ30","icon":"plus"},
    {"id":"coupon-ariete-italy","title":"Ariete: 25 % na kompletní sortiment","text":"Slevový kód ITALY platí na kompletní sortiment Ariete.cz do konce roku 2026.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=ffcf2387&desturl=https%3A%2F%2Fwww.ariete.cz%2F","tag":"Kupón ITALY","contexts":["home","sidebar","general"],"weight":7,"validTo":"2026-12-31","theme":("#14532d","#16a34a","#fef08a"),"lines":["25 % SLEVA","KÓD ITALY"],"sub":["Kompletní sortiment Ariete.cz","Platí do konce roku 2026"],"code":"ITALY","icon":"plus"},
    {"id":"promo-aranys-80","title":"Aranys: výprodej se slevami až 80 %","text":"Výprodej vybraných produktů Aranys.cz se slevami až 80 %.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=15991a3f&desturl=https%3A%2F%2Faranys.cz%2Fakce-slevy","tag":"Výprodej až 80 %","contexts":["general","sidebar","home"],"weight":8,"validTo":"2026-12-31","theme":("#500724","#be185d","#fce7f3"),"lines":["VÝPRODEJ","SLEVY AŽ 80 %"],"sub":["Vybrané produkty Aranys.cz","Aktuální akční nabídka"],"code":"","icon":"plus"},
    {"id":"coupon-museum-partner30","title":"Museum of Bricks: 30 % na vstupenky","text":"Slevový kód PARTNER30 na vstupenky. Platí do 31. srpna.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=160115dc&desturl=https%3A%2F%2Fmuseumofbricks.cz%2F","tag":"Kupón PARTNER30","contexts":["family","travel","sidebar","general","local"],"weight":8,"validTo":"2026-08-31","theme":("#172554","#2563eb","#facc15"),"lines":["30 % NA VSTUPENKY","KÓD PARTNER30"],"sub":["Museum of Bricks","Platí do 31. srpna 2026"],"code":"PARTNER30","icon":"plus"},
    {"id":"promo-bricks-shop-august","title":"Museum of Bricks: akční nabídka v e-shopu","text":"Slevy na vybrané produkty v e-shopu platí do 16. srpna.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=3ffab0a4&desturl=https%3A%2F%2Feshop.museumofbricks.cz%2Fakcni-nabidka%2F","tag":"Akce do 16. srpna","contexts":["family","sidebar","general","local"],"weight":7,"validTo":"2026-08-16","theme":("#1e3a8a","#2563eb","#fde047"),"lines":["AKČNÍ NABÍDKA","MUSEUM OF BRICKS"],"sub":["Slevy na vybrané produkty e-shopu","Platí do 16. srpna 2026"],"code":"","icon":"plus"},
    {"id":"promo-petexpert-two-months","title":"PetExpert: dva měsíce pojištění zdarma","text":"Akce na pojištění psů a koček platí do 31. srpna.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=ce2e382f","tag":"2 měsíce zdarma","contexts":["pets","family","sidebar","general"],"weight":6,"validTo":"2026-08-31","theme":("#3f1d12","#ea580c","#ffedd5"),"lines":["2 MĚSÍCE","POJIŠTĚNÍ ZDARMA"],"sub":["Pojištění psů a koček PetExpert","Platí do 31. srpna 2026"],"code":"","icon":"shield"},
    {"id":"promo-csob-eurooil1000","title":"ČSOB: poukázka EuroOil 1 000 Kč","text":"Elektronická poukázka EuroOil k autopojištění. Podmínky ověřte u partnera.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=f5e0f8fb&desturl=https%3A%2F%2Fwww.csobpoj.cz%2Fpojisteni%2Fpojisteni-vozidel","tag":"Poukázka 1 000 Kč","contexts":["auto","finance","sidebar","general"],"weight":5,"validTo":"2026-09-30","theme":("#082f49","#0369a1","#fbbf24"),"lines":["POUKÁZKA 1 000 KČ","K AUTOPOJIŠTĚNÍ"],"sub":["Elektronická poukázka EuroOil","Platí do 30. září 2026"],"code":"","icon":"shield"},
    {"id":"promo-rb-six500","title":"Raiffeisenbank: bonus až 6×500 Kč","text":"Bonus na nový běžný účet. Konkrétní podmínky ověřte na cílové stránce.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=446f3eb0","tag":"Bonus až 3 000 Kč","contexts":["finance","sidebar","general"],"weight":5,"validTo":"2026-12-31","theme":("#713f12","#eab308","#111827"),"lines":["BONUS AŽ 6×500 KČ","NA NOVÝ ÚČET"],"sub":["Raiffeisenbank běžný účet","Podmínky na cílové stránce"],"code":"","icon":"plus"},
    {"id":"promo-mbank-421","title":"mBank: úrok až 4,21 % p.a.","text":"mSpořicí účet Plus k novému mKontu. Akce platí do 16. srpna.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=cb64a4ba&desturl=https%3A%2F%2Fmbank.ehub.cz%2F","tag":"Platí do 16. srpna","contexts":["finance","sidebar","general"],"weight":6,"validTo":"2026-08-16","theme":("#7f1d1d","#dc2626","#ffffff"),"lines":["ÚROK AŽ 4,21 % P.A.","K NOVÉMU mKONTU"],"sub":["mSpořicí účet Plus","Platí do 16. srpna 2026"],"code":"","icon":"plus"},
    {"id":"vodafone-current-offers","title":"Vodafone: aktuální tarify, internet a TV","text":"Ověřte právě dostupné nabídky. Staré červencové ceny se nezobrazují.","url":"https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=aface625","tag":"Aktuální nabídky","contexts":["internet","home","sidebar","general"],"weight":4,"theme":("#7f1d1d","#e60000","#ffffff"),"lines":["VODAFONE","TARIFY, INTERNET A TV"],"sub":["Ověřte právě dostupné nabídky","Ceny a podmínky na cílové stránce"],"code":"","icon":"signal"}
]

TOWERS = {"season-concept-fans","season-proalergiky-aircon","owned-vaseuklizecka","owned-vyklidime-banner","coupon-concept-leto30","coupon-concept-vyprodej30","coupon-museum-partner30","promo-aranys-80","vodafone-current-offers"}


def svg(item: dict, width: int, height: int, fmt: str) -> str:
    bg1, bg2, accent = item["theme"]
    title = item["lines"]
    sub = item["sub"]
    wide = fmt == "wide"
    square = fmt == "square"
    title_size = 58 if wide else 47 if square else 30
    sub_size = 24 if wide else 22 if square else 16
    x = 72 if wide else width / 2
    anchor = "start" if wide else "middle"
    title_y = 150 if wide else 190 if square else 110
    gap = title_size * 1.08
    sub_y = title_y + len(title) * gap + (18 if wide else 28)
    icon_x = width - 270 if wide else width / 2 - 105
    icon_y = 68 if wide else height * .55
    icon_size = 210 if wide else 210 if square else 150
    button_w = 265 if wide else width * .68
    button_h = 54 if wide else 52
    button_x = 72 if wide else (width - button_w) / 2
    button_y = height - button_h - (42 if wide else 48)
    title_svg = "".join(f'<text x="{x}" y="{title_y+i*gap}" text-anchor="{anchor}" fill="#fff" font-size="{title_size}" font-weight="900">{html.escape(line)}</text>' for i,line in enumerate(title))
    sub_svg = "".join(f'<text x="{x}" y="{sub_y+i*sub_size*1.35}" text-anchor="{anchor}" fill="#e2e8f0" font-size="{sub_size}" font-weight="600">{html.escape(line)}</text>' for i,line in enumerate(sub))
    if item["icon"] == "fan":
        icon = f'<g transform="translate({icon_x} {icon_y})" fill="none" stroke="{accent}" stroke-width="10" stroke-linecap="round"><circle cx="{icon_size/2}" cy="{icon_size/2}" r="{icon_size*.42}"/><circle cx="{icon_size/2}" cy="{icon_size/2}" r="{icon_size*.08}"/><path d="M{icon_size*.5} {icon_size*.42}c-{icon_size*.25}-{icon_size*.30}-{icon_size*.45}-{icon_size*.12}-{icon_size*.32} {icon_size*.09}"/><path d="M{icon_size*.58} {icon_size*.5}c{icon_size*.37}-{icon_size*.04} {icon_size*.34}-{icon_size*.29} {icon_size*.10}-{icon_size*.29}"/><path d="M{icon_size*.45} {icon_size*.57}c-{icon_size*.12} {icon_size*.35} {icon_size*.15} {icon_size*.43} {icon_size*.29} {icon_size*.20}"/></g>'
    else:
        icon = f'<circle cx="{icon_x+icon_size/2}" cy="{icon_y+icon_size/2}" r="{icon_size*.42}" fill="none" stroke="{accent}" stroke-width="10"/><text x="{icon_x+icon_size/2}" y="{icon_y+icon_size*.68}" text-anchor="middle" fill="{accent}" font-size="{icon_size*.62}" font-weight="900">%</text>'
    badge = html.escape(item["tag"].upper())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(item['title'])}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient><radialGradient id="r"><stop offset="0" stop-color="{accent}" stop-opacity=".24"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient></defs><rect width="{width}" height="{height}" rx="28" fill="url(#g)"/><circle cx="{width*.86 if wide else width*.5}" cy="{height*.52 if wide else height*.70}" r="{height*.66 if wide else width*.58}" fill="url(#r)"/><rect x="{72 if wide else width*.08}" y="{38 if wide else 42}" width="{320 if wide else width*.84}" height="42" rx="21" fill="{accent}" fill-opacity=".18" stroke="{accent}" stroke-opacity=".55"/><text x="{90 if wide else width/2}" y="{66 if wide else 70}" text-anchor="{'start' if wide else 'middle'}" fill="#fff" font-size="17" font-weight="850" letter-spacing="1.1">{badge}</text>{title_svg}{sub_svg}{icon}<rect x="{button_x}" y="{button_y}" width="{button_w}" height="{button_h}" rx="{button_h/2}" fill="{accent}"/><text x="{button_x+button_w/2}" y="{button_y+button_h*.67}" text-anchor="middle" fill="{bg1}" font-size="{19 if wide else 17}" font-weight="900">ZJISTIT VÍCE</text></svg>'''


def js_item(item: dict) -> str:
    attrs = [
        f"id:{item['id']!r}", f"title:{item['title']!r}", f"text:{item['text']!r}", f"url:{item['url']!r}",
        f"banner:{('/assets/reklamy/'+item['id']+'-square.svg')!r}", f"wideBanner:{('/assets/reklamy/'+item['id']+'-wide.svg')!r}",
        f"tag:{item['tag']!r}", f"contexts:{item['contexts']!r}", f"weight:{item['weight']}", "fullBleed:true"
    ]
    if item.get("validFrom"): attrs.append(f"validFrom:{item['validFrom']!r}")
    if item.get("validTo"): attrs.append(f"validTo:{item['validTo']!r}")
    return "  {" + ",".join(attrs) + "},"


def tower_item(item: dict) -> str:
    attrs = [f"id:{(item['id']+'-tower')!r}", f"title:{item['title']!r}", f"url:{item['url']!r}", f"image:{('/assets/reklamy/'+item['id']+'-tower.svg')!r}", "width:300", "height:600", f"contexts:{item['contexts']!r}", f"weight:{max(1,item['weight']//2)}"]
    if item.get("validFrom"): attrs.append(f"validFrom:{item['validFrom']!r}")
    if item.get("validTo"): attrs.append(f"validTo:{item['validTo']!r}")
    return "  {" + ",".join(attrs) + "},"


def patch_js(text: str) -> str:
    promo_block = "/* ACTIVE_PROMOTIONS_START */\n" + "\n".join(js_item(item) for item in PROMOS) + "\n/* ACTIVE_PROMOTIONS_END */\n"
    text = re.sub(r"/\* ACTIVE_PROMOTIONS_START \*/.*?/\* ACTIVE_PROMOTIONS_END \*/\n?", "", text, flags=re.S)
    text = text.replace("const promoItems=[\n", "const promoItems=[\n" + promo_block, 1)

    tower_block = "/* ACTIVE_TOWERS_START */\n" + "\n".join(tower_item(item) for item in PROMOS if item["id"] in TOWERS) + "\n/* ACTIVE_TOWERS_END */\n"
    text = re.sub(r"/\* ACTIVE_TOWERS_START \*/.*?/\* ACTIVE_TOWERS_END \*/\n?", "", text, flags=re.S)
    text = text.replace("const towerCreativeItems=[\n", "const towerCreativeItems=[\n" + tower_block, 1)

    helper = '''function isPromoActive(item){
  const today=new Date().toISOString().slice(0,10);
  if(item.validFrom&&today<item.validFrom)return false;
  if(item.validTo&&today>item.validTo)return false;
  return true;
}

'''
    if "function isPromoActive(item)" not in text:
        text = text.replace("function pickPromos(context,count,offset){", helper + "function pickPromos(context,count,offset){", 1)

    new_pick = '''function pickPromos(context,count,offset){
  const expand=item=>Array.from({length:Math.max(1,Number(item.weight)||1)},()=>item);
  const active=promoItems.filter(isPromoActive);
  const exact=active.filter(item=>item.contexts.includes(context)).flatMap(expand);
  const exactIds=new Set(exact.map(item=>item.id));
  const fallback=active.filter(item=>!exactIds.has(item.id)).flatMap(expand);
  const pool=[...exact,...fallback];
  if(!pool.length)return [];
  const day=new Date().toISOString().slice(0,10);
  const shift=(hashSeed(location.pathname+day)+offset)%pool.length;
  const rotated=[...pool.slice(shift),...pool.slice(0,shift)];
  const fresh=rotated.filter(item=>!usedPromoIds.has(item.id));
  const ordered=[...fresh,...rotated.filter(item=>!fresh.includes(item))];
  const selected=[];
  for(const item of ordered){
    if(selected.some(entry=>entry.id===item.id))continue;
    selected.push(item);
    if(selected.length===count)break;
  }
  selected.forEach(item=>usedPromoIds.add(item.id));
  return selected;
}

'''
    text = re.sub(r"function pickPromos\(context,count,offset\)\{.*?\n\}\n\n(?=function inferPromoContext)", new_pick, text, flags=re.S)

    new_tower = '''function pickTowerCreative(context,offset=0){
  const expand=item=>Array.from({length:Math.max(1,Number(item.weight)||1)},()=>item);
  const active=towerCreativeItems.filter(isPromoActive);
  const exact=active.filter(item=>item.contexts.includes(context)).flatMap(expand);
  const exactIds=new Set(exact.map(item=>item.id));
  const pool=[...exact,...active.filter(item=>!exactIds.has(item.id)).flatMap(expand)];
  if(!pool.length)return null;
  const day=new Date().toISOString().slice(0,10);
  return pool[(hashSeed(`${location.pathname}|${day}|tower`)+offset)%pool.length];
}

'''
    text = re.sub(r"function pickTowerCreative\(context,offset=0\)\{.*?\n\}\n\n(?=function pickRailPromo)", new_tower, text, flags=re.S)
    text = text.replace("  const pool=[\n    ...promoItems.filter(item=>item.contexts.includes(context)&&item.banner),", "  const active=promoItems.filter(isPromoActive);\n  const pool=[\n    ...active.filter(item=>item.contexts.includes(context)&&item.banner),", 1)
    text = text.replace("    ...promoItems.filter(item=>!item.contexts.includes(context)&&item.banner),\n    ...promoItems.filter(item=>item.contexts.includes(context)&&!item.banner),\n    ...promoItems.filter(item=>!item.contexts.includes(context)&&!item.banner)", "    ...active.filter(item=>!item.contexts.includes(context)&&item.banner),\n    ...active.filter(item=>item.contexts.includes(context)&&!item.banner),\n    ...active.filter(item=>!item.contexts.includes(context)&&!item.banner)", 1)
    return text


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for item in PROMOS:
        (ASSETS / f"{item['id']}-wide.svg").write_text(svg(item, 1200, 400, "wide"), encoding="utf-8")
        (ASSETS / f"{item['id']}-square.svg").write_text(svg(item, 800, 800, "square"), encoding="utf-8")
        if item["id"] in TOWERS:
            (ASSETS / f"{item['id']}-tower.svg").write_text(svg(item, 300, 600, "tower"), encoding="utf-8")
    text = JS.read_text(encoding="utf-8")
    JS.write_text(patch_js(text), encoding="utf-8")


if __name__ == "__main__":
    main()
