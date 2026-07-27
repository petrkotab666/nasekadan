#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "clanky" / "epetice-nemocnice-kadan.html"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Nenalezena očekávaná část: {label}")
    return text.replace(old, new, 1)


def main() -> int:
    text = PATH.read_text(encoding="utf-8")

    replacements = [
        (
            "Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná | Naše Kadaň",
            "Petice za nemocnici je online na soukromém portálu. Co to mění | Naše Kadaň",
            "title",
        ),
        (
            "Předkladatelka petice za Nemocnici Kadaň připravuje ePetici. Vysvětlujeme limit 3500 znaků, totožnost obou verzí, ověřené podpisy i právní účinky.",
            "Petice za Nemocnici Kadaň je zveřejněna na soukromém portálu e-petice.cz. Vysvětlujeme rozdíl proti státní ePetici, způsob potvrzení podpory a právní účinky.",
            "description",
        ),
        (
            "Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná",
            "Petice za nemocnici je online na soukromém portálu. Co to mění",
            "og title a h1",
        ),
        (
            "Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze sčítat elektronické a listinné podpisy.",
            "Petice běží na e-petice.cz, nikoli ve státním nástroji. Co soukromá platforma ověřuje a jaké účinky mají její online podpory.",
            "og description",
        ),
        (
            ".hero-visual:after{content:'3500';",
            ".hero-visual:after{content:'ONLINE';",
            "hero label",
        ),
        (
            '"headline":"Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná"',
            '"headline":"Petice za nemocnici je online na soukromém portálu. Co to mění"',
            "json headline",
        ),
        (
            '"description":"Předkladatelka petice za Nemocnici Kadaň připravuje ePetici. Vysvětlujeme limit 3500 znaků, totožnost obou verzí, ověřené podpisy i právní účinky."',
            '"description":"Petice za Nemocnici Kadaň je zveřejněna na soukromém portálu e-petice.cz. Vysvětlujeme rozdíl proti státní ePetici, způsob potvrzení podpory a právní účinky."',
            "json description",
        ),
        (
            '<p class="tag">MIMOŘÁDNĚ · NEMOCNICE KADAŇ · PETICE · AKTUALIZOVÁNO 27. ČERVENCE 2026</p>',
            '<p class="tag">NEMOCNICE KADAŇ · PETICE · AKTUALIZOVÁNO 27. ČERVENCE 2026</p>',
            "tag",
        ),
        (
            '<p class="leadtext">Předkladatelka petice za zachování Nemocnice Kadaň ve vlastnictví města oznámila přípravu oficiální ePetice. Po původním zveřejnění článku doplnila fotografie celého listinného znění a snímky rozpracovaného formuláře. Nové podklady ukázaly osm konkrétních požadavků i problém s limitem 3500 znaků. Vysvětlujeme, co tato aktualizace mění a proč je zásadní, aby elektronická a listinná verze měly totožný text.</p>',
            '<p class="leadtext">Petice za zachování Nemocnice Kadaň ve vlastnictví města je nyní veřejně dostupná na soukromém portálu e-petice.cz. Nejde o státní nástroj ePetice na Portálu občana. Podpis se proto nepotvrzuje Identitou občana a na současný sběr se automaticky nevztahuje limit 3500 znaků ani technická pravidla státního systému. Vysvětlujeme, co soukromá platforma skutečně ověřuje, jak souvisí s listinnými archy a co lze bezpečně tvrdit o právních účincích nasbíraných podpor.</p>',
            "lead",
        ),
        (
            '<div class="hero-visual"><strong><span class="hero-kicker">Mimořádné vysvětlení pravidel</span>Elektronická petice může zapojení občanů usnadnit. Zkrácení textu ale nesmí změnit to, co lidé svým podpisem podporují.</strong></div>',
            '<div class="hero-visual"><strong><span class="hero-kicker">Soukromý portál, nikoli státní ePetice</span>Online sběr může zapojit více lidí. Je ale nutné přesně rozlišit potvrzenou podporu na soukromém webu od podpisu ověřeného státním nástrojem.</strong></div>',
            "hero",
        ),
        (
            '<div class="status-box"><b>Co se změnilo po původním zveřejnění:</b> Článek vyšel 26. července v 10:15, kdy veřejný odkaz na ePetici nebyl dohledatelný. Později předkladatelka zveřejnila celé listinné znění a snímky rozpracovaného formuláře. Díky nim už lze přesně popsat osm požadavků i místo, kde formulář narazil na limit. Veřejně otevřenou ePetici jsme při aktualizaci 27. července stále nedohledali.</div>',
            '<div class="status-box"><b>Aktuální stav:</b> Veřejná online verze už existuje na e-petice.cz a obsahuje všech osm požadavků listinné petice. Platformu provozuje spolek NÁŠ HLAS NAHLAS, z.s.; nejde o Portál občana ani o elektronický nástroj Ministerstva vnitra podle § 6a petičního zákona. Původní snímky z Portálu občana proto dokládají pouze dřívější pokus založit státní ePetici, nikoli způsob, kterým dnes podpisy skutečně vznikají.</div>',
            "status",
        ),
        (
            '<div class="numbers"><div><b>3500 znaků</b><span>nejvyšší délka vlastního textu ePetice</span></div><div><b>Totožný text</b><span>podmínka pro kombinaci listinného a elektronického sběru</span></div><div><b>Identita občana</b><span>podpis je spojen s ověřeným uživatelem</span></div><div><b>30 dnů</b><span>lhůta pro písemnou odpověď po podání petice</span></div></div>',
            '<div class="numbers"><div><b>e-petice.cz</b><span>soukromá nezisková platforma, na níž nyní petice běží</span></div><div><b>E-mail</b><span>podpora se potvrzuje odkazem zaslaným na uvedenou adresu</span></div><div><b>Bez eIdentity</b><span>platforma nepoužívá Identitu občana ani státní ověření osoby</span></div><div><b>8 požadavků</b><span>online verze obsahuje stejné hlavní body jako listinný dokument</span></div></div>',
            "numbers",
        ),
        (
            '<div class="toc"><strong>Co v článku vysvětlujeme</strong><ol><li><a href="#oznameni">Původní oznámení ePetice</a></li><li><a href="#plne-zneni">Co přinesla pozdější aktualizace</a></li><li><a href="#limit">Jak funguje limit 3500 znaků</a></li><li><a href="#stejny-text">Proč musí být text totožný</a></li><li><a href="#podpisy">Co se stane s podpisy</a></li><li><a href="#schvaleni">Zda se ePetice schvaluje</a></li><li><a href="#podepsani">Jak se ePetice podepisuje</a></li><li><a href="#ucinky">Jaké má petice právní účinky</a></li><li><a href="#sledovani">Jak budeme pokračovat</a></li></ol></div>',
            '<div class="toc"><strong>Co v článku vysvětlujeme</strong><ol><li><a href="#oznameni">Jak se petice dostala online</a></li><li><a href="#plne-zneni">Co obsahuje veřejná verze</a></li><li><a href="#limit">Co platilo jen pro Portál občana</a></li><li><a href="#stejny-text">Proč je stále důležité znění</a></li><li><a href="#podpisy">Jak rozlišovat podpisy a online podpory</a></li><li><a href="#schvaleni">Jak funguje soukromý portál</a></li><li><a href="#podepsani">Jak se potvrzuje podpora</a></li><li><a href="#ucinky">Jaké jsou právní účinky</a></li><li><a href="#sledovani">Co budeme dál ověřovat</a></li></ol></div>',
            "toc",
        ),
        (
            '<h2 id="oznameni">Předkladatelka oznámila souběžnou ePetici</h2>',
            '<h2 id="oznameni">Původní pokus mířil na Portál občana, veřejná petice ale vznikla jinde</h2>',
            "announcement heading",
        ),
        (
            '<p>Možnost podpisu na dálku může petici významně rozšířit. Lidé nebudou muset vyhledávat fyzické petiční místo a systém současně ověří totožnost každého podporovatele. Před zveřejněním však musí být vyřešena otázka konečného znění.</p>',
            '<p>Původní příspěvek tak popisoval pokus použít státní ePetici na Portálu občana. Tento pokus narazil na limit 3500 znaků. K veřejnému sběru však nakonec nebyl použit státní systém, ale soukromý web e-petice.cz. Právě tato změna je pro posouzení podpisů a pravidel rozhodující.</p>',
            "announcement bridge",
        ),
        (
            '<h2 id="plne-zneni">Pozdější aktualizace ukázala celé znění listinné petice</h2>',
            '<h2 id="plne-zneni">Soukromá online verze zveřejnila celé znění petice</h2>',
            "full text heading",
        ),
        (
            '<p>Po původním zveřejnění tohoto článku předkladatelka doplnila další snímky. Poprvé tak bylo možné přečíst všech osm požadavků listinné petice a současně vidět rozpracovaný formulář ePetice. Aktualizace nemění pravidla elektronického sběru, ale zpřesňuje, jak rozsáhlý text se předkladatelka pokouší do systému převést.</p>',
            '<p>Na portálu e-petice.cz je nyní veřejně dostupný celý text. Obsahuje stejných osm hlavních požadavků, které byly zachyceny na listinných arších. Soukromá platforma tedy umožnila zveřejnit rozsáhlé znění bez limitu 3500 znaků, který platí pro formulář státní ePetice.</p>',
            "full text intro",
        ),
        (
            '<div class="status-box"><b>Co dokládají snímky z Portálu občana:</b> Ve formuláři ePetice se zobrazilo upozornění na překročení limitu 3500 znaků už ve chvíli, kdy byly ve viditelné části zadány pouze první tři požadavky. Další snímek dokládá založený nebo rozpracovaný záznam v části „Moje petice“. Sám o sobě ale ještě nepotvrzuje, že byla ePetice veřejně zveřejněna a otevřena k podpisu.</div>',
            '<div class="status-box"><b>Dvě různé platformy:</b> Snímky z Portálu občana dokazují rozpracovaný pokus o státní ePetici a problém s limitem 3500 znaků. Aktuální veřejný odkaz ale vede na e-petice.cz. Na tomto soukromém webu se podpisy nepotvrzují Identitou občana; portál podle svých podmínek vyžaduje osobní údaje a potvrzení odkazu doručeného e-mailem.</div>',
            "platform distinction",
        ),
        (
            '<p>Z nových podkladů tak vyplývá hlavní praktický problém: osmibodové listinné znění se do formuláře v dosavadní podobě nevešlo. Nejde jen o technické odstranění mezer. Rozhodující je, zda má vzniknout jedna společná petice s totožným textem, nebo dva samostatné dokumenty s oddělenými podpisy.</p>',
            '<p>Aktuální otázkou už proto není, jak vměstnat text do státního formuláře. Je třeba rozlišit listinné podpisy, podpory potvrzené na soukromém portálu a případné podpisy v oficiálním státním nástroji. Každý z těchto způsobů má jinou míru ověření a při předložení městu musí být popsán pravdivě.</p>',
            "practical issue",
        ),
        (
            '<h2 id="limit">Limit 3500 znaků skutečně platí</h2>',
            '<h2 id="limit">Limit 3500 znaků platil pro státní ePetici, nikoli pro současný portál</h2>',
            "limit heading",
        ),
        (
            '<p>Oficiální formulář Portálu občana rozlišuje název, krátký popis a vlastní text petice. Název může mít nejvýše 200 znaků, stručný popis 290 znaků a vlastní petiční text 3500 znaků.</p>',
            '<p>Státní nástroj ePetice na Portálu občana rozlišuje název, krátký popis a vlastní text petice; pro vlastní text stanoví limit 3500 znaků. Toto pravidlo vysvětluje původní technický problém předkladatelky. Současná petice však běží na e-petice.cz, jejíž veřejný formulář umožnil zveřejnit celé osmibodové znění.</p>',
            "limit paragraph",
        ),
        (
            '<p>K petici lze přidat přílohy, například dokumenty, fotografie nebo nákresy. Příloha může obsahovat podrobnější argumentaci, jádro požadavků ale musí zůstat srozumitelně uvedeno v samotném textu, který občan podepisuje.</p>',
            '<p>Možnost příloh, maximální délka sběru a pravidla kombinace listinného a elektronického podání popsaná Portálem veřejné správy se vztahují ke státnímu nástroji. Nelze je bez dalšího vydávat za provozní podmínky soukromého webu e-petice.cz.</p>',
            "limit scope",
        ),
        (
            '<h2 id="stejny-text">Papírová a elektronická verze musí být naprosto stejná</h2>',
            '<h2 id="stejny-text">Stejné znění je důležité, ale současný portál má jiná pravidla</h2>',
            "same text heading",
        ),
        (
            '<p>Pro kadaňskou petici je nejdůležitější výslovná podmínka Portálu veřejné správy. Zakladatel si může vybrat pouze listinnou petici, pouze elektronickou petici nebo kombinaci obou způsobů. Při kombinaci však musí být text obou verzí totožný.</p>',
            '<p>Požadavek Portálu veřejné správy na naprosto stejný text platí při kombinaci listinných podpisů s podpisy ve státním nástroji ePetice. Současný online sběr ale probíhá na soukromé platformě. Její podmínky takovou formulaci jako technické pravidlo nestanoví.</p>',
            "same text scope",
        ),
        (
            '<blockquote>„Pokud kombinujete oba způsoby, text petice listinné i elektronické musí být naprosto stejný.“</blockquote>',
            '<blockquote>U státní ePetice nahrazuje podpis podpora ověřená Identitou občana. Na soukromém portálu se podpora potvrzuje e-mailem a tuto úroveň státního ověření nemá.</blockquote>',
            "same text quote",
        ),
        (
            '<p>Nestačí tedy stejný název, podobné téma nebo obecně stejný cíl. Elektronicky i na papíře musí lidé podpořit stejné požadavky ve stejném znění.</p>',
            '<p>Přesto zůstává přesné znění podstatné: každý člověk podporuje konkrétní text, který před potvrzením vidí. Pokud se listinná a online verze v požadavcích liší, nelze počty jednoduše prezentovat jako podpisy pod jedním totožným dokumentem.</p>',
            "same text principle",
        ),
        (
            '<h2 id="podpisy">Již získané podpisy zůstávají u původního textu</h2>',
            '<h2 id="podpisy">Listinné podpisy a podpory na soukromém portálu je nutné rozlišovat</h2>',
            "signatures heading",
        ),
        (
            '<p>Jestliže se má elektronický a listinný sběr počítat jako jedna petice, musí se totožné zkrácené znění použít v ePetici i na nových listinných arších. Již získané podpisy pod delším původním zněním zůstávají podporou původního dokumentu. Pokud se elektronická verze od původní listinné petice liší, musí být oba sběry vykazovány odděleně.</p>',
            '<p>Na e-petice.cz podepisující vyplňuje jméno, příjmení, adresní údaje a e-mail a podporu potvrzuje odkazem v doručené zprávě. E-mailové potvrzení ověřuje přístup k dané schránce, nikoli totožnost prostřednictvím státního registru. Při předložení výsledků je proto přesnější uvést zvlášť počet vlastnoručních listinných podpisů a zvlášť počet potvrzených online podpor.</p>',
            "signatures distinction",
        ),
        (
            '<div class="factcheck"><h3>Tři možné postupy</h3><ul><li><strong>Totožná verze:</strong> stejný text se použije na papíře i elektronicky a výsledky mohou být předloženy společně.</li><li><strong>Nová kratší verze:</strong> nové listinné archy i ePetice používají totožný zkrácený text; starší podpisy zůstávají pod původním zněním.</li><li><strong>Dvě odlišné petice:</strong> obě mohou sledovat podobný cíl, ale jejich podpisy musí být prezentovány jako podpora dvou různých textů.</li></ul></div>',
            '<div class="factcheck"><h3>Tři druhy podpory, které nelze zaměňovat</h3><ul><li><strong>Listinný podpis:</strong> vlastnoruční podpis spolu se jménem, příjmením a bydlištěm podle petičního zákona.</li><li><strong>Státní ePetice:</strong> podpora ověřená Identitou občana; zákon ji výslovně staví na roveň podpisu.</li><li><strong>Soukromý portál e-petice.cz:</strong> osobní údaje a e-mailové potvrzení podle podmínek provozovatele, bez ověření prostředkem státní elektronické identity.</li></ul></div>',
            "three types",
        ),
        (
            '<h2 id="schvaleni">Oficiální postup standardní „schvalování“ nepopisuje</h2>',
            '<h2 id="schvaleni">Soukromý portál může obsah zveřejnit nebo moderovat podle vlastních podmínek</h2>',
            "approval heading",
        ),
        (
            '<p>Oficiální návod uvádí, že zakladatel vyplní údaje, projde rekapitulaci a může návrh uložit, smazat nebo petici založit. Založením dojde k jejímu zveřejnění. Běžnou samostatnou fázi obsahového schvalování úředníkem návod nepopisuje.</p>',
            '<p>U státní ePetice oficiální návod samostatné obsahové schvalování úředníkem nepopisuje. e-petice.cz je však soukromě provozovaný server a jeho provozovatel si v podmínkách vyhrazuje možnost užívání pozastavit nebo ukončit, pokud je obsah v rozporu s právními předpisy nebo pravidly serveru. Dřívější zmínka o čekání na schválení proto mohla souviset právě s interním procesem soukromé platformy nebo s rozpracovaným návrhem.</p>',
            "approval distinction",
        ),
        (
            '<p>Po zveřejnění už navíc text nelze běžně editovat. Změna znamená původní ePetici uzavřít a založit novou. Konečné znění je proto potřeba zkontrolovat předem.</p>',
            '<p>Pravidlo, že zveřejněnou petici nelze editovat a je nutné založit novou, popisuje státní Portál občana. U soukromého webu je rozhodující jeho vlastní administrace a podmínky. Veřejný text kadaňské petice proto budeme porovnávat při každé podstatné změně.</p>',
            "editing distinction",
        ),
        (
            '<h2 id="podepsani">Elektronický podpis není anonymní kliknutí</h2>',
            '<h2 id="podepsani">Na e-petice.cz se podpora potvrzuje e-mailem, nikoli Identitou občana</h2>',
            "signing heading",
        ),
        (
            '<p>Oficiální ePetici lze podepsat pouze po přihlášení do Portálu občana prostřednictvím Identity občana. Podpis podporovatele je tak spojen s ověřenou osobou a systém brání duplicitním či smyšleným podpisům.</p>',
            '<p>Podle podmínek e-petice.cz uvádí zájemce jméno, příjmení, město, PSČ, ulici, číslo domu a e-mailovou adresu. Podporu následně potvrzuje prostřednictvím odkazu doručeného e-mailem. Platforma může zveřejnit jméno, příjmení a město, pokud s tím uživatel souhlasí.</p>',
            "signing process",
        ),
        (
            '<p>Podporovatel nepotřebuje vlastní kvalifikovaný elektronický podpis. Přihlášení a potvrzení podpory v Portálu občana nahrazuje vlastnoruční podpis na archu. Během sběru může občan svůj podpis také odvolat.</p>',
            '<p>To je jiný mechanismus než státní ePetice. e-petice.cz podle veřejných podmínek nepoužívá bankovní identitu, eObčanku ani jiný kvalifikovaný prostředek elektronické identifikace. Nelze proto tvrdit, že každý online záznam představuje státem ověřenou osobu.</p>',
            "signing verification",
        ),
        (
            '<p>Veřejně je dostupný text petice a počet podporovatelů, nikoli osobní údaje jednotlivých podepsaných. Zakladatel získá úplný výpis podpisů až po uzavření petice.</p>',
            '<p>Soukromý portál zobrazuje veřejný počet potvrzených podpor a podle nastavení také část údajů podporovatelů. Provozovatel současně nabízí podpisový arch v PDF. Jak přesně budou online údaje předány městu a zda je adresát uzná jako formální podpisy podle petičního zákona, bude možné posoudit až podle skutečného podání.</p>',
            "signing output",
        ),
        (
            '<h2 id="ucinky">Petice nutí úřad odpovědět, nikoli automaticky vyhovět</h2>',
            '<h2 id="ucinky">Zveřejnění na soukromém webu samo o sobě ještě nezakládá povinnost města odpovědět</h2>',
            "effects heading",
        ),
        (
            '<p>Řádně podaná ePetice je z hlediska petičního zákona srovnatelná s listinnou peticí. Adresovaný orgán je povinen ji přijmout, posoudit a do 30 dnů písemně sdělit své stanovisko a způsob vyřízení.</p>',
            '<p>Povinnost adresovaného orgánu petici přijmout, posoudit a do 30 dnů písemně odpovědět vzniká až řádným podáním petice podle petičního zákona. Tuto roli může bez pochyb splnit listinná petice nebo státní ePetice podle § 6a. Samotné zveřejnění výzvy a nasbírání podpor na soukromém webu ještě není podáním městu.</p>',
            "effects 30 days",
        ),
        (
            '<p>Vedle petičního zákona může být významné také právo občanů obce požadovat projednání konkrétní záležitosti v samostatné působnosti. Pokud takový požadavek podepíše nejméně 0,5 procenta občanů Kadaně, musí být v působnosti zastupitelstva projednán nejpozději do 90 dnů. Rozhodující jsou zde občané obce, tedy zejména osoby s trvalým pobytem v Kadani, nikoli automaticky všichni podporovatelé odjinud.</p>',
            '<p>Vedle petičního zákona může být významné také právo občanů obce požadovat projednání konkrétní záležitosti v samostatné působnosti. U hranice 0,5 procenta jsou rozhodující občané Kadaně. Pouhý veřejný počet na soukromém portálu k prokázání této podmínky nestačí, protože e-mailové potvrzení samo neověřuje totožnost ani postavení občana obce. Rozhodující bude seznam skutečně předložený městu a způsob jeho ověření.</p>',
            "effects municipality",
        ),
        (
            '<h2 id="sledovani">Jak budeme pokračovat</h2>',
            '<h2 id="sledovani">Co budeme dál ověřovat</h2>',
            "monitoring heading",
        ),
        (
            '<p>Naše Kadaň nastavila pravidelnou kontrolu veřejného seznamu ePetic a dalších ověřitelných informací k této podpisové akci.</p>',
            '<p>Naše Kadaň bude sledovat veřejnou stránku petice na e-petice.cz, případné změny textu, počet potvrzených online podpor a hlavně způsob, kterým předkladatelka výsledky předá městu.</p>',
            "monitoring intro",
        ),
        (
            '<p>Jakmile bude elektronická verze veřejná, zkontrolujeme:</p>',
            '<p>Při dalším vývoji zkontrolujeme:</p>',
            "monitoring list intro",
        ),
        (
            '<ul><li>přesné znění všech požadavků,</li><li>shodu s dosavadní listinnou peticí,</li><li>zakladatele a adresáta,</li><li>datum zveřejnění a konec sběru,</li><li>případné přílohy,</li><li>a veřejně dostupný počet podpisů.</li></ul>',
            '<ul><li>zda se veřejný text na soukromém portálu nezměnil,</li><li>zda se shoduje s listinnými archy v podstatných požadavcích,</li><li>kolik je vlastnoručních podpisů a kolik potvrzených online podpor,</li><li>jaký výpis soukromý portál předkladatelce poskytne,</li><li>jak bude petice doručena městu,</li><li>a jak město jednotlivé druhy podpory právně vyhodnotí.</li></ul>',
            "monitoring list",
        ),
        (
            '<h2>Elektronická petice může pomoci, pravidla ale musí být jasná</h2>',
            '<h2>Soukromá online petice může mobilizovat veřejnost, právní režim je ale nutné popsat přesně</h2>',
            "conclusion heading",
        ),
        (
            '<p>Přesun petice do oficiálního elektronického systému je legitimní a pro občany pohodlný krok. Může se zapojit více lidí a každý podpis je ověřený.</p>',
            '<p>Zveřejnění na e-petice.cz je legitimní způsob, jak petici šířit a získat veřejnou podporu. Neznamená však, že každý záznam má automaticky stejnou právní váhu jako vlastnoruční podpis nebo podpora ověřená Identitou občana ve státní ePetici.</p>',
            "conclusion first",
        ),
        (
            '<p>Právě proto však musí být před zahájením elektronického sběru jednoznačné, co občan podepisuje a zda je to skutečně stejný text jako na již používaných papírových arších.</p>',
            '<p>Pro důvěryhodnost celé akce bude rozhodující, aby předkladatelka při předání městu oddělila listinné podpisy od online podpor, doložila jejich počet a nespojovala různé úrovně ověření do jediného nerozlišeného čísla.</p>',
            "conclusion second",
        ),
        (
            '<blockquote>Zkrátit vysvětlení lze. Změnit požadavky a automaticky k nim přičíst starší podpisy pod jiným textem by ale nebylo správné.</blockquote>',
            '<blockquote>Soukromý portál může dobře ukázat rozsah veřejné podpory. Státem ověřený elektronický podpis však nahrazuje pouze nástroj ePetice v Portálu občana.</blockquote>',
            "conclusion quote",
        ),
        (
            '<p>Naše Kadaň podporuje právo občanů obracet se peticí na město a současně bude trvat na přesném rozlišování ověřených podpisů, znění jednotlivých verzí a skutečných právních účinků.</p>',
            '<p>Naše Kadaň podporuje právo občanů obracet se peticí na město a současně bude přesně rozlišovat listinné podpisy, potvrzené online podpory na soukromém webu, případné státní elektronické podpisy a skutečné právní účinky konečného podání.</p>',
            "conclusion final",
        ),
        (
            '<p class="updated">Publikováno 26. 7. 2026 v 10:15 · aktualizováno 27. 7. 2026</p><p>Doplnili jsme celé listinné znění a snímky rozpracované ePetice. Veřejný odkaz na aktivní ePetici zatím chybí.</p>',
            '<p class="updated">Publikováno 26. 7. 2026 v 10:15 · zásadně aktualizováno 27. 7. 2026</p><p>Petice je veřejná na soukromém portálu e-petice.cz. Doplnili jsme rozdíly proti státní ePetici a přesnější popis online podpor.</p>',
            "sidebar status",
        ),
        (
            '<div class="sidebox"><h3>Nejdůležitější pravidlo</h3><p><strong>Při společném elektronickém a listinném sběru musí být text obou verzí naprosto stejný.</strong></p></div>',
            '<div class="sidebox"><h3>Nejdůležitější rozdíl</h3><p><strong>e-petice.cz je soukromá platforma. Podpora potvrzená e-mailem není totéž jako podpis ověřený Identitou občana.</strong></p></div>',
            "sidebar rule",
        ),
        (
            '<div class="sidebox"><h3>Máte veřejný odkaz?</h3><p>Pošlete ho na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>. Znění okamžitě porovnáme.</p></div>',
            '<div class="sidebox"><h3>Veřejný odkaz</h3><p><a href="https://e-petice.cz/petitions/petice-za-zachovani-nemocnice-kadan-s-r-o-ve-vlastnictvi-mesta.html" target="_blank" rel="noopener noreferrer">Otevřít petici na e-petice.cz →</a></p></div>',
            "sidebar link",
        ),
    ]

    for old, new, label in replacements:
        text = replace_once(text, old, new, label)

    # Aktualizace data v JSON-LD.
    text = re.sub(
        r'"dateModified":"[^"]+"',
        '"dateModified":"2026-07-27T20:30:00+02:00"',
        text,
        count=1,
    )

    # Rozšířit zdroje o aktuální soukromou platformu a její pravidla.
    marker = '<div class="source-list"><h2>Zdroje a metodika</h2><ul>'
    additions = (
        '<li><a href="https://e-petice.cz/petitions/petice-za-zachovani-nemocnice-kadan-s-r-o-ve-vlastnictvi-mesta.html" target="_blank" rel="noopener noreferrer">e-petice.cz: veřejná online verze petice za Nemocnici Kadaň</a></li>'
        '<li><a href="https://e-petice.cz/podminky-serveru/" target="_blank" rel="noopener noreferrer">e-petice.cz: podmínky serveru, požadované údaje a potvrzení podpory</a></li>'
    )
    text = replace_once(text, marker, marker + additions, "sources additions")

    old_note = (
        '<small>Veřejný odkaz na ePetici nebyl dohledatelný při původním zveřejnění 26. 7. 2026 ani při redakční aktualizaci 27. 7. 2026. '
        'To nevylučuje existenci rozpracovaného záznamu v neveřejné části Portálu občana.</small>'
    )
    new_note = (
        '<small>Článek odlišuje státní nástroj ePetice podle § 6a petičního zákona od soukromého serveru e-petice.cz. '
        'Veřejná online podpora na soukromé platformě je významným projevem názoru, její právní započtení však závisí na podobě konečného podání a posouzení adresáta.</small>'
    )
    text = replace_once(text, old_note, new_note, "source note")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("Článek o e-petici byl opraven podle skutečné soukromé platformy e-petice.cz.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
