# Trvalé pravidlo zveřejňování článků Naše Kadaň

Toto pravidlo platí bez výjimky pro všechny články: ručně připravené, automaticky vytvořené, plánované i mimořádně zveřejňované.

## Povinný publikační řetězec

1. Každý článek musí být uložen ve veřejné složce `clanky/` a mít produkční metadata, datum publikace a `index,follow`.
2. Článek se musí objevit na titulní straně, v archivu článků, RSS, hlavní sitemapě a news sitemapě, pokud do ní podle stáří patří.
3. Každý článek musí mít vlastní jedinečný sociální obrázek PNG o rozměrech 1200 × 630. Generický obrázek webu není přípustný.
4. Po nasazení se musí veřejně ověřit článek, upoutávka na titulní straně, archiv, feedy i dostupnost a rozměry sociálního obrázku.
5. Teprve po úspěšném ověření živého webu se článek zveřejní na facebookové stránce Naše Kadaň.
6. Facebookové zveřejnění musí být potvrzeno záznamem v `.github/facebook-published/`, včetně ID příspěvku a použitého OG obrázku.
7. Selhání nasazení nebo Facebooku nesmí skončit pouhým upozorněním. Automat musí položku ponechat ve frontě, opakovat pokus a při bezpečně opravitelné chybě provést přímé nasazení na server.

## Technická pojistka

- `.github/workflows/publication-integrity-guard.yml` pravidelně kontroluje čerstvé články na živém webu, chybějící soubory samoopravuje a znovu zpracovává Facebook frontu.
- `.github/workflows/publish-facebook.yml` kontroluje, že živý článek používá vlastní PNG 1200 × 630, a nezveřejní odkaz s generickou grafikou.
- Jednorázové plánované články musí mít vedle hlavního publikačního běhu alespoň dva následné opravné běhy.
- Úspěch se nesmí deklarovat pouze podle commitu nebo dokončeného workflow. Rozhodující je veřejná kontrola produkční URL a potvrzení Facebook příspěvku.

Toto je výchozí a trvalá publikační politika projektu Naše Kadaň.
