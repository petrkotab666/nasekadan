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
