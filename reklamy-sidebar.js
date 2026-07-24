(function(){
  const ASSET_VERSION='20260724-adstream-3';

  if(!document.querySelector('link[data-article-adstream-css]')){
    const style=document.createElement('link');
    style.rel='stylesheet';
    style.href=`/reklamy-sidebar.css?v=${ASSET_VERSION}`;
    style.setAttribute('data-article-adstream-css','true');
    document.head.appendChild(style);
  }

  function normalizePartnerKey(value){
    const raw=String(value||'partner');
    if(typeof normalizeToken==='function')return normalizeToken(raw);
    return raw
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g,'')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g,'-')
      .replace(/^-+|-+$/g,'');
  }

  function partnerKey(item){
    return normalizePartnerKey(item?.title||item?.partner||item?.id||item?.url);
  }

  function uniqueByCreative(items){
    const seenIds=new Set();
    const seenImages=new Set();
    return items.filter(entry=>{
      const id=String(entry?.id||'');
      const image=String(entry?.image||entry?.banner||'');
      if(!id||seenIds.has(id))return false;
      if(image&&seenImages.has(image))return false;
      seenIds.add(id);
      if(image)seenImages.add(image);
      return true;
    });
  }

  function combinedPartnerPool(context){
    const towerSource=typeof towerCreativeItems==='undefined'?[]:towerCreativeItems;
    const promoSource=typeof promoItems==='undefined'?[]:promoItems;

    const towers=uniqueByCreative(towerSource
      .filter(item=>item&&item.image&&item.url)
      .map(item=>({kind:'tower',item,key:partnerKey(item),id:`tower:${item.id}`})));

    const promos=uniqueByCreative(promoSource
      .filter(item=>item&&item.url)
      .map(item=>({kind:'custom',item,key:partnerKey(item),id:`custom:${item.id}`})));

    const exact=[
      ...towers.filter(entry=>Array.isArray(entry.item.contexts)&&entry.item.contexts.includes(context)),
      ...promos.filter(entry=>Array.isArray(entry.item.contexts)&&entry.item.contexts.includes(context))
    ];
    const fallback=[
      ...towers.filter(entry=>!exact.includes(entry)),
      ...promos.filter(entry=>!exact.includes(entry))
    ];

    const ordered=[...exact,...fallback];
    const seenCreative=new Set();
    return ordered.filter(entry=>{
      if(!entry.key||seenCreative.has(entry.id))return false;
      seenCreative.add(entry.id);
      return true;
    });
  }

  function selectVariedAds(pool,count,seed){
    if(!pool.length||count<1)return [];
    const start=seed%pool.length;
    const rotated=[...pool.slice(start),...pool.slice(0,start)];
    const selected=[];
    const usedPartnerKeys=new Set();

    // Nejdřív použít co nejvíce různých partnerů bez jediného opakování.
    for(const entry of rotated){
      if(usedPartnerKeys.has(entry.key))continue;
      selected.push(entry);
      usedPartnerKeys.add(entry.key);
      if(selected.length===count)return selected;
    }

    // Až po vyčerpání všech partnerů lze začít další kolo, nikdy však stejný partner za sebou.
    let cursor=0;
    let safety=0;
    while(selected.length<count&&safety<count*pool.length*3){
      const entry=rotated[cursor%rotated.length];
      const previous=selected[selected.length-1];
      cursor+=1;
      safety+=1;
      if(previous&&entry.key===previous.key)continue;
      selected.push(entry);
    }

    return selected;
  }

  function renderEntry(entry){
    if(entry.kind==='tower'&&typeof renderTowerRailCard==='function'){
      return renderTowerRailCard(entry.item);
    }
    if(entry.kind==='custom'&&typeof renderCustomRailCard==='function'){
      return renderCustomRailCard(entry.item);
    }

    const item=entry.item||{};
    const title=String(item.title||'Partnerská nabídka');
    const url=String(item.url||'#');
    const image=String(item.image||item.banner||'');
    if(image){
      return `<a class="article-rail-card article-rail-card-tower" href="${url}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span class="article-rail-label">Reklama</span><span class="article-rail-tower-picture"><img src="${image}" width="300" height="600" alt="${title}" loading="lazy" decoding="async"></span><span class="article-rail-fallback">${title}</span></a>`;
    }
    return `<a class="article-rail-card article-rail-card-custom" href="${url}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span class="article-rail-label">Reklama</span><span class="article-rail-copy"><strong>${title}</strong><span>${String(item.text||'Vybraná partnerská nabídka.')}</span><b>Zjistit více →</b></span></a>`;
  }

  function isDomainTitle(value){
    return /^[^\s]+\.[a-z0-9-]{2,}$/i.test(String(value||'').trim());
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

    const pool=combinedPartnerPool(context);
    if(!pool.length)return;

    const editorialHeight=[...sidebar.querySelectorAll(':scope > .sidebox')]
      .reduce((sum,node)=>sum+node.getBoundingClientRect().height+18,0);
    const articleHeight=Math.max(article.scrollHeight,article.getBoundingClientRect().height);
    const desktop=window.matchMedia('(min-width:981px)').matches;
    const availableHeight=Math.max(620,articleHeight-editorialHeight);
    const desktopCount=Math.max(1,Math.ceil(availableHeight/560));
    const count=desktop?Math.min(24,desktopCount):Math.min(2,Math.max(1,pool.length));
    const day=new Date().toISOString().slice(0,10);
    const seed=typeof hashSeed==='function'?hashSeed(`${location.pathname}|${day}|sidebar-stream-v3`):0;
    const selected=selectVariedAds(pool,count,seed);
    if(!selected.length)return;

    const stream=document.createElement('div');
    stream.className='article-aside-adstream';
    stream.setAttribute('aria-label','Střídající se reklamy vedle článku');

    selected.forEach((entry,index)=>{
      const slot=document.createElement('div');
      slot.className=`article-aside-ad article-aside-ad-${entry.kind}`;
      slot.dataset.adIndex=String(index+1);
      slot.dataset.partner=entry.key;
      slot.innerHTML=renderEntry(entry);
      const title=String(entry.item?.title||'').trim();
      const heading=slot.querySelector('.article-rail-copy strong');
      if(heading&&isDomainTitle(title)){
        heading.classList.add('ad-domain-title');
        heading.setAttribute('title',title);
      }
      stream.appendChild(slot);
    });

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
