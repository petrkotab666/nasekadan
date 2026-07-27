#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
path = root / 'reklamy.js'
text = path.read_text(encoding='utf-8')

replacements = {
"{id:'pojistime',title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',tag:'Pojištění',contexts:['finance','auto','home','travel','sidebar','general']}":
"{id:'pojistime',title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',banner:'/assets/reklamy/pojistime-300x600.svg',tag:'Pojištění',contexts:['finance','auto','home','travel','sidebar','general']}",
"{id:'vyklidime',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',tag:'Místní služba',contexts:['home','sidebar','local','general']}":
"{id:'vyklidime',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',banner:'/assets/reklamy/vyklidime-300x600.svg',tag:'Místní služba',contexts:['home','sidebar','local','general']}",
"{id:'uklizecka',title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',tag:'Místní služba',contexts:['home','sidebar','local','general']}":
"{id:'uklizecka',title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',banner:'/assets/reklamy/vaseuklizecka-300x600.svg',tag:'Místní služba',contexts:['home','sidebar','local','general']},\n  {id:'realitykadan',title:'RealityKadan.cz',text:'Prodej, pronájem a výkup bytů, domů, pozemků a garáží v Kadani a okolí.',url:'https://realitykadan.cz',banner:'/assets/reklamy/realitykadan-300x600.svg',tag:'Místní reality',contexts:['home','sidebar','local','general']}",
}

for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f'Nenalezen očekávaný reklamní záznam: {old[:60]}')

start = text.find('function renderArticleSideRails(){')
end_marker = '\n\ndocument.addEventListener(\'DOMContentLoaded\''
end = text.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit('Nenalezena funkce renderArticleSideRails nebo konec souboru.')

new_function = r'''function renderArticleSideRails(){
  const shell=document.querySelector('main.article-shell');
  const article=shell?.querySelector('article.article');
  const sidebar=shell?.querySelector('aside.sticky');
  if(!shell||!article||!sidebar||sidebar.querySelector('.article-side-ad-column'))return;

  const ids=['pojistime','uklizecka','vyklidime','realitykadan'];
  const items=ids.map(id=>promoItems.find(item=>item.id===id)).filter(Boolean);
  if(!items.length)return;

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
    const existing=[...sidebar.children].filter(node=>node!==column)
      .reduce((sum,node)=>sum+node.getBoundingClientRect().height,0);
    column.style.minHeight=`${Math.max(900,article.scrollHeight-existing-32)}px`;
  };
  resize();
  window.addEventListener('load',resize,{once:true});
  window.addEventListener('resize',resize,{passive:true});
  installImageFallbacks(column);
}
'''

text = text[:start] + new_function + text[end:]

style_anchor = "    .article-ad-auto{margin:52px 0}\n"
style_addition = r'''    .article-ad-auto{margin:52px 0}
    .article-ad-rail{display:none!important}
    .article-sidebar-with-ads{position:relative!important;top:auto!important;align-self:stretch!important;display:flex!important;flex-direction:column}
    .article-side-ad-column{display:flex;flex:1;flex-direction:column;justify-content:space-between;gap:64px;margin-top:28px;padding-bottom:12px}
    .article-side-ad-column .article-rail-card{width:100%;max-width:300px;max-height:none;margin:0 auto;border-radius:18px}
    .article-side-ad-column .article-rail-tower-picture{min-height:auto}
    .article-side-ad-column .article-rail-tower-picture img{display:block;width:100%;height:auto;aspect-ratio:1/2;object-fit:contain;padding:0}
    @media(max-width:980px){.article-side-ad-column{display:none!important}}
'''
if style_addition not in text:
    if style_anchor not in text:
        raise SystemExit('Nenalezen bod pro doplnění CSS reklamního sloupce.')
    text = text.replace(style_anchor, style_addition, 1)

path.write_text(text, encoding='utf-8', newline='\n')
print('Reklamy byly přesunuty do pravého sloupce po celé délce článku.')
