#!/usr/bin/env python3
"""Doplní do data/events.json sportovní utkání kadaňských klubů."""
from __future__ import annotations
import hashlib, html, json, re, unicodedata
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'events.json'
UA='NaseKadanBot/1.0 (+https://nasekadan.cz; info@nasekadan.cz)'

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=25) as r:
        return r.read().decode(r.headers.get_content_charset() or 'utf-8',errors='replace')

def clean(v):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',v))).strip()

def slug(v):
    v=unicodedata.normalize('NFKD',v).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',v).strip('-')

def add(events,title,start,time,place,description,source):
    key=f'{title}|{start}|{place}'.lower()
    events.append({'id':f'{slug(title)}-{start}-{hashlib.sha1(key.encode()).hexdigest()[:7]}','title':title,'start':start,'time':time,'place':place,'category':'Sport','description':description,'price':'ověřte u pořadatele','source':source,'sourceName':'Oficiální web sportovního klubu','verified':True})

def parse_hockey(events):
    url='https://www.skkadan.cz/zapas.asp?sezona=2027-2'
    text=clean(fetch(url))
    months={'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'11':11,'12':12}
    for d,m,home,away,time in re.findall(r'(\d{1,2})\.(\d{1,2})\.\s+([^|]{2,35}?)\s+([^|]{2,35}?)\s+(\d{1,2}:\d{2})',text):
        if 'Kadaň' not in home+away and 'Kadan' not in home+away: continue
        date=f'2026-{int(m):02d}-{int(d):02d}'
        place='Zimní stadion Kadaň' if home.strip()=='SK Kadaň' else 'venkovní utkání'
        add(events,f'{home.strip()} – {away.strip()}',date,time,place,'Přípravné hokejové utkání SK Kadaň před sezonou 2026/2027.',url)

def parse_floorball(events):
    url='https://www.katikadan.cz/'
    text=clean(fetch(url))
    for d,m,year,title in re.findall(r'(?:so|ne|pá|út|st|čt)\s+(\d{1,2})\.(\d{1,2})\.(20\d{2})\s*,?\s*([^–]{5,100})',text,re.I):
        if 'Kadaň' not in title and 'Kati' not in title: continue
        date=f'{year}-{int(m):02d}-{int(d):02d}'
        add(events,clean(title),date,'čas ověřte u klubu','dle rozpisu soutěže','Utkání FBC DDM Kati Kadaň. Přesný čas a sportovní hala se mohou změnit.',url)

def main():
    payload=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {'events':[]}
    events=list(payload.get('events',[]))
    errors=[]
    for parser in (parse_hockey,parse_floorball):
        try: parser(events)
        except Exception as exc: errors.append(str(exc))
    unique={}
    for e in events:
        key=(slug(e.get('title','')),e.get('start','')[:10],slug(e.get('place','')))
        if key not in unique or len(e.get('description',''))>len(unique[key].get('description','')): unique[key]=e
    payload['events']=sorted(unique.values(),key=lambda x:x.get('start',''))
    payload.setdefault('sources',[]).append('Sportovní kluby')
    payload.setdefault('errors',[]).extend(errors)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Sportovní kalendář doplněn, celkem {len(payload["events"])} akcí.')
if __name__=='__main__': main()
