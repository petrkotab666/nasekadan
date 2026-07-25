(()=>{
  'use strict';

  const IMAGE_SELECTOR='.promo-card img,.article-rail-card img';

  function repairImage(image){
    if(!(image instanceof HTMLImageElement)||image.dataset.promoImageRepaired==='1')return;
    image.dataset.promoImageRepaired='1';

    const rail=image.closest('.article-rail-card');
    if(rail){
      rail.classList.add('is-image-error');
      return;
    }

    const banner=image.closest('.promo-banner');
    if(!banner)return;

    const card=image.closest('.promo-card');
    if(card?.classList.contains('promo-card-wide')){
      const title=card.querySelector('.promo-wide-copy strong, strong')?.textContent?.trim()||image.alt||'Partnerská nabídka';
      banner.classList.add('promo-banner-fallback');
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
    }

    const isZonky=/zonky/i.test(`${image.alt||''} ${image.currentSrc||image.src||''}`);
    if(isZonky||(image.complete&&image.naturalWidth===0))repairImage(image);
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

    [100,500,1500,4000].forEach(delay=>setTimeout(()=>watch(),delay));
  }

  document.addEventListener('error',event=>{
    if(event.target instanceof HTMLImageElement)repairImage(event.target);
  },true);

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
