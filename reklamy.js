const promoItems=[
  {title:'Pojistime.to',text:'Srovnání pojištění auta, domácnosti, cestování a dalších rizik na jednom místě.',url:'https://pojistime.to',tag:'Pojištění'},
  {title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a širokém okolí.',url:'https://vyklidime.to',tag:'Místní služba'},
  {title:'Vaše uklízečka',text:'Úklid domácností, firem, kanceláří a bytových domů na Kadaňsku.',url:'https://vaseuklizecka.cz',tag:'Místní služba'},
  {title:'Haffit',text:'Krmivo pro psy připravené na míru podle potřeb konkrétního psa.',url:'https://www.haffit.cz/?a_box=cbhtyjjm&a_cam=1',tag:'Pro chovatele'},
  {title:'Zonky půjčka',text:'Online půjčka od Zonky s přehledným vyřízením a možností předčasného splacení.',url:'https://www.zonky.cz/pujcka-od-zonky/?a_box=s8m27mmy',tag:'Finance'}
];

function renderPromos(){
  document.querySelectorAll('[data-promos]').forEach((box,i)=>{
    const count=box.dataset.count?Number(box.dataset.count):3;
    const shift=(i*2)%promoItems.length;
    const ordered=[...promoItems.slice(shift),...promoItems.slice(0,shift)].slice(0,count);
    box.innerHTML='<div class="promo-label">REKLAMA</div><div class="promo-grid">'+ordered.map(x=>`<a class="promo-card" href="${x.url}" target="_blank" rel="sponsored noopener"><small>${x.tag}</small><strong>${x.title}</strong><span>${x.text}</span><b>Zjistit více →</b></a>`).join('')+'</div>';
  });
}

document.addEventListener('DOMContentLoaded',renderPromos);
