(()=>{
  'use strict';

  const FACEBOOK_URL='https://www.facebook.com/nasekadan/';
  const noindex=document.querySelector('meta[name="robots"]')?.content?.toLowerCase().includes('noindex');
  if(noindex||document.documentElement.dataset.facebookFollowReady==='1')return;
  document.documentElement.dataset.facebookFollowReady='1';

  function trackFacebookClick(placement){
    const payload={
      path:`/odchod/facebook/${placement}`,
      title:`Facebook follow: ${placement}`,
      referrer:location.pathname,
    };
    const body=JSON.stringify(payload);
    try{
      if(navigator.sendBeacon){
        navigator.sendBeacon('/api/analytics/pageview',new Blob([body],{type:'application/json'}));
      }else{
        fetch('/api/analytics/pageview',{
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body,
          keepalive:true,
          credentials:'same-origin',
        }).catch(()=>{});
      }
    }catch(_){ }
  }

  function linkMarkup(placement,label='Sledovat na Facebooku'){
    return `<a class="facebook-follow-link" data-facebook-placement="${placement}" href="${FACEBOOK_URL}" target="_blank" rel="noopener noreferrer"><span aria-hidden="true" class="facebook-follow-icon">f</span><span>${label}</span><b aria-hidden="true">→</b></a>`;
  }

  function addStyles(){
    if(document.getElementById('facebook-follow-styles'))return;
    const style=document.createElement('style');
    style.id='facebook-follow-styles';
    style.textContent=`
      .nav-facebook-link{display:inline-flex!important;align-items:center;gap:7px;padding:9px 13px!important;border-radius:999px;background:#1877f2;color:#fff!important;font-weight:850!important;box-shadow:0 7px 18px rgba(24,119,242,.2);white-space:nowrap}
      .nav-facebook-link:before{content:'f';display:grid;place-items:center;width:20px;height:20px;border-radius:50%;background:#fff;color:#1877f2;font:900 16px/1 Arial,sans-serif}
      .facebook-follow-box{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:28px;margin:42px auto;padding:30px 34px;border-radius:22px;background:linear-gradient(135deg,#0b3974 0%,#1877f2 60%,#0b4ea2 100%);color:#fff;box-shadow:0 18px 45px rgba(11,57,116,.22)}
      .facebook-follow-box:after{content:'f';position:absolute;right:165px;top:50%;transform:translateY(-50%);color:#fff;font:900 190px/1 Arial,sans-serif;opacity:.07;pointer-events:none}
      .facebook-follow-box__copy{position:relative;z-index:1;min-width:0}
      .facebook-follow-box__eyebrow{display:block;margin-bottom:5px;color:#dbeaff;font-size:12px;font-weight:900;letter-spacing:.11em;text-transform:uppercase}
      .facebook-follow-box h2,.facebook-follow-box h3{margin:0 0 8px;color:#fff;font:800 clamp(27px,3vw,39px)/1.08 Georgia,serif;letter-spacing:-.02em}
      .facebook-follow-box p{margin:0;color:#edf5ff;font-size:17px;line-height:1.55}
      .facebook-follow-link{position:relative;z-index:1;display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:52px;padding:13px 20px;border-radius:999px;background:#fff;color:#0b4ea2!important;text-decoration:none!important;font-weight:900;white-space:nowrap;box-shadow:0 10px 24px rgba(0,0,0,.14);transition:transform .18s ease,box-shadow .18s ease}
      .facebook-follow-link:hover{transform:translateY(-2px);box-shadow:0 14px 30px rgba(0,0,0,.2)}
      .facebook-follow-icon{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#1877f2;color:#fff;font:900 22px/1 Arial,sans-serif}
      .facebook-follow-box--article{margin:42px 0 34px;padding:26px 28px}
      .facebook-follow-box--article h3{font-size:30px}
      .facebook-follow-footer{margin:20px auto 0;padding:18px 20px;border:1px solid rgba(255,255,255,.14);border-radius:16px;background:rgba(255,255,255,.07)}
      .facebook-follow-footer__inner{display:flex;align-items:center;justify-content:space-between;gap:18px}
      .facebook-follow-footer strong{display:block;color:#fff;font-size:17px}
      .facebook-follow-footer span.facebook-follow-footer__text{display:block;margin-top:3px;color:#bcc9d0;font-size:14px}
      .facebook-follow-footer .facebook-follow-link{min-height:44px;padding:9px 15px;font-size:14px}
      .facebook-follow-footer .facebook-follow-icon{width:24px;height:24px;font-size:19px}
      @media(max-width:900px){
        .facebook-follow-box{grid-template-columns:1fr;gap:20px;padding:27px 25px}
        .facebook-follow-box:after{right:-10px;top:60%;font-size:170px}
        .facebook-follow-link{width:max-content;max-width:100%}
        .facebook-follow-footer__inner{align-items:flex-start;flex-direction:column}
      }
      @media(max-width:700px){
        .nav-facebook-link{border-radius:10px;padding:11px 13px!important}
        .facebook-follow-box{margin:32px auto;padding:23px 20px;border-radius:18px}
        .facebook-follow-box h2,.facebook-follow-box h3,.facebook-follow-box--article h3{font-size:27px}
        .facebook-follow-box p{font-size:16px}
        .facebook-follow-link{width:100%;white-space:normal;text-align:center}
      }
    `;
    document.head.appendChild(style);
  }

  function addNavigationLink(){
    document.querySelectorAll('.head nav').forEach(nav=>{
      if(nav.querySelector('.nav-facebook-link'))return;
      const link=document.createElement('a');
      link.className='nav-facebook-link';
      link.href=FACEBOOK_URL;
      link.target='_blank';
      link.rel='noopener noreferrer';
      link.dataset.facebookPlacement='menu';
      link.textContent='Facebook';
      nav.appendChild(link);
    });
  }

  function addHomepageBox(){
    if(!['/','/index.html'].includes(location.pathname)||document.querySelector('[data-facebook-follow="home"]'))return;
    const anchor=document.querySelector('.home-articles')||document.querySelector('main .hero');
    if(!anchor)return;
    const section=document.createElement('section');
    section.className='wrap facebook-follow-box facebook-follow-box--home';
    section.dataset.facebookFollow='home';
    section.setAttribute('aria-label','Sledujte Naše Kadaň na Facebooku');
    section.innerHTML=`<div class="facebook-follow-box__copy"><span class="facebook-follow-box__eyebrow">NAŠE KADAŇ NA FACEBOOKU</span><h2>Neunikne vám nic důležitého z Kadaně</h2><p>Nové články, rychlá upozornění a zajímavosti z města uvidíte hned po zveřejnění.</p></div>${linkMarkup('homepage')}`;
    anchor.after(section);
  }

  function addArticleBox(){
    const article=document.querySelector('article.article');
    if(!article||article.querySelector('[data-facebook-follow="article"]'))return;
    const box=document.createElement('section');
    box.className='facebook-follow-box facebook-follow-box--article';
    box.dataset.facebookFollow='article';
    box.setAttribute('aria-label','Sledujte Naše Kadaň na Facebooku');
    box.innerHTML=`<div class="facebook-follow-box__copy"><span class="facebook-follow-box__eyebrow">ČTĚTE NÁS PRAVIDELNĚ</span><h3>Neunikne vám další článek z Kadaně</h3><p>Sledujte Naše Kadaň na Facebooku a nový text uvidíte hned po zveřejnění.</p></div>${linkMarkup('article')}`;
    const source=article.querySelector(':scope > .source-list');
    if(source)source.before(box);else article.appendChild(box);
  }

  function addFooterBox(){
    const footer=document.querySelector('footer.site-footer,footer');
    if(!footer||footer.querySelector('[data-facebook-follow="footer"]'))return;
    const box=document.createElement('div');
    box.className='wrap facebook-follow-footer';
    box.dataset.facebookFollow='footer';
    box.innerHTML=`<div class="facebook-follow-footer__inner"><div><strong>Sledujte Naše Kadaň na Facebooku</strong><span class="facebook-follow-footer__text">Aktuální články a upozornění z města přímo ve vašem přehledu.</span></div>${linkMarkup('footer','Přejít na Facebook')}</div>`;
    const legal=footer.querySelector('.footer-legal');
    if(legal)legal.before(box);else footer.appendChild(box);
  }

  addStyles();
  addNavigationLink();
  addHomepageBox();
  addArticleBox();
  addFooterBox();

  document.addEventListener('click',event=>{
    const link=event.target.closest('[data-facebook-placement]');
    if(!link)return;
    trackFacebookClick(link.dataset.facebookPlacement||'unknown');
  },true);
})();
