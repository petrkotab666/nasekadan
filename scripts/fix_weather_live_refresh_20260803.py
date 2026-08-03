#!/usr/bin/env python3
"""Opraví obnovování počasí, odmítání zastaralého měření a cache busting."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / 'pocasi.js'
LOADER = ROOT / 'scripts' / 'ensure_weather_loader.py'
PAGES = (ROOT / 'index.html', ROOT / 'pocasi' / 'index.html')
VERSION = '20260803-weather-live-refresh-3'
MARKER = 'WEATHER_LIVE_REFRESH_V3'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: očekáván právě jeden výskyt, nalezeno {count}.')
    return text.replace(old, new, 1)


def patch_js() -> None:
    text = JS.read_text(encoding='utf-8')
    if MARKER in text:
        print('pocasi.js už obsahuje živou opravu v3.')
        return

    text = replace_once(
        text,
        "    cacheKey: 'nasekadan-weather-v2',\n    cacheMinutes: 30\n",
        "    cacheKey: 'nasekadan-weather-v3',\n    cacheMinutes: 5,\n    refreshMinutes: 5,\n    observationMaxAgeMinutes: 45\n",
        'Konfigurace počasí',
    )

    old_start = """  const cached = readCache();
  if (cached) render(target, cached, true);
  const cacheIsFresh = cached && cached.fetchedAt && Number.isFinite(Date.parse(cached.fetchedAt))
    && Date.now() - Date.parse(cached.fetchedAt) < CONFIG.cacheMinutes * 60 * 1000;
  if (cacheIsFresh) return;

  loadWeather().then(data => {
    if (!data) return;
    writeCache(data);
    render(target, data, false);
  }).catch(() => {
    if (!cached) renderError(target);
  });
"""
    new_start = """  // WEATHER_LIVE_REFRESH_V3: cache je jen okamžitá záloha, nikoli důvod přeskočit síťovou aktualizaci.
  const cached = readCache();
  if (cached) render(target, cached, true);

  let refreshInFlight = false;
  let lastRefreshStartedAt = 0;

  async function refreshWeather(force = false) {
    const now = Date.now();
    if (refreshInFlight) return;
    if (!force && now - lastRefreshStartedAt < 60 * 1000) return;
    refreshInFlight = true;
    lastRefreshStartedAt = now;
    try {
      const data = await loadWeather();
      if (!data) {
        if (!cached) renderError(target);
        return;
      }
      writeCache(data);
      render(target, data, false);
    } catch (_) {
      if (!cached) renderError(target);
    } finally {
      refreshInFlight = false;
    }
  }

  // Načíst čerstvá data při každém otevření, poté každých pět minut a při návratu do záložky.
  refreshWeather(true);
  window.setInterval(() => refreshWeather(true), CONFIG.refreshMinutes * 60 * 1000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) refreshWeather(true);
  });
  window.addEventListener('focus', () => refreshWeather(true));
"""
    text = replace_once(text, old_start, new_start, 'Spouštěcí blok počasí')

    old_observation = """    const forecast = forecastResult.status === 'fulfilled' ? forecastResult.value : null;
    const observation = observationResult.status === 'fulfilled' ? observationResult.value : null;
    if (!forecast && !observation) return null;
"""
    new_observation = """    const forecast = forecastResult.status === 'fulfilled' ? forecastResult.value : null;
    const rawObservation = observationResult.status === 'fulfilled' ? observationResult.value : null;
    // ČHMÚ může během výpadku ponechat poslední denní soubor beze změny. Staré měření proto nesmí přebít aktuální předpověď.
    const observation = rawObservation && isFreshTimestamp(rawObservation.time, CONFIG.observationMaxAgeMinutes)
      ? rawObservation : null;
    if (!forecast && !observation) return null;
"""
    text = replace_once(text, old_observation, new_observation, 'Kontrola stáří měření')

    text = replace_once(
        text,
        """    const response = await fetch(CONFIG.forecastUrl, {
      headers: { 'Accept': 'application/json' },
      credentials: 'same-origin'
    });
""",
        """    const response = await fetch(cacheBusted(CONFIG.forecastUrl), {
      headers: { 'Accept': 'application/json', 'Cache-Control': 'no-cache' },
      credentials: 'same-origin',
      cache: 'no-store'
    });
""",
        'Načtení předpovědi bez cache',
    )

    text = replace_once(
        text,
        """        const url = `${CONFIG.chmiBase}10m-${CONFIG.stationId}-${date}.json`;
        const response = await fetch(url, {
          headers: { 'Accept': 'application/json' },
          credentials: 'same-origin'
        });
""",
        """        const url = cacheBusted(`${CONFIG.chmiBase}10m-${CONFIG.stationId}-${date}.json`);
        const response = await fetch(url, {
          headers: { 'Accept': 'application/json', 'Cache-Control': 'no-cache' },
          credentials: 'same-origin',
          cache: 'no-store'
        });
""",
        'Načtení ČHMÚ bez cache',
    )

    helper_anchor = """  function formatPragueDate(dayOffset) {
"""
    helpers = """  function cacheBusted(url) {
    const separator = String(url).includes('?') ? '&' : '?';
    return `${url}${separator}_weather=${Date.now()}`;
  }

  function isFreshTimestamp(value, maxAgeMinutes) {
    const timestamp = Date.parse(value);
    if (!Number.isFinite(timestamp)) return false;
    const age = Date.now() - timestamp;
    // Malý záporný rozdíl tolerujeme kvůli rozdílnému času serverů.
    return age >= -5 * 60 * 1000 && age <= maxAgeMinutes * 60 * 1000;
  }

  function formatPragueDate(dayOffset) {
"""
    text = replace_once(text, helper_anchor, helpers, 'Pomocné funkce čerstvosti')
    JS.write_text(text, encoding='utf-8', newline='\n')


def patch_loader() -> None:
    text = LOADER.read_text(encoding='utf-8')
    text, count = re.subn(r'/pocasi\.js\?v=[^"\']+', f'/pocasi.js?v={VERSION}', text)
    if count < 1:
        raise SystemExit('V ensure_weather_loader.py nebyla nalezena verze pocasi.js.')
    LOADER.write_text(text, encoding='utf-8', newline='\n')


def patch_pages() -> None:
    for path in PAGES:
        text = path.read_text(encoding='utf-8')
        pattern = r'(<script[^>]+data-nk-weather-direct="1"[^>]+src=")/pocasi\.js\?v=[^"\']+("[^>]*></script>)'
        replacement = rf'\1/pocasi.js?v={VERSION}\2'
        text, count = re.subn(pattern, replacement, text)
        if count == 0:
            loader = f'<script data-nk-weather-direct="1" data-nk-weather="direct" src="/pocasi.js?v={VERSION}" defer></script>'
            if '</body>' not in text:
                raise SystemExit(f'{path}: chybí </body>.')
            text = text.replace('</body>', loader + '\n</body>', 1)
        path.write_text(text, encoding='utf-8', newline='\n')


def validate() -> None:
    js = JS.read_text(encoding='utf-8')
    required = [MARKER, 'refreshMinutes: 5', 'observationMaxAgeMinutes: 45', "cache: 'no-store'", "visibilitychange", 'isFreshTimestamp']
    missing = [item for item in required if item not in js]
    if missing:
        raise SystemExit(f'Počasí po opravě postrádá: {missing}')
    for path in PAGES:
        text = path.read_text(encoding='utf-8')
        if f'/pocasi.js?v={VERSION}' not in text:
            raise SystemExit(f'{path}: chybí nová verze loaderu.')
        if text.count('data-nk-weather-direct="1"') != 1:
            raise SystemExit(f'{path}: loader počasí není právě jednou.')


def main() -> None:
    patch_js()
    patch_loader()
    patch_pages()
    validate()
    print('Živá aktualizace počasí je připravena k nasazení.')


if __name__ == '__main__':
    main()
