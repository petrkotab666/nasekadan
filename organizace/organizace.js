const root=document.querySelector('#organization-groups');
const esc=v=>String(v||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
fetch('/data/organizations.json?ts='+Date.now(),{cache:'no-store'})
 .then(r=>{if(!r.ok)throw new Error('Adresář není dostupný');return r.json();})
 .then(data=>{
   root.innerHTML=(data.groups||[]).map(group=>`<section class="group"><h2>${esc(group.name)}</h2><div class="grid">${(group.items||[]).map(item=>`<article class="card"><h3>${esc(item.name)}</h3><p>${esc(item.description)}</p><a href="${esc(item.url)}" target="_blank" rel="noopener">Otevřít oficiální web →</a></article>`).join('')}</div></section>`).join('');
 })
 .catch(()=>{root.innerHTML='<p>Adresář se nepodařilo načíst. Opravu můžete nahlásit na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p>';});
