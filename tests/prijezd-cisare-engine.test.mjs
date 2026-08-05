import test from 'node:test';
import assert from 'node:assert/strict';
import {
  CHAPTERS,
  DIFFICULTIES,
  applyChoice,
  calculateScore,
  createGame,
  deserializeGame,
  evaluateAchievements,
  getDailySeed,
  getEnding,
  getScene,
  serializeGame
} from '../hry/prijezd-karla-iv/engine.mjs';

test('hra má osm kapitol, dvě varianty a tři volby', () => {
  assert.equal(CHAPTERS.length, 8);
  for (const chapter of CHAPTERS) {
    assert.ok(chapter.variants.length >= 2);
    for (const variant of chapter.variants) assert.equal(variant.choices.length, 3);
  }
});

test('všechny obtížnosti mají pět ukazatelů', () => {
  for (const difficulty of Object.values(DIFFICULTIES)) {
    assert.deepEqual(Object.keys(difficulty.initial).sort(), ['favor', 'order', 'people', 'supplies', 'treasury']);
  }
});

test('stejný seed vybere stejnou scénu', () => {
  const a = createGame({ seed: 'test-seed' });
  const b = createGame({ seed: 'test-seed' });
  assert.equal(getScene(a).variant.title, getScene(b).variant.title);
});

test('celou hru lze automaticky dohrát bez hodnot mimo rozsah', () => {
  let state = createGame({ difficulty: 'royal', seed: 'autoplay' });
  while (state.status === 'playing') {
    const scene = getScene(state);
    state = applyChoice(state, scene.variant.choices[0].id).state;
    for (const value of Object.values(state.stats)) assert.ok(value >= 0 && value <= 100);
  }
  assert.equal(state.history.length, 8);
  assert.equal(state.codex.length, 8);
  assert.ok(calculateScore(state) >= 0 && calculateScore(state) <= 100);
  assert.ok(getEnding(state).title);
  assert.ok(evaluateAchievements(state).includes('firstCouncil'));
});

test('uložení a obnovení zachová rozehranou partii', () => {
  let state = createGame({ difficulty: 'scribe', seed: 'save-test' });
  const scene = getScene(state);
  state = applyChoice(state, scene.variant.choices[1].id).state;
  const restored = deserializeGame(serializeGame(state));
  assert.equal(restored.chapterIndex, 1);
  assert.equal(restored.history[0].choiceId, scene.variant.choices[1].id);
});

test('poškozené nebo staré uložení se odmítne', () => {
  assert.equal(deserializeGame('{bad json'), null);
  assert.equal(deserializeGame(JSON.stringify({ version: 1 })), null);
});

test('denní seed je stabilní pro dané datum', () => {
  assert.equal(getDailySeed('2026-08-02T12:00:00Z'), 'daily-2026-08-02-kadan-1367');
});

test('identifikátory scén a voleb jsou jedinečné a každá volba má následek i historickou stopu', async () => {
  const { ACHIEVEMENTS, EVENTS } = await import('../hry/prijezd-karla-iv/engine.mjs');
  const sceneIds = new Set();
  const choiceIds = new Set();
  for (const chapter of CHAPTERS) {
    assert.ok(chapter.id);
    chapter.variants.forEach((variant, variantIndex) => {
      const sceneId = `${chapter.id}-${variantIndex}`;
      assert.ok(!sceneIds.has(sceneId), `Duplicitní scéna: ${sceneId}`);
      sceneIds.add(sceneId);
      assert.ok(variant.title && variant.text && variant.eyebrow && variant.illustration);
      for (const choice of variant.choices) {
        assert.ok(!choiceIds.has(choice.id), `Duplicitní volba: ${choice.id}`);
        choiceIds.add(choice.id);
        assert.ok(choice.title && choice.text && choice.result && choice.history);
        assert.ok(Object.keys(choice.effects).length >= 2);
      }
    });
  }
  assert.equal(sceneIds.size, 16);
  assert.equal(choiceIds.size, 48);
  assert.ok(EVENTS.length >= 6);
  assert.equal(Object.keys(ACHIEVEMENTS).length, 9);
});

test('vyvážená strategie na střední obtížnost není trestána náhodnou krizí', () => {
  const chooseBalanced = (scene, state) => {
    let bestIndex = 0;
    let bestValue = -Infinity;
    scene.variant.choices.forEach((choice, index) => {
      const values = Object.entries(state.stats).map(([key, value]) => Math.max(0, Math.min(100, value + (choice.effects[key] ?? 0))));
      const average = values.reduce((sum, value) => sum + value, 0) / values.length;
      const minimum = Math.min(...values);
      const spread = Math.max(...values) - minimum;
      const value = average + minimum * .7 - spread * .45;
      if (value > bestValue) { bestValue = value; bestIndex = index; }
    });
    return bestIndex;
  };

  for (let seed = 1; seed <= 100; seed += 1) {
    let state = createGame({ difficulty: 'burgrave', seed: `balance-${seed}` });
    while (state.status === 'playing') {
      const scene = getScene(state);
      state = applyChoice(state, scene.variant.choices[chooseBalanced(scene, state)].id).state;
    }
    assert.notEqual(getEnding(state).tier, 'crisis');
    assert.ok(calculateScore(state) >= 55);
  }
});
