(()=>{
  'use strict';

  const PARTNERS=[
    {id:'invia',name:'Invia.cz',label:'Dovolená a zájezdy',text:'Last minute i běžné zájezdy k moři, do hor a za poznáním.',url:'https://www.invia.cz/dovolena/last-minute/?b_https=1&aid=9256106'},
    {id:'atis',name:'Atis.cz',label:'Dovolená a pobyty',text:'Pobytové, poznávací a wellness zájezdy po Česku, Slovensku i Evropě.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=49886ce2'},
    {id:'excursia',name:'Excursia.cz',label:'Výlety a zážitky',text:'Poznávací zájezdy, výlety, exkurze a další zážitky v Česku i zahraničí.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=76c9b39c',image:'https://doc.ehub.cz/b/2e6a0944/368140a3.jpg'},
    {id:'csob',name:'ČSOB Pojišťovna',label:'Pojištění',text:'Pojištění auta, majetku, odpovědnosti, cestování i podnikatelských rizik.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=f5e0f8fb',image:'https://doc.ehub.cz/b/174174d6/041e34d5.jpg'},
    {id:'mutumutu',name:'Mutumutu.cz',label:'Život a příjem',text:'Životní pojištění a ochrana příjmu sjednávané online.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=74eab778',image:'https://doc.ehub.cz/b/706fc994/00043bad.png'},
    {id:'petexpert',name:'PetExpert.cz',label:'Mazlíčci',text:'Pojištění psů a koček pro nečekané veterinární výdaje.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=ce2e382f',image:'https://doc.ehub.cz/b/a540cd53/0dce0d8e.png'},
    {id:'eon',name:'E.ON.cz',label:'Energie',text:'Elektřina, plyn a energetická řešení pro domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=87497054',image:'https://doc.ehub.cz/b/40b76033/0d98713f.png'},
    {id:'poda',name:'PODA.cz',label:'Internet a TV',text:'Internetové připojení a televizní služby podle dostupnosti na adrese.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=a86d04cf',image:'https://doc.ehub.cz/b/6b66a101/30907ccc.jpg'},
    {id:'telly',name:'Telly.cz',label:'Televize',text:'Internetová televize se sportovními, filmovými a dalšími programy.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b1a888ed',image:'https://doc.ehub.cz/b/77a1720e/11b66e36.jpg'},
    {id:'nejpripojeni',name:'NejPřipojení.cz',label:'Internet',text:'Porovnání možností internetu a IPTV podle konkrétní adresy.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=7dc84251',image:'https://doc.ehub.cz/b/a7ced961/16394373.png'},
    {id:'klik',name:'Klik.cz',label:'Srovnávač',text:'Online srovnání pojištění auta, majetku a cestování.',url:'https://www.tkqlhce.com/click-101819174-15024026',image:'https://www.awltovhc.com/image-101819174-15021022'},
    {id:'kalkulator',name:'Kalkulator.cz',label:'Srovnávač',text:'Srovnání pojištění, energií a dalších pravidelných výdajů domácnosti.',url:'https://www.tkqlhce.com/click-101819174-15616422',image:'https://www.ftjcfx.com/image-101819174-15616436'},
    {id:'proalergiky',name:'Proalergiky.cz',label:'Zdraví',text:'Specializované produkty pro alergiky a zdravější prostředí v domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=abc25217',image:'https://doc.ehub.cz/b/cbee71d3/017d5633.jpg'},
    {id:'nanospace',name:'Nanospace.cz',label:'Zdravá domácnost',text:'České produkty pro zdravější domácnost, alergiky a kvalitnější spánek.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=32dfe8fd',image:'https://doc.ehub.cz/b/21118d16/022986bf.jpg'},
    {id:'biano',name:'Biano.cz',label:'Bydlení',text:'Nábytek, dekorace a vybavení domácnosti z nabídky mnoha internetových obchodů.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=da726a9e',image:'https://doc.ehub.cz/b/80610cd6/82a1c42b.png'},
    {id:'dobre-knihy',name:'Dobré-knihy.cz',label:'Knihy',text:'Knihy, audioknihy a další čtení pro volný čas i celou rodinu.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=1ec2df65',image:'https://doc.ehub.cz/b/57ad8ec1/30a97424.jpg'},
    {id:'pojistime',name:'Pojistime.to',label:'Pojištění',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to'},
    {id:'vyklidime',name:'VYKLIDIME.TO',label:'Místní služba',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to'},
    {id:'uklizecka',name:'Vaše uklízečka',label:'Místní služba',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz'}
  ];

  const esc=value=>String(value??'').replace(/[&<>'"]/g,char=>({
    '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
  })[char]);

  const hash=value=>[...String(value)].reduce((sum,char)=>((sum*33)+char.charCodeAt(0))>>>0,5381);

  function orderedPartners(salt){
    const day=new Date().toISOString().slice(0,10);
    const start=hash(`${location.pathname}|${day}|${salt}`)%PARTNERS.length;
    return [...PARTNERS.slice(start),...PARTNERS.slice(0,start)];
  }

  function visual(item,side=false){
    const fallback=`<span class="nk-doplnek-vizual nk-doplnek-vizual-text"><strong>${esc(item.name)}</strong></span>`;
    if(!item.image)return fallback;
    return `<span class="nk-doplnek-vizual${side?' nk-doplnek-vizual-side':''}"><img src="${esc(item.image)}" alt="${esc(item.name)}" loading="lazy" decoding="async" onerror="this.parentElement.className='nk-doplnek-vizual nk-doplnek-vizual-text';this.parentElement.innerHTML='<strong>${esc(item.name)}</strong>'"></span>`;
  }

  function wideCard(item){
    return `<a class="nk-doplnek-karta nk-doplnek-siroka" href="${esc(item.url)}" target="_blank" rel="nofollow sponsored noopener noreferrer">${visual(item)}<span class="nk-doplnek-text"><small>${esc(item.label)}</small><strong>${esc(item.name)}</strong><span>${esc(item.text)}</span><b>Zjistit více →</b></span></a>`;
  }

  function sideCard(item){
    return `<a class="nk-doplnek-karta nk-doplnek-side" href="${esc(item.url)}" target="_blank" rel="nofollow sponsored noopener noreferrer"><span class="nk-doplnek-znacka">REKLAMA</span>${visual(item,true)}<span class="nk-doplnek-text"><small>${esc(item.label)}</small><strong>${esc(item.name)}</strong><span>${esc(item.text)}</span><b>Zjistit více →</b></span></a>`;
  }

  function addStyles(){
    if(document.getElementById('nk-doplnky-style'))return;
    const style=document.createElement('style');
    style.id='nk-doplnky-style';
    style.textContent=`
      .nk-doplnek-blok{display:block!important;margin:52px 0!important;visibility:visible!important;opacity:1!important}
      .nk-doplnek-popisek{display:block!important;margin-bottom:9px;color:#777;font-size:11px;letter-spacing:.12em;text-transform:uppercase}
      .nk-doplnek-karta{display:flex!important;background:#fff;border:1px solid var(--line,#dde3e6);border-radius:16px;box-shadow:0 10px 28px rgba(18,35,45,.08);color:var(--ink,#13232d);overflow:hidden;text-decoration:none!important;visibility:visible!important;opacity:1!important}
      .nk-doplnek-siroka{display:grid!important;grid-template-columns:minmax(230px,35%) minmax(0,1fr);min-height:175px}
      .nk-doplnek-vizual{display:flex!important;align-items:center;justify-content:center;min-height:175px;background:#fff;border-right:1px solid var(--line,#dde3e6);overflow:hidden}
      .nk-doplnek-vizual img{display:block!important;width:100%;height:100%;max-height:175px;object-fit:contain;padding:10px;visibility:visible!important;opacity:1!important}
      .nk-doplnek-vizual-text{background:linear-gradient(135deg,#7f1720,#a9232b);color:#fff;padding:24px;text-align:center}
      .nk-doplnek-vizual-text strong{font:800 26px/1.15 Georgia,serif}
      .nk-doplnek-text{display:flex!important;flex-direction:column;min-width:0;padding:22px 25px}
      .nk-doplnek-text small{color:var(--red,#a9232b);font-weight:850;letter-spacing:.06em;text-transform:uppercase}
      .nk-doplnek-text strong{margin:6px 0;font:700 28px/1.15 Georgia,serif;overflow-wrap:anywhere}
      .nk-doplnek-text>span{color:#53616a;line-height:1.5;flex:1}
      .nk-doplnek-text b{margin-top:12px;color:var(--red,#a9232b)}
      .nk-doplnek-side-list{display:grid!important;gap:22px;margin-top:18px;visibility:visible!important;opacity:1!important}
      .nk-doplnek-side{display:flex!important;flex-direction:column;min-height:390px}
      .nk-doplnek-side .nk-doplnek-znacka{padding:7px 9px 6px;background:#f5f7f8;border-bottom:1px solid #e1e6e8;color:#747f85;font-size:9px;font-weight:900;letter-spacing:.12em;text-align:center}
      .nk-doplnek-side .nk-doplnek-vizual{width:100%;height:145px;min-height:145px;border-right:0;border-bottom:1px solid var(--line,#dde3e6)}
      .nk-doplnek-side .nk-doplnek-vizual img{max-height:145px}
      .nk-doplnek-side .nk-doplnek-vizual-text strong{font-size:23px}
      .nk-doplnek-side .nk-doplnek-text{padding:17px 18px;min-height:230px}
      .nk-doplnek-side .nk-doplnek-text strong{font-size:23px}
      .nk-doplnek-side .nk-doplnek-text>span{font-size:14px}
      main.article-shell>aside.sticky.nk-doplnek-pravy,main.article-shell>aside>.sticky.nk-doplnek-pravy{position:static!important;top:auto!important}
      @media(max-width:980px){.nk-doplnek-side-list{display:none!important}}
      @media(max-width:700px){.nk-doplnek-siroka{grid-template-columns:1fr}.nk-doplnek-vizual{height:130px;min-height:130px;border-right:0;border-bottom:1px solid var(--line,#dde3e6)}.nk-doplnek-vizual img{max-height:130px}.nk-doplnek-text strong{font-size:23px}.nk-doplnek-blok{margin:44px 0!important}}
    `;
    document.head.appendChild(style);
  }

  function cleanIncompleteOldLayer(){
    document.querySelectorAll('.article-ad-auto,.article-ad-rail').forEach(node=>node.remove());
    document.querySelectorAll('[data-promos]').forEach(node=>{node.innerHTML='';node.style.display='none';});
    document.querySelectorAll('.article-aside-tower').forEach(node=>node.remove());
  }

  function insertInArticle(article){
    if(article.querySelector('.nk-doplnek-blok'))return;
    const children=[...article.children];
    const source=article.querySelector(':scope > .source-list');
    const firstHeading=article.querySelector(':scope > h2');
    if(!firstHeading)return;
    const start=children.indexOf(firstHeading)+1;
    const end=source?children.indexOf(source):children.length;
    const candidates=children.slice(start,end).filter(node=>node.matches('p,table,ul,ol,blockquote,.numbers,.callout,.factcheck,.scenario-grid,section'));
    if(candidates.length<2)return;
    const count=candidates.length>=14?6:candidates.length>=10?5:candidates.length>=7?4:3;
    const partners=orderedPartners('content').slice(0,count);
    const usedIndexes=new Set();
    for(let i=count-1;i>=0;i--){
      let index=Math.round(((i+1)*candidates.length)/(count+1))-1;
      index=Math.max(0,Math.min(candidates.length-1,index));
      while(usedIndexes.has(index)&&index<candidates.length-1)index++;
      if(usedIndexes.has(index))continue;
      usedIndexes.add(index);
      const block=document.createElement('section');
      block.className='nk-doplnek-blok';
      block.innerHTML=`<div class="nk-doplnek-popisek">REKLAMA</div>${wideCard(partners[i])}`;
      candidates[index].after(block);
    }
  }

  function findRightHost(shell){
    return shell.querySelector(':scope > aside.sticky')
      ||shell.querySelector(':scope > aside > .sticky')
      ||shell.querySelector(':scope > aside');
  }

  function fillRightColumn(shell){
    const host=findRightHost(shell);
    if(!host||host.querySelector('.nk-doplnek-side-list'))return;
    host.classList.add('nk-doplnek-pravy');
    const list=document.createElement('div');
    list.className='nk-doplnek-side-list';
    list.innerHTML=orderedPartners('right').slice(0,7).map(sideCard).join('');
    host.appendChild(list);
  }

  function renderStandalone(){
    if(document.documentElement.dataset.nkDoplnky==='1')return;
    const shell=document.querySelector('main.article-shell');
    const article=shell?.querySelector(':scope > article.article');
    if(!shell||!article)return;
    document.documentElement.dataset.nkDoplnky='1';
    addStyles();
    cleanIncompleteOldLayer();
    insertInArticle(article);
    fillRightColumn(shell);
  }

  function attempt(){
    if(document.documentElement.dataset.nkDoplnky==='1')return;
    const oldCards=document.querySelectorAll('.promo-card,.article-rail-card').length;
    const oldRight=document.querySelectorAll('main.article-shell>aside .promo-card,main.article-shell>aside .article-rail-card').length;
    if(oldCards>=4&&oldRight>=2)return;
    renderStandalone();
  }

  function start(){
    [50,450,1200,2500].forEach(delay=>setTimeout(attempt,delay));
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
