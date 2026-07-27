#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
js_path = root / 'reklamy.js'
text = js_path.read_text(encoding='utf-8')

# Doplnit čtyři vlastní reklamní bannery, pokud ještě nejsou v seznamu.
records = {
    'pojistime': "{id:'pojistime',title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',banner:'/assets/reklamy/pojistime-300x600.svg',tag:'Pojištění',contexts:['finance','auto','home','travel','sidebar','general']}",
    'uklizecka': "{id:'uklizecka',title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',banner:'/assets/reklamy/vaseuklizecka-300x600.svg',tag:'Místní služba',contexts:['home','sidebar','local','general']}",
    'vyklidime': "{id:'vyklidime',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',banner:'/assets/reklamy/vyklidime-300x600.svg',tag:'Místní služba',contexts:['home','sidebar','local','general']}",
    'realitykadan': "{id:'realitykadan',title:'RealityKadan.cz',text:'Prodej, pronájem a výkup bytů, domů, pozemků a garáží v Kadani a okolí.',url:'https://realitykadan.cz',banner:'/assets/reklamy/realitykadan-300x600.svg',tag:'Místní reality',contexts:['home','sidebar','local','general']}",
}

for item_id, record in records.items():
    pattern = re.compile(r"\{id:'" + re.escape(item_id) + r"'.*?\}(?=,?\n)")
    if pattern.search(text):
        text = pattern.sub(record, text, count=1)
    else:
        marker = 'const promoItems=['
        if marker not in text:
            raise SystemExit('Nenalezen seznam promoItems.')
        text = text.replace(marker, marker + '\n  ' + record + ',', 1)

start = text.find('function renderArticleSideRails(){')
end_marker = "\n\ndocument.addEventListener('DOMContentLoaded'"
end = text.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit('Nenalezena funkce renderArticleSideRails.')

new_function = r'''function renderArticleSideRails(){
  const shell=document.querySelector('main.article-shell');
  const article=shell?.querySelector('article.article');
  const sidebar=shell?.querySelector('aside.sticky');
  if(!shell||!article||!sidebar)return;

  sidebar.querySelectorAll('.article-side-ad-column').forEach(node=>node.remove());
  document.querySelectorAll('.article-ad-rail').forEach(node=>node.remove());

  const ids=['pojistime','uklizecka','vyklidime','realitykadan'];
  const items=ids.map(id=>promoItems.find(item=>item.id===id)).filter(Boolean);
  if(items.length!==4)return;

  sidebar.classList.add('article-sidebar-with-ads');
  const column=document.createElement('div');
  column.className='article-side-ad-column';
  column.setAttribute('aria-label','Reklamy v pravém sloupci článku');
  column.innerHTML=items.map(item=>renderTowerRailCard({
    ...item,
    image:item.banner,
    width:300,
    height:600
  })).join('');
  sidebar.appendChild(column);

  const resize=()=>{
    const reserved=[...sidebar.children].filter(node=>node!==column)
      .reduce((sum,node)=>sum+node.getBoundingClientRect().height,0);
    column.style.minHeight=`${Math.max(1200,article.scrollHeight-reserved)}px`;
  };
  resize();
  window.addEventListener('load',resize,{once:true});
  window.addEventListener('resize',resize,{passive:true});
  installImageFallbacks(column);
}
'''
text = text[:start] + new_function + text[end:]

css = r'''
    .article-ad-rail{display:none!important}
    .article-sidebar-with-ads{position:relative!important;top:auto!important;align-self:stretch!important;display:flex!important;flex-direction:column!important}
    .article-side-ad-column{display:flex!important;flex:1;flex-direction:column;justify-content:space-between;gap:72px;margin-top:28px;padding-bottom:24px}
    .article-side-ad-column .article-rail-card{display:flex!important;width:100%;max-width:300px;max-height:none;margin:0 auto;border-radius:18px}
    .article-side-ad-column .article-rail-tower-picture{display:flex!important;min-height:auto}
    .article-side-ad-column .article-rail-tower-picture img{display:block!important;width:100%;height:auto;aspect-ratio:1/2;object-fit:contain;padding:0}
    @media(max-width:980px){
      .article-side-ad-column{display:none!important}
      .article-ad-auto{display:block!important}
    }
'''
if '.article-sidebar-with-ads' not in text:
    anchor = '    .article-ad-auto{margin:52px 0}\n'
    if anchor not in text:
        raise SystemExit('Nenalezen bod pro CSS reklam.')
    text = text.replace(anchor, anchor + css, 1)
else:
    text = re.sub(r"\n    \.article-ad-rail\{display:none!important\}.*?@media\(max-width:980px\)\{\.article-side-ad-column\{display:none!important\}\}\n", '\n' + css, text, count=1, flags=re.S)

js_path.write_text(text, encoding='utf-8', newline='\n')

# Vynutit načtení nové verze reklamního skriptu ve všech článcích.
version = '20260727-right-column-ads-2'
for article in (root / 'clanky').glob('*.html'):
    html = article.read_text(encoding='utf-8')
    updated = re.sub(r'/reklamy\.js\?v=[^"\']+', f'/reklamy.js?v={version}', html)
    if '/reklamy.js' in updated and updated != html:
        article.write_text(updated, encoding='utf-8', newline='\n')

print('Pravý reklamní sloupec obnoven a cache reklamního skriptu obnovena.')
