#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "clanky" / "starosta-losenicky-nemocnice-slovan-nepedagogove.html"
MODIFIED = "2026-07-30T18:19:00+02:00"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Nenalezen marker pro {label}")
    return text.replace(old, new, 1)


def main() -> int:
    text = ARTICLE.read_text(encoding="utf-8")

    text = re.sub(
        r'<meta property="article:modified_time" content="[^"]+">',
        f'<meta property="article:modified_time" content="{MODIFIED}">',
        text,
        count=1,
    )
    text = re.sub(
        r'("dateModified":"?)[^",}]+',
        rf'\g<1>{MODIFIED}',
        text,
        count=1,
    )

    text = text.replace(
        '<meta name="description" content="Jan Losenický veřejně slíbil zvládnutí situace nemocnice, vyšší nový Slovan a dostatek peněz na nepedagogické pracovníky škol.">',
        '<meta name="description" content="Jan Losenický doplnil své vyjádření: vysvětlil dofinancování nemocnice, ukončení první stavby Slovanu, pobočku městské policie a financování nepedagogů.">',
        1,
    )
    text = text.replace(
        '<meta property="og:description" content="Veřejné ujištění o nemocnici, novém Slovanu a financování škol doprovodil Jan Losenický ostrou narážkou na spasitele a třicet stříbrných.">',
        '<meta property="og:description" content="Aktualizováno: starosta vysvětlil dofinancování nemocnice, zdržení Slovanu, pobočku městské policie a peníze na nepedagogy.">',
        1,
    )
    text = text.replace(
        '<meta name="twitter:description" content="Tři konkrétní veřejné přísliby a ostrý politický závěr vyjádření Jana Losenického.">',
        '<meta name="twitter:description" content="Aktualizováno o starostovy odpovědi k nemocnici, Slovanu, služebně městské policie a nepedagogům.">',
        1,
    )

    if ".update-alert{" not in text:
        text = replace_once(
            text,
            '.fact{background:#eef5f7;border:1px solid #cbdde3;border-radius:18px;padding:24px;margin:28px 0}.fact h3{margin-top:0}.warning{border-left:6px solid #b87910;background:#fff7dc;padding:22px 25px;border-radius:0 16px 16px 0;margin:30px 0}',
            '.fact{background:#eef5f7;border:1px solid #cbdde3;border-radius:18px;padding:24px;margin:28px 0}.fact h3{margin-top:0}.warning{border-left:6px solid #b87910;background:#fff7dc;padding:22px 25px;border-radius:0 16px 16px 0;margin:30px 0}.update-alert{border:2px solid #a9232b;background:#fff5f5;border-radius:18px;padding:20px 23px;margin:24px 0 30px;box-shadow:0 10px 28px #a9232b14}.update-alert b{display:block;color:#a9232b;font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:7px}.update-alert p{margin:0;font-size:17px}',
            "styl upozornění",
        )

    text = text.replace(
        '<p class="tag">KOMUNÁLNÍ POLITIKA · VEŘEJNÉ VÝROKY · 29. ČERVENCE 2026</p>',
        '<p class="tag">KOMUNÁLNÍ POLITIKA · VEŘEJNÉ VÝROKY · AKTUALIZOVÁNO 30. ČERVENCE 2026</p>',
        1,
    )

    if 'data-update-discussion="20260730"' not in text:
        lead = '<p class="leadtext"><strong>Kadaňský starosta Jan Losenický reagoval na otázky, proč se podporuje pomoc dětem s rakovinou, staví lávka a pořizují umělecká díla v době, kdy se řeší nemocnice, nedokončená výstavba na sídlišti B a financování zaměstnanců škol. Odmítl, že by si město muselo vybrat jen jednu prioritu. Současně veřejně vyslovil tři konkrétní přísliby.</strong></p>'
        alert = '''<div class="update-alert" data-update-discussion="20260730"><b>Aktualizováno 30. července 2026 v 18:19</b><p>Starosta v navazující diskusi doplnil, proč nemocnice potřebuje přechodné dofinancování, proč město ukončilo první stavbu Slovanu, že v nové budově má být pobočka městské policie a že město podle něj dostalo od státu peníze na nepedagogické pracovníky.</p></div>'''
        text = replace_once(text, lead, lead + "\n  " + alert, "upozornění na aktualizaci")

    if 'data-discussion-followup="20260730"' not in text:
        marker = '<div class="warning"><strong>Naše Kadaň připravuje o Slovanu samostatný článek.</strong> Zaměří se na původní projekt se 38 byty, ukončení první stavby, osud dotace, náklady prvního pokusu a nový plán se 48 byty.</div>'
        section = '''

  <section data-discussion-followup="20260730">
    <h2>Starosta v diskusi doplnil konkrétní vysvětlení</h2>
    <p>V navazující diskusi pod příspěvkem Jan Losenický odpověděl na přímé otázky k nemocnici, výstavbě na sídlišti B a nepedagogickým pracovníkům. Jeho odpověď je podstatně konkrétnější než původní obecné ujištění, že město všechny oblasti zvládne.</p>

    <h3>Nemocnice má podle něj překlenout tlak na menší zařízení</h3>
    <p>Starosta uvedl, že stát směřuje zdravotní péči k větší centralizaci a nastavení úhrad od zdravotních pojišťoven tlačí na menší nemocnice, aby se transformovaly nebo spojovaly s většími zařízeními. Přechodné období proto podle něj vyžaduje dofinancování od zřizovatele.</p>
    <p>Toto tvrzení vysvětluje, proč město nemocnici finančně podporuje. Stále však neříká, jak dlouho má přechodné období trvat, kolik dalších peněz bude potřeba ani jaká konkrétní transformace se v Kadani připravuje.</p>

    <h3>Od první smlouvy se podle starosty ustoupilo kvůli vícepracím a možným sporům</h3>
    <p>K projektu Slovan Losenický napsal, že město muselo postupovat jako řádný hospodář. Pokud stavbě hrozily předražené vícepráce nebo soudy s dodavatelem, bylo podle něj správné od smlouvy ustoupit. Projekt byl následně přepracován a nyní se znovu soutěží podle zákona.</p>
    <blockquote class="statement">„Byty se postaví a problém je prostě objektivní, museli jsme se chovat jako řádný hospodář.“<cite>Jan Losenický v navazující diskusi</cite></blockquote>
    <p>Jde o důležité veřejné vysvětlení vedení města. Samostatný článek o Slovanu proto prověří zejména hrozící vícepráce, důvody ukončení původní smlouvy, případné spory s dodavatelem a finanční vypořádání prvního pokusu.</p>

    <h3>V novostavbě má být pobočka městské policie</h3>
    <p>Starosta současně výslovně potvrdil, že v nové budově má být <strong>pobočka služebny Městské policie Kadaň</strong>. Reagoval tím i na diskutující, kteří popisovali nepořádek, pohyb uživatelů drog a obavy o bezpečnost v lokalitě.</p>
    <p>Redakce v připravovaném článku ověří, zda půjde o trvale obsazené pracoviště, kontaktní místo nebo pouze zázemí pro okrskáře a hlídky. Samotné zkušenosti diskutujících nelze bez statistických podkladů vydávat za přesný obraz kriminality celého sídliště.</p>

    <h3>Převod nepedagogů považuje za správný</h3>
    <p>Losenický uvedl, že převod odpovědnosti za kuchařky, uklízečky, školníky a další nepedagogické pracovníky na města považuje za správný. Podle něj město dostalo peníze od státu a nyní může optimalizovat jídelny, úklid a správu školních budov.</p>
    <p>Starosta neupřesnil, jak bude optimalizace v Kadani vypadat. Může znamenat lepší organizaci služeb, ale také slučování provozů, změny úvazků nebo využití externích dodavatelů. Rozhodující proto budou konkrétní rozpočtová opatření a kroky vůči jednotlivým školám.</p>

    <h3>„Rozpočet podle toho samozřejmě vypadá“</h3>
    <p>Na námitku, že veřejná ujištění by měla být doložena čísly, starosta odpověděl, že na otázky odpověděl a městský rozpočet podle toho vypadá. Svou odpověď zakončil nezvykle expresivním zdůrazněním osobní odpovědnosti za veřejná slova.</p>
    <blockquote class="statement">„Nerad si dělám z huby sráč. Ani si to ve své roli nemůžu jaksi dovolit, nejsem jen soukromá osoba, co si může plácat, co chce.“<cite>Jan Losenický v navazující diskusi</cite></blockquote>
    <p>Tím se původní příspěvek ještě více posouvá od obecné úvahy ke konkrétnímu politickému závazku. Tvrzení bude možné porovnat s rozpočtem města, další podporou nemocnice, výsledkem nové zakázky na Slovan a skutečnými výdaji na nepedagogické pracovníky.</p>
  </section>'''
        text = replace_once(text, marker, marker + section, "doplnění diskuse")

    text = text.replace(
        'Jan Losenický – veřejný příspěvek</a>: citované vyjádření o nemocnici, Slovanu, školách a městských prioritách.',
        'Jan Losenický – veřejný příspěvek a navazující diskuse</a>: citované vyjádření o nemocnici, Slovanu, pobočce městské policie, školách a městských prioritách.',
        1,
    )

    if '<h3>Aktualizace článku</h3>' not in text:
        sidebar_marker = '<aside class="sticky"><div class="sidebox"><h3>Co starosta slíbil</h3>'
        sidebar_new = '<aside class="sticky"><div class="sidebox"><h3>Aktualizace článku</h3><p><strong>30. 7. 2026 v 18:19</strong></p><p>Doplněny starostovy odpovědi z následné diskuse.</p></div><div class="sidebox"><h3>Co starosta slíbil</h3>'
        text = replace_once(text, sidebar_marker, sidebar_new, "upozornění v bočním panelu")

    ARTICLE.write_text(text, encoding="utf-8", newline="\n")
    print("Článek byl aktualizován o navazující diskusi a viditelné upozornění.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
