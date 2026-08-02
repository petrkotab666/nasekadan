export const CHAPTERS_B = [
  {
    "id": "poradek",
    "label": "Čistota a voda",
    "codexTitle": "Každodennost středověkého města",
    "variants": [
      {
        "eyebrow": "DVA TÝDNY DO PŘÍJEZDU",
        "title": "Ulice jsou plné bláta a odpadu",
        "text": "Po dešti se tržiště mění v bahno. Hrozí ostuda i nemoc.",
        "illustration": "street",
        "choices": [
          {
            "id": "clean-all",
            "title": "Zaplatit velký úklid",
            "text": "Najmout povozy a odvézt nečistoty za hradby.",
            "result": "Město voní lépe a návštěvníci si toho všimnou.",
            "history": "Městské vyhlášky regulovaly nečistoty, odpad a průjezdnost ulic. Rozsah úklidu je herní.",
            "effects": {
              "treasury": -12,
              "order": 12,
              "people": 7,
              "favor": 7
            }
          },
          {
            "id": "house-duty",
            "title": "Přikázat úklid před každým domem",
            "text": "Každý odpovídá za svůj úsek ulice.",
            "result": "Výsledek je rychlý, ale pokuty vyvolají spory.",
            "history": "Povinnost udržovat prostor před domem je historicky doložitelný typ městského pravidla. Konkrétní kadaňský příkaz zde není citován.",
            "effects": {
              "order": 10,
              "people": -5,
              "favor": 4,
              "treasury": 2
            }
          },
          {
            "id": "cover-mud",
            "title": "Překrýt nejhorší místa slámou",
            "text": "Zvolit levné provizorium před průvodem.",
            "result": "Hlavní trasa vypadá lépe, problém ale zůstává.",
            "history": "Použití organického materiálu na rozbahněných cestách je možné; tato scéna je herní.",
            "effects": {
              "treasury": -3,
              "order": 2,
              "people": 2,
              "favor": -2
            }
          }
        ]
      },
      {
        "eyebrow": "DVA TÝDNY DO PŘÍJEZDU",
        "title": "Studna na náměstí se kalí",
        "text": "Řemeslníci varují, že voda nemusí stačit návštěvníkům ani koním.",
        "illustration": "well",
        "choices": [
          {
            "id": "repair-well",
            "title": "Vyčistit a opravit studnu",
            "text": "Přerušit odběr a povolat zkušené řemeslníky.",
            "result": "Voda je čistší, ale město dva dny protestuje.",
            "history": "Studny byly zásadní součástí městské infrastruktury. Konkrétní oprava je herní.",
            "effects": {
              "treasury": -11,
              "supplies": 10,
              "order": 7,
              "people": 4,
              "favor": 4
            }
          },
          {
            "id": "water-carts",
            "title": "Vozit vodu z okolí",
            "text": "Organizovat nepřetržitou dopravu vody v sudech.",
            "result": "Návštěva je zajištěna, provoz je však drahý a chaotický.",
            "history": "Dovoz vody byl možným nouzovým řešením. Tato situace je autorská.",
            "effects": {
              "treasury": -14,
              "supplies": 8,
              "order": -4,
              "people": 5,
              "favor": 6
            }
          },
          {
            "id": "private-wells",
            "title": "Otevřít soukromé studny",
            "text": "Nařídit bohatším domům sdílení vody.",
            "result": "Vody je dost, vlastníci domů se cítí poškozeni.",
            "history": "Městská autorita mohla v krizi zasahovat do soukromých práv. Konkrétní nařízení je herní.",
            "effects": {
              "supplies": 8,
              "order": 5,
              "people": -7,
              "favor": 3
            }
          }
        ]
      }
    ]
  },
  {
    "id": "spor",
    "label": "Soud a pořádek",
    "codexTitle": "Městská spravedlnost",
    "variants": [
      {
        "eyebrow": "TÝDEN DO PŘÍJEZDU",
        "title": "Kupci se poprali kvůli místu",
        "text": "Jeden je vlivný host, druhý oblíbený kadaňský řemeslník. Dav čeká na rozsudek.",
        "illustration": "court",
        "choices": [
          {
            "id": "strict-law",
            "title": "Potrestat oba stejně",
            "text": "Udělit pokutu bez ohledu na postavení.",
            "result": "Rozsudek působí spravedlivě, cizí kupec vyhrožuje odjezdem.",
            "history": "Městské soudnictví chránilo pořádek a obchod. Konkrétní spor je smyšlený.",
            "effects": {
              "treasury": 5,
              "order": 13,
              "people": 8,
              "supplies": -3,
              "favor": -2
            }
          },
          {
            "id": "protect-guest",
            "title": "Ustoupit významnému hostu",
            "text": "Potrestat domácího řemeslníka a zachovat obchodní vztahy.",
            "result": "Kupci zůstávají, obyvatelé zuří.",
            "history": "Zvýhodnění vlivného hosta je herní morální dilema, nikoli doložený rozsudek.",
            "effects": {
              "treasury": 8,
              "order": -7,
              "people": -14,
              "favor": 7,
              "supplies": 4
            }
          },
          {
            "id": "mediate",
            "title": "Vynutit veřejné smíření",
            "text": "Oba zaplatí škodu a společně podpoří městskou chudinu.",
            "result": "Dav přijme kompromis a spor se stane poučením.",
            "history": "Smír patřil vedle trestu k možným způsobům řešení konfliktů. Přesná forma je autorská.",
            "effects": {
              "treasury": 2,
              "order": 8,
              "people": 10,
              "favor": 3
            }
          }
        ]
      },
      {
        "eyebrow": "TÝDEN DO PŘÍJEZDU",
        "title": "Po městě se šíří zvěst o zlodějích",
        "text": "Několik hostů přišlo o měšce. Stráž chce prohledávat příchozí u bran.",
        "illustration": "thief",
        "choices": [
          {
            "id": "search-all",
            "title": "Zavést přísné kontroly",
            "text": "Prohledávat povozy i zavazadla.",
            "result": "Krádeže klesnou, fronty a ponížení rostou.",
            "history": "Kontroly u bran byly součástí městského dohledu. Zvolená intenzita je herní.",
            "effects": {
              "order": 15,
              "supplies": -6,
              "people": -8,
              "favor": 2,
              "treasury": -3
            }
          },
          {
            "id": "plainclothes",
            "title": "Nasadit nenápadné hlídky",
            "text": "Strážní se vmísí mezi návštěvníky.",
            "result": "Několik pachatelů je chyceno bez velkého rozruchu.",
            "history": "Nenápadné hlídky jsou autorským prvkem; hra tím modeluje kompromis mezi bezpečností a volným obchodem.",
            "effects": {
              "order": 10,
              "treasury": -8,
              "people": 4,
              "favor": 4
            }
          },
          {
            "id": "reward-info",
            "title": "Vypsat odměnu za informace",
            "text": "Zaplatit tomu, kdo přivede pachatele.",
            "result": "Město získá svědky, ale také mnoho falešných obvinění.",
            "history": "Odměny za dopadení pachatelů jsou historicky možné. Následky jsou herní.",
            "effects": {
              "treasury": -7,
              "order": 6,
              "people": -3,
              "favor": 2
            }
          }
        ]
      }
    ]
  },
  {
    "id": "prijezd",
    "label": "Císař před branami",
    "codexTitle": "Karel IV. v Kadani roku 1367",
    "variants": [
      {
        "eyebrow": "DEN PŘÍJEZDU",
        "title": "Císařská korouhev je na obzoru",
        "text": "Průvod dorazil dřív. Část výzdoby není hotová a obyvatelé se tlačí u brány.",
        "illustration": "arrival",
        "choices": [
          {
            "id": "ceremony",
            "title": "Zdržet průvod slavnostním uvítáním",
            "text": "Získat čas dlouhým projevem a ceremonií.",
            "result": "Řečník zachrání situaci a město dokončí poslední přípravy.",
            "history": "Ceremoniální uvítání panovníka odpovídá dobové reprezentaci. Konkrétní projev je smyšlený.",
            "effects": {
              "treasury": -4,
              "order": 4,
              "people": 6,
              "favor": 12
            }
          },
          {
            "id": "open-gates",
            "title": "Otevřít brány bez prodlení",
            "text": "Přiznat, že město není dokonalé, ale je připravené sloužit.",
            "result": "Upřímnost působí dobře, nepořádek je však vidět.",
            "history": "Přesný průběh příjezdu není v této hře rekonstruován jako doložený fakt.",
            "effects": {
              "order": -5,
              "people": 8,
              "favor": 5,
              "treasury": 2
            }
          },
          {
            "id": "clear-square",
            "title": "Vyklidit náměstí silou",
            "text": "Uvolnit cestu a skrýt nedokončené stánky.",
            "result": "Průvod projede hladce, dav si pamatuje hrubost.",
            "history": "Zásah stráže je herní dramatizace.",
            "effects": {
              "order": 11,
              "people": -12,
              "favor": 8,
              "treasury": -2
            }
          }
        ]
      },
      {
        "eyebrow": "DEN PŘÍJEZDU",
        "title": "Město musí předat císaři dar",
        "text": "Rada se nemůže shodnout, zda má být dar drahý, praktický, nebo symbolický.",
        "illustration": "gift",
        "choices": [
          {
            "id": "silver-gift",
            "title": "Darovat stříbrnou číši",
            "text": "Zaplatit reprezentativní dar z městské pokladny.",
            "result": "Dar vzbudí obdiv, účetní však zbledne.",
            "history": "Dary patřily k politické reprezentaci. Konkrétní číše je herní.",
            "effects": {
              "treasury": -18,
              "favor": 17,
              "people": -2,
              "order": 2
            }
          },
          {
            "id": "local-craft",
            "title": "Darovat práci kadaňských řemeslníků",
            "text": "Předat soubor výrobků místních mistrů.",
            "result": "Císař pozná schopnosti města a řemeslníci získají prestiž.",
            "history": "Prezentace místních řemesel je uvěřitelná autorská rekonstrukce.",
            "effects": {
              "treasury": -8,
              "favor": 11,
              "people": 9,
              "supplies": -3
            }
          },
          {
            "id": "charity-gift",
            "title": "Požádat o ochranu trhu místo daru",
            "text": "Předat skromný dar a zdůraznit potřeby města.",
            "result": "Dvůr ocení odvahu, část rady to považuje za risk.",
            "history": "Vyjednávání privilegií bylo podstatou vztahu měst a panovníka. Konkrétní scéna je smyšlená.",
            "effects": {
              "treasury": 3,
              "favor": 7,
              "people": 6,
              "order": -3
            }
          }
        ]
      }
    ]
  },
  {
    "id": "privilegium",
    "label": "Poslední rada",
    "codexTitle": "Privilegium a paměť města",
    "variants": [
      {
        "eyebrow": "POSLEDNÍ VEČER",
        "title": "Císař se ptá, co město potřebuje",
        "text": "Rada má jedinou příležitost doporučit, jakou podporu má panovník Kadani dát.",
        "illustration": "charter",
        "choices": [
          {
            "id": "annual-market",
            "title": "Žádat výroční trh",
            "text": "Prosadit několikadenní obchodní událost pro kupce zblízka i zdaleka.",
            "result": "Město získá dlouhodobou obchodní příležitost.",
            "history": "Karel IV. v roce 1367 Kadani skutečně udělil privilegium osmidenního výročního trhu. Herní je způsob, jakým k rozhodnutí dochází.",
            "effects": {
              "treasury": 10,
              "supplies": 7,
              "people": 7,
              "favor": 9,
              "order": 2
            }
          },
          {
            "id": "fortification",
            "title": "Žádat podporu opevnění",
            "text": "Upřednostnit bezpečnost a dlouhodobou obranu.",
            "result": "Hradby získají pozornost, obchodníci čekali víc.",
            "history": "Podpora opevnění je alternativní herní historie. Skutečnou stopou roku 1367 je výroční trh.",
            "effects": {
              "treasury": -2,
              "order": 15,
              "people": 3,
              "favor": 5,
              "supplies": -2
            }
          },
          {
            "id": "tax-relief",
            "title": "Žádat dočasnou úlevu",
            "text": "Pomoci obyvatelům po nákladných přípravách.",
            "result": "Lidé slaví, městská rada však ztrácí část budoucích příjmů.",
            "history": "Daňová úleva je herní alternativa, nikoli tvrzení o privilegiu z roku 1367.",
            "effects": {
              "treasury": -10,
              "people": 16,
              "favor": 4,
              "order": 3
            }
          }
        ]
      },
      {
        "eyebrow": "POSLEDNÍ VEČER",
        "title": "Kronikář čeká na poslední zápis",
        "text": "Jak má být návštěva zachována v paměti města?",
        "illustration": "chronicle",
        "choices": [
          {
            "id": "truthful-record",
            "title": "Zapsat úspěchy i chyby",
            "text": "Nechat budoucím generacím poctivou zprávu.",
            "result": "Kronika nepůsobí dokonale, ale je důvěryhodná.",
            "history": "Dochované prameny jsou výběrové a jejich interpretace vyžaduje opatrnost. Tato volba připomíná rozdíl mezi dějinami a legendou.",
            "effects": {
              "people": 8,
              "order": 6,
              "favor": 3,
              "treasury": 2
            }
          },
          {
            "id": "glorious-record",
            "title": "Zapsat jen velkolepý triumf",
            "text": "Vytvořit příběh bez sporů a nedostatků.",
            "result": "Legenda roste, paměť se vzdaluje skutečnosti.",
            "history": "Idealizace panovnických návštěv patří k tradiční reprezentaci. Konkrétní kronikář je smyšlený.",
            "effects": {
              "favor": 11,
              "people": 2,
              "order": -3,
              "treasury": 3
            }
          },
          {
            "id": "people-record",
            "title": "Nechat promluvit obyvatele",
            "text": "Zapsat zkušenosti řemeslníků, žen, strážných i kupců.",
            "result": "Vzniká neobvyklá mnohovrstevná paměť města.",
            "history": "Hlas běžných obyvatel je ve středověkých pramenech zachycen nerovnoměrně. Volba je moderní herní perspektivou.",
            "effects": {
              "people": 13,
              "favor": 4,
              "order": 2,
              "treasury": -2
            }
          }
        ]
      }
    ]
  }
];
