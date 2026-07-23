const promoItems=[
{label:'Naše služba',title:'Reality Kadaň',text:'Odhad, prodej a výkup nemovitostí v Kadani a okolí.',url:'https://realitykadan.cz'},
{label:'Naše služba',title:'VYKLIDIME.TO',text:'Vyklízení bytů, domů, sklepů a pozůstalostí v Kadani a okolí.',url:'https://vyklidime.to'},
{label:'Naše služba',title:'Vaše uklízečka',text:'Úklid domácností, firem a bytových domů v Kadani.',url:'https://vaseuklizecka.cz'},
{label:'Naše služba',title:'Díly na zakázku',text:'3D skenování, modelování a výroba dílů na zakázku.',url:'https://dilynazakazku.cz'},
{label:'Partner',title:'Airalo eSIM',text:'Datová eSIM pro cestování bez drahého roamingu.',url:'https://airalo.pxf.io/c/7478089/1268485/15608'},
{label:'Partner',title:'Haffit',text:'Krmivo připravené na míru konkrétnímu psovi.',url:'https://www.haffit.cz/?a_box=cbhtyjjm&a_cam=1'}
];
function renderPromos(){document.querySelectorAll('[data-promos]').forEach((box,i)=>{const items=[promoItems[i%promoItems.length],promoItems[(i+1)%promoItems.length],promoItems[(i+2)%promoItems.length]];box.innerHTML='<div class="promo-label">REKLAMA</div><div class="promo-grid">'+items.map(x=>`<a class="promo-card" href="${x.url}" target="_blank" rel="sponsored noopener"><small>${x.label}</small><strong>${x.title}</strong><span>${x.text}</span><b>Zjistit více →</b></a>`).join('')+'</div>';});}document.addEventListener('DOMContentLoaded',renderPromos);