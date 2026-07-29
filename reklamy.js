const promoItems=[
  {id:'pojistime',title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',tag:'Pojištění',contexts:['finance','auto','home','travel','sidebar','general']},
  {id:'csob',title:'ČSOB Pojišťovna',text:'Pojištění auta, majetku, odpovědnosti, cestování i podnikatelských rizik.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=f5e0f8fb',banner:'https://doc.ehub.cz/b/174174d6/041e34d5.jpg',tag:'Pojištění',contexts:['finance','auto','home','travel','general']},
  {id:'mutumutu',title:'Mutumutu.cz',text:'Životní pojištění a ochrana příjmu pro každodenní život.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=74eab778',banner:'https://doc.ehub.cz/b/706fc994/00043bad.png',tag:'Život a příjem',contexts:['finance','health','general']},
  {id:'petexpert',title:'PetExpert.cz',text:'Pojištění psů a koček pro nečekané veterinární výdaje.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=ce2e382f',banner:'https://doc.ehub.cz/b/a540cd53/0dce0d8e.png',tag:'Mazlíčci',contexts:['pets','family','general']},
  {id:'eon',title:'E.ON.cz',text:'Elektřina, plyn a energetická řešení pro domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=87497054',banner:'https://doc.ehub.cz/b/40b76033/0d98713f.png',tag:'Energie',contexts:['home','energy','general']},
  {id:'poda',title:'PODA.cz',text:'Internet a televizní služby pro domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=a86d04cf',banner:'https://doc.ehub.cz/b/6b66a101/30907ccc.jpg',tag:'Internet a TV',contexts:['internet','home','general']},
  {id:'telly',title:'Telly.cz',text:'Internetová televize a sportovní i filmové programy.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b1a888ed',banner:'https://doc.ehub.cz/b/77a1720e/11b66e36.jpg',tag:'Televize',contexts:['internet','sport','general']},
  {id:'nejpripojeni',title:'NejPřipojení.cz',text:'Porovnání možností internetu a IPTV podle dostupnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=7dc84251',banner:'https://doc.ehub.cz/b/a7ced961/16394373.png',tag:'Internet',contexts:['internet','home','general']},
  {id:'uvtnet',title:'ÚVTnet.cz',text:'Internetové připojení a související služby.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=51dbb2b9',banner:'https://doc.ehub.cz/b/f402ef36/135fd2cd.png',tag:'Internet',contexts:['internet','home','general']},
  {id:'klik',title:'Klik.cz',text:'Srovnání pojištění auta, majetku a cestování.',url:'https://www.tkqlhce.com/click-101819174-15024026',banner:'https://www.awltovhc.com/image-101819174-15021022',tag:'Srovnávač',contexts:['finance','auto','travel','home','general']},
  {id:'kalkulator',title:'Kalkulator.cz',text:'Srovnání pojištění, energií a dalších výdajů domácnosti.',url:'https://www.tkqlhce.com/click-101819174-15616422',banner:'https://www.ftjcfx.com/image-101819174-15616436',tag:'Srovnávač',contexts:['finance','auto','energy','home','general']},
  {id:'rixo',title:'RIXO.cz',text:'Online srovnání pojištění vozidel, majetku, cestování i dalších rizik.',url:'https://www.rixo.cz/pojisteni-vozidel/?a_box=9n97unga&a_cam=1',tag:'Pojištění',contexts:['finance','auto','travel','home','general']},
  {id:'vyklidime',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',tag:'Místní služba',contexts:['home','sidebar','local','general']},
  {id:'uklizecka',title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',tag:'Místní služba',contexts:['home','sidebar','local','general']},
  {id:'uklizecka-cisteni',title:'Čištění koberců, sedaček a čalounění',text:'Hloubkové čištění koberců, sedaček a čalounění na Kadaňsku. Objednávky: 603 206 308.',url:'https://www.vaseuklizecka.cz/sluzby/cisteni-kobercu-a-calouneni/',banner:'/assets/reklamy/vaseuklizecka-cisteni-wide-sharp-v3.svg',wideBanner:'/assets/reklamy/vaseuklizecka-cisteni-wide-sharp-v3.svg',tag:'Místní služba',contexts:['home','sidebar','local','general'],weight:4},
  {id:'haffit',title:'Haffit',text:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',url:'https://www.haffit.cz/?a_box=cbhtyjjm&a_cam=1',tag:'Pro chovatele',contexts:['pets','family','general']},
  {id:'zonky',title:'Zonky půjčka',text:'Online půjčka od Zonky s přehledným vyřízením a možností předčasného splacení.',url:'https://www.zonky.cz/pujcka-od-zonky/?a_box=s8m27mmy',tag:'Finance',contexts:['finance','home','general']}
];

const towerCreativeItems=[
  {
    id:'dobre-knihy-tower',
    title:'Dobré-knihy.cz',
    url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=5e05c229',
    image:'https://doc.ehub.cz/b/57ad8ec1/5e05c229.jpg',
    width:300,
    height:600,
    contexts:['general','family','local','health']
  },
  {
    id:'network-tower',
    title:'Partnerská nabídka',
    url:'https://www.tkqlhce.com/click-101819174-15753082',
    image:'https://www.lduhtrp.net/image-101819174-15753082',
    width:300,
    height:600,
    contexts:['general','finance','auto','home','local']
  }
  ,{
    id:'uklizecka-cisteni-tower',
    title:'Čištění koberců, sedaček a čalounění',
    url:'https://www.vaseuklizecka.cz/sluzby/cisteni-kobercu-a-calouneni/',
    image:'/assets/reklamy/vaseuklizecka-cisteni-yellow-tower-160x237.webp',
    width:300,
    height:600,
    contexts:['general','home','local','health','sidebar'],
    weight:4
  }
];

const usedPromoIds=new Set();

const partnerCopy={
  'dobre-knihy':'Knihy, audioknihy a další čtení pro volný čas i celou rodinu.',
  biano:'Inspirace a nabídky pro bydlení, nábytek a vybavení domácnosti.',
  nanospace:'České produkty pro zdravější domácnost, alergiky a kvalitnější spánek.',
  concept:'Domácí spotřebiče a praktické vybavení pro každodenní provoz domácnosti.',
  proalergiky:'Specializované produkty pro alergiky a zdravější prostředí v domácnosti.',
  poda:'Internetové připojení a televizní služby pro domácnosti.',
  telly:'Internetová televize se sportovními, filmovými a dalšími programy.',
  nejpripojeni:'Porovnání dostupných možností internetu a IPTV.',
  csob:'Pojištění auta, majetku, odpovědnosti, cestování i dalších rizik.',
  mutumutu:'Životní pojištění a ochrana příjmu pro každodenní život.',
  petexpert:'Pojištění psů a koček pro nečekané veterinární výdaje.',
  eon:'Energie a energetická řešení pro domácnosti.',
  klik:'Srovnání pojištění auta, majetku a cestování.',
  kalkulator:'Srovnání pojištění, energií a dalších výdajů domácnosti.',
  haffit:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',
  zonky:'Online půjčka s přehledným vyřízením a možností předčasného splacení.'
};

function hashSeed(value){
  return [...String(value)].reduce((sum,char)=>((sum*31)+char.charCodeAt(0))>>>0,0);
}

function normalizeToken(value){
  return String(value||'')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g,'')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g,'-')
    .replace(/^-+|-+$/g,'');
}

function safeHttpUrl(value){
  try{
    const url=new URL(String(value||''),location.origin);
    return /^(https?:)$/.test(url.protocol)?url.href:'';
  }catch{
    return '';
  }
}

function escapeHtml(value){
  return String(value||'').replace(/[&<>'"]/g,char=>({
    '&':'&amp;',
    '<':'&lt;',
    '>':'&gt;',
    "'":'&#39;',
    '"':'&quot;'
  })[char]);
}

function contextsFromCategories(categories){
  const text=(categories||[]).map(normalizeToken).join(' ');
  const contexts=new Set(['general']);
  if(/auto|vozid|doprava|povinne-ruceni/.test(text))contexts.add('auto');
  if(/internet|televize|iptv|telekomunikace|mobil/.test(text))contexts.add('internet');
  if(/energie|elektrina|plyn/.test(text))contexts.add('energy');
  if(/majetek|domacnost|bydleni|nabytek|spotrebice/.test(text))contexts.add('home');
  if(/zdravi|zivot|alergie|ochrana-prijmu/.test(text))contexts.add('health');
  if(/finance|pujcka|pojisteni|odpovednost/.test(text))contexts.add('finance');
  if(/cestovani/.test(text))contexts.add('travel');
  if(/mazlicci|pes|kocka/.test(text))contexts.add('pets');
  if(/rodina|knihy|volny-cas/.test(text))contexts.add('family');
  return [...contexts];
}

function tagFromContexts(contexts,categories){
  if(contexts.includes('internet'))return 'Internet a TV';
  if(contexts.includes('auto'))return 'Auto a pojištění';
  if(contexts.includes('health'))return 'Zdraví';
  if(contexts.includes('energy'))return 'Energie';
  if(contexts.includes('home'))return 'Domácnost';
  if(contexts.includes('pets'))return 'Mazlíčci';
  if(contexts.includes('finance'))return 'Finance';
  const first=(categories||[])[0];
  return first?String(first).replace(/-/g,' '):'Partnerská nabídka';
}

function firstPartnerLink(row){
  const candidates=[
    row.baseClickUrl,
    row.trackingUrl,
    ...(Array.isArray(row.links)?row.links.flatMap(link=>[link.clickUrl,link.url,link.trackingUrl]):[])
  ];
  return candidates.map(safeHttpUrl).find(Boolean)||'';
}

function firstPartnerBanner(row){
  const bannerRows=Array.isArray(row.banners)?row.banners:[];
  const preferred=bannerRows.find(banner=>String(banner.format||'').toLowerCase()==='300x600')||bannerRows[0];
  return safeHttpUrl(row.sampleBanner||preferred?.imageUrl||preferred?.src||'');
}

function mergeSnapshotPartners(snapshot){
  const existing=new Set(promoItems.map(item=>normalizeToken(item.id||item.title)));
  for(const row of snapshot?.partners||[]){
    if(!row||typeof row!=='object')continue;
    const id=normalizeToken(row.id||row.name||row.defaultLinkId);
    if(!id||existing.has(id))continue;
    const url=firstPartnerLink(row);
    if(!url)continue;
    const categories=Array.isArray(row.categories)?row.categories:[];
    const contexts=contextsFromCategories(categories);
    promoItems.push({
      id,
      title:String(row.name||row.id||'Partnerská nabídka'),
      text:partnerCopy[id]||'Vybraná partnerská nabídka z centrální databáze propojených webů.',
      url,
      banner:firstPartnerBanner(row),
      tag:tagFromContexts(contexts,categories),
      contexts
    });
    existing.add(id);

    for(const banner of row.banners||[]){
      if(String(banner.format||'').toLowerCase()!=='300x600')continue;
      const image=safeHttpUrl(banner.imageUrl||banner.src);
      const click=safeHttpUrl(banner.clickUrl||url);
      const towerId=`${id}-${normalizeToken(banner.id||'tower')}`;
      if(!image||!click||towerCreativeItems.some(item=>item.id===towerId))continue;
      towerCreativeItems.push({
        id:towerId,
        title:String(row.name||'Partnerská nabídka'),
        url:click,
        image,
        width:300,
        height:600,
        contexts
      });
    }
  }
}

async function loadAffiliateSnapshot(){
  try{
    const url=new URL('/assets/affiliate-site-snapshot.json',location.origin);
    url.searchParams.set('v',new Date().toISOString().slice(0,13));
    const response=await fetch(url,{cache:'no-store',headers:{'Accept':'application/json'}});
    if(!response.ok)return;
    const snapshot=await response.json();
    mergeSnapshotPartners(snapshot);
  }catch(error){
    console.warn('Centrální affiliate snapshot se nepodařilo načíst.',error);
  }
}

function pickPromos(context,count,offset){
  const expand=item=>Array.from({length:Math.max(1,Number(item.weight)||1)},()=>item);
  const exact=promoItems.filter(item=>item.contexts.includes(context)).flatMap(expand);
  const exactIds=new Set(exact.map(item=>item.id));
  const fallback=promoItems.filter(item=>!exactIds.has(item.id)).flatMap(expand);
  const pool=[...exact,...fallback];
  if(!pool.length)return [];
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
  if(/nehod|doprav|řidič|silnic|vozidl|auto/.test(value))return 'auto';
  if(/internet|televiz|kabel|optik|připojen/.test(value))return 'internet';
  if(/nemocnic|zdrav|porod|péč|audit|lékař|pacient|zraněn/.test(value))return 'health';
  if(/požár|hasič|vyklíz|budov|energie|opravy|domác|investic/.test(value))return 'home';
  if(/peněz|financ|dotac|náklad|výnos|hospodař|milion/.test(value))return 'finance';
  if(/pes|kočk|zvíř|mazlíčk/.test(value))return 'pets';
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
    .featured-cleaning-ad{display:block;margin:28px auto 48px;max-width:1180px;padding:0 20px}
    article.article>.featured-cleaning-ad{margin:34px 0 46px;padding:0;max-width:none}
    .featured-cleaning-ad>.promo-label{margin-bottom:8px;color:#747f85;font-size:10px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}
    .featured-cleaning-ad>a{display:block;overflow:hidden;max-width:900px;margin:0 auto;border:1px solid #d8e0e4;border-radius:16px;background:#fff;box-shadow:0 12px 32px rgba(18,35,45,.12)}
    .featured-cleaning-ad img{display:block;width:100%;height:auto;object-fit:contain;background:#fff}


    .article-ad-rail{display:none;position:fixed;top:96px;width:176px;z-index:8;max-height:calc(100vh - 116px);overflow:hidden}
    .article-ad-rail-left{left:calc((100vw - 1180px)/2 - 194px)}
    .article-ad-rail-right{right:calc((100vw - 1180px)/2 - 194px)}
    .article-rail-card{display:flex;flex-direction:column;width:176px;max-height:calc(100vh - 116px);overflow:hidden;background:#fff;border:1px solid #d8e0e4;border-radius:16px;box-shadow:0 14px 38px rgba(18,35,45,.14);color:var(--ink);transition:transform .2s,box-shadow .2s}
    .article-rail-card:hover{transform:translateY(-3px);box-shadow:0 20px 48px rgba(18,35,45,.18)}
    .article-rail-label{display:block;padding:7px 9px 6px;color:#747f85;background:#f5f7f8;border-bottom:1px solid #e1e6e8;font-size:9px;font-weight:900;letter-spacing:.12em;text-align:center;text-transform:uppercase}
    .article-rail-tower-picture{display:flex;align-items:center;justify-content:center;background:#fff;min-height:352px}
    .article-rail-tower-picture img{display:block;width:176px;height:352px;object-fit:contain;border:0}
    .article-rail-visual{display:flex;align-items:center;justify-content:center;height:108px;min-height:108px;background:#fff;border-bottom:1px solid var(--line);overflow:hidden}
    .article-rail-visual img{display:block;width:100%;height:100%;object-fit:contain;padding:8px}
    .article-rail-copy{display:flex;flex-direction:column;min-height:240px;padding:15px}
    .article-rail-copy small{color:var(--red);font-size:10px;font-weight:900;letter-spacing:.06em;text-transform:uppercase}
    .article-rail-copy strong{font:800 22px/1.13 Georgia,serif;margin:7px 0 9px;overflow-wrap:anywhere}
    .article-rail-copy span{color:#53616a;font-size:13px;line-height:1.45;flex:1;overflow-wrap:anywhere}
    .article-rail-copy b{color:var(--red);font-size:13px;margin-top:13px}
    .article-rail-fallback{display:none;align-items:center;justify-content:center;min-height:270px;padding:18px;background:linear-gradient(145deg,var(--red2),var(--red));color:#fff;font:800 22px/1.2 Georgia,serif;text-align:center}
    .article-rail-card.is-image-error .article-rail-tower-picture,.article-rail-card.is-image-error .article-rail-visual{display:none}
    .article-rail-card.is-image-error .article-rail-fallback{display:flex}
    .article-aside-tower{display:none;margin-top:18px}
    .article-aside-tower .article-rail-card{width:100%;max-width:300px;max-height:none;margin:auto}
    .article-aside-tower .article-rail-tower-picture{min-height:auto}
    .article-aside-tower .article-rail-tower-picture img{width:100%;height:auto;aspect-ratio:1/2;object-fit:contain}

    @media(min-width:981px) and (max-width:1579px){
      .article-aside-tower{display:block}
    }
    @media(min-width:1580px) and (min-height:680px){
      .article-ad-rail{display:block}
    }
    @media(max-height:679px){
      .article-ad-rail{display:none!important}
    }
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
  const title=escapeHtml(item.title);
  const banner=safeHttpUrl(item.banner);
  const visual=banner?`<span class="promo-banner"><img src="${escapeHtml(banner)}" alt="${title}" loading="lazy" decoding="async"></span>`:'';
  return `<a class="promo-card" href="${escapeHtml(safeHttpUrl(item.url))}" target="_blank" rel="nofollow sponsored noopener noreferrer">${visual}<small>${escapeHtml(item.tag)}</small><strong>${title}</strong><span>${escapeHtml(item.text)}</span><b>Zjistit více →</b></a>`;
}

function renderBannerCard(item){
  const title=escapeHtml(item.title);
  const banner=safeHttpUrl(item.wideBanner||item.banner);
  const visual=banner
    ?`<span class="promo-banner"><img src="${escapeHtml(banner)}" alt="${title}" loading="lazy" decoding="async"></span>`
    :`<span class="promo-banner promo-banner-fallback">${title}</span>`;
  return `<a class="promo-card promo-card-wide" href="${escapeHtml(safeHttpUrl(item.url))}" target="_blank" rel="nofollow sponsored noopener noreferrer">${visual}<span class="promo-wide-copy"><small>${escapeHtml(item.tag)}</small><strong>${title}</strong><span class="promo-description">${escapeHtml(item.text)}</span><b>Zjistit více →</b></span></a>`;
}

function renderPromos(){
  document.querySelectorAll('[data-promos]').forEach((box,index)=>{
    const context=box.dataset.context||'general';
    const layout=box.dataset.layout||(context==='sidebar'?'compact':'feed');
    const isBanner=layout==='banner';
    const count=box.dataset.count?Number(box.dataset.count):(context==='sidebar'||isBanner?1:3);
    let items=pickPromos(context,count,index*5);
    const featured=promoItems.find(item=>item.id==='uklizecka-cisteni');
    if(featured&&(index===0||context==='sidebar')){
      items=[featured,...items.filter(item=>item.id!==featured.id)].slice(0,Math.max(1,count));
    }
    const compact=context==='sidebar'?' promo-grid-compact':'';
    const bannerClass=isBanner?' promo-grid-banner':'';
    const cards=items.map(item=>isBanner?renderBannerCard(item):renderFeedCard(item)).join('');
    box.innerHTML=`<div class="promo-label">REKLAMA</div><div class="promo-grid${compact}${bannerClass}">${cards}</div>`;
  });
}

function pickTowerCreative(context,offset=0){
  const expand=item=>Array.from({length:Math.max(1,Number(item.weight)||1)},()=>item);
  const exact=towerCreativeItems.filter(item=>item.contexts.includes(context)).flatMap(expand);
  const exactIds=new Set(exact.map(item=>item.id));
  const pool=[...exact,...towerCreativeItems.filter(item=>!exactIds.has(item.id)).flatMap(expand)];
  if(!pool.length)return null;
  const day=new Date().toISOString().slice(0,10);
  return pool[(hashSeed(`${location.pathname}|${day}|tower`)+offset)%pool.length];
}

function pickRailPromo(context,offset=0){
  const pool=[
    ...promoItems.filter(item=>item.contexts.includes(context)&&item.banner),
    ...promoItems.filter(item=>!item.contexts.includes(context)&&item.banner),
    ...promoItems.filter(item=>item.contexts.includes(context)&&!item.banner),
    ...promoItems.filter(item=>!item.contexts.includes(context)&&!item.banner)
  ].filter((item,index,array)=>array.findIndex(entry=>entry.id===item.id)===index);
  if(!pool.length)return null;
  const day=new Date().toISOString().slice(0,10);
  const start=(hashSeed(`${location.pathname}|${day}|rail`)+offset)%pool.length;
  for(let step=0;step<pool.length;step++){
    const item=pool[(start+step)%pool.length];
    if(!usedPromoIds.has(item.id))return item;
  }
  return pool[start];
}

function renderTowerRailCard(item){
  const title=escapeHtml(item.title);
  return `<a class="article-rail-card article-rail-card-tower" href="${escapeHtml(safeHttpUrl(item.url))}" target="_blank" rel="nofollow sponsored noopener noreferrer" aria-label="Reklama: ${title}"><span class="article-rail-label">Reklama</span><span class="article-rail-tower-picture"><img src="${escapeHtml(safeHttpUrl(item.image))}" width="${Number(item.width)||300}" height="${Number(item.height)||600}" alt="${title}" loading="lazy" decoding="async"></span><span class="article-rail-fallback">${title}</span></a>`;
}

function renderCustomRailCard(item){
  const title=escapeHtml(item.title);
  const banner=safeHttpUrl(item.banner);
  const visual=banner?`<span class="article-rail-visual"><img src="${escapeHtml(banner)}" alt="${title}" loading="lazy" decoding="async"></span>`:'';
  return `<a class="article-rail-card article-rail-card-custom" href="${escapeHtml(safeHttpUrl(item.url))}" target="_blank" rel="nofollow sponsored noopener noreferrer" aria-label="Reklama: ${title}"><span class="article-rail-label">Reklama</span>${visual}<span class="article-rail-copy"><small>${escapeHtml(item.tag)}</small><strong>${title}</strong><span>${escapeHtml(item.text)}</span><b>Zjistit více →</b></span><span class="article-rail-fallback">${title}</span></a>`;
}

function installImageFallbacks(root=document){
  root.querySelectorAll('.article-rail-card img').forEach(image=>{
    image.addEventListener('error',()=>image.closest('.article-rail-card')?.classList.add('is-image-error'),{once:true});
  });
}

function renderArticleSideRails(){
  const shell=document.querySelector('main.article-shell');
  const article=shell?.querySelector('article.article');
  if(!shell||!article||document.querySelector('.article-ad-rail'))return;

  const context=inferPromoContext(`${document.title} ${article.textContent||''}`);
  const featuredTower=towerCreativeItems.find(item=>item.id==='uklizecka-cisteni-tower');
  const tower=featuredTower||pickTowerCreative(context,0);
  const custom=pickRailPromo(context,7);
  if(!tower&&!custom)return;

  const seed=hashSeed(location.pathname+new Date().toISOString().slice(0,10));
  const leftContent=seed%2===0
    ?(tower?renderTowerRailCard(tower):renderCustomRailCard(custom))
    :(custom?renderCustomRailCard(custom):renderTowerRailCard(tower));
  const rightContent=seed%2===0
    ?(custom?renderCustomRailCard(custom):renderTowerRailCard(tower))
    :(tower?renderTowerRailCard(tower):renderCustomRailCard(custom));

  if(custom)usedPromoIds.add(custom.id);

  const left=document.createElement('aside');
  left.className='article-ad-rail article-ad-rail-left';
  left.setAttribute('aria-label','Reklama vlevo od článku');
  left.innerHTML=leftContent;

  const right=document.createElement('aside');
  right.className='article-ad-rail article-ad-rail-right';
  right.setAttribute('aria-label','Reklama vpravo od článku');
  right.innerHTML=rightContent;

  document.body.append(left,right);

  const sticky=shell.querySelector('aside.sticky');
  if(sticky&&tower){
    const inside=document.createElement('div');
    inside.className='article-aside-tower';
    inside.setAttribute('aria-label','Svislá reklama');
    inside.innerHTML=renderTowerRailCard(tower);
    sticky.appendChild(inside);
  }

  installImageFallbacks(document);
}


function installGuaranteedCleaningBanner(){
  if(document.querySelector('.featured-cleaning-ad'))return;
  const item=promoItems.find(entry=>entry.id==='uklizecka-cisteni');
  if(!item)return;
  const section=document.createElement('section');
  section.className='featured-cleaning-ad';
  section.setAttribute('aria-label','Reklama: Čištění koberců, sedaček a čalounění');
  section.innerHTML=`<div class="promo-label">REKLAMA</div><a href="${escapeHtml(safeHttpUrl(item.url))}" target="_blank" rel="nofollow sponsored noopener noreferrer"><img src="/assets/reklamy/vaseuklizecka-cisteni-wide-sharp-v3.svg" width="1200" height="576" alt="Čištění koberců, sedaček a čalounění – Vaše uklízečka, telefon 603 206 308" decoding="async"></a>`;
  const article=document.querySelector('article.article');
  if(article){
    const anchor=article.querySelector('.hero-visual')||article.querySelector('.leadtext')||article.querySelector('h1');
    if(anchor){anchor.after(section);return;}
  }
  const homeHero=document.querySelector('main .hero');
  if(homeHero){homeHero.after(section);return;}
  const main=document.querySelector('main');
  if(main)main.prepend(section);
}

document.addEventListener('DOMContentLoaded',async()=>{
  ensurePromoStyles();
  installGuaranteedCleaningBanner();
  await loadAffiliateSnapshot();
  redistributeArticlePromos();
  renderArticleSideRails();
  renderPromos();
});
