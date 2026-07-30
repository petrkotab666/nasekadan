const root = document.querySelector('#organization-groups');
const searchInput = document.querySelector('#organization-search');
const countNode = document.querySelector('#organization-count');

const esc = value => String(value || '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

let directory = { groups: [] };

function normalize(value) {
  return String(value || '')
    .toLocaleLowerCase('cs-CZ')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function render(query = '') {
  const needle = normalize(query.trim());
  let visibleCount = 0;

  const groups = (directory.groups || []).map(group => {
    const items = (group.items || []).filter(item => {
      if (!needle) return true;
      return normalize([
        item.name,
        item.description,
        item.address,
        group.name
      ].join(' ')).includes(needle);
    });

    if (!items.length) return '';
    visibleCount += items.length;

    return `<section class="group">
      <div class="group-heading">
        <h2>${esc(group.name)}</h2>
        <span>${items.length} ${items.length === 1 ? 'položka' : items.length < 5 ? 'položky' : 'položek'}</span>
      </div>
      <div class="grid">
        ${items.map(item => {
          const meta = [
            item.address ? `<span class="organization-meta">📍 ${esc(item.address)}</span>` : '',
            item.phone ? `<span class="organization-meta">☎ ${esc(item.phone)}</span>` : '',
            item.email ? `<span class="organization-meta">✉ ${esc(item.email)}</span>` : ''
          ].filter(Boolean).join('');

          return `<article class="card">
            <h3>${esc(item.name)}</h3>
            <p>${esc(item.description)}</p>
            ${meta ? `<div class="organization-details">${meta}</div>` : ''}
            <a href="${esc(item.url)}" target="_blank" rel="noopener noreferrer">${esc(item.linkLabel || 'Otevřít oficiální web')} →</a>
          </article>`;
        }).join('')}
      </div>
    </section>`;
  }).join('');

  root.innerHTML = groups || '<div class="empty-result"><strong>Žádná odpovídající organizace nebyla nalezena.</strong><p>Zkuste jiný název, obor nebo část adresy.</p></div>';
  if (countNode) countNode.textContent = needle
    ? `Nalezeno ${visibleCount} z ${directory.totalCount || 0} organizací a institucí.`
    : `Adresář obsahuje ${directory.totalCount || visibleCount} organizací a institucí v ${directory.groups?.length || 0} oblastech.`;
}

fetch('/data/organizations.json?ts=' + Date.now(), { cache: 'no-store' })
  .then(response => {
    if (!response.ok) throw new Error('Adresář není dostupný');
    return response.json();
  })
  .then(data => {
    directory = data;
    directory.totalCount = (data.groups || []).reduce((sum, group) => sum + (group.items || []).length, 0);
    render(searchInput?.value || '');
  })
  .catch(() => {
    root.innerHTML = '<div class="empty-result"><strong>Adresář se nepodařilo načíst.</strong><p>Opravu můžete nahlásit na <a href="mailto:info@nasekadan.cz">info@nasekadan.cz</a>.</p></div>';
    if (countNode) countNode.textContent = 'Adresář je dočasně nedostupný.';
  });

searchInput?.addEventListener('input', event => render(event.target.value));
