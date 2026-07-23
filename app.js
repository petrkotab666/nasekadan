const MONTHS=['LED','ÚNO','BŘE','DUB','KVĚ','ČVN','ČVC','SRP','ZÁŘ','ŘÍ','LIS','PRO'];
const grid=document.querySelector('#events');

function dateParts(value){
  const date=new Date(value);
  if(Number.isNaN(date.getTime())) return {day:'–',month:''};
  return {day:String(date.getDate()).padStart(2,'0'),month:MONTHS[date.getMonth()]};
}
function escapeHtml(value){return String(value||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function render(events,generatedAt){
  const now=new Date();
  const upcoming=events.filter(e=>{
    const end=new Date(e.end||e.start);
    return Number.isNaN(end.getTime())||end>=new Date(now.getFullYear(),now.getMonth(),now.getDate()-1);
  }).slice(0,9);
  if(!upcoming.length){grid.innerHTML='<p>Aktuálně nemáme žádnou ověřenou budoucí akci. Tip můžete poslat na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p>';return;}
  grid.innerHTML=upcoming.map(e=>{
    const d=dateParts(e.start);
    const status=e.verified?'Ověřený zdroj':'Čeká na ověření';
    return `<article class="event"><div class="date"><b>${d.day}</b><span>${d.month}</span></div><div><span class="event-cat">${escapeHtml(e.category||'Akce')} · ${status}</span><h3>${escapeHtml(e.title)}</h3><p class="event-meta">${escapeHtml(e.place||'Kadaň')}${e.time?' · '+escapeHtml(e.time):''}</p><p>${escapeHtml(e.description||'Podrobnosti jsou na stránce pořadatele.')}</p>${e.price?`<p><b>Vstupné:</b> ${escapeHtml(e.price)}</p>`:''}<a href="${escapeHtml(e.source)}" target="_blank" rel="noopener">Podrobnosti a aktuální stav →</a></div></article>`;
  }).join('');
  if(generatedAt){grid.insertAdjacentHTML('afterend',`<p class="events-updated">Kalendář naposledy automaticky zkontrolován: ${new Date(generatedAt).toLocaleString('cs-CZ')}.</p>`);}
}

fetch('/data/events.json?ts='+Date.now(),{cache:'no-store'})
  .then(r=>{if(!r.ok) throw new Error('Kalendář není dostupný');return r.json();})
  .then(data=>render(Array.isArray(data.events)?data.events:[],data.generatedAt))
  .catch(()=>{grid.innerHTML='<p>Kalendář se právě nepodařilo načíst. Aktuální program ověřte na stránkách pořadatelů nebo napište na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p>';});
