#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

STYLE = '''<style data-heat-feed-static-style>
.nk-horko-feed{margin:38px auto 48px;padding:24px;border:1px solid #e5d7bd;border-radius:20px;background:linear-gradient(135deg,#fffaf0,#fff 58%,#eef7fb);box-shadow:0 12px 34px rgba(18,35,45,.08);max-width:1180px}
.nk-horko-feed-head{display:flex;justify-content:space-between;gap:16px;align-items:end;margin-bottom:16px}.nk-horko-feed-head small{display:block;color:#a9232b;font-size:11px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}.nk-horko-feed-head strong{display:block;margin-top:4px;font:800 28px/1.15 Georgia,serif;color:#14232d}.nk-horko-feed-head span{color:#66747c;font-size:12px}.nk-horko-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.nk-horko-card{display:flex;flex-direction:column;min-width:0;background:#fff;border:1px solid #dde4e7;border-radius:16px;overflow:hidden;color:#14232d!important;text-decoration:none!important;box-shadow:0 8px 24px rgba(18,35,45,.07)}.nk-horko-image{display:flex;align-items:center;justify-content:center;height:112px;background:linear-gradient(135deg,#eef7fb,#fff7e9);border-bottom:1px solid #e4e8ea;font-size:48px}.nk-horko-copy{display:flex;flex-direction:column;flex:1;padding:17px}.nk-horko-copy small{color:#a9232b;font-weight:850;text-transform:uppercase;letter-spacing:.05em}.nk-horko-copy strong{font:800 22px/1.17 Georgia,serif;margin:7px 0}.nk-horko-copy span{color:#53616a;line-height:1.45;flex:1}.nk-horko-target{display:block;margin-top:10px;color:#6d777d!important;font-size:11px;word-break:break-all}.nk-horko-copy b{color:#a9232b;margin-top:13px}@media(max-width:850px){.nk-horko-grid{grid-template-columns:1fr}.nk-horko-image{height:96px}.nk-horko-feed-head{align-items:start;flex-direction:column}.nk-horko-feed{margin:28px 16px 40px}}
</style>'''

BLOCK = '''<section class="nk-horko-feed" data-heat-affiliate-feed="1">
<div class="nk-horko-feed-head"><div><small>REKLAMA · SEZÓNNÍ VÝBĚR</small><strong>Jak zvládnout horké dny doma</strong></div><span>Přímé odkazy do kategorií</span></div>
<div class="nk-horko-grid">
<a class="nk-horko-card" href="https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b23975b5&data1=nasekadan&data2=horko-concept&desturl=https%3A%2F%2Fwww.concept.cz%2Fventilatory_c3392989.html" target="_blank" rel="nofollow sponsored noopener noreferrer" data-final-target="concept.cz/ventilatory"><span class="nk-horko-image" aria-hidden="true">🌬️</span><span class="nk-horko-copy"><small>Ventilátory</small><strong>Ventilátory Concept</strong><span>Přímý výběr stolních, stojanových a sloupových ventilátorů pro ochlazení bytu, kanceláře nebo ložnice.</span><em class="nk-horko-target">Cíl: concept.cz/ventilatory</em><b>Prohlédnout konkrétní nabídku →</b></span></a>
<a class="nk-horko-card" href="https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=da726a9e&data1=nasekadan&data2=horko-biano&desturl=https%3A%2F%2Fwww.biano.cz%2Fprodukty%2Frolety" target="_blank" rel="nofollow sponsored noopener noreferrer" data-final-target="biano.cz/produkty/rolety"><span class="nk-horko-image" aria-hidden="true">🪟</span><span class="nk-horko-copy"><small>Stínění</small><strong>Rolety a žaluzie na Biano</strong><span>Přímý výpis rolet, žaluzií a zatemňovacího stínění, které pomáhá omezit přehřívání interiéru.</span><em class="nk-horko-target">Cíl: biano.cz/produkty/rolety</em><b>Prohlédnout konkrétní nabídku →</b></span></a>
<a class="nk-horko-card" href="https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=abc25217&data1=nasekadan&data2=horko-pro&desturl=https%3A%2F%2Fwww.proalergiky.cz%2Feshop%2Fcisticky-vzduchu" target="_blank" rel="nofollow sponsored noopener noreferrer" data-final-target="proalergiky.cz/eshop/cisticky-vzduchu"><span class="nk-horko-image" aria-hidden="true">🍃</span><span class="nk-horko-copy"><small>Čistší vzduch</small><strong>Čističky vzduchu ProAlergiky</strong><span>Přímý výběr čističek vzduchu pro zachytávání pylu, prachu, kouře a dalších nečistot v domácnosti.</span><em class="nk-horko-target">Cíl: proalergiky.cz/eshop/cisticky-vzduchu</em><b>Prohlédnout konkrétní nabídku →</b></span></a>
</div></section>'''


def inject(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'data-heat-affiliate-feed="1"' in text:
        return False
    if '</head>' in text and 'data-heat-feed-static-style' not in text:
        text = text.replace('</head>', STYLE + '\n</head>', 1)
    if '<section class="wrap promo-wrap"' in text:
        text = text.replace('<section class="wrap promo-wrap"', BLOCK + '\n<section class="wrap promo-wrap"', 1)
    elif '<main' in text:
        pos = text.find('>', text.find('<main')) + 1
        text = text[:pos] + '\n' + BLOCK + text[pos:]
    else:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default='.')
    args = parser.parse_args()
    root = Path(args.root)
    changed = 0
    for path in [root / 'index.html', *sorted((root / 'clanky').glob('*.html'))]:
        if path.exists() and inject(path):
            changed += 1
    print(f'Statický feed vložen do {changed} HTML souborů.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
