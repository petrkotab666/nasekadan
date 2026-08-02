(() => {
  'use strict';

  const STAT_LABELS = {
    treasury: 'Pokladna',
    supplies: 'Zásoby',
    order: 'Pořádek',
    people: 'Obyvatelé',
    favor: 'Přízeň'
  };

  const DIFFICULTIES = {
    scribe: {
      name: 'Městský písař',
      start: { treasury: 78, supplies: 76, order: 72, people: 70, favor: 62 },
      effectScale: 0.85
    },
    burgrave: {
      name: 'Purkmistr',
      start: { treasury: 66, supplies: 64, order: 62, people: 60, favor: 52 },
      effectScale: 1
    },
    royal: {
      name: 'Královský správce',
      start: { treasury: 54, supplies: 52, order: 50, people: 49, favor: 43 },
      effectScale: 1.15
    }
  };

  const SCENES = [
    {
      chapter: 'Obnova města',
      eyebrow: 'PĚT LET PO VELKÉM POŽÁRU',
      title: 'Město ještě není úplně opravené',
      text: 'Požár roku 1362 poškodil Kadaň i hrad. Císař má dorazit za několik dní a ty můžeš dokončit jen jednu velkou práci.',
      art: 'fire',
      symbol: '♜',
      choices: [
        {
          title: 'Zpevnit brány a hradby',
          hint: 'Bezpečnost bude vidět, ale obyvatelé budou dál bydlet mezi lešením.',
          effects: { treasury: -12, order: 13, favor: 5, people: -3 },
          result: 'Stráže hlásí pevné brány a klidnější noc. Měšťané však reptají, že jejich domy musejí počkat.',
          history: 'Kadaň se po požáru obnovovala z kamene a současně zdokonalovala opevnění. Hradby nebyly kulisou, ale základním bezpečnostním systémem města.'
        },
        {
          title: 'Opravit náměstí a domy pro hosty',
          hint: 'Příjezd bude působivý, obrana ale zůstane slabší.',
          effects: { treasury: -11, people: 11, favor: 9, order: -4 },
          result: 'Císařská družina najde čisté ulice a připravené komnaty. Velitel stráží upozorňuje na nedokončený úsek hradeb.',
          history: 'Měšťanský dům nebyl jen obydlím. V přízemí se pracovalo, obchodovalo a skladovalo zboží, takže jeho oprava pomáhala domácnosti i hospodářství.'
        },
        {
          title: 'Zakryjeme škody praporci a plátnem',
          hint: 'Nejlevnější řešení, které může císař snadno prohlédnout.',
          effects: { treasury: -4, favor: -8, order: -5, people: 2 },
          result: 'Z dálky město vypadá slavnostně. Zblízka je však patrné, že část oprav je pouze namalovaná na plátně.',
          history: 'Panovnická návštěva byla zároveň přehlídkou moci a pořádku. Stav města vypovídal o schopnosti jeho rady stejně jako slavnostní projevy.'
        }
      ]
    },
    {
      chapter: 'Výroční trh',
      eyebrow: 'OBCHODNÍCI ČEKAJÍ PŘED BRANOU',
      title: 'Jak připravíš městský trh?',
      text: 'Na zprávu o příjezdu panovníka reagují kupci z okolí. Trh může naplnit sklady a pokladnu, ale také přivést zloděje a spory.',
      art: 'market',
      symbol: '⚖',
      choices: [
        {
          title: 'Snížit poplatky a pozvat co nejvíce kupců',
          hint: 'Méně peněz za stánek, více zboží a návštěvníků.',
          effects: { treasury: -6, supplies: 13, people: 9, favor: 5, order: -3 },
          result: 'Náměstí se zaplnilo látkami, obilím, vínem i lidmi. Stráže mají plné ruce práce, ale město působí bohatě.',
          history: 'Výroční trh byl skutečnou hospodářskou výsadou. Přiváděl kupce na několik dní a podporoval obchod, ubytování i městské poplatky.'
        },
        {
          title: 'Zvýšit poplatky, císařská návštěva je vzácná',
          hint: 'Pokladna vydělá, chudší prodejci ale odjedou jinam.',
          effects: { treasury: 15, supplies: 2, people: -10, favor: -3, order: 2 },
          result: 'Městská truhlice těžkne, tržiště je však poloprázdné a kupci si stěžují na hamižnost rady.',
          history: 'Městská rada mohla obchod regulovat, vážit zboží a vybírat poplatky. Příliš tvrdé podmínky ale mohly odvést obchod do sousedního města.'
        },
        {
          title: 'Přednost dostanou kadaňští řemeslníci',
          hint: 'Místní vydělají a trh zůstane přehlednější.',
          effects: { treasury: 6, supplies: 7, order: 7, people: 7, favor: 1 },
          result: 'Cechy obsadily nejlepší místa a město působí spořádaně. Přespolní kupci čekají za druhou řadou stánků.',
          history: 'Mílové právo chránilo vybrané městské živnosti a obchod před konkurencí v okolí. Pro místní bylo výhodou, pro cizí kupce omezením.'
        }
      ]
    },
    {
      chapter: 'Císařská družina',
      eyebrow: 'POSLOVÉ PŘINÁŠEJÍ NOVOU ZPRÁVU',
      title: 'Přijede dvakrát více hostů, než se čekalo',
      text: 'Koně potřebují píci, vojáci jídlo a významní hosté střechu nad hlavou. Městské sklady nejsou bezedné.',
      art: 'emperor',
      symbol: '♞',
      choices: [
        {
          title: 'Nařídit mimořádné odvody obilí a masa',
          hint: 'Císař bude spokojený, obyvatelé zaplatí vysokou cenu.',
          effects: { supplies: -17, favor: 12, people: -13, order: -2 },
          result: 'Družina je nasycená, ale v domácnostech zůstaly prázdnější spižírny. Na tržišti se šeptá o nespravedlnosti.',
          history: 'Pobyt panovníka nebyl pro hostitelské město levný. Ubytování, krmivo a zásobování početné družiny musely zajistit místní zdroje.'
        },
        {
          title: 'Zaplatit hostinským a měšťanům z pokladny',
          hint: 'Drahé, ale obyvatelé nebudou nuceni zásoby odevzdat zdarma.',
          effects: { treasury: -15, supplies: -9, people: 8, favor: 7, order: 3 },
          result: 'Hosté jsou rozmístěni po městě a měšťané dostali zaplaceno. Pokladník však počítá poslední rezervy.',
          history: 'Bohatší měšťanské domy mohly ubytovat hosty a poskytnout služby. Peníze z návštěvy se tak vracely části obyvatel města.'
        },
        {
          title: 'Zavést stejné příděly pro hosty i obyvatele',
          hint: 'Úsporné a relativně spravedlivé, císařští dvořané to mohou chápat jako urážku.',
          effects: { supplies: -10, people: 6, favor: -7, order: 6 },
          result: 'Zásoby vydržely a u stolů se neplýtvalo. Část císařovy družiny však očekávala mnohem okázalejší přijetí.',
          history: 'Ve středověkém městě byly rozdíly mezi jídelníčkem bohatých, čeledi a chudiny značné. Rovné příděly by byly neobvyklým rozhodnutím.'
        }
      ]
    },
    {
      chapter: 'Městské brány',
      eyebrow: 'SLUNCE ZAPADÁ ZA HRADBAMI',
      title: 'Kupci chtějí vstupovat do města i po setmění',
      text: 'Uzavřené brány chrání město. Pozdní příjezdy ale přivážejí zboží potřebné pro slavnost.',
      art: 'gate',
      symbol: '▥',
      choices: [
        {
          title: 'Zavřít brány dříve a nikoho nepouštět',
          hint: 'Nejvyšší bezpečnost, část zásob zůstane venku.',
          effects: { order: 13, supplies: -6, people: -5, favor: 1 },
          result: 'Noc proběhla klidně. Před hradbami však čekají vozy s moukou, vínem a látkami.',
          history: 'Městské brány se na noc skutečně zavíraly. Kontrolovaly pohyb lidí, zboží i výběr poplatků a byly zásadní součástí obrany.'
        },
        {
          title: 'Nechat jednu bránu otevřenou pod silnou stráží',
          hint: 'Vyvážené řešení, které stojí peníze a lidi.',
          effects: { treasury: -6, order: 6, supplies: 9, people: 5, favor: 3 },
          result: 'Vozy projíždějí jednotlivě, písař zapisuje náklad a stráže prohledávají podezřelé povozy.',
          history: 'Kontrola u bran spojovala bezpečnost, správu a výběr poplatků. Každé otevření po setmění by vyžadovalo zvláštní dohled.'
        },
        {
          title: 'Nechat průchod volný, slavnost potřebuje život',
          hint: 'Rychlé zásobování, vysoké bezpečnostní riziko.',
          effects: { supplies: 7, people: 3, order: -16, favor: -2 },
          result: 'Tržiště je plné ještě v noci. Ráno však chybí několik měšců a stráže netuší, kdo město opustil.',
          history: 'Hradby bez kontroly by ztrácely smysl. Ve městě plném cizinců rostlo riziko krádeží, sporů i požáru.'
        }
      ]
    },
    {
      chapter: 'Městský soud',
      eyebrow: 'SPOR PŘED RADNICÍ',
      title: 'Kupec obvinil řezníka z falešné váhy',
      text: 'Oba mají vlivné zastánce. Rozhodnutí sleduje celé náměstí a zpráva se může dostat až k císaři.',
      art: 'court',
      symbol: '⚖',
      choices: [
        {
          title: 'Veřejně přezkoušet váhy a vyslechnout svědky',
          hint: 'Pomalejší, ale průhledný postup.',
          effects: { treasury: -3, order: 10, people: 7, favor: 5 },
          result: 'Městská váha odhalila podvod. Trest je přijat jako spravedlivý a tržiště se uklidňuje.',
          history: 'Městská samospráva řešila spory, pořádek i tresty. Veřejnost rozsudku byla důležitá, protože měla obnovit důvěru a odradit další provinilce.'
        },
        {
          title: 'Podpořit bohatší cech, který městu více platí',
          hint: 'Rychlé peníze výměnou za důvěru obyvatel.',
          effects: { treasury: 9, order: -7, people: -11, favor: -2 },
          result: 'Cech daroval městu peníze, ale na náměstí se mluví o koupeném rozsudku.',
          history: 'Cechy byly důležitou hospodářskou silou, ale privilegia mohla vyvolávat napětí mezi bohatými měšťany, drobnými řemeslníky a cizinci.'
        },
        {
          title: 'Předložit spor přímo císaři',
          hint: 'Projev úcty, ale také přiznání, že městský soud si neví rady.',
          effects: { favor: 7, order: -5, people: -3, treasury: -2 },
          result: 'Dvořané oceňují císařovu autoritu. Městská rada však působí slabě a další spory se hromadí.',
          history: 'Kadaň měla vlastní samosprávu a soudní pravomoci. Přenést běžný tržní spor na panovníka by oslabovalo obraz schopného královského města.'
        }
      ]
    },
    {
      chapter: 'Požár v dílně',
      eyebrow: 'ZVONY BIJÍ NA POPLACH',
      title: 'U tržiště vzplála řemeslnická dílna',
      text: 'Oheň se může přenést na sousední domy. Všichni si stále pamatují velký požár před pěti lety.',
      art: 'fire',
      symbol: '♨',
      choices: [
        {
          title: 'Svolat řetěz s vědry a strhnout sousední kůlnu',
          hint: 'Rychlý zásah zachrání čtvrť, ale poškodí majetek.',
          effects: { treasury: -8, supplies: -4, order: 9, people: 9, favor: 3 },
          result: 'Oheň se podařilo zastavit. Majitel kůlny žádá náhradu, ostatní domy však zůstaly stát.',
          history: 'V husté zástavbě se požár šířil velmi rychle. Voda, bourání ohrožených konstrukcí a organizace sousedů patřily k hlavním možnostem obrany.'
        },
        {
          title: 'Nejdříve chránit hrad a císařské komnaty',
          hint: 'Panovník bude v bezpečí, městská čtvrť může shořet.',
          effects: { favor: 10, people: -14, order: -4, treasury: -3 },
          result: 'Hrad je bezpečný, několik domů u trhu však lehlo popelem. Obyvatelé považují rozhodnutí za zradu.',
          history: 'Panovnický hrad měl mimořádnou hodnotu, ale město tvořili především jeho obyvatelé, dílny a domy. Jejich ztráta znamenala dlouhodobý hospodářský problém.'
        },
        {
          title: 'Nechat zásah na příslušném cechu',
          hint: 'Město ušetří, oheň ale nečeká na poradu.',
          effects: { treasury: -1, order: -12, people: -6, supplies: -6, favor: -3 },
          result: 'Cechovní mistři se přeli o odpovědnost a plameny přeskočily na sklad se zbožím.',
          history: 'Cechovní organizace pomáhala řídit řemesla, ale při městském nebezpečí musela koordinaci převzít rada a stráže.'
        }
      ]
    },
    {
      chapter: 'Dar pro panovníka',
      eyebrow: 'CÍSAŘ VSTUPUJE NA NÁMĚSTÍ',
      title: 'Jaký dar představí charakter Kadaně?',
      text: 'Dar není jen zdvořilost. Ukazuje, co město vyrábí, čím je bohaté a jak rozumí svému panovníkovi.',
      art: 'emperor',
      symbol: '♛',
      choices: [
        {
          title: 'Drahý stříbrný pohár ze společné pokladny',
          hint: 'Okázalé gesto, které vyčerpá finanční rezervu.',
          effects: { treasury: -17, favor: 13, people: -4, order: 1 },
          result: 'Pohár budí obdiv dvořanů. Pokladník však připomíná, že po slavnosti bude třeba zaplatit opravy.',
          history: 'Drahocenný kov byl tradičním reprezentativním darem. Jeho hodnota zároveň ukazovala finanční sílu městské obce.'
        },
        {
          title: 'Kadaňské pivo, chléb a ukázky řemesel',
          hint: 'Méně okázalé, ale pevně spojené s městem.',
          effects: { supplies: -9, favor: 9, people: 8, treasury: 2 },
          result: 'Císař ochutnal místní produkci a na náměstí se slaví společně. Město představilo práci svých obyvatel.',
          history: 'Pivovarnictví, řemesla a obchod byly základem městského hospodářství. Mílové právo je chránilo před konkurencí z blízkého okolí.'
        },
        {
          title: 'Uspořádat nákladný turnaj a ohňovou podívanou',
          hint: 'Velkolepá zábava, ale vysoké náklady a bezpečnostní riziko.',
          effects: { treasury: -19, favor: 9, people: 6, order: -6 },
          result: 'Diváci jásají a dvořané mají o čem vyprávět. Stráže řeší několik zranění a pokladna je téměř prázdná.',
          history: 'Turnaje patří k dnešnímu obrazu středověkých slavností. Konkrétní podoba programu je však novodobou stylizací, nikoli doloženým průběhem návštěvy roku 1367.'
        }
      ]
    },
    {
      chapter: 'Císařské slyšení',
      eyebrow: 'POSLEDNÍ ROZHODNUTÍ',
      title: 'O jaké privilegium požádáš Karla IV.?',
      text: 'Panovník je s městem připraven jednat. Dobrá žádost může ovlivnit kadaňský obchod na celé generace.',
      art: 'emperor',
      symbol: '✦',
      choices: [
        {
          title: 'Povolení osmidenního výročního trhu',
          hint: 'Více kupců, zboží, hostů a příjmů pro celé město.',
          effects: { favor: 9, treasury: 8, supplies: 5, people: 8, order: 2 },
          result: 'Císař žádosti vyhověl. Kadaň získává příležitost pořádat trh, který přivede obchodníky z širšího okolí.',
          history: 'Právě povolení osmidenního výročního trhu patří k doloženým výsledkům návštěvy Karla IV. v Kadani roku 1367.'
        },
        {
          title: 'Osvobození městských kupců od části mýta',
          hint: 'Výhoda pro obchodníky, menší přímý přínos pro ostatní obyvatele.',
          effects: { treasury: 11, favor: 5, people: 2, order: -2, supplies: 3 },
          result: 'Kupci slaví a slibují větší obchod. Řemeslníci se ptají, proč výsadu získala jen část města.',
          history: 'Mýta a obchodní privilegia zásadně ovlivňovala, kudy zboží proudilo a která města na dálkovém obchodu vydělávala.'
        },
        {
          title: 'Nežádat nic, návštěva sama je dostatečná čest',
          hint: 'Bez rizika odmítnutí, ale také bez dlouhodobého přínosu.',
          effects: { favor: -4, order: 3, people: -2, treasury: 1 },
          result: 'Císař odjíždí bez konfliktu, městská rada však promarnila vzácnou příležitost.',
          history: 'Panovnická návštěva měla praktický význam právě díky listinám a privilegiím. Bez nich by zůstala především reprezentativní událostí.'
        }
      ]
    }
  ];

  const RANDOM_EVENTS = [
    {
      after: 1,
      variants: [
        { text: 'Noční déšť poškodil část stánků.', effects: { treasury: -3, supplies: -2 } },
        { text: 'Přijel vůz s kvalitní moukou za dobrou cenu.', effects: { treasury: -2, supplies: 5 } },
        { text: 'Stráže chytily kapsáře ještě před otevřením trhu.', effects: { order: 4, people: 2 } }
      ]
    },
    {
      after: 4,
      variants: [
        { text: 'Jeden z císařských koní se zranil a potřebuje péči.', effects: { treasury: -3, favor: 3 } },
        { text: 'Místní pekaři věnovali část chleba městské chudině.', effects: { supplies: -3, people: 5 } },
        { text: 'V noci zmizel sud piva určený pro družinu.', effects: { supplies: -4, order: -3 } }
      ]
    }
  ];

  const elements = {
    startScreen: document.getElementById('startScreen'),
    playScreen: document.getElementById('playScreen'),
    resultScreen: document.getElementById('resultScreen'),
    startButton: document.getElementById('startButton'),
    soundButton: document.getElementById('soundButton'),
    bestScore: document.getElementById('bestScore'),
    chapterNumber: document.getElementById('chapterNumber'),
    chapterTitle: document.getElementById('chapterTitle'),
    progressBar: document.getElementById('progressBar'),
    sceneIllustration: document.getElementById('sceneIllustration'),
    sceneEyebrow: document.getElementById('sceneEyebrow'),
    sceneTitle: document.getElementById('sceneTitle'),
    sceneText: document.getElementById('sceneText'),
    choices: document.getElementById('choices'),
    consequence: document.getElementById('consequence'),
    consequenceResult: document.getElementById('consequenceResult'),
    effectList: document.getElementById('effectList'),
    historyNote: document.getElementById('historyNote'),
    continueButton: document.getElementById('continueButton'),
    resultMedal: document.getElementById('resultMedal'),
    resultTitle: document.getElementById('resultTitle'),
    resultScore: document.getElementById('resultScore'),
    resultDescription: document.getElementById('resultDescription'),
    resultStats: document.getElementById('resultStats'),
    resultHistory: document.getElementById('resultHistory'),
    restartButton: document.getElementById('restartButton'),
    shareButton: document.getElementById('shareButton'),
    shareStatus: document.getElementById('shareStatus')
  };

  if (!elements.startScreen || !elements.playScreen || !elements.resultScreen) {
    return;
  }

  let state = createInitialState('scribe');
  let audioContext = null;

  function createInitialState(difficulty) {
    const settings = DIFFICULTIES[difficulty] || DIFFICULTIES.scribe;
    return {
      difficulty,
      sceneIndex: 0,
      stats: { ...settings.start },
      notes: [],
      decisions: [],
      locked: false,
      pendingRandomEvent: null,
      sound: false
    };
  }

  function clamp(value) {
    return Math.max(0, Math.min(100, Math.round(value)));
  }

  function scaledEffect(value) {
    const scale = DIFFICULTIES[state.difficulty].effectScale;
    if (value >= 0) {
      return Math.round(value / Math.max(0.9, scale));
    }
    return Math.round(value * scale);
  }

  function applyEffects(effects) {
    const applied = {};
    Object.entries(effects).forEach(([key, rawValue]) => {
      const value = scaledEffect(rawValue);
      state.stats[key] = clamp(state.stats[key] + value);
      applied[key] = value;
    });
    updateStats();
    return applied;
  }

  function updateStats() {
    document.querySelectorAll('.stat').forEach((node) => {
      const key = node.dataset.stat;
      const value = state.stats[key] ?? 0;
      const output = node.querySelector('output');
      const bar = node.querySelector('.stat__bar i');
      if (output) output.textContent = String(value);
      if (bar) {
        bar.style.width = `${value}%`;
        bar.style.background = value < 30 ? 'var(--game-bad)' : value < 55 ? 'var(--game-gold)' : 'var(--game-good)';
      }
    });
  }

  function renderScene() {
    const scene = SCENES[state.sceneIndex];
    if (!scene) {
      renderResult();
      return;
    }

    state.locked = false;
    elements.consequence.hidden = true;
    elements.choices.hidden = false;
    elements.choices.innerHTML = '';
    elements.chapterNumber.textContent = `Kapitola ${state.sceneIndex + 1} z ${SCENES.length}`;
    elements.chapterTitle.textContent = scene.chapter;
    elements.progressBar.style.width = `${(state.sceneIndex / SCENES.length) * 100}%`;
    elements.sceneEyebrow.textContent = scene.eyebrow;
    elements.sceneTitle.textContent = scene.title;
    elements.sceneText.textContent = scene.text;
    elements.sceneIllustration.dataset.scene = scene.art;
    elements.sceneIllustration.dataset.symbol = scene.symbol;

    scene.choices.forEach((choice, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'choice-button';
      button.dataset.choiceIndex = String(index);
      button.innerHTML = `<span class="choice-button__number">${index + 1}</span><span><b>${escapeHtml(choice.title)}</b><small>${escapeHtml(choice.hint)}</small></span>`;
      button.addEventListener('click', () => choose(index));
      elements.choices.appendChild(button);
    });

    updateStats();
    announceGameEvent('scene', { scene: state.sceneIndex + 1, difficulty: state.difficulty });
  }

  function choose(index) {
    if (state.locked) return;
    const scene = SCENES[state.sceneIndex];
    const choice = scene?.choices[index];
    if (!choice) return;

    state.locked = true;
    sound('choice');
    const applied = applyEffects(choice.effects);
    state.decisions.push({ scene: state.sceneIndex, choice: index });
    state.notes.push(choice.history);

    elements.choices.hidden = true;
    elements.consequence.hidden = false;
    elements.consequenceResult.textContent = choice.result;
    elements.historyNote.textContent = choice.history;
    elements.effectList.innerHTML = '';

    Object.entries(applied).forEach(([key, value]) => {
      const pill = document.createElement('span');
      pill.className = `effect-pill ${value >= 0 ? 'is-positive' : 'is-negative'}`;
      pill.textContent = `${STAT_LABELS[key]} ${value >= 0 ? '+' : ''}${value}`;
      elements.effectList.appendChild(pill);
    });

    const event = randomEventForScene(state.sceneIndex);
    if (event) {
      const eventApplied = applyEffects(event.effects);
      const eventText = document.createElement('p');
      eventText.className = 'consequence__event';
      eventText.textContent = `Nečekaná událost: ${event.text}`;
      elements.effectList.before(eventText);
      Object.entries(eventApplied).forEach(([key, value]) => {
        const pill = document.createElement('span');
        pill.className = `effect-pill ${value >= 0 ? 'is-positive' : 'is-negative'}`;
        pill.textContent = `${STAT_LABELS[key]} ${value >= 0 ? '+' : ''}${value}`;
        elements.effectList.appendChild(pill);
      });
    }

    elements.continueButton.textContent = state.sceneIndex === SCENES.length - 1 ? 'Přivítat císaře' : 'Pokračovat';
    elements.continueButton.focus({ preventScroll: true });
    announceGameEvent('choice', { scene: state.sceneIndex + 1, choice: index + 1, stats: { ...state.stats } });
  }

  function randomEventForScene(sceneIndex) {
    const entry = RANDOM_EVENTS.find((item) => item.after === sceneIndex);
    if (!entry) return null;
    const seed = state.decisions.reduce((sum, decision) => sum + ((decision.scene + 1) * (decision.choice + 2)), 0);
    return entry.variants[seed % entry.variants.length];
  }

  function continueGame() {
    sound('continue');
    state.sceneIndex += 1;
    if (state.sceneIndex >= SCENES.length) {
      renderResult();
      return;
    }
    renderScene();
    document.getElementById('gameApp')?.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
  }

  function calculateScore() {
    const values = Object.values(state.stats);
    const average = values.reduce((sum, value) => sum + value, 0) / values.length;
    const balancePenalty = Math.max(...values) - Math.min(...values);
    const collapsePenalty = values.filter((value) => value < 20).length * 8;
    const survivalBonus = values.every((value) => value >= 35) ? 7 : 0;
    return clamp(average - (balancePenalty * 0.12) - collapsePenalty + survivalBonus);
  }

  function resultForScore(score) {
    if (score >= 86) {
      return {
        title: 'Císařský správce Kadaně',
        medal: '♛',
        description: 'Město působí bohatě, bezpečně a sebevědomě. Karel IV. odjíždí s dobrým dojmem a obyvatelé mají pocit, že náklady slavnosti nebyly marné.'
      };
    }
    if (score >= 72) {
      return {
        title: 'Vážený purkmistr',
        medal: '⚜',
        description: 'Příjezd se podařil. Některé skupiny zaplatily vyšší cenu než jiné, ale město udrželo pořádek a dokázalo využít císařovu návštěvu.'
      };
    }
    if (score >= 55) {
      return {
        title: 'Městský správce bez odpočinku',
        medal: '◆',
        description: 'Císař přijel a město obstálo, i když několik rozhodnutí zanechalo prázdné sklady, dluhy nebo nespokojené obyvatele.'
      };
    }
    if (score >= 38) {
      return {
        title: 'Písař, který bude dlouho vysvětlovat',
        medal: '✒',
        description: 'Slavnost se nezhroutila, ale rada bude ještě dlouho počítat škody a uklidňovat měšťany. Příště bude potřeba více rovnováhy.'
      };
    }
    return {
      title: 'Katova ulička si tvé jméno zapamatuje',
      medal: '⚠',
      description: 'Pokladna, zásoby nebo pořádek se dostaly na hranici kolapsu. Císař sice městem projel, ale tvá kariéra správce tím pravděpodobně skončila.'
    };
  }

  function renderResult() {
    elements.playScreen.hidden = true;
    elements.resultScreen.hidden = false;
    const score = calculateScore();
    const result = resultForScore(score);
    const previousBest = readBestScore();

    if (score > previousBest) {
      writeBestScore(score);
    }

    elements.resultMedal.textContent = result.medal;
    elements.resultTitle.textContent = result.title;
    elements.resultScore.textContent = String(score);
    elements.resultDescription.textContent = result.description;
    elements.resultStats.innerHTML = '';

    Object.entries(state.stats).forEach(([key, value]) => {
      const item = document.createElement('div');
      item.className = 'result-stat';
      item.innerHTML = `<b>${value}</b><span>${STAT_LABELS[key]}</span>`;
      elements.resultStats.appendChild(item);
    });

    const weakest = Object.entries(state.stats).sort((a, b) => a[1] - b[1])[0];
    const strongest = Object.entries(state.stats).sort((a, b) => b[1] - a[1])[0];
    elements.resultHistory.innerHTML = `<strong>Tvoje město po odjezdu císaře:</strong><br>Nejsilnější stránkou je <b>${STAT_LABELS[strongest[0]].toLowerCase()}</b> (${strongest[1]}). Největší problém zůstává v oblasti <b>${STAT_LABELS[weakest[0]].toLowerCase()}</b> (${weakest[1]}). Ve skutečných dějinách získala Kadaň roku 1367 právo pořádat osmidenní výroční trh.`;

    elements.progressBar.style.width = '100%';
    updateBestScoreText();
    sound(score >= 72 ? 'win' : 'end');
    announceGameEvent('finish', { score, difficulty: state.difficulty, stats: { ...state.stats } });
    elements.resultScreen.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
  }

  function startGame() {
    const selected = document.querySelector('.difficulty-option.is-selected')?.dataset.difficulty || 'scribe';
    state = createInitialState(selected);
    state.sound = elements.soundButton.getAttribute('aria-pressed') === 'true';
    elements.startScreen.hidden = true;
    elements.resultScreen.hidden = true;
    elements.playScreen.hidden = false;
    elements.shareStatus.textContent = '';
    updateStats();
    renderScene();
    sound('start');
    document.getElementById('gameApp')?.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
  }

  function restartGame() {
    elements.resultScreen.hidden = true;
    elements.playScreen.hidden = true;
    elements.startScreen.hidden = false;
    elements.shareStatus.textContent = '';
    updateBestScoreText();
    elements.startButton.focus({ preventScroll: true });
  }

  async function shareResult() {
    const score = calculateScore();
    const title = 'Příjezd císaře: Kadaň 1367';
    const text = `Ve hře Příjezd císaře jsem získal(a) ${score} bodů ze 100. Dokážeš připravit Kadaň na návštěvu Karla IV. lépe?`;
    const url = 'https://nasekadan.cz/hry/prijezd-karla-iv/';

    try {
      if (navigator.share) {
        await navigator.share({ title, text, url });
        elements.shareStatus.textContent = 'Výsledek byl připraven ke sdílení.';
      } else if (navigator.clipboard) {
        await navigator.clipboard.writeText(`${text} ${url}`);
        elements.shareStatus.textContent = 'Výsledek a odkaz jsme zkopírovali do schránky.';
      } else {
        elements.shareStatus.textContent = `${text} ${url}`;
      }
      announceGameEvent('share', { score });
    } catch (error) {
      if (error?.name !== 'AbortError') {
        elements.shareStatus.textContent = 'Sdílení se nepodařilo. Odkaz můžeš zkopírovat z adresního řádku.';
      }
    }
  }

  function readBestScore() {
    try {
      return Number.parseInt(localStorage.getItem('nasekadan-karel-game-best') || '0', 10) || 0;
    } catch {
      return 0;
    }
  }

  function writeBestScore(score) {
    try {
      localStorage.setItem('nasekadan-karel-game-best', String(score));
    } catch {
      // Hra funguje i bez localStorage.
    }
  }

  function updateBestScoreText() {
    const best = readBestScore();
    elements.bestScore.textContent = best > 0 ? `Nejlepší výsledek: ${best} bodů ze 100` : 'Nejlepší výsledek: zatím žádný';
  }

  function toggleSound() {
    const enabled = elements.soundButton.getAttribute('aria-pressed') !== 'true';
    elements.soundButton.setAttribute('aria-pressed', String(enabled));
    elements.soundButton.innerHTML = `<span aria-hidden="true">♪</span> Zvuk ${enabled ? 'zapnutý' : 'vypnutý'}`;
    state.sound = enabled;
    if (enabled) sound('choice');
  }

  function sound(type) {
    if (!state.sound && elements.soundButton.getAttribute('aria-pressed') !== 'true') return;
    try {
      audioContext = audioContext || new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      const frequencies = { start: 392, choice: 330, continue: 440, win: 523, end: 262 };
      oscillator.frequency.value = frequencies[type] || 330;
      oscillator.type = type === 'win' ? 'sine' : 'triangle';
      gain.gain.setValueAtTime(0.0001, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.08, audioContext.currentTime + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.18);
      oscillator.connect(gain).connect(audioContext.destination);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.2);
    } catch {
      // Zvuk je pouze doplněk.
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function prefersReducedMotion() {
    return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  }

  function announceGameEvent(name, detail) {
    window.dispatchEvent(new CustomEvent('nasekadan:game', { detail: { name, ...detail } }));
    if (typeof window.gtag === 'function') {
      window.gtag('event', `game_${name}`, detail);
    }
  }

  document.querySelectorAll('.difficulty-option').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.difficulty-option').forEach((option) => {
        const selected = option === button;
        option.classList.toggle('is-selected', selected);
        option.setAttribute('aria-checked', String(selected));
      });
      sound('choice');
    });
  });

  elements.startButton.addEventListener('click', startGame);
  elements.continueButton.addEventListener('click', continueGame);
  elements.restartButton.addEventListener('click', restartGame);
  elements.shareButton.addEventListener('click', shareResult);
  elements.soundButton.addEventListener('click', toggleSound);

  document.addEventListener('keydown', (event) => {
    if (elements.playScreen.hidden || state.locked) return;
    const index = Number.parseInt(event.key, 10) - 1;
    if (index >= 0 && index <= 2) {
      const button = elements.choices.querySelector(`[data-choice-index="${index}"]`);
      if (button) {
        event.preventDefault();
        button.click();
      }
    }
  });

  updateBestScoreText();
})();