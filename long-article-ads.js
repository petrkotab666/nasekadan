(()=>{
  'use strict';
  const VERSION='20260731-long-articles-2';

  function meaningful(node){
    return node instanceof Element && !node.matches('script,style,.tag,.source-list,.next-teaser,.author-box,.article-footer,[data-promos],.featured-cleaning-ad,.nk-horko-feed') &&
      (node.matches('p,ul,ol,table,blockquote,.callout,.factcheck,.numbers,.scenario-grid,.article-photo,h2,h3') || (node.textContent||'').trim().length>=120);
  }
  function context(text){
    const value=String(text||'').toLocaleLowerCase('cs');
    if(/auto|vozidl|doprav|řidič|silnic/.test(value))return 'auto';
    if(/nemocnic|lékař|zdrav|pacient|ambulanc/.test(value))return 'health';
    if(/finance|milion|dotac|náklad|rozpočet|cena/.test(value))return 'finance';
    if(/byt|dům|domác|stavb|energie|oprava/.test(value))return 'home';
    if(/výlet|dovolen|cestov|koupališt|léto/.test(value))return 'travel';
    return 'local';
  }
  function desiredSlots(article,height){
    const chars=(article.textContent||'').replace(/\s+/g,' ').trim().length;
    if(height>=9000||chars>=26000)return 7;
    if(height>=7000||chars>=21000)return 6;
    if(height>=5200||chars>=16000)return 5;
    if(height>=3600||chars>=11000)return 4;
    if(height>=2200||chars>=7000)return 3;
    if(height>=1200||chars>=4000)return 2;
    if(height>=650||chars>=2200)return 1;
    return 0;
  }
  function distribute(){
    const article=document.querySelector('article.article');
    if(!article||typeof renderPromos!=='function')return;
    article.querySelectorAll(':scope > .article-ad-auto[data-promos]').forEach(node=>node.remove());
    const children=[...article.children];
    const end=article.querySelector(':scope > .source-list,:scope > .next-teaser,:scope > .author-box,:scope > .article-footer');
    const endIndex=end?children.indexOf(end):children.length;
    const candidates=children.slice(0,endIndex<0?children.length:endIndex).filter(meaningful);
    if(!candidates.length)return;
    const top=article.getBoundingClientRect().top;
    const first=candidates[0].getBoundingClientRect().top-top;
    const bottom=end?end.getBoundingClientRect().top-top:article.scrollHeight;
    const height=Math.max(0,bottom-first);
    const desired=Math.min(desiredSlots(article,height),candidates.length);
    if(!desired)return;
    const minIndexGap=Math.max(2,Math.floor(candidates.length/(desired+1)*0.55));
    const chosen=[];
    for(let i=0;i<desired;i++){
      const target=Math.round((i+1)*candidates.length/(desired+1));
      let index=Math.min(candidates.length-1,Math.max(0,target));
      while(chosen.some(value=>Math.abs(value-index)<minIndexGap)&&index<candidates.length-1)index++;
      if(chosen.some(value=>Math.abs(value-index)<2))continue;
      chosen.push(index);
    }
    chosen.sort((a,b)=>b-a).forEach((candidateIndex,reverseIndex)=>{
      const actualIndex=chosen.length-1-reverseIndex;
      const anchor=candidates[candidateIndex];
      const box=document.createElement('section');
      box.className='article-ad article-ad-auto';
      box.dataset.promos='';
      box.dataset.context=context((anchor.textContent||'')+' '+(anchor.nextElementSibling?.textContent||''));
      box.dataset.layout=actualIndex%2===0?'banner':'feed';
      box.dataset.count=box.dataset.layout==='banner'?'1':'3';
      anchor.after(box);
    });
    renderPromos();
    article.dataset.longArticleAds=VERSION;
  }
  function start(){
    setTimeout(distribute,250);
    setTimeout(distribute,1200);
    setTimeout(distribute,3200);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
