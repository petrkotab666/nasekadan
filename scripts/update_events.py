#!/usr/bin/env python3
from __future__ import annotations
import hashlib, html, json, re, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]; SEED=ROOT/'data'/'events-seed.json'; OUT=ROOT/'data'/'events.json'
UA='NaseKadanBot/1.2 (+https://nasekadan.cz; info@nasekadan.cz)'
SOURCES=[
 {'name':'Kultura Kadaň','url':'https://www.kultura-kadan.cz/redakce/index.php?etc=4339&search=yes&subakce=events&xuser=','kind':'culture','category':'Kultura'},
 {'name':'Kino Hvězda Kadaň','url':'https://www.kinokadan.cz/cely-program','kind':'cinema','category':'Kino'},
 {'name':'Městská knihovna Kadaň','url':'https://www.knihovnakadan.cz/','kind':'cards','category':'Knihovna'},
 {'name':'e-region – Kadaň','url':'https://www.e-region.cz/akce/mesto-kadan','kind':'eregion','category':'Akce'},
 {'name':'RADKA Kadaň','url':'https://radka.kadan.cz/uvodni-stranka/pripravujeme/','kind':'ranges','category':'Komunitní'},
]
def fetch(url):
 with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Language':'cs,en;q=0.7'}),timeout=30) as r:return r.read().decode(r.headers.get_content_charset() or 'utf-8',errors='replace')
def clean(v):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',str(v or '')))).strip()
def slug(v):
 v=unicodedata.normalize('NFKD',clean(v)).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','-',v).strip('-')[:80]
def normalize(e,s):
 title=clean(e.get('title') or e.get('name'));start=str(e.get('start') or e.get('startDate') or '').strip()
 if not title or not start:return None
 place=clean(e.get('place') or e.get('location') or 'Kadaň');raw=f'{title}|{start[:10]}|{place}'.lower()
 return {'id':e.get('id') or f'{slug(title)}-{start[:10]}-{hashlib.sha1(raw.encode()).hexdigest()[:7]}','title':title,'start':start,**({'end':e['end']} if e.get('end') else {}),'time':clean(e.get('time')),'place':place,'category':clean(e.get('category') or s['category']),'description':clean(e.get('description'))[:1000],'price':clean(e.get('price')),'format':clean(e.get('format')),'image':str(e.get('image') or ''),'source':str(e.get('source') or s['url']),'sourceName':str(e.get('sourceName') or s['name']),'verified':bool(e.get('verified',True))}
def parse_cinema(page,s):
 text=clean(page);out=[]
 rx=re.compile(r'(?:Hlavní obrázek pro\s+)?(.{2,100}?)\s+(.{0,260}?)\s+(?:Dnes|Zítra|Pondělí|Úterý|Středa|Čtvrtek|Pátek|Sobota|Neděle)\s*[•-]\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(20\d{2})\s*[•-]\s*(\d{1,2}:\d{2})\s+KINO HVĚZDA KADAŇ\s+(.{0,170}?)(?=Zůstává|Vstupenky|Hlavní obrázek pro|$)',re.I)
 for title,desc,d,m,y,tm,fmt in rx.findall(text):
  title=clean(title)
  if len(title)>100 or title.lower()=='celý program':continue
  out.append({'title':title,'start':f'{y}-{int(m):02d}-{int(d):02d}T{tm}:00+02:00','time':tm,'place':'Kino Hvězda Kadaň','description':clean(desc),'format':clean(fmt),'source':s['url'],'category':'Kino'})
 return out
def parse_culture(page,s):
 text=clean(page);out=[]
 rx=re.compile(r'(\d{1,2})\.(\d{1,2})\.(20\d{2})\s+([a-zá-ž -]{2,30})\s+(.{3,110}?)\s+(.{0,180}?)(?=\s+více\b|\s+\d{1,2}\.\d{1,2}\.20\d{2}|$)',re.I)
 for d,m,y,cat,title,desc in rx.findall(text):
  title=clean(title)
  if title.lower().startswith(('kalendář','filtrování')):continue
  out.append({'title':title,'start':f'{y}-{int(m):02d}-{int(d):02d}','place':'Kadaň / dle pořadatele','description':clean(desc),'category':clean(cat).title(),'source':s['url']})
 return out
def parse_cards(page,s):
 out=[]
 for href,title,tail in re.findall(r'href=["\']([^"\']+)["\'][^>]*>.*?<h[2-6][^>]*>(.*?)</h[2-6]>(.{0,1400})',page,re.I|re.S):
  m=re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(20\d{2})',clean(tail))
  if m:
   d,mo,y=map(int,m.groups());out.append({'title':clean(title),'start':f'{y:04d}-{mo:02d}-{d:02d}','place':'Městská knihovna Kadaň','description':clean(tail)[:500],'source':urljoin(s['url'],href),'category':s['category']})
 return out
def parse_eregion(page,s):
 text=clean(page);out=[]
 rx=re.compile(r'od\s+(\d{1,2})\.(\d{1,2})\.(20\d{2}),?\s*\w*\s+do\s+(\d{1,2})\.(\d{1,2})\.(20\d{2}),?\s*\w*\s+(.*?)(?=\s+od\s+\d{1,2}\.\d{1,2}\.20\d{2}|$)',re.I)
 for d1,m1,y1,d2,m2,y2,block in rx.findall(text):
  block=clean(block);parts=re.split(r'(?<=[.!?])\s+',block,maxsplit=1);title=parts[0].strip(' -|')[:120];desc=parts[1] if len(parts)>1 else ''
  if len(title)>90:title=' '.join(title.split()[:8]);desc=block[len(title):].strip()
  place='Kadaň'
  for x in ['Minoritská bašta','Kadaňský hrad','Františkánský klášter','Mírové náměstí','Studentské náměstí']:
   if x.lower() in block.lower():place=x;break
  out.append({'title':title,'start':f'{y1}-{int(m1):02d}-{int(d1):02d}','end':f'{y2}-{int(m2):02d}-{int(d2):02d}','place':place,'description':desc,'category':'Výstava','source':s['url']})
 return out
def parse_ranges(page,s):
 text=clean(page);out=[]
 for m in re.finditer(r'([^.!?]{5,100}?)\s+(\d{1,2})\.(\d{1,2})\.\s*-\s*(\d{1,2})\.(\d{1,2})\.\s*(20\d{2})',text):
  title,d1,m1,d2,m2,y=m.groups();out.append({'title':clean(title)[-90:],'start':f'{y}-{int(m1):02d}-{int(d1):02d}','end':f'{y}-{int(m2):02d}-{int(d2):02d}','place':'RADKA / dle pořadatele','category':s['category'],'source':s['url']})
 return out
def main():
 seed=json.loads(SEED.read_text(encoding='utf-8')).get('events',[]) if SEED.exists() else [];events=[];used=['ručně ověřený základ'];errors=[]
 for e in seed:
  n=normalize(e,{'name':e.get('sourceName','Ověřený zdroj'),'url':e.get('source',''),'category':e.get('category','Akce')})
  if n:events.append(n)
 parsers={'cinema':parse_cinema,'culture':parse_culture,'cards':parse_cards,'eregion':parse_eregion,'ranges':parse_ranges}
 for s in SOURCES:
  try:
   parsed=parsers[s['kind']](fetch(s['url']),s);count=0
   for e in parsed:
    n=normalize(e,s)
    if n:events.append(n);count+=1
   used.append(f"{s['name']} ({count})")
  except Exception as exc:errors.append(f"{s['name']}: {exc}")
 unique={}
 for e in events:
  key=(slug(e['title']),e['start'][:10],slug(e.get('place','')));old=unique.get(key)
  if old is None or len(e.get('description',''))>len(old.get('description','')):unique[key]=e
 payload={'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':used,'errors':errors,'events':sorted(unique.values(),key=lambda x:x['start'])}
 OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(OUT)
 print(f'Uloženo {len(payload["events"])} akcí.');print(*used,sep='\n- ')
 if errors:print(*errors,sep='\n',file=sys.stderr)
if __name__=='__main__':main()
