(()=>{
  'use strict';

  const ITEMS=[
    {
      id:'horko-concept',
      title:'Ventilátory a mobilní klimatizace',
      text:'Výběr domácích spotřebičů pro ochlazení bytu, kanceláře nebo ložnice během horkých dnů.',
      tag:'Ochlazení domácnosti',
      url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b23975b5',
      image:'https://doc.ehub.cz/b/035e8afb/e737c1f9.jpg'
    },
    {
      id:'horko-biano',
      title:'Stínění a vybavení proti přehřívání',
      text:'Rolety, závěsy, venkovní stínění a další vybavení, které pomáhá omezit přehřívání interiéru.',
      tag:'Stínění a bydlení',
      url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=da726a9e',
      image:'https://doc.ehub.cz/b/80610cd6/82a1c42b.png'
    },
    {
      id:'horko-proalergiky',
      title:'Čistší vzduch i během vedra',
      text:'Čističky a další vybavení pro příjemnější prostředí v domácnosti při větrání, pylu a letním horku.',
      tag:'Vzduch v domácnosti',
      url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=abc25217',
      image:'https://doc.ehub.cz/b/cbee71d3/017d5633.jpg'
    }
  ];

  const esc=value=>String(value??'').replace(/[&<>'"]/g,char=>({
    '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
  })[char]);

  function styles(){
    if(document.getElementById('nk-horko-feed-style'))return;
    const style=document.createElement('style');
    style.id='nk-horko-feed-style';
    style.textContent=`
      .nk-horko-feed{margin:38px 0 48px;padding:24px;border:1px solid #e5d7bd;border-radius:20px;background:linear-gradient(135deg,#fffaf0,#fff 58%,#eef7fb);box-shadow:0 12px 34px rgba(18,35,45,.08)}
      .nk-horko-feed-head{display:flex;justify-content:space-between;gap:16px;align-items:end;margin-bottom:16px}
      .nk-horko-feed-head small{display:block;color:#a9232b;font-size:11px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}
      .nk-horko-feed-head strong{display:block;margin-top:4px;font:800 28px/1.15 Georgia,serif;color:#14232d}
      .nk-horko-feed-head span{color:#66747c;font-size:12px}
      .nk-horko-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
      .nk-horko-card{display:flex;flex-direction:column;min-width:0;background:#fff;border:1px solid #dde4e7;border-radius:16px;overflow:hidden;color:#14232d!important;text-decoration:none!important;box-shadow:0 8px 24px rgba(18,35,45,.07);transition:transform .2s,box-shadow .2s}
      .nk-horko-card:hover{transform:translateY(-3px);box-shadow:0 14px 32px rgba(18,35,45,.12)}
      .nk-horko-image{display:flex;align-items:center;justify-content:center;height:130px;background:#fff;border-bottom:1px solid #e4e8ea}
      .nk-horko-image img{display:block;width:100%;height:100%;object-fit:contain;padding:10px}
      .nk-horko-copy{display:flex;flex-direction:column;flex:1;padding:17px}
      .nk-horko-copy small{color:#a9232b;font-weight:850;text-transform:uppercase;letter-spacing:.05em}
      .nk-horko-copy strong{font:800 22px/1.17 Georgia,serif;margin:7px 0}
      .nk-horko-copy span{color:#53616a;line-height:1.45;flex:1}
      .nk-horko-copy b{color:#a9232b;margin-top:13px}
      @media(max-width:850px){.nk-horko-grid{grid-template-columns:1fr}.nk-horko-image{height:115px}.nk-horko-feed-head{align-items:start;flex-direction:column}}
    `;
    document.head.appendChild(style);
  }

  function card(item){
    return `<a class="nk-horko-card" href="${esc(item.url)}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span class="nk-horko-image"><img src="${esc(item.image)}" alt="${esc(item.title)}" loading="lazy" decoding="async"></span><span class="nk-horko-copy"><small>${esc(item.tag)}</small><strong>${esc(item.title)}</strong><span>${esc(item.text)}</span><b>Prohlédnout nabídku →</b></span></a>`;
  }

  function block(){
    const section=document.createElement('section');
    section.className='nk-horko-feed';
    section.dataset.heatAffiliateFeed='1';
    section.innerHTML=`<div class="nk-horko-feed-head"><div><small>REKLAMA · SEZÓNNÍ VÝBĚR</small><strong>Jak zvládnout horké dny doma</strong></div><span>Partnerské nabídky</span></div><div class="nk-horko-grid">${ITEMS.map(card).join('')}</div>`;
    return section;
  }

  function install(){
    if(document.querySelector('[data-heat-affiliate-feed]'))return;
    styles();

    const article=document.querySelector('main.article-shell article.article');
    if(article){
      const anchor=article.querySelector('.hero-visual')||article.querySelector('.leadtext')||article.querySelector('h1');
      if(anchor)anchor.after(block());
      return;
    }

    const promo=document.querySelector('main [data-promos], main .promo-wrap');
    if(promo){
      promo.before(block());
      return;
    }

    const main=document.querySelector('main');
    if(main)main.prepend(block());
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(install,350),{once:true});
  else setTimeout(install,350);
})();
