import {
  ACHIEVEMENTS,
  CHAPTERS,
  DIFFICULTIES,
  STAT_META,
  applyChoice,
  calculateScore,
  createGame,
  deserializeGame,
  evaluateAchievements,
  getDailySeed,
  getEnding,
  getScene,
  serializeGame
} from './engine.mjs?v=20260802-v2';

const KEYS = {
  save: 'nasekadan.karel1367.v2.save',
  best: 'nasekadan.karel1367.v2.best',
  achievements: 'nasekadan.karel1367.v2.achievements',
  settings: 'nasekadan.karel1367.v2.settings',
  daily: 'nasekadan.karel1367.v2.daily'
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const elements = {
  body: document.body,
  app: $('#gameApp'),
  startScreen: $('#startScreen'),
  playScreen: $('#playScreen'),
  resultScreen: $('#resultScreen'),
  startButton: $('#startButton'),
  resumeCard: $('#resumeCard'),
  resumeButton: $('#resumeButton'),
  resumeTitle: $('#resumeTitle'),
  resumeMeta: $('#resumeMeta'),
  bestScore: $('#bestScore'),
  dailyStatus: $('#dailyStatus'),
  chapterNumber: $('#chapterNumber'),
  chapterTitle: $('#chapterTitle'),
  progressTrack: $('.progress-track'),
  progressBar: $('#progressBar'),
  stats: $('#stats'),
  sceneIllustration: $('#sceneIllustration'),
  sceneEyebrow: $('#sceneEyebrow'),
  sceneTitle: $('#sceneTitle'),
  sceneText: $('#sceneText'),
  choices: $('#choices'),
  consequence: $('#consequence'),
  consequenceResult: $('#consequenceResult'),
  effectList: $('#effectList'),
  historyNote: $('#historyNote'),
  eventCard: $('#eventCard'),
  eventTitle: $('#eventTitle'),
  eventText: $('#eventText'),
  eventEffects: $('#eventEffects'),
  continueButton: $('#continueButton'),
  resultMedal: $('#resultMedal'),
  resultTitle: $('#resultTitle'),
  resultScore: $('#resultScore'),
  resultDescription: $('#resultDescription'),
  resultStats: $('#resultStats'),
  newAchievements: $('#newAchievements'),
  newAchievementList: $('#newAchievementList'),
  decisionList: $('#decisionList'),
  restartButton: $('#restartButton'),
  shareButton: $('#shareButton'),
  shareStatus: $('#shareStatus'),
  codexButton: $('#codexButton'),
  achievementsButton: $('#achievementsButton'),
  settingsButton: $('#settingsButton'),
  codexCount: $('#codexCount'),
  achievementCount: $('#achievementCount'),
  codexDialog: $('#codexDialog'),
  achievementsDialog: $('#achievementsDialog'),
  settingsDialog: $('#settingsDialog'),
  codexList: $('#codexList'),
  achievementList: $('#achievementList'),
  soundSetting: $('#soundSetting'),
  largeTextSetting: $('#largeTextSetting'),
  motionSetting: $('#motionSetting'),
  resetProgressButton: $('#resetProgressButton'),
  toast: $('#toast')
};

let state = null;
let pendingState = null;
let lastFocused = null;
let toastTimer = null;
let audioContext = null;
let settings = loadJson(KEYS.settings, { sound: false, largeText: false, reduceMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches });
let unlockedAchievements = new Set(loadJson(KEYS.achievements, []));

function storageGet(key) {
  try { return window.localStorage.getItem(key); } catch { return null; }
}

function storageSet(key, value) {
  try { window.localStorage.setItem(key, value); return true; } catch { return false; }
}

function storageRemove(key) {
  try { window.localStorage.removeItem(key); return true; } catch { return false; }
}

function loadJson(key, fallback) {
  try {
    const value = storageGet(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

function saveJson(key, value) {
  storageSet(key, JSON.stringify(value));
}

function emit(name, detail = {}) {
  window.dispatchEvent(new CustomEvent('nasekadan:game', { detail: { name, ...detail } }));
}

function showToast(message) {
  clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.hidden = false;
  toastTimer = window.setTimeout(() => { elements.toast.hidden = true; }, 2600);
}

function playTone(kind = 'select') {
  if (!settings.sound) return;
  try {
    audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();
    const map = { select: [360, .04], positive: [620, .08], negative: [190, .1], finish: [440, .16] };
    const [frequency, duration] = map[kind] ?? map.select;
    oscillator.frequency.value = frequency;
    oscillator.type = kind === 'negative' ? 'sawtooth' : 'sine';
    gain.gain.setValueAtTime(.0001, audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(.08, audioContext.currentTime + .01);
    gain.gain.exponentialRampToValueAtTime(.0001, audioContext.currentTime + duration);
    oscillator.connect(gain).connect(audioContext.destination);
    oscillator.start();
    oscillator.stop(audioContext.currentTime + duration + .02);
  } catch { /* Audio is optional. */ }
}

function applySettings() {
  elements.body.classList.toggle('is-large-text', Boolean(settings.largeText));
  elements.body.classList.toggle('reduce-motion', Boolean(settings.reduceMotion));
  elements.soundSetting.checked = Boolean(settings.sound);
  elements.largeTextSetting.checked = Boolean(settings.largeText);
  elements.motionSetting.checked = Boolean(settings.reduceMotion);
  saveJson(KEYS.settings, settings);
}

function selectedValue(name) {
  return $(`input[name="${name}"]:checked`)?.value;
}

function syncPickerClasses() {
  $$('.mode-option, .difficulty-option').forEach((label) => label.classList.toggle('is-selected', Boolean($('input', label)?.checked)));
  updateBestScore();
}

function bestMap() { return loadJson(KEYS.best, {}); }
function bestKey(mode, difficulty) { return `${mode}:${difficulty}`; }

function dateKey(date = new Date()) {
  return getDailySeed(date).replace('daily-', '').replace('-kadan-1367', '');
}

function getDailySummary() {
  const history = loadJson(KEYS.daily, {});
  const today = new Date();
  const todayKey = dateKey(today);
  const todayScore = Number(history[todayKey]) || 0;
  const cursor = new Date(today);
  if (!todayScore) cursor.setDate(cursor.getDate() - 1);
  let streak = 0;
  while (Number(history[dateKey(cursor)]) > 0 && streak < 366) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return { todayScore, streak };
}

function updateBestScore() {
  const mode = selectedValue('mode') ?? 'story';
  const difficulty = selectedValue('difficulty') ?? 'burgrave';
  const best = bestMap()[bestKey(mode, difficulty)];
  const modeLabel = mode === 'daily' ? 'denní výzva' : 'volná kronika';
  elements.bestScore.textContent = best ? `Nejlepší výsledek (${modeLabel}): ${best} bodů` : `Nejlepší výsledek (${modeLabel}): zatím žádný`;
  const { todayScore, streak } = getDailySummary();
  if (todayScore) {
    elements.dailyStatus.textContent = `Dnešní výzva: ${todayScore} bodů · série ${streak} ${streak === 1 ? 'den' : streak < 5 ? 'dny' : 'dní'}`;
  } else if (streak) {
    elements.dailyStatus.textContent = `Dnešní výzva čeká · aktivní série ${streak} ${streak === 1 ? 'den' : streak < 5 ? 'dny' : 'dní'}`;
  } else {
    elements.dailyStatus.textContent = 'Dnešní výzva čeká – stejná partie pro všechny po celý den.';
  }
}

function updateProgressCounters() {
  const saved = deserializeGame(storageGet(KEYS.save));
  const codex = new Set(saved?.codex ?? []);
  const historical = loadJson(`${KEYS.save}.codex`, []);
  historical.forEach((id) => codex.add(id));
  elements.codexCount.textContent = `${codex.size}/${CHAPTERS.length}`;
  elements.achievementCount.textContent = `${unlockedAchievements.size}/${Object.keys(ACHIEVEMENTS).length}`;
}

function renderResume() {
  const saved = deserializeGame(storageGet(KEYS.save));
  if (!saved || saved.status !== 'playing') {
    elements.resumeCard.hidden = true;
    return;
  }
  const chapter = CHAPTERS[saved.chapterIndex];
  elements.resumeCard.hidden = false;
  elements.resumeTitle.textContent = `Kapitola ${saved.chapterIndex + 1} z ${CHAPTERS.length}: ${chapter?.label ?? 'Pokračování'}`;
  elements.resumeMeta.textContent = `${DIFFICULTIES[saved.difficulty].label} · ${saved.mode === 'daily' ? 'denní výzva' : 'volná kronika'}`;
}

function setScreen(screen) {
  elements.startScreen.hidden = screen !== 'start';
  elements.playScreen.hidden = screen !== 'play';
  elements.resultScreen.hidden = screen !== 'result';
  requestAnimationFrame(() => elements.app.focus({ preventScroll: true }));
}

function startGame() {
  const mode = selectedValue('mode') ?? 'story';
  const difficulty = selectedValue('difficulty') ?? 'burgrave';
  const seed = mode === 'daily' ? getDailySeed() : undefined;
  state = createGame({ mode, difficulty, seed });
  pendingState = null;
  saveState();
  setScreen('play');
  renderGame();
  playTone('select');
  emit('start', { mode, difficulty });
}

function resumeGame() {
  const saved = deserializeGame(storageGet(KEYS.save));
  if (!saved || saved.status !== 'playing') return renderResume();
  state = saved;
  pendingState = null;
  setScreen('play');
  renderGame();
  showToast('Rozehraná kronika byla obnovena.');
  emit('resume', { chapterIndex: state.chapterIndex, mode: state.mode, difficulty: state.difficulty });
}

function saveState() {
  if (!state) return;
  storageSet(KEYS.save, serializeGame(state));
  const allCodex = new Set(loadJson(`${KEYS.save}.codex`, []));
  state.codex.forEach((id) => allCodex.add(id));
  saveJson(`${KEYS.save}.codex`, [...allCodex]);
  updateProgressCounters();
}

function renderStats(stats) {
  elements.stats.innerHTML = '';
  Object.entries(STAT_META).forEach(([key, meta]) => {
    const value = stats[key];
    const item = document.createElement('div');
    item.className = `stat${value < 35 ? ' is-danger' : value < 52 ? ' is-warning' : ''}`;
    item.dataset.stat = key;
    item.innerHTML = `<span class="stat__icon" aria-hidden="true">${meta.icon}</span><div class="stat__label"><b>${meta.label}</b><div class="stat__bar" aria-hidden="true"><i style="width:${value}%"></i></div></div><output aria-label="${meta.label}: ${value} ze 100">${value}</output>`;
    elements.stats.append(item);
  });
}

function renderGame() {
  if (!state) return;
  if (state.status === 'finished') return renderResult();
  const scene = getScene(state);
  if (!scene) return;
  setScreen('play');
  pendingState = null;
  elements.consequence.hidden = true;
  elements.choices.hidden = false;
  elements.chapterNumber.textContent = `Kapitola ${state.chapterIndex + 1} z ${CHAPTERS.length}`;
  elements.chapterTitle.textContent = scene.chapter.label;
  elements.progressBar.style.width = `${(state.chapterIndex / CHAPTERS.length) * 100}%`;
  elements.progressTrack.setAttribute('aria-valuenow', String(state.chapterIndex));
  renderStats(state.stats);
  elements.sceneEyebrow.textContent = scene.variant.eyebrow;
  elements.sceneTitle.textContent = scene.variant.title;
  elements.sceneText.textContent = scene.variant.text;
  elements.sceneIllustration.dataset.scene = scene.variant.illustration;
  elements.choices.innerHTML = '';
  scene.variant.choices.forEach((choice, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'choice-button';
    button.dataset.choiceId = choice.id;
    button.innerHTML = `<span class="choice-number">${index + 1}</span><span class="choice-copy"><b>${choice.title}</b><small>${choice.text}</small></span><span class="choice-arrow" aria-hidden="true">›</span>`;
    button.addEventListener('click', () => choose(choice.id));
    elements.choices.append(button);
  });
  requestAnimationFrame(() => $('.choice-button', elements.choices)?.focus({ preventScroll: true }));
}

function effectPill(key, value) {
  const meta = STAT_META[key];
  const pill = document.createElement('span');
  pill.className = `effect-pill ${value >= 0 ? 'is-positive' : 'is-negative'}`;
  pill.textContent = `${meta?.icon ?? ''} ${meta?.label ?? key} ${value >= 0 ? '+' : ''}${value}`;
  return pill;
}

function choose(choiceId) {
  if (!state || pendingState) return;
  const outcome = applyChoice(state, choiceId);
  pendingState = outcome.state;
  $$('.choice-button', elements.choices).forEach((button) => { button.disabled = true; });
  elements.choices.hidden = true;
  elements.consequence.hidden = false;
  elements.consequenceResult.textContent = outcome.choice.result;
  elements.historyNote.textContent = outcome.choice.history;
  elements.effectList.innerHTML = '';
  Object.entries(outcome.effects).forEach(([key, value]) => elements.effectList.append(effectPill(key, value)));
  if (outcome.event) {
    elements.eventCard.hidden = false;
    elements.eventTitle.textContent = outcome.event.title;
    elements.eventText.textContent = outcome.event.text;
    elements.eventEffects.innerHTML = '';
    Object.entries(outcome.event.effects).forEach(([key, value]) => elements.eventEffects.append(effectPill(key, value)));
  } else {
    elements.eventCard.hidden = true;
  }
  const net = [...Object.values(outcome.effects), ...Object.values(outcome.event?.effects ?? {})].reduce((sum, value) => sum + value, 0);
  playTone(net >= 0 ? 'positive' : 'negative');
  elements.continueButton.textContent = pendingState.status === 'finished' ? 'Uzavřít kroniku' : 'Pokračovat';
  elements.continueButton.focus();
  emit('choice', { chapterIndex: state.chapterIndex, choiceId, difficulty: state.difficulty, mode: state.mode });
}

function continueGame() {
  if (!pendingState) return;
  state = pendingState;
  pendingState = null;
  saveState();
  if (state.status === 'finished') {
    renderResult();
  } else {
    renderGame();
  }
}

function persistResult(score) {
  const best = bestMap();
  const key = bestKey(state.mode, state.difficulty);
  if (!best[key] || score > best[key]) {
    best[key] = score;
    saveJson(KEYS.best, best);
    showToast('Nový osobní rekord!');
  }
  if (state.mode === 'daily') {
    const daily = loadJson(KEYS.daily, {});
    const day = dateKey();
    daily[day] = Math.max(daily[day] ?? 0, score);
    saveJson(KEYS.daily, daily);
    updateBestScore();
  }
}

function renderResult() {
  setScreen('result');
  const score = calculateScore(state);
  const ending = getEnding(state);
  const achieved = evaluateAchievements(state);
  const newlyUnlocked = achieved.filter((id) => !unlockedAchievements.has(id));
  achieved.forEach((id) => unlockedAchievements.add(id));
  saveJson(KEYS.achievements, [...unlockedAchievements]);
  persistResult(score);
  storageRemove(KEYS.save);
  saveJson(`${KEYS.save}.codex`, [...new Set([...loadJson(`${KEYS.save}.codex`, []), ...state.codex])]);
  updateProgressCounters();
  renderResume();

  elements.resultMedal.dataset.tier = ending.tier;
  elements.resultMedal.textContent = ending.tier === 'gold' ? '♛' : ending.tier === 'crisis' ? '!' : '✦';
  elements.resultTitle.textContent = ending.title;
  elements.resultScore.textContent = score;
  elements.resultDescription.textContent = ending.description;
  elements.resultStats.innerHTML = '';
  Object.entries(STAT_META).forEach(([key, meta]) => {
    const item = document.createElement('div');
    item.className = 'result-stat';
    item.innerHTML = `<span>${meta.label}</span><b>${state.stats[key]}</b>`;
    elements.resultStats.append(item);
  });
  elements.decisionList.innerHTML = '';
  state.history.forEach((entry) => {
    const item = document.createElement('li');
    item.innerHTML = `<strong>${entry.chapterLabel}:</strong> ${entry.choiceTitle}`;
    elements.decisionList.append(item);
  });
  if (newlyUnlocked.length) {
    elements.newAchievements.hidden = false;
    elements.newAchievementList.innerHTML = '';
    newlyUnlocked.forEach((id) => {
      const badge = document.createElement('b');
      badge.textContent = ACHIEVEMENTS[id].title;
      elements.newAchievementList.append(badge);
    });
  } else {
    elements.newAchievements.hidden = true;
  }
  playTone('finish');
  emit('finish', { score, ending: ending.tier, difficulty: state.difficulty, mode: state.mode, achievements: achieved });
}

function restart() {
  state = null;
  pendingState = null;
  elements.shareStatus.textContent = '';
  setScreen('start');
  renderStart();
  window.scrollTo({ top: elements.app.getBoundingClientRect().top + window.scrollY - 90, behavior: settings.reduceMotion ? 'auto' : 'smooth' });
}

async function shareResult() {
  const score = calculateScore(state);
  const ending = getEnding(state);
  const text = `V historické hře Příjezd císaře: Kadaň 1367 jsem získal(a) ${score}/100 – ${ending.title}.`;
  const shareData = { title: 'Příjezd císaře: Kadaň 1367', text, url: 'https://nasekadan.cz/hry/prijezd-karla-iv/' };
  try {
    if (navigator.share) await navigator.share(shareData);
    else await navigator.clipboard.writeText(`${text} ${shareData.url}`);
    elements.shareStatus.textContent = navigator.share ? 'Sdílení bylo otevřeno.' : 'Výsledek byl zkopírován.';
    emit('share', { score });
  } catch (error) {
    if (error?.name !== 'AbortError') elements.shareStatus.textContent = 'Výsledek se nepodařilo sdílet.';
  }
}

function openDialog(dialog) {
  lastFocused = document.activeElement;
  if (typeof dialog.showModal === 'function') dialog.showModal();
  else dialog.setAttribute('open', '');
  $('.dialog-close', dialog)?.focus();
}

function closeDialog(dialog) {
  if (typeof dialog.close === 'function') dialog.close();
  else dialog.removeAttribute('open');
  lastFocused?.focus?.();
}

function renderCodex() {
  const historical = new Set(loadJson(`${KEYS.save}.codex`, []));
  state?.codex?.forEach((id) => historical.add(id));
  elements.codexList.innerHTML = '';
  CHAPTERS.forEach((chapter, index) => {
    const unlocked = historical.has(chapter.id);
    const historyEntry = [...(state?.history ?? [])].reverse().find((entry) => entry.chapterId === chapter.id);
    const item = document.createElement('article');
    item.className = `codex-entry${unlocked ? '' : ' is-locked'}`;
    item.innerHTML = `<span>KAPITOLA ${index + 1}</span><h3>${unlocked ? chapter.codexTitle : 'Neodemčená stopa'}</h3><p>${unlocked ? (historyEntry?.history ?? 'Tato historická stopa byla odemčena v některé z předchozích partií.') : 'Dokonči příslušnou kapitolu.'}</p>`;
    elements.codexList.append(item);
  });
}

function renderAchievements() {
  elements.achievementList.innerHTML = '';
  Object.entries(ACHIEVEMENTS).forEach(([id, achievement]) => {
    const unlocked = unlockedAchievements.has(id);
    const item = document.createElement('article');
    item.className = `achievement-entry${unlocked ? '' : ' is-locked'}`;
    item.innerHTML = `<span>${unlocked ? 'ODEMČENO' : 'ZAMČENO'}</span><h3>${unlocked ? '✦ ' : '◇ '}${achievement.title}</h3><p>${achievement.description}</p>`;
    elements.achievementList.append(item);
  });
}

function resetProgress() {
  const confirmed = window.confirm('Opravdu smazat rozehranou partii, rekordy, kroniku i všechny úspěchy?');
  if (!confirmed) return;
  Object.values(KEYS).forEach(storageRemove);
  storageRemove(`${KEYS.save}.codex`);
  state = null;
  pendingState = null;
  unlockedAchievements = new Set();
  renderStart();
  renderCodex();
  renderAchievements();
  updateProgressCounters();
  closeDialog(elements.settingsDialog);
  showToast('Herní postup byl smazán.');
}

function renderStart() {
  renderResume();
  updateBestScore();
  updateProgressCounters();
  syncPickerClasses();
}

$$('input[name="mode"], input[name="difficulty"]').forEach((input) => input.addEventListener('change', syncPickerClasses));
elements.startButton.addEventListener('click', startGame);
elements.resumeButton.addEventListener('click', resumeGame);
elements.continueButton.addEventListener('click', continueGame);
elements.restartButton.addEventListener('click', restart);
elements.shareButton.addEventListener('click', shareResult);
elements.codexButton.addEventListener('click', () => { renderCodex(); openDialog(elements.codexDialog); });
elements.achievementsButton.addEventListener('click', () => { renderAchievements(); openDialog(elements.achievementsDialog); });
elements.settingsButton.addEventListener('click', () => openDialog(elements.settingsDialog));
$$('[data-close-dialog]').forEach((button) => button.addEventListener('click', () => closeDialog(button.closest('dialog'))));
$$('dialog').forEach((dialog) => dialog.addEventListener('click', (event) => { if (event.target === dialog) closeDialog(dialog); }));
elements.soundSetting.addEventListener('change', () => { settings.sound = elements.soundSetting.checked; applySettings(); playTone('select'); });
elements.largeTextSetting.addEventListener('change', () => { settings.largeText = elements.largeTextSetting.checked; applySettings(); });
elements.motionSetting.addEventListener('change', () => { settings.reduceMotion = elements.motionSetting.checked; applySettings(); });
elements.resetProgressButton.addEventListener('click', resetProgress);

document.addEventListener('keydown', (event) => {
  if ($('dialog[open]')) return;
  if (!elements.playScreen.hidden && !pendingState && ['1', '2', '3'].includes(event.key)) {
    const button = $$('.choice-button', elements.choices)[Number(event.key) - 1];
    if (button && !button.disabled) { event.preventDefault(); button.click(); }
  } else if (!elements.playScreen.hidden && pendingState && event.key === 'Enter') {
    event.preventDefault(); continueGame();
  }
});

window.addEventListener('storage', (event) => {
  if (event.key === KEYS.save) renderResume();
});

applySettings();
renderStart();
renderCodex();
renderAchievements();
emit('ready', { version: 2 });
