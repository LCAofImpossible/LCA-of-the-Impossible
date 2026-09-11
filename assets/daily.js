(() => {
  'use strict';

  const STORAGE_KEY = 'lca-impossible-daily-v1';
  const SCORE_STEPS = Object.freeze([500, 400, 300, 200, 100]);
  const CLUE_LABELS = Object.freeze(['Season', 'Inventory', 'Impact', 'Function', 'Final clue']);
  const REQUIRED_FIELDS = Object.freeze([
    'number', 'slug', 'title', 'url', 'seasonLabel', 'lcaLabel', 'lcaCharacteristics',
    'result', 'hotspot', 'functionalUnit', 'subjectDescription'
  ]);

  const dayKey = (value = new Date()) => new Date(value).toISOString().slice(0, 10);
  const previousDayKey = (key) => {
    const date = new Date(`${key}T00:00:00.000Z`);
    date.setUTCDate(date.getUTCDate() - 1);
    return dayKey(date);
  };
  const hashDay = (key) => {
    let hash = 2166136261;
    for (const character of key) {
      hash ^= character.charCodeAt(0);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  };
  const selectEpisode = (episodes, key) => {
    const ordered = [...episodes].sort((left, right) => Number(left.number) - Number(right.number));
    return ordered.length ? ordered[hashDay(key) % ordered.length] : null;
  };
  const normalizedAnswer = (value = '') => String(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/^(the|a|an)\s+/, '');
  const eligible = (episode) => episode && REQUIRED_FIELDS.every((field) => {
    const value = episode[field];
    return Array.isArray(value) ? value.length > 0 : String(value ?? '').trim().length > 0;
  });
  const titlePattern = (title) => {
    const withoutArticle = String(title).replace(/^(the|a|an)\s+/i, '');
    const alternatives = [title, withoutArticle]
      .filter(Boolean)
      .sort((left, right) => right.length - left.length)
      .map((value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    return new RegExp(`\\b(?:${alternatives.join('|')})\\b`, 'gi');
  };
  const redactSubject = (episode) => {
    const redacted = String(episode.subjectDescription).replace(titlePattern(episode.title), '[SUBJECT REDACTED]');
    return redacted === episode.subjectDescription ? `The final case note reads: ${redacted}` : redacted;
  };
  const inventoryClue = (episode) => {
    const model = episode.structuredMetadata?.model;
    const primary = model?.primaryDriver
      ? `${String(model.primaryDriver).replaceAll('-', ' ')} is the registered primary driver`
      : `the approved case is classified as ${String(episode.lcaLabel).toLowerCase()}`;
    const signals = (model?.secondaryDrivers?.length ? model.secondaryDrivers : episode.lcaCharacteristics)
      .map((value) => String(value).replaceAll('-', ' '))
      .filter((value) => !normalizedAnswer(value).includes(normalizedAnswer(model?.primaryDriver || episode.lcaLabel)))
      .slice(0, 2);
    return signals.length
      ? `In the model, ${primary}; secondary registered signals include ${signals.join(' and ')}.`
      : `In the model, ${primary}.`;
  };
  const buildClues = (episode) => [
    `This case belongs to ${episode.seasonLabel}.`,
    inventoryClue(episode),
    `The approved headline result is ${episode.result}. ${episode.hotspot}`,
    `Reporting basis: ${episode.functionalUnit}`,
    redactSubject(episode)
  ];
  const answerVariants = (episode) => new Set([
    normalizedAnswer(episode.title),
    normalizedAnswer(String(episode.title).replace(/^(the|a|an)\s+/i, '')),
    normalizedAnswer(String(episode.slug).replaceAll('-', ' '))
  ]);
  const defaultRecord = () => ({ lastDate: '', solved: false, currentStreak: 0, bestStreak: 0, result: null });
  const safeRecord = (value) => {
    if (!value || typeof value !== 'object') return defaultRecord();
    const result = value.result && typeof value.result === 'object' ? {
      date: String(value.result.date || ''),
      episodeNumber: Number(value.result.episodeNumber) || 0,
      score: Math.max(0, Math.min(500, Number(value.result.score) || 0)),
      solved: Boolean(value.result.solved),
      clueIndex: Math.max(0, Math.min(4, Number(value.result.clueIndex) || 0)),
      attempts: Math.max(0, Number(value.result.attempts) || 0)
    } : null;
    return {
      lastDate: String(value.lastDate || ''),
      solved: Boolean(value.solved),
      currentStreak: Math.max(0, Number(value.currentStreak) || 0),
      bestStreak: Math.max(0, Number(value.bestStreak) || 0),
      result
    };
  };
  const loadRecord = (storage) => {
    let target = storage;
    try {
      target ||= window.localStorage;
      const raw = target.getItem(STORAGE_KEY);
      if (!raw) return { available: true, record: defaultRecord() };
      try {
        return { available: true, record: safeRecord(JSON.parse(raw)) };
      } catch (error) {
        console.warn('Daily Impossible ignored an invalid local record:', error);
        target.removeItem(STORAGE_KEY);
        return { available: true, record: defaultRecord() };
      }
    } catch (error) {
      console.warn('Daily Impossible storage unavailable:', error);
      return { available: false, record: defaultRecord() };
    }
  };
  const recordForDate = (value, key) => {
    const record = safeRecord(value);
    if (record.lastDate && record.lastDate < previousDayKey(key)) record.currentStreak = 0;
    return record;
  };
  const nextRecord = (previous, outcome) => {
    const prior = safeRecord(previous);
    if (prior.result?.date === outcome.date) return prior;
    const consecutive = prior.lastDate === previousDayKey(outcome.date) && prior.solved;
    const currentStreak = outcome.solved ? (consecutive ? prior.currentStreak + 1 : 1) : 0;
    return {
      lastDate: outcome.date,
      solved: Boolean(outcome.solved),
      currentStreak,
      bestStreak: Math.max(prior.bestStreak, currentStreak),
      result: {
        date: outcome.date,
        episodeNumber: Number(outcome.episodeNumber),
        score: Math.max(0, Math.min(500, Number(outcome.score) || 0)),
        solved: Boolean(outcome.solved),
        clueIndex: Math.max(0, Math.min(4, Number(outcome.clueIndex) || 0)),
        attempts: Math.max(0, Number(outcome.attempts) || 0)
      }
    };
  };

  window.ImpossibleDaily = Object.freeze({
    STORAGE_KEY, SCORE_STEPS, dayKey, previousDayKey, hashDay, selectEpisode,
    normalizedAnswer, eligible, buildClues, answerVariants, safeRecord, loadRecord, recordForDate, nextRecord
  });

  const form = document.getElementById('daily-answer-form');
  const clueList = document.getElementById('daily-clue-list');
  if (!form || !clueList) return;

  const elements = {
    date: document.getElementById('daily-date'),
    points: document.getElementById('daily-points'),
    streak: document.getElementById('daily-streak'),
    bestStreak: document.getElementById('daily-best-streak'),
    state: document.getElementById('daily-state'),
    status: document.getElementById('daily-status'),
    input: document.getElementById('daily-answer-input'),
    options: document.getElementById('daily-answer-options'),
    submit: document.getElementById('daily-submit'),
    feedback: document.getElementById('daily-feedback'),
    reveal: document.getElementById('daily-reveal'),
    result: document.getElementById('daily-result'),
    resultState: document.getElementById('daily-result-state'),
    resultTitle: document.getElementById('daily-result-title'),
    resultSubject: document.getElementById('daily-result-subject'),
    resultScore: document.getElementById('daily-result-score'),
    resultEpisode: document.getElementById('daily-result-episode'),
    resultSeason: document.getElementById('daily-result-season'),
    resultImpact: document.getElementById('daily-result-impact'),
    resultHotspot: document.getElementById('daily-result-hotspot'),
    resultLink: document.getElementById('daily-result-link'),
    returnNote: document.getElementById('daily-return-note')
  };
  const today = dayKey();
  const state = {
    episodes: [], current: null, clues: [], clueIndex: 0, attempts: 0,
    resolved: false, storageAvailable: true, record: defaultRecord()
  };
  const setText = (element, value) => { if (element) element.textContent = String(value); };
  const formatDate = (key) => new Intl.DateTimeFormat('en-GB', {
    timeZone: 'UTC', day: '2-digit', month: 'short', year: 'numeric'
  }).format(new Date(`${key}T00:00:00Z`)).toUpperCase();
  const setFeedback = (message, type = '') => {
    elements.feedback.className = `lab-feedback${type ? ` is-${type}` : ''}`;
    setText(elements.feedback, message);
  };
  const renderStats = () => {
    setText(elements.points, state.resolved ? 0 : SCORE_STEPS[state.clueIndex]);
    setText(elements.streak, state.record.currentStreak);
    setText(elements.bestStreak, state.record.bestStreak);
    setText(elements.state, state.resolved ? 'COMPLETE' : 'OPEN');
  };
  const renderClues = (revealAll = false) => {
    [...clueList.querySelectorAll('[data-daily-clue]')].forEach((item, index) => {
      const visible = revealAll || index <= state.clueIndex;
      item.classList.toggle('is-locked', !visible);
      item.classList.toggle('is-current', !state.resolved && index === state.clueIndex);
      const paragraph = item.querySelector('p');
      if (paragraph) paragraph.textContent = visible ? state.clues[index] : 'Encrypted';
    });
  };
  const renderOptions = () => {
    const fragment = document.createDocumentFragment();
    [...state.episodes].sort((left, right) => left.title.localeCompare(right.title)).forEach((episode) => {
      const option = document.createElement('option');
      option.value = episode.title;
      fragment.appendChild(option);
    });
    elements.options.replaceChildren(fragment);
  };
  const storeOutcome = (solved, score) => {
    state.record = nextRecord(state.record, {
      date: today,
      episodeNumber: state.current.number,
      score,
      solved,
      clueIndex: state.clueIndex,
      attempts: state.attempts
    });
    if (!state.storageAvailable) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state.record));
    } catch (error) {
      state.storageAvailable = false;
      console.warn('Daily Impossible result could not be stored:', error);
    }
  };
  const showResult = (solved, score, restored = false) => {
    state.resolved = true;
    elements.input.disabled = true;
    elements.submit.disabled = true;
    elements.reveal.disabled = true;
    elements.result.hidden = false;
    renderClues(restored);
    renderStats();
    setText(elements.resultState, solved ? `DAILY CASE IDENTIFIED · +${score} PTS` : 'DAILY CASE DECLASSIFIED · 0 PTS');
    setText(elements.resultTitle, state.current.title);
    setText(elements.resultSubject, state.current.subjectDescription);
    setText(elements.resultScore, score);
    setText(elements.resultEpisode, `#${state.current.number}`);
    setText(elements.resultSeason, state.current.seasonLabel);
    setText(elements.resultImpact, state.current.result);
    setText(elements.resultHotspot, state.current.hotspot);
    elements.resultLink.href = state.current.url;
    setText(elements.status, restored ? "Today's challenge is already complete on this browser." : 'Daily identity confirmed against the registry.');
    setFeedback(
      restored
        ? `${solved ? 'Solved' : 'Revealed'} today for ${score} points. Return after 00:00 UTC for a new case.`
        : solved ? `Correct. You identified today's case from clue ${state.clueIndex + 1}.` : `Today's subject was ${state.current.title}.`,
      solved ? 'correct' : 'wrong'
    );
    setText(elements.returnNote, state.storageAvailable
      ? 'Your daily result and streak are stored only in this browser. A new case becomes available at 00:00 UTC.'
      : 'Browser storage is unavailable, so this result cannot be retained after you leave. A new case becomes available at 00:00 UTC.');
    if (!restored) elements.result.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'nearest'
    });
  };
  const finish = (solved, score = 0) => {
    if (state.resolved) return;
    storeOutcome(solved, score);
    showResult(solved, score, false);
  };
  const revealNext = (fromWrongGuess = false) => {
    if (state.resolved) return;
    if (state.clueIndex >= state.clues.length - 1) {
      finish(false, 0);
      return;
    }
    state.clueIndex += 1;
    renderClues();
    renderStats();
    elements.reveal.textContent = state.clueIndex === state.clues.length - 1 ? 'Reveal answer' : 'Reveal next clue';
    setText(elements.status, `Clue ${String(state.clueIndex + 1).padStart(2, '0')} of 05 unlocked.`);
    setFeedback(fromWrongGuess ? 'Not this case. The next clue has been unlocked.' : `${CLUE_LABELS[state.clueIndex]} clue unlocked.`, fromWrongGuess ? 'wrong' : '');
    elements.input.focus();
  };
  const restoreToday = () => {
    const stored = state.record.result;
    if (!stored || stored.date !== today) return false;
    const storedEpisode = state.episodes.find((episode) => Number(episode.number) === stored.episodeNumber);
    if (storedEpisode) {
      state.current = storedEpisode;
      state.clues = buildClues(storedEpisode);
    }
    state.clueIndex = stored.clueIndex;
    state.attempts = stored.attempts;
    showResult(stored.solved, stored.score, true);
    return true;
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (state.resolved || !state.current) return;
    const answer = elements.input.value.trim();
    if (!answer) {
      setFeedback('Enter an episode title before submitting.', 'wrong');
      return;
    }
    state.attempts += 1;
    if (answerVariants(state.current).has(normalizedAnswer(answer))) {
      finish(true, SCORE_STEPS[state.clueIndex]);
      return;
    }
    elements.input.select();
    revealNext(true);
  });
  elements.reveal.addEventListener('click', () => revealNext(false));

  setText(elements.date, formatDate(today));
  const stored = loadRecord();
  state.storageAvailable = stored.available;
  state.record = recordForDate(stored.record, today);

  fetch('episodes.json', { cache: 'no-store', credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`Registry request returned ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      state.episodes = Array.isArray(registry.episodes) ? registry.episodes.filter(eligible) : [];
      if (!state.episodes.length) throw new Error('No complete episode records are available');
      state.current = selectEpisode(state.episodes, today);
      state.clues = buildClues(state.current);
      renderOptions();
      if (restoreToday()) return;
      elements.input.disabled = false;
      elements.submit.disabled = false;
      elements.reveal.disabled = false;
      renderClues();
      renderStats();
      setText(elements.status, 'Clue 01 of 05 unlocked. Subject identity remains classified.');
      setFeedback('Submit a title now for 500 points, or reveal another clue.');
      elements.input.focus();
    })
    .catch((error) => {
      console.warn('Daily Impossible unavailable:', error);
      setText(elements.state, 'OFFLINE');
      setText(elements.status, "Today's case could not be loaded.");
      setFeedback('The daily challenge is temporarily unavailable. The complete episode archive remains accessible.', 'wrong');
      elements.input.disabled = true;
      elements.submit.disabled = true;
      elements.reveal.disabled = true;
    });
})();
