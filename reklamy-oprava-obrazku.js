(()=>{
  'use strict';

  const IMAGE_SELECTOR='.promo-card img,.article-rail-card img';
  const GENERIC_COPY=/vybran[aá]\s+partnersk[aá]\s+nab[ií]dka|centr[aá]ln[ií]\s+datab[aá]z|propojen[yý]ch\s+web|partnersk[aá]\s+nab[ií]dka/i;
  const SEASONAL_CONTEXTS=new Set(['general','local','sidebar','family','travel','summer','finance','home','health','internet','auto','energy','pets','sport']);
  const TRAVEL_IDS=new Set([
    'atis','atis-cz','ceskekormidlo','ceskekormidlo-cz','excursia','excursia-cz'
  ]);
  const HEAT_IDS=new Set([
    'apollostore','apollostore-cz','concept','concept-cz','proalergiky','proalergiky-cz'
  ]);
  const POJISTIME_IDS=new Set(['pojistime-family-wide-a','pojistime-family-wide-b','pojistime-family-square']);
  const NO_IMAGE_IDS=new Set([
    'atis','atis-cz','apollostore','apollostore-cz','concept','concept-cz','proalergiky','proalergiky-cz'
  ]);
  const COPY={
    pojistime:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',
    csob:'Pojištění auta, majetku, odpovědnosti, cestování i podnikatelských rizik.',
    mutumutu:'Životní pojištění a ochrana příjmu sjednávané online.',
    petexpert:'Pojištění psů a koček pro nečekané veterinární výdaje.',
    eon:'Elektřina, plyn a energetická řešení pro domácnosti.',
    vodafone:'Mobilní tarify, pevný internet a televizní služby pro domácnosti.',
    poda:'Internetové připojení a televizní služby podle dostupnosti na adrese.',
    telly:'Internetová televize se sportovními, filmovými a dalšími programy.',
    nejpripojeni:'Porovnání možností internetu a IPTV podle konkrétní adresy.',
    uvtnet:'Internetové připojení a související služby podle dostupnosti v lokalitě.',
    klik:'Online srovnání pojištění auta, majetku a cestování.',
    kalkulator:'Srovnání pojištění, energií a dalších pravidelných výdajů domácnosti.',
    rixo:'Online srovnání pojištění vozidel, majetku, cestování a dalších rizik.',
    vyklidime:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',
    uklizecka:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',
    'vase-uklizecka':'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',
    'uklizecka-cisteni-rotating':'Hloubkové čištění koberců, sedaček a čalounění na Kadaňsku. Objednávky: 603 206 308.',
    haffit:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',
    zonky:'Online půjčka s přehledným vyřízením a možností předčasného splacení.',
    'dobre-knihy':'Knihy, audioknihy a další čtení pro volný čas i celou rodinu.',
    biano:'Nábytek, dekorace a vybavení domácnosti z nabídky mnoha internetových obchodů.',
    nanospace:'České produkty pro zdravější domácnost, alergiky a kvalitnější spánek.',
    concept:'Ventilátory, čističky vzduchu, zvlhčovače a další spotřebiče pro příjemnější domácnost.',
    'concept-cz':'Ventilátory, čističky vzduchu, zvlhčovače a další spotřebiče pro příjemnější domácnost.',
    proalergiky:'Klimatizace, ventilátory, čističky vzduchu a další vybavení pro zdravější prostředí doma.',
    'proalergiky-cz':'Klimatizace, ventilátory, čističky vzduchu a další vybavení pro zdravější prostředí doma.',
    apollostore:'Klimatizace, ventilátory, odvlhčovače a další spotřebiče pro horké letní dny.',
    'apollostore-cz':'Klimatizace, ventilátory, odvlhčovače a další spotřebiče pro horké letní dny.',
    atis:'Pobytové, poznávací a wellness zájezdy po Česku, Slovensku i Evropě.',
    'atis-cz':'Pobytové, poznávací a wellness zájezdy po Česku, Slovensku i Evropě.',
    ceskekormidlo:'Last minute, pobytové a poznávací zájezdy od Českého kormidla.',
    'ceskekormidlo-cz':'Last minute, pobytové a poznávací zájezdy od Českého kormidla.',
    excursia:'Výlety, exkurze a zážitky pro volný čas v Česku i zahraničí.',
    'excursia-cz':'Výlety, exkurze a zážitky pro volný čas v Česku i zahraničí.',
    brainmarket:'Sportovní výživa, zdravé potraviny, vitaminy a další produkty pro aktivní životní styl.',
    brainmax:'Vitaminy, minerály, zdravé potraviny a sportovní výživa značky BrainMax.',
    glami:'Vyhledávání módy, obuvi a doplňků z nabídky internetových obchodů.',
    aranys:'Šperky, hodinky a módní doplňky pro ženy i muže.',
    marre:'Aromaterapie, přírodní oleje a vybavení pro domácí wellness.',
    'diskont-zahradkar':'Zahradnické potřeby, osiva, hnojiva a vybavení pro zahradu.',
    'ceska-zahrada':'Rostliny, zahradnické potřeby a další vybavení pro pěstování.',
    barman:'Vybavení pro přípravu nápojů, domácí bar a gastronomii.'
  };

  let seasonalInsertCount=0;

  function normalizeToken(value){
    return String(value||'')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g,'')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g,'-')
      .replace(/^-+|-+$/g,'');
  }

  function localHash(value){
    return [...String(value)].reduce((sum,char)=>((sum*31)+char.charCodeAt(0))>>>0,0);
  }

  function isSummerSeason(){
    const month=new Date().getMonth()+1;
    return month>=5&&month<=9;
  }

  function itemId(item){
    return normalizeToken(item?.id||item?.title);
  }

  function copyFromTag(title,tag){
    const value=normalizeToken(tag);
    if(/klimatiz|ventilator|ochlaz|vzduch|spotrebice|domacnost/.test(value))return `${title} nabízí vybavení pro příjemnější domácnost během horkých dnů.`;
    if(/dovolen|cestov|zajezd|pobyt|vylet|zazit/.test(value))return `${title} nabízí dovolené, zájezdy, pobyty nebo další služby pro cestování a volný čas.`;
    if(/internet|televize|mobil/.test(value))return `${title} nabízí internetové, televizní nebo mobilní služby podle aktuálních podmínek.`;
    if(/pojist|finance|srovnavac/.test(value))return `${title} nabízí finanční nebo pojistné služby s možností ověřit aktuální podmínky online.`;
    if(/energie/.test(value))return `${title} nabízí energie nebo související služby pro domácnosti.`;
    if(/zdravi|sport/.test(value))return `${title} nabízí produkty zaměřené na zdraví, péči o tělo nebo aktivní životní styl.`;
    if(/mazlicci|chovatel/.test(value))return `${title} nabízí produkty nebo služby pro domácí mazlíčky.`;
    if(/knihy|volny-cas|rodina/.test(value))return `${title} nabízí produkty a služby pro rodinu a volný čas.`;
    return `Nabídka produktů nebo služeb od ${title}.`;
  }

  function itemCopy(item){
    return COPY[itemId(item)]||copyFromTag(String(item?.title||'Inzerent'),String(item?.tag||''));
  }

  function normalizePromoItems(){
    if(typeof promoItems==='undefined'||!Array.isArray(promoItems))return;
    for(let i=promoItems.length-1;i>=0;i--){if(itemId(promoItems[i]).replace(/-/g,'').startsWith('lastminute'+'slevy'))promoItems.splice(i,1);}
    const url='https://pojistime.to/?utm_source=nasekadan&utm_medium=banner&utm_campaign=pojistime_rotation_2026';
    const additions=[
      {id:'pojistime-family-wide-a',title:'Pojistime.to – jistota pro každý den',text:'Srovnání pojištění auta, bydlení, cestování i dalších rizik přehledně online.',url,banner:'/assets/reklamy/pojistime-family-wide-a.svg',wideBanner:'/assets/reklamy/pojistime-family-wide-a.svg',tag:'Pojištění online',contexts:['general','local','sidebar','finance','auto','home','travel'],weight:3},
      {id:'pojistime-family-wide-b',title:'Pojistime.to – pojištění jednoduše',text:'Porovnejte nabídky pojištění online a vyberte vhodnou cenu i podmínky.',url,banner:'/assets/reklamy/pojistime-family-wide-b.svg',wideBanner:'/assets/reklamy/pojistime-family-wide-b.svg',tag:'Chytré pojištění',contexts:['general','local','sidebar','finance','auto','home','travel'],weight:3},
      {id:'pojistime-family-square',title:'Pojistime.to – porovnat nabídky',text:'Auto, bydlení, cestování a další druhy pojištění na jednom místě.',url,banner:'/assets/reklamy/pojistime-family-square.svg',tag:'Srovnání pojištění',contexts:['general','local','sidebar','finance','auto','home','travel'],weight:2}
    ];
    for(const item of additions){if(!promoItems.some(row=>itemId(row)===item.id))promoItems.push(item);}
    if(typeof towerCreativeItems!=='undefined'&&!towerCreativeItems.some(row=>row.id==='pojistime-family-tower'))towerCreativeItems.push({id:'pojistime-family-tower',title:'Pojistime.to',url,image:'/assets/reklamy/pojistime-family-tower.svg',width:300,height:600,contexts:['general','local','finance','auto','home','travel','sidebar'],weight:4});
    for(const item of promoItems){
      if(!item||typeof item!=='object')continue;
      const id=itemId(item);
      if(!String(item.text||'').trim()||GENERIC_COPY.test(String(item.text)))item.text=itemCopy(item);
      if(NO_IMAGE_IDS.has(id))item.banner='';
      if(TRAVEL_IDS.has(id)){
        item.tag=id.startsWith('excursia')?'Výlety a zážitky':id.startsWith('atis')?'Dovolená a pobyty':'Last minute a zájezdy';
        item.contexts=[...new Set([...(item.contexts||[]),'travel','family','general','sidebar'])];
        item.weight=Math.max(2,Number(item.weight)||1);
      }
      if(HEAT_IDS.has(id)){
        item.tag='Léto a ochlazení';
        item.contexts=[...new Set([...(item.contexts||[]),'summer','home','health','general','sidebar'])];
        item.weight=Math.max(3,Number(item.weight)||1);
      }
    }
  }

  function seasonalGroupFor(context,seed){
    if(context==='travel')return TRAVEL_IDS;
    if(['summer','home','health','energy'].includes(context))return HEAT_IDS;
    return seed%2===0?TRAVEL_IDS:HEAT_IDS;
  }

  function installFeaturedSeasonalBanner(){
    if(document.querySelector('.featured-cleaning-ad'))return;
    if(typeof promoItems==='undefined'||!Array.isArray(promoItems)||typeof renderBannerCard!=='function')return;
    normalizePromoItems();

    const cleaning=promoItems.filter(item=>itemId(item)==='uklizecka-cisteni-rotating');
    const seasonal=isSummerSeason()?promoItems.filter(item=>TRAVEL_IDS.has(itemId(item))||HEAT_IDS.has(itemId(item))||POJISTIME_IDS.has(itemId(item))):[];
    const candidates=[...cleaning,...seasonal].filter((item,index,array)=>array.findIndex(entry=>entry.id===item.id)===index);
    if(!candidates.length)return;

    const weighted=candidates.flatMap(item=>Array.from({length:Math.max(1,Number(item.weight)||1)},()=>item));
    const day=new Date().toISOString().slice(0,10);
    const item=weighted[localHash(`${location.pathname}|${day}|featured-seasonal`)%weighted.length];
    const section=document.createElement('section');
    section.className='featured-cleaning-ad featured-rotating-ad';
    section.setAttribute('aria-label',`Reklama: ${item.title}`);
    section.innerHTML=`<div class="promo-label">REKLAMA</div>${renderBannerCard(item)}`;
    try{if(typeof usedPromoIds!=='undefined'&&usedPromoIds?.add)usedPromoIds.add(item.id);}catch{}

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

  function patchPromoEngine(){
    try{
      if(typeof partnerCopy==='object'&&partnerCopy)Object.assign(partnerCopy,COPY);

      if(typeof promoItems!=='undefined'&&Array.isArray(promoItems)){
        const cleaning=promoItems.find(item=>item.id==='uklizecka-cisteni');
        if(cleaning)cleaning.id='uklizecka-cisteni-rotating';
      }
      if(typeof towerCreativeItems!=='undefined'&&Array.isArray(towerCreativeItems)){
        const cleaningTower=towerCreativeItems.find(item=>item.id==='uklizecka-cisteni-tower');
        if(cleaningTower){cleaningTower.id='uklizecka-cisteni-tower-rotating';cleaningTower.weight=2;}
      }

      if(typeof contextsFromCategories==='function'){
        const original=contextsFromCategories;
        contextsFromCategories=function(categories){
          const contexts=new Set(original(categories));
          const text=(categories||[]).map(normalizeToken).join(' ');
          if(/cestov|dovolen|zajezd|last-minute|pobyt|hotel|wellness|eurovikend|plavb|vylet|exkurz|zazitk/.test(text))contexts.add('travel');
          if(/klimatiz|ventilator|ochlaz|odvlhcov|cisticky-vzduchu|zvlhcov|vedra|leto|spotrebice/.test(text)){
            contexts.add('summer');contexts.add('home');
          }
          if(/rodina/.test(text))contexts.add('family');
          return [...contexts];
        };
      }

      if(typeof tagFromContexts==='function'){
        const original=tagFromContexts;
        tagFromContexts=function(contexts,categories){
          const text=(categories||[]).map(normalizeToken).join(' ');
          if(/klimatiz|ventilator|ochlaz|odvlhcov|cisticky-vzduchu|zvlhcov|vedra|leto/.test(text))return 'Léto a ochlazení';
          if(/cestov|dovolen|zajezd|last-minute|pobyt|hotel|wellness|vylet|exkurz|zazitk/.test(text))return 'Dovolená a cestování';
          return original(contexts,categories);
        };
      }

      if(typeof inferPromoContext==='function'){
        const original=inferPromoContext;
        inferPromoContext=function(text){
          const value=String(text||'').toLocaleLowerCase('cs');
          if(/vedr|hork|trop|léto|letní|koupališt|klimatiz|ventilátor|ochlaz|slunce|teplot|sucho/.test(value))return 'summer';
          if(/dovolen|zájezd|cestov|hotel|letišt|moř|pláž|prázdnin|výlet|pobyt/.test(value))return 'travel';
          return original(text);
        };
      }

      if(typeof loadAffiliateSnapshot==='function'&&typeof mergeSnapshotPartners==='function'){
        const originalLoad=loadAffiliateSnapshot;
        loadAffiliateSnapshot=async function(...args){
          await originalLoad.apply(this,args);
          normalizePromoItems();
          try{
            const url=new URL('/assets/affiliate-site-travel-overlay.json',location.origin);
            url.searchParams.set('v',new Date().toISOString().slice(0,13));
            const response=await fetch(url,{cache:'no-store',headers:{Accept:'application/json'}});
            if(response.ok)mergeSnapshotPartners(await response.json());
          }catch(error){
            console.warn('Letní reklamní data se nepodařilo načíst.',error);
          }
          normalizePromoItems();
          installFeaturedSeasonalBanner();
        };
      }

      if(typeof installGuaranteedCleaningBanner==='function'){
        installGuaranteedCleaningBanner=function(){};
      }

      if(typeof pickPromos==='function'){
        const originalPick=pickPromos;
        pickPromos=function(context,count,offset){
          normalizePromoItems();
          const selected=originalPick(context,count,offset);
          if(!isSummerSeason()||!count||!SEASONAL_CONTEXTS.has(context)||seasonalInsertCount>=4)return selected;
          if(typeof promoItems==='undefined'||!Array.isArray(promoItems))return selected;

          const day=new Date().toISOString().slice(0,10);
          const seed=localHash(`${location.pathname}|${day}|${context}|${offset}|seasonal`);
          const group=seasonalGroupFor(context,seed+seasonalInsertCount);
          if(selected.some(item=>group.has(itemId(item))))return selected;
          if(context!=='travel'&&context!=='summer'&&seasonalInsertCount>0&&seed%3===0)return selected;

          const pool=promoItems.filter(item=>group.has(itemId(item))&&!selected.some(entry=>entry.id===item.id));
          if(!pool.length)return selected;
          const seasonal=pool[seed%pool.length];
          if(selected.length<count)selected.push(seasonal);
          else selected[Math.max(0,selected.length-1)]=seasonal;
          seasonalInsertCount++;
          try{if(typeof usedPromoIds!=='undefined'&&usedPromoIds?.add)usedPromoIds.add(seasonal.id);}catch{}
          return selected;
        };
      }
    }catch(error){
      console.warn('Oprava reklam se nepodařila inicializovat.',error);
    }
  }

  function normalizeCard(card){
    if(!(card instanceof Element))return;
    const title=card.querySelector('strong')?.textContent?.trim();
    if(!title)return;
    const id=normalizeToken(title);
    const tag=card.querySelector('small')?.textContent?.trim()||'';
    const description=card.querySelector('.promo-description,.article-rail-copy strong + span,strong + span');
    if(description&&(!description.textContent.trim()||GENERIC_COPY.test(description.textContent))){
      description.textContent=COPY[id]||copyFromTag(title,tag);
    }
    if(NO_IMAGE_IDS.has(id))card.querySelector('.promo-banner,.article-rail-visual')?.remove();
  }

  function normalizeCards(root=document){
    if(root.matches?.('.promo-card,.article-rail-card-custom'))normalizeCard(root);
    root.querySelectorAll?.('.promo-card,.article-rail-card-custom').forEach(normalizeCard);
  }

  function repairImage(image){
    if(!(image instanceof HTMLImageElement)||image.dataset.promoImageRepaired==='1')return;
    image.dataset.promoImageRepaired='1';
    const card=image.closest('.promo-card');
    const rail=image.closest('.article-rail-card');
    if(rail){
      const visual=image.closest('.article-rail-visual');
      if(visual)visual.remove();
      else rail.classList.add('is-image-error');
      return;
    }
    const banner=image.closest('.promo-banner');
    if(!banner)return;
    if(card?.classList.contains('promo-card-wide')){
      const title=card.querySelector('strong')?.textContent?.trim()||image.alt||'Reklama';
      banner.className='promo-banner promo-banner-fallback';
      banner.textContent=title;
    }else{
      banner.remove();
    }
  }

  function watchImage(image){
    if(!(image instanceof HTMLImageElement))return;
    image.style.visibility='hidden';
    if(image.dataset.promoImageWatched!=='1'){
      image.dataset.promoImageWatched='1';
      image.addEventListener('load',()=>{if(image.isConnected)image.style.visibility='visible';},{once:true});
      image.addEventListener('error',()=>repairImage(image),{once:true});
    }
    if(image.complete){
      if(image.naturalWidth>0)image.style.visibility='visible';
      else repairImage(image);
    }
    setTimeout(()=>{
      if(image.isConnected&&image.style.visibility==='hidden')repairImage(image);
    },3000);
  }

  function watch(root=document){
    normalizePromoItems();
    normalizeCards(root);
    if(root instanceof HTMLImageElement)watchImage(root);
    root.querySelectorAll?.(IMAGE_SELECTOR).forEach(watchImage);
  }

  function start(){
    watch();
    const observer=new MutationObserver(records=>{
      for(const record of records){
        for(const node of record.addedNodes){
          if(node instanceof Element)watch(node);
        }
      }
    });
    observer.observe(document.body,{childList:true,subtree:true});
    [50,200,600,1500,3500].forEach(delay=>setTimeout(()=>watch(),delay));
  }

  patchPromoEngine();
  document.addEventListener('error',event=>{
    if(event.target instanceof HTMLImageElement)repairImage(event.target);
  },true);

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
