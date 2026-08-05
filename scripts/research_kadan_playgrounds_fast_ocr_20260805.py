#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, re, shutil, ssl, subprocess, time, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research'/'kadanska-hriste-fast-ocr-20260805'
TMP=Path('/tmp/kadanska-hriste-fast-ocr-20260805')
OUT.mkdir(parents=True,exist_ok=True); TMP.mkdir(parents=True,exist_ok=True)
UA='NaseKadan-playgrounds-fast-ocr/1.0'
DUMPS=['2026_01','2026_02','2026_03','2026_04','2026_05','2025_01','2025_04','2024_11']
KEYS=['00261912','město kadaň','mesto kadan']
TARGETS=['hřiště hrou','hriste hrou','herold','envy sport','radana kučer','radana kucer','hřiště 5.20','hriste 5.20','golovinova','rafanda','strážiště','straziste','dětských hřišť','detskych hrist','sportovišť','sportovist']

def ctx(): return ssl._create_unverified_context()
def get(url,tries=6,timeout=300):
    last=None
    for i in range(tries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'*/*'})
            with urllib.request.urlopen(req,timeout=timeout,context=ctx()) as r: data=r.read()
            if data:return data
        except Exception as e:
            last=e; time.sleep(min(15,2+i*2))
    raise RuntimeError(f'{url}: {last}')
def loc(t): return t.rsplit('}',1)[-1]
def vals(e):
    out=[]
    for n in e.iter():
        if n.text and n.text.strip(): out.append((loc(n.tag),n.text.strip()))
        for a in n.attrib.values(): out.append(('@attr',a))
    return out

def cmd(a): return subprocess.run(a,text=True,capture_output=True,check=False)
def ocr_pdf(pdf:Path,stem:str):
    raw=TMP/(stem+'-raw.txt'); cmd(['pdftotext','-layout',str(pdf),str(raw)])
    text=raw.read_text(encoding='utf-8',errors='replace') if raw.exists() else ''
    info=cmd(['pdfinfo',str(pdf)]).stdout
    m=re.search(r'^Pages:\s+(\d+)',info,re.M); pages=int(m.group(1)) if m else 1
    if len(re.sub(r'\s+','',text))<max(250,min(pages,20)*60):
        prefix=TMP/(stem+'-page')
        cmd(['pdftoppm','-jpeg','-r','240','-f','1','-l',str(min(pages,25)),str(pdf),str(prefix)])
        pieces=[]
        for i,img in enumerate(sorted(TMP.glob(stem+'-page-*.jpg')),1):
            outbase=TMP/(stem+f'-ocr-{i:03d}')
            cmd(['tesseract',str(img),str(outbase),'-l','ces+eng','--psm','6'])
            txt=outbase.with_suffix('.txt')
            pieces.append(f'\n\n===== OCR STRANA {i} =====\n'+(txt.read_text(encoding='utf-8',errors='replace') if txt.exists() else ''))
        text += ''.join(pieces)
    dest=OUT/'texts'/(stem+'.txt'); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(text,encoding='utf-8')
    return str(dest.relative_to(OUT)),pages

records=[]; errors=[]
for dm in DUMPS:
    url=f'https://data.smlouvy.gov.cz/dump_{dm}.xml'; p=TMP/(f'dump_{dm}.xml')
    try:p.write_bytes(get(url))
    except Exception as e: errors.append({'dump':dm,'error':str(e)}); continue
    try:
        for _,e in ET.iterparse(p,events=('end',)):
            if loc(e.tag).casefold()!='zaznam':continue
            x=ET.tostring(e,encoding='unicode'); low=x.casefold()
            if not any(k in low for k in KEYS) or not any(k in low for k in TARGETS):e.clear();continue
            v=vals(e); urls=sorted({z for _,z in v if z.startswith('http')})
            records.append({'dump':dm,'values':v,'urls':urls,'xml':x})
            e.clear()
    except Exception as ex: errors.append({'dump':dm,'error':'parse '+str(ex)})
    p.unlink(missing_ok=True)

# deduplikovat a vytáhnout přílohy
uniq={}
for r in records:
    key=hashlib.sha256(r['xml'].encode()).hexdigest(); uniq[key]=r
records=list(uniq.values())
attachments=[]
for ri,r in enumerate(records,1):
    for ai,u in enumerate(r['urls'],1):
        if not (re.search(r'\.(pdf|docx?|odt|rtf)(\?|$)',u,re.I) or '/soubor/' in u or '/priloha/' in u):continue
        row={'record':ri,'url':u}
        try:
            data=get(u); ext=Path(urlparse(u).path).suffix.lower() or '.pdf'; f=TMP/f'r{ri:03d}-{ai:02d}{ext}'; f.write_bytes(data)
            row['bytes']=len(data); row['sha256']=hashlib.sha256(data).hexdigest()
            if data[:5]==b'%PDF-' or ext=='.pdf':
                row['text_file'],row['pages']=ocr_pdf(f,f'r{ri:03d}-{ai:02d}')
        except Exception as ex: row['error']=str(ex)
        attachments.append(row)

(OUT/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'attachments.json').write_text(json.dumps(attachments,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
# souhrnný fulltext
parts=[]
for p in sorted((OUT/'texts').glob('*.txt')):
    parts.append(f'\n\n===== {p.name} =====\n'+p.read_text(encoding='utf-8',errors='replace'))
(OUT/'FULLTEXT-OCR.txt').write_text(''.join(parts),encoding='utf-8')
(OUT/'STATUS.json').write_text(json.dumps({'records':len(records),'attachments':len(attachments),'errors':len(errors)},ensure_ascii=False,indent=2),encoding='utf-8')
shutil.rmtree(TMP,ignore_errors=True)
print(json.dumps({'records':len(records),'attachments':len(attachments),'errors':len(errors)},ensure_ascii=False))
