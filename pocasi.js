(() => {
  'use strict';

  const CONFIG = {
    latitude: 50.3760,
    longitude: 13.2713,
    altitude: 300,
    stationId: '0-20000-0-11438',
    stationName: 'Tušimice',
    forecastUrl: 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=50.3760&lon=13.2713&altitude=300',
    chmiBase: 'https://opendata.chmi.cz/meteorology/climate/now/data/',
    cacheKey: 'nasekadan-weather-v2',
    cacheMinutes: 30
  };

  const path = window.location.pathname.replace(/\/+$/, '') || '/';
  const isHome = path === '/';
  const isWeatherPage = path === '/pocasi';
  if (!isHome && !isWeatherPage) return;

  injectStyles();
  const target = isHome ? createStrip() : document.getElementById('weather-app');
  if (!target) return;

  const cached = readCache();
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

  async function loadWeather() {
    const [forecastResult, observationResult] = await Promise.allSettled([
      fetchForecast(),
      fetchObservation()
    ]);

    const forecast = forecastResult.status === 'fulfilled' ? forecastResult.value : null;
    const observation = observationResult.status === 'fulfilled' ? observationResult.value : null;
    if (!forecast && !observation) return null;

    return {
      fetchedAt: new Date().toISOString(),
      observation,
      forecast,
      source: {
        observation: observation ? 'ČHMÚ – stanice Tušimice' : null,
        forecast: forecast ? 'MET Norway – bodová předpověď pro Kadaň' : null
      }
    };
  }

  async function fetchForecast() {
    const response = await fetch(CONFIG.forecastUrl, {
      headers: { 'Accept': 'application/json' },
      mode: 'cors',
      credentials: 'omit'
    });
    if (!response.ok) throw new Error(`Forecast HTTP ${response.status}`);
    const json = await response.json();
    const timeseries = json && json.properties && Array.isArray(json.properties.timeseries)
      ? json.properties.timeseries
      : [];
    if (!timeseries.length) throw new Error('Forecast is empty');

    const now = Date.now();
    const future = timeseries.filter(item => Date.parse(item.time) >= now - 60 * 60 * 1000);
    const currentEntry = future[0] || timeseries[0];
    const currentDetails = currentEntry.data && currentEntry.data.instant
      ? currentEntry.data.instant.details || {}
      : {};
    const currentSymbol = getSymbol(currentEntry);

    const hourly = future.slice(0, 30).map(item => {
      const details = item.data && item.data.instant ? item.data.instant.details || {} : {};
      const next = pickNextPeriod(item.data || {});
      return {
        time: item.time,
        temperature: numberOrNull(details.air_temperature),
        feelsLike: calculateFeelsLike(details.air_temperature, details.wind_speed, details.relative_humidity),
        humidity: numberOrNull(details.relative_humidity),
        windSpeed: msToKmh(details.wind_speed),
        windDirection: numberOrNull(details.wind_from_direction),
        pressure: numberOrNull(details.air_pressure_at_sea_level),
        precipitation: numberOrNull(next.details && next.details.precipitation_amount),
        symbol: next.summary && next.summary.symbol_code ? next.summary.symbol_code : currentSymbol
      };
    });

    const dailyMap = new Map();
    future.slice(0, 24 * 9).forEach(item => {
      const details = item.data && item.data.instant ? item.data.instant.details || {} : {};
      const next = pickNextPeriod(item.data || {});
      const dayKey = localDateKey(item.time);
      if (!dailyMap.has(dayKey)) {
        dailyMap.set(dayKey, {
          date: dayKey,
          min: null,
          max: null,
          precipitation: 0,
          maxWind: 0,
          symbols: [],
          representative: null
        });
      }
      const day = dailyMap.get(dayKey);
      const temp = numberOrNull(details.air_temperature);
      if (temp !== null) {
        day.min = day.min === null ? temp : Math.min(day.min, temp);
        day.max = day.max === null ? temp : Math.max(day.max, temp);
      }
      const precipitation = numberOrNull(next.details && next.details.precipitation_amount);
      if (precipitation !== null) day.precipitation += precipitation;
      const wind = msToKmh(details.wind_speed);
      if (wind !== null) day.maxWind = Math.max(day.maxWind, wind);
      const symbol = next.summary && next.summary.symbol_code ? next.summary.symbol_code : null;
      if (symbol) day.symbols.push(symbol);
      const hour = localHour(item.time);
      if (hour >= 11 && hour <= 14 && symbol) day.representative = symbol;
    });

    const daily = Array.from(dailyMap.values()).slice(0, 8).map(day => ({
      date: day.date,
      min: round1(day.min),
      max: round1(day.max),
      precipitation: round1(day.precipitation),
      maxWind: Math.round(day.maxWind),
      symbol: day.representative || mostSignificantSymbol(day.symbols)
    }));

    return {
      updatedAt: json.properties && json.properties.meta ? json.properties.meta.updated_at : null,
      current: {
        time: currentEntry.time,
        temperature: numberOrNull(currentDetails.air_temperature),
        humidity: numberOrNull(currentDetails.relative_humidity),
        windSpeed: msToKmh(currentDetails.wind_speed),
        windDirection: numberOrNull(currentDetails.wind_from_direction),
        pressure: numberOrNull(currentDetails.air_pressure_at_sea_level),
        symbol: currentSymbol
      },
      hourly,
      daily
    };
  }

  async function fetchObservation() {
    const dates = [0, -1].map(offset => formatPragueDate(offset));
    for (const date of dates) {
      try {
        const url = `${CONFIG.chmiBase}10m-${CONFIG.stationId}-${date}.json`;
        const response = await fetch(url, {
          headers: { 'Accept': 'application/json' },
          mode: 'cors',
          credentials: 'omit'
        });
        if (!response.ok) continue;
        const json = await response.json();
        const parsed = parseChmiTable(json);
        if (parsed) return parsed;
      } catch (_) {
        // The previous day is tried automatically.
      }
    }
    throw new Error('CHMI observation unavailable');
  }

  function parseChmiTable(json) {
    const table = json && json.data && json.data.data ? json.data.data : (json && json.data ? json.data : json);
    if (!table || !Array.isArray(table.values)) return null;
    const header = Array.isArray(table.header)
      ? table.header.map(String)
      : String(table.header || '').split(',').map(value => value.trim());
    if (!header.length) return null;

    const normalized = header.map(normalizeKey);
    let elementIndex = normalized.findIndex(key => key.includes('EGELABBREVIATION'));
    if (elementIndex < 0) elementIndex = normalized.findIndex(key => key === 'ELEMENT' || key.includes('ABBREVIATION'));
    let valueIndex = normalized.findIndex(key => key === 'VALUE' || key === 'HODNOTA');
    if (valueIndex < 0) valueIndex = normalized.findIndex(key => key.includes('VALUE'));
    let timeIndex = normalized.findIndex(key => key.includes('DATE') || key.includes('DATUM') || key.includes('TIME'));

    const knownElements = new Set(['T', 'H', 'F', 'FPRUM', 'FMAX', 'D', 'DPRUM', 'P', 'SRA10M']);
    const records = [];

    table.values.forEach(row => {
      if (!Array.isArray(row)) return;
      let elIndex = elementIndex;
      if (elIndex < 0) elIndex = row.findIndex(value => knownElements.has(String(value).toUpperCase()));
      const element = elIndex >= 0 ? String(row[elIndex]).toUpperCase() : '';
      if (!knownElements.has(element)) return;

      let tsIndex = timeIndex;
      if (tsIndex < 0) tsIndex = row.findIndex(value => typeof value === 'string' && !Number.isNaN(Date.parse(value)));
      const time = tsIndex >= 0 ? row[tsIndex] : null;
      if (!time || Number.isNaN(Date.parse(time))) return;

      let valIndex = valueIndex;
      if (valIndex < 0 && elIndex >= 0) {
        for (let i = elIndex + 1; i < row.length; i += 1) {
          if (typeof row[i] === 'number' || (typeof row[i] === 'string' && row[i].trim() !== '' && !Number.isNaN(Number(row[i])))) {
            valIndex = i;
            break;
          }
        }
      }
      const value = valIndex >= 0 ? numberOrNull(row[valIndex]) : null;
      if (value === null) return;
      records.push({ time, element, value });
    });

    if (!records.length) return null;
    records.sort((a, b) => Date.parse(a.time) - Date.parse(b.time));
    const latestTemperature = [...records].reverse().find(record => record.element === 'T');
    if (!latestTemperature) return null;
    const cutoff = Date.parse(latestTemperature.time) - 20 * 60 * 1000;
    const recent = records.filter(record => Date.parse(record.time) >= cutoff);
    const latest = element => [...recent].reverse().find(record => record.element === element);
    const wind = latest('FPRUM') || latest('F');
    const direction = latest('DPRUM') || latest('D');
    const rainRecent = recent.filter(record => record.element === 'SRA10M').reduce((sum, record) => sum + record.value, 0);

    return {
      station: CONFIG.stationName,
      time: latestTemperature.time,
      temperature: latestTemperature.value,
      humidity: latest('H') ? latest('H').value : null,
      windSpeed: wind ? msToKmh(wind.value) : null,
      windDirection: direction ? direction.value : null,
      windGust: latest('FMAX') ? msToKmh(latest('FMAX').value) : null,
      pressureStation: latest('P') ? latest('P').value : null,
      rainLast20Minutes: round1(rainRecent)
    };
  }

  function createStrip() {
    if (document.getElementById('weather-strip')) return document.getElementById('weather-strip');
    const strip = document.createElement('section');
    strip.id = 'weather-strip';
    strip.className = 'nk-weather-strip';
    strip.setAttribute('aria-label', 'Aktuální počasí v Kadani');
    strip.innerHTML = '<div class="wrap nk-weather-loading">Načítám aktuální počasí pro Kadaň…</div>';
    const ticker = document.querySelector('.ticker');
    if (ticker) ticker.insertAdjacentElement('afterend', strip);
    else {
      const header = document.querySelector('header');
      if (header) header.insertAdjacentElement('afterend', strip);
    }
    return strip;
  }

  function render(target, data, fromCache) {
    if (isHome) renderStrip(target, data, fromCache);
    else renderPage(target, data, fromCache);
  }

  function renderStrip(target, data, fromCache) {
    const current = currentValues(data);
    const today = data.forecast && data.forecast.daily ? data.forecast.daily[0] : null;
    const tomorrow = data.forecast && data.forecast.daily ? data.forecast.daily[1] : null;
    const symbol = describeSymbol(current.symbol);
    const observationLabel = data.observation ? `měření ${CONFIG.stationName}` : 'bodová předpověď';
    target.innerHTML = `
      <div class="wrap nk-weather-strip__inner">
        <a class="nk-weather-strip__now" href="/pocasi/" aria-label="Otevřít podrobnou předpověď počasí">
          <span class="nk-weather-icon" aria-hidden="true">${symbol.icon}</span>
          <span><b>Kadaň právě teď</b><small>${escapeHtml(observationLabel)}</small></span>
          <strong>${formatTemperature(current.temperature)}</strong>
          <span class="nk-weather-condition">${escapeHtml(symbol.label)}</span>
        </a>
        <div class="nk-weather-strip__facts">
          ${current.windSpeed !== null ? `<span>Vítr <b>${Math.round(current.windSpeed)} km/h</b></span>` : ''}
          ${current.humidity !== null ? `<span>Vlhkost <b>${Math.round(current.humidity)} %</b></span>` : ''}
          ${today ? `<span>Dnes <b>${formatTemperature(today.max)} / ${formatTemperature(today.min)}</b></span>` : ''}
          ${tomorrow ? `<span>Zítra <b>${formatTemperature(tomorrow.max)} / ${formatTemperature(tomorrow.min)}</b></span>` : ''}
        </div>
        <a class="nk-weather-strip__link" href="/pocasi/">Podrobná předpověď →</a>
      </div>
      ${fromCache ? '<span class="nk-weather-cache-note">Zobrazeny poslední uložené údaje</span>' : ''}
    `;
  }

  function renderPage(target, data, fromCache) {
    const current = currentValues(data);
    const symbol = describeSymbol(current.symbol);
    const hourly = data.forecast && data.forecast.hourly ? data.forecast.hourly.slice(0, 24) : [];
    const daily = data.forecast && data.forecast.daily ? data.forecast.daily.slice(0, 7) : [];
    const updated = current.time || data.fetchedAt;
    const sourceParts = [data.source && data.source.observation, data.source && data.source.forecast].filter(Boolean);

    target.innerHTML = `
      <section class="nk-weather-hero">
        <div>
          <p class="nk-weather-eyebrow">AKTUÁLNÍ POČASÍ V KADANI</p>
          <div class="nk-weather-current">
            <span class="nk-weather-current__icon" aria-hidden="true">${symbol.icon}</span>
            <div><strong>${formatTemperature(current.temperature)}</strong><span>${escapeHtml(symbol.label)}</span></div>
          </div>
          <p class="nk-weather-measurement">${data.observation ? `Skutečné měření stanice ČHMÚ ${CONFIG.stationName}` : 'Aktuální hodnota z bodové předpovědi pro Kadaň'}</p>
        </div>
        <dl class="nk-weather-metrics">
          ${metric('Pocitově', formatTemperature(current.feelsLike))}
          ${metric('Vlhkost', current.humidity !== null ? `${Math.round(current.humidity)} %` : '—')}
          ${metric('Vítr', current.windSpeed !== null ? `${Math.round(current.windSpeed)} km/h ${windDirection(current.windDirection)}` : '—')}
          ${metric('Nárazy', current.windGust !== null ? `${Math.round(current.windGust)} km/h` : '—')}
          ${metric('Tlak', current.pressure !== null ? `${Math.round(current.pressure)} hPa` : '—')}
          ${metric('Aktualizace', formatDateTime(updated))}
        </dl>
      </section>

      ${daily.length ? `
      <section class="nk-weather-section">
        <div class="nk-weather-section__head"><div><p class="nk-weather-eyebrow">VÝHLED</p><h2>Předpověď na sedm dní</h2></div><p>Nejspolehlivější je nejbližších 24 až 72 hodin. U dalších dnů počítejte s možnou změnou.</p></div>
        <div class="nk-weather-days">
          ${daily.map((day, index) => dayCard(day, index)).join('')}
        </div>
      </section>` : ''}

      ${hourly.length ? `
      <section class="nk-weather-section">
        <div class="nk-weather-section__head"><div><p class="nk-weather-eyebrow">HODINU PO HODINĚ</p><h2>Nejbližších 24 hodin</h2></div><p>Teplota, srážky a vítr přímo pro souřadnice Kadaně.</p></div>
        <div class="nk-weather-hours" tabindex="0" aria-label="Hodinová předpověď">
          ${hourly.map(hourCard).join('')}
        </div>
      </section>` : ''}

      <section class="nk-weather-source">
        <h2>Odkud údaje pocházejí</h2>
        <p>${escapeHtml(sourceParts.join(' · '))}. Aktuální měření je převzato z desetiminutových otevřených dat ČHMÚ. Bodová předpověď je počítána pro střed Kadaně v nadmořské výšce přibližně 300 metrů.</p>
        <p><a href="https://www.chmi.cz/" rel="noopener noreferrer">ČHMÚ</a> · <a href="https://api.met.no/" rel="noopener noreferrer">MET Norway</a> · data pod licencí CC BY 4.0.</p>
        ${fromCache ? '<p class="nk-weather-warning">Zdroj je právě nedostupný, proto jsou zobrazeny poslední uložené údaje.</p>' : ''}
      </section>
    `;
  }

  function currentValues(data) {
    const observation = data.observation || {};
    const forecastCurrent = data.forecast && data.forecast.current ? data.forecast.current : {};
    const temperature = firstNumber(observation.temperature, forecastCurrent.temperature);
    const humidity = firstNumber(observation.humidity, forecastCurrent.humidity);
    const windSpeed = firstNumber(observation.windSpeed, forecastCurrent.windSpeed);
    const windDirectionValue = firstNumber(observation.windDirection, forecastCurrent.windDirection);
    const pressure = firstNumber(forecastCurrent.pressure, observation.pressureStation);
    return {
      time: observation.time || forecastCurrent.time || data.fetchedAt,
      temperature,
      humidity,
      windSpeed,
      windDirection: windDirectionValue,
      windGust: firstNumber(observation.windGust),
      pressure,
      feelsLike: calculateFeelsLike(temperature, windSpeed !== null ? windSpeed / 3.6 : null, humidity),
      symbol: forecastCurrent.symbol || 'cloudy'
    };
  }

  function dayCard(day, index) {
    const symbol = describeSymbol(day.symbol);
    return `<article class="nk-weather-day${index === 0 ? ' is-today' : ''}">
      <span class="nk-weather-day__name">${index === 0 ? 'Dnes' : formatWeekday(day.date)}</span>
      <span class="nk-weather-day__date">${formatShortDate(day.date)}</span>
      <span class="nk-weather-day__icon" aria-hidden="true">${symbol.icon}</span>
      <strong>${formatTemperature(day.max)} <small>${formatTemperature(day.min)}</small></strong>
      <span>${escapeHtml(symbol.label)}</span>
      <span class="nk-weather-day__details">Déšť ${formatMillimetres(day.precipitation)} · vítr do ${day.maxWind || 0} km/h</span>
    </article>`;
  }

  function hourCard(hour) {
    const symbol = describeSymbol(hour.symbol);
    return `<article class="nk-weather-hour">
      <time datetime="${escapeHtml(hour.time)}">${formatHour(hour.time)}</time>
      <span class="nk-weather-hour__icon" aria-hidden="true">${symbol.icon}</span>
      <strong>${formatTemperature(hour.temperature)}</strong>
      <span>${formatMillimetres(hour.precipitation)}</span>
      <small>${hour.windSpeed !== null ? `${Math.round(hour.windSpeed)} km/h` : '—'}</small>
    </article>`;
  }

  function metric(label, value) {
    return `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`;
  }

  function renderError(target) {
    target.innerHTML = isHome
      ? '<div class="wrap nk-weather-loading">Počasí je nyní dočasně nedostupné. <a href="/pocasi/">Otevřít stránku počasí</a></div>'
      : '<div class="nk-weather-error"><h2>Údaje se nepodařilo načíst</h2><p>Zkuste stránku obnovit později. Ostatní obsah webu tím není ovlivněn.</p></div>';
  }

  function pickNextPeriod(data) {
    return data.next_1_hours || data.next_6_hours || data.next_12_hours || { summary: {}, details: {} };
  }

  function getSymbol(entry) {
    const next = pickNextPeriod(entry.data || {});
    return next.summary && next.summary.symbol_code ? next.summary.symbol_code : 'cloudy';
  }

  function describeSymbol(code) {
    const clean = String(code || 'cloudy').replace(/_(day|night|polartwilight)$/, '');
    const dictionary = {
      clearsky: ['Jasno', '☀️'], fair: ['Skoro jasno', '🌤️'], partlycloudy: ['Polojasno', '⛅'], cloudy: ['Zataženo', '☁️'], fog: ['Mlha', '🌫️'],
      lightrain: ['Slabý déšť', '🌦️'], rain: ['Déšť', '🌧️'], heavyrain: ['Silný déšť', '🌧️'], lightrainshowers: ['Slabé přeháňky', '🌦️'], rainshowers: ['Přeháňky', '🌦️'], heavyrainshowers: ['Silné přeháňky', '🌧️'],
      lightsleet: ['Slabý déšť se sněhem', '🌨️'], sleet: ['Déšť se sněhem', '🌨️'], heavysleet: ['Silný déšť se sněhem', '🌨️'], lightsnow: ['Slabé sněžení', '🌨️'], snow: ['Sněžení', '❄️'], heavysnow: ['Silné sněžení', '❄️'],
      lightsnowshowers: ['Slabé sněhové přeháňky', '🌨️'], snowshowers: ['Sněhové přeháňky', '🌨️'], heavysnowshowers: ['Silné sněhové přeháňky', '❄️'],
      lightrainandthunder: ['Slabý déšť a bouřky', '⛈️'], rainandthunder: ['Déšť a bouřky', '⛈️'], heavyrainandthunder: ['Silný déšť a bouřky', '⛈️'], lightrainshowersandthunder: ['Přeháňky a bouřky', '⛈️'], rainshowersandthunder: ['Přeháňky a bouřky', '⛈️'], heavyrainshowersandthunder: ['Silné bouřky', '⛈️'],
      lightsleetandthunder: ['Déšť se sněhem a bouřky', '⛈️'], sleetandthunder: ['Déšť se sněhem a bouřky', '⛈️'], heavysleetandthunder: ['Silné srážky a bouřky', '⛈️'], lightsnowandthunder: ['Sněžení a bouřky', '⛈️'], snowandthunder: ['Sněžení a bouřky', '⛈️'], heavysnowandthunder: ['Silné sněžení a bouřky', '⛈️']
    };
    const item = dictionary[clean] || ['Proměnlivo', '🌥️'];
    return { label: item[0], icon: item[1] };
  }

  function mostSignificantSymbol(symbols) {
    if (!symbols.length) return 'cloudy';
    const weight = symbol => {
      const s = String(symbol);
      if (s.includes('thunder')) return 100;
      if (s.includes('heavysnow') || s.includes('heavyrain')) return 90;
      if (s.includes('snow') || s.includes('sleet')) return 80;
      if (s.includes('rain')) return 70;
      if (s.includes('fog')) return 60;
      if (s.includes('cloudy')) return 50;
      if (s.includes('partlycloudy')) return 40;
      if (s.includes('fair')) return 30;
      return 20;
    };
    return [...symbols].sort((a, b) => weight(b) - weight(a))[0];
  }

  function calculateFeelsLike(tempValue, windValueMs, humidityValue) {
    const temp = numberOrNull(tempValue);
    const windMs = numberOrNull(windValueMs);
    const humidity = numberOrNull(humidityValue);
    if (temp === null) return null;
    if (temp <= 10 && windMs !== null && windMs > 1.3) {
      const windKmh = windMs * 3.6;
      return round1(13.12 + 0.6215 * temp - 11.37 * Math.pow(windKmh, 0.16) + 0.3965 * temp * Math.pow(windKmh, 0.16));
    }
    if (temp >= 27 && humidity !== null) {
      const c1 = -8.78469475556, c2 = 1.61139411, c3 = 2.33854883889, c4 = -0.14611605, c5 = -0.012308094, c6 = -0.0164248277778, c7 = 0.002211732, c8 = 0.00072546, c9 = -0.000003582;
      return round1(c1 + c2 * temp + c3 * humidity + c4 * temp * humidity + c5 * temp * temp + c6 * humidity * humidity + c7 * temp * temp * humidity + c8 * temp * humidity * humidity + c9 * temp * temp * humidity * humidity);
    }
    return round1(temp);
  }

  function formatPragueDate(dayOffset) {
    const date = new Date(Date.now() + dayOffset * 86400000);
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Prague', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(date).reduce((acc, part) => { acc[part.type] = part.value; return acc; }, {});
    return `${parts.year}${parts.month}${parts.day}`;
  }

  function localDateKey(iso) {
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Prague', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date(iso)).reduce((acc, part) => { acc[part.type] = part.value; return acc; }, {});
    return `${parts.year}-${parts.month}-${parts.day}`;
  }

  function localHour(iso) { return Number(new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Prague', hour: '2-digit', hourCycle: 'h23' }).format(new Date(iso))); }
  function formatHour(iso) { return new Intl.DateTimeFormat('cs-CZ', { timeZone: 'Europe/Prague', hour: '2-digit', minute: '2-digit' }).format(new Date(iso)); }
  function formatDateTime(iso) { return !iso || Number.isNaN(Date.parse(iso)) ? '—' : new Intl.DateTimeFormat('cs-CZ', { timeZone: 'Europe/Prague', day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(iso)); }
  function formatWeekday(dateKey) { return new Intl.DateTimeFormat('cs-CZ', { weekday: 'short', timeZone: 'Europe/Prague' }).format(new Date(`${dateKey}T12:00:00+02:00`)).replace('.', ''); }
  function formatShortDate(dateKey) { return new Intl.DateTimeFormat('cs-CZ', { day: 'numeric', month: 'numeric', timeZone: 'Europe/Prague' }).format(new Date(`${dateKey}T12:00:00+02:00`)); }
  function windDirection(degrees) { if (degrees === null || typeof degrees === 'undefined') return ''; const labels = ['S', 'SV', 'V', 'JV', 'J', 'JZ', 'Z', 'SZ']; return labels[Math.round(Number(degrees) / 45) % 8]; }
  function formatTemperature(value) { return value === null || typeof value === 'undefined' || Number.isNaN(Number(value)) ? '—' : `${Math.round(Number(value))} °C`; }
  function formatMillimetres(value) { const number = numberOrNull(value); return number === null ? '—' : `${number < 0.1 ? '0' : round1(number).toLocaleString('cs-CZ')} mm`; }
  function msToKmh(value) { const number = numberOrNull(value); return number === null ? null : number * 3.6; }
  function firstNumber(...values) { for (const value of values) { const number = numberOrNull(value); if (number !== null) return number; } return null; }
  function numberOrNull(value) { if (value === null || typeof value === 'undefined' || value === '') return null; const number = Number(value); return Number.isFinite(number) ? number : null; }
  function round1(value) { const number = numberOrNull(value); return number === null ? null : Math.round(number * 10) / 10; }
  function normalizeKey(value) { return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]/g, '').toUpperCase(); }
  function escapeHtml(value) { return String(value === null || typeof value === 'undefined' ? '' : value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;'); }

  function readCache() {
    try {
      const raw = localStorage.getItem(CONFIG.cacheKey);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.savedAt || !parsed.data) return null;
      if (Date.now() - parsed.savedAt > 12 * 60 * 60 * 1000) return null;
      return parsed.data;
    } catch (_) { return null; }
  }

  function writeCache(data) {
    try { localStorage.setItem(CONFIG.cacheKey, JSON.stringify({ savedAt: Date.now(), data })); } catch (_) { /* Weather also works without local storage. */ }
  }

  function injectStyles() {
    if (document.getElementById('nk-weather-styles')) return;
    const style = document.createElement('style');
    style.id = 'nk-weather-styles';
    style.textContent = `
      .nk-weather-strip{background:#eef3f5;border-bottom:1px solid #d8e0e4;color:#13232d;position:relative}.nk-weather-strip__inner{min-height:72px;display:grid;grid-template-columns:minmax(280px,1.35fr) minmax(380px,2fr) auto;align-items:center;gap:24px}.nk-weather-strip__now{display:flex;align-items:center;gap:11px;min-width:0}.nk-weather-strip__now b{display:block;font-size:14px}.nk-weather-strip__now small{display:block;color:#63727b;font-size:11px}.nk-weather-icon{font-size:30px;line-height:1}.nk-weather-strip__now strong{font:900 25px/1 Georgia,serif;white-space:nowrap}.nk-weather-condition{font-size:14px;color:#52616a;white-space:nowrap}.nk-weather-strip__facts{display:flex;align-items:center;justify-content:center;gap:21px;font-size:13px}.nk-weather-strip__facts span{white-space:nowrap;color:#5a6870}.nk-weather-strip__facts b{color:#172a35}.nk-weather-strip__link{color:#9f2626;font-size:13px;font-weight:900;white-space:nowrap}.nk-weather-loading{min-height:64px;display:flex;align-items:center;font-weight:750}.nk-weather-loading a{color:#9f2626}.nk-weather-cache-note{position:absolute;right:16px;bottom:1px;color:#718089;font-size:10px}
      .weather-page{padding-top:46px;padding-bottom:72px}.weather-page h1{font:900 clamp(42px,6vw,68px)/1.02 Georgia,serif;margin:.18em 0}.weather-page__intro{max-width:760px;color:#52616a;font-size:18px;margin-bottom:30px}.nk-weather-hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(420px,1fr);gap:28px;background:linear-gradient(135deg,#122a38,#315a6c 63%,#9f2626);color:#fff;border-radius:24px;padding:36px;box-shadow:0 22px 58px rgba(18,35,45,.18)}.nk-weather-eyebrow{margin:0;color:#ffd5d5;font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.nk-weather-current{display:flex;align-items:center;gap:19px;margin:15px 0}.nk-weather-current__icon{font-size:76px;line-height:1}.nk-weather-current strong{display:block;font:900 clamp(56px,8vw,82px)/.92 Georgia,serif}.nk-weather-current span{display:block;color:#e7eff3;font-size:19px}.nk-weather-measurement{margin:0;color:#dbe8ed;font-size:14px}.nk-weather-metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:0}.nk-weather-metrics div{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.16);border-radius:15px;padding:15px}.nk-weather-metrics dt{color:#cbdde5;font-size:12px}.nk-weather-metrics dd{margin:3px 0 0;font-size:19px;font-weight:900}
      .nk-weather-section{margin-top:48px}.nk-weather-section__head{display:flex;justify-content:space-between;align-items:end;gap:28px;margin-bottom:20px}.nk-weather-section__head .nk-weather-eyebrow{color:#a9232b}.nk-weather-section__head h2,.nk-weather-source h2{font:850 36px/1.08 Georgia,serif;margin:5px 0 0}.nk-weather-section__head>p{max-width:540px;margin:0;color:#65727a}.nk-weather-days{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:11px}.nk-weather-day{display:flex;flex-direction:column;align-items:center;text-align:center;min-width:0;padding:18px 10px;border:1px solid #dde3e6;border-radius:17px;background:#fff;box-shadow:0 10px 28px rgba(18,35,45,.06)}.nk-weather-day.is-today{border-color:#a9232b;box-shadow:inset 0 4px 0 #a9232b,0 10px 28px rgba(18,35,45,.08)}.nk-weather-day__name{font-weight:900;text-transform:capitalize}.nk-weather-day__date{font-size:12px;color:#76838a}.nk-weather-day__icon{font-size:37px;margin:10px 0}.nk-weather-day strong{font-size:21px}.nk-weather-day strong small{font-size:15px;color:#6d7980}.nk-weather-day>span:not(.nk-weather-day__icon):not(.nk-weather-day__name):not(.nk-weather-day__date):not(.nk-weather-day__details){font-size:12px;color:#53616a}.nk-weather-day__details{margin-top:9px;color:#77838a;font-size:10px;line-height:1.35}.nk-weather-hours{display:flex;gap:10px;overflow-x:auto;padding:2px 2px 14px;scroll-snap-type:x proximity}.nk-weather-hour{min-width:106px;scroll-snap-align:start;text-align:center;background:#fff;border:1px solid #dde3e6;border-radius:15px;padding:14px 10px}.nk-weather-hour time{display:block;font-weight:900}.nk-weather-hour__icon{display:block;font-size:29px;margin:8px 0}.nk-weather-hour strong{display:block;font-size:19px}.nk-weather-hour>span:not(.nk-weather-hour__icon){display:block;color:#4d6571;font-size:12px}.nk-weather-hour small{color:#78858c}.nk-weather-source{margin-top:46px;padding:28px;border-radius:20px;background:#f3efe7}.nk-weather-source p{color:#53616a}.nk-weather-source a{color:#9f2626;font-weight:850}.nk-weather-warning{padding:11px 13px;background:#fff5d8;border-radius:10px;color:#6b4b00!important}.nk-weather-error{padding:35px;border-radius:20px;background:#fff;border:1px solid #dde3e6}
      @media(max-width:1050px){.nk-weather-strip__inner{grid-template-columns:1fr auto}.nk-weather-strip__facts{grid-column:1/-1;justify-content:flex-start;padding-bottom:13px;margin-top:-14px}.nk-weather-days{grid-template-columns:repeat(4,minmax(0,1fr))}}@media(max-width:760px){.nk-weather-strip__inner{display:flex;flex-wrap:wrap;gap:9px 16px;padding:10px 0}.nk-weather-strip__now{flex:1 1 260px}.nk-weather-condition{display:none}.nk-weather-strip__facts{order:3;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));width:100%;gap:4px 12px;padding:6px 0 3px;margin:0;border-top:1px solid #d8e0e4}.nk-weather-strip__link{margin-left:auto}.nk-weather-cache-note{display:none}.weather-page{padding-top:30px}.nk-weather-hero{grid-template-columns:1fr;padding:25px}.nk-weather-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.nk-weather-days{display:flex;overflow-x:auto;padding-bottom:12px}.nk-weather-day{min-width:145px}.nk-weather-section__head{display:block}.nk-weather-section__head>p{margin-top:9px}.nk-weather-section__head h2,.nk-weather-source h2{font-size:30px}}@media(max-width:430px){.nk-weather-current__icon{font-size:58px}.nk-weather-current strong{font-size:58px}.nk-weather-metrics{grid-template-columns:1fr 1fr}.nk-weather-metrics dd{font-size:16px}.nk-weather-strip__now strong{font-size:22px}}
    `;
    document.head.appendChild(style);
  }
})();
