const MONTHS=['LED','ÚNO','BŘE','DUB','KVĚ','ČVN','ČVC','SRP','ZÁŘ','ŘÍJ','LIS','PRO'];
const grid=document.querySelector('#events');
function asDate(value){const d=new Date(value);return Number.isNaN(d.getTime())?null:d}
function dateParts(value){const d=asDate(value);return d?{day:String(d.getDate()).padStart(2,'0'),month:MONTHS[d.getMonth()]}:{day:'–',month:''}}
function fmtDate(value){const d=asDate(value);return d?d.toLocaleDateString('cs-CZ',{day:'numeric',month:'long',year:'numeric'}):''}
function escapeHtml(value){return String(value||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function isGenericSource(url){
 const value=String(url||'').toLowerCase().replace(/\/$/,'');
 return /\/redakce\/index\.php|\/cely-program$|\/akce\/mesto-kadan$|\/akce\/frantiskansky-klaster-kadan$|\/kultura$|\/aktivity\/galerie-josefa-lieslera$/.test(value);
}
function isDirectDetail(e){
 const value=String(e.source||'');
 if(!value||isGenericSource(value))return false;
 return /\/dre-cs\/|[?&]detail=\d+|\/akce\/[^/?#]+\/?$|\/detail(?:\/|$)|\/udalost(?:\/|$)|\/event(?:\/|$)/i.test(value);
}
function eventCard(e,now){
 const start=asDate(e.start),end=asDate(e.end),d=dateParts(e.start);
 const ongoing=start&&end&&start<=now&&end>=now;
 const dateLabel=ongoing?`Probíhá do ${fmtDate(e.end)}`:(end&&fmtDate(e.end)!==fmtDate(e.start)?`${fmtDate(e.start)} – ${fmtDate(e.end)}`:'');
 const status=e.verified?'Ověřený zdroj':'Čeká na ověření';
 const details=[e.place||'Kadaň',e.time,e.format].filter(Boolean).join(' · ');
 const direct=isDirectDetail(e);
 const linkText=direct?'Otevřít detail akce →':'Otevřít kalendář pořadatele →';
 return `<article class="event${e.category==='Kino'?' event-cinema':''}"><div class="date"><b>${ongoing?'DO':d.day}</b><span>${ongoing?dateParts(e.end).month:d.month}</span></div><div><span class="event-cat">${escapeHtml(e.category||'Akce')} · ${status}</span><h3>${escapeHtml(e.title)}</h3>${dateLabel?`<p class="event-range">${escapeHtml(dateLabel)}</p>`:''}<p class="event-meta">${escapeHtml(details)}</p><p>${escapeHtml(e.description||'Podrobnosti jsou na stránce pořadatele.')}</p>${e.price?`<p><b>Vstupné:</b> ${escapeHtml(e.price)}</p>`:''}<a href="${escapeHtml(e.source)}" target="_blank" rel="noopener">${linkText}</a></div></article>`;
}
function section(title,intro,events,now){if(!events.length)return '';return `<div class="events-group"><div class="events-group-head"><h3>${title}</h3><p>${intro}</p></div><div class="cards">${events.map(e=>eventCard(e,now)).join('')}</div></div>`}
function render(events,generatedAt){
 const now=new Date(),today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
 const current=events.filter(e=>{const end=asDate(e.end||e.start);return !end||end>=today}).sort((a,b)=>String(a.start).localeCompare(String(b.start)));
 const cinema=current.filter(e=>e.category==='Kino').slice(0,12);
 const culture=current.filter(e=>e.category!=='Kino').slice(0,18);
 if(!current.length){grid.innerHTML='<p>Aktuálně nemáme žádnou ověřenou budoucí akci. Tip můžete poslat na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p>';return;}
 grid.classList.add('events-root');
 grid.innerHTML=section('Kino Hvězda','Nejbližší projekce včetně času, jazykové verze a technického formátu.',cinema,now)+section('Kultura, výstavy, sport a komunitní akce','Jednodenní události i dlouhodobé výstavy. U probíhajících akcí uvádíme především datum ukončení.',culture,now);
 if(generatedAt)grid.insertAdjacentHTML('afterend',`<p class="events-updated">Kalendář naposledy automaticky zkontrolován: ${new Date(generatedAt).toLocaleString('cs-CZ')}.</p>`);
}
fetch('/data/events.json?ts='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error();return r.json()}).then(data=>render(Array.isArray(data.events)?data.events:[],data.generatedAt)).catch(()=>{grid.innerHTML='<p>Kalendář se právě nepodařilo načíst. Napište na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p>'});
