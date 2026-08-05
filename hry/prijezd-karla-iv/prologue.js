const startScreen = document.querySelector('#startScreen');
const prologueScreen = document.querySelector('#prologueScreen');
const startButton = document.querySelector('#startButton');
const continueButton = document.querySelector('#prologueContinueButton');
const backButton = document.querySelector('#prologueBackButton');
const app = document.querySelector('#gameApp');
const sceneTitle = document.querySelector('#sceneTitle');
const sceneText = document.querySelector('#sceneText');

let releaseStart = false;

function focusApp() {
  requestAnimationFrame(() => app?.focus({ preventScroll: true }));
}

function openPrologue(event) {
  if (releaseStart) {
    releaseStart = false;
    return;
  }
  event.preventDefault();
  event.stopImmediatePropagation();
  startScreen.hidden = true;
  prologueScreen.hidden = false;
  continueButton?.focus({ preventScroll: true });
  window.dispatchEvent(new CustomEvent('nasekadan:game', { detail: { name: 'prologue' } }));
}

function beginGame() {
  prologueScreen.hidden = true;
  startScreen.hidden = false;
  releaseStart = true;
  startButton.click();
}

function returnToSetup() {
  prologueScreen.hidden = true;
  startScreen.hidden = false;
  focusApp();
}

function clarifyOpeningScene() {
  const title = sceneTitle?.textContent.trim();
  if (title === 'Radnice žádá rychlý plán obnovy') {
    sceneTitle.textContent = 'Radnice žádá plán posledních oprav';
    sceneText.textContent = 'Město se pět let zvedá z požáru. Do císařova příjezdu zbývá šest týdnů a kameníci, tesaři i nádeníci čekají, co má dostat přednost.';
  } else if (title === 'Domy ještě nesou stopy požáru') {
    sceneText.textContent = 'Pět let po velkém požáru je centrum znovu vystavěné, ale na trase císařského průvodu zůstávají poškozené střechy, rozbité cesty a nedokončená veřejná místa. Peníze nestačí na všechno.';
  }
}

startButton?.addEventListener('click', openPrologue, true);
continueButton?.addEventListener('click', beginGame);
backButton?.addEventListener('click', returnToSetup);

if (sceneTitle) {
  new MutationObserver(clarifyOpeningScene).observe(sceneTitle, { childList: true, subtree: true, characterData: true });
}
