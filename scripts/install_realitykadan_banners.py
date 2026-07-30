#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADS = ROOT / 'reklamy.js'
FIX = ROOT / 'reklamy-oprava-obrazku.js'


def main() -> int:
    text = ADS.read_text(encoding='utf-8')
    marker = "const promoItems=[\n"
    if "id:'realitykadan-byt'" not in text:
        block = """  {id:'realitykadan-byt',title:'Prodáváte byt v Kadani nebo v Klášterci?',text:'Rychlá nabídka bez zbytečného čekání. Férově, nezávazně a bez provize.',url:'https://realitykadan.cz',banner:'/assets/reklamy/realitykadan-byt-wide-v1.svg',wideBanner:'/assets/reklamy/realitykadan-byt-wide-v1.svg',tag:'Výkup nemovitostí',contexts:['home','local','sidebar','general','finance'],weight:6,fullBleed:true},
  {id:'realitykadan-garaz',title:'Prodáváte garáž v Kadani nebo v Klášterci?',text:'Rychlá nabídka, minimum formalit a férové podmínky.',url:'https://realitykadan.cz',banner:'/assets/reklamy/realitykadan-garaz-wide-v1.svg',wideBanner:'/assets/reklamy/realitykadan-garaz-wide-v1.svg',tag:'Výkup nemovitostí',contexts:['home','local','sidebar','general'],weight:5,fullBleed:true},
"""
        if marker not in text:
            raise RuntimeError('V reklamy.js chybí začátek promoItems.')
        text = text.replace(marker, marker + block, 1)

    css_marker = "    .promo-grid-banner{grid-template-columns:minmax(0,1fr)!important}\n"
    if '.promo-card-full-image{' not in text:
        css = """    .promo-card-full-image{display:block!important;padding:0!important;min-height:0!important;overflow:hidden}
    .promo-card-full-image .promo-banner{display:block!important;height:auto!important;min-height:0!important;margin:0!important;border:0!important}
    .promo-card-full-image .promo-banner img{display:block!important;width:100%!important;height:auto!important;max-width:none!important;max-height:none!important;object-fit:contain!important;padding:0!important;background:#fff}
    .promo-card-full-image .promo-wide-copy{display:none!important}
"""
        if css_marker not in text:
            raise RuntimeError('V reklamy.js chybí CSS marker.')
        text = text.replace(css_marker, css_marker + css, 1)

    # Staré obecné pravidlo .promo-card-wide je níže v CSS a přepisovalo
    # display:block i rozměry obrázku. Silnější pravidla proto vkládáme až
    # za obecné styly a používáme kombinovaný selektor obou tříd.
    full_width_marker = "    .promo-card-wide .promo-banner img{width:100%;height:100%;max-width:none!important;max-height:none!important;object-fit:contain;padding:10px;background:#fff}\n"
    full_width_css = """    .promo-card-wide.promo-card-full-image{display:block!important;grid-template-columns:none!important;width:100%!important;max-width:1180px!important;min-height:0!important;padding:0!important}
    .promo-card-wide.promo-card-full-image>.promo-banner{display:block!important;width:100%!important;height:auto!important;min-height:0!important;margin:0!important;border:0!important}
    .promo-card-wide.promo-card-full-image>.promo-banner img{display:block!important;width:100%!important;height:auto!important;max-width:none!important;max-height:none!important;object-fit:contain!important;padding:0!important;background:#fff}
    .promo-card-wide.promo-card-full-image>.promo-wide-copy{display:none!important}
    .featured-cleaning-ad>a.promo-card-full-image{max-width:1180px!important}
"""
    if '.promo-card-wide.promo-card-full-image{' not in text:
        if full_width_marker not in text:
            raise RuntimeError('V reklamy.js chybí obecný styl široké reklamy.')
        text = text.replace(full_width_marker, full_width_marker + full_width_css, 1)

    old_return = "  return `<a class=\"promo-card promo-card-wide\" href=\"${escapeHtml(safeHttpUrl(item.url))}\" target=\"_blank\" rel=\"nofollow sponsored noopener noreferrer\">${visual}<span class=\"promo-wide-copy\"><small>${escapeHtml(item.tag)}</small><strong>${title}</strong><span class=\"promo-description\">${escapeHtml(item.text)}</span><b>Zjistit více →</b></span></a>`;"
    new_return = "  const fullClass=item.fullBleed?' promo-card-full-image':'';\n  return `<a class=\"promo-card promo-card-wide${fullClass}\" href=\"${escapeHtml(safeHttpUrl(item.url))}\" target=\"_blank\" rel=\"nofollow sponsored noopener noreferrer\">${visual}<span class=\"promo-wide-copy\"><small>${escapeHtml(item.tag)}</small><strong>${title}</strong><span class=\"promo-description\">${escapeHtml(item.text)}</span><b>Zjistit více →</b></span></a>`;"
    if 'const fullClass=item.fullBleed' not in text:
        if old_return not in text:
            raise RuntimeError('V reklamy.js chybí renderBannerCard marker.')
        text = text.replace(old_return, new_return, 1)

    mobile_marker = "      .promo-card-wide .promo-banner{height:112px!important;min-height:112px;border-right:0;border-bottom:1px solid var(--line)}\n"
    mobile_full = "      .promo-card-full-image .promo-banner{height:auto!important;min-height:0!important;border:0!important}\n"
    if mobile_full not in text:
        if mobile_marker not in text:
            raise RuntimeError('V reklamy.js chybí mobilní CSS marker.')
        text = text.replace(mobile_marker, mobile_marker + mobile_full, 1)

    ADS.write_text(text, encoding='utf-8', newline='\n')

    ftext = FIX.read_text(encoding='utf-8')
    cleaning = "    const cleaning=promoItems.filter(item=>itemId(item)==='uklizecka-cisteni-rotating');\n"
    reality = "    const reality=promoItems.filter(item=>['realitykadan-byt','realitykadan-garaz'].includes(itemId(item)));\n"
    if reality not in ftext:
        if cleaning not in ftext:
            raise RuntimeError('V reklamy-oprava-obrazku.js chybí marker hlavní rotace.')
        ftext = ftext.replace(cleaning, cleaning + reality, 1)

    old_candidates = "    const candidates=[...cleaning,...seasonal].filter((item,index,array)=>array.findIndex(entry=>entry.id===item.id)===index);"
    new_candidates = "    const candidates=[...reality,...cleaning,...seasonal].filter((item,index,array)=>array.findIndex(entry=>entry.id===item.id)===index);"
    if old_candidates in ftext:
        ftext = ftext.replace(old_candidates, new_candidates, 1)
    if new_candidates not in ftext:
        raise RuntimeError('Nepodařilo se zapojit Reality Kadaň do hlavní rotace.')
    FIX.write_text(ftext, encoding='utf-8', newline='\n')

    for name, phrase in (
        ('realitykadan-byt-wide-v1.svg', 'KOUPÍME HO.'),
        ('realitykadan-garaz-wide-v1.svg', 'KOUPÍME JI.'),
    ):
        data = (ROOT / 'assets' / 'reklamy' / name).read_text(encoding='utf-8')
        if '<svg' not in data or '2400' not in data or phrase not in data:
            raise RuntimeError(f'Neplatný banner {name}.')

    if '.promo-card-wide.promo-card-full-image{' not in text:
        raise RuntimeError('Chybí finální pravidlo pro plnou šířku banneru.')

    print('Reality Kadaň: oba bannery jsou zapojené a vyplní celou šířku reklamní karty.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
