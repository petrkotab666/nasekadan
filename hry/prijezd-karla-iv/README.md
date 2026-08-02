# Příjezd císaře: Kadaň 1367 — pracovní verze v2

Tato verze je vyvíjena odděleně od veřejného webu. Stránka má `noindex,nofollow,noarchive`, není vložena do titulní strany, navigace ani sitemap a nesmí být nasazena bez samostatného rozhodnutí a závěrečného veřejného ověření.

## Co hra obsahuje

- historický prolog vysvětlující požár roku 1362, pětiletou obnovu a důvod příprav;
- osm kapitol, šestnáct scén a čtyřicet osm rozhodnutí;
- tři obtížnosti a pět vzájemně provázaných ukazatelů;
- volnou kroniku s proměnlivými scénami a stabilní denní výzvu;
- nenadálé události, několik typů zakončení a devět úspěchů;
- kroniku historických stop, souhrn všech rozhodnutí a sdílení výsledku;
- automatické uložení, pokračování, osobní rekordy a denní sérii;
- ovládání klávesami 1–3, omezení pohybu, větší text a volitelný zvuk;
- provoz bez registrace, serverového účtu a osobních údajů.

Historická fakta a autorská rekonstrukce jsou v textech oddělené. Hra nesmí tvrdit jako doložený fakt konkrétní situaci, rozhovor nebo rozhodnutí, které prameny nepotvrzují.

## Kontroly

```bash
node --check hry/prijezd-karla-iv/game.js
node --test tests/prijezd-cisare-engine.test.mjs tests/prijezd-cisare-static.test.mjs
```

Před případným zveřejněním je nutné navíc provést celý průchod na desktopu i mobilu, ověřit ukládání po obnovení stránky, dialogy, klávesnici, sdílení, sociální kartu a teprve potom samostatně připravit integraci do webu.
