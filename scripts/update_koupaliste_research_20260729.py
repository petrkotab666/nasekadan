#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RESEARCH = ROOT / ".github/drafts/koupaliste-kadan-research-2026.html"
ARTICLE = ROOT / ".github/drafts/pozemky-koupaliste-kadan.html"
FINAL = ROOT / ".github/drafts/koupaliste-kadan-skluzavka-niagara.html"

RESEARCH_BLOCK = r'''
<!-- BEGIN UPDATE 2026-07-29 -->
<section data-update="2026-07-29">
  <h2>17. Nové ověřené zjištění: dotace byla schválena po otevření</h2>
  <p><strong>Doloženo:</strong> skluzavka Niagara byla slavnostně uvedena do provozu 21. června 2026. Zastupitelstvo města schválilo individuální investiční dotaci č. 11/2026 ve výši 2 miliony Kč až 25. června 2026, tedy o čtyři dny později. Smlouva byla uzavřena 1. července a zveřejněna 3. července.</p>
  <p>V zápisu zastupitelstva se Jana Demjanová zeptala, co dvoumilionová cena obsahuje. Starosta Jan Losenický uvedl, že jde o cenu skluzavky a všechny vedlejší práce. Jednatel TH Kadaň Dušan Kučera doplnil, že cena byla vysoutěžena ve výběrovém řízení. Usnesení č. 66/2026 bylo přijato poměrem 25 pro, 0 proti, 0 se zdrželo.</p>
  <p><strong>Právní a redakční opatrnost:</strong> schválení dotace po otevření samo o sobě neprokazuje pochybení. TH Kadaň mohlo být investorem a město mohlo následně schválit úhradu části uznatelných nákladů. K uzavření věci je nutná smlouva s dodavatelem, zadávací dokumentace, faktura a konečné vyúčtování.</p>

  <h3>Aktualizovaná časová osa</h3>
  <ul>
    <li><strong>21. 6. 2026:</strong> slavnostní otevření nové skluzavky.</li>
    <li><strong>25. 6. 2026:</strong> zastupitelstvo schválilo dvoumilionovou dotaci.</li>
    <li><strong>29. 6. 2026:</strong> provozovatel varoval před rozpálenými kovovými schody.</li>
    <li><strong>1. 7. 2026:</strong> uzavření dotační smlouvy.</li>
    <li><strong>3. 7. 2026:</strong> první zveřejnění smlouvy v registru.</li>
  </ul>

  <h3>Dodavatel: stopa KOVO BATH zesílila, ale není uzavřená</h3>
  <p><strong>Silná stopa:</strong> Hlídač státu řadí KOVO BATH mezi největší smluvní dodavatele TH Kadaň v roce 2026. Firma vyrábí vodní skluzavky typu Niagara a kovová schodiště. Přímá kadaňská smlouva, objednávka nebo faktura však stále nebyla nalezena. Dodavatele proto nelze prezentovat jako definitivně potvrzeného.</p>

  <h3>Nový publikační stav</h3>
  <p>Finální pracovní článek je uložen v <code>.github/drafts/koupaliste-kadan-skluzavka-niagara.html</code> a připraven pro zveřejnění v pátek 31. července 2026 v 5:00. Hlavní osa článku je časová posloupnost, financování, přehřívání schodů a chybějící veřejný harmonogram atrakcí.</p>

  <h3>Nové primární zdroje</h3>
  <ul>
    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5095122.pdf">Zápis ze 17. zasedání Zastupitelstva města Kadaně dne 25. 6. 2026</a></li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38634856">Registr smluv: individuální investiční dotace č. 11/2026</a></li>
    <li><a href="https://www.cez.cz/cs/pro-media/tiskove-zpravy/kralovske-mesto-kadan-nadelilo-svemu-koupalisti-k-padesatinam-novou-skluzavku-financne-na-ni-jednim-milionem-korun-prispela-nadace-cez-235563">Nadace ČEZ: otevření, rozměr, cena a nadační příspěvek</a></li>
  </ul>
</section>
<!-- END UPDATE 2026-07-29 -->
'''.strip()

ARTICLE_BLOCK = r'''
<!-- BEGIN UPDATE 2026-07-29 -->
<section data-update="2026-07-29">
  <h2>Nové zjištění: dva miliony byly schváleny čtyři dny po otevření</h2>
  <p>Zápis ze zastupitelstva umožnil uzavřít schvalovací osu. Skluzavka byla otevřena 21. června 2026. Zastupitelé schválili individuální investiční dotaci pro Tepelné hospodářství až 25. června usnesením č. 66/2026, poměrem 25–0–0. Smlouva byla následně uzavřena 1. července a zveřejněna 3. července.</p>
  <p>Jana Demjanová se na jednání zeptala, co dva miliony zahrnují. Starosta Jan Losenický odpověděl, že jde o skluzavku a všechny vedlejší práce. Jednatel TH Kadaň Dušan Kučera uvedl, že cena byla vysoutěžena ve výběrovém řízení.</p>
  <div class="callout"><strong>Co z toho neplyne</strong>Schválení dotace po otevření samo o sobě neprokazuje porušení pravidel ani nehospodárnost. Ukazuje však, proč je potřeba zveřejnit zadávací dokumentaci, vítězného dodavatele, položkový rozpočet, konečnou fakturu a vyúčtování městské i nadační podpory.</div>
  <p>Finální páteční verze článku je připravena jako samostatný draft <code>.github/drafts/koupaliste-kadan-skluzavka-niagara.html</code>.</p>
</section>
<!-- END UPDATE 2026-07-29 -->
'''.strip()

COUNCIL_BLOCK = r'''
<!-- BEGIN COUNCIL APPROVAL 2026-07-29 -->
<section data-council-approval="2026-07-29">
  <h2 id="zastupitelstvo">Co přesně zaznělo na zastupitelstvu</h2>
  <p>Zápis z 25. června přináší nejkonkrétnější veřejné vysvětlení dvoumilionové částky. Jana Demjanová se zeptala, v čem cena skluzavky spočívá. Starosta Jan Losenický odpověděl, že jde o cenu skluzavky a všechny vedlejší práce.</p>
  <p>Jednatel Tepelného hospodářství Dušan Kučera doplnil, že podobné atrakce jsou samy o sobě velmi drahé a cena byla vysoutěžena ve výběrovém řízení. Zastupitelé pak dotaci schválili jednomyslně: 25 hlasů pro, nikdo proti a nikdo se nezdržel.</p>
  <div class="callout"><strong>Schválení po otevření není samo o sobě důkazem chyby</strong>Tepelné hospodářství mohlo být investorem a město mohlo následně schválit úhradu části uznatelných nákladů. Veřejné dokumenty ale stále musí umožnit zjistit, kdy byl závazek vůči dodavateli uzavřen, co přesně zahrnovaly vedlejší práce a kolik bylo skutečně čerpáno.</div>
</section>
<!-- END COUNCIL APPROVAL 2026-07-29 -->
'''.strip()


def inject(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(
        r"\s*<!-- BEGIN UPDATE 2026-07-29 -->.*?<!-- END UPDATE 2026-07-29 -->\s*",
        "\n",
        text,
        flags=re.S,
    )
    marker = "</main>" if "</main>" in text else "</body>"
    if marker not in text:
        raise RuntimeError(f"V {path} chybí uzavírací značka")
    text = text.replace(marker, "\n" + block + "\n" + marker, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    return text != original


def patch_final(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = text.replace("2026-07-31T14:00:00+02:00", "2026-07-31T05:00:00+02:00")
    text = text.replace(
        "Kadaň otevřela dvoudráhovou skluzavku Niagara 21. června. Podle oficiální tiskové zprávy stála včetně schodů necelých 2,35 milionu korun a milion poskytla Nadace ČEZ. O deset dní později město uzavřelo s Tepelným hospodářstvím Kadaň dvoumilionovou investiční dotaci označenou jako „klouzačka“. Veřejně viditelné zdroje podpory tak nominálně dosahují tří milionů, bez konečného vyúčtování to ale není důkaz přeplacení ani dvojího financování. Osm dní po otevření navíc provozovatel varoval, že kovové schody mohou v horku pálit do chodidel.",
        "Kadaň otevřela dvoudráhovou skluzavku Niagara 21. června. Teprve o čtyři dny později zastupitelé schválili Tepelnému hospodářství dvoumilionovou investiční dotaci a osm dní po slavnosti provozovatel upozornil na riziko popálení o rozpálené kovové schody. Podle oficiální tiskové zprávy stála atrakce včetně schodů necelých 2,35 milionu korun a milion poskytla Nadace ČEZ. Bez konečného vyúčtování ale nelze tvrdit přeplacení ani dvojí financování."
    )

    if "<b>25. června 2026</b>" not in text:
        needle = '<div class="timeline-item"><b>21. června 2026</b><p>Skluzavka je slavnostně uvedena do provozu při padesátém výročí koupaliště.</p></div>'
        addition = needle + '\n    <div class="timeline-item"><b>25. června 2026</b><p>Zastupitelstvo schvaluje individuální investiční dotaci č. 11/2026 ve výši dva miliony korun. Usnesení č. 66/2026 přijímá poměrem 25–0–0.</p></div>'
        text = text.replace(needle, addition, 1)

    text = re.sub(
        r"\s*<!-- BEGIN COUNCIL APPROVAL 2026-07-29 -->.*?<!-- END COUNCIL APPROVAL 2026-07-29 -->\s*",
        "\n",
        text,
        flags=re.S,
    )
    marker = '  <h2 id="financovani">'
    if marker in text:
        text = text.replace(marker, COUNCIL_BLOCK + "\n\n" + marker, 1)

    source = '    <li><a href="https://www.mesto-kadan.cz/filemanager/files/5095122.pdf" target="_blank" rel="noopener noreferrer">Město Kadaň: zápis ze 17. zasedání zastupitelstva dne 25. června 2026</a></li>\n'
    source_marker = '    <li><a href="https://www.cez.cz/'
    if "filemanager/files/5095122.pdf" not in text and source_marker in text:
        text = text.replace(source_marker, source + source_marker, 1)

    text = text.replace(
        '<li>otevření 21. června a varování před horkými schody 29. června;</li>',
        '<li>otevření 21. června, schválení dotace 25. června a varování před horkými schody 29. června;</li>'
    )
    text = text.replace(
        "Připraveno pro pátek 31. července 2026.",
        "Připraveno pro pátek 31. července 2026 v 5:00."
    )

    path.write_text(text, encoding="utf-8", newline="\n")
    return text != original


def main() -> int:
    changed = inject(RESEARCH, RESEARCH_BLOCK)
    changed = inject(ARTICLE, ARTICLE_BLOCK) or changed
    changed = patch_final(FINAL) or changed
    print("Aktualizace rešerše koupaliště:", "změněno" if changed else "beze změn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
