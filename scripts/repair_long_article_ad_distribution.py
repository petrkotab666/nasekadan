#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "reklamy.js"
REPORT = ROOT / "reports" / "article-ad-distribution-audit.json"
VERSION = "20260731-long-articles-1"

OLD_RE = re.compile(
    r"function redistributeArticlePromos\(\)\{.*?\n\}\n\nfunction ensurePromoStyles\(\)",
    re.S,
)

NEW_FUNCTION = r'''function redistributeArticlePromos(){
  const article=document.querySelector('article.article');
  if(!article)return;

  // Odstranit pouze dříve automaticky vložené sloty. Ruční a úvodní reklamy zůstanou.
  article.querySelectorAll(':scope > .article-ad-auto[data-promos]').forEach(node=>node.remove());

  const children=[...article.children];
  if(children.length<4)return;

  const firstHeading=article.querySelector(':scope > h2,:scope > h3');
  const lead=article.querySelector(':scope > .leadtext');
  const hero=article.querySelector(':scope > .hero-visual');
  const startAnchor=firstHeading||lead||hero||children[0];

  // Některé články nemají .source-list. V takovém případě končí obsah před teaserem,
  // autorským boxem nebo posledním smysluplným blokem článku.
  const explicitEnd=article.querySelector(':scope > .source-list,:scope > .next-teaser,:scope > .author-box,:scope > .article-footer');
  const endAnchor=explicitEnd||children[children.length-1];
  const startIndex=Math.max(0,children.indexOf(startAnchor));
  let endIndex=children.indexOf(endAnchor);
  if(endIndex<0)endIndex=children.length;
  if(endIndex<=startIndex+2)endIndex=children.length;

  const candidates=children.slice(startIndex+1,endIndex).filter(isPlacementCandidate);
  if(!candidates.length)return;

  const articleTop=article.getBoundingClientRect().top;
  const startY=startAnchor.getBoundingClientRect().bottom-articleTop;
  const endY=(explicitEnd?explicitEnd.getBoundingClientRect().top:article.scrollHeight)-articleTop;
  const contentHeight=Math.max(0,endY-startY);
  const textLength=(article.textContent||'').replace(/\s+/g,' ').trim().length;

  // Výška je hlavní údaj, délka textu slouží jako pojistka pro stránky renderované
  // v nezvykle úzkém nebo širokém rozvržení.
  let desired=0;
  if(contentHeight>=9000||textLength>=26000)desired=7;
  else if(contentHeight>=7000||textLength>=21000)desired=6;
  else if(contentHeight>=5200||textLength>=16000)desired=5;
  else if(contentHeight>=3600||textLength>=11000)desired=4;
  else if(contentHeight>=2200||textLength>=7000)desired=3;
  else if(contentHeight>=1200||textLength>=4000)desired=2;
  else if(contentHeight>=650||textLength>=2200)desired=1;
  if(!desired)return;
  desired=Math.min(desired,candidates.length);

  const edgePadding=Math.min(560,Math.max(240,contentHeight*0.055));
  const usableStart=startY+edgePadding;
  const usableEnd=Math.max(usableStart+1,endY-edgePadding);
  const usableHeight=Math.max(1,usableEnd-usableStart);
  const minGap=Math.max(560,usableHeight/(desired+0.65)*0.55);

  let points=candidates.map((node,index)=>({
    node,
    index,
    y:node.getBoundingClientRect().bottom-articleTop
  })).filter(point=>point.y>=usableStart&&point.y<=usableEnd);

  // Při neúplném layoutu (např. obrázek se ještě nenačetl) použít rovnoměrné pořadí
  // bloků místo úplného zrušení reklam.
  if(points.length<desired){
    points=candidates.map((node,index)=>({
      node,index,y:usableStart+(usableHeight*(index+1)/(candidates.length+1))
    }));
  }

  const selected=[];
  let previousY=-Infinity;
  for(let position=0;position<desired;position++){
    const target=usableStart+(usableHeight*(position+0.5)/desired);
    const remaining=desired-position-1;
    const eligible=points.filter(point=>{
      if(selected.some(entry=>entry.index===point.index))return false;
      if(point.y-previousY<minGap)return false;
      return remaining===0||(usableEnd-point.y)>=remaining*minGap*0.68;
    });
    const pool=eligible.length?eligible:points.filter(point=>
      !selected.some(entry=>entry.index===point.index)&&point.y-previousY>=minGap*0.55
    );
    if(!pool.length)break;
    pool.sort((a,b)=>Math.abs(a.y-target)-Math.abs(b.y-target));
    selected.push(pool[0]);
    previousY=pool[0].y;
  }

  selected.forEach((entry,index)=>{
    const block=document.createElement('section');
    block.className='article-ad article-ad-auto';
    block.dataset.promos='';
    block.dataset.context=inferPromoContext(nearbyText(entry.node));
    block.dataset.layout=index%2===0?'banner':'feed';
    block.dataset.count=block.dataset.layout==='banner'?'1':'3';
    entry.node.after(block);
  });
}

function ensurePromoStyles()'''


def strip_tags(text: str) -> str:
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def expected_slots(length: int) -> int:
    if length >= 26000: return 7
    if length >= 21000: return 6
    if length >= 16000: return 5
    if length >= 11000: return 4
    if length >= 7000: return 3
    if length >= 4000: return 2
    if length >= 2200: return 1
    return 0


def audit_articles() -> list[dict]:
    rows=[]
    for path in sorted((ROOT / "clanky").glob("*.html")):
        if path.name == "index.html":
            continue
        raw=path.read_text(encoding="utf-8")
        match=re.search(r'<article\b[^>]*class=["\'][^"\']*\barticle\b[^"\']*["\'][^>]*>(.*?)</article>',raw,re.I|re.S)
        if not match:
            continue
        body=match.group(1)
        length=len(strip_tags(body))
        rows.append({
            "path":str(path.relative_to(ROOT)),
            "textCharacters":length,
            "expectedAutomaticSlots":expected_slots(length),
            "hasH2":bool(re.search(r'<h2\b',body,re.I)),
            "hasSourceList":"source-list" in body,
            "staticPromoSlots":len(re.findall(r'data-promos',body,re.I)),
        })
    return sorted(rows,key=lambda r:r["textCharacters"],reverse=True)


def main() -> int:
    text=JS.read_text(encoding="utf-8")
    updated,count=OLD_RE.subn(NEW_FUNCTION,text,count=1)
    if count != 1:
        raise SystemExit("Funkci redistributeArticlePromos se nepodařilo jednoznačně nahradit.")
    JS.write_text(updated,encoding="utf-8")

    # Nová verze musí obejít cache na všech veřejných stránkách.
    for path in ROOT.rglob("*.html"):
        rel=path.relative_to(ROOT)
        if any(part in {".git",".github","nahled","sdilet"} for part in rel.parts):
            continue
        raw=path.read_text(encoding="utf-8")
        current=re.sub(r'reklamy\.js(?:\?v=[^"\']*)?',f'reklamy.js?v={VERSION}',raw)
        if current != raw:
            path.write_text(current,encoding="utf-8")

    rows=audit_articles()
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "schemaVersion":1,
        "version":VERSION,
        "articleCount":len(rows),
        "longArticles":sum(1 for row in rows if row["expectedAutomaticSlots"]>=3),
        "articles":rows,
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    long_without_source=[r for r in rows if r["expectedAutomaticSlots"]>=3 and not r["hasSourceList"]]
    print(f"Zkontrolováno {len(rows)} článků; dlouhých {sum(r['expectedAutomaticSlots']>=3 for r in rows)}; dlouhých bez source-list {len(long_without_source)}.")
    print(f"Nová reklamní verze: {VERSION}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
