(function(){
  if(!document.querySelector('link[data-article-adstream-css]')){
    const style=document.createElement('link');
    style.rel='stylesheet';
    style.href='/reklamy-sidebar.css?v=20260724-adstream-1';
    style.setAttribute('data-article-adstream-css','true');
    document.head.appendChild(style);
  }

  function orderedTowerPool(context){
    if(typeof towerCreativeItems==='undefined')return [];
    const exact=towerCreativeItems.filter(item=>Array.isArray(item.contexts)&&item.contexts.includes(context));
    const fallback=towerCreativeItems.filter(item=>!exact.includes(item));
    return [...exact,...fallback].filter((item,index,array)=>
      item&&item.image&&item.url&&array.findIndex(entry=>entry.id===item.id)===index
    );
  }

  function rebuildArticleAdStream(){
    const shell=document.querySelector('main.article-shell');
    const article=shell?.querySelector('article.article');
    const sidebar=shell?.querySelector('aside.sticky');
    if(!shell||!article||!sidebar)return;

    document.querySelectorAll('.article-ad-rail').forEach(node=>node.remove());
    sidebar.querySelectorAll(':scope > .article-aside-tower,:scope > .article-aside-adstream').forEach(node=>node.remove());

    let context='general';
    try{
      if(typeof inferPromoContext==='function')context=inferPromoContext(`${document.title} ${article.textContent||''}`);
    }catch(error){
      console.warn('Nepodařilo se určit kontext reklamy.',error);
    }

    const pool=orderedTowerPool(context);
    if(!pool.length)return;

    const editorialHeight=[...sidebar.querySelectorAll(':scope > .sidebox')]
      .reduce((sum,node)=>sum+node.getBoundingClientRect().height+18,0);
    const articleHeight=Math.max(article.scrollHeight,article.getBoundingClientRect().height);
    const desktop=window.matchMedia('(min-width:981px)').matches;
    const availableHeight=Math.max(620,articleHeight-editorialHeight);
    const desktopCount=Math.max(1,Math.ceil(availableHeight/640));
    const count=desktop?Math.min(18,desktopCount):Math.min(2,Math.max(1,pool.length));
    const day=new Date().toISOString().slice(0,10);
    const seed=typeof hashSeed==='function'?hashSeed(`${location.pathname}|${day}|sidebar-stream`):0;
    const start=seed%pool.length;

    const stream=document.createElement('div');
    stream.className='article-aside-adstream';
    stream.setAttribute('aria-label','Reklamy vedle článku');

    for(let index=0;index<count;index++){
      const item=pool[(start+index)%pool.length];
      const slot=document.createElement('div');
      slot.className='article-aside-ad';
      slot.dataset.adIndex=String(index+1);
      if(typeof renderTowerRailCard==='function'){
        slot.innerHTML=renderTowerRailCard(item);
      }else{
        slot.innerHTML=`<a class="article-rail-card article-rail-card-tower" href="${item.url}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span class="article-rail-label">Reklama</span><span class="article-rail-tower-picture"><img src="${item.image}" width="300" height="600" alt="${item.title||'Partnerská nabídka'}" loading="lazy" decoding="async"></span></a>`;
      }
      stream.appendChild(slot);
    }

    sidebar.appendChild(stream);
    if(typeof installImageFallbacks==='function')installImageFallbacks(stream);
  }

  window.renderArticleSideRails=rebuildArticleAdStream;

  let resizeTimer;
  window.addEventListener('resize',()=>{
    clearTimeout(resizeTimer);
    resizeTimer=setTimeout(rebuildArticleAdStream,220);
  });

  rebuildArticleAdStream();
  setTimeout(rebuildArticleAdStream,450);
  setTimeout(rebuildArticleAdStream,1400);
})();
