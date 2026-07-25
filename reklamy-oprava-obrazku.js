(()=>{
  'use strict';

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

  function watch(root=document){
    root.querySelectorAll('.promo-card img,.article-rail-card img').forEach(image=>{
      image.addEventListener('error',()=>repairImage(image),{once:true});
      if(image.complete&&image.naturalWidth===0)repairImage(image);
    });
  }

  document.addEventListener('error',event=>{
    if(event.target instanceof HTMLImageElement)repairImage(event.target);
  },true);

  document.addEventListener('DOMContentLoaded',()=>{
    watch();
    const observer=new MutationObserver(records=>{
      for(const record of records){
        for(const node of record.addedNodes){
          if(node instanceof Element){
            if(node.matches('.promo-card img,.article-rail-card img'))watch(node.parentElement||document);
            else watch(node);
          }
        }
      }
    });
    observer.observe(document.body,{childList:true,subtree:true});
  });
})();
