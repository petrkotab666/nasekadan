#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "epetice-nemocnice-kadan.html"
PRIVATE_URL = "https://e-petice.cz/en/petitions/petice-za-zachovani-nemocnice-kadan-s-r-o-ve-vlastnictvi-mesta.html"
OLD_TITLE = "Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná"
NEW_TITLE = "Online petice za nemocnici byla spuštěna. Nejde ale o státní ePetici"
OLD_DESCRIPTION = "Předkladatelka petice za Nemocnici Kadaň připravuje ePetici. Vysvětlujeme limit 3500 znaků, totožnost obou verzí, ověřené podpisy i právní účinky."
NEW_DESCRIPTION = "Online petice za zachování Nemocnice Kadaň byla spuštěna na soukromém portálu e-petice.cz. Vysvětlujeme rozdíl proti státní ePetici s ověřenou Identitou občana."
MODIFIED = "2026-07-27T14:00:00+02:00"


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_article() -> None:
    if not ARTICLE.exists():
        return
    text = ARTICLE.read_text(encoding="utf-8")

    replacements = {
        f"<title>{OLD_TITLE} | Naše Kadaň</title>": f"<title>{NEW_TITLE} | Naše Kadaň</title>",
        f'<meta name="description" content="{OLD_DESCRIPTION}">': f'<meta name="description" content="{NEW_DESCRIPTION}">',
        f'<meta property="og:title" content="{OLD_TITLE}">': f'<meta property="og:title" content="{NEW_TITLE}">',
        '<meta property="og:description" content="Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze sčítat elektronické a listinné podpisy.">': '<meta property="og:description" content="Online sběr podpisů běží na soukromém portálu e-petice.cz, nikoli ve státním systému ePetice v Portálu občana.">',
        '<p class="tag">MIMOŘÁDNĚ · NEMOCNICE KADAŇ · PETICE · 26. ČERVENCE 2026</p>': '<p class="tag">AKTUALIZOVÁNO · NEMOCNICE KADAŇ · ONLINE PETICE · 27. ČERVENCE 2026</p>',
        f"<h1>{OLD_TITLE}</h1>": f"<h1>{NEW_TITLE}</h1>",
        '<p class="leadtext">Předkladatelka petice za zachování Nemocnice Kadaň ve vlastnictví města oznámila přípravu oficiální ePetice. Narazila přitom na limit 3500 znaků a uvedla, že čeká na její schválení. Vysvětlujeme, jak státní systém skutečně funguje a proč je zásadní, aby elektronická a listinná verze měly totožný text.</p>': '<p class="leadtext">Veřejný online sběr podpisů za zachování Nemocnice Kadaň ve vlastnictví města byl spuštěn. Odkaz ale nevede do státní služby ePetice v Portálu občana, nýbrž na soukromý server e-petice.cz. Podpis na tomto webu proto není totéž jako podpis ověřený Identitou občana a výsledky nelze automaticky vydávat za státní ePetici.</p>',
        '<div class="hero-visual"><strong><span class="hero-kicker">Mimořádné vysvětlení pravidel</span>Elektronická petice může zapojení občanů usnadnit. Zkrácení textu ale nesmí změnit to, co lidé svým podpisem podporují.</strong></div>': '<div class="hero-visual"><strong><span class="hero-kicker">Důležité rozlišení</span>Online petice je veřejná a lze ji podepsat. Nejde však o státní ePetici s podpisem ověřeným prostřednictvím Identity občana.</strong></div>',
        '<div class="status-box"><b>Stav při zveřejnění článku:</b> K 26. červenci 2026 v 10:11 nebyla petice za Nemocnici Kadaň ve veřejně dostupném seznamu oficiálních ePetic dohledatelná. Jakmile se objeví, porovnáme její úplné znění s listinnou verzí a článek aktualizujeme.</div>': f'<div class="status-box"><b>Aktuální stav:</b> Online petice byla zveřejněna na soukromém portálu <a href="{PRIVATE_URL}" target="_blank" rel="noopener noreferrer">e-petice.cz</a>. Ve veřejném seznamu státních ePetic v Portálu občana jsme ji jako státní ePetici nepotvrdili. Jde o dva rozdílné systémy s rozdílným způsobem ověřování podpisů.</div>',
        '<div class="numbers"><div><b>3500 znaků</b><span>nejvyšší délka vlastního textu ePetice</span></div><div><b>Totožný text</b><span>podmínka pro kombinaci listinného a elektronického sběru</span></div><div><b>Identita občana</b><span>podpis je spojen s ověřeným uživatelem</span></div><div><b>30 dnů</b><span>lhůta pro písemnou odpověď po podání petice</span></div></div>': '<div class="numbers"><div><b>Soukromý portál</b><span>online sběr běží na webu e-petice.cz</span></div><div><b>Bez Identity občana</b><span>nejde o podpis ve státní službě ePetice</span></div><div><b>Oddělené součty</b><span>podpisy nelze automaticky sčítat jako jednu ověřenou ePetici</span></div><div><b>Veřejný odkaz</b><span>petici lze nyní sdílet a podepisovat online</span></div></div>',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace(
        '<div class="toc"><strong>Co v článku vysvětlujeme</strong><ol>',
        '<div class="toc"><strong>Co v článku vysvětlujeme</strong><ol><li><a href="#soukromy-portal">Proč nejde o státní ePetici</a></li>',
        1,
    )

    announcement_pattern = re.compile(
        r'<h2 id="oznameni">Předkladatelka oznámila souběžnou ePetici</h2>.*?'
        r'<p>Možnost podpisu na dálku může petici významně rozšířit\..*?</p>',
        re.S,
    )
    announcement = f'''<h2 id="oznameni">Předkladatelka oznámila spuštění online petice</h2>
  <p>Vlasta Štaubrová na svém veřejném facebookovém profilu oznámila, že online petice byla spuštěna, a zveřejnila odkaz na stránku <a href="{PRIVATE_URL}" target="_blank" rel="noopener noreferrer">„Petice za zachování Nemocnice Kadaň s.r.o. ve vlastnictví města“</a>.</p>
  <blockquote>„Povedlo se, e-petice byla spuštěna.“</blockquote>
  <p>Online sběr tak skutečně začal. Zveřejněný odkaz však nevede na Portál občana ani na Portál veřejné správy. Vede na soukromou petiční platformu e-petice.cz.</p>'''
    text = announcement_pattern.sub(announcement, text, count=1)

    if 'id="soukromy-portal"' not in text:
        marker = '<h2 id="plne-zneni">'
        section = f'''<h2 id="soukromy-portal">e-petice.cz není státní ePetice v Portálu občana</h2>
  <p>Podobnost názvů může být matoucí. Státní služba se jmenuje <strong>ePetice</strong> a funguje uvnitř Portálu občana. Podepsat ji lze pouze po přihlášení prostřednictvím Identity občana. Stát tuto službu označuje za jedinou státem uznávanou formu elektronické petice a každý podpis je spojen s ověřenou osobou.</p>
  <p>Web <strong>e-petice.cz</strong> provozuje spolek NÁŠ HLAS NAHLAS, z.s. Jde o soukromou platformu. Podle jejích podmínek podepisující vyplňuje jméno, příjmení, bydliště a e-mail, nejde ale o přihlášení Identitou občana ani o podpis ve státním systému.</p>
  <div class="callout"><strong>Online podpora ano, státní ePetice ne</strong>Podpisy na soukromém webu mohou ukázat veřejnou podporu a mohou být předkladatelkou následně využity při podání petice. Nelze je však automaticky označovat za ověřené podpisy státní ePetice ani je bez dalšího sčítat s podpisy v Portálu občana.</div>
  <p>Veřejně doložené je nyní spuštění online sběru na soukromém portálu. Veřejně doložené naopak není, že byla stejná petice založena také ve státní službě ePetice v Portálu občana.</p>

  <h2 id="plne-zneni">'''
        text = text.replace(marker, section, 1)

    text = re.sub(
        r'<div class="status-box"><b>Co dokládají snímky z Portálu občana:</b>.*?</div>',
        '<div class="status-box"><b>Co se změnilo:</b> Původní pokus o založení státní ePetice v Portálu občana narazil na limit textu. Nyní byla spuštěna petice na jiné, soukromé platformě. Tím se problém limitu 3500 znaků obešel, ale současně se změnil způsob ověřování podpisů a jejich právní režim.</div>',
        text,
        count=1,
        flags=re.S,
    )

    text = re.sub(
        r'<h2 id="schvaleni">Oficiální postup standardní „schvalování“ nepopisuje</h2>.*?'
        r'<p>Po zveřejnění už navíc text nelze běžně editovat\..*?</p>',
        '''<h2 id="schvaleni">Soukromý portál používá jiný postup než Portál občana</h2>
  <p>Dřívější zmínka o čekání na „schválení“ souvisela podle zveřejněných snímků s pokusem použít Portál občana. Aktuální odkaz ale směřuje na jinou službu. Zveřejnění na e-petice.cz proto nepotvrzuje, že byl dokončen původní proces ve státním systému.</p>
  <p>Státní ePetice se po založení zveřejňuje na Portálu veřejné správy a podepisuje v Portálu občana. Soukromý web má vlastní registrační a publikační pravidla.</p>''',
        text,
        count=1,
        flags=re.S,
    )

    text = re.sub(
        r'<h2 id="podepsani">Elektronický podpis není anonymní kliknutí</h2>.*?'
        r'<p>Veřejně je dostupný text petice a počet podporovatelů, nikoli osobní údaje jednotlivých podepsaných\..*?</p>',
        '''<h2 id="podepsani">Jaký je rozdíl při podepisování</h2>
  <p>Státní ePetici lze podepsat jen po přihlášení do Portálu občana prostřednictvím Identity občana. Tím je jednoznačně ověřeno, kdo podporu připojil, a systém brání duplicitním podpisům.</p>
  <p>Na soukromém portálu e-petice.cz podepisující vyplňuje osobní údaje prostřednictvím formuláře provozovatele. Nejde o státní ověření totožnosti. Počet podpisů zobrazený na soukromém portálu proto musí být popisován jako počet podporovatelů na této platformě, nikoli jako počet ověřených podpisů státní ePetice.</p>''',
        text,
        count=1,
        flags=re.S,
    )

    text = text.replace(
        '<p>Řádně podaná ePetice je z hlediska petičního zákona srovnatelná s listinnou peticí. Adresovaný orgán je povinen ji přijmout, posoudit a do 30 dnů písemně sdělit své stanovisko a způsob vyřízení.</p>',
        '<p>Plnou zákonnou rovnocennost s listinnou peticí stát výslovně přiznává své službě ePetice v Portálu občana. U podpisů získaných na soukromé platformě bude záležet na tom, v jaké podobě, s jakými údaji a jakým způsobem je předkladatelka následně předá adresátovi. Samotné zveřejnění stránky na e-petice.cz ještě automaticky nevytváří státní ePetici.</p>',
    )

    tracking_pattern = re.compile(
        r'<h2 id="sledovani">Jak budeme pokračovat</h2>.*?'
        r'<p>Pokud budou texty totožné,.*?</p>',
        re.S,
    )
    tracking = f'''<h2 id="sledovani">Co budeme dál sledovat</h2>
  <p>Naše Kadaň bude sledovat samostatně soukromou online petici, případnou státní ePetici v Portálu občana a listinný sběr.</p>
  <p>U zveřejněné petice na e-petice.cz budeme kontrolovat zejména úplné znění, veřejný počet podporovatelů, případné změny a informaci o jejím předání městu. Současně budeme ověřovat, zda se petice neobjeví také v oficiálním seznamu státních ePetic.</p>
  <p>Přímý odkaz k podpisu na soukromém portálu je dostupný <a href="{PRIVATE_URL}" target="_blank" rel="noopener noreferrer">zde</a>.</p>'''
    text = tracking_pattern.sub(tracking, text, count=1)

    text = text.replace(
        '<h2>Elektronická petice může pomoci, pravidla ale musí být jasná</h2>',
        '<h2>Online petice běží. Její typ je ale nutné pojmenovat přesně</h2>',
    )
    text = text.replace(
        '<p>Přesun petice do oficiálního elektronického systému je legitimní a pro občany pohodlný krok. Může se zapojit více lidí a každý podpis je ověřený.</p>',
        '<p>Spuštění online sběru usnadní zapojení veřejnosti a umožní petici rychle sdílet. Podpisy na zveřejněném odkazu ale nejsou podpisy v oficiálním elektronickém systému státu.</p>',
    )
    text = text.replace(
        '<p>Právě proto však musí být před zahájením elektronického sběru jednoznačné, co občan podepisuje a zda je to skutečně stejný text jako na již používaných papírových arších.</p>',
        '<p>Pro další hodnocení bude důležité porovnat úplné znění online a listinné verze a odděleně uvádět počty podpisů z každého způsobu sběru.</p>',
    )
    text = text.replace(
        '<blockquote>Zkrátit vysvětlení lze. Změnit požadavky a automaticky k nim přičíst starší podpisy pod jiným textem by ale nebylo správné.</blockquote>',
        '<blockquote>Petici lze podepsat online. Není však správné zaměňovat soukromý podpisový portál za státní ePetici s ověřenou Identitou občana.</blockquote>',
    )

    source_marker = '<div class="source-list"><h2>Zdroje a metodika</h2><ul>'
    if PRIVATE_URL not in text and source_marker in text:
        source_add = (
            f'<li><a href="{PRIVATE_URL}" target="_blank" rel="noopener noreferrer">Veřejná online petice za zachování Nemocnice Kadaň na soukromém portálu e-petice.cz</a></li>'
            '<li><a href="https://e-petice.cz/info/o-nas/" target="_blank" rel="noopener noreferrer">e-petice.cz: informace o provozovateli NÁŠ HLAS NAHLAS, z.s.</a></li>'
            '<li><a href="https://e-petice.cz/podminky-serveru/" target="_blank" rel="noopener noreferrer">e-petice.cz: podmínky serveru a údaje vyžadované při podpisu</a></li>'
        )
        text = text.replace(source_marker, source_marker + source_add, 1)
    text = re.sub(
        r'<small>Veřejný seznam ePetic byl kontrolován.*?</small>',
        '<small>Aktualizováno 27. 7. 2026 po zveřejnění odkazu na soukromou platformu e-petice.cz. Článek důsledně rozlišuje tuto službu od státní ePetice v Portálu občana.</small>',
        text,
        count=1,
        flags=re.S,
    )

    text = re.sub(
        r'<aside class="sticky"><div class="sidebox"><h3>Stav článku</h3>.*?<div data-promos',
        f'''<aside class="sticky"><div class="sidebox"><h3>Aktuální stav</h3><p class="updated">Aktualizováno: 27. 7. 2026</p><p>Online petice je spuštěná na soukromém portálu e-petice.cz.</p><p><a href="{PRIVATE_URL}" target="_blank" rel="noopener noreferrer">Otevřít petici →</a></p></div><div class="sidebox"><h3>Důležité rozlišení</h3><p><strong>e-petice.cz není státní služba ePetice v Portálu občana.</strong></p></div><div class="sidebox"><h3>Co dál ověřujeme</h3><p>Porovnáme úplné znění s listinnou peticí a budeme sledovat případné podání městu.</p></div>
  <div data-promos''',
        text,
        count=1,
        flags=re.S,
    )

    # Update NewsArticle JSON-LD without relying on exact formatting.
    def update_schema(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        if data.get("@type") == "NewsArticle":
            data["headline"] = NEW_TITLE
            data["description"] = NEW_DESCRIPTION
            data["dateModified"] = MODIFIED
            data["image"] = "https://nasekadan.cz/social/epetice-nemocnice-kadan-71560a0788.png"
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"

    text = re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        update_schema,
        text,
        count=1,
        flags=re.S,
    )
    write(ARTICLE, text)


def update_other_files() -> None:
    old_card_description = "Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze spojit elektronické a listinné podpisy."
    new_card_description = "Online sběr podpisů byl spuštěn na soukromém portálu e-petice.cz, nikoli ve státním systému Portálu občana."
    files = [
        ROOT / "index.html",
        ROOT / "clanky" / "index.html",
        ROOT / "rss.xml",
        ROOT / "news-sitemap.xml",
        ROOT / "llms.txt",
        ROOT / "site.js",
    ]
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(OLD_TITLE, NEW_TITLE)
        text = text.replace("Petice za nemocnici míří online. Obě verze ale musí být stejné", "Online petice běží. Nejde ale o státní ePetici")
        text = text.replace("Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze sčítat elektronické a listinné podpisy.", new_card_description)
        text = text.replace(old_card_description, new_card_description)
        text = text.replace("Vysvětlujeme limit 3500 znaků, pravidla kombinovaného sběru podpisů a skutečný postup zveřejnění ePetice.", new_card_description)
        if path.name == "site.js":
            text = text.replace(
                "<b>Stav při poslední kontrole:</b> K 26. červenci 2026 ve 13:27 nebyla petice za Nemocnici Kadaň ve veřejně dostupném seznamu oficiálních ePetic dohledatelná. Jakmile se objeví, porovnáme její úplné znění s listinnou verzí a článek aktualizujeme.",
                f'<b>Aktuální stav:</b> Online petice byla spuštěna na soukromém portálu <a href="{PRIVATE_URL}" target="_blank" rel="noopener noreferrer">e-petice.cz</a>. Nejde o státní ePetici v Portálu občana.',
            )
            text = text.replace("2026-07-26T13:27:00+02:00", MODIFIED)
        write(path, text)


def main() -> int:
    update_article()
    update_other_files()
    print("Článek o online petici byl aktualizován a soukromý portál byl odlišen od státní ePetice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
