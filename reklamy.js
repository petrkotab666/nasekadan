(()=>{
  'use strict';

  const promos=[
    {id:'pojistime',title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',tag:'Pojištění',contexts:['finance','auto','home','travel','sidebar','general']},
    {id:'csob',title:'ČSOB Pojišťovna',text:'Pojištění auta, majetku, odpovědnosti, cestování i podnikatelských rizik.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=f5e0f8fb',banner:'https://doc.ehub.cz/b/174174d6/041e34d5.jpg',tag:'Pojištění',contexts:['finance','auto','home','travel','general']},
    {id:'mutumutu',title:'Mutumutu.cz',text:'Životní pojištění a ochrana příjmu sjednávané online.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=74eab778',banner:'https://doc.ehub.cz/b/706fc994/00043bad.png',tag:'Život a příjem',contexts:['finance','health','general']},
    {id:'petexpert',title:'PetExpert.cz',text:'Pojištění psů a koček pro nečekané veterinární výdaje.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=ce2e382f',banner:'https://doc.ehub.cz/b/a540cd53/0dce0d8e.png',tag:'Mazlíčci',contexts:['pets','family','general']},
    {id:'eon',title:'E.ON.cz',text:'Elektřina, plyn a energetická řešení pro domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=87497054',banner:'https://doc.ehub.cz/b/40b76033/0d98713f.png',tag:'Energie',contexts:['home','energy','general']},
    {id:'vodafone',title:'Vodafone.cz',text:'Mobilní tarify, pevný internet a televizní služby pro domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=aface625',banner:'https://doc.ehub.cz/b/6965053d/0168d188.jpg',tag:'Internet a mobil',contexts:['internet','home','general']},
    {id:'poda',title:'PODA.cz',text:'Internetové připojení a televizní služby podle dostupnosti na adrese.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=a86d04cf',banner:'https://doc.ehub.cz/b/6b66a101/30907ccc.jpg',tag:'Internet a TV',contexts:['internet','home','general']},
    {id:'telly',title:'Telly.cz',text:'Internetová televize se sportovními, filmovými a dalšími programy.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b1a888ed',banner:'https://doc.ehub.cz/b/77a1720e/11b66e36.jpg',tag:'Televize',contexts:['internet','sport','general']},
    {id:'nejpripojeni',title:'NejPřipojení.cz',text:'Porovnání možností internetu a IPTV podle konkrétní adresy.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=7dc84251',banner:'https://doc.ehub.cz/b/a7ced961/16394373.png',tag:'Internet',contexts:['internet','home','general']},
    {id:'uvtnet',title:'ÚVTnet.cz',text:'Internetové připojení a související služby podle dostupnosti v lokalitě.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=51dbb2b9',banner:'https://doc.ehub.cz/b/f402ef36/135fd2cd.png',tag:'Internet',contexts:['internet','home','general']},
    {id:'klik',title:'Klik.cz',text:'Online srovnání pojištění auta, majetku a cestování.',url:'https://www.tkqlhce.com/click-101819174-15024026',banner:'https://www.awltovhc.com/image-101819174-15021022',tag:'Srovnávač',contexts:['finance','auto','travel','home','general']},
    {id:'kalkulator',title:'Kalkulator.cz',text:'Srovnání pojištění, energií a dalších pravidelných výdajů domácnosti.',url:'https://www.tkqlhce.com/click-101819174-15616422',banner:'https://www.ftjcfx.com/image-101819174-15616436',tag:'Srovnávač',contexts:['finance','auto','energy','home','general']},
    {id:'rixo',title:'RIXO.cz',text:'Online srovnání pojištění vozidel, majetku, cestování a dalších rizik.',url:'https://www.rixo.cz/pojisteni-vozidel/?a_box=9n97unga&a_cam=1',tag:'Pojištění',contexts:['finance','auto','travel','home','general']},
    {id:'vyklidime',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',tag:'Místní služba',contexts:['home','sidebar','local','general']},
    {id:'uklizecka',title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',tag:'Místní služba',contexts:['home','sidebar','local','general']},
    {id:'haffit',title:'Haffit',text:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',url:'https://www.haffit.cz/?a_box=cbhtyjjm&a_cam=1',tag:'Pro chovatele',contexts:['pets','family','general']},
    {id:'zonky',title:'Zonky půjčka',text:'Online půjčka s přehledným vyřízením a možností předčasného splacení.',url:'https://www.zonky.cz/pujcka-od-zonky/?a_box=s8m27mmy',tag:'Finance',contexts:['finance','home','general']},
    {id:'dobre-knihy',title:'Dobré-knihy.cz',text:'Knihy, audioknihy a další čtení pro volný čas i celou rodinu.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=1ec2df65',banner:'https://doc.ehub.cz/b/57ad8ec1/30a97424.jpg',tag:'Knihy',contexts:['family','general']},
    {id:'biano',title:'Biano.cz',text:'Nábytek, dekorace a vybavení domácnosti z nabídky mnoha internetových obchodů.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=da726a9e',banner:'https://doc.ehub.cz/b/80610cd6/82a1c42b.png',tag:'Bydlení',contexts:['home','general']},
    {id:'nanospace',title:'Nanospace.cz',text:'České produkty pro zdravější domácnost, alergiky a kvalitnější spánek.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=32dfe8fd',banner:'https://doc.ehub.cz/b/21118d16/022986bf.jpg',tag:'Zdravá domácnost',contexts:['health','home','general']},
    {id:'concept',title:'Concept.cz',text:'Domácí spotřebiče a praktické vybavení pro každodenní provoz domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=b23975b5',banner:'https://doc.ehub.cz/b/035e8afb/e737c1f9.jpg',tag:'Spotřebiče',contexts:['home','general']},
    {id:'proalergiky',title:'Proalergiky.cz',text:'Specializované produkty pro alergiky a zdravější prostředí v domácnosti.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=abc25217',banner:'https://doc.ehub.cz/b/cbee71d3/017d5633.jpg',tag:'Zdraví',contexts:['health','home','general']},
    {id:'invia-cz',title:'Invia.cz',text:'Last minute i běžné zájezdy k moři, do hor a za poznáním s možností porovnání nabídek.',url:'https://www.invia.cz/dovolena/last-minute/?b_https=1&aid=9256106',tag:'Dovolená a zájezdy',contexts:['travel','family','general']},
    {id:'atis-cz',title:'Atis.cz',text:'Pobytové, poznávací a wellness zájezdy po Česku, Slovensku i Evropě.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=49886ce2',tag:'Dovolená a pobyty',contexts:['travel','family','general']},
    {id:'excursia-cz',title:'Excursia.cz',text:'Poznávací zájezdy, výlety, exkurze a další zážitky v Česku i zahraničí.',url:'https://ehub.cz/system/scripts/click.php?a_aid=6926a50f&a_bid=76c9b39c',banner:'https://doc.ehub.cz/b/2e6a0944/368140a3.jpg',tag:'Výlety a zážitky',contexts:['travel','family','general']}
  ];

  const used=new Set();

  function esc(value){
    return String(value??'').replace(/[&<>'"]/g,char=>({
      '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
    })[char]);
  }

  function safeUrl(value){
    try{
      const url=new URL(String(value||''),location.origin);
      return /^https?:$/.test(url.protocol)?url.href:'';
    }catch{return '';}
  }

  function hash(value){
    return [...String(value)].reduce((sum,char)=>((sum*33)+char.charCodeAt(0))>>>0,5381);
  }

  function contextFromText(text){
    const value=String(text||'').toLocaleLowerCase('cs');
    if(/vlak|želez|výluk|nádraž|autobus|doprav|silnic|auto/.test(value))return 'auto';
    if(/internet|televiz|kabel|optik|připojen/.test(value))return 'internet';
    if(/nemocnic|zdrav|lékař|pacient|ambulanc|porod/.test(value))return 'health';
    if(/dovolen|zájezd|cestov|výlet|hotel|moře|letišt/.test(value))return 'travel';
    if(/peněz|financ|dotac|náklad|milion|hospodař/.test(value))return 'finance';
    if(/energie|elektřin|plyn|domác|bydlen|stavb/.test(value))return 'home';
    if(/pes|kočk|zvíř|mazlíčk/.test(value))return 'pets';
    if(/kadaň|volb|politik|měst|zastupitel/.test(value))return 'local';
    return 'general';
  }

  function pick(context,count,offset=0){
    const exact=promos.filter(item=>item.contexts.includes(context));
    const rest=promos.filter(item=>!exact.includes(item));
    const pool=[...exact,...rest];
    const day=new Date().toISOString().slice(0,10);
    const start=(hash(`${location.pathname}|${day}|${context}|${offset}`)%pool.length+pool.length)%pool.length;
    const rotated=[...pool.slice(start),...pool.slice(0,start)];
    const result=[];
    for(const item of rotated){
      if(result.some(row=>row.id===item.id))continue;
      if(used.has(item.id)&&result.length+1<count)continue;
      result.push(item);
      if(result.length>=count)break;
    }
    result.forEach(item=>used.add(item.id));
    return result;
  }

  function imageMarkup(item,wide=false){
    const src=safeUrl(item.banner);
    if(!src)return wide?`<span class="promo-banner promo-banner-fallback">${esc(item.title)}</span>`:'';
    return `<span class="promo-banner"><img src="${esc(src)}" alt="${esc(item.title)}" loading="lazy" decoding="async"></span>`;
  }

  function card(item,wide=false){
    const href=safeUrl(item.url);
    if(!href)return '';
    if(wide){
      return `<a class="promo-card promo-card-wide" href="${esc(href)}" target="_blank" rel="nofollow sponsored noopener noreferrer">${imageMarkup(item,true)}<span class="promo-wide-copy"><small>${esc(item.tag)}</small><strong>${esc(item.title)}</strong><span class="promo-description">${esc(item.text)}</span><b>Zjistit více →</b></span></a>`;
    }
    return `<a class="promo-card" href="${esc(href)}" target="_blank" rel="nofollow sponsored noopener noreferrer">${imageMarkup(item,false)}<small>${esc(item.tag)}</small><strong>${esc(item.title)}</strong><span>${esc(item.text)}</span><b>Zjistit více →</b></a>`;
  }

  function ensureStyles(){
    if(document.getElementById('nk-ad-styles'))return;
    const style=document.createElement('style');
    style.id='nk-ad-styles';
    style.textContent=`
      .promo-grid-banner{grid-template-columns:minmax(0,1fr)!important}
      .promo-card-wide{display:grid!important;grid-template-columns:minmax(220px,35%) minmax(0,1fr);padding:0!important;min-height:170px!important}
      .promo-card-wide .promo-banner{height:100%!important;min-height:170px;margin:0!important;border:0;border-right:1px solid var(--line)}
      .promo-card-wide .promo-banner img{width:100%;height:100%;max-width:none!important;max-height:none!important;object-fit:contain;padding:10px;background:#fff}
      .promo-banner-fallback{display:flex!important;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--red2),var(--red))!important;color:#fff!important;font:800 25px/1.2 Georgia,serif;text-align:center;padding:24px}
      .promo-wide-copy{display:flex!important;flex-direction:column;padding:22px 25px;color:inherit!important;min-width:0}
      .promo-wide-copy small{color:var(--red);font-weight:850;text-transform:uppercase;letter-spacing:.06em}
      .promo-wide-copy strong{font:700 28px/1.15 Georgia,serif;margin:6px 0;overflow-wrap:anywhere}
      .promo-wide-copy .promo-description{color:#53616a;flex:1;overflow-wrap:anywhere}
      .promo-wide-copy b{color:var(--red);margin-top:12px}
      .article-ad-auto{margin:48px 0}
      @media(max-width:700px){
        .promo-card-wide{grid-template-columns:1fr}
        .promo-card-wide .promo-banner{height:112px!important;min-height:112px;border-right:0;border-bottom:1px solid var(--line)}
        .promo-wide-copy strong{font-size:23px}
      }
    `;
    document.head.appendChild(style);
  }

  function ensureArticlePlacements(){
    const article=document.querySelector('article.article');
    if(!article)return;
    if(article.querySelector(':scope > [data-promos]'))return;
    const source=article.querySelector(':scope > .source-list');
    const candidates=[...article.children].filter(node=>{
      if(source&&node===source)return false;
      return node.matches('p,.numbers,.callout,.factcheck,blockquote,table,ul,ol,.scenario-grid');
    });
    if(candidates.length<3)return;
    const count=candidates.length>=10?3:2;
    const indexes=count===3
      ?[Math.floor(candidates.length*.28),Math.floor(candidates.length*.58),Math.floor(candidates.length*.82)]
      :[Math.floor(candidates.length*.38),Math.floor(candidates.length*.76)];
    indexes.reverse().forEach((candidateIndex,reverseIndex)=>{
      const target=candidates[Math.min(candidateIndex,candidates.length-1)];
      if(!target)return;
      const section=document.createElement('section');
      section.className='article-ad article-ad-auto';
      section.dataset.promos='';
      section.dataset.context=contextFromText(`${target.textContent||''} ${target.nextElementSibling?.textContent||''}`);
      const originalIndex=indexes.length-1-reverseIndex;
      section.dataset.layout=originalIndex%2===0?'banner':'feed';
      section.dataset.count=section.dataset.layout==='banner'?'1':'3';
      target.after(section);
    });
  }

  function renderBox(box,index){
    if(!(box instanceof Element)||box.dataset.promoRendered==='1')return;
    const context=box.dataset.context||'general';
    const layout=box.dataset.layout||(context==='sidebar'?'compact':'feed');
    const wide=layout==='banner';
    const count=Math.max(1,Number(box.dataset.count)||(context==='sidebar'||wide?1:3));
    const items=pick(context,count,index*7);
    const cards=items.map(item=>card(item,wide)).join('');
    box.innerHTML=`<div class="promo-label">REKLAMA</div><div class="promo-grid${context==='sidebar'?' promo-grid-compact':''}${wide?' promo-grid-banner':''}">${cards}</div>`;
    box.dataset.promoRendered='1';
    box.querySelectorAll('img').forEach(image=>{
      image.addEventListener('error',()=>{
        const banner=image.closest('.promo-banner');
        const promoCard=image.closest('.promo-card');
        if(!banner)return;
        if(promoCard?.classList.contains('promo-card-wide')){
          const title=promoCard.querySelector('strong')?.textContent||image.alt||'Reklama';
          banner.className='promo-banner promo-banner-fallback';
          banner.textContent=title;
        }else banner.remove();
      },{once:true});
    });
  }

  function renderAll(root=document){
    const boxes=[];
    if(root.matches?.('[data-promos]'))boxes.push(root);
    root.querySelectorAll?.('[data-promos]').forEach(box=>boxes.push(box));
    boxes.forEach((box,index)=>renderBox(box,index));
  }

  function start(){
    ensureStyles();
    ensureArticlePlacements();
    renderAll();
    new MutationObserver(records=>{
      for(const record of records){
        for(const node of record.addedNodes){
          if(node instanceof Element)renderAll(node);
        }
      }
    }).observe(document.body,{childList:true,subtree:true});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
