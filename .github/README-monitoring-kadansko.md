# Jednotný monitoring Kadaně a Kadaňska

Kanonickým zdrojem pravdy je `data/monitoring-registry.json`. Registr se automaticky skládá z adresáře kadaňských organizací, ručně vedených zdrojů, akutních a celostátních zdrojů a doplňkového seznamu všech 19 obcí ORP Kadaň.

## Tři produkční vrstvy

1. **Akutní, každých 15 minut** – HZS, Policie, mimořádné události, odstávky, doprava, regionální média a provozní zdroje. Běží na vlastním runneru a má nezávislou hodinovou cloudovou zálohu.
2. **Hodinová** – město, úřední desky, městské společnosti, nemocnice, školy a školky, sociální služby, kultura, sport, okolní obce, média, doprava a sítě.
3. **Denní dokumentová** – smlouvy, veřejné zakázky, NEN, Zakázky GOV, Věstník veřejných zakázek, EIA/SEA, dotační a ministerské zdroje a další méně často měněné dokumentové registry.

Jednotný watchdog kontroluje čerstvost skutečných GitHub Actions běhů, úplnost registru, výpadky povinných zdrojů a procento nedostupných adres. Technický problém vede pouze do jednoho zdravotního issue.

## Ochrana proti šumu

- URL se sjednocují bez cache parametrů, měřicích parametrů a proměnlivých časových značek.
- Počítadla stažení, počty volných míst, meteorologické hodnoty a jiné proměnlivé údaje se neberou jako nový dokument.
- Navigace, kategorie, „Číst více“, jména autorů bez místní vazby a jiné falešné titulky se zahazují.
- Shodné odkazy a titulky se slučují; přímý zdroj má přednost před agregátorem.
- Akutní a významné nálezy mají vlastní issue. Méně naléhavé položky se sdružují do jednoho denního přehledu, aby monitoring nezaplavoval redakci.
- Stav se do repozitáře ukládá jen při skutečné obsahové nebo zdravotní změně, ne každých 15 minut.

## Rozsah

Registr zahrnuje Kadaň, všech 19 obcí správního obvodu ORP Kadaň a bezprostředně související zdroje v Březně a Chomutově. Povinně hlídá oblasti samosprávy, úředních desek, smluv, zakázek, bezpečnosti, zdravotnictví, školství, sociálních služeb, městských služeb, dopravy, sítí a médií.

Veřejné profily Facebooku a Instagramu jsou v registru zachované, ale bez oficiálního API slouží pouze ke kontrole dostupnosti. Neveřejné skupiny, příspěvky vyžadující přihlášení a obsah skrytý platformou nelze spolehlivě automaticky monitorovat.
