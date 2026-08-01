#!/usr/bin/env python3
from pathlib import Path

PATH = Path('.github/drafts/cisarsky-den-kadan-historie-2026.html')
text = PATH.read_text(encoding='utf-8')

if 'data-kadan-development="1367-2026"' in text:
    print('Vývojová kapitola je již vložena.')
    raise SystemExit(0)

css_anchor = '    .source-list{margin-top:44px;padding:24px;border-radius:18px;background:#eef3f5}'
css_extra = '''    .city-arc{margin:44px 0;padding:30px;border-radius:24px;background:linear-gradient(145deg,#eef3f5,#fff 48%,#f7efe3);border:1px solid #d6dfe2}.city-arc>small{display:block;color:#9f2626;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.city-arc>h2{margin:7px 0 12px!important}.city-arc>p{max-width:760px}.era-line{margin:34px 0;padding-left:28px;border-left:4px solid #c9a45a}.era{position:relative;padding:0 0 30px}.era:before{content:'';position:absolute;left:-38px;top:8px;width:16px;height:16px;border-radius:50%;background:#9f2626;border:4px solid #fff;box-shadow:0 0 0 1px #9f2626}.era:last-child{padding-bottom:0}.era time{display:block;color:#9f2626;font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.era h3{margin:4px 0 8px}.era p{margin:0}.era-note{margin-top:11px;padding:14px 16px;border-radius:13px;background:#fff;border:1px solid #dbe2e5;font-size:15px;color:#53616a}.two-identities{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:28px 0}.two-identities>div{padding:23px;border-radius:18px;background:#fff;border:1px solid #dbe2e5}.two-identities h3{margin:0 0 9px}.two-identities p{margin:0;font-size:16px}.royal{border-top:5px solid #9f2626!important}.energy{border-top:5px solid #315d70!important}@media(max-width:700px){.two-identities{grid-template-columns:1fr}}\n'''
if css_anchor not in text:
    raise SystemExit('Chybí CSS kotva.')
text = text.replace(css_anchor, css_extra + css_anchor, 1)

anchor = '  <h2>Proč slavnost přežila více než tři desetiletí</h2>'
section = '''  <section class="city-arc" data-kadan-development="1367-2026">
    <small>Od císařovy návštěvy k dnešnímu městu</small>
    <h2>Kadaň se nevyvíjela rovně. Opakovaně se znovu stavěla</h2>
    <p>Dějiny Kadaně nejsou příběhem nepřetržitého růstu. Město několikrát vyhořelo, bylo dobyto, vyrabováno, vylidněno a přestavěno. Každá etapa však zanechala vrstvu, kterou lze ve městě číst dodnes.</p>

    <div class="era-line">
      <div class="era"><time>1367–1374</time><h3>Královské město na vrcholu sebevědomí</h3><p>Karel IV. přijel do města krátce po velkém požáru z roku 1362. Kadaň byla obnovena z kamene, měla nové opevnění, radnici a silnou samosprávu. Výroční trh, mílové právo a pozdější vinařské privilegium posilovaly její obchod, řemesla a příjmy.</p></div>

      <div class="era"><time>1421</time><h3>Husitská válka přinesla dvojí dobytí</h3><p>Na jaře město dobyli Pražané a připojili je k pražskému městskému svazu. Už na podzim Kadaň obsadila vojska druhé křížové výpravy. Město poté zůstalo na katolické straně až do konce husitských válek.</p></div>

      <div class="era"><time>1469–1519</time><h3>Lobkovicové a pozdně gotická proměna</h3><p>Kadaň byla padesát let v zástavním držení rodu Lobkoviců. Jan Hasištejnský z Lobkovic a jeho bratři podporovali výstavbu františkánského kláštera. Kolem roku 1500 se město rozšířilo na západ a vznikala podoba pozdně gotické Kadaně, jejíž stopy dodnes určují centrum.</p><div class="era-note">Právě z této doby pochází i kamenná radniční věž, která se stala symbolem městské hrdosti.</div></div>

      <div class="era"><time>1534</time><h3>Kadaňský mír dostal město do evropské politiky</h3><p>V Kadani jednali král Ferdinand Habsburský a württemberský vévoda Oldřich. Výsledná dohoda známá jako Kadaňský mír patřila k významným událostem reformace a ukázala, že město stále mohlo být místem vysoké politiky.</p></div>

      <div class="era"><time>1618–1648</time><h3>Třicetiletá válka město zlomila</h3><p>Po stavovském povstání následovala rekatolizace, drancování a opakované požáry. Roku 1631 a 1635 byla Kadaň vydrancována a vypálena; švédský vpád roku 1648 zničil zejména hradní komplex.</p></div>

      <div class="era"><time>1750–1765</time><h3>Z královského hradu se stala kasárna</h3><p>Za Marie Terezie byl zničený hrad přestavěn na vojenská kasárna. Tím se změnila jeho role z panovnického sídla na vojenský objekt. Armáda zde působila ještě na počátku první světové války.</p></div>

      <div class="era"><time>19. století</time><h3>Město vystoupilo z hradeb</h3><p>Ve 30. letech začalo bourání bran a částí opevnění. Roku 1850 se Kadaň stala sídlem okresních úřadů a začala rychleji růst. Vznikly Smetanovy sady, vilová čtvrť směrem k Ohři a nové veřejné budovy. Roku 1904 se město připojilo místní železnicí k síti Buštěhradské dráhy.</p></div>

      <div class="era"><time>1919</time><h3>Masakr na náměstí rozdělil paměť města</h3><p>Dne 4. března při demonstraci německého obyvatelstva zahájili českoslovenští vojáci palbu. Nejméně 25 lidí zemřelo a desítky byly zraněny. Událost zůstává jedním z nejcitlivějších bodů moderních dějin Kadaně.</p></div>

      <div class="era"><time>1938–1945</time><h3>Nacistická okupace a zničení židovské komunity</h3><p>Po Mnichovské dohodě byla Kadaň připojena k Třetí říši. Během Křišťálové noci shořela synagoga a židovští obyvatelé byli pronásledováni a deportováni. Dne 8. května 1945 vstoupila do města sovětská armáda.</p></div>

      <div class="era"><time>Po roce 1945</time><h3>Odsun změnil obyvatelstvo téměř přes noc</h3><p>Tisíce německých obyvatel byly odsunuty a poloprázdný region byl dosidlován lidmi z různých částí Československa. Přetrhla se část rodinných, jazykových i řemeslných tradic a město získalo nové obyvatelstvo i novou identitu.</p></div>

      <div class="era"><time>60.–80. léta</time><h3>Elektrárny a panelová výstavba vytvořily novou Kadaň</h3><p>Elektrárna Tušimice I zahájila výrobu v letech 1963–1964, Tušimice II v letech 1974–1975 a Prunéřov II v letech 1981–1982. Průmysl přivedl pracovníky, urychlil výstavbu sídlišť a proměnil Kadaň v energetické centrum. Zároveň zanedbané historické čtvrti chátraly, některé domy byly demolovány a centrum se vylidňovalo.</p><div class="era-note">Roku 1978 bylo historické jádro vyhlášeno městskou památkovou rezervací. Ochrana přišla ve chvíli, kdy byla část staré zástavby už vážně ohrožena.</div></div>

      <div class="era"><time>Po roce 1989</time><h3>Návrat života do historického centra</h3><p>Začala obnova radnice, hradeb, náměstí, kláštera i měšťanských domů. Z chátrajícího jádra se postupně znovu stalo centrum služeb, kultury a turistického života. Od počátku 90. let k této nové identitě patří také Císařský den.</p></div>

      <div class="era"><time>2025–2026</time><h3>Historické město hledá místo po uhlí</h3><p>Kadaň byla krajským vítězem soutěže Historické město roku 2025 díky obnově Mikulovické brány a domů na náměstí. Současně řeší proměnu energetiky: Tušimice stále zásobují město teplem, ale připravuje se nový horkovod z Prunéřova s dokončením plánovaným do konce roku 2027.</p></div>
    </div>

    <h2>Dvě identity dnešní Kadaně</h2>
    <div class="two-identities">
      <div class="royal"><h3>Královské a historické město</h3><p>Hrad, opevnění, klášter, radniční věž, památková rezervace a slavnosti připomínající Karla IV.</p></div>
      <div class="energy"><h3>Energetické a průmyslové město</h3><p>Elektrárny, teplárenství, sídliště, pracovní migrace a dnešní hledání nové ekonomiky po postupném útlumu uhlí.</p></div>
    </div>
    <p>Právě napětí mezi těmito dvěma identitami vysvětluje dnešní Kadaň lépe než samotný seznam památek. Město není jen zachovaný středověk ani jen průmyslové sídlo. Je výsledkem obou příběhů.</p>
  </section>

'''
if anchor not in text:
    raise SystemExit('Chybí obsahová kotva.')
text = text.replace(anchor, section + anchor, 1)

# Doplnit zdroje.
source_marker = '    <small>Před vydáním aktualizovat kompletní program'
if source_marker in text and 'Historické město roku 2025' not in text:
    links = '''      <li><a href="https://kadan.eu/kadan-historicka/" target="_blank" rel="noopener">Oficiální historie města od středověku po obnovu po roce 1989</a></li>\n      <li><a href="https://www.pamatkovykatalog.cz/kadan-mestska-pamatkova-rezervace-7663598" target="_blank" rel="noopener">Památkový katalog – urbanistický vývoj Kadaně</a></li>\n      <li><a href="https://www.npu.cz/cs/uop-usti-nad-labem/pro-media/131501-kadan-se-stava-historickym-mestem-roku-2025" target="_blank" rel="noopener">NPÚ – krajský vítěz Historické město roku 2025</a></li>\n      <li><a href="https://www.cez.cz/cs/o-cez/vyrobni-zdroje/uhelne-elektrarny-a-teplarny/uhelne-elektrarny-a-teplarny-cez-v-cr/elektrarny-tusimice-58175" target="_blank" rel="noopener">ČEZ – historie elektráren Tušimice</a></li>\n      <li><a href="https://www.cez.cz/nextcez/cs/pro-media/tiskove-zpravy/bykovi-se-za-jeho-kravkami-nechtelo-a-tak-na-malou-chvili-zbrzdil-realizaci-horkovodu-z-elektrarny-prunerov-do-kadane-ta-je-jiz-v-plnem-proudu-235288" target="_blank" rel="noopener">ČEZ – nový horkovod z Prunéřova do Kadaně</a></li>\n'''
    pos = text.find(source_marker)
    text = text[:pos] + links + text[pos:]

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Kapitola o vývoji Kadaně byla vložena.')
