const promoItems=[
  {label:'Náš projekt',title:'Pojistime.to',text:'Přehledné pojištění auta, domácnosti, cestování i dalších životních situací.',url:'https://pojistime.to'},
  {label:'Místní služba',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a okolí.',url:'https://vyklidime.to'},
  {label:'Místní služba',title:'Vaše uklízečka',text:'Úklid domácností, firem a bytových domů v Kadani a na Kadaňsku.',url:'https://vaseuklizecka.cz'}
];

// LastMinuteSlevy.cz se přidá až po dokončení opravy webu.
// DilyNaZakazku.cz je záměrně vypnuté do dokončení projektu.
// RealityKadan.cz zůstává samostatný projekt bez křížové propagace.

function renderPromos(){
  document.querySelectorAll('[data-promos]').forEach((box,i)=>{
    const shift=i%promoItems.length;
    const items=[...promoItems.slice(shift),...promoItems.slice(0,shift)];
    box.innerHTML='<div class="promo-label">REKLAMA</div><div class="promo-grid">'+items.map(x=>`<a class="promo-card" href="${x.url}" target="_blank" rel="sponsored noopener"><small>${x.label}</small><strong>${x.title}</strong><span>${x.text}</span><b>Zjistit více →</b></a>`).join('')+'</div>';
  });
}

document.addEventListener('DOMContentLoaded',renderPromos);
