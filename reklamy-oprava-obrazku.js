(()=>{
  'use strict';

  const IMAGE_SELECTOR='.promo-card img,.article-rail-card img';
  const SUMMER_TRAVEL_CONTEXTS=new Set(['general','local','sidebar','family','travel']);
  const TRAVEL_COPY={
    'invia-cz':'Last minute i běžné zájezdy k moři, do hor i za poznáním na jednom místě.',
    'atis-cz':'Pobytové, poznávací a wellness zájezdy po Česku, Slovensku i Evropě.',
    'excursia-cz':'Výlety, exkurze a zážitky pro volný čas v Česku i zahraničí.'
  };

  function localHash(value){
    return [...String(value)].reduce((sum,char)=>((sum*31)+char.charCodeAt(0))>>>0,0);
  }

  function isSummerSeason(){
    const month=new Date().getMonth()+1;
    return month>=5&&month<=9;
  }

  function patchPromoEngine(){
    try{
      if(typeof partnerCopy==='object'&&partnerCopy){
        Object.assign(partnerCopy,TRAVEL_COPY);
      }

      if(typeof contextsFromCategories==='function'){
        const originalContextsFromCategories=contextsFromCategories;
        contextsFromCategories=function(categories){
          const contexts=new Set(originalContextsFromCategories(categories));
          const text=(categories||[]).map(value=>String(value||'').toLocaleLowerCase('cs')).join(' ');
          if(/cestov|dovolen|zájezd|zajezd|last[- ]?minute|pobyt|hotel|wellness|eurovíkend|eurovikend|plavb|výlet|vylet|exkurz/.test(text))contexts.add('travel');
          if(/rodin/.test(text))contexts.add('family');
          return [...contexts];
        };
      }

      if(typeof tagFromContexts==='function'){
        const originalTagFromContexts=tagFromContexts;
        tagFromContexts=function(contexts,categories){
          if(Array.isArray(contexts)&&contexts.includes('travel'))return 'Dovolená a cestování';
          return originalTagFromContexts(contexts,categories);
        };
      }

      if(typeof inferPromoContext==='function'){
        const originalInferPromoContext=inferPromoContext;
        inferPromoContext=function(text){
          const value=String(text||'').toLocaleLowerCase('cs');
          if(/dovolen|zájezd|zajezd|last[- ]?minute|hotel|letišt|letist|cestov|moře|more|pláž|plaz|wellness|výlet|vylet/.test(value))return 'travel';
          return originalInferPromoContext(text);
        };
      }

      if(typeof pickPromos==='function'){
        const originalPickPromos=pickPromos;
        pickPromos=function(context,count,offset){
          const selected=originalPickPromos(context,count,offset);
          if(!isSummerSeason()||!count||!SUMMER_TRAVEL_CONTEXTS.has(context))return selected;
          if(typeof promoItems==='undefined'||!Array.isArray(promoItems))return selected;

          const day=new Date().toISOString().slice(0,10);
          const seed=localHash(`${location.pathname}|${day}|${context}|${offset}|summer-travel`);
          if(context!=='travel'&&seed%3!==0)return selected;
          if(selected.some(item=>item?.contexts?.includes('travel')))return selected;

          const pool=promoItems.filter(item=>item?.contexts?.includes('travel')&&!selected.some(entry=>entry.id===item.id));
          if(!pool.length)return selected;
          const travel=pool[seed%pool.length];

          if(selected.length<count)selected.push(travel);
          else selected[Math.max(0,selected.length-1)]=travel;
          try{
            if(typeof usedPromoIds!=='undefined'&&usedPromoIds?.add)usedPromoIds.add(travel.id);
          }catch{}
          return selected;
        };
      }

      if(typeof renderPromos==='function'){
        const originalRenderPromos=renderPromos;
        renderPromos=function(...args){
          const result=originalRenderPromos.apply(this,args);
          queueMicrotask(()=>watch());
          setTimeout(()=>watch(),250);
          return result;
        };
      }

      if(typeof renderArticleSideRails==='function'){
        const originalRenderArticleSideRails=renderArticleSideRails;
        renderArticleSideRails=function(...args){
          const result=originalRenderArticleSideRails.apply(this,args);
          queueMicrotask(()=>watch());
          setTimeout(()=>watch(),250);
          return result;
        };
      }
    }catch(error){
      console.warn('Doplňková oprava reklam se nepodařila inicializovat.',error);
    }
  }

  function repairImage(image){
    if(!(image instanceof HTMLImageElement)||image.dataset.promoImageRepaired==='1')return;
    image.dataset.promoImageRepaired='1';

    const rail=image.closest('.article-rail-card');
    if(rail){
      rail.classList.add('is-image-error');
      image.removeAttribute('src');
      return;
    }

    const banner=image.closest('.promo-banner');
    if(!banner)return;

    const card=image.closest('.promo-card');
    if(card?.classList.contains('promo-card-wide')){
      const title=card.querySelector('.promo-wide-copy strong, strong')?.textContent?.trim()||image.alt||'Partnerská nabídka';
      banner.classList.add('promo-banner-fallback');
      banner.setAttribute('role','img');
      banner.setAttribute('aria-label',title);
      banner.textContent=title;
    }else{
      banner.remove();
    }
  }

  function watchImage(image){
    if(!(image instanceof HTMLImageElement))return;

    if(image.dataset.promoImageWatched!=='1'){
      image.dataset.promoImageWatched='1';
      image.addEventListener('error',()=>repairImage(image),{once:true});
      setTimeout(()=>{
        if(!image.isConnected||image.dataset.promoImageRepaired==='1')return;
        if(!image.complete||image.naturalWidth===0)repairImage(image);
      },5000);
    }

    if(!image.getAttribute('src')||(image.complete&&image.naturalWidth===0))repairImage(image);
  }

  function watch(root=document){
    if(root instanceof HTMLImageElement)watchImage(root);
    root.querySelectorAll?.(IMAGE_SELECTOR).forEach(watchImage);
  }

  function start(){
    watch();

    const observer=new MutationObserver(records=>{
      for(const record of records){
        for(const node of record.addedNodes){
          if(node instanceof Element)watch(node);
        }
      }
    });
    observer.observe(document.body,{childList:true,subtree:true});

    [50,250,750,1500,4000,6500].forEach(delay=>setTimeout(()=>watch(),delay));
  }

  patchPromoEngine();

  document.addEventListener('error',event=>{
    if(event.target instanceof HTMLImageElement)repairImage(event.target);
  },true);

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
