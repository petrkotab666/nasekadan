(()=>{
  const state={configured:false,loaded:false,error:false};

  const setStatus=(text)=>{
    document.querySelectorAll('[data-cmp-status]').forEach((node)=>{node.textContent=text;});
  };

  const openSettings=(event)=>{
    if(event)event.preventDefault();
    if(typeof window.__tcfapi==='function'){
      try{
        window.__tcfapi('displayConsentUi',2,()=>{});
        return;
      }catch(_){ }
    }
    if(location.pathname==='/cookies/'||location.pathname==='/cookies'){
      setStatus(state.configured
        ? 'Nastavení souhlasu se nyní nepodařilo otevřít. Obnovte stránku nebo napište na info@nasekadan.cz.'
        : 'Reklamní CMP zatím není aktivní, protože Seznam reklamy na webu ještě neběží. Žádné reklamní cookies Seznam Partneru se nyní nenačítají.');
      location.hash='nastaveni';
    }else{
      location.href='/cookies/#nastaveni';
    }
  };

  const normalizeFooter=()=>{
    document.querySelectorAll('.footer-legal').forEach((footer)=>{
      footer.querySelectorAll('a[href="/o-webu/#provozovatel"],a[href="/o-webu/#provozovatel/"]').forEach((link)=>{
        link.href='/provozovatel/';
      });

      const contact=Array.from(footer.querySelectorAll('a')).find((link)=>link.href.startsWith('mailto:'));
      const insert=(link)=>{contact?footer.insertBefore(link,contact):footer.appendChild(link);};

      if(!footer.querySelector('a[href="/cookies/"]')){
        const link=document.createElement('a');
        link.href='/cookies/';
        link.textContent='Cookies';
        insert(link);
      }
      if(!footer.querySelector('a[href="/provozovatel/"]')){
        const link=document.createElement('a');
        link.href='/provozovatel/';
        link.textContent='Provozovatel';
        insert(link);
      }
      if(!footer.querySelector('[data-open-privacy-settings]')){
        const link=document.createElement('a');
        link.href='/cookies/#nastaveni';
        link.textContent='Nastavení soukromí';
        link.setAttribute('data-open-privacy-settings','');
        insert(link);
      }
    });

    document.querySelectorAll('[data-open-privacy-settings]').forEach((control)=>{
      if(control.dataset.privacyBound==='1')return;
      control.dataset.privacyBound='1';
      control.addEventListener('click',openSettings);
    });
  };

  const loadCmp=async()=>{
    try{
      const response=await fetch('/cmp-config.json',{cache:'no-store',credentials:'same-origin'});
      if(!response.ok)return;
      const config=await response.json();
      const scriptUrl=String(config&&config.scriptUrl||'').trim();
      state.configured=Boolean(config&&config.enabled&&/^https:\/\//i.test(scriptUrl));
      if(!state.configured){
        setStatus('Reklamní CMP zatím není aktivní, protože Seznam reklamy na webu ještě neběží. Žádné reklamní cookies Seznam Partneru se nyní nenačítají.');
        return;
      }
      if(document.querySelector('script[data-nk-cmp]'))return;
      const script=document.createElement('script');
      script.src=scriptUrl;
      script.async=true;
      script.setAttribute('data-nk-cmp','1');
      script.addEventListener('load',()=>{
        state.loaded=true;
        setStatus('Správa souhlasu je aktivní. Tlačítkem můžete svůj souhlas kdykoli změnit nebo odvolat.');
      });
      script.addEventListener('error',()=>{
        state.error=true;
        setStatus('Správu souhlasu se nepodařilo načíst. Reklamní technologie vyžadující souhlas proto nesmějí být spuštěny.');
      });
      document.head.appendChild(script);
    }catch(_){
      state.error=true;
    }
  };

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',()=>{normalizeFooter();loadCmp();});
  }else{
    normalizeFooter();
    loadCmp();
  }
})();
