const promoItems=[
  {title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',tag:'Pojištění',contexts:['finance','home','travel','sidebar','general']},
  {title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',tag:'Služby',contexts:['home','sidebar','general']},
  {title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',tag:'Služby',contexts:['home','sidebar','general']},
  {title:'Haffit',text:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',url:'https://www.haffit.cz/?a_box=cbhtyjjm&a_cam=1',tag:'Pro chovatele',contexts:['home','general']},
  {title:'Zonky půjčka',text:'Online půjčka od Zonky s přehledným vyřízením a možností předčasného splacení.',url:'https://www.zonky.cz/pujcka-od-zonky/?a_box=s8m27mmy',tag:'Finance',contexts:['finance','home','general']}
];

function pickPromos(context,count,offset){
  const exact=promoItems.filter(x=>x.contexts.includes(context));
  const fallback=promoItems.filter(x=>!exact.includes(x));
  const pool=[...exact,...fallback];
  const shifted=[...pool.slice(offset%pool.length),...pool.slice(0,offset%pool.length)];
  return shifted.slice(0,count);
}

function renderPromos(){
  document.querySelectorAll('[data-promos]').forEach((box,i)=>{
    const context=box.dataset.context||'general';
    const count=box.dataset.count?Number(box.dataset.count):(context==='sidebar'?1:3);
    const items=pickPromos(context,count,i*2);
    const compact=context==='sidebar'?' promo-grid-compact':'';
    box.innerHTML='<div class="promo-label">REKLAMA</div><div class="promo-grid'+compact+'">'+items.map(x=>`<a class="promo-card" href="${x.url}" target="_blank" rel="sponsored noopener"><small>${x.tag}</small><strong>${x.title}</strong><span>${x.text}</span><b>Zjistit více →</b></a>`).join('')+'</div>';
  });
}

document.addEventListener('DOMContentLoaded',renderPromos);
