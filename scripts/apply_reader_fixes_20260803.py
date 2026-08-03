#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / 'clanky' / 'silnice-zatec-kadan-prejezd-uzavirka-srpen-2026.html'
PUBLISHER = ROOT / 'scripts' / 'publish_zatec_kadan_prejezd_20260803.py'
VISIBILITY = ROOT / 'scripts' / 'enforce_article_visibility.py'
PAGINATION_WORKFLOW = ROOT / '.github' / 'workflows' / 'paginate-articles-12-per-page.yml'

OLD_LEAD_END = 'Právě dvě různá místa způsobila zmatek v termínech.'
NEW_LEAD_END = 'Jde o dvě samostatné uzavírky na různých místech.'
OLD_CALLOUT_TITLE = '<strong>Kde vznikl zmatek</strong>'
NEW_CALLOUT_TITLE = '<strong>Druhý přejezd má vlastní termín</strong>'
OLD_CALLOUT_TEXT = 'V krajském systému je současně druhá událost nazvaná „Žabokliky – uzavírka železničního přejezdu“. Ta má začít až 11. srpna a skončit 28. srpna. Jde však o jiný přejezd, nikoli o prodloužení uzavírky hlavní silnice II/225.'
NEW_CALLOUT_TEXT = 'V krajském systému je současně vedena také uzavírka přejezdu označeného Žabokliky. Začne 11. srpna a skončí 28. srpna. Jde o jiný přejezd než ten na silnici II/225, který se uzavírá od 4. do 11. srpna.'
OLD_FOLLOWUP = 'Časově na sebe obě akce téměř navazují. První má skončit 11. srpna v 6 hodin, druhá začít téhož dne v 7 hodin. Podobný název i blízkost míst proto mohou snadno vyvolat dojem, že jde o jedinou uzavírku s rozdílně uváděným termínem.'
NEW_FOLLOWUP = 'Obě akce na sebe časově téměř navazují. První má skončit 11. srpna v 6 hodin a druhá začne téhož dne v 7 hodin. Pro řidiče je proto podstatné sledovat, kterého přejezdu se konkrétní termín týká.'


def patch_text(path: Path) -> None:
    text = path.read_text(encoding='utf-8')
    text = text.replace(OLD_LEAD_END, NEW_LEAD_END)
    text = text.replace(OLD_CALLOUT_TITLE, NEW_CALLOUT_TITLE)
    text = text.replace(OLD_CALLOUT_TEXT, NEW_CALLOUT_TEXT)
    text = text.replace(OLD_FOLLOWUP, NEW_FOLLOWUP)
    lowered = text.lower()
    if 'zmatek' in lowered or 'zmatk' in lowered:
        raise SystemExit(f'{path}: zůstala formulace o zmatku')
    required = [NEW_LEAD_END, NEW_CALLOUT_TITLE, NEW_CALLOUT_TEXT, NEW_FOLLOWUP]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f'{path}: chybí nové formulace {missing}')
    path.write_text(text, encoding='utf-8', newline='\n')


def patch_visibility() -> None:
    text = VISIBILITY.read_text(encoding='utf-8')
    text = text.replace('HOME_TOTAL = 12', 'HOME_TOTAL = 14', 1)
    text = text.replace('Titulní strana nemá správných deset navazujících článků.', 'Titulní strana nemá správných dvanáct navazujících článků.')
    text = text.replace('Titulní strana obsahuje více než dvanáct nejnovějších článků.', 'Titulní strana obsahuje více než čtrnáct nejnovějších článků.')
    if 'HOME_TOTAL = 14' not in text or 'PAGE_SIZE = 12' not in text:
        raise SystemExit('Nesprávné limity titulky nebo archivu.')
    VISIBILITY.write_text(text, encoding='utf-8', newline='\n')


def patch_workflow() -> None:
    text = PAGINATION_WORKFLOW.read_text(encoding='utf-8')
    text = text.replace("assert count == 10, f'Na titulce má být 10 karet pod dvěma zvýrazněnými články, nalezeno {count}.'", "assert count == 12, f'Na titulce má být 12 karet pod dvěma zvýrazněnými články, nalezeno {count}.'")
    text = text.replace("assert len(re.findall(r'data-auto-article=', grid)) == 10", "assert len(re.findall(r'data-auto-article=', grid)) == 12")
    if "assert count == 12" not in text or "== 12" not in text:
        raise SystemExit('Kontrola titulky nebyla přepnuta na dvanáct karet.')
    PAGINATION_WORKFLOW.write_text(text, encoding='utf-8', newline='\n')


patch_text(ARTICLE)
patch_text(PUBLISHER)
patch_visibility()
patch_workflow()
print('Odstraněny formulace o zmatku; titulka nastavena na 14 článků celkem.')
