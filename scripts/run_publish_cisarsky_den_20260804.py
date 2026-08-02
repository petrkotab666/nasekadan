#!/usr/bin/env python3
"""Bezpečný spouštěč publikace Císařského dne.

Pro jediný publikační běh doplní potvrzené bezplatné vstupné a nahradí
starší ochranu titulky obecnou kontrolou zachování všech současných karet.
Zdrojový návrh zůstává neveřejný a beze změny.
"""
from pathlib import Path
import re

TARGET = Path(__file__).with_name('publish_cisarsky_den_20260804.py')
ROOT = TARGET.resolve().parents[1]
INDEX = ROOT / 'index.html'
EXPECTED_REL = '/clanky/cisarsky-den-kadan-historie-2026.html'


def patch_source(source: str) -> str:
    replacements = [
        (
            "DESC = 'Císařský den 2026 v Kadani se koná 22. srpna od 10 do 22 hodin. Přinášíme potvrzené časy, praktické informace a velký příběh města od Karla IV. po současnost.'",
            "DESC = 'Císařský den 2026 v Kadani se koná 22. srpna od 10 do 22 hodin a vstup je zdarma. Přinášíme potvrzené časy, praktické informace a velký příběh města od Karla IV. po současnost.'",
        ),
        (
            '<span class="status-badge">POTVRZENO POŘADATELEM</span><h2 id="quickTitle">Císařský den 2026 – rychlý přehled</h2><p>Sobota 22. srpna 2026 · historické centrum Kadaně · 10:00–22:00</p>',
            '<span class="status-badge">POTVRZENO POŘADATELEM</span><h2 id="quickTitle">Císařský den 2026 – rychlý přehled</h2><p>Sobota 22. srpna 2026 · historické centrum Kadaně · 10:00–22:00 · vstup zdarma</p>',
        ),
        (
            '<p class="quick-note"><strong>Potvrzený rámec dne:</strong> Kulturní zařízení Kadaň uvádí konání od 10 do 22 hodin. Úplný rozpis všech scén a vystoupení zatím zveřejněn nebyl.</p>',
            '<p class="quick-note"><strong>Potvrzený rámec dne:</strong> Kulturní zařízení Kadaň uvádí konání od 10 do 22 hodin a vstup zdarma. Úplný rozpis všech scén a vystoupení zatím zveřejněn nebyl.</p>',
        ),
        (
            '<article class="fact-box confirmed"><b>POTVRZENO PRO ROK 2026</b><p>Datum, čas 10:00–22:00, 34. ročník a tři hlavní časy.</p></article>',
            '<article class="fact-box confirmed"><b>POTVRZENO PRO ROK 2026</b><p>Datum, čas 10:00–22:00, vstup zdarma, 34. ročník a tři hlavní časy.</p></article>',
        ),
        (
            '<article class="fact-box waiting"><b>ČEKÁME NA ZVEŘEJNĚNÍ</b><p>Podrobný harmonogram, mapa, parkování, uzavírky, zvláštní doprava, vstupné a změny kvůli počasí.</p></article>',
            '<article class="fact-box waiting"><b>ČEKÁME NA ZVEŘEJNĚNÍ</b><p>Podrobný harmonogram, mapa, parkování, uzavírky, zvláštní doprava a změny kvůli počasí.</p></article>',
        ),
        (
            '<article><h3>Vstupné</h3><p>Pro rok 2026 zatím nemáme potvrzené podmínky.</p></article>',
            '<article><h3>Vstupné</h3><p><strong>Vstup je zdarma.</strong></p></article>',
        ),
        (
            "required=[TITLE,'10:00–22:00','14:00','14:30','18:00',URL,IMAGE_URL,'NewsArticle','index,follow,max-image-preview:large','Hru spustíme 12. srpna v 18:00']",
            "required=[TITLE,'10:00–22:00','vstup zdarma','14:00','14:30','18:00',URL,IMAGE_URL,'NewsArticle','index,follow,max-image-preview:large','Hru spustíme 12. srpna v 18:00']",
        ),
        (
            "forbidden=['PŘIPRAVOVANÝ ČLÁNEK','Stav návrhu','vstup zdarma','href=\"/hry/prijezd-karla-iv/\"']",
            "forbidden=['PŘIPRAVOVANÝ ČLÁNEK','Stav návrhu','href=\"/hry/prijezd-karla-iv/\"']",
        ),
        (
            "draw.rounded_rectangle((310,545,525,595),radius=18,fill=gold); draw.text((334,556),'10:00–22:00',font=ImageFont.truetype(bold,23),fill=(45,27,29))",
            "draw.rounded_rectangle((310,545,525,595),radius=18,fill=gold); draw.text((334,556),'10:00–22:00',font=ImageFont.truetype(bold,23),fill=(45,27,29)); draw.rounded_rectangle((545,545,805,595),radius=18,fill=burg); draw.text((568,556),'VSTUP ZDARMA',font=ImageFont.truetype(bold,21),fill='white')",
        ),
    ]
    for old, new in replacements:
        if source.count(old) != 1:
            raise SystemExit(f'Bezpečný spouštěč nenašel právě jeden očekávaný řetězec: {old[:80]}')
        source = source.replace(old, new, 1)

    old_sequence = """    write(ARTICLE,build_article()); social_image(); update_home(); update_archive(); update_feeds()
    protector=ROOT/'scripts/ensure_recent_home_articles_20260801.py'
    if protector.exists(): subprocess.run(['python3',str(protector)],check=True,cwd=ROOT)
    validate()
"""
    new_sequence = """    write(ARTICLE,build_article()); social_image(); update_home(); update_archive(); update_feeds()
    validate()
"""
    if source.count(old_sequence) != 1:
        raise SystemExit('Bezpečný spouštěč nenašel právě jednu očekávanou publikační sekvenci.')
    return source.replace(old_sequence, new_sequence, 1)


def main() -> None:
    before = INDEX.read_text(encoding='utf-8')
    before_cards = re.findall(r'data-auto-article="([^"]+)"', before)
    if len(before_cards) != len(set(before_cards)):
        raise SystemExit('Titulka obsahuje duplicitní automatické karty ještě před publikací.')

    patched = patch_source(TARGET.read_text(encoding='utf-8'))
    namespace = {'__name__': '__main__', '__file__': str(TARGET)}
    exec(compile(patched, str(TARGET), 'exec'), namespace)

    after = INDEX.read_text(encoding='utf-8')
    after_cards = re.findall(r'data-auto-article="([^"]+)"', after)
    missing_cards = sorted(set(before_cards) - set(after_cards))
    if missing_cards:
        raise SystemExit(f'Publikace odstranila existující karty titulky: {missing_cards}')
    if len(after_cards) != len(set(after_cards)):
        raise SystemExit('Publikace vytvořila duplicitní automatické karty titulky.')
    if f'data-latest-article-href="{EXPECTED_REL}"' not in after:
        raise SystemExit('Titulka nemá nový článek v atributu data-latest-article-href.')
    if after.count(f'href="{EXPECTED_REL}"') < 1:
        raise SystemExit('Titulka neobsahuje odkaz na nový článek.')
    if '<div class="article-list">' not in after:
        raise SystemExit('Publikace poškodila seznam článků na titulce.')

    print('Nezávislá kontrola integrity titulní stránky prošla.')


if __name__ == '__main__':
    main()
