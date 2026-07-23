#!/usr/bin/env python3
from __future__ import annotations
import hashlib, html, json, re, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data'/'events-seed.json'
OUT=ROOT/'data'/'events.json'
UA='NaseKadanBot/1.4 (+https://nasekadan.cz; info@nasekadan.cz)'
SOURCES=[
 {'name':'Kultura Kadaň','url':'https://www.kultura-kadan.cz/redakce/index.php?etc=4339&search=yes&subakce=events&xuser=','kind':'culture','category':'Kultura'},
 {'name':'Kino Hvězda Kadaň','url':'https://www.kinokadan.cz/cely-program','kind':'cinema','category':'Kino'},
 {'name':'Městská knihovna Kadaň','url':'https://www.knihovnakadan.cz/','kind':'cards','category':'Knihovna'},
 {'name':'e-region – Kadaň','url':'https://www.e-region.cz/akce/mesto-kadan','kind':'eregion','category':'Akce'},
 {'name':'RADKA Kadaň','url':'https://radka.kadan.cz/','kind':'ranges','category':'Komunitní'},
]

GENERIC_PATHS={
 '/','',
 '/cely-program',
 '/akce/mesto-kadan',
 '/akce/frantiskansky-klaster-kadan',
 '/kultura',
 '/aktivity/galerie-josefa-lieslera',
}

def fetch(url):
 with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Language':'cs,en;q=0.7'}),timeout=30) as r:
  return r.read().decode(r.headers.get_content_charset() or 'utf-8',errors='replace')

def clean(v):
 return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',str(v or '')))).strip()

def slug(v):
 v=unicodedata.normalize('NFKD',clean(v)).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','-',v).strip('-')[:80]

def normalize(e,s):
 title=clean(e.get('title') or e.get('name'));start=str(e.get('start') or e.get('startDate') or '').strip()
 if not title or not start:return None
 place=clean(e.get('place') or e.get('location') or 'Kadaň');raw=f'{title}|{start[:10]}|{place}'.lower()
 return {'id':e.get('id') or f'{slug(title)}-{start[:10]}-{hashlib.sha1(raw.encode()).hexdigest()[:7]}','title':title,'start':start,**({'end':e['end']} if e.get('end') else {}),'time':clean(e.get('time')),'place':place,'category':clean(e.get('category') or s['category']),'description':clean(e.get('description'))[:1400],'price':clean(e.get('price')),'format':clean(e.get('format')),'image':str(e.get('image') or ''),'source':str(e.get('source') or s['url']),'sourceName':str(e.get('sourceName') or s['name']),'verified':bool(e.get('verified',True))}

def normalized_path(url):
 try:return urlparse(str(url or '')).path.rstrip('/').lower()
 except Exception:return ''

def source_quality(event):
 url=str(event.get('source') or '').strip();lower=url.lower();path=normalized_path(url);score=0
 if not url:return -100
 if '/dre-cs/' in lower:score+=140
 if 'dodila.cz/akce/' in lower:score+=140
 if re.search(r'[?&]detail=\d+',lower):score+=135
 if re.search(r'/akce/[^/?#]+/?$',urlparse(url).path,re.I) and path not in GENERIC_PATHS:score+=100
 if '/calendar/' in lower or '/udalost/' in lower or '/event/' in lower:score+=80
 if path and path not in GENERIC_PATHS:score+=25
 if '/redakce/index.php' in lower or path in GENERIC_PATHS:score-=100
 if 'e-region.cz' in lower:score-=20
 name=str(event.get('sourceName') or '').lower()
 if 'kultura kadaň' in name:score+=12
 if 'detail akce' in name:score+=15
 if event.get('verified'):score+=3
 return score

def event_key(event):
 title=slug(event.get('title',''));start=str(event.get('start') or '')
 if clean(event.get('category')).lower()=='kino':when=start[:16]
 else:when=start[:10]
 return title,when

def prefer_event(candidate,current):
 cq,oq=source_quality(candidate),source_quality(current)
 if cq!=oq:return candidate if cq>oq else current
 c_info=sum(len(clean(candidate.get(k))) for k in ('description','time','place','price','format'))
 o_info=sum(len(clean(current.get(k))) for k in ('description','time','place','price','format'))
 return candidate if c_info>o_info else current

def detail_url_near_title(page,title,base):
 needles={title,html.escape(title,quote=False)};best=[]
 for needle in needles:
  for match in re.finditer(re.escape(needle),page,re.I):
   chunk=page[max(0,match.start()-2400):match.start()+3000]
   for href in re.findall(r'href=["\']([^"\']+)["\']',chunk,re.I):
    absolute=urljoin(base,html.unescape(href));low=absolute.lower();score=0
    if re.search(r'[?&]detail=\d+',low):score=100
    elif '/detail/' in low or '/film/' in low:score=90
    elif '/program/' in low and not low.rstrip('/').endswith('/cely-program'):score=60
    if score:best.append((score,absolute))
   break
 return max(best,key=lambda item:item[0])[1] if best else base

def parse_cinema(page,s):
 text=clean(page);out=[]
 rx=re.compile(r'(?:Hlavní obrázek pro\s+)?(.{2,100}?)\s+(.{0,260}?)\s+(?:Dnes|Zítra|Pondělí|Úterý|Středa|Čtvrtek|Pátek|Sobota|Neděle)\s*[•-]\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(20\d{2})\s*[•-]\s*(\d{1,2}:\d{2})\s+KINO HVĚZDA KADAŇ\s+(.{0,170}?)(?=Zůstává|Vstupenky|Hlavní obrázek pro|$)',re.I)
 for title,desc,d,m,y,tm,fmt in rx.findall(text):
  title=clean(title)
  if len(title)>100 or title.lower()=='celý program':continue
  out.append({'title':title,'start':f'{y}-{int(m):02d}-{int(d):02d}T{tm}:00+02:00','time':tm,'place':'Kino Hvězda Kadaň','description':clean(desc),'format':clean(fmt),'source':detail_url_near_title(page,title,s['url']),'sourceName':'Kino Hvězda Kadaň','category':'Kino'})
 return out

def detail_value(text,label,next_labels):
 pattern=rf'{re.escape(label)}\s*(.*?)(?='+'|'.join(re.escape(x) for x in next_labels)+r'|$)'
 m=re.search(pattern,text,re.I)
 return clean(m.group(1)) if m else ''

def parse_culture_detail(url,title,date_hint,category_hint):
 try: page=fetch(url)
 except Exception: return {'title':title,'start':date_hint,'category':category_hint,'source':url,'place':'Kadaň / dle pořadatele'}
 text=clean(page)
 place=detail_value(text,'Místo konání:',['Datum konání:','Typ akce:']) or 'Kadaň / dle pořadatele'
 date_text=detail_value(text,'Datum konání:',['Typ akce:','Tematická kategorie:','Anotace:'])
 typ=detail_value(text,'Typ akce:',['Tematická kategorie:','Anotace:']) or category_hint
 annotation=detail_value(text,'Anotace:',['Podrobný popis:','Sponzoři'])
 desc=detail_value(text,'Podrobný popis:',['Sponzoři','Přihlásit se k odběru'])
 price=''
 pm=re.search(r'vstupn[ée]:\s*([^.;]{1,120})',text,re.I)
 if pm: price=clean(pm.group(1))
 dm=re.search(r'(\d{1,2})\.(\d{1,2})\.(20\d{2})(?:\s+od\s+(\d{1,2}:\d{2}))?',date_text)
 start=date_hint;time=''
 if dm:
  d,m,y,tm=dm.groups();start=f'{y}-{int(m):02d}-{int(d):02d}'+(f'T{tm}:00+02:00' if tm else '');time=tm or ''
 return {'title':title,'start':start,'time':time,'place':place,'category':typ.title(),'description':(annotation+' '+desc).strip(),'price':price,'source':url,'sourceName':'Kultura Kadaň','verified':True}

def parse_culture_pages(s,max_pages=8):
 out=[];seen=set()
 for page_no in range(1,max_pages+1):
  url=s['url'] if page_no==1 else s['url']+f'&page={page_no}'
  try: raw=fetch(url)
  except Exception: break
  found=0
  for m in re.finditer(r'href=["\']([^"\']*/dre-cs/[^"\']+\.html)["\'][^>]*>(.*?)</a>',raw,re.I|re.S):
   href=urljoin(url,m.group(1));title=clean(m.group(2))
   if not title or href in seen or title.lower() in {'více','detail'}:continue
   before=clean(raw[max(0,m.start()-700):m.start()])
   dm=list(re.finditer(r'(\d{1,2})\.(\d{1,2})\.(20\d{2})',before))
   if not dm:continue
   d,mo,y=dm[-1].groups();date_hint=f'{y}-{int(mo):02d}-{int(d):02d}'
   cat='Kultura'
   cm=re.search(r'(hudba|výstava|divadlo|kino|sport|zájezd|slavnost|workshop|přednáška|festival|pro děti)\s*$',before,re.I)
   if cm:cat=cm.group(1).title()
   seen.add(href);found+=1
   out.append(parse_culture_detail(href,title,date_hint,cat))
  if found==0:break
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
  for x in ['Minoritská bašta','Kadaňský hrad','Františkánský klášter','Mírové náměstí','Studentské náměstí','Galerie Josefa Lieslera']:
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
 parsers={'cinema':parse_cinema,'cards':parse_cards,'eregion':parse_eregion,'ranges':parse_ranges}
 for s in SOURCES:
  try:
   parsed=parse_culture_pages(s) if s['kind']=='culture' else parsers[s['kind']](fetch(s['url']),s);count=0
   for e in parsed:
    n=normalize(e,s)
    if n:events.append(n);count+=1
   used.append(f"{s['name']} ({count})")
  except Exception as exc:errors.append(f"{s['name']}: {exc}")
 unique={}
 for event in events:
  key=event_key(event);old=unique.get(key)
  unique[key]=event if old is None else prefer_event(event,old)
 payload={'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':used,'errors':errors,'events':sorted(unique.values(),key=lambda x:x['start'])}
 OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(OUT)
 print(f'Uloženo {len(payload["events"])} akcí.');print(*used,sep='\n- ')
 if errors:print(*errors,sep='\n',file=sys.stderr)
if __name__=='__main__':main()
