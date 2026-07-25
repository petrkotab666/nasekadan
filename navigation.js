// Jednotná hlavní navigace pro všechny stránky webu Naše Kadaň.
// Menu se skládá na jednom místě, aby se mezi stránkami nikdy nerozcházelo.
document.addEventListener('DOMContentLoaded',()=>{
  const items=[
    {href:'/',label:'Úvod',section:'home'},
    {href:'/clanky/',label:'Naše články',section:'articles'},
    {href:'/prehled-zdroju/',label:'Přehled zdrojů',section:'sources'},
    {href:'/#akce',label:'Akce',section:'events'},
    {href:'/pruvodce/',label:'Průvodce',section:'guide'},
    {href:'/prakticke/',label:'Praktická Kadaň',section:'practical'},
    {href:'/doprava/',label:'Doprava',section:'transport'},
    {href:'/organizace/',label:'Organizace',section:'organizations'},
    {href:'/zapojte-se/',label:'Zapojte se',section:'tips'}
  ];

  const path=window.location.pathname.replace(/\/+$/,'')||'/';
  const hash=window.location.hash;
  const activeSection=(()=>{
    if(path.startsWith('/clanky')||path.startsWith('/zpravy'))return 'articles';
    if(path.startsWith('/prehled-zdroju'))return 'sources';
    if(path.startsWith('/pruvodce'))return 'guide';
    if(path.startsWith('/prakticke'))return 'practical';
    if(path.startsWith('/doprava'))return 'transport';
    if(path.startsWith('/organizace'))return 'organizations';
    if(path.startsWith('/zapojte-se'))return 'tips';
    if(path==='/'&&hash==='#akce')return 'events';
    if(path==='/')return 'home';
    return '';
  })();

  document.querySelectorAll('header .head').forEach((head,index)=>{
    const nav=head.querySelector('nav');
    if(!nav)return;

    nav.setAttribute('aria-label','Hlavní navigace');
    nav.innerHTML=items.map(item=>{
      const current=item.section===activeSection?' aria-current="page" class="is-current"':'';
      return `<a href="${item.href}"${current}>${item.label}</a>`;
    }).join('');

    // Starší site.js mohl již tlačítku přidat vlastní posluchač. Klon odstraní
    // původní posluchače a zabrání dvojímu otevření/zavření mobilního menu.
    const oldButton=head.querySelector('.menu-toggle');
    let button;
    if(oldButton){
      button=oldButton.cloneNode(true);
      oldButton.replaceWith(button);
    }else{
      button=document.createElement('button');
      button.className='menu-toggle';
      button.type='button';
      button.innerHTML='<span></span><span></span><span></span>';
      head.appendChild(button);
    }

    const navId=index===0?'main-navigation':`main-navigation-${index+1}`;
    nav.id=navId;
    button.setAttribute('aria-controls',navId);

    const setMenuState=open=>{
      nav.classList.toggle('is-open',open);
      button.classList.toggle('is-open',open);
      button.setAttribute('aria-expanded',String(open));
      button.setAttribute('aria-label',open?'Zavřít hlavní menu':'Otevřít hlavní menu');
    };

    setMenuState(false);
    button.addEventListener('click',()=>setMenuState(!nav.classList.contains('is-open')));
    nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>setMenuState(false)));
  });

  // Důležité provozní odkazy se zobrazují v patičce každé veřejné stránky.
  document.querySelectorAll('footer').forEach(footer=>{
    let legal=footer.querySelector('.footer-legal');
    if(!legal){
      legal=document.createElement('div');
      legal.className='footer-legal';
      footer.appendChild(legal);
    }

    const footerLinks=[
      {
        href:'/inzerce/',
        text:'Inzerce',
        aria:'Ceník a podmínky inzerce na webu Naše Kadaň'
      },
      {
        href:'/o-webu/#provozovatel',
        text:'Provozovatel',
        aria:'Identifikační údaje provozovatele webu',
        subtle:true
      }
    ];

    footerLinks.forEach(item=>{
      if(legal.querySelector(`a[href="${item.href}"]`))return;
      const link=document.createElement('a');
      link.href=item.href;
      link.textContent=item.text;
      link.setAttribute('aria-label',item.aria);
      if(item.subtle){
        link.style.fontSize='12px';
        link.style.opacity='.68';
      }
      legal.appendChild(link);
    });
  });
});
