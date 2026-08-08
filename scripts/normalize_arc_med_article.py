#!/usr/bin/env python3
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
path = root / 'clanky' / 'arc-med-nemocnice-kadan.html'
text = path.read_text(encoding='utf-8')

# Veřejná verze a standardní cesty.
text = text.replace('content="noindex,nofollow"', 'content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"')
text = text.replace('href="../../favicon.svg"', 'href="../favicon.svg"')
text = text.replace('href="../../style.css"', 'href="../style.css"')
text = text.replace('href="../../index.html"', 'href="../index.html"')
text = text.replace('href="../../pruvodce/"', 'href="../pruvodce/"')
text = text.replace('src="../../site.js"', 'src="../site.js"')
text = text.replace('ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · PŘIPRAVOVANÝ ČLÁNEK', 'ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · 28. ČERVENCE 2026')

# Oprava faktického omylu z původní verze článku: metadata Registru smluv cenu
# neukazují, ale přiložená smlouva ji uvádí včetně pěti splátek a rozdělení
# mezi pět převodců. Oprava je idempotentní, aby ji další normalizace nevracela.
old_desc = 'Nemocnice Kadaň koupila ARC-MED podle veřejných vyjádření za 16 milionů korun. Rozebíráme dva odhady hodnoty, schvalování transakce a tvrzení o 12,1 milionu od pojišťovny.'
new_desc = 'Zveřejněná smlouva potvrzuje kupní cenu ARC-MED 16 milionů korun i pět splátek. Rozebíráme ocenění, schvalování transakce a spor o 12,1 milionu.'
text = text.replace(old_desc, new_desc)

old_tag = '<p class="tag">ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · 28. ČERVENCE 2026</p>'
new_tag = '<p class="tag">ZDRAVOTNICTVÍ · VEŘEJNÉ PENÍZE · 28. ČERVENCE 2026 · AKTUALIZOVÁNO 8. SRPNA 2026</p>'
text = text.replace(old_tag, new_tag)

old_lead = '<p class="leadtext">Nemocnice Kadaň tvrdí, že rehabilitační společnost ARC-MED koupila za cenu nejméně o 10,4 milionu korun vyšší, než odpovídalo její tržní hodnotě. Bývalý jednatel Petr Hossner namítá, že město o transakci vědělo a že převzetí firmy přineslo nemocnici personál, smluvní vztahy i další příjmy. Veřejné dokumenty potvrzují rychlý nákup a následnou fúzi. Zatím ale neukazují celý výpočet ceny ani jednoznačný akt, kterým by rada města schválila právě částku 16 milionů.</p>'
new_lead = '<p class="leadtext">Zveřejněná smlouva o převodu obchodního podílu výslovně potvrzuje, že Nemocnice Kadaň koupila ARC-MED za 16 milionů korun, a obsahuje i pět splátek a rozdělení ceny mezi pět prodávajících. Spor se proto netýká toho, zda byla částka 16 milionů sjednána, ale především přiměřenosti této ceny, podkladů pro její stanovení a způsobu, jakým byla transakce projednána a schválena.</p>'
text = text.replace(old_lead, new_lead)

correction = '''
<div class="factcheck" data-arc-med-correction="2026-08-08"><h3>Aktualizace 8. srpna 2026</h3><p>V původní verzi článku jsme nesprávně uvedli, že veřejný záznam Registru smluv částku 16 milionů korun sám nepotvrzuje a že chybí úplná smlouva včetně splátkového kalendáře. Metadata Registru smluv hodnotu skutečně neuvádějí, ale přiložené PDF smlouvy ji výslovně stanoví na 16&nbsp;000&nbsp;000 Kč a obsahuje i rozdělení pěti splátek mezi pět prodávajících. Text jsme proto opravili a doplnili.</p></div>
'''
if 'data-arc-med-correction="2026-08-08"' not in text:
    text = text.replace(new_lead, new_lead + correction, 1)

text = text.replace(
    '<div><b>16 mil. Kč</b><span>kupní cena uváděná nemocnicí a veřejnými vyjádřeními aktérů</span></div>',
    '<div><b>16 mil. Kč</b><span>kupní cena výslovně sjednaná ve zveřejněné smlouvě</span></div>'
)

old_jiste = '<p>Registr smluv potvrzuje, že Nemocnice Kadaň uzavřela 22. května 2024 smlouvu označenou jako smlouva o převodu obchodního podílu. Zveřejněna byla následující den. V metadatech registru však není uvedena hodnota smlouvy a veřejný záznam proto sám o sobě nepotvrzuje částku 16 milionů korun. Tuto cenu uvádí současné vedení nemocnice, bývalý jednatel i veřejná mediální vyjádření.</p>'
new_jiste = '''<p>Registr smluv potvrzuje, že Nemocnice Kadaň uzavřela 22. května 2024 smlouvu o převodu obchodního podílu a zveřejnila ji následující den. V metadatech registru sice zůstala pole pro hodnotu smlouvy prázdná, samotná přiložená smlouva však částku potvrzuje jednoznačně: článek 2.1 stanoví kupní cenu na <strong>16&nbsp;000&nbsp;000 Kč</strong>.</p>
<p>Článek 2.2 zároveň obsahuje přesný splátkový kalendář. První platba činila podle smlouvy 6 milionů korun a měla být uhrazena do dvou pracovních dnů po účinnosti smlouvy. Další čtyři platby činí každá 2,5 milionu korun a jsou splatné vždy k výročí uzavření smlouvy. Smlouva tedy rozkládá kupní cenu do pěti plateb: 6 + 2,5 + 2,5 + 2,5 + 2,5 milionu korun.</p>
<h3>Jak smlouva rozděluje 16 milionů mezi pět prodávajících</h3>
<table><thead><tr><th>Prodávající</th><th>Podíl</th><th>1. platba</th><th>Každá z plateb 2.–5.</th><th>Celkem dle smlouvy</th></tr></thead><tbody>
<tr><td>MUDr. Zora Ouzká</td><td>52 %</td><td>3 120 000 Kč</td><td>1 300 000 Kč</td><td>8 320 000 Kč</td></tr>
<tr><td>MUDr. Roman Jíra</td><td>14 %</td><td>840 000 Kč</td><td>350 000 Kč</td><td>2 240 000 Kč</td></tr>
<tr><td>MUDr. Jan Voráč</td><td>13 %</td><td>780 000 Kč</td><td>325 000 Kč</td><td>2 080 000 Kč</td></tr>
<tr><td>Ing. Josef Kolařík</td><td>13 %</td><td>780 000 Kč</td><td>325 000 Kč</td><td>2 080 000 Kč</td></tr>
<tr><td>Ing. Kamila Vrtišková</td><td>8 %</td><td>480 000 Kč</td><td>200 000 Kč</td><td>1 280 000 Kč</td></tr>
</tbody></table>
<p><strong>Důležitá hranice důkazu:</strong> zveřejněná smlouva dokládá sjednanou cenu a splatnost, nikoli sama o sobě skutečné provedení všech plateb. K tomu jsou potřeba účetní nebo bankovní doklady nemocnice.</p>'''
text = text.replace(old_jiste, new_jiste)

text = text.replace(
    '<tr><td>23. 5. 2024</td><td>Smlouva zveřejněna v registru smluv bez uvedené hodnoty.</td></tr>',
    '<tr><td>23. 5. 2024</td><td>Smlouva zveřejněna v Registru smluv. Metadata hodnotu neuvádějí, přiložené PDF však stanoví kupní cenu na 16 milionů korun a obsahuje splátkový kalendář.</td></tr>'
)

text = text.replace(
    '<li>Úplná smlouva o převodu všech podílů včetně příloh a přesného splátkového kalendáře.</li>',
    '<li>Účetní nebo bankovní doklady o skutečném provedení jednotlivých plateb podle zveřejněného splátkového kalendáře.</li>'
)

text = text.replace(
    '<li><strong>Nemocnici:</strong> Kolik bylo dosud skutečně zaplaceno prodávajícím a proč není kupní cena uvedena v metadatech registru smluv?</li>',
    '<li><strong>Nemocnici:</strong> Které z pěti smluvních plateb byly dosud skutečně uhrazeny, v jakých datech a z jakých účtů?</li>'
)

text = text.replace(
    '<p>Nemocnice Kadaň zaplatila podle shodných veřejných vyjádření za ARC-MED 16 milionů korun. Současné vedení tvrdí, že cena výrazně převyšovala tržní hodnotu, a věc předalo policii. Bývalý jednatel se brání strategickou hodnotou firmy, informováním města a tvrzenými dodatečnými příjmy.</p>',
    '<p>Zveřejněná smlouva výslovně stanoví kupní cenu ARC-MED na 16 milionů korun a rozděluje ji do pěti plateb mezi pět prodávajících. Současné vedení tvrdí, že tato cena výrazně převyšovala tržní hodnotu, a věc předalo policii. Bývalý jednatel se brání strategickou hodnotou firmy, informováním města a tvrzenými dodatečnými příjmy.</p>'
)

text = text.replace(
    '<p>Veřejné dokumenty potvrzují, že nákup a fúze proběhly rychle a že rada města o záměru podle obou verzí věděla. Zatím ale neukazují úplný ekonomický výpočet ani jednoznačné schválení konkrétní ceny. Proto dnes nelze poctivě rozhodnout, zda nemocnice koupila předraženou firmu, nebo zda zaplatila za strategický provoz, jehož přínosy nebyly veřejnosti úplně vysvětleny.</p>',
    '<p>Veřejná smlouva už jasně ukazuje sjednanou cenu i mechanismus její úhrady. Nadále ale chybí úplné podklady k ocenění, účetní doklady k provedeným platbám a jednoznačný veřejný dokument, který by před podpisem zachycoval schválení konkrétní ceny. Proto dnes nelze poctivě rozhodnout, zda nemocnice koupila předraženou firmu, nebo zda zaplatila za strategický provoz, jehož přínosy nebyly veřejnosti úplně vysvětleny.</p>'
)

text = text.replace(
    '<p class="note">Článek odděluje ověřitelné dokumenty od tvrzení jednotlivých stran. Částky uváděné pouze účastníky sporu nejsou prezentovány jako nezávisle potvrzené.</p>',
    '<p class="note">Článek odděluje ověřitelné dokumenty od tvrzení jednotlivých stran. Kupní cena 16 milionů korun a její splátkový kalendář jsou potvrzeny zveřejněnou smlouvou; částky uváděné pouze účastníky sporu bez účetního či jiného dokladu jako nezávisle potvrzené neprezentujeme.</p>'
)

text = text.replace(
    '<div class="sidebox"><h3>Nejsilnější bod</h3><p>Veřejné dokumenty zatím nerozhodují spor mezi tržní a investiční hodnotou ani otázku schválení ceny.</p></div>',
    '<div class="sidebox"><h3>Nejsilnější bod</h3><p>Smlouva potvrzuje 16milionovou cenu i pět splátek. Otevřená zůstává přiměřenost ceny, skutečně provedené platby a způsob schválení transakce.</p></div>'
)

# Stejná struktura jako u ostatních článků.
text = re.sub(r'<article(?![^>]*class=)>', '<article class="article">', text, count=1)
text = re.sub(r'<article\s+class="(?![^"]*\barticle\b)([^"]*)">', r'<article class="article \1">', text, count=1)

# Odstranit návrhové formulace.
text = re.sub(r'\s*<div class="sidebox"><h3>Pracovní verze</h3>.*?</div>', '', text, count=1, flags=re.S)
text = text.replace('Pracovní text odděluje ověřitelné dokumenty od tvrzení jednotlivých stran.', 'Článek odděluje ověřitelné dokumenty od tvrzení jednotlivých stran.')
text = text.replace(' Před zveřejněním doporučujeme zaslat dotazy nemocnici, městu, Petru Hossnerovi a bývalým vlastníkům ARC-MED.', '')

# Pevný statický systém nesmí v článku zůstat.
text = re.sub(r'<style id="static-article-ads-style">.*?</style>\s*', '', text, flags=re.S)
text = re.sub(r'<div class="static-article-ads".*?</div>', '', text, flags=re.S)
text = re.sub(r'<div class="article-aside-tower".*?</div>', '', text, flags=re.S)

# Standardní dynamická reklamní pozice v pravém sloupci.
text = re.sub(r'<div\s+data-promos\s+data-context="sidebar"[^>]*>.*?</div>', '', text, flags=re.S)
text = text.replace('</aside>', '  <div data-promos data-context="sidebar"></div>\n</aside>', 1)

# Datum publikace zůstává původní, datum změny odpovídá redakční opravě.
published = '2026-07-28T05:00:00+02:00'
modified = '2026-08-08T07:06:00+02:00'
if 'article:published_time' not in text:
    text = text.replace('</head>', f'  <meta property="article:published_time" content="{published}">\n  <meta property="article:modified_time" content="{modified}">\n</head>', 1)
else:
    text = re.sub(r'(<meta property="article:published_time" content=")[^"]+', r'\g<1>' + published, text)
    text = re.sub(r'(<meta property="article:modified_time" content=")[^"]+', r'\g<1>' + modified, text)

pattern = r'(<script type="application/ld\+json">)(.*?)(</script>)'
def update_json(match: re.Match[str]) -> str:
    try:
        data = json.loads(match.group(2))
    except json.JSONDecodeError:
        return match.group(0)
    if isinstance(data, dict) and data.get('@type') == 'NewsArticle':
        data['description'] = new_desc
        data['datePublished'] = published
        data['dateModified'] = modified
    return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + match.group(3)
text = re.sub(pattern, update_json, text, count=1, flags=re.S)

# Jediný správný reklamní systém: reklamy.js + proud různých nabídek vpravo.
for script_name in ('reklamy.js?v=20260728-vaseuklizecka-guaranteed-3', 'reklamy-sidebar.js', 'reklamy-oprava-obrazku.js', 'obsah-doplnky.js'):
    text = re.sub(rf'\s*<script[^>]+src="/{re.escape(script_name)}[^>]*></script>', '', text)

scripts = '''
<script src="/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3"></script>
<script src="/reklamy-sidebar.js?v=20260728-adstream-4"></script>
<script src="/reklamy-oprava-obrazku.js?v=20260728-dynamic-2"></script>
<script src="/obsah-doplnky.js?v=20260728-dynamic-2"></script>
'''
text = text.replace('</body>', scripts + '</body>', 1)

# Povinné kontroly, včetně redakční opravy z 8. 8. 2026.
assert 'noindex' not in text
assert 'PŘIPRAVOVANÝ ČLÁNEK' not in text
assert 'Pracovní verze' not in text
assert 'static-article-ads' not in text
assert '<article class="article">' in text
assert '<div data-promos data-context="sidebar"></div>' in text
assert '/reklamy.js?v=20260728-vaseuklizecka-guaranteed-3' in text
assert '/reklamy-sidebar.js?' in text
assert 'data-arc-med-correction="2026-08-08"' in text
assert '16&nbsp;000&nbsp;000 Kč' in text
assert 'MUDr. Zora Ouzká' in text
assert 'Úplná smlouva o převodu všech podílů včetně příloh a přesného splátkového kalendáře.' not in text
assert 'veřejný záznam proto sám o sobě nepotvrzuje částku 16 milionů korun' not in text

path.write_text(text, encoding='utf-8', newline='\n')
print('ARC-MED opraven podle zveřejněné smlouvy a sjednocen s dynamickým reklamním proudem.')
