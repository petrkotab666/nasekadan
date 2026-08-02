# Seznam Partner – dokončení CMP

Web je připravený v bezpečném režimu bez reklamních cookies Seznam Partneru. Dokud není níže uvedený krok dokončen, `cmp-config.json` musí zůstat s `enabled: false` a reklamní kód Seznam Partner se nesmí nasadit.

## Povinný poslední krok

1. Založit účet u CMP certifikované podle IAB TCF 2.2. Seznam doporučuje consentmanager.
2. V CMP nastavit doménu `nasekadan.cz`, češtinu, identitu provozovatele a rovnocenné volby Přijmout / Odmítnout na první vrstvě.
3. Povolit minimálně vendory požadované Seznam Partnerem:
   - 16 – RTB House
   - 32 – Xandr
   - 50 – Adform
   - 76 – PubMatic
   - 91 – Criteo
   - 621 – Seznam.cz
   - 755 – Google advertising
4. Zkopírovat úplný a nezměněný CMP kód poskytovatele.
5. Do `cmp-config.json` vložit HTTPS adresu skriptu a nastavit `enabled: true` pouze tehdy, když je CMP skutečně nakonfigurovaná.
6. Spustit `python scripts/check_seznam_partner_readiness.py`.
7. Na živém webu ověřit:
   - dialog se zobrazí novému návštěvníkovi,
   - odmítnutí je stejně snadné jako přijetí,
   - `__tcfapi` vrací platný TCF 2.2 stav,
   - bez souhlasu se nenačte žádný reklamní vendor,
   - odkaz „Nastavení soukromí“ znovu otevře dialog,
   - po odvolání souhlasu se stav správně změní.
8. Teprve potom vložit reklamní zóny Seznam Partner a příslušný `ads.txt` řádek získaný přímo z partnerského rozhraní.

## Nové posouzení

Po živém ověření požádat o nové posouzení webu ID 81896 na `seznam.partner@firma.seznam.cz`. Do žádosti uvést, že:

- provozovatel je uveden na `/provozovatel/` a v patičce,
- stránka ochrany osobních údajů a cookies byla aktualizována,
- byla nasazena certifikovaná TCF 2.2 CMP,
- reklamy se před souhlasem nenačítají.
