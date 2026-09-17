(() => {
  'use strict';

  const map = document.getElementById('origins-map');
  if (!map) return;

  const SESSION_ROUNDS = 10;
  const POINTS_PER_COMPONENT = 100;
  const PERFECT_ORIGIN_BONUS = 50;
  const MAX_POINTS_PER_CASE = (POINTS_PER_COMPONENT * 2) + PERFECT_ORIGIN_BONUS;
  const fallbackConfig = Object.freeze({
    rounds: SESSION_ROUNDS,
    regionChoices: 0,
    subjectDescription: true,
    mapLabels: true,
    eraRanges: true,
    qualifiedFirst: false
  });
  const elements = {
    caseCount: document.getElementById('origins-case-count'),
    score: document.getElementById('origins-score'),
    round: document.getElementById('origins-round'),
    regionCorrect: document.getElementById('origins-region-correct'),
    eraCorrect: document.getElementById('origins-era-correct'),
    status: document.getElementById('origins-status'),
    startPanel: document.getElementById('origins-start-panel'),
    start: document.getElementById('origins-start'),
    roundPanel: document.getElementById('origins-round-panel'),
    episode: document.getElementById('origins-episode'),
    season: document.getElementById('origins-season'),
    subjectTitle: document.getElementById('origins-subject-title'),
    subjectDescription: document.getElementById('origins-subject-description'),
    mapLabels: document.getElementById('origins-map-labels'),
    mapHudName: document.getElementById('origins-map-hud-name'),
    mapBeacon: document.getElementById('origins-map-beacon'),
    regionSelect: document.getElementById('origins-region-select'),
    eraPanel: document.getElementById('origins-era-panel'),
    eraOptions: document.getElementById('origins-era-options'),
    confirm: document.getElementById('origins-confirm'),
    next: document.getElementById('origins-next'),
    feedback: document.getElementById('origins-feedback'),
    reveal: document.getElementById('origins-reveal'),
    roundPoints: document.getElementById('origins-round-points'),
    revealTitle: document.getElementById('origins-reveal-title'),
    revealOrigin: document.getElementById('origins-reveal-origin'),
    revealRegion: document.getElementById('origins-reveal-region'),
    revealEra: document.getElementById('origins-reveal-era'),
    revealDate: document.getElementById('origins-reveal-date'),
    revealBasis: document.getElementById('origins-reveal-basis'),
    revealEvent: document.getElementById('origins-reveal-event'),
    revealSource: document.getElementById('origins-reveal-source'),
    revealAmbiguity: document.getElementById('origins-reveal-ambiguity'),
    episodeLink: document.getElementById('origins-episode-link'),
    final: document.getElementById('origins-final'),
    finalCopy: document.getElementById('origins-final-copy'),
    finalRegions: document.getElementById('origins-final-regions'),
    finalEras: document.getElementById('origins-final-eras'),
    finalCases: document.getElementById('origins-final-cases'),
    finalPerfect: document.getElementById('origins-final-perfect'),
    again: document.getElementById('origins-again')
  };
  const resultTarget = elements.final?.querySelector('[data-lab-result-scorecard]');
  const difficultySystem = window.ImpossibleLabDifficulty;
  const regionPaths = [...map.querySelectorAll('[data-region]')];
  const regionLabels = [...map.querySelectorAll('[data-map-label]')];
  const REGION_ANCHORS = Object.freeze({
    'north-america': [205, 160],
    'latin-america-caribbean': [276, 338],
    'northern-europe': [493, 103],
    'western-europe': [490, 139],
    'southern-europe-mediterranean': [520, 169],
    'eastern-europe': [558, 126],
    'north-africa': [491, 242],
    'sub-saharan-africa': [531, 345],
    'west-asia': [604, 214],
    'central-asia': [674, 153],
    'south-asia': [683, 257],
    'east-asia': [796, 175],
    'southeast-asia': [797, 285],
    oceania: [865, 362]
  });
  const state = {
    pool: [],
    regions: [],
    eraBands: [],
    cases: [],
    index: 0,
    selectedRegion: '',
    selectedEra: '',
    revealedRegion: '',
    activeRegions: new Set(),
    score: 0,
    correctRegions: 0,
    correctEras: 0,
    perfectOrigins: 0,
    streak: 0,
    bestStreak: 0,
    locked: true
  };

  const config = () => ({ ...fallbackConfig, ...(difficultySystem?.config('origins') || {}) });

  const shuffle = (values) => {
    const copy = [...values];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const target = Math.floor(Math.random() * (index + 1));
      [copy[index], copy[target]] = [copy[target], copy[index]];
    }
    return copy;
  };
  const setStatus = (message) => {
    if (elements.status) elements.status.textContent = message;
  };
  const setFeedback = (message, stateName = '') => {
    if (!elements.feedback) return;
    elements.feedback.textContent = message;
    elements.feedback.classList.toggle('is-correct', stateName === 'correct');
    elements.feedback.classList.toggle('is-partial', stateName === 'partial');
  };
  const regionLabel = (id) => state.regions.find((region) => region.id === id)?.label || id;
  const setMapFocus = (id = '', prefix = '') => {
    regionLabels.forEach((label) => label.classList.toggle('is-active', label.dataset.mapLabel === id));
    if (!elements.mapHudName) return;
    elements.mapHudName.textContent = id
      ? `${prefix ? `${prefix} · ` : ''}${regionLabel(id)}`
      : 'Scan the atlas';
  };
  const setMapBeacon = (id = '') => {
    if (!elements.mapBeacon) return;
    const anchor = REGION_ANCHORS[id];
    if (!anchor) {
      elements.mapBeacon.hidden = true;
      elements.mapBeacon.removeAttribute('transform');
      return;
    }
    elements.mapBeacon.setAttribute('transform', `translate(${anchor[0]} ${anchor[1]})`);
    elements.mapBeacon.hidden = false;
  };
  const restoreMapFocus = () => {
    if (state.revealedRegion) {
      setMapFocus(state.revealedRegion, 'RECOVERED ORIGIN');
      return;
    }
    setMapFocus(state.selectedRegion, state.selectedRegion ? 'REGION SELECTED' : '');
  };
  const eraFor = (orderYear) => state.eraBands.find((band) => {
    const aboveMinimum = band.minimumOrderYear === undefined || orderYear >= band.minimumOrderYear;
    const belowMaximum = band.maximumOrderYear === undefined || orderYear <= band.maximumOrderYear;
    return aboveMinimum && belowMaximum;
  });
  const current = () => state.cases[state.index];

  const eraRangeLabel = (band) => {
    if (band.maximumOrderYear !== undefined && band.minimumOrderYear === undefined) return `Before ${band.maximumOrderYear + 1} CE`;
    if (band.minimumOrderYear !== undefined && band.maximumOrderYear !== undefined) return `${band.minimumOrderYear}–${band.maximumOrderYear}`;
    return `${band.minimumOrderYear}+`;
  };

  const populateRegionSelect = (regionIds = state.regions.map((region) => region.id)) => {
    const permitted = new Set(regionIds);
    const regionFragment = document.createDocumentFragment();
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = 'Choose a geographic region';
    regionFragment.appendChild(placeholder);
    state.regions.filter((region) => permitted.has(region.id)).forEach((region) => {
      const option = document.createElement('option');
      option.value = region.id;
      option.textContent = region.label;
      regionFragment.appendChild(option);
    });
    elements.regionSelect.replaceChildren(regionFragment);
  };

  const populateControls = () => {
    populateRegionSelect();

    const eraFragment = document.createDocumentFragment();
    state.eraBands.forEach((band) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'origins-era-option';
      button.dataset.era = band.id;
      button.setAttribute('aria-pressed', 'false');
      const label = document.createElement('strong');
      const range = document.createElement('small');
      label.textContent = band.label;
      range.textContent = eraRangeLabel(band);
      button.append(label, range);
      button.addEventListener('click', () => selectEra(band.id));
      eraFragment.appendChild(button);
    });
    elements.eraOptions.replaceChildren(eraFragment);
  };

  const setControlState = (disabled) => {
    elements.regionSelect.disabled = disabled;
    regionPaths.forEach((path) => {
      const available = !state.activeRegions.size || state.activeRegions.has(path.dataset.region);
      const inactive = disabled || !available;
      path.setAttribute('aria-disabled', String(inactive));
      path.tabIndex = inactive ? -1 : 0;
      path.classList.toggle('is-unavailable', !available);
    });
    elements.eraOptions.querySelectorAll('button').forEach((button) => {
      button.disabled = disabled;
    });
  };

  const updateConfirm = () => {
    elements.confirm.disabled = state.locked || !state.selectedRegion || !state.selectedEra;
  };

  const selectRegion = (id) => {
    if (state.locked || (state.activeRegions.size && !state.activeRegions.has(id)) || !state.regions.some((region) => region.id === id)) return;
    state.selectedRegion = id;
    elements.regionSelect.value = id;
    regionPaths.forEach((path) => {
      const selected = path.dataset.region === id;
      path.classList.toggle('is-selected', selected);
      path.setAttribute('aria-pressed', String(selected));
    });
    setMapFocus(id, 'REGION SELECTED');
    setFeedback(`${regionLabel(id)} selected. Choose a period, then confirm.`);
    updateConfirm();
  };

  function selectEra(id) {
    if (state.locked || !state.eraBands.some((band) => band.id === id)) return;
    state.selectedEra = id;
    elements.eraOptions.querySelectorAll('button').forEach((button) => {
      const selected = button.dataset.era === id;
      button.classList.toggle('is-selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    setFeedback(`${state.eraBands.find((band) => band.id === id)?.label || id} selected. Confirm when ready.`);
    updateConfirm();
  }

  const resetSelections = () => {
    state.selectedRegion = '';
    state.selectedEra = '';
    state.revealedRegion = '';
    elements.regionSelect.value = '';
    regionPaths.forEach((path) => {
      path.classList.remove('is-selected', 'is-correct', 'is-wrong');
      path.setAttribute('aria-pressed', 'false');
    });
    setMapBeacon();
    setMapFocus();
    elements.eraOptions.querySelectorAll('button').forEach((button) => {
      button.classList.remove('is-selected', 'is-correct', 'is-wrong');
      button.setAttribute('aria-pressed', 'false');
    });
  };

  const configureRoundAssists = (entry) => {
    const rules = config();
    const allRegionIds = state.regions.map((region) => region.id);
    if (rules.regionChoices > 0 && rules.regionChoices < allRegionIds.length) {
      const accepted = [...new Set(entry.acceptedMapRegions)];
      const decoys = shuffle(allRegionIds.filter((id) => !accepted.includes(id)))
        .slice(0, Math.max(0, rules.regionChoices - accepted.length));
      state.activeRegions = new Set(shuffle([...accepted, ...decoys]));
    } else {
      state.activeRegions = new Set(allRegionIds);
    }
    populateRegionSelect([...state.activeRegions]);
    if (elements.mapLabels) elements.mapLabels.toggleAttribute('hidden', !rules.mapLabels);
    elements.subjectDescription.hidden = !rules.subjectDescription;
    elements.eraOptions.querySelectorAll('small').forEach((range) => {
      range.hidden = !rules.eraRanges;
    });
  };

  const buildSession = () => {
    const rules = config();
    const roundTarget = Math.min(rules.rounds, state.pool.length);
    const seasonOne = shuffle(state.pool.filter((entry) => entry.episode.seasonNumber === 1));
    const otherPool = state.pool.filter((entry) => entry.episode.seasonNumber !== 1);
    const otherCases = rules.qualifiedFirst
      ? [
        ...shuffle(otherPool.filter((entry) => entry.confidence === 'qualified')),
        ...shuffle(otherPool.filter((entry) => entry.confidence !== 'qualified'))
      ]
      : shuffle(otherPool);
    const seasonOneTarget = Math.min(2, seasonOne.length, roundTarget);
    const selected = [
      ...seasonOne.slice(0, seasonOneTarget),
      ...otherCases.slice(0, roundTarget - seasonOneTarget)
    ];
    if (selected.length < roundTarget) {
      const used = new Set(selected.map((entry) => entry.episodeNumber));
      selected.push(...shuffle(state.pool.filter((entry) => !used.has(entry.episodeNumber))).slice(0, roundTarget - selected.length));
    }
    return shuffle(selected);
  };

  const renderRound = () => {
    const entry = current();
    if (!entry) return;
    state.locked = false;
    resetSelections();
    configureRoundAssists(entry);
    setControlState(false);
    elements.confirm.hidden = false;
    elements.confirm.disabled = true;
    elements.next.hidden = true;
    elements.reveal.hidden = true;
    elements.roundPoints.textContent = `Round score: 0 / ${MAX_POINTS_PER_CASE}`;
    elements.round.textContent = `${state.index + 1} / ${state.cases.length}`;
    elements.episode.textContent = `EPISODE ${String(entry.episode.number).padStart(2, '0')}`;
    elements.season.textContent = entry.episode.seasonLabel;
    elements.subjectTitle.textContent = entry.episode.title;
    elements.subjectDescription.textContent = entry.episode.subjectDescription;
    setStatus(`Case ${state.index + 1}: locate ${entry.episode.title} and recover its historical period. Up to ${MAX_POINTS_PER_CASE} points are available.`);
    setFeedback('Select one region and one period.');
    elements.roundPanel.hidden = false;
    elements.roundPanel.scrollIntoView({ behavior: 'auto', block: 'start' });
  };

  const renderReveal = (entry, expectedEra) => {
    elements.revealTitle.textContent = entry.episode.title;
    elements.revealOrigin.textContent = entry.originLabel;
    elements.revealRegion.textContent = entry.acceptedMapRegions.map(regionLabel).join(' / ');
    elements.revealEra.textContent = expectedEra.label;
    elements.revealDate.textContent = entry.timeline.dateLabel;
    elements.revealBasis.textContent = entry.locationBasis;
    elements.revealEvent.textContent = entry.timeline.event;
    elements.revealSource.textContent = `Historical basis: ${entry.timeline.source}`;
    if (entry.ambiguityNote) {
      elements.revealAmbiguity.textContent = `Archive qualification: ${entry.ambiguityNote}`;
      elements.revealAmbiguity.hidden = false;
    } else {
      elements.revealAmbiguity.textContent = '';
      elements.revealAmbiguity.hidden = true;
    }
    elements.episodeLink.href = entry.episode.url;
    elements.episodeLink.textContent = `Open Episode #${String(entry.episode.number).padStart(2, '0')} →`;
    elements.reveal.hidden = false;
  };

  const assessRound = () => {
    const entry = current();
    if (state.locked || !entry || !state.selectedRegion || !state.selectedEra) return;
    state.locked = true;
    const expectedEra = eraFor(entry.timeline.orderYear);
    const regionIsCorrect = entry.acceptedMapRegions.includes(state.selectedRegion);
    const eraIsCorrect = expectedEra?.id === state.selectedEra;
    const perfectOrigin = regionIsCorrect && eraIsCorrect;
    const gained = (regionIsCorrect ? POINTS_PER_COMPONENT : 0)
      + (eraIsCorrect ? POINTS_PER_COMPONENT : 0)
      + (perfectOrigin ? PERFECT_ORIGIN_BONUS : 0);
    if (regionIsCorrect) state.correctRegions += 1;
    if (eraIsCorrect) state.correctEras += 1;
    if (perfectOrigin) {
      state.perfectOrigins += 1;
      state.streak += 1;
      state.bestStreak = Math.max(state.bestStreak, state.streak);
    } else {
      state.streak = 0;
    }
    state.score += gained;
    elements.score.textContent = state.score.toLocaleString('en-US');
    elements.regionCorrect.textContent = String(state.correctRegions);
    elements.eraCorrect.textContent = String(state.correctEras);
    elements.roundPoints.textContent = `Round score: ${gained} / ${MAX_POINTS_PER_CASE}`;

    regionPaths.forEach((path) => {
      const id = path.dataset.region;
      path.classList.toggle('is-correct', entry.acceptedMapRegions.includes(id));
      path.classList.toggle('is-wrong', id === state.selectedRegion && !regionIsCorrect);
    });
    state.revealedRegion = entry.mapRegion || entry.acceptedMapRegions[0];
    setMapBeacon(state.revealedRegion);
    setMapFocus(state.revealedRegion, 'RECOVERED ORIGIN');
    elements.eraOptions.querySelectorAll('button').forEach((button) => {
      button.classList.toggle('is-correct', button.dataset.era === expectedEra?.id);
      button.classList.toggle('is-wrong', button.dataset.era === state.selectedEra && !eraIsCorrect);
    });
    setControlState(true);
    elements.confirm.disabled = true;
    elements.confirm.hidden = true;
    elements.next.hidden = false;
    elements.next.textContent = state.index + 1 >= state.cases.length ? 'View expedition report →' : 'Next case →';

    if (perfectOrigin) {
      setFeedback(`Origin recovered: both geography and period are correct. +${gained} points · streak ${state.streak}.`, 'correct');
    } else if (regionIsCorrect || eraIsCorrect) {
      setFeedback(`Partial recovery: the ${regionIsCorrect ? 'region' : 'period'} is correct. +${gained} points.`, 'partial');
    } else {
      setFeedback('Archive mismatch. No points awarded; review the recovered evidence below.', 'partial');
    }
    setStatus('Origin revealed. Review the geographic and historical evidence before continuing.');
    renderReveal(entry, expectedEra);
  };

  const finishSession = () => {
    state.locked = true;
    elements.roundPanel.hidden = true;
    elements.reveal.hidden = true;
    const maximum = state.cases.length * MAX_POINTS_PER_CASE;
    const accuracy = state.cases.length
      ? ((state.correctRegions + state.correctEras) / (state.cases.length * 2)) * 100
      : 0;
    elements.finalCopy.textContent = `${state.correctRegions} geographic regions and ${state.correctEras} historical periods were recovered across ${state.cases.length} cases. Best perfect streak: ${state.bestStreak}.`;
    elements.finalRegions.textContent = `${state.correctRegions} / ${state.cases.length}`;
    elements.finalEras.textContent = `${state.correctEras} / ${state.cases.length}`;
    elements.finalCases.textContent = String(state.cases.length);
    elements.finalPerfect.textContent = `${state.perfectOrigins} / ${state.cases.length}`;
    window.ImpossibleLabResults?.render(resultTarget, {
      title: 'Impossible Origins complete',
      score: state.score,
      maximum,
      completion: 100,
      accuracy,
      scoreLabel: 'Origin score'
    });
    elements.final.hidden = false;
    setStatus('Expedition complete. Review your result and record status below.');
    elements.final.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  };

  const startSession = () => {
    state.cases = buildSession();
    state.index = 0;
    state.score = 0;
    state.correctRegions = 0;
    state.correctEras = 0;
    state.perfectOrigins = 0;
    state.streak = 0;
    state.bestStreak = 0;
    elements.score.textContent = '0';
    elements.regionCorrect.textContent = '0';
    elements.eraCorrect.textContent = '0';
    elements.round.textContent = `0 / ${state.cases.length}`;
    resultTarget?.replaceChildren();
    elements.final.hidden = true;
    elements.startPanel.hidden = true;
    renderRound();
  };

  regionPaths.forEach((path) => {
    path.addEventListener('click', () => selectRegion(path.dataset.region));
    path.addEventListener('pointerenter', () => {
      if (!path.classList.contains('is-unavailable')) setMapFocus(path.dataset.region, 'TRACE REGION');
    });
    path.addEventListener('pointerleave', restoreMapFocus);
    path.addEventListener('focus', () => setMapFocus(path.dataset.region, 'TRACE REGION'));
    path.addEventListener('blur', restoreMapFocus);
    path.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      selectRegion(path.dataset.region);
    });
  });
  elements.regionSelect.addEventListener('change', () => selectRegion(elements.regionSelect.value));
  elements.confirm.addEventListener('click', assessRound);
  elements.next.addEventListener('click', () => {
    if (state.index + 1 >= state.cases.length) {
      finishSession();
      return;
    }
    state.index += 1;
    renderRound();
  });
  elements.start.addEventListener('click', startSession);
  elements.again.addEventListener('click', startSession);

  Promise.all([
    fetch('episodes.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    }),
    fetch('timeline.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Timeline registry returned ${response.status}`);
      return response.json();
    }),
    fetch('origins.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Origins registry returned ${response.status}`);
      return response.json();
    })
  ]).then(([episodeRegistry, timelineRegistry, originsRegistry]) => {
    const episodes = new Map((episodeRegistry.episodes || []).map((episode) => [Number(episode.number), episode]));
    const timeline = new Map((timelineRegistry.entries || []).map((entry) => [Number(entry.episodeNumber), entry]));
    state.regions = Array.isArray(originsRegistry.macroRegions) ? originsRegistry.macroRegions : [];
    state.eraBands = Array.isArray(originsRegistry.eraBands) ? originsRegistry.eraBands : [];
    state.pool = (originsRegistry.entries || [])
      .filter((entry) => entry?.eligible)
      .map((entry) => ({
        ...entry,
        episode: episodes.get(Number(entry.episodeNumber)),
        timeline: timeline.get(Number(entry.episodeNumber))
      }))
      .filter((entry) => entry.episode?.title && entry.episode?.url && entry.timeline?.orderYear !== undefined && eraFor(entry.timeline.orderYear));
    if (state.pool.length < Math.max(SESSION_ROUNDS, config().rounds) || state.regions.length !== 14 || state.eraBands.length !== 6) {
      throw new Error('The Origins registry does not expose a complete playable pool.');
    }
    populateControls();
    setControlState(true);
    elements.caseCount.textContent = String(state.pool.length);
    elements.start.disabled = false;
    elements.start.textContent = 'Start expedition';
    setStatus(`${state.pool.length} geographic records ready. Choose a level and start the expedition.`);
  }).catch((error) => {
    console.error(error);
    elements.start.disabled = true;
    elements.start.textContent = 'Archive unavailable';
    setStatus('The geographic archive could not be loaded. Use the complete episode Archive instead.');
    setFeedback('Impossible Origins is temporarily unavailable.');
  });
})();
