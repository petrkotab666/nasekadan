import { CHAPTERS_A } from './game-data-a.mjs';
import { CHAPTERS_B } from './game-data-b.mjs';

export const GAME_VERSION = 2;

export const STAT_META = {
  treasury: { label: 'Pokladna', icon: '◈' },
  supplies: { label: 'Zásoby', icon: '♨' },
  order: { label: 'Pořádek', icon: '⚖' },
  people: { label: 'Obyvatelé', icon: '♟' },
  favor: { label: 'Přízeň', icon: '♛' }
};

export const DIFFICULTIES = {
  scribe: {
    label: 'Městský písař',
    description: 'Více prostředků a mírnější následky.',
    negativeMultiplier: 0.8,
    scoreBonus: 0,
    initial: { treasury: 72, supplies: 70, order: 66, people: 72, favor: 52 }
  },
  burgrave: {
    label: 'Purkmistr',
    description: 'Vyvážená historická výzva.',
    negativeMultiplier: 1,
    scoreBonus: 4,
    initial: { treasury: 58, supplies: 58, order: 56, people: 58, favor: 42 }
  },
  royal: {
    label: 'Královský správce',
    description: 'Málo prostředků a tvrdé následky.',
    negativeMultiplier: 1.18,
    scoreBonus: 8,
    initial: { treasury: 44, supplies: 46, order: 50, people: 48, favor: 34 }
  }
};

export const CHAPTERS = [...CHAPTERS_A, ...CHAPTERS_B];

export const EVENTS = [
  { id: 'storm', title: 'Prudká bouře', text: 'Déšť poškodil část stánků, ale naplnil nádoby vodou.', effects: { treasury: -5, supplies: 4, order: -3 } },
  { id: 'merchant-gift', title: 'Dar vděčného kupce', text: 'Kupec, kterému město pomohlo, věnoval sud soli.', effects: { supplies: 7, people: 2 } },
  { id: 'rumor', title: 'Zlá pověst', text: 'Po okolí se šíří zpráva, že město nestíhá přípravy.', effects: { favor: -6, order: -2 } },
  { id: 'volunteers', title: 'Dobrovolní pomocníci', text: 'Mladí tovaryši se nabídli, že zdarma uklidí náměstí.', effects: { order: 6, people: 5 } },
  { id: 'spoiled-grain', title: 'Zkažené obilí', text: 'Část zásob zvlhla ve skladu.', effects: { supplies: -8, treasury: -3 } },
  { id: 'good-news', title: 'Příznivá zpráva od dvora', text: 'Posel chválí dosavadní přípravy.', effects: { favor: 7, people: 2 } }
];

export const ACHIEVEMENTS = {
  firstCouncil: { title: 'První městská rada', description: 'Dokonči první partii.' },
  balanced: { title: 'Mistr rovnováhy', description: 'Dokonči hru se všemi ukazateli alespoň 55.' },
  peopleHero: { title: 'Hlas obyvatel', description: 'Dokonči hru s obyvateli na 80 nebo více.' },
  imperialSeal: { title: 'Císařská pečeť', description: 'Dokonči hru s přízní na 80 nebo více.' },
  keeper: { title: 'Strážce pokladny', description: 'Dokonči hru s pokladnou na 75 nebo více.' },
  royalSurvivor: { title: 'Královský správce', description: 'Na nejtěžší obtížnost získej alespoň 58 bodů.' },
  chronicler: { title: 'Kadaňský kronikář', description: 'Odemkni historickou stopu všech osmi kapitol.' },
  goldenCouncil: { title: 'Zlatá rada', description: 'Získej alespoň 86 bodů.' },
  dailyWitness: { title: 'Svědek dne', description: 'Dokonči denní výzvu.' }
};

export function clamp(value, min = 0, max = 100) {
  return Math.max(min, Math.min(max, Math.round(value)));
}

export function hashSeed(input) {
  const text = String(input ?? 'kadan-1367');
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function seededRandom(seed) {
  let state = hashSeed(seed);
  return () => {
    state += 0x6D2B79F5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

export function getDailySeed(date = new Date()) {
  const iso = typeof date === 'string' ? date.slice(0, 10) : date.toISOString().slice(0, 10);
  return `daily-${iso}-kadan-1367`;
}

function normalizeEffects(effects, difficultyKey) {
  const difficulty = DIFFICULTIES[difficultyKey] ?? DIFFICULTIES.burgrave;
  return Object.fromEntries(Object.entries(effects).map(([key, value]) => {
    const adjusted = value < 0 ? value * difficulty.negativeMultiplier : value;
    return [key, Math.round(adjusted)];
  }));
}

function applyEffects(stats, effects) {
  const next = { ...stats };
  for (const [key, value] of Object.entries(effects)) {
    if (!(key in next)) continue;
    next[key] = clamp(next[key] + value);
  }
  return next;
}

export function createGame({ difficulty = 'burgrave', mode = 'story', seed } = {}) {
  const safeDifficulty = DIFFICULTIES[difficulty] ? difficulty : 'burgrave';
  const safeMode = mode === 'daily' ? 'daily' : 'story';
  const selectedSeed = seed ?? (safeMode === 'daily' ? getDailySeed() : `story-${Date.now()}-${Math.random()}`);
  return {
    version: GAME_VERSION,
    status: 'playing',
    difficulty: safeDifficulty,
    mode: safeMode,
    seed: String(selectedSeed),
    chapterIndex: 0,
    stats: { ...DIFFICULTIES[safeDifficulty].initial },
    history: [],
    codex: [],
    eventsSeen: [],
    startedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
}

export function getScene(state) {
  if (!state || state.status !== 'playing') return null;
  const chapter = CHAPTERS[state.chapterIndex];
  if (!chapter) return null;
  const random = seededRandom(`${state.seed}:chapter:${state.chapterIndex}`);
  const variantIndex = Math.floor(random() * chapter.variants.length);
  return { chapter, variant: chapter.variants[variantIndex], variantIndex };
}

function getEvent(state, chapterIndex) {
  if (![1, 3, 5].includes(chapterIndex)) return null;
  const random = seededRandom(`${state.seed}:event:${chapterIndex}`);
  return EVENTS[Math.floor(random() * EVENTS.length)];
}

export function applyChoice(state, choiceId) {
  if (!state || state.status !== 'playing') throw new Error('Hra není rozehraná.');
  const current = getScene(state);
  if (!current) throw new Error('Kapitola neexistuje.');
  const choice = current.variant.choices.find((item) => item.id === choiceId);
  if (!choice) throw new Error('Neplatná volba.');

  const choiceEffects = normalizeEffects(choice.effects, state.difficulty);
  let stats = applyEffects(state.stats, choiceEffects);
  const event = getEvent(state, state.chapterIndex);
  let eventEffects = null;
  if (event) {
    eventEffects = normalizeEffects(event.effects, state.difficulty);
    stats = applyEffects(stats, eventEffects);
  }

  const codex = state.codex.includes(current.chapter.id) ? [...state.codex] : [...state.codex, current.chapter.id];
  const eventsSeen = event && !state.eventsSeen.includes(event.id) ? [...state.eventsSeen, event.id] : [...state.eventsSeen];
  const historyEntry = {
    chapterId: current.chapter.id,
    chapterLabel: current.chapter.label,
    codexTitle: current.chapter.codexTitle,
    sceneTitle: current.variant.title,
    choiceId: choice.id,
    choiceTitle: choice.title,
    result: choice.result,
    history: choice.history,
    effects: choiceEffects,
    event: event ? { ...event, effects: eventEffects } : null
  };

  const chapterIndex = state.chapterIndex + 1;
  const finished = chapterIndex >= CHAPTERS.length;
  const nextState = {
    ...state,
    stats,
    history: [...state.history, historyEntry],
    codex,
    eventsSeen,
    chapterIndex,
    status: finished ? 'finished' : 'playing',
    updatedAt: new Date().toISOString()
  };

  return { state: nextState, choice, effects: choiceEffects, event: historyEntry.event };
}

export function calculateScore(state) {
  const values = Object.values(state.stats);
  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  const minimum = Math.min(...values);
  const spread = Math.max(...values) - minimum;
  const balanceBonus = Math.max(0, 12 - spread * 0.18);
  const difficultyBonus = DIFFICULTIES[state.difficulty]?.scoreBonus ?? 0;
  return clamp(average * 0.76 + minimum * 0.12 + balanceBonus + difficultyBonus);
}

export function getEnding(state) {
  const score = calculateScore(state);
  const { treasury, supplies, order, people, favor } = state.stats;
  if (Math.min(treasury, supplies, order, people, favor) <= 18) {
    return { tier: 'crisis', title: 'Město na hraně', description: 'Císař přijel, ale jedna část města se téměř zhroutila. Příště bude nutné držet rovnováhu a neobětovat vše jedinému cíli.' };
  }
  if (score >= 86) return { tier: 'gold', title: 'Zlatý věk městské rady', description: 'Kadaň zvládla návštěvu jako sebevědomé královské město. Císař, kupci i obyvatelé odjíždějí s respektem.' };
  if (score >= 72) return { tier: 'silver', title: 'Důstojné císařské přivítání', description: 'Město obstálo a většina rozhodnutí se ukázala jako prozíravá. Několik sporů však zůstane tématem dalších rad.' };
  if (score >= 56) return { tier: 'bronze', title: 'Kadaň návštěvu zvládla', description: 'Nebyl to triumf bez chyby, ale brány se otevřely, hosté dostali jídlo a město si zachovalo tvář.' };
  return { tier: 'wood', title: 'Poučení pro příští radu', description: 'Přípravy odhalily slabiny města. Návštěva proběhla, ale kronikář má o čem psát a další partie může dopadnout úplně jinak.' };
}

export function evaluateAchievements(state) {
  if (!state || state.status !== 'finished') return [];
  const score = calculateScore(state);
  const unlocked = ['firstCouncil'];
  if (Object.values(state.stats).every((value) => value >= 55)) unlocked.push('balanced');
  if (state.stats.people >= 80) unlocked.push('peopleHero');
  if (state.stats.favor >= 80) unlocked.push('imperialSeal');
  if (state.stats.treasury >= 75) unlocked.push('keeper');
  if (state.difficulty === 'royal' && score >= 58) unlocked.push('royalSurvivor');
  if (state.codex.length >= CHAPTERS.length) unlocked.push('chronicler');
  if (score >= 86) unlocked.push('goldenCouncil');
  if (state.mode === 'daily') unlocked.push('dailyWitness');
  return unlocked;
}

export function serializeGame(state) {
  return JSON.stringify(state);
}

export function deserializeGame(serialized) {
  try {
    const state = JSON.parse(serialized);
    if (!state || state.version !== GAME_VERSION) return null;
    if (!DIFFICULTIES[state.difficulty]) return null;
    if (!['playing', 'finished'].includes(state.status)) return null;
    if (!Number.isInteger(state.chapterIndex) || state.chapterIndex < 0 || state.chapterIndex > CHAPTERS.length) return null;
    for (const key of Object.keys(STAT_META)) {
      if (!Number.isFinite(state.stats?.[key])) return null;
      state.stats[key] = clamp(state.stats[key]);
    }
    return state;
  } catch {
    return null;
  }
}
