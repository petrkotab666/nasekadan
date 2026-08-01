// Společné bezpečné chování webu. Tento soubor nesmí měnit pořadí článků,
// titulní hero ani redakční texty.
document.addEventListener('DOMContentLoaded', () => {
  if (!document.querySelector('link[data-mobile-css]')) {
    const mobile = document.createElement('link');
    mobile.rel = 'stylesheet';
    mobile.href = '/mobile.css?v=20260728-stable-1';
    mobile.setAttribute('data-mobile-css', 'true');
    document.head.appendChild(mobile);
  }

  const canonicalNav = [
    ['/clanky/', 'Články'],
    ['/#akce', 'Akce'],
    ['/pruvodce/', 'Průvodce'],
    ['/zapojte-se/', 'Poslat tip'],
  ];

  document.querySelectorAll('.head').forEach((head) => {
    let nav = head.querySelector('nav');
    if (!nav) {
      nav = document.createElement('nav');
      const logo = head.querySelector('.logo');
      if (logo) logo.after(nav);
      else head.prepend(nav);
    }

    nav.setAttribute('aria-label', 'Hlavní navigace');
    nav.innerHTML = canonicalNav
      .map(([href, label]) => `<a href="${href}">${label}</a>`)
      .join('');

    const path = location.pathname;
    nav.querySelectorAll('a').forEach((link) => {
      const href = link.getAttribute('href') || '';
      const active =
        (href === '/clanky/' && path.startsWith('/clanky/')) ||
        (href === '/pruvodce/' && path.startsWith('/pruvodce/')) ||
        (href === '/zapojte-se/' && path.startsWith('/zapojte-se/')) ||
        (href === '/#akce' && path === '/' && location.hash === '#akce');
      if (active) link.setAttribute('aria-current', 'page');
    });

    if (head.querySelector('.menu-toggle')) return;

    const button = document.createElement('button');
    button.className = 'menu-toggle';
    button.type = 'button';
    button.setAttribute('aria-label', 'Otevřít hlavní menu');
    button.setAttribute('aria-expanded', 'false');
    button.innerHTML = '<span></span><span></span><span></span>';
    button.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      button.classList.toggle('is-open', open);
      button.setAttribute('aria-expanded', String(open));
      button.setAttribute('aria-label', open ? 'Zavřít hlavní menu' : 'Otevřít hlavní menu');
    });
    head.appendChild(button);
  });

  // Ankety Naše Kadaň: samostatné ukládání hlasů a veřejné průběžné výsledky.
  const pollVoteEndpoint = '/api/newsletter/poll/vote';
  const pollResultsEndpoint = '/api/newsletter/poll/results';

  if (!document.getElementById('nk-poll-results-style')) {
    const style = document.createElement('style');
    style.id = 'nk-poll-results-style';
    style.textContent = `
      .poll-results{display:block;margin-top:20px;padding-top:18px;border-top:1px solid #d9e0e3}
      .poll-results-head{display:flex;justify-content:space-between;gap:16px;align-items:baseline;margin-bottom:13px;color:#20313a}
      .poll-results-head strong{font:800 20px Georgia,serif}
      .poll-results-total{font-size:13px;color:#667780;font-weight:800}
      .poll-result-row{margin:0 0 13px}
      .poll-result-meta{display:flex;justify-content:space-between;gap:14px;margin-bottom:5px;font-size:14px;line-height:1.4}
      .poll-result-label{color:#20313a;font-weight:800}
      .poll-result-value{color:#667780;white-space:nowrap;font-weight:800}
      .poll-result-track{height:11px;overflow:hidden;border-radius:999px;background:#e7ecee}
      .poll-result-fill{height:100%;width:0;border-radius:inherit;background:#9f2626;transition:width .35s ease}
      .poll-results-status{margin:8px 0 0!important;color:#73818a;font-size:12px!important}
      .poll-results-error{color:#8e2525!important}
      /* POLL_GREENERY_HIGH_CONTRAST_V4: tmavá anketa potřebuje světlý text. */
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results{background:rgba(3,18,27,.30);border:1px solid rgba(255,255,255,.30);border-radius:16px;padding:18px 18px 14px}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-head,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-head strong,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-label{color:#ffffff!important;text-shadow:0 1px 2px rgba(0,0,0,.35)}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-total,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-value,
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-results-status{color:#eef8fb!important;font-weight:800}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-track{background:#f5f8f9;box-shadow:0 0 0 1px rgba(255,255,255,.65)}
      [data-poll-id="sekani-travniku-kadan-2026"] .poll-result-fill{background:#d92f38}
    `;
    document.head.appendChild(style);
  }

  document.querySelectorAll('[data-poll-id]').forEach((section) => {
    if (section.dataset.pollBound === '2') return;
    section.dataset.pollBound = '2';
    const pollId = section.getAttribute('data-poll-id') || 'poll';
    const storageKey = `nk-poll-${pollId}`;
    const buttons = Array.from(section.querySelectorAll('[data-poll-vote]'));
    const message = section.querySelector('.poll-message');
    const options = section.querySelector('.poll-options');
    let sending = false;
    const choices = buttons.map((button) => ({key: button.getAttribute('data-poll-vote') || '',label: (button.textContent || '').trim()})).filter((item) => item.key);

    const results = document.createElement('div');
    results.className = 'poll-results';
    results.setAttribute('aria-live', 'polite');
    results.innerHTML = `<div class="poll-results-head"><strong>Průběžné výsledky</strong><span class="poll-results-total" data-poll-total>Načítáme…</span></div>${choices.map((item) => `<div class="poll-result-row" data-poll-result="${item.key}"><div class="poll-result-meta"><span class="poll-result-label">${item.label}</span><span class="poll-result-value">0 hlasů · 0 %</span></div><div class="poll-result-track"><div class="poll-result-fill"></div></div></div>`).join('')}<p class="poll-results-status">Načítáme aktuální počet hlasů…</p>`;
    if (options) options.after(results); else section.appendChild(results);

    const setMessage = (value, type = 'success') => {
      if (!message) return;
      message.textContent = value;
      message.style.background = type === 'error' ? '#fff0f0' : '#eaf4ed';
      message.style.color = type === 'error' ? '#8e2525' : '#245d36';
      message.classList.add('show');
    };
    const setLocked = (vote) => {
      buttons.forEach((button) => {
        button.disabled = true;
        const selected = button.getAttribute('data-poll-vote') === vote;
        button.style.borderColor = selected ? '#9f2626' : '';
        button.style.background = selected ? '#fff4f4' : '';
        button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
    };
    const setUnlocked = () => buttons.forEach((button) => {button.disabled=false;button.style.borderColor='';button.style.background='';button.setAttribute('aria-pressed','false');});
    const voteWord = (count) => count === 1 ? 'hlas' : (count >= 2 && count <= 4 ? 'hlasy' : 'hlasů');

    const renderResults = (payload) => {
      const counts = payload && payload.counts ? payload.counts : {};
      const percentages = payload && payload.percentages ? payload.percentages : {};
      const total = Number(payload && payload.total) || 0;
      const totalEl = results.querySelector('[data-poll-total]');
      if (totalEl) totalEl.textContent = `${total} ${voteWord(total)} celkem`;
      choices.forEach((item) => {
        const count = Number(counts[item.key]) || 0;
        const percent = Number.isFinite(Number(percentages[item.key])) ? Number(percentages[item.key]) : (total > 0 ? Math.round((count / total) * 1000) / 10 : 0);
        const row = results.querySelector(`[data-poll-result="${item.key}"]`);
        if (!row) return;
        const value = row.querySelector('.poll-result-value');
        const fill = row.querySelector('.poll-result-fill');
        if (value) value.textContent = `${count} ${voteWord(count)} · ${String(percent).replace('.', ',')} %`;
        if (fill) fill.style.width = `${Math.max(0,Math.min(100,percent))}%`;
      });
      const status = results.querySelector('.poll-results-status');
      if (status) {status.classList.remove('poll-results-error');status.textContent = total > 0 ? 'Výsledky se aktualizují průběžně.' : 'Zatím nebyl odevzdán žádný hlas.';}
      // POLL_SERVER_AUTHORITATIVE_V3: cookie a databáze jsou jediný zdroj pravdy.
      if (payload && payload.selected) {
        try { localStorage.setItem(storageKey, payload.selected); } catch (_) {}
        setLocked(payload.selected);
        setMessage('Děkujeme, váš hlas už byl zaznamenán.');
      } else {
        // Starší nefunkční anketa mohla uložit pouze localStorage bez serverového hlasu.
        // Takový záznam nesmí blokovat nové hlasování.
        try { localStorage.removeItem(storageKey); } catch (_) {}
        setUnlocked();
        if (message && /Ověřujeme dřívější hlas|už byl zaznamenán/.test(message.textContent || '')) {
          message.classList.remove('show');
        }
      }
    };

    const loadResults = async () => {
      try {
        const response = await fetch(`${pollResultsEndpoint}?poll=${encodeURIComponent(pollId)}&t=${Date.now()}`, {method:'GET',cache:'no-store',credentials:'same-origin'});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        if (!payload || payload.ok !== true) throw new Error('invalid_payload');
        renderResults(payload);
      } catch (_) {
        const status = results.querySelector('.poll-results-status');
        if (status) {status.textContent='Výsledky se nyní nepodařilo načíst. Hlasování můžete zkusit znovu za chvíli.';status.classList.add('poll-results-error');}
        const totalEl = results.querySelector('[data-poll-total]');
        if (totalEl) totalEl.textContent='Dočasně nedostupné';
      }
    };

    // Lokální záznam je pouze nápověda; tlačítka uzamkne až potvrzení serveru.
    try {
      if (localStorage.getItem(storageKey)) setMessage('Ověřujeme dřívější hlas…');
    } catch (_) {}
    loadResults();

    buttons.forEach((button) => {
      button.addEventListener('click', async (event) => {
        event.preventDefault();event.stopImmediatePropagation();
        if (sending) return;
        // Hlas vždy posíláme serveru. Duplicitní hlas bezpečně odmítne databáze podle cookie.
        const vote=button.getAttribute('data-poll-vote');if(!vote)return;
        sending=true;setLocked(vote);setMessage('Odesíláme váš hlas…');
        try{
          const response=await fetch(pollVoteEndpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pollId,choice:vote}),keepalive:true,credentials:'same-origin'});
          const payload=await response.json().catch(()=>null);
          if(!response.ok||!payload||payload.ok!==true)throw new Error(`HTTP ${response.status}`);
          const selected=payload.selected||vote;try{localStorage.setItem(storageKey,selected);}catch(_){}
          setLocked(selected);setMessage(payload.accepted===false?'Z tohoto zařízení už byl hlas zaznamenán. Zobrazujeme aktuální výsledky.':'Děkujeme, váš hlas byl zaznamenán.');renderResults(payload);
        }catch(_){setUnlocked();setMessage('Hlas se nyní nepodařilo odeslat. Zkuste to prosím znovu.','error');await loadResults();}
        sending=false;
      }, true);
    });
    window.setInterval(() => {if(!document.hidden)loadResults();},20000);
  });

  // U článků se statickými reklamami se žádný starý dynamický reklamní skript nenačítá.
  const articleShell = document.querySelector('main.article-shell');
  if (articleShell && !document.querySelector('.static-article-ads') && !document.querySelector('script[data-article-adstream]')) {
    const adstream = document.createElement('script');
    adstream.src = '/reklamy-sidebar.js?v=20260728-fallback-1';
    adstream.async = true;
    adstream.setAttribute('data-article-adstream', 'true');
    document.head.appendChild(adstream);
  }
});
