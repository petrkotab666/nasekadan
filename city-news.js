const cityNewsBox=document.querySelector('#city-news');
const cityNewsFallback={generatedAt:'2026-07-29T04:20:00Z',items:[
 {title:'Musíme si pomáhat: Nemocnice Kadaň darovala 82 lůžek na Ukrajinu',date:'2026-07-27',category:'Zdravotnictví',source:'https://www.nemkadan.cz/pro-verejnost/verejnost/aktuality/musime-si-pomahat-948cs.html',sourceName:'Nemocnice Kadaň'},
 {title:'Kino Hvězda zveřejnilo program na konec července a začátek srpna',date:'2026-07-26',category:'Kino',source:'https://www.kinokadan.cz/cely-program',sourceName:'Kino Hvězda'},
 {title:'RADKA připravuje mezinárodní výměnu mládeže Beyond Labels',date:'2026-08-02',category:'Komunita a mládež',source:'https://radka.kadan.cz/udalosti/vymena-mladeze-beyond-labels/',sourceName:'RADKA Kadaň'}
]};
function esc(v){return String(v||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function cityNewsDate(v){if(!v)return 'Datum neuvedeno';const d=new Date(`${v}T12:00:00`);return Number.isNaN(d.getTime())?'Datum neuvedeno':d.toLocaleDateString('cs-CZ');}
function renderCityNews(data,isFallback=false){
 const items=Array.isArray(data&&data.items)?data.items.slice(0,18):[];
 if(!items.length){cityNewsBox.innerHTML='<p>Aktuálně není k dispozici žádná automaticky načtená novinka. Zdroje dál kontrolujeme.</p>';return;}
 const note=isFallback?'<p class="events-updated"><strong>Záložní režim:</strong> zobrazujeme poslední ověřené položky, než se obnoví automatické načítání.</p>':'';
 const generated=data&&data.generatedAt?new Date(data.generatedAt):null;
 const updated=generated&&!Number.isNaN(generated.getTime())?`<p class="events-updated">Přehled naposledy aktualizován: ${generated.toLocaleString('cs-CZ')}.</p>`:'';
 cityNewsBox.innerHTML=note+'<div class="source-list">'+items.map(x=>`<a href="${esc(x.source)}" target="_blank" rel="noopener"><small>${cityNewsDate(x.date)} · ${esc(x.category)}${x.sourceName?` · ${esc(x.sourceName)}`:''}</small><br>${esc(x.title)}</a>`).join('')+'</div>'+updated;
}
if(cityNewsBox){fetch('/data/city-news.json?ts='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json();}).then(data=>renderCityNews(data,false)).catch(()=>renderCityNews(cityNewsFallback,true));}
