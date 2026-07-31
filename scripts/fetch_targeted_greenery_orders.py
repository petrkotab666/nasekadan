#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.github'/'research'/'greenery-kadan-2026'
TEXTS=OUT/'targeted-texts'
WORK=OUT/'targeted-work'
TEXTS.mkdir(parents=True,exist_ok=True)
WORK.mkdir(parents=True,exist_ok=True)

S=requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (compatible; NaseKadanResearch/1.3; +https://nasekadan.cz)','Accept-Language':'cs-CZ,cs;q=0.9,en;q=0.5'})

SEARCHES={
 'KU-KU':'https://smlouvy.gov.cz/vyhledavani?party_box=v37djpw&searchResultList-limit=500',
 'Zalabák':'https://smlouvy.gov.cz/vyhledavani?party_idnum=04946081&searchResultList-limit=500',
}
TARGETS={
 'KU-KU':{'objednávka 5/Jan/2026','objednávka 6/Jan/2026','objednávka 10/Jan/2026','objednávka 12/Jan/2026','objednávka 82/Jan/2026','objednávka 83/Jan/2026','objednávka 104/Jan/2026','objednávka 119/Jan/2026'},
 'Zalabák':{'objednávka 20/Jan/2026','objednávka 22/Jan/2026','objednávka 25/Jan/2026','objednávka 80/Jan/2026'},
 'Čepelák':{'objednávka 33/Jan/2026'},
}
KNOWN={'objednávka 33/Jan/2026':'https://smlouvy.gov.cz/smlouva/36438289'}


def request(url:str, *, binary=False, referer=''):
    headers={'Referer':referer} if referer else {}
    last=''
    for attempt in range(7):
        try:
            r=S.get(url,headers=headers,timeout=90,allow_redirects=True)
            if r.status_code in (429,502,503,504):
                last=f'HTTP {r.status_code}'
                time.sleep(min(120,10*(2**attempt)))
                continue
            r.raise_for_status()
            time.sleep(4)
            return r.content if binary else r.text
        except Exception as exc:
            last=f'{type(exc).__name__}: {exc}'
            time.sleep(min(120,10*(2**attempt)))
    raise RuntimeError(f'{url}: {last}')


def discover():
    result=dict(KNOWN)
    for party,url in SEARCHES.items():
        page=request(url)
        soup=BeautifulSoup(page,'html.parser')
        for row in soup.select('table tr'):
            text=' '.join(row.get_text(' ',strip=True).split())
            for target in TARGETS[party]:
                if target.lower() in text.lower():
                    a=row.select_one('a[href^="/smlouva/"]')
                    if a:
                        result[target]=urljoin(url,a.get('href','')).split('?')[0]
        # Some pages are rendered without a regular table selector.
        for a in soup.select('a[href^="/smlouva/"]'):
            parent=' '.join(a.parent.get_text(' ',strip=True).split()) if a.parent else ''
            for target in TARGETS[party]:
                if target.lower() in parent.lower():
                    result[target]=urljoin(url,a.get('href','')).split('?')[0]
    return result


def pdf_text(pdf:Path, stem:str):
    txt=TEXTS/f'{stem}.txt'
    p=subprocess.run(['pdftotext','-layout',str(pdf),str(txt)],text=True,capture_output=True)
    text=txt.read_text(encoding='utf-8',errors='replace') if txt.exists() else ''
    if len(re.sub(r'\s+','',text))>=150:
        return text,'pdftotext'
    folder=WORK/stem
    shutil.rmtree(folder,ignore_errors=True); folder.mkdir(parents=True)
    subprocess.run(['pdftoppm','-r','250','-png',str(pdf),str(folder/'page')],text=True,capture_output=True,timeout=300)
    chunks=[]
    for i,image in enumerate(sorted(folder.glob('page-*.png'))[:20],1):
        base=folder/f'ocr-{i:03d}'
        subprocess.run(['tesseract',str(image),str(base),'-l','ces+eng','--psm','6'],text=True,capture_output=True,timeout=180)
        path=base.with_suffix('.txt')
        if path.exists(): chunks.append(path.read_text(encoding='utf-8',errors='replace'))
    text='\n\n'.join(chunks); txt.write_text(text,encoding='utf-8')
    shutil.rmtree(folder,ignore_errors=True)
    return text,'ocr-tesseract'


def parse(target,url):
    page=request(url)
    soup=BeautifulSoup(page,'html.parser')
    plain='\n'.join(x.strip() for x in soup.get_text('\n').splitlines() if x.strip())
    links=[]
    for a in soup.select('a[href*="/smlouva/soubor/"]'):
        href=urljoin(url,a.get('href',''))
        if '.pdf' in href.lower(): links.append((a.get_text(' ',strip=True),href))
    extracted=[]
    for i,(name,href) in enumerate(dict.fromkeys(links),1):
        stem=f'{re.search(r"/smlouva/(\\d+)",url).group(1)}-{i:02d}-{re.sub(r"[^0-9A-Za-zÀ-ž._-]+","-",name)[:90]}'
        pdf=WORK/f'{stem}.pdf'
        pdf.write_bytes(request(href,binary=True,referer=url))
        text,method=pdf_text(pdf,stem)
        extracted.append({'name':name,'url':href,'text_file':str((TEXTS/f'{stem}.txt').relative_to(ROOT)),'method':method,'characters':len(text),'text':text})
        pdf.unlink(missing_ok=True)
    return {'target':target,'url':url,'page_text':plain,'attachments':extracted}


def main():
    found=discover()
    missing=[]
    wanted=set().union(*TARGETS.values())
    for item in sorted(wanted):
        if item not in found: missing.append(item)
    rows=[]
    for target,url in sorted(found.items()):
        if target not in wanted: continue
        try:
            rows.append(parse(target,url))
            print('OK',target,url)
        except Exception as exc:
            rows.append({'target':target,'url':url,'error':f'{type(exc).__name__}: {exc}'})
            print('FAIL',target,exc)
    payload={'found':len(found),'requested':len(wanted),'missing':missing,'orders':rows}
    (OUT/'targeted-orders.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# Klíčové celoroční objednávky zeleně - OCR','',f"Vyžádáno: **{len(wanted)}**, nalezeno: **{len(found)}**, chybí: **{len(missing)}**.",'']
    if missing: md += ['Chybějící: '+', '.join(missing),'']
    for row in rows:
        md += [f"## {row['target']}",'',f"- Registr: {row['url']}"]
        if row.get('error'):
            md += [f"- Chyba: {row['error']}",'']; continue
        for a in row.get('attachments',[]):
            md += [f"- Příloha: {a['name']} - **{a['method']}**, {a['characters']} znaků",'', '```text', a['text'].strip(), '```','']
    (OUT/'TARGETED-ORDERS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    shutil.rmtree(WORK,ignore_errors=True)
    print(json.dumps({'requested':len(wanted),'found':len(found),'missing':missing,'processed':len(rows)},ensure_ascii=False))

if __name__=='__main__': main()
