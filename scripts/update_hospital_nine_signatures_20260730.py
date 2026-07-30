#!/usr/bin/env python3
from pathlib import Path

PATH = Path('clanky/nemocnice-kadan-nove-vedeni-pavel-marek-jiri-vlas.html')
text = PATH.read_text(encoding='utf-8')

text = text.replace('2026-07-30T12:09:00+02:00', '2026-07-30T12:15:00+02:00')
text = text.replace('Aktuální zpráva · aktualizováno v 12:09', 'Aktuální zpráva · aktualizováno v 12:15')
text = text.replace('k 30. červenci v 12:09 nebyl', 'k 30. červenci v 12:15 nebyl')
text = text.replace('při kontrole 30. července v 12:09', 'při kontrole 30. července v 12:15')
text = text.replace('Poslední ověřená aktualizace 30. července 2026 v 12:09.', 'Poslední ověřená aktualizace 30. července 2026 v 12:15.')

old_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 12:09</strong><p>Prověřili jsme profesní minulost Pavla Marka a letošní řízení ÚOHS k zakázce na nemocniční lůžka. Marek byl v roce 2017 v České Lípě vybrán hodnoticí komisí a po devíti letech odešel na konci roku 2025 podle oficiálních zdrojů z vlastní iniciativy v souvislosti s fúzí nemocnic. Veřejný doklad o výběrovém řízení pro jeho novou funkci v Kadani jsme nenašli. V případě zakázky na lůžka ÚOHS návrh vyloučeného dodavatele zamítl a nenašel důvod k nápravnému opatření.</p></div>'''
new_update = '''  <div class="update-box"><strong>Aktualizace 30. července v 12:15</strong><p>Kadaň má v tomto volebním období 27 zastupitelů. Zákonná žádost o mimořádné zasedání proto musí mít podpis nejméně devíti členů zastupitelstva. Veřejný požadavek Jiřího Kulhánka ze zasedání 25. června je doložen, ale veřejný dokument s devíti podpisy, datem doručení a navrženým programem jsme zatím nenašli. Město dosud nezveřejnilo ani pozvánku na mimořádné zasedání.</p></div>'''
if old_update not in text:
    raise SystemExit('Nenalezen aktualizační box 12:09')
text = text.replace(old_update, new_update)

old_para = '''  <p>To nevylučuje, že zastupitelé mohou svolání požadovat nebo že se taková žádost připravuje. Žádost nebo politické oznámení ale ještě není totéž jako oficiálně svolané veřejné zasedání. Podle zákona o obcích musí starosta zasedání svolat, požádá-li o to alespoň třetina členů zastupitelstva; konat se pak musí nejpozději do 21 dnů od doručení žádosti obecnímu úřadu. Informace o místě, době a programu se následně zveřejňuje na úřední desce.</p>'''
new_para = '''  <p>To nevylučuje, že zastupitelé mohou svolání požadovat nebo že se taková žádost připravuje. Žádost nebo politické oznámení ale ještě není totéž jako oficiálně svolané veřejné zasedání. Kadaň má 27 zastupitelů, takže zákonnou hranici jedné třetiny tvoří nejméně devět podpisů. Pokud je taková žádost doručena obecnímu úřadu, musí se zasedání konat nejpozději do 21 dnů. Informace o místě, době a programu se následně zveřejňuje na úřední desce.</p>'''
if old_para not in text:
    raise SystemExit('Nenalezen právní odstavec k mimořádnému zastupitelstvu')
text = text.replace(old_para, new_para)

callout_anchor = '''  <div class="callout"><strong>Pozor na rozdíl mezi radou a zastupitelstvem</strong><p>Dne 29. července se konala mimořádná schůze rady města, nikoli zastupitelstva. Informace, že zastupitelé chtějí vyvolat mimořádné zasedání, zatím není totéž jako jeho formální svolání a zveřejnění termínu.</p></div>'''
callout_repl = callout_anchor + '''
  <div class="fact-grid">
    <div class="fact-card"><span>Zákonný práh</span><strong>9 podpisů</strong><p>Jedna třetina z 27 členů kadaňského zastupitelstva znamená nejméně devět zastupitelů.</p></div>
    <div class="fact-card"><span>Veřejně doloženo</span><strong>Požadavek jednoho člena</strong><p>Zápis zachycuje návrh Jiřího Kulhánka. Nezachycuje však společnou formální žádost devíti členů ani datum jejího doručení úřadu.</p></div>
  </div>'''
if 'Jedna třetina z 27 členů' not in text:
    text = text.replace(callout_anchor, callout_repl)

text = text.replace(
    '<li>Zda bude formálně svoláno mimořádné zastupitelstvo a jaký bude jeho program.</li>',
    '<li>Zda byla úřadu doručena formální žádost nejméně devíti zastupitelů, kdy a s jakým programem.</li>'
)
text = text.replace(
    '<li>Požadavek na mimořádné ZM zazněl 25. června</li>',
    '<li>Pro formální žádost je třeba 9 podpisů</li><li>Požadavek na mimořádné ZM zazněl 25. června</li>'
)

required = [
    'Zákonný práh</span><strong>9 podpisů',
    'Jedna třetina z 27 členů kadaňského zastupitelstva',
    '2026-07-30T12:15:00+02:00',
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'Chybí aktualizace: {needle}')

PATH.write_text(text, encoding='utf-8', newline='\n')
print('Článek doplněn o zákonnou hranici devíti podpisů.')
