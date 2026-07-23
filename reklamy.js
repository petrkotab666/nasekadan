const promoItems=[
  {id:'pojistime',title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',tag:'Pojištění',contexts:['finance','home','travel','sidebar','general']},
  {id:'csob',title:'ČSOB Pojišťovna',text:'Pojištění auta, majetku, odpovědnosti, cestování i podnikatelských rizik.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=f5e0f8fb',banner:'https://doc.ehub.cz/b/174174d6/041e34d5.jpg',tag:'Pojištění',contexts:['finance','home','travel','general']},
  {id:'mutumutu',title:'Mutumutu.cz',text:'Životní pojištění a ochrana příjmu pro každodenní život.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=74eab778',banner:'https://doc.ehub.cz/b/706fc994/00043bad.png',tag:'Život a příjem',contexts:['finance','health','general']},
  {id:'petexpert',title:'PetExpert.cz',text:'Pojištění psů a koček pro nečekané veterinární výdaje.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=ce2e382f',banner:'https://doc.ehub.cz/b/a540cd53/0dce0d8e.png',tag:'Mazlíčci',contexts:['pets','family','general']},
  {id:'eon',title:'E.ON.cz',text:'Elektřina, plyn a energetická řešení pro domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=87497054',banner:'https://doc.ehub.cz/b/40b76033/0d98713f.png',tag:'Energie',contexts:['home','energy','general']},
  {id:'vodafone',title:'Vodafone.cz',text:'Mobilní tarify, internet a televize pro domácnosti i jednotlivce.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=aface625',banner:'https://doc.ehub.cz/b/6965053d/0168d188.jpg',tag:'Internet a mobil',contexts:['internet','home','general']},
  {id:'poda',title:'PODA.cz',text:'Internet a televizní služby pro domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=a86d04cf',banner:'https://doc.ehub.cz/b/6b66a101/30907ccc.jpg',tag:'Internet a TV',contexts:['internet','home','general']},
  {id:'telly',title:'Telly.cz',text:'Internetová televize a sportovní i filmové programy.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b1a888ed',banner:'https://doc.ehub.cz/b/77a1720e/11b66e36.jpg',tag:'Televize',contexts:['internet','sport','general']},
  {id:'nejpripojeni',title:'NejPřipojení.cz',text:'Porovnání možností internetu a IPTV podle dostupnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=7dc84251',banner:'https://doc.ehub.cz/b/a7ced961/16394373.png',tag:'Internet',contexts:['internet','home','general']},
  {id:'uvtnet',title:'ÚVTnet.cz',text:'Internetové připojení a související služby.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=51dbb2b9',banner:'https://doc.ehub.cz/b/f402ef36/135fd2cd.png',tag:'Internet',contexts:['internet','home','general']},
  {id:'klik',title:'Klik.cz',text:'Srovnání pojištění auta, majetku a cestování.',url:'https://www.tkqlhce.com/click-101819174-15024026',banner:'https://www.awltovhc.com/image-101819174-15021022',tag:'Srovnávač',contexts:['finance','travel','home','general']},
  {id:'kalkulator',title:'Kalkulator.cz',text:'Srovnání pojištění, energií a dalších výdajů domácnosti.',url:'https://www.tkqlhce.com/click-101819174-15616422',banner:'https://www.ftjcfx.com/image-101819174-15616436',tag:'Srovnávač',contexts:['finance','energy','home','general']},
  {id:'rixo',title:'RIXO.cz',text:'Online srovnání pojištění vozidel, majetku, cestování i dalších rizik.',url:'https://www.rixo.cz/pojisteni-vozidel/?a_box=9n97unga&a_cam=1',tag:'Pojištění',contexts:['finance','travel','home','general']},
  {id:'vyklidime',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',tag:'Místní služba',contexts:['home','sidebar','local','general']},
  {id:'uklizecka',title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',tag:'Místní služba',contexts:['home','sidebar','local','general']},
  {id:'haffit',title:'Haffit',text:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',url:'https://www.haffit.cz/?a_box=cbhtyjjm&a_cam=1',tag:'Pro chovatele',contexts:['pets','family','general']},
  {id:'zonky',title:'Zonky půjčka',text:'Online půjčka od Zonky s přehledným vyřízením a možností předčasného splacení.',url:'https://www.zonky.cz/pujcka-od-zonky/?a_box=s8m27mmy',tag:'Finance',contexts:['finance','home','general']}
];

const usedPromoIds=new Set();

function hashSeed(value){
  return [...String(value)].reduce((sum,char)=>((sum*31)+char.charCodeAt(0))>>>0,0);
}

function pickPromos(context,count,offset){
  const exact=promoItems.filter(item=>item.contexts.includes(context));
  const fallback=promoItems.filter(item=>!exact.includes(item));
  const pool=[...exact,...fallback];
  const day=new Date().toISOString().slice(0,10);
  const shift=(hashSeed(location.pathname+day)+offset)%pool.length;
  const rotated=[...pool.slice(shift),...pool.slice(0,shift)];
  const fresh=rotated.filter(item=>!usedPromoIds.has(item.id));
  const ordered=[...fresh,...rotated.filter(item=>!fresh.includes(item))];
  const selected=[];
  for(const item of ordered){
    if(selected.some(entry=>entry.id===item.id))continue;
    selected.push(item);
    if(selected.length===count)break;
  }
  selected.forEach(item=>usedPromoIds.add(item.id));
  return selected;
}

function inferPromoContext(text){
  const value=String(text||'').toLocaleLowerCase('cs');
  if(/nemocnic|zdrav|porod|péč|audit|lékař|pacient/.test(value))return 'health';
  if(/peněz|financ|dotac|náklad|výnos|hospodař|milion/.test(value))return 'finance';
  if(/budov|energie|opravy|domác|investic/.test(value))return 'home';
  if(/kadaň|ods|volb|kandid|politik|měst|zastupitel/.test(value))return 'local';
  return 'general';
}

function isPlacementCandidate(node){
  if(!node||node.matches('[data-promos],.source-list,.tag,h1,.leadtext,.hero-visual,.toc'))return false;
  return node.matches('p,table,ul,ol,blockquote,.numbers,.callout,.factcheck,.scenario-grid');
}

function nearbyText(node){
  const parts=[node.textContent||''];
  let cursor=node.nextElementSibling;
  for(let i=0;i<3&&cursor;i++,cursor=cursor.nextElementSibling){
    if(cursor.matches('.source-list'))break;
    parts.push(cursor.textContent||'');
  }
  return parts.join(' ');
}

function redistributeArticlePromos(){
  const article=document.querySelector('article.article');
  if(!article)return;

  article.querySelectorAll(':scope > [data-promos]').forEach(node=>node.remove());

  const children=[...article.children];
  const firstHeading=article.querySelector(':scope > h2');
  const sourceList=article.querySelector(':scope > .source-list');
  if(!firstHeading||!sourceList)return;

  const firstIndex=children.indexOf(firstHeading);
  const sourceIndex=children.indexOf(sourceList);
  const candidates=children.slice(firstIndex+1,sourceIndex).filter(isPlacementCandidate);
  if(candidates.length<4)return;

  const articleTop=article.getBoundingClientRect().top;
  const startY=firstHeading.getBoundingClientRect().bottom-articleTop;
  const endY=sourceList.getBoundingClientRect().top-articleTop;
  const contentHeight=Math.max(0,endY-startY);
  const desired=contentHeight>=7200?6:contentHeight>=5600?5:contentHeight>=4000?4:3;
  const edgePadding=Math.min(520,Math.max(280,contentHeight*0.07));
  const usableStart=startY+edgePadding;
  const usableEnd=endY-edgePadding;
  const usableHeight=Math.max(1,usableEnd-usableStart);
  const minGap=Math.max(620,usableHeight/(desired+0.7)*0.58);

  const points=candidates.map((node,index)=>({
    node,
    index,
    y:node.getBoundingClientRect().bottom-articleTop
  })).filter(point=>point.y>=usableStart&&point.y<=usableEnd);

  const selected=[];
  let previousY=-Infinity;

  for(let position=0;position<desired;position++){
    const target=usableStart+(usableHeight*(position+0.5)/desired);
    const remaining=desired-position-1;
    const eligible=points.filter(point=>{
      if(selected.some(entry=>entry.index===point.index))return false;
      if(point.y-previousY<minGap)return false;
      const roomAfter=usableEnd-point.y;
      return remaining===0||roomAfter>=remaining*minGap*0.78;
    });

    const pool=eligible.length?eligible:points.filter(point=>
      !selected.some(entry=>entry.index===point.index)&&
      point.y-previousY>=minGap*0.72
    );
    if(!pool.length)break;

    pool.sort((a,b)=>Math.abs(a.y-target)-Math.abs(b.y-target));
    const chosen=pool[0];
    selected.push(chosen);
    previousY=chosen.y;
  }

  selected.forEach((entry,index)=>{
    const block=document.createElement('section');
    block.className='article-ad article-ad-auto';
    block.dataset.promos='';
    block.dataset.context=inferPromoContext(nearbyText(entry.node));
    block.dataset.layout=index%2===0?'banner':'feed';
    block.dataset.count=block.dataset.layout==='banner'?'1':'3';
    entry.node.after(block);
  });
}

function ensurePromoStyles(){
  if(document.getElementById('promo-dynamic-styles'))return;
  const style=document.createElement('style');
  style.id='promo-dynamic-styles';
  style.textContent=`
    .promo-label{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
    .promo-label span{font-size:10px;letter-spacing:0;text-transform:none;color:#8a949a}
    .promo-grid-banner{grid-template-columns:minmax(0,1fr)!important}
    .promo-card-wide{display:grid!important;grid-template-columns:minmax(210px,34%) minmax(0,1fr);padding:0!important;min-height:154px!important}
    .promo-card-wide .promo-banner{height:100%!important;min-height:154px;margin:0!important;border:0;border-right:1px solid var(--line)}
    .promo-card-wide .promo-banner img{width:100%;height:100%;max-width:none!important;max-height:none!important;object-fit:contain;padding:10px;background:#fff}
    .promo-banner-fallback{background:linear-gradient(135deg,var(--red2),var(--red))!important;color:#fff;font:800 24px/1.2 Georgia,serif;text-align:center;padding:24px}
    .promo-wide-copy{display:flex!important;flex-direction:column;padding:22px 25px;color:inherit!important;min-width:0}
    .promo-wide-copy small{color:var(--red);font-weight:850;text-transform:uppercase;letter-spacing:.06em}
    .promo-wide-copy strong{font:700 28px/1.15 Georgia,serif;margin:6px 0;overflow-wrap:anywhere}
    .promo-wide-copy .promo-description{color:#53616a;flex:1;overflow-wrap:anywhere}
    .promo-wide-copy b{color:var(--red);margin-top:12px}
    .article-ad-auto{margin:52px 0}
    @media(max-width:700px){
      .promo-card-wide{grid-template-columns:1fr}
      .promo-card-wide .promo-banner{height:112px!important;min-height:112px;border-right:0;border-bottom:1px solid var(--line)}
      .promo-wide-copy strong{font-size:23px}
      .article-ad-auto{margin:44px 0}
    }
  `;
  document.head.appendChild(style);
}

function renderFeedCard(item){
  return `<a class="promo-card" href="${item.url}" target="_blank" rel="nofollow sponsored noopener noreferrer">${item.banner?`<span class="promo-banner"><img src="${item.banner}" alt="${item.title}" loading="lazy" decoding="async"></span>`:''}<small>${item.tag}</small><strong>${item.title}</strong><span>${item.text}</span><b>Zjistit více →</b></a>`;
}

function renderBannerCard(item){
  const visual=item.banner
    ?`<span class="promo-banner"><img src="${item.banner}" alt="${item.title}" loading="lazy" decoding="async"></span>`
    :`<span class="promo-banner promo-banner-fallback">${item.title}</span>`;
  return `<a class="promo-card promo-card-wide" href="${item.url}" target="_blank" rel="nofollow sponsored noopener noreferrer">${visual}<span class="promo-wide-copy"><small>${item.tag}</small><strong>${item.title}</strong><span class="promo-description">${item.text}</span><b>Zjistit více →</b></span></a>`;
}

function renderPromos(){
  document.querySelectorAll('[data-promos]').forEach((box,index)=>{
    const context=box.dataset.context||'general';
    const layout=box.dataset.layout||(context==='sidebar'?'compact':'feed');
    const isBanner=layout==='banner';
    const count=box.dataset.count?Number(box.dataset.count):(context==='sidebar'||isBanner?1:3);
    const items=pickPromos(context,count,index*5);
    const compact=context==='sidebar'?' promo-grid-compact':'';
    const bannerClass=isBanner?' promo-grid-banner':'';
    const cards=items.map(item=>isBanner?renderBannerCard(item):renderFeedCard(item)).join('');
    box.innerHTML=`<div class="promo-label">REKLAMA <span>Některé odkazy jsou affiliate a mohou podpořit provoz webu.</span></div><div class="promo-grid${compact}${bannerClass}">${cards}</div>`;
  });
}

document.addEventListener('DOMContentLoaded',()=>{
  ensurePromoStyles();
  redistributeArticlePromos();
  renderPromos();
});
