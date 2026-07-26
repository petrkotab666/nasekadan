(()=>{
  'use strict';

  const GENERIC=/vybran[aá]\s+partnersk[aá]\s+nab[ií]dka|centr[aá]ln[ií]\s+datab[aá]z|propojen[yý]ch\s+web|partnersk[aá]\s+nab[ií]dka/i;
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
    haffit:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',
    zonky:'Online půjčka s přehledným vyřízením a možností předčasného splacení.',
    'dobre-knihy':'Knihy, audioknihy a další čtení pro volný čas i celou rodinu.',
    biano:'Nábytek, dekorace a vybavení domácnosti z nabídky mnoha internetových obchodů.',
    nanospace:'České produkty pro zdravější domácnost, alergiky a kvalitnější spánek.',
    concept:'Domácí spotřebiče a praktické vybavení pro každodenní provoz domácnosti.',
    proalergiky:'Specializované produkty pro alergiky a zdravější prostředí v domácnosti.',
    invia:'Last minute i běžné zájezdy k moři, do hor a za poznáním s možností porovnání nabídek.',
    'invia-cz':'Last minute i běžné zájezdy k moři, do hor a za poznáním s možností porovnání nabídek.',
    atis:'Pobytové, poznávací a wellness zájezdy po Česku, Slovensku i Evropě.',
    'atis-cz':'Pobytové, poznávací a wellness zájezdy po Česku, Slovensku i Evropě.',
    excursia:'Poznávací zájezdy, výlety, exkurze a další zážitky v Česku i zahraničí.',
    'excursia-cz':'Poznávací zájezdy, výlety, exkurze a další zážitky v Česku i zahraničí.',
    brainmarket:'Sportovní výživa, zdravé potraviny, vitaminy a další produkty pro aktivní životní styl.',
    brainmax:'Vitaminy, minerály, zdravé potraviny a sportovní výživa značky BrainMax.',
    glami:'Vyhledávání módy, obuvi a doplňků z nabídky internetových obchodů.',
    aranys:'Šperky, hodinky a módní doplňky pro ženy i muže.',
    marre:'Aromaterapie, přírodní oleje a vybavení pro domácí wellness.',
    'diskont-zahradkar':'Zahradnické potřeby, osiva, hnojiva a vybavení pro zahradu.',
    'ceska-zahrada':'Rostliny, zahradnické potřeby a další vybavení pro pěstování.',
    barman:'Vybavení pro přípravu nápojů, domácí bar a gastronomii.'
  };

  function norm(value){
    return String(value||'')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g,'')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g,'-')
      .replace(/^-+|-+$/g,'');
  }

  function fallback(title,tag){
    const value=norm(tag);
    if(/dovolen|cestov|zajezd|pobyt|vylet|zazit/.test(value))return `${title} nabízí dovolené, zájezdy, pobyty nebo služby pro cestování a volný čas.`;
    if(/internet|televize|mobil/.test(value))return `${title} nabízí internetové, televizní nebo mobilní služby.`;
    if(/pojist|finance|srovnavac/.test(value))return `${title} nabízí finanční nebo pojistné služby s online sjednáním či porovnáním.`;
    if(/energie/.test(value))return `${title} nabízí energie nebo související služby pro domácnosti.`;
    if(/zdravi|sport/.test(value))return `${title} nabízí produkty zaměřené na zdraví, péči o tělo nebo aktivní životní styl.`;
    if(/domacnost|bydleni|spotrebice/.test(value))return `${title} nabízí vybavení, produkty nebo služby pro domácnost a bydlení.`;
    if(/mazlicci|chovatel/.test(value))return `${title} nabízí produkty nebo služby pro domácí mazlíčky.`;
    return `Produkty a služby od ${title}.`;
  }

  function copyFor(item){
    const id=norm(item?.id||item?.title);
    return COPY[id]||fallback(String(item?.title||'Inzerent'),String(item?.tag||''));
  }

  function fixItems(){
    try{
      if(typeof partnerCopy==='object'&&partnerCopy)Object.assign(partnerCopy,COPY);
      if(typeof promoItems==='undefined'||!Array.isArray(promoItems))return;
      for(const item of promoItems){
        if(!item||typeof item!=='object')continue;
        const exact=COPY[norm(item.id||item.title)];
        if(exact||GENERIC.test(String(item.text||''))||!String(item.text||'').trim())item.text=exact||copyFor(item);
      }
    }catch{}
  }

  function fixCard(card){
    const title=card.querySelector('strong')?.textContent?.trim();
    if(!title)return;
    const tag=card.querySelector('small')?.textContent?.trim()||'';
    const id=norm(title);
    const description=card.querySelector('.promo-description,.article-rail-copy strong + span,strong + span');
    if(!description)return;
    const exact=COPY[id];
    if(exact||GENERIC.test(description.textContent)||!description.textContent.trim())description.textContent=exact||fallback(title,tag);
  }

  function run(root=document){
    fixItems();
    if(root.matches?.('.promo-card,.article-rail-card-custom'))fixCard(root);
    root.querySelectorAll?.('.promo-card,.article-rail-card-custom').forEach(fixCard);
  }

  function start(){
    run();
    new MutationObserver(records=>{
      for(const record of records){
        for(const node of record.addedNodes){
          if(node instanceof Element)run(node);
        }
      }
    }).observe(document.body,{childList:true,subtree:true});
    [50,200,500,1000,2500,5000].forEach(delay=>setTimeout(()=>run(),delay));
  }

  fixItems();
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
