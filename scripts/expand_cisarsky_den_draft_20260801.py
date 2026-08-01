#!/usr/bin/env python3
from pathlib import Path

PATH = Path('.github/drafts/cisarsky-den-kadan-historie-2026.html')
text = PATH.read_text(encoding='utf-8')

if 'data-expanded-cisarsky-den="v2"' in text:
    print('Návrh je již rozšířený.')
    raise SystemExit(0)

# Rozšířené komponenty článku.
css_anchor = "    .program{display:grid;gap:12px;margin:28px 0}.program div{display:grid;grid-template-columns:90px 1fr;gap:16px;padding:19px 21px;border:1px solid var(--line);border-radius:16px;background:#fff}.program time{color:#9f2626;font-weight:900;font-size:20px}.program b{font:800 20px Georgia,serif}.program p{margin:4px 0 0;font-size:15px;color:var(--muted)}\n"
css_extra = """    .toc{margin:30px 0;padding:24px;border:1px solid var(--line);border-radius:18px;background:#f5f8f9}.toc strong{font:800 22px Georgia,serif}.toc ol{columns:2;gap:30px;margin-bottom:0}.toc li{font-size:15px;margin:8px 0}.toc a{text-decoration:none}\n    .fact-grid,.role-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;margin:28px 0}.fact-card,.role-card{padding:21px;border:1px solid var(--line);border-radius:17px;background:#fff;box-shadow:0 9px 25px rgba(18,35,45,.05)}.fact-card b,.role-card b{display:block;margin-bottom:6px;color:#9f2626;font:800 21px/1.18 Georgia,serif}.fact-card p,.role-card p{margin:0;font-size:15px;color:#53616a}\n    .factcheck{margin:34px 0;padding:24px;border:1px solid #c9d9df;border-radius:18px;background:#f1f7f9}.factcheck h3{margin:0 0 13px}.factcheck ul{margin-bottom:0}.factcheck li{margin-bottom:8px}\n    .route-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;margin:28px 0}.route-card{padding:20px;border:1px solid var(--line);border-radius:17px;background:#fff}.route-card small{display:block;color:#9f2626;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.route-card b{display:block;margin:5px 0;font:800 21px/1.15 Georgia,serif}.route-card p{margin:0;font-size:15px;color:#53616a}\n    .comparison{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:30px 0}.comparison>div{padding:23px;border-radius:18px;border:1px solid var(--line);background:#fff}.comparison h3{margin:0 0 11px}.comparison .history{border-top:5px solid #2f6e4f}.comparison .theatre{border-top:5px solid #9f2626}.comparison li{font-size:16px;margin-bottom:8px}\n    .practical{margin:34px 0;padding:25px;border-radius:19px;background:linear-gradient(135deg,#fff8e9,#eef4f6);border:1px solid #d8dfe2}.practical h2{margin:0 0 12px}.practical ul{columns:2;gap:30px}.practical li{font-size:16px;margin-bottom:8px}\n"""
if css_anchor not in text:
    raise SystemExit('Chybí CSS bod pro rozšíření.')
text = text.replace(css_anchor, css_anchor + css_extra, 1)
text = text.replace(
    "    @media(max-width:700px){.facts{grid-template-columns:1fr}.program div{grid-template-columns:1fr}.hero{min-height:315px}.hero:after{font-size:68px}.article h1{font-size:42px}.article .leadtext{font-size:20px}}",
    "    @media(max-width:700px){.facts,.fact-grid,.role-grid,.route-grid,.comparison{grid-template-columns:1fr}.program div{grid-template-columns:1fr}.toc ol,.practical ul{columns:1}.hero{min-height:315px}.hero:after{font-size:68px}.article h1{font-size:42px}.article .leadtext{font-size:20px}}",
    1,
)

facts_block = """  <div class=\"facts\">\n    <div><b>22. 8. 2026</b><span>datum letošního 34. ročníku</span></div>\n    <div><b>1367 a 1374</b><span>doložené návštěvy Karla IV. v Kadani</span></div>\n    <div><b>1992–1993</b><span>vznik námětu a začátek pravidelné slavnosti</span></div>\n    <div><b>600+ účinkujících</b><span>rozsah uváděný oficiální historií akce</span></div>\n  </div>\n"""
toc = """  <div class=\"toc\" data-expanded-cisarsky-den=\"v2\"><strong>Co v článku najdete</strong><ol><li><a href=\"#proc-kadan\">Proč byla Kadaň důležitá</a></li><li><a href=\"#navsteva-1367\">První návštěva roku 1367</a></li><li><a href=\"#navsteva-1374\">Druhá návštěva a vinohrady</a></li><li><a href=\"#vznik-slavnosti\">Vznik novodobé tradice</a></li><li><a href=\"#fakta-a-divadlo\">Historie versus stylizace</a></li><li><a href=\"#mesto-jeviste\">Osm míst jednoho příběhu</a></li><li><a href=\"#program-2026\">Program roku 2026</a></li><li><a href=\"#poradatelstvi\">Kdo akci pořádá</a></li></ol></div>\n"""
if facts_block not in text:
    raise SystemExit('Chybí blok základních faktů.')
text = text.replace(facts_block, facts_block + '\n' + toc, 1)

anchor = "  <h2>Co se v Kadani stalo roku 1367</h2>\n"
section = """  <h2 id=\"proc-kadan\">Proč byla Kadaň pro Karla IV. důležitá</h2>\n  <p>Kadaň nebyla ve 14. století okrajovým městečkem. Kolem roku 1260 ji Přemysl Otakar II. povýšil na královské město a stala se správním a hospodářským centrem Kadaňské župy. Jan Lucemburský roku 1319 potvrdil měšťanům jejich dřívější správní, soudní a hospodářská privilegia.</p>\n  <p>Také Karel IV. vnímal Kadaň jako důležitý opěrný bod Koruny české. V návrhu zemského zákoníku Majestas Carolina ji zařadil mezi devatenáct královských měst, která neměla být nikdy odloučena od koruny. Jeho návštěvy proto nebyly pouhou zdvořilostní zastávkou. Panovník zde několik dní úřadoval, řešil veřejné záležitosti a vydával listiny.</p>\n  <div class=\"fact-grid\">\n    <div class=\"fact-card\"><b>Královské město</b><p>Postavení města znamenalo vlastní správu, hospodářská práva a přímější vztah k panovníkovi.</p></div>\n    <div class=\"fact-card\"><b>Kadaňská župa</b><p>Město bylo správním centrem rozsáhlejšího regionu a důležitým bodem na cestách severozápadními Čechami.</p></div>\n    <div class=\"fact-card\"><b>Hrad jako kancelář</b><p>Při první návštěvě Karel IV. na kadaňském hradě několik dní skutečně úřadoval.</p></div>\n    <div class=\"fact-card\"><b>Město Koruny české</b><p>Majestas Carolina počítala s Kadaní mezi královskými městy, která neměla být zcizena.</p></div>\n  </div>\n\n  <h2 id=\"navsteva-1367\">Co se v Kadani stalo roku 1367</h2>\n"""
if anchor not in text:
    raise SystemExit('Chybí nadpis první návštěvy.')
text = text.replace(anchor, section, 1)

anchor = "  <div class=\"callout\"><strong>Císařský den není připomínkou smyšlené legendy</strong><p>Základní příběh vychází z archivně doloženého několikadenního pobytu Karla IV. ve městě. Slavnost jej převádí do podoby veřejného divadla, průvodu a císařského slyšení.</p></div>\n"
extra = """\n  <h3>Co přinesl osmidenní výroční trh</h3>\n  <p>Právo pořádat výroční trh nebylo jen čestným gestem. Několikadenní trh přiváděl do města obchodníky, řemeslníky a kupující z širšího okolí. Měšťané získávali další příležitost prodávat zboží, poskytovat ubytování a vybírat související poplatky. Pro královské město šlo o praktický nástroj hospodářského růstu.</p>\n  <p>Listina z 1. června 1367 se týkala venkovských statků kadaňských měšťanů. Ukazuje, že panovníkův pobyt zasahoval i do konkrétních majetkových a správních otázek, nikoli jen do slavnostních ceremonií.</p>\n  <div class=\"factcheck\"><h3>Tři události, které se často směšují</h3><ul><li><strong>4. ledna 1367:</strong> potvrzení mílového práva, vydané v Karlových Varech, nikoli při návštěvě Kadaně.</li><li><strong>29. května 1367:</strong> začátek doloženého pobytu a povolení osmidenního výročního trhu.</li><li><strong>1. června 1367:</strong> další kadaňská listina týkající se venkovských statků měšťanů.</li></ul></div>\n"""
if anchor not in text:
    raise SystemExit('Chybí historický callout.')
text = text.replace(anchor, anchor + extra, 1)

text = text.replace('  <h2>Druhá návštěva a počátek vinařské tradice</h2>\n', '  <h2 id="navsteva-1374">Druhá návštěva a počátek vinařské tradice</h2>\n', 1)
anchor = "  <p>S Karlovou dobou souvisí také potvrzení mílového práva z ledna 1367, které chránilo hospodářské postavení města. Tato listina však nebyla vydána při císařově pobytu v Kadani, nýbrž v Karlových Varech. Pro přesné vyprávění historie je proto důležité jednotlivé události nerozmělňovat do jediného příběhu.</p>\n"
extra = """  <p>Vinařské privilegium nebylo jen obecným souhlasem. Středověká pravidla podporovala zakládání vinic daňovými úlevami, stanovovala dohled perkmistra a nutila vlastníky vhodných pozemků půdu buď osázet, nebo ji přenechat jiným vinařům. Ochrana vinic byla na dnešní poměry mimořádně přísná.</p>\n  <p>Právě druhá Karlova návštěva vysvětluje, proč se k císařské tradici v Kadani přirozeně připojuje také víno. Městské vinice u františkánského kláštera tak nejsou pouze moderní turistickou dekorací, ale navazují na privilegium z roku 1374.</p>\n"""
if anchor not in text:
    raise SystemExit('Chybí závěr druhé návštěvy.')
text = text.replace(anchor, anchor + extra, 1)

text = text.replace('  <h2>Jak vznikla novodobá slavnost</h2>\n', '  <h2 id="vznik-slavnosti">Jak vznikla novodobá slavnost</h2>\n', 1)
anchor = "  </div>\n\n  <h2>Jak vypadá tradiční scénář</h2>\n"
section = """  </div>\n\n  <h2 id=\"fakta-a-divadlo\">Co je historický fakt a co divadelní stylizace</h2>\n  <p>Silnou stránkou slavnosti je, že skutečné dějiny nepředkládá jako školní výklad, ale převádí je do příběhu. Současně je dobré obě roviny rozlišovat. Z listin známe návštěvy, data a udělená práva. Podoba průvodu a veřejných scén je novodobým divadelním zpracováním.</p>\n  <div class=\"comparison\">\n    <div class=\"history\"><h3>Archivně doloženo</h3><ul><li>několikadenní pobyt od 29. května 1367</li><li>úřadování Karla IV. na kadaňském hradě</li><li>povolení osmidenního výročního trhu</li><li>listina z 1. června 1367</li><li>druhá návštěva a vinařské privilegium 8. září 1374</li></ul></div>\n    <div class=\"theatre\"><h3>Novodobé městské divadlo</h3><ul><li>předání vlády starostou císaři</li><li>přesná podoba a trasa průvodu</li><li>veřejné císařské slyšení na pódiu</li><li>inspekce tržiště a účast na kolbišti</li><li>večerní monolog, ohňová show a finále pod hradbami</li></ul></div>\n  </div>\n\n  <h2 id=\"mesto-jeviste\">Město se na jeden den mění v jeviště</h2>\n  <p>Císařský den není soustředěný do jednoho areálu. Jeho scénář využívá skutečnou podobu historické Kadaně. Průvod propojuje františkánský klášter s Mírovým náměstím, další program pokračuje na hradě, hradbách, Studentském náměstí a ve Smetanových sadech. Návštěvník tak při přesunu mezi scénami současně prochází městem.</p>\n\n  <h2>Jak vypadá tradiční scénář</h2>\n"""
if anchor not in text:
    raise SystemExit('Chybí místo za časovou osou.')
text = text.replace(anchor, section, 1)

anchor = "  <p>Následuje slavnostní ceremonie a císařské slyšení. Příběh připomíná privilegia a význam Kadaně v době Karla IV. Další části programu se odehrávají na hradě, hradbách a v parcích. Děti procházejí Sedmerem rytířských ctností, ve Smetanových sadech vzniká vojenské ležení a kolbiště a den tradičně uzavírá ohňový program a závěrečné loučení císaře s městem.</p>\n"
routes = """  <div class=\"route-grid\">\n    <div class=\"route-card\"><small>1 · Mírové náměstí</small><b>Hlavní scéna a tržiště</b><p>Ceremonie, císařské slyšení, hudba, řemesla a největší soustředění návštěvníků.</p></div>\n    <div class=\"route-card\"><small>2 · Žebrácká ulice</small><b>Kontrast středověkého města</b><p>Stylizovaná bída a pouliční obrazy vedoucí směrem ke hradu.</p></div>\n    <div class=\"route-card\"><small>3 · Kadaňský hrad</small><b>Místo skutečného pobytu</b><p>Nádvoří, kde se historická kulisa potkává s místem, na němž Karel IV. opravdu úřadoval.</p></div>\n    <div class=\"route-card\"><small>4 · Městské hradby</small><b>Sedmero rytířských ctností</b><p>Dětská cesta úkolů zakončená pasováním na rytíře nebo lady.</p></div>\n    <div class=\"route-card\"><small>5 · Ulice Jana Švermy</small><b>Hudba a pouliční divadlo</b><p>Spojovací tepna průvodu s kejklíři, muzikanty a diváky podél trasy.</p></div>\n    <div class=\"route-card\"><small>6 · Studentské náměstí</small><b>Klidnější rodinná zóna</b><p>Odpočinek a program pro děti mimo největší ruch hlavního náměstí.</p></div>\n    <div class=\"route-card\"><small>7 · Smetanovy sady</small><b>Kolbiště a vojenské ležení</b><p>Jezdecké turnaje, ukázky života v ležení, sokolníci a další atrakce.</p></div>\n    <div class=\"route-card\"><small>8 · Prostor pod hradbami</small><b>Večerní finále</b><p>Ohňový průvod, závěrečný císařův proslov a tradiční ukončení slavnosti.</p></div>\n  </div>\n"""
if anchor not in text:
    raise SystemExit('Chybí tradiční scénář.')
text = text.replace(anchor, anchor + routes, 1)

text = text.replace('  <h2>Co je zatím zveřejněno pro rok 2026</h2>\n', '  <h2 id="program-2026">Co je zatím zveřejněno pro rok 2026</h2>\n', 1)
anchor = "  <p>Další program má probíhat současně na několika místech. Počítá se s historickým tržištěm, dobovými řemesly, hudbou, pouličním divadlem, dětskými aktivitami a programem ve Smetanových sadech. Podrobný časový rozpis doplníme po jeho úplném zveřejnění.</p>\n"
practical = """  <div class=\"practical\"><h2>Co bude potřeba před akcí ještě ověřit</h2><ul><li>úplný program všech scén</li><li>čas otevření tržiště a jednotlivých zón</li><li>dopravní uzavírky v centru</li><li>možnosti parkování a příjezdové trasy</li><li>případné historické vlaky</li><li>vstupné nebo bezplatný režim jednotlivých částí</li><li>přístupnost pro kočárky a osoby s omezenou pohyblivostí</li><li>změny programu při nepříznivém počasí</li></ul></div>\n"""
if anchor not in text:
    raise SystemExit('Chybí závěr programu 2026.')
text = text.replace(anchor, anchor + practical, 1)

anchor = "  <h2>Proč slavnost přežila více než tři desetiletí</h2>\n"
roles = """  <h2 id=\"poradatelstvi\">Kdo Císařský den pořádá a kdo se na něm podílí</h2>\n  <p>Oficiálním pořadatelem a držitelem značky je město Kadaň. Kulturní zařízení Kadaň je partnerem a podílí se na produkčním a kulturním zajištění. Další partneři pomáhají s financováním, dopravou, propagací a jednotlivými programovými částmi.</p>\n  <div class=\"role-grid\">\n    <div class=\"role-card\"><b>Město Kadaň</b><p>Pořadatel slavnosti a držitel práv k označení CÍSAŘSKÝ DEN®.</p></div>\n    <div class=\"role-card\"><b>Kulturní zařízení Kadaň</b><p>Partner zajišťující významnou část kulturní produkce a městského zázemí.</p></div>\n    <div class=\"role-card\"><b>Stovky účinkujících</b><p>Historické skupiny, hudebníci, jezdci, šermíři, divadelníci, řemeslníci a další profese.</p></div>\n    <div class=\"role-card\"><b>Regionální zážitek</b><p>Slavnost nese certifikaci POOHŘÍ regionální produkt® s číslem 926009.</p></div>\n  </div>\n\n  <h2>Proč slavnost přežila více než tři desetiletí</h2>\n"""
if anchor not in text:
    raise SystemExit('Chybí závěrečný hodnoticí nadpis.')
text = text.replace(anchor, roles, 1)

# Rozšíření postranního přehledu.
sidebar_anchor = "  <aside class=\"sticky\">\n"
sidebar = """  <aside class=\"sticky\">\n    <div class=\"sidebox\"><h3>Čtyři vrstvy příběhu</h3><ul><li>královské město a jeho privilegia</li><li>návštěvy v letech 1367 a 1374</li><li>vznik scénáře v roce 1992</li><li>34. ročník dne 22. srpna 2026</li></ul></div>\n"""
if sidebar_anchor not in text:
    raise SystemExit('Chybí postranní panel.')
text = text.replace(sidebar_anchor, sidebar, 1)

# Přidat další zdroje, jen pokud je seznam obsahuje.
source_anchor = '      <li><a href="https://www.noviny-kadan.cz/l/650-let-od-druhe-navstevy-karla-iv-v-kadani/" target="_blank" rel="noopener">Kadaňské noviny – druhá návštěva Karla IV. roku 1374</a></li>\n'
source_extra = '      <li><a href="https://www.regionalni-znacky.cz/poohri/zazitky/cisarsky-den-v-kadani" target="_blank" rel="noopener">Asociace regionálních značek – certifikace, provozovatel a programové prostory</a></li>\n'
if source_anchor in text and source_extra not in text:
    text = text.replace(source_anchor, source_anchor + source_extra, 1)

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Rozšířený návrh Císařského dne byl připraven.')
