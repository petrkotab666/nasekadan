(()=>{
  try{
    if(navigator.doNotTrack!=='1'){
      const payload={
        path:location.pathname,
        title:document.title,
        referrer:document.referrer?new URL(document.referrer).hostname:'',
      };
      const body=JSON.stringify(payload);
      const endpoint='/api/newsletter/analytics/pageview';
      if(navigator.sendBeacon){
        navigator.sendBeacon(endpoint,new Blob([body],{type:'application/json'}));
      }else{
        fetch(endpoint,{
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body,
          keepalive:true,
          credentials:'same-origin',
        }).catch(()=>{});
      }
    }
  }catch(_){ }

  if(!document.querySelector('script[data-facebook-follow-loader]')){
    const script=document.createElement('script');
    script.src='/facebook-follow.js?v=20260801-1';
    script.defer=true;
    script.setAttribute('data-facebook-follow-loader','1');
    document.head.appendChild(script);
  }
})();
