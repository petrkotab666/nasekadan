// Jednotná hlavní navigace a patička pro všechny stránky webu Naše Kadaň.
// Skládají se na jednom místě, aby se mezi stránkami nikdy nerozcházely.
document.addEventListener('DOMContentLoaded',()=>{
  const items=[
    {href:'/',label:'Úvod',section:'home'},
    {href:'/clanky/',label:'Naše články',section:'articles'},
    {href:'/#akce',label:'Akce',section:'events'},
    {href:'/pruvodce/',label:'Průvodce',section:'guide'},
    {href:'/prakticke/',label:'Praktická Kadaň',section:'practical'},
    {href:'/inzerce/',label:'Inzerce',section:'advertising'},
    {href:'/zapojte-se/',label:'Zapojte se',section:'tips'}
  ];

  const path=window.location.pathname.replace(/\/+$/,'')||'/';
  const hash=window.location.hash;
  const activeSection=(()=>{
    if(path.startsWith('/clanky')||path.startsWith('/zpravy'))return 'articles';
    if(path.startsWith('/pruvodce'))return 'guide';
    if(path.startsWith('/prakticke'))return 'practical';
    if(path.startsWith('/inzerce'))return 'advertising';
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

    // Starší site.js mohl tlačítku přidat vlastní posluchač. Klon odstraní
    // původní posluchače a zabrání dvojímu otevření mobilního menu.
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

  // Stejná patička je zároveň napevno zapsaná ve všech HTML souborech.
  // Toto přepsání je druhá pojistka proti staré cache nebo historickým šablonám.
  let footer=document.querySelector('footer');
  if(!footer){
    footer=document.createElement('footer');
    document.body.appendChild(footer);
  }

  footer.className='site-footer';
  footer.dataset.siteFooter='v1';
  footer.innerHTML=`
    <div class="wrap footer-grid">
      <div class="footer-brand">
        <a class="logo" href="/" aria-label="Naše Kadaň – úvodní stránka"><span class="logo-mark">NK</span><span>NAŠE <b>KADAŇ</b></span></a>
        <p>Nezávislé informace, události a příběhy města.</p>
      </div>
      <div class="footer-column">
        <strong>Obsah webu</strong>
        <a href="/">Úvod</a>
        <a href="/clanky/">Naše články</a>
        <a href="/#akce">Akce</a>
        <a href="/pruvodce/">Průvodce</a>
        <a href="/prehled-zdroju/">Přehled zdrojů</a>
      </div>
      <div class="footer-column">
        <strong>Praktické a kontakt</strong>
        <a href="/prakticke/">Praktická Kadaň</a>
        <a href="/doprava/">Doprava</a>
        <a href="/organizace/">Organizace</a>
        <a href="/zapojte-se/">Zapojte se</a>
        <a href="/inzerce/"><b>Inzerce a ceník</b></a>
        <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>
      </div>
    </div>
    <div class="footer-legal">
      <span>© 2026 Naše Kadaň</span>
      <a href="/o-webu/">O webu</a>
      <a href="/inzerce/">Inzerce</a>
      <a href="/ochrana-osobnich-udaju/">Ochrana osobních údajů</a>
      <a href="/o-webu/#provozovatel">Provozovatel</a>
      <a href="mailto:info@nasekadan.cz">Kontakt</a>
    </div>`;
});
