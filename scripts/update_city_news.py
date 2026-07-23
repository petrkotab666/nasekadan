#!/usr/bin/env python3
"""Konzervativní import veřejných novinek souvisejících s Kadaní.

Zveřejní jen položky s rozpoznaným názvem, datem a přímým odkazem. Výstup slouží
jako přehled zdrojů; samostatné analytické články vznikají až po kontrole.
"""
from __future__ import annotations
import hashlib, html, json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'city-news.json'
UA='NaseKadanBot/1.0 (+https://nasekadan.cz; info@nasekadan.cz)'
SOURCES=[
 {'name':'Kadaňské noviny','url':'https://www.noviny-kadan.cz/vsechny-clanky/','category':'Město'},
 {'name':'Sportovní zařízení Kadaň','url':'https://www.sportkadan.cz/','category':'Sport'},
 {'name':'SK Kadaň','url':'https://www.skkadan.cz/','category':'Sport'},
 {'name':'Nemocnice Kadaň','url':'https://www.nemkadan.cz/pro-verejnost/verejnost/aktuality/','category':'Zdravotnictví'},
]

def fetch(url):
 req=Request(url,headers={'User-Agent':UA,'Accept-Language':'cs,en;q=0.7'})
 with urlopen(req,timeout=25) as r:return r.read().decode(r.headers.get_content_charset() or 'utf-8',errors='replace')

def clean(v):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',str(v or '')))).strip()

def parse(page,source):
 out=[]
 # Odkaz + textový blok; vyžadujeme datum DD.MM.YYYY nebo D.M.YYYY v blízkosti.
 for href,body in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',page,re.I|re.S):
  title=clean(body)
  if len(title)<5 or len(title)>180:continue
  pos=page.find(href)
  around=clean(page[max(0,pos-350):pos+900]) if pos>=0 else ''
  m=re.search(r'(\d{1,2})[./]\s*(\d{1,2})[./]\s*(20\d{2})',around)
  if not m:continue
  d,mo,y=map(int,m.groups())
  url=urljoin(source['url'],href)
  if url==source['url']:continue
  desc=around.replace(title,'',1)[:420].strip(' -|')
  key=hashlib.sha1(f'{title}|{y}-{mo}-{d}|{url}'.encode()).hexdigest()[:10]
  out.append({'id':key,'title':title,'date':f'{y:04d}-{mo:02d}-{d:02d}','category':source['category'],'description':desc,'source':url,'sourceName':source['name']})
 return out

def main():
 items=[];errors=[];used=[]
 for source in SOURCES:
  try:
   parsed=parse(fetch(source['url']),source)
   items.extend(parsed);used.append(f"{source['name']} ({len(parsed)})")
  except Exception as exc:errors.append(f"{source['name']}: {exc}")
 unique={}
 for item in items:
  key=(item['title'].lower(),item['date'])
  if key not in unique or len(item['description'])>len(unique[key]['description']):unique[key]=item
 payload={'generatedAt':datetime.now(timezone.utc).isoformat(),'sources':used,'errors':errors,'items':sorted(unique.values(),key=lambda x:x['date'],reverse=True)[:40]}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(OUT)
 print(f'Uloženo {len(payload["items"])} novinek.')

if __name__=='__main__':main()
