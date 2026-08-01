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

  // Ankety jsou obsluhované z externího skriptu, aby fungovaly i při blokování inline JavaScriptu.
  // Veřejná trasa /api/newsletter/* je v Caddy přesměrována na backend a prefix se odstraní.
  const pollEndpoint = '/api/newsletter/analytics/pageview';
  document.querySelectorAll('[data-poll-id]').forEach((section) => {
    if (section.dataset.pollBound === '1') return;
    section.dataset.pollBound = '1';

    const pollId = section.getAttribute('data-poll-id') || 'poll';
    const storageKey = `nk-poll-${pollId}`;
    const buttons = Array.from(section.querySelectorAll('[data-poll-vote]'));
    const message = section.querySelector('.poll-message');
    let sending = false;

    const setMessage = (text, type = 'success') => {
      if (!message) return;
      message.textContent = text;
      message.style.background = type === 'error' ? '#fff0f0' : '#eaf4ed';
      message.style.color = type === 'error' ? '#8e2525' : '#245d36';
      message.classList.add('show');
    };

    const setLocked = (vote) => {
      buttons.forEach((button) => {
        button.disabled = true;
        if (button.getAttribute('data-poll-vote') === vote) {
          button.style.borderColor = '#9f2626';
          button.style.background = '#fff4f4';
        }
      });
    };

    const setUnlocked = () => {
      buttons.forEach((button) => {
        button.disabled = false;
        button.style.borderColor = '';
        button.style.background = '';
      });
    };

    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        setLocked(saved);
        setMessage('Děkujeme, váš hlas už byl zaznamenán.');
      }
    } catch (_) {}

    buttons.forEach((button) => {
      button.addEventListener('click', async (event) => {
        // Zachytávací posluchač zároveň zastaví starší vložený skript v článku,
        // aby se jeden hlas neodeslal dvakrát.
        event.preventDefault();
        event.stopImmediatePropagation();
        if (sending) return;

        let saved = '';
        try { saved = localStorage.getItem(storageKey) || ''; } catch (_) {}
        if (saved) {
          setLocked(saved);
          setMessage('Děkujeme, váš hlas už byl zaznamenán.');
          return;
        }

        const vote = button.getAttribute('data-poll-vote');
        if (!vote) return;

        sending = true;
        setLocked(vote);
        setMessage('Odesíláme váš hlas…');

        const payload = {
          path: `/anketa/${pollId}/${vote}`,
          title: `Anketa ${pollId}: ${vote}`,
          referrer: location.pathname,
        };
        const body = JSON.stringify(payload);
        let recorded = false;

        try {
          const response = await fetch(pollEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body,
            keepalive: true,
            credentials: 'same-origin',
          });
          recorded = response.ok;
        } catch (_) {}

        if (!recorded && navigator.sendBeacon) {
          try {
            recorded = navigator.sendBeacon(
              pollEndpoint,
              new Blob([body], { type: 'application/json' }),
            );
          } catch (_) {}
        }

        if (recorded) {
          try { localStorage.setItem(storageKey, vote); } catch (_) {}
          setMessage('Děkujeme, váš hlas byl zaznamenán.');
        } else {
          setUnlocked();
          setMessage('Hlas se nyní nepodařilo odeslat. Zkuste to prosím znovu.', 'error');
        }
        sending = false;
      }, true);
    });
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
