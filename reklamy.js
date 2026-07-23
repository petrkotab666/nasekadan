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

function hashSeed(value){return [...String(value)].reduce((sum,char)=>((sum*31)+char.charCodeAt(0))>>>0,0)}
function pickPromos(context,count,offset){
  const exact=promoItems.filter(x=>x.contexts.includes(context));
  const fallback=promoItems.filter(x=>!exact.includes(x));
  const pool=[...exact,...fallback];
  const day=new Date().toISOString().slice(0,10);
  const shift=(hashSeed(location.pathname+day)+offset)%pool.length;
  return [...pool.slice(shift),...pool.slice(0,shift)].slice(0,count);
}
function renderPromos(){
  document.querySelectorAll('[data-promos]').forEach((box,i)=>{
    const context=box.dataset.context||'general';
    const count=box.dataset.count?Number(box.dataset.count):(context==='sidebar'?1:3);
    const items=pickPromos(context,count,i*3);
    const compact=context==='sidebar'?' promo-grid-compact':'';
    box.innerHTML='<div class="promo-label">REKLAMA</div><div class="promo-grid'+compact+'">'+items.map(x=>`<a class="promo-card" href="${x.url}" target="_blank" rel="nofollow sponsored noopener noreferrer">${x.banner?`<span class="promo-banner"><img src="${x.banner}" alt="${x.title}" loading="lazy"></span>`:''}<small>${x.tag}</small><strong>${x.title}</strong><span>${x.text}</span><b>Zjistit více →</b></a>`).join('')+'</div>';
  });
}
document.addEventListener('DOMContentLoaded',renderPromos);
