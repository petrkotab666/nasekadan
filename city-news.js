const cityNewsBox=document.querySelector('#city-news');
function esc(v){return String(v||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
if(cityNewsBox){fetch('/data/city-news.json?ts='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error();return r.json();}).then(data=>{
 const items=Array.isArray(data.items)?data.items.slice(0,18):[];
 if(!items.length){cityNewsBox.innerHTML='<p>Aktuálně není k dispozici žádná automaticky načtená novinka. Zdroje dál kontrolujeme.</p>';return;}
 cityNewsBox.innerHTML='<div class="source-list">'+items.map(x=>`<a href="${esc(x.source)}" target="_blank" rel="noopener"><small>${new Date(x.date).toLocaleDateString('cs-CZ')} · ${esc(x.category)}</small><br>${esc(x.title)}</a>`).join('')+'</div>';
 }).catch(()=>{cityNewsBox.innerHTML='<p>Automatický přehled se právě nepodařilo načíst. Ověřené články zůstávají dostupné na hlavní stránce.</p>';});}
