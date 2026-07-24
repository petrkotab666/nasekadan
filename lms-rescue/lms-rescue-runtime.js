(() => {
  "use strict";

  const BUILD = "20260724-rescue-runtime-1";
  const ORIGIN = "https://catalog.57-129-43-215.sslip.io";
  const BASE = `${ORIGIN}/assets/catalog-v7`;
  const PAGE_SIZE = 36;
  const state = { manifest: null, total: 0, offers: [], results: [], loadedKeys: new Set(), busy: false };
  const normalize = (value) => String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("cs-CZ").replace(/[^a-z0-9]+/g, " ").trim();
  const clean = (value) => String(value ?? "").replace(/\s+/g, " ").trim();
  const fmt = (value) => new Intl.NumberFormat("cs-CZ").format(Number(value || 0));
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", init, { once: true }) : init();

  async function init() {
    document.documentElement.dataset.rescueRuntime = BUILD;
    const main = document.querySelector("main#hlavni-obsah") || document.querySelector("main");
    const search = document.querySelector("#nabidky");
    const results = document.querySelector("#vysledky");
    const form = document.querySelector("#catalogFilterV3");
    const grid = document.querySelector("#offersGrid");
    const info = document.querySelector("#resultInfo");
    if (!main || !search || !results || !form || !grid || !info) return;

    if (main.firstElementChild !== search) main.prepend(search);
    if (search.nextElementSibling !== results) search.insertAdjacentElement("afterend", results);
    installStyles();
    enforceAdvertising(results);

    form.className = "catalog-filter-v7 lms-rescue-filter";
    form.dataset.bootstrapState = "loading";
    form.setAttribute("aria-busy", "true");
    form.innerHTML = `<div class="cf7-loading-results">Načítám celkový katalog a filtry…</div>`;
    grid.innerHTML = `<div class="empty-state">Vyberte alespoň jednu podmínku ve vyhledávači.</div>`;
    info.textContent = "Připravuji katalog…";

    try {
      state.manifest = await fetchJson(`${BASE}/manifest.json?build=${Date.now()}`);
      state.total = Number(state.manifest?.totalOffers || 0);
      if (!(state.total > 2000000)) throw new Error(`Manifest obsahuje jen ${fmt(state.total)} nabídek.`);
      buildForm(form);
      bind(form);
      form.dataset.catalogTotalOffers = String(state.total);
      form.dataset.bootstrapState = "ready";
      form.dataset.allFiltersPreserved = "1";
      form.setAttribute("aria-busy", "false");
      info.textContent = `Celý katalog obsahuje ${fmt(state.total)} nabídek. Vyberte zemi nebo jiný filtr.`;
      document.dispatchEvent(new CustomEvent("lms:catalog-v7-ready", { detail: { offers: state.total, totalOffers: state.total, rescue: BUILD } }));
    } catch (error) {
      console.error("Nouzový katalog:", error);
      form.dataset.bootstrapState = "error";
      form.setAttribute("aria-busy", "false");
      form.innerHTML = `<div class="cf7-error"><strong>Vyhledávač se nepodařilo načíst.</strong><span>${esc(error?.message || error)}</span><button type="button" onclick="location.reload()">Načíst znovu</button></div>`;
      info.textContent = "Katalog se nepodařilo načíst.";
    }
  }

  function installStyles() {
    if (document.querySelector("#lms-rescue-style")) return;
    const style = document.createElement("style");
    style.id = "lms-rescue-style";
    style.textContent = `
      .lms-rescue-filter{display:grid;gap:1rem}.lms-rescue-filter .rescue-head{display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;flex-wrap:wrap}.lms-rescue-filter .rescue-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.75rem}.lms-rescue-filter details{border:1px solid #d9e3ec;border-radius:12px;background:#fff;overflow:hidden}.lms-rescue-filter summary{cursor:pointer;padding:.8rem 1rem;font-weight:700;display:flex;justify-content:space-between}.lms-rescue-filter .rescue-options{max-height:250px;overflow:auto;padding:0 .8rem .8rem;display:grid;gap:.35rem}.lms-rescue-filter label{display:flex;gap:.5rem;align-items:center}.lms-rescue-filter label span{flex:1}.lms-rescue-filter .rescue-range{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.6rem}.lms-rescue-filter input,.lms-rescue-filter select{max-width:100%;padding:.6rem;border:1px solid #bac9d6;border-radius:8px}.lms-rescue-filter .rescue-actions{position:sticky;bottom:0;z-index:4;background:#fff;border:1px solid #d9e3ec;border-radius:12px;padding:.8rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;box-shadow:0 -4px 18px rgba(20,45,70,.08)}.lms-rescue-filter button{cursor:pointer}.lms-rescue-ad{margin-top:1.5rem}.lms-rescue-ad a{display:block;padding:1.25rem;border-radius:16px;border:1px solid #d9e3ec;text-decoration:none;background:#fff}.lms-rescue-ad strong{display:block;font-size:1.25rem;margin:.25rem 0}.lms-rescue-filter .rescue-muted{color:#65778b;font-size:.86rem}.lms-rescue-filter .is-unavailable{opacity:.45}.lms-rescue-filter .rescue-query{display:grid;grid-template-columns:minmax(220px,1fr) minmax(170px,260px);gap:.7rem}@media(max-width:700px){.lms-rescue-filter .rescue-query{grid-template-columns:1fr}.lms-rescue-filter .rescue-actions{align-items:stretch;flex-direction:column}.lms-rescue-filter .rescue-actions button{width:100%}}
    `;
    document.head.append(style);
  }

  function buildForm(form) {
    const countries = facetEntries("countries", countryEntries());
    const providers = facetEntries("providers");
    const departures = facetEntries("departures");
    form.innerHTML = `
      <div class="rescue-head"><div><p class="eyebrow">Celý katalog: ${fmt(state.total)} nabídek</p><h3>Najděte dovolenou podle všech parametrů</h3><p>Po výběru se načtou odpovídající části celého katalogu.</p></div><button type="button" data-reset>Vymazat vše</button></div>
      <div class="rescue-query"><label>Hledat<input type="search" name="query" placeholder="Země, oblast, hotel nebo partner"></label><label>Řazení<select name="sort"><option value="recommended">Doporučené</option><option value="price">Nejnižší cena</option><option value="date">Nejbližší termín</option><option value="rating">Nejlepší hodnocení</option><option value="discount">Největší sleva</option></select></label></div>
      <div class="rescue-grid">
        ${group("countries", "Země", countries, true)}
        ${group("regions", "Oblast", [], false, "Načte se po výběru země")}
        ${group("resorts", "Letovisko", [], false, "Načte se po výběru země")}
        ${group("hotels", "Hotel", [], false, "Načte se po výběru země")}
        ${group("tripTypes", "Typ zájezdu", [["stay","Pobytová dovolená"],["sightseeing","Poznávací zájezd"],["city-break","Eurovíkend"],["skiing","Lyžování"],["sports","Sportovní zájezd"]])}
        ${group("sports", "Sport", [["football","Fotbal"],["formula-1","Formule 1"],["running","Běžecké závody"],["other","Ostatní sport"]])}
        ${group("transports", "Doprava", [["flight","Letecky"],["bus","Autobusem"],["own","Vlastní doprava"],["train","Vlakem"],["other","Jiná doprava"]])}
        ${group("departures", "Odletové letiště", departures.length ? departures : [["Praha","Praha"],["Brno","Brno"],["Ostrava","Ostrava"],["Vídeň","Vídeň"],["Katovice","Katovice"]])}
        ${group("providers", "Nabídka u", providers)}
        ${group("boards", "Strava", [["all-inclusive","All inclusive"],["full-board","Plná penze"],["half-board","Polopenze"],["breakfast","Snídaně"],["no-meals","Bez stravy"],["other","Jiná / neuvedená"]])}
        ${group("categories", "Termín odjezdu", [["depart-3-days","Odjezd do 3 dnů"],["super-last-minute","Odjezd do týdne"],["last-minute","Odjezd za 8–30 dnů"],["first-minute","First minute"],["standard","Ostatní termíny"]])}
        ${group("freshness", "Aktuálnost nabídky", [["today","Ověřeno dnes"],["recent","Ověřeno do 3 dnů"],["week","Ověřeno tento týden"],["older","Starší kontrola"],["unknown","Aktuálnost neuvedena"]])}
        ${group("travelers", "Složení cestujících", [["solo","1 dospělý"],["couple","2 dospělí"],["parent-1","1 dospělý + 1 dítě"],["parent-2","1 dospělý + 2 děti"],["family-1","2 dospělí + 1 dítě"],["family-2","2 dospělí + 2 děti"],["family-3","2 dospělí + 3 děti"]])}
      </div>
      <div class="rescue-range">
        <label>Cena od<input type="number" name="minPrice" min="0" step="500"></label><label>Cena do<input type="number" name="maxPrice" min="0" step="500"></label>
        <label>Termín od<input type="date" name="dateFrom"></label><label>Termín do<input type="date" name="dateTo"></label>
        <label>Nocí od<input type="number" name="minNights" min="1" max="60"></label><label>Nocí do<input type="number" name="maxNights" min="1" max="60"></label>
        <label>Hodnocení od<select name="minRating"><option value="">Bez omezení</option><option value="7">7/10</option><option value="8">8/10</option><option value="9">9/10</option></select></label>
        <label>Sleva od<select name="minDiscount"><option value="">Bez omezení</option><option value="10">10 %</option><option value="20">20 %</option><option value="30">30 %</option><option value="40">40 %</option></select></label>
      </div>
      <div class="rescue-actions"><div><strong data-search-status>Bez omezení · ${fmt(state.total)} nabídek v celém katalogu</strong><div class="rescue-muted">Vyberte alespoň jednu podmínku.</div></div><button type="button" class="btn primary" data-search>Vyhledat v ${fmt(state.total)} nabídkách</button></div>`;
  }

  function group(name, label, rows, open = false, emptyText = "") {
    const options = rows.length ? rows.map(([value, text, count]) => `<label data-value="${esc(value)}"><input type="checkbox" name="${esc(name)}" value="${esc(value)}"><span>${esc(text)}</span><b>${count == null ? "" : fmt(count)}</b></label>`).join("") : `<div class="rescue-muted">${esc(emptyText || "Možnosti se doplní podle výběru.")}</div>`;
    return `<details data-group="${esc(name)}"${open ? " open" : ""}><summary><span>${esc(label)}</span><b data-selected>0</b></summary><div class="rescue-options">${options}</div></details>`;
  }

  function facetEntries(name, fallback = []) {
    const raw = state.manifest?.facets?.[name];
    if (!Array.isArray(raw) || !raw.length) return fallback;
    return raw.map((row) => [clean(row?.value), clean(row?.label || row?.value), Number(row?.count || 0)]).filter((row) => row[0]).sort((a,b) => b[2]-a[2] || a[1].localeCompare(b[1], "cs"));
  }

  function countryEntries() {
    const counts = new Map();
    for (const item of state.manifest?.chunks || []) {
      const country = clean(item?.country);
      if (country) counts.set(country, (counts.get(country) || 0) + Number(item?.offers || 0));
    }
    for (const country of Object.keys(state.manifest?.countryChunks || {})) if (!counts.has(country)) counts.set(country, 0);
    return [...counts].map(([value,count]) => [value,value,count]).sort((a,b) => b[2]-a[2] || a[0].localeCompare(b[0], "cs"));
  }

  function bind(form) {
    let timer;
    form.addEventListener("change", () => { updateSelected(form); clearTimeout(timer); timer = setTimeout(() => void runSearch(form), 120); });
    form.addEventListener("input", (event) => { if (event.target.matches('input[type="search"],input[type="number"]')) { clearTimeout(timer); timer = setTimeout(() => void runSearch(form), 350); } });
    form.querySelector("[data-search]")?.addEventListener("click", () => void runSearch(form));
    form.querySelector("[data-reset]")?.addEventListener("click", () => {
      form.reset(); state.results = []; updateSelected(form); setStatus(form, `Bez omezení · ${fmt(state.total)} nabídek v celém katalogu`);
      document.querySelector("#resultInfo").textContent = `Celý katalog obsahuje ${fmt(state.total)} nabídek. Vyberte alespoň jeden filtr.`;
      document.querySelector("#offersGrid").innerHTML = `<div class="empty-state">Vyberte parametry ve vyhledávači.</div>`;
    });
  }

  function updateSelected(form) {
    for (const details of form.querySelectorAll("details[data-group]")) details.querySelector("[data-selected]").textContent = String(details.querySelectorAll('input[type="checkbox"]:checked').length);
  }

  function filters(form) {
    const multi = ["countries","regions","resorts","hotels","tripTypes","sports","transports","departures","providers","boards","categories","freshness","travelers"];
    const out = {};
    for (const name of multi) out[name] = [...form.querySelectorAll(`input[name="${name}"]:checked`)].map((node) => node.value);
    for (const name of ["query","sort","minPrice","maxPrice","dateFrom","dateTo","minNights","maxNights","minRating","minDiscount"]) out[name] = form.elements.namedItem(name)?.value || "";
    return out;
  }

  async function runSearch(form) {
    if (state.busy) return;
    const f = filters(form);
    const active = Object.entries(f).some(([key,value]) => key !== "sort" && (Array.isArray(value) ? value.length : clean(value)));
    if (!active) { setStatus(form, `Bez omezení · ${fmt(state.total)} nabídek v celém katalogu`); return; }
    state.busy = true;
    setStatus(form, "Načítám odpovídající části celého katalogu…");
    const grid = document.querySelector("#offersGrid");
    const info = document.querySelector("#resultInfo");
    grid.innerHTML = `<div class="cf7-loading-results">Načítám skutečné nabídky…</div>`;
    try {
      const keys = candidateKeys(f);
      const combined = new Map();
      let offset = 0;
      while (offset < keys.length && offset < 32) {
        const batch = keys.slice(offset, offset + 4);
        const payloads = await Promise.all(batch.map((key) => loadChunk(key).catch((error) => { console.warn("Chunk", key, error); return []; })));
        for (const rows of payloads) for (const offer of rows) combined.set(String(offer.id || `${offer.title}-${offer.startDate}-${offer.priceFrom}`), offer);
        state.offers = [...combined.values()];
        state.results = sortOffers(state.offers.filter((offer) => matches(offer, f)), f.sort);
        if (state.results.length >= PAGE_SIZE || offset + 4 >= keys.length) break;
        offset += 4;
      }
      updateHierarchy(form, state.offers, f);
      renderResults(state.results.slice(0, PAGE_SIZE));
      const message = state.results.length ? `${fmt(state.results.length)} odpovídajících nabídek v načtené části celého katalogu` : "V načtené části nejsou odpovídající nabídky – rozšiřte výběr";
      setStatus(form, message);
      info.textContent = state.results.length ? `Zobrazeno ${fmt(Math.min(PAGE_SIZE, state.results.length))} skutečných nabídek. Celý katalog obsahuje ${fmt(state.total)} záznamů.` : "Pro zvolenou kombinaci nebyly nalezeny nabídky.";
      document.dispatchEvent(new CustomEvent("lms:v7-rendered", { detail: { results: state.results.length, visible: state.results.slice(0,PAGE_SIZE), filters: f, rescue: BUILD } }));
    } catch (error) {
      console.error("Vyhledávání:", error);
      setStatus(form, "Vyhledávání se nepodařilo dokončit.");
      info.textContent = error?.message || "Chyba načítání nabídky.";
      grid.innerHTML = `<div class="empty-state">Načítání selhalo. Zkuste změnit filtr nebo obnovit stránku.</div>`;
    } finally { state.busy = false; }
  }

  function candidateKeys(f) {
    const chunks = Array.isArray(state.manifest?.chunks) ? state.manifest.chunks : [];
    const map = new Map(chunks.map((item) => [item.key, item]));
    const keys = new Set();
    if (f.countries.length) {
      for (const selected of f.countries) {
        const direct = Object.entries(state.manifest?.countryChunks || {}).find(([country]) => normalize(country) === normalize(selected));
        for (const key of direct?.[1] || []) keys.add(key);
        for (const item of chunks) if (normalize(item?.country) === normalize(selected)) keys.add(item.key);
      }
    }
    if (!keys.size) for (const item of chunks) keys.add(item.key);
    return [...keys].filter((key) => map.has(key)).sort((a,b) => String(map.get(a)?.month || "").localeCompare(String(map.get(b)?.month || "")) || Number(map.get(b)?.offers || 0)-Number(map.get(a)?.offers || 0));
  }

  async function loadChunk(key) {
    if (state.loadedKeys.has(key)) return [];
    const meta = (state.manifest?.chunks || []).find((item) => item?.key === key);
    const path = meta?.url || state.manifest?.shards?.[key];
    if (!path) return [];
    const payload = await readCompressed(asset(path));
    state.loadedKeys.add(key);
    return hydrate(payload).map((offer) => ({ ...offer, shard: offer.shard || key }));
  }

  function hydrate(payload) {
    if (Array.isArray(payload)) return payload;
    const fields = Array.isArray(payload?.fields) ? payload.fields : [];
    return (payload?.offers || []).map((row) => Array.isArray(row) ? Object.fromEntries(fields.map((field,index) => [field,row[index]]).filter(([,value]) => value !== null && value !== undefined)) : row);
  }

  function matches(offer, f) {
    const inList = (value, selected) => !selected.length || selected.some((item) => normalize(item) === normalize(value));
    const includes = (value, selected) => !selected.length || selected.some((item) => normalize(value).includes(normalize(item)) || normalize(item).includes(normalize(value)));
    if (f.query && !normalize([offer.title,offer.country,offer.destination,offer.resort,offer.hotel,offer.provider].join(" ")).includes(normalize(f.query))) return false;
    if (!inList(offer.country, f.countries)) return false;
    if (!includes(offer.destination, f.regions)) return false;
    if (!includes(offer.resort || offer.locality || offer.destination, f.resorts)) return false;
    if (!includes(offer.hotel || offer.title, f.hotels)) return false;
    if (!includes(offer.tripType || offer.type || "stay", f.tripTypes)) return false;
    if (!includes(offer.sport || offer.sportType || "", f.sports)) return false;
    if (!includes(offer.transportationType || offer.transportation || "other", f.transports)) return false;
    if (!includes(offer.departureCity || "", f.departures)) return false;
    if (!includes(offer.provider || "", f.providers)) return false;
    if (!includes(offer.board || "", f.boards)) return false;
    const price = Number(offer.priceCzk || offer.priceFrom || offer.price || 0), nights = Number(offer.nights || 0), rating = Number(offer.rating || 0), discount = Number(offer.discount || offer.discountPercent || 0);
    if (f.minPrice && price < Number(f.minPrice)) return false; if (f.maxPrice && price > Number(f.maxPrice)) return false;
    if (f.minNights && nights < Number(f.minNights)) return false; if (f.maxNights && nights > Number(f.maxNights)) return false;
    if (f.minRating && rating < Number(f.minRating)) return false; if (f.minDiscount && discount < Number(f.minDiscount)) return false;
    const date = clean(offer.startDate || offer.dateFrom); if (f.dateFrom && date && date < f.dateFrom) return false; if (f.dateTo && date && date > f.dateTo) return false;
    if (f.categories.length && !f.categories.some((category) => categoryMatches(date, category))) return false;
    return true;
  }

  function categoryMatches(dateText, category) {
    const date = new Date(dateText), today = new Date(); if (Number.isNaN(date.getTime())) return category === "standard";
    const days = Math.ceil((date - new Date(today.getFullYear(),today.getMonth(),today.getDate())) / 86400000);
    if (category === "depart-3-days") return days >= 0 && days <= 3;
    if (category === "super-last-minute") return days >= 0 && days <= 7;
    if (category === "last-minute") return days >= 8 && days <= 30;
    if (category === "first-minute") return days > 90;
    return days > 30 && days <= 90;
  }

  function sortOffers(rows, mode) {
    const copy = [...rows];
    if (mode === "price") return copy.sort((a,b) => Number(a.priceCzk || a.priceFrom || 9e15)-Number(b.priceCzk || b.priceFrom || 9e15));
    if (mode === "date") return copy.sort((a,b) => String(a.startDate || "9999").localeCompare(String(b.startDate || "9999")));
    if (mode === "rating") return copy.sort((a,b) => Number(b.rating || 0)-Number(a.rating || 0));
    if (mode === "discount") return copy.sort((a,b) => Number(b.discount || b.discountPercent || 0)-Number(a.discount || a.discountPercent || 0));
    return copy.sort((a,b) => Number(Boolean(b.imageUrl))-Number(Boolean(a.imageUrl)) || Number(a.priceCzk || a.priceFrom || 9e15)-Number(b.priceCzk || b.priceFrom || 9e15));
  }

  function updateHierarchy(form, offers, f) {
    const values = (getter, limit=120) => {
      const counts = new Map(); for (const offer of offers) { const value=clean(getter(offer)); if(value) counts.set(value,(counts.get(value)||0)+1); }
      return [...counts].map(([value,count]) => [value,value,count]).sort((a,b)=>b[2]-a[2]||a[0].localeCompare(b[0],"cs")).slice(0,limit);
    };
    replaceGroup(form,"regions","Oblast",values((o)=>o.destination));
    replaceGroup(form,"resorts","Letovisko",values((o)=>o.resort || o.locality || o.destination));
    replaceGroup(form,"hotels","Hotel",values((o)=>o.hotel || o.title,150));
  }

  function replaceGroup(form,name,label,rows) {
    const old=form.querySelector(`details[data-group="${name}"]`); if(!old)return;
    const selected=new Set([...old.querySelectorAll('input:checked')].map(i=>i.value));
    const wrap=document.createElement("div"); wrap.innerHTML=group(name,label,rows); const fresh=wrap.firstElementChild;
    for(const input of fresh.querySelectorAll("input")) input.checked=selected.has(input.value);
    old.replaceWith(fresh);
  }

  function renderResults(rows) {
    const grid = document.querySelector("#offersGrid");
    grid.innerHTML = rows.length ? rows.map(card).join("") : `<div class="empty-state">Pro tento výběr nejsou v načtené části nabídky.</div>`;
  }

  function card(offer) {
    const price = Number(offer.priceCzk || offer.priceFrom || offer.price || 0);
    const currency = String(offer.currency || "CZK").toUpperCase();
    const priceText = price > 0 ? new Intl.NumberFormat("cs-CZ", { style:"currency", currency: currency === "EUR" ? "EUR" : "CZK", maximumFractionDigits:0 }).format(price) : "Cena v detailu";
    const title=clean(offer.title || offer.hotel || "Akční zájezd"), place=[offer.country,offer.destination,offer.resort,offer.hotel].filter(Boolean).join(" · ");
    const image=offer.imageUrl ? `<img src="${esc(offer.imageUrl)}" alt="${esc(title)}" loading="lazy">` : `<strong>${esc(offer.country || "Dovolená")}</strong>`;
    return `<article class="offer-card catalog-offer-card"><div class="offer-image">${image}</div><div class="offer-body"><h3>${esc(title)}</h3><p>${esc(place)}</p><div class="offer-meta"><span>${esc(offer.transportation || offer.transportationType || "Doprava dle nabídky")}</span><span>${esc(formatDate(offer.startDate))}</span><span>${offer.nights ? `${fmt(offer.nights)} nocí` : "Délka v detailu"}</span><span>${esc(offer.board || "Strava v detailu")}</span></div><div class="offer-price"><div><small>${esc(offer.provider || "Cestovní partner")}</small><strong>${esc(priceText)} / osoba</strong></div></div><div class="partner-row"><span>Nabídka u ${esc(offer.provider || "partnera")}</span><a href="${esc(offer.url || "#")}" target="_blank" rel="nofollow sponsored noopener noreferrer">Ověřit detail</a></div></div></article>`;
  }

  function formatDate(value) { const date=new Date(value); return !value || Number.isNaN(date.getTime()) ? "Termín v detailu" : new Intl.DateTimeFormat("cs-CZ",{day:"numeric",month:"long",year:"numeric"}).format(date); }
  function setStatus(form,text) { const node=form.querySelector("[data-search-status]"); if(node)node.textContent=text; }
  function asset(path) { const value=clean(path); if(/^https?:\/\//i.test(value))return value; if(value.startsWith("/"))return `${ORIGIN}${value}`; return `${BASE}/${value.replace(/^\.?\//,"")}`; }
  async function fetchJson(url) { const response=await fetch(url,{cache:"no-store"}); if(!response.ok)throw new Error(`HTTP ${response.status}`); return response.json(); }
  async function readCompressed(url) {
    try {
      const response=await fetch(url,{cache:"force-cache"}); if(!response.ok)throw new Error(`HTTP ${response.status}`);
      if (/gzip/i.test(response.headers.get("content-encoding")||"")) return response.json();
      if (url.includes(".gz") && "DecompressionStream" in window && response.body) return JSON.parse(await new Response(response.body.pipeThrough(new DecompressionStream("gzip"))).text());
      return JSON.parse(await response.text());
    } catch(error) {
      if(!url.includes(".gz"))throw error;
      const response=await fetch(url.replace(/\.gz(?=\?|$)/,""),{cache:"force-cache"}); if(!response.ok)throw error; return response.json();
    }
  }

  function enforceAdvertising(results) {
    const place = () => {
      for (const ad of document.querySelectorAll('[data-slevomat-home-section],.lms-slevomat-home')) if (results.compareDocumentPosition(ad) & Node.DOCUMENT_POSITION_PRECEDING) results.insertAdjacentElement("afterend",ad);
      if (!document.querySelector("[data-slevomat-home-section]")) {
        const section=document.createElement("section"); section.className="section destination-section lms-rescue-ad"; section.dataset.slevomatHomeSection="after-results"; section.innerHTML=`<div class="section-heading"><p class="eyebrow">Reklama · partnerský odkaz</p><h2>Pobyty, wellness a zážitky na Slevomatu</h2></div><a href="https://www.slevomat.cz/?utm_source=affiliate&utm_medium=cpc&utm_campaign=dis_akv_gen_cze_all_buy_37wcgfes_lastminuteslevy.cz&utm_content=homepage&utm_term=37wcgfes&a_box=37wcgfes" target="_blank" rel="nofollow sponsored noopener noreferrer"><span>Pobyty a volný čas</span><strong>Otevřít nabídky Slevomatu</strong><small>Aktuální cenu a dostupnost ověřte přímo na Slevomatu.</small></a>`; results.insertAdjacentElement("afterend",section);
      }
    };
    place(); new MutationObserver(place).observe(document.querySelector("main") || document.body,{childList:true,subtree:true});
  }
})();
