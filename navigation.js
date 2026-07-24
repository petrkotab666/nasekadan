// Jednotná hlavní navigace pro všechny stránky webu Naše Kadaň.
// Menu se skládá na jednom místě, aby se mezi stránkami nikdy nerozcházelo.
document.addEventListener('DOMContentLoaded',()=>{
  const items=[
    {href:'/',label:'Úvod',section:'home'},
    {href:'/clanky/',label:'Články',section:'articles'},
    {href:'/#akce',label:'Akce',section:'events'},
    {href:'/pruvodce/',label:'Průvodce',section:'guide'},
    {href:'/zapojte-se/',label:'Poslat tip',section:'tips'}
  ];

  const path=window.location.pathname.replace(/\/+$/,'')||'/';
  const hash=window.location.hash;
  const activeSection=(()=>{
    if(path.startsWith('/clanky')||path.startsWith('/zpravy'))return 'articles';
    if(path.startsWith('/pruvodce'))return 'guide';
    if(path.startsWith('/zapojte-se'))return 'tips';
    if(path==='/'&&hash==='#akce')return 'events';
    if(path==='/')return 'home';
    return '';
  })();

  document.querySelectorAll('header .head').forEach(head=>{
    const nav=head.querySelector('nav');
    if(!nav)return;

    nav.setAttribute('aria-label','Hlavní navigace');
    nav.innerHTML=items.map(item=>{
      const current=item.section===activeSection?' aria-current="page" class="is-current"':'';
      return `<a href="${item.href}"${current}>${item.label}</a>`;
    }).join('');

    let button=head.querySelector('.menu-toggle');
    if(!button){
      button=document.createElement('button');
      button.className='menu-toggle';
      button.type='button';
      button.innerHTML='<span></span><span></span><span></span>';
      head.appendChild(button);
    }

    const setMenuState=open=>{
      nav.classList.toggle('is-open',open);
      button.classList.toggle('is-open',open);
      button.setAttribute('aria-expanded',String(open));
      button.setAttribute('aria-label',open?'Zavřít hlavní menu':'Otevřít hlavní menu');
    };

    button.setAttribute('aria-controls','main-navigation');
    nav.id='main-navigation';
    setMenuState(false);

    // Vlastní obsluha je potřeba také na stránkách, které starší site.js nenačítají.
    if(!button.dataset.unifiedMenu){
      button.dataset.unifiedMenu='true';
      button.addEventListener('click',()=>setMenuState(!nav.classList.contains('is-open')));
    }

    nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>setMenuState(false)));
  });
});
