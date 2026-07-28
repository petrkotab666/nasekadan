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

  document.querySelectorAll('.head').forEach((head) => {
    const nav = head.querySelector('nav');
    if (!nav || head.querySelector('.menu-toggle')) return;

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
