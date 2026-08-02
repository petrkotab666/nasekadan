(()=>{
  try{
    const faviconHref='/favicon.svg?v=20260801-2';
    document.head.querySelectorAll('link[rel]').forEach(link=>{
      const rel=(link.getAttribute('rel')||'').toLowerCase().split(/\s+/);
      if(rel.includes('icon'))link.remove();
    });

    const primary=document.createElement('link');
    primary.rel='icon';
    primary.type='image/svg+xml';
    primary.sizes='any';
    primary.href=faviconHref;
    primary.setAttribute('data-nasekadan-favicon','primary');
    document.head.appendChild(primary);

    const shortcut=document.createElement('link');
    shortcut.rel='shortcut icon';
    shortcut.type='image/svg+xml';
    shortcut.href=faviconHref;
    shortcut.setAttribute('data-nasekadan-favicon','shortcut');
    document.head.appendChild(shortcut);

    let theme=document.head.querySelector('meta[name="theme-color"]');
    if(!theme){
      theme=document.createElement('meta');
      theme.name='theme-color';
      document.head.appendChild(theme);
    }
    theme.content='#9f2626';
  }catch(_){ }

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

  if(!document.querySelector('script[data-privacy-controls-loader]')){
    const privacy=document.createElement('script');
    privacy.src='/privacy-controls.js?v=20260802-seznam-partner-1';
    privacy.defer=true;
    privacy.setAttribute('data-privacy-controls-loader','1');
    document.head.appendChild(privacy);
  }
})();
