import fs from 'node:fs';
import { JSDOM } from 'jsdom';

const html = `<!doctype html><html><head></head><body>
<section class="poll" data-poll-id="sekani-travniku-kadan-2026">
  <div class="poll-options">
    <button type="button" data-poll-vote="soucasny-rezim">Současný způsob sečení mi vyhovuje.</button>
    <button type="button" data-poll-vote="mene-casto-vyse">Méně často a výše.</button>
  </div>
  <p class="poll-message">Děkujeme, váš hlas byl zaznamenán.</p>
</section>
</body></html>`;

const dom = new JSDOM(html, {
  url: 'https://nasekadan.cz/clanky/sekani-travniku-kadan-spravci-vysky-2026.html',
  runScripts: 'outside-only',
  pretendToBeVisual: true,
});
const { window } = dom;
window.localStorage.setItem('nk-poll-sekani-travniku-kadan-2026', 'mene-casto-vyse');
let posts = 0;
window.fetch = async (url, options = {}) => {
  const method = String(options.method || 'GET').toUpperCase();
  if (method === 'GET') {
    return {
      ok: true,
      status: 200,
      json: async () => ({
        ok: true,
        pollId: 'sekani-travniku-kadan-2026',
        total: 0,
        counts: {},
        percentages: {},
      }),
    };
  }
  posts += 1;
  return {
    ok: true,
    status: 200,
    json: async () => ({
      ok: true,
      pollId: 'sekani-travniku-kadan-2026',
      total: 1,
      counts: {'soucasny-rezim': 1},
      percentages: {'soucasny-rezim': 100},
      selected: 'soucasny-rezim',
      accepted: true,
    }),
  };
};

window.eval(fs.readFileSync('site.js', 'utf8'));
window.document.dispatchEvent(new window.Event('DOMContentLoaded', {bubbles: true}));
await new Promise((resolve) => setTimeout(resolve, 80));

const first = window.document.querySelector('[data-poll-vote="soucasny-rezim"]');
if (!first) throw new Error('Chybí první tlačítko ankety.');
if (first.disabled) throw new Error('Zastaralý localStorage stále blokuje tlačítka.');
if (window.localStorage.getItem('nk-poll-sekani-travniku-kadan-2026')) {
  throw new Error('Zastaralý localStorage nebyl po serverovém ověření odstraněn.');
}

first.click();
await new Promise((resolve) => setTimeout(resolve, 80));
if (posts !== 1) throw new Error(`Server nedostal právě jeden hlas, ale ${posts}.`);
if (!first.disabled) throw new Error('Po přijatém hlasu nebyla anketa uzamčena.');
const text = window.document.querySelector('.poll-results')?.textContent || '';
if (!text.includes('1 hlas') || !text.includes('100 %')) {
  throw new Error(`Výsledky nejsou viditelné: ${text}`);
}
console.log('Regresní test prošel: starý localStorage neblokuje hlas a výsledek je viditelný.');
