#!/usr/bin/env python3
from __future__ import annotations
import hashlib,html,json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'city-news.json'
SOURCES_FILE=ROOT/'data'/'city-sources.json'
UA='NaseKadanBot/1.1 (+https://nasekadan.cz; info@nasekadan.cz)'

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Language':'cs,en;q=0.7'}),timeout=25) as r:
        return r.read().decode(r.headers.get_content_charset() or 'utf-8',errors='replace')

def clean(v):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',str(v or '')))).strip()

def parse(page,source):
    out=[]
    for href,body in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',page,re.I|re.S):
        title=clean(body)
        if len(title)<10 or len(title)>180: continue
        low=title.lower()
        if any(x in low for x in ('více','menu','kontakt','facebook','instagram','cookies','úvodní stránka','přihlásit')): continue
        url=urljoin(source['url'],href)
        if not url.startswith('http') or url==source['url']: continue
        pos=page.find(href)
        around=clean(page[max(0,pos-450):pos+1100]) if pos>=0 else ''
        m=re.search(r'(\d{1,2})[./]\s*(\d{1,2})[./]\s*(20\d{2})',around)
        date=f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else ''
        desc=around.replace(title,'',1)[:420].strip(' -|')
        key=hashlib.sha1(f'{title}|{url}'.encode()).hexdigest()[:12]
        out.append({'id':key,'title':title,'date':date,'category':source['category'],'description':desc,'source':url,'sourceName':source['name']})
    unique={}
    for item in out: unique.setdefault((item['title'].lower(),item['source']),item)
    return list(unique.values())[:15]

def main():
    config=json.loads(SOURCES_FILE.read_text(encoding='utf-8'))
    items=[];errors=[];used=[]
    for source in config.get('sources',[]):
        try:
            parsed=parse(fetch(source['url']),source)
            items.extend(parsed);used.append(f"{source['name']} ({len(parsed)})")
        except Exception as exc: errors.append(f"{source['name']}: {exc}")
    unique={}
    for item in items:
        key=(item['title'].lower(),item['source'])
        if key not in unique or len(item['description'])>len(unique[key]['description']): unique[key]=item
    result=sorted(unique.values(),key=lambda x:(x.get('date') or '0000-00-00',x['title']),reverse=True)[:100]
    payload={'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':used,'errors':errors,'items':result}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(OUT)
    print(f'Uloženo {len(result)} městských novinek a odkazů.')
if __name__=='__main__': main()
