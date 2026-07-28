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
if(grid){fetch('/data/events.json?ts='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error();return r.json()}).then(data=>render(Array.isArray(data.events)?data.events:[],data.generatedAt)).catch(()=>{grid.innerHTML='<p>Kalendář se právě nepodařilo načíst. Napište na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p>'});}

(function enforceHomepageOrder(){
 const path=location.pathname.replace(/\/+$/,'');
 if(path!==''&&path!=='/index.html')return;
 const hero=document.querySelector('section.hero');
 if(hero){
   const lead=hero.querySelector('.lead');
   if(lead){
     lead.setAttribute('data-arc-med-hero','');
     lead.removeAttribute('data-weekly-events-hero');
     lead.innerHTML=`<div class="photo" style="background:linear-gradient(135deg,#132630,#3f6576 58%,#a9232b)"><span>ZDRAVOTNICTVÍ</span><strong>ARC-MED</strong></div><div class="copy"><small>VEŘEJNÉ PENÍZE · 28. 07. 2026 · 5:00</small><h1>ARC-MED za 16 milionů: dva posudky, nejasné schválení a spor o dvanáct milionů</h1><p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p><a class="btn" href="/clanky/arc-med-nemocnice-kadan.html">Přečíst celý článek →</a></div>`;
   }
   const aside=hero.querySelector('.current-aside');
   if(aside)aside.innerHTML=`<p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p><p class="aside-date">27. 7. 2026 v 22:35</p><h2>Kadaňští hasiči cvičili na Nechranicích záchranu lidí z vody</h2><p>Společný výcvik prověřil práci člunů i součinnost záchranných složek.</p><a class="aside-button" href="/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html">Přečíst článek →</a><div class="aside-links"><a href="/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html">82 lůžek z Kadaně pro Ukrajinu</a><a href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Kulturní přehled na tento týden</a><a href="/clanky/">Všechny články podle data</a></div>`;
 }
 const list=document.querySelector('.article-list');
 if(!list)return;
 const cards={
   arc:`<article class="article-card hospital" data-arc-med-card><div class="visual" style="background:linear-gradient(135deg,#132630,#3f6576 58%,#a9232b)"><strong>ARC-MED za 16 milionů</strong></div><div class="article-body"><span class="meta">28. 7. 2026 · 5:00 · Zdravotnictví a veřejné peníze</span><h3>Dva posudky, nejasné schválení a spor o dvanáct milionů</h3><p>Co nemocnice skutečně koupila, proč se ocenění rozcházejí a co zatím nelze doložit.</p><a class="read-more" href="/clanky/arc-med-nemocnice-kadan.html">Přečíst článek →</a></div></article>`,
   fire:`<article class="article-card transport" data-nechranice-card><div class="visual" style="background:linear-gradient(135deg,#12313f,#28617a 58%,#a56b24)"><strong>Záchrana na vodě</strong></div><div class="article-body"><span class="meta">27. 7. 2026 · 22:35 · Hasiči</span><h3>Kadaňští hasiči cvičili na Nechranicích</h3><p>Společný výcvik prověřil práci člunů i součinnost záchranných složek.</p><a class="read-more" href="/clanky/hasici-kadan-vycvik-zachrana-voda-nechranice.html">Přečíst článek →</a></div></article>`,
   beds:`<article class="article-card hospital" data-beds-card><div class="visual" style="background:linear-gradient(135deg,#142b37,#36586a 58%,#9d222a)"><strong>82 lůžek pro Ukrajinu</strong></div><div class="article-body"><span class="meta">27. 7. 2026 · 21:40 · Nemocnice Kadaň</span><h3>Z Kadaně až k frontové linii</h3><p>Funkční nemocniční postele dostaly druhou šanci tam, kde jsou mimořádně potřebné.</p><a class="read-more" href="/clanky/nemocnice-kadan-darovala-82-luzek-ukrajine.html">Přečíst článek →</a></div></article>`,
   culture:`<article class="article-card events" data-weekly-events-card><div class="visual" style="background:linear-gradient(135deg,#143342,#39748a 58%,#b58b25)"><strong>Kam příští týden</strong></div><div class="article-body"><span class="meta">26. 07. 2026 · 12:00 · Kultura a volný čas</span><h3>Kam v Kadani a okolí od 27. července do 2. srpna</h3><p>Živá hudba na Liďáku, festival čaje, kino, koupaliště, historický vlak a galakoncert.</p><a class="read-more" href="/clanky/kam-v-kadani-a-okoli-27-cervence-2-srpna-2026.html">Otevřít celý přehled →</a></div></article>`
 };
 list.querySelectorAll('[data-arc-med-card],[data-nechranice-card],[data-beds-card],[data-weekly-events-card]').forEach(node=>node.remove());
 list.insertAdjacentHTML('afterbegin',cards.arc+cards.fire+cards.beds+cards.culture);
})();
