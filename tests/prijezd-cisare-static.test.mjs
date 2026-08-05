import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const root = new URL('../hry/prijezd-karla-iv/', import.meta.url);
const [html, css, js, prologue] = await Promise.all([
  readFile(new URL('index.html', root), 'utf8'),
  Promise.all(['game.css', 'game-core.css', 'game-play.css', 'game-responsive.css'].map((name) => readFile(new URL(name, root), 'utf8'))).then((parts) => parts.join('\n')),
  readFile(new URL('game.js', root), 'utf8'),
  readFile(new URL('prologue.js', root), 'utf8')
]);

test('pracovní stránka se nesmí indexovat ani vydávat za veřejnou verzi', () => {
  assert.match(html, /name="robots" content="noindex,nofollow,noarchive"/);
  assert.match(html, /HRA NENÍ VEŘEJNĚ PUBLIKOVANÁ/);
  assert.doesNotMatch(html, /rel="canonical"/);
});

test('rozhraní obsahuje návratové mechanismy a přístupnost', () => {
  assert.equal((html.match(/name="mode"/g) ?? []).length, 2);
  assert.equal((html.match(/name="difficulty"/g) ?? []).length, 3);
  assert.equal((html.match(/<dialog/g) ?? []).length, 3);
  for (const id of ['dailyStatus', 'resumeCard', 'prologueScreen', 'prologueContinueButton', 'codexDialog', 'achievementsDialog', 'settingsDialog']) {
    assert.match(html, new RegExp(`id="${id}"`));
  }
  assert.match(js, /getDailySummary/);
  assert.match(js, /serializeGame/);
  assert.match(js, /event\.key/);
  assert.match(js, /navigator\.share|clipboard/);
});

test('prolog vysvětluje požár, obnovu a důvod prvního rozhodnutí', () => {
  assert.match(html, /Roku 1362 zachvátil Kadaň rozsáhlý požár/);
  assert.match(html, /Nezačínáš na spáleništi/);
  assert.match(html, /Požár roku 1362 a Karlova návštěva roku 1367 jsou doložené/);
  assert.match(prologue, /function openPrologue/);
  assert.match(prologue, /Radnice žádá plán posledních oprav/);
  assert.match(prologue, /Město se pět let zvedá z požáru/);
});

test('skryté prvky zůstávají skutečně skryté i při vlastním display stylu', () => {
  assert.match(css, /body\.game-page \[hidden\]\s*\{\s*display:\s*none\s*!important/);
});

test('CSS má vyvážené složené závorky a mobilní pravidla', () => {
  const opens = [...css].filter((char) => char === '{').length;
  const closes = [...css].filter((char) => char === '}').length;
  assert.equal(opens, closes);
  assert.match(css, /@media \(max-width: 560px\)/);
  assert.match(css, /grid-template-columns:\s*repeat\(2,minmax\(0,1fr\)\)/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /\.prologue-timeline/);
});

test('úložiště je volitelné a jeho zákaz nesmí shodit hru', () => {
  assert.match(js, /function storageGet/);
  assert.match(js, /catch \{ return null; \}/);
  assert.match(js, /function storageSet/);
  assert.match(js, /function storageRemove/);
});
