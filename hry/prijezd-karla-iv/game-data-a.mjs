export const CHAPTERS_A = [
  {
    "id": "obnova",
    "label": "Obnova města",
    "codexTitle": "Město po pohromě",
    "variants": [
      {
        "eyebrow": "ŠEST TÝDNŮ DO PŘÍJEZDU",
        "title": "Domy ještě nesou stopy požáru",
        "text": "Císařská družina očekává bezpečné ulice. Městská rada však nemá dost peněz na úplnou opravu všeho.",
        "illustration": "fire",
        "choices": [
          {
            "id": "repair-main",
            "title": "Opravit hlavní trasu",
            "text": "Soustředit řemeslníky na cestu od brány k náměstí.",
            "result": "Průjezd bude důstojný, ale lidé z vedlejších ulic reptají.",
            "history": "Středověká města opravovala po požárech především klíčové komunikace a veřejné stavby. Konkrétní pořadí oprav je herní rekonstrukce.",
            "effects": {
              "treasury": -16,
              "order": 9,
              "favor": 8,
              "people": -4
            }
          },
          {
            "id": "repair-shared",
            "title": "Rozdělit práci po čtvrtích",
            "text": "Každá čtvrť opraví vlastní nejhorší místa.",
            "result": "Město se zvedá rovnoměrně, i když pomaleji.",
            "history": "Na obnově měst se běžně podíleli majitelé domů, řemeslníci i městská obec. Rozdělení povinností podle čtvrtí je pravděpodobný model, nikoli doložený kadaňský zápis z roku 1367.",
            "effects": {
              "treasury": -10,
              "order": 4,
              "people": 8,
              "favor": 2
            }
          },
          {
            "id": "repair-levy",
            "title": "Vyhlásit mimořádnou dávku",
            "text": "Získat peníze od majetnějších obyvatel a obchodníků.",
            "result": "Práce postupují rychle, ale město se rozdělí.",
            "history": "Mimořádné městské dávky patřily k nástrojům financování obrany a oprav. Jejich přesná podoba v této situaci je herní.",
            "effects": {
              "treasury": 12,
              "order": 6,
              "people": -13,
              "favor": 5
            }
          }
        ]
      },
      {
        "eyebrow": "ŠEST TÝDNŮ DO PŘÍJEZDU",
        "title": "Radnice žádá rychlý plán obnovy",
        "text": "Kameníci, tesaři i nádeníci čekají na rozhodnutí. Každý den prodlení zvyšuje cenu.",
        "illustration": "builders",
        "choices": [
          {
            "id": "guild-contract",
            "title": "Dohodnout cenu s cechy",
            "text": "Zaručit řemeslníkům další zakázky výměnou za nižší cenu nyní.",
            "result": "Dohoda funguje a řemeslníci drží slovo.",
            "history": "Cechovní organizace ovlivňovala městská řemesla, ale přesná smlouva je autorskou rekonstrukcí.",
            "effects": {
              "treasury": -9,
              "order": 5,
              "people": 6,
              "favor": 3
            }
          },
          {
            "id": "forced-labor",
            "title": "Nařídit pracovní povinnost",
            "text": "Každý dům vyšle jednoho člověka na veřejné práce.",
            "result": "Ulice se čistí rychle, nálada však tvrdne.",
            "history": "Města mohla ukládat obyvatelům povinnosti spojené s obranou a údržbou. Rozsah zde je herní.",
            "effects": {
              "treasury": -3,
              "order": 8,
              "people": -12,
              "favor": 2
            }
          },
          {
            "id": "borrow",
            "title": "Půjčit si od kupců",
            "text": "Zaplatit obnovu hned a dluh splatit z budoucího trhu.",
            "result": "Město se rozzáří, ale závazek zůstává.",
            "history": "Úvěr a zálohy od majetných měšťanů či kupců byly ve středověkých městech běžné. Konkrétní půjčka je herní.",
            "effects": {
              "treasury": -18,
              "order": 7,
              "people": 5,
              "favor": 9
            }
          }
        ]
      }
    ]
  },
  {
    "id": "trh",
    "label": "Výroční trh",
    "codexTitle": "Osmidenní výroční trh",
    "variants": [
      {
        "eyebrow": "PĚT TÝDNŮ DO PŘÍJEZDU",
        "title": "Kupci chtějí místo na náměstí",
        "text": "Zpráva o císařově návštěvě láká obchodníky. Stánků je víc než bezpečného prostoru.",
        "illustration": "market",
        "choices": [
          {
            "id": "market-fees",
            "title": "Dražit nejlepší místa",
            "text": "Nechat kupce přihazovat za stánky u radnice.",
            "result": "Pokladna se plní, menší obchodníci zůstávají stranou.",
            "history": "Karel IV. spojil svou kadaňskou návštěvu s privilegiem výročního trhu. Rozdělení míst dražbou je herní rekonstrukce.",
            "effects": {
              "treasury": 16,
              "supplies": 3,
              "order": 2,
              "people": -7,
              "favor": 4
            }
          },
          {
            "id": "market-balance",
            "title": "Rozdělit místa losem",
            "text": "Část míst vyhradit domácím, část hostům.",
            "result": "Trh je pestrý a napětí klesá.",
            "history": "Výroční trhy přiváděly do měst cizí kupce a podporovaly místní řemesla. Přesný kadaňský organizační řád zde není doložen.",
            "effects": {
              "treasury": 5,
              "supplies": 8,
              "order": 5,
              "people": 7,
              "favor": 3
            }
          },
          {
            "id": "market-open",
            "title": "Rozšířit trh do ulic",
            "text": "Povolit stánky i mimo náměstí a posílit hlídky.",
            "result": "Město žije obchodem, ale hlídky nestíhají.",
            "history": "Rozšíření trhu do přilehlých ulic je uvěřitelná, nikoli doložená situace.",
            "effects": {
              "treasury": 10,
              "supplies": 10,
              "order": -10,
              "people": 5,
              "favor": 5
            }
          }
        ]
      },
      {
        "eyebrow": "PĚT TÝDNŮ DO PŘÍJEZDU",
        "title": "Přicházejí první cizí obchodníci",
        "text": "Město může vydělat, ale ceny obilí a masa začínají růst.",
        "illustration": "caravan",
        "choices": [
          {
            "id": "price-cap",
            "title": "Omezit nejvyšší ceny",
            "text": "Stanovit cenové stropy na základní potraviny.",
            "result": "Obyvatelé jásají, část kupců odjíždí.",
            "history": "Městské autority regulovaly některé ceny a míry. Konkrétní strop je herní rozhodnutí.",
            "effects": {
              "treasury": -4,
              "supplies": -5,
              "order": 8,
              "people": 13,
              "favor": -2
            }
          },
          {
            "id": "buy-reserve",
            "title": "Vykoupit zásoby předem",
            "text": "Město nakoupí obilí a maso do rezervy.",
            "result": "Zásoby jsou bezpečné, pokladna téměř prázdná.",
            "history": "Tvorba městských zásob je historicky uvěřitelná. Přesná kadaňská akce není doložena.",
            "effects": {
              "treasury": -17,
              "supplies": 18,
              "order": 4,
              "people": 7,
              "favor": 2
            }
          },
          {
            "id": "free-market",
            "title": "Nechat obchod volný",
            "text": "Spolehnout se, že konkurence ceny srazí.",
            "result": "Kupci přijíždějí, chudší domácnosti však strádají.",
            "history": "Tržní soutěž i městská regulace vedle sebe ve středověku existovaly. Výsledek je modelovaný.",
            "effects": {
              "treasury": 8,
              "supplies": 8,
              "order": -5,
              "people": -10,
              "favor": 6
            }
          }
        ]
      }
    ]
  },
  {
    "id": "brany",
    "label": "Brány a hradby",
    "codexTitle": "Opevněná Kadaň",
    "variants": [
      {
        "eyebrow": "ČTYŘI TÝDNY DO PŘÍJEZDU",
        "title": "Noční hlídka našla slabé místo",
        "text": "U jedné brány se uvolnilo zdivo. Oprava zbrzdí dopravu na trh.",
        "illustration": "gate",
        "choices": [
          {
            "id": "close-gate",
            "title": "Bránu dočasně uzavřít",
            "text": "Přesměrovat povozy a opravit zdivo pořádně.",
            "result": "Bezpečnost roste, kupci čekají ve frontách.",
            "history": "Kadaň byla opevněným městem. Konkrétní porucha brány je herní rekonstrukce.",
            "effects": {
              "treasury": -9,
              "order": 14,
              "supplies": -6,
              "people": -2,
              "favor": 4
            }
          },
          {
            "id": "quick-fix",
            "title": "Provést jen rychlou opravu",
            "text": "Zpevnit nejnutnější část a provoz nepřerušovat.",
            "result": "Trh pokračuje, ale hlídka zůstává nervózní.",
            "history": "Provizorní opravy jsou obecně věrohodné, nikoli konkrétně doložené.",
            "effects": {
              "treasury": -4,
              "order": -5,
              "supplies": 6,
              "people": 4,
              "favor": 2
            }
          },
          {
            "id": "merchant-help",
            "title": "Požádat kupce o vozy a lidi",
            "text": "Za pomoc jim odpustit část poplatků.",
            "result": "Brána je opravena bez velkého výdaje, pokladna ale přijde o příjem.",
            "history": "Městská obec mohla směňovat výsady za pomoc. Tato dohoda je autorská.",
            "effects": {
              "treasury": -8,
              "order": 9,
              "supplies": 3,
              "people": 3,
              "favor": 3
            }
          }
        ]
      },
      {
        "eyebrow": "ČTYŘI TÝDNY DO PŘÍJEZDU",
        "title": "Strážní žádají posily",
        "text": "Příliv návštěvníků znamená víc sporů, krádeží a neznámých lidí u bran.",
        "illustration": "watch",
        "choices": [
          {
            "id": "hire-watch",
            "title": "Najmout další strážné",
            "text": "Zaplatit zkušené muže na dobu trhu.",
            "result": "Ulice jsou klidnější, náklady rostou.",
            "history": "Dočasné posílení městské stráže je historicky pravděpodobné. Konkrétní počet není znám.",
            "effects": {
              "treasury": -13,
              "order": 16,
              "people": 5,
              "favor": 4
            }
          },
          {
            "id": "citizen-watch",
            "title": "Zapojit měšťany do hlídek",
            "text": "Rozdělit noční služby mezi domy.",
            "result": "Pořádek se zlepšuje, lidé jsou unavení.",
            "history": "Měšťané se podíleli na obraně města. Rozpis služeb je herní.",
            "effects": {
              "treasury": -3,
              "order": 11,
              "people": -8,
              "favor": 2
            }
          },
          {
            "id": "trust-gates",
            "title": "Spolehnout se na stávající stráž",
            "text": "Ušetřit peníze a nechat brány v běžném režimu.",
            "result": "Pokladna si oddechne, drobné krádeže však přibývají.",
            "history": "Výsledek je herní model, nikoli popis doložené události.",
            "effects": {
              "treasury": 8,
              "order": -14,
              "people": -5,
              "favor": -3
            }
          }
        ]
      }
    ]
  },
  {
    "id": "hostina",
    "label": "Zásoby a nocleh",
    "codexTitle": "Péče o císařskou družinu",
    "variants": [
      {
        "eyebrow": "TŘI TÝDNY DO PŘÍJEZDU",
        "title": "Družina bude větší, než se čekalo",
        "text": "Posel hlásí desítky dalších koní a služebníků. Město musí rychle najít jídlo i lůžka.",
        "illustration": "feast",
        "choices": [
          {
            "id": "grand-feast",
            "title": "Připravit velkolepou hostinu",
            "text": "Nakoupit nejlepší maso, víno a koření.",
            "result": "Císařští poslové jsou nadšeni, městská pokladna krvácí.",
            "history": "Hostiny byly součástí reprezentace panovníka i města. Konkrétní jídelníček je herní.",
            "effects": {
              "treasury": -20,
              "supplies": -12,
              "people": 2,
              "favor": 18,
              "order": 2
            }
          },
          {
            "id": "civic-hosting",
            "title": "Rozdělit hosty mezi domy",
            "text": "Majetnější domácnosti ubytují členy družiny.",
            "result": "Město nápor zvládne, ne všichni hostitelé jsou spokojeni.",
            "history": "Ubytovací povinnost patřila k možným břemenům návštěvy panovníka. Přesný kadaňský rozpis není doložen.",
            "effects": {
              "treasury": -6,
              "supplies": -8,
              "people": -5,
              "favor": 10,
              "order": 5
            }
          },
          {
            "id": "modest-table",
            "title": "Nabídnout střídmé pohoštění",
            "text": "Dát přednost dostatku před okázalostí.",
            "result": "Nikdo nehladoví, dvůr však velkolepost nevidí.",
            "history": "Střídmá varianta je herní protiklad k reprezentativní hostině.",
            "effects": {
              "treasury": -8,
              "supplies": -4,
              "people": 7,
              "favor": -6,
              "order": 4
            }
          }
        ]
      },
      {
        "eyebrow": "TŘI TÝDNY DO PŘÍJEZDU",
        "title": "Ve skladech chybí oves pro koně",
        "text": "Bez krmiva se císařská družina neobejde. Okolní vesnice však samy nemají přebytek.",
        "illustration": "stable",
        "choices": [
          {
            "id": "buy-far",
            "title": "Nakoupit oves z větší dálky",
            "text": "Poslat povozy a zaplatit vyšší cenu.",
            "result": "Krmiva je dost, ale cesta spolykala peníze.",
            "history": "Dálkový obchod doplňoval místní zdroje. Konkrétní trasa je herní.",
            "effects": {
              "treasury": -16,
              "supplies": 15,
              "favor": 6,
              "order": 2
            }
          },
          {
            "id": "ration",
            "title": "Nařídit příděly",
            "text": "Omezit spotřebu ve městě a vytvořit rezervu pro návštěvu.",
            "result": "Zásoby vydrží, obyvatelé to považují za nespravedlivé.",
            "history": "Přídělové hospodaření je obecně možné; tato epizoda je herní.",
            "effects": {
              "supplies": 10,
              "order": 6,
              "people": -13,
              "favor": 5
            }
          },
          {
            "id": "ask-monastery",
            "title": "Požádat církevní statky o pomoc",
            "text": "Vyměnit budoucí výhodu za okamžité zásoby.",
            "result": "Pomoc přijde včas, ale město se zaváže.",
            "history": "Vztahy měst s církevními institucemi byly významné. Konkrétní dohoda je autorská.",
            "effects": {
              "treasury": -6,
              "supplies": 12,
              "people": 3,
              "favor": 4
            }
          }
        ]
      }
    ]
  }
];
