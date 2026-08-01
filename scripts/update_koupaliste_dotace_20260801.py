#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / ".github/drafts/koupaliste-kadan-research-2026.html",
    ROOT / ".github/drafts/pozemky-koupaliste-kadan.html",
]
MARKER = '<!-- BEGIN UPDATE 2026-08-01 DOTACE -->'
SECTION = '''

<!-- BEGIN UPDATE 2026-08-01 DOTACE -->
<section data-update="2026-08-01-dotace">
  <h2>Nový primární doklad: jedna smlouva odkazuje na dvě usnesení a stanoví termín vyúčtování</h2>

  <h3>Doloženo</h3>
  <ul>
    <li>Úplné znění smlouvy o individuální investiční dotaci č. 11/2026 uvádí v článku II poskytnutí 2 000 000 Kč „v souladu s usnesením zastupitelstva města Kadaně č. 11/2026 ze dne 26. 2. 2026“.</li>
    <li>Tatáž smlouva v článku VII odst. 6 současně uvádí, že byla schválena usnesením zastupitelstva č. 66/2026 ze dne 25. 6. 2026.</li>
    <li>Účelem je výhradně investice „Doplnění atrakce skluzavky na městském koupališti v Kadani“.</li>
    <li>Dotace má být použita do 31. 12. 2026. Tepelné hospodářství musí doložit účel a způsob čerpání nejpozději do 31. 1. 2027.</li>
    <li>Nevyužité prostředky nebo částky bez prokázaného účelu a hodnoty čerpání se vracejí; smlouva zároveň vyžaduje oddělené účetní sledování dotace.</li>
    <li>Registr smluv obsahuje dvě publikace téhož názvu a nominální částky: první byla zveřejněna 3. 7. 2026 pod č. j. 00079/OE/2026 s přílohou DOC, druhá 9. 7. 2026 pod č. j. 00084/OE/2026 s přílohou PDF.</li>
  </ul>

  <h3>Silná stopa / pracovní výklad</h3>
  <p>Dvojice odkazů v jedné smlouvě pravděpodobně rozlišuje dřívější rozpočtové rozhodnutí nebo schválení záměru (usnesení 11/2026) a pozdější schválení samotné dotační smlouvy (usnesení 66/2026). Jde však o redakční výklad; přesnou roli obou usnesení je nutné potvrdit jejich úplným textem a důvodovými zprávami.</p>

  <h3>Neprokázáno</h3>
  <ul>
    <li>Z dokumentu stále nelze zjistit vítězného dodavatele, konečnou fakturu, položkový rozpočet ani skutečně vyčerpanou částku.</li>
    <li>Dvojí zveřejnění samo o sobě neprokazuje dvě dotace ani dvojí platbu.</li>
    <li>Protože řádné vyúčtování je splatné až 31. 1. 2027, jeho absence v srpnu 2026 neznamená porušení povinnosti.</li>
  </ul>

  <h3>Otázky k ověření</h3>
  <ol>
    <li>Získat úplné znění usnesení č. 11/2026 ze dne 26. 2. 2026 a určit, zda šlo o rozpočtové opatření, schválení záměru nebo jiný krok.</li>
    <li>Porovnat obě zveřejněné verze smlouvy a zjistit důvod změny čísla jednacího 00079/OE/2026 na 00084/OE/2026.</li>
    <li>Po 31. 1. 2027 vyžádat konečné vyúčtování, seznam uznatelných nákladů a případnou vratku.</li>
    <li>Nadále hledat zadávací dokumentaci, smlouvu s dodavatelem, faktury, předávací protokol a technické řešení schodů.</li>
  </ol>

  <h3>Primární zdroje</h3>
  <ul>
    <li><a href="https://smlouvy.gov.cz/smlouva/38634856">Registr smluv – první zveřejnění 3. 7. 2026</a></li>
    <li><a href="https://smlouvy.gov.cz/smlouva/38695400">Registr smluv – druhé zveřejnění 9. 7. 2026</a></li>
    <li><a href="https://smlouvy.gov.cz/smlouva/soubor/46715816/Tepelné%20hospodářství%20-%20klouzačka.pdf">Úplné znění dotační smlouvy v PDF</a></li>
  </ul>
</section>
<!-- END UPDATE 2026-08-01 DOTACE -->
'''

for path in FILES:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        continue
    if "</main>" not in text:
        raise RuntimeError(f"Chybí </main> v {path}")
    text = text.replace("</main>", SECTION + "\n</main>", 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Aktualizováno: {path.relative_to(ROOT)}")
