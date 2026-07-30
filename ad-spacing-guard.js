(()=>{
  const ARTICLE_SELECTOR='article.article';
  const INLINE_AD_SELECTOR='.featured-cleaning-ad,.article-ad,[data-promos]';

  function isInlineAd(node,article){
    return node instanceof Element&&node.parentElement===article&&node.matches(INLINE_AD_SELECTOR);
  }

  function isMeaningfulContent(node){
    if(!(node instanceof Element))return false;
    if(node.matches('script,style,.tag'))return false;
    if(node.matches('h2,h3,p,ul,ol,blockquote,table,.callout,.factcheck,.numbers,.scenario-grid,.article-photo,.hero-visual,.next-teaser'))return true;
    return (node.textContent||'').trim().length>=80;
  }

  function preferRemoval(previous,current){
    if(current.classList.contains('article-ad-auto'))return current;
    if(previous.classList.contains('article-ad-auto'))return previous;
    if(current.hasAttribute('data-promos'))return current;
    return current;
  }

  function enforceSpacing(){
    const article=document.querySelector(ARTICLE_SELECTOR);
    if(!article)return;

    let previousAd=null;
    let contentBlocks=99;
    for(const node of [...article.children]){
      if(isInlineAd(node,article)){
        if(previousAd&&contentBlocks<2){
          const remove=preferRemoval(previousAd,node);
          remove.remove();
          if(remove===previousAd){
            previousAd=node;
            contentBlocks=0;
          }
          continue;
        }
        previousAd=node;
        contentBlocks=0;
        continue;
      }
      if(previousAd&&isMeaningfulContent(node))contentBlocks++;
    }
  }

  function start(){
    const article=document.querySelector(ARTICLE_SELECTOR);
    if(!article)return;
    let timer=0;
    const schedule=()=>{
      clearTimeout(timer);
      timer=window.setTimeout(enforceSpacing,40);
    };
    new MutationObserver(schedule).observe(article,{childList:true});
    enforceSpacing();
    window.setTimeout(enforceSpacing,350);
    window.setTimeout(enforceSpacing,1400);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
