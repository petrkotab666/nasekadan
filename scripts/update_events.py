#!/usr/bin/env python3
"""Konzervativní automatický import veřejných akcí pro Naše Kadaň.

Zveřejní jen záznamy s rozpoznaným názvem a datem. Při výpadku zdroje zachová
ručně ověřený základ. Každý záznam obsahuje původní URL pro kontrolu změn.
"""
from __future__ import annotations
import hashlib, html, json, re, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data'/'events-seed.json'
OUT=ROOT/'data'/'events.json'
UA='NaseKadanBot/1.1 (+https://nasekadan.cz; info@nasekadan.cz)'
SOURCES=[
 {'name':'Kino Hvězda Kadaň','url':'https://www.kinokadan.cz/cely-program','kind':'jsonld','category':'Kino'},
 {'name':'Městská knihovna Kadaň','url':'https://www.knihovnakadan.cz/','kind':'cards','category':'Knihovna'},
 {'name':'e-region – Kadaň','url':'https://www.e-region.cz/akce/mesto-kadan','kind':'eregion','category':'Akce'},
 {'name':'RADKA Kadaň','url':'https://radka.kadan.cz/uvodni-stranka/pripravujeme/','kind':'ranges','category':'Komunitní'},
]

def fetch(url):
 with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Language':'cs,en;q=0.7'}),timeout=25) as r:
  return r.read().decode(r.headers.get_content_charset() or 'utf-8',errors='replace')
def clean(v): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',str(v or '')))).strip()
def slug(v):
 v=unicodedata.normalize('NFKD',clean(v)).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','-',v).strip('-')[:80]
def walk(v):
 if isinstance(v,dict):
  yield v
  for x in v.values(): yield from walk(x)
 elif isinstance(v,list):
  for x in v: yield from walk(x)
def normalize(e,source):
 title=clean(e.get('title') or e.get('name')); start=str(e.get('start') or e.get('startDate') or '').strip()
 if not title or not start: return None
 place=clean(e.get('place') or e.get('location') or 'Kadaň')
 raw=f'{title}|{start[:10]}|{place}'.lower()
 return {'id':e.get('id') or f'{slug(title)}-{start[:10]}-{hashlib.sha1(raw.encode()).hexdigest()[:7]}','title':title,'start':start,**({'end':e['end']} if e.get('end') else {}),'time':clean(e.get('time')),'place':place,'category':clean(e.get('category') or source['category']),'description':clean(e.get('description'))[:900],'price':clean(e.get('price')),'image':str(e.get('image') or ''),'source':str(e.get('source') or source['url']),'sourceName':str(e.get('sourceName') or source['name']),'verified':bool(e.get('verified',True))}
def parse_jsonld(page,source):
 out=[]
 for raw in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',page,re.I|re.S):
  try: data=json.loads(html.unescape(raw).strip())
  except Exception: continue
  for item in walk(data):
   types=item.get('@type'); types=types if isinstance(types,list) else [types]
   if not any(t in {'Event','Movie','ScreeningEvent','Festival'} for t in types): continue
   loc=item.get('location') or {}; place=loc.get('name','') if isinstance(loc,dict) else str(loc)
   image=item.get('image'); image=image[0] if isinstance(image,list) and image else image
   out.append({'name':item.get('name'),'startDate':item.get('startDate'),'end':item.get('endDate'),'location':place or 'Kino Hvězda Kadaň','description':item.get('description'),'image':image,'source':item.get('url') or source['url'],'category':source['category']})
 return out
def parse_cards(page,source):
 out=[]
 for href,title,tail in re.findall(r'href=["\']([^"\']+)["\'][^>]*>.*?<h[2-6][^>]*>(.*?)</h[2-6]>(.{0,1400})',page,re.I|re.S):
  m=re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(20\d{2})',clean(tail))
  if not m: continue
  d,mo,y=map(int,m.groups()); out.append({'title':clean(title),'start':f'{y:04d}-{mo:02d}-{d:02d}','place':'Městská knihovna Kadaň','description':clean(tail)[:500],'source':urljoin(source['url'],href),'category':source['category']})
 return out
def parse_eregion(page,source):
 text=clean(page); out=[]
 for m in re.finditer(r'od\s+(\d{1,2})\.(\d{1,2})\.(20\d{2}).{0,120}?do\s+(\d{1,2})\.(\d{1,2})\.(20\d{2}).{0,35}?([^|]{4,100})',text,re.I):
  d1,m1,y1,d2,m2,y2,title=m.groups(); out.append({'title':clean(title),'start':f'{y1}-{int(m1):02d}-{int(d1):02d}','end':f'{y2}-{int(m2):02d}-{int(d2):02d}','place':'Kadaň','category':source['category'],'source':source['url']})
 return out
def parse_ranges(page,source):
 text=clean(page); out=[]
 for m in re.finditer(r'([^.!?]{5,100}?)\s+(\d{1,2})\.(\d{1,2})\.\s*-\s*(\d{1,2})\.(\d{1,2})\.\s*(20\d{2})',text):
  title,d1,m1,d2,m2,y=m.groups(); out.append({'title':clean(title)[-90:],'start':f'{y}-{int(m1):02d}-{int(d1):02d}','end':f'{y}-{int(m2):02d}-{int(d2):02d}','place':'RADKA / dle pořadatele','category':source['category'],'source':source['url']})
 return out

def main():
 seed=json.loads(SEED.read_text(encoding='utf-8')).get('events',[]) if SEED.exists() else []
 events=[]; used=['ručně ověřený základ']; errors=[]
 for e in seed:
  n=normalize(e,{'name':e.get('sourceName','Ověřený zdroj'),'url':e.get('source',''),'category':e.get('category','Akce')})
  if n: events.append(n)
 parsers={'jsonld':parse_jsonld,'cards':parse_cards,'eregion':parse_eregion,'ranges':parse_ranges}
 for source in SOURCES:
  try:
   parsed=parsers[source['kind']](fetch(source['url']),source); count=0
   for e in parsed:
    n=normalize(e,source)
    if n: events.append(n); count+=1
   used.append(f"{source['name']} ({count})")
  except Exception as exc: errors.append(f"{source['name']}: {exc}")
 unique={}
 for e in events:
  key=(slug(e['title']),e['start'][:10],slug(e.get('place',''))); old=unique.get(key)
  if old is None or (e.get('verified') and not old.get('verified')) or len(e.get('description',''))>len(old.get('description','')): unique[key]=e
 payload={'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':used,'errors':errors,'events':sorted(unique.values(),key=lambda x:x['start'])}
 OUT.parent.mkdir(parents=True,exist_ok=True); tmp=OUT.with_suffix('.tmp'); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8'); tmp.replace(OUT)
 print(f'Uloženo {len(payload["events"])} akcí.');
 if errors: print(*errors,sep='\n',file=sys.stderr)
if __name__=='__main__': main()
