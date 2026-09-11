(() => {
  'use strict';

  const STORAGE_KEY = 'lca-impossible-lab-difficulty-v1';
  const SCHEMA_VERSION = 1;
  const DEFAULT_LEVEL = 'analyst';
  const PLAY_TARGET = 'lab-game-area';
  const LEVELS = Object.freeze(['explorer', 'analyst', 'impossible']);
  const GAME_FILES = new Set(['lab.html', 'lab-crossword.html', 'lab-alphabet.html', 'lab-spin.html']);
  const progressSystem = window.ImpossibleLabProgress;

  const LEVEL_DETAILS = Object.freeze({
    explorer: Object.freeze({
      label: 'Explorer',
      short: 'More guidance and room to learn.',
      description: 'More guidance, a gentler pace and the same archive-powered subjects.'
    }),
    analyst: Object.freeze({
      label: 'Analyst',
      short: 'The standard Lab rules.',
      description: 'The standard rules. Only Analyst records contribute to the official Lab Score.'
    }),
    impossible: Object.freeze({
      label: 'Impossible',
      short: 'Less help and tighter limits.',
      description: 'Fewer assists and tighter limits for a separate expert-level personal best.'
    })
  });

  const GAME_CONFIGS = Object.freeze({
    guess: Object.freeze({
      explorer: Object.freeze({ choices: 4, suggestions: false }),
      analyst: Object.freeze({ choices: 0, suggestions: true }),
      impossible: Object.freeze({ choices: 0, suggestions: false })
    }),
    crossword: Object.freeze({
      explorer: Object.freeze({ targetWords: 8, minWords: 6, freeInitials: true, revealLimit: null }),
      analyst: Object.freeze({ targetWords: 10, minWords: 8, freeInitials: false, revealLimit: null }),
      impossible: Object.freeze({ targetWords: 12, minWords: 10, freeInitials: false, revealLimit: 3 })
    }),
    alphabet: Object.freeze({
      explorer: Object.freeze({ letters: 12, seconds: 300, passLimit: null }),
      analyst: Object.freeze({ letters: 18, seconds: 180, passLimit: null }),
      impossible: Object.freeze({ letters: 18, seconds: 120, passLimit: 3 })
    }),
    spin: Object.freeze({
      explorer: Object.freeze({ spins: 20, solveAttempts: 5, vowelCost: 75, hintCost: 150, wrongSolutionCost: 100 }),
      analyst: Object.freeze({ spins: 15, solveAttempts: 3, vowelCost: 150, hintCost: 300, wrongSolutionCost: 200 }),
      impossible: Object.freeze({ spins: 10, solveAttempts: 2, vowelCost: 200, hintCost: 450, wrongSolutionCost: 300 })
    })
  });

  const GAME_DESCRIPTIONS = Object.freeze({
    guess: Object.freeze({
      explorer: 'Choose from four registry-derived subjects while the five clues unlock normally.',
      analyst: 'Enter or select a subject title from the complete registry suggestion list.',
      impossible: 'Enter the subject title without suggestions or multiple-choice assistance.'
    }),
    crossword: Object.freeze({
      explorer: 'Solve an 8-word grid with the first letter of every answer already revealed for free.',
      analyst: 'Solve the standard 10-word grid with optional 10-point letter reveals.',
      impossible: 'Solve a 12-word grid with no starter letters and only three paid reveals.'
    }),
    alphabet: Object.freeze({
      explorer: 'Resolve 12 initials in five minutes with unlimited passes.',
      analyst: 'Resolve up to 18 initials in three minutes with unlimited passes.',
      impossible: 'Resolve up to 18 initials in two minutes with no more than three passes.'
    }),
    spin: Object.freeze({
      explorer: 'Play with 20 spins, five solution attempts and lower assistance costs.',
      analyst: 'Play the standard round with 15 spins, three attempts and standard costs.',
      impossible: 'Play with 10 spins, two solution attempts and higher assistance costs.'
    })
  });

  const finiteNumber = (value) => Number.isFinite(Number(value)) ? Number(value) : 0;
  const rounded = (value) => Math.round(finiteNumber(value));
  const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
  const validLevel = (level) => LEVELS.includes(level) ? level : DEFAULT_LEVEL;
  const emptyState = () => ({ version: SCHEMA_VERSION, selected: DEFAULT_LEVEL, games: {} });

  const storageAvailable = () => {
    try {
      const probe = `${STORAGE_KEY}-probe`;
      window.localStorage.setItem(probe, '1');
      window.localStorage.removeItem(probe);
      return true;
    } catch (error) {
      return false;
    }
  };

  const available = storageAvailable();
  let ephemeralSelection = null;

  const sanitizeRecord = (record) => {
    if (!record || typeof record !== 'object') return null;
    return {
      bestScore: Math.max(0, rounded(record.bestScore)),
      bestMaximum: Math.max(0, rounded(record.bestMaximum)),
      bestNormalized: clamp(rounded(record.bestNormalized), 0, 1000),
      plays: Math.max(1, rounded(record.plays))
    };
  };

  const sanitize = (candidate) => {
    const clean = emptyState();
    if (!candidate || typeof candidate !== 'object' || candidate.version !== SCHEMA_VERSION) return clean;
    clean.selected = validLevel(candidate.selected);
    Object.keys(GAME_CONFIGS).forEach((gameId) => {
      const levels = {};
      LEVELS.forEach((level) => {
        const record = sanitizeRecord(candidate.games?.[gameId]?.[level]);
        if (record) levels[level] = record;
      });
      if (Object.keys(levels).length) clean.games[gameId] = levels;
    });
    return clean;
  };

  const read = () => {
    if (!available) return emptyState();
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      return stored ? sanitize(JSON.parse(stored)) : emptyState();
    } catch (error) {
      return emptyState();
    }
  };

  const write = (state) => {
    if (!available) return false;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(sanitize(state)));
      return true;
    } catch (error) {
      return false;
    }
  };

  const query = () => new URLSearchParams(window.location?.search || '');
  const isRunMode = () => query().get('run') === '1';
  const current = () => isRunMode() ? DEFAULT_LEVEL : validLevel(query().get('difficulty') || ephemeralSelection || read().selected);
  const detail = (level = current()) => LEVEL_DETAILS[validLevel(level)];
  const config = (gameId, level = current()) => GAME_CONFIGS[gameId]?.[validLevel(level)] || {};
  const descriptionFor = (level = current(), gameId = document.body?.dataset?.labGame || '') => (
    GAME_DESCRIPTIONS[gameId]?.[validLevel(level)] || detail(level).description
  );

  const set = (level) => {
    const selected = validLevel(level);
    ephemeralSelection = selected;
    const state = read();
    state.selected = selected;
    write(state);
    return selected;
  };

  const mergeRecords = (left, right) => {
    if (!left) return right ? { ...right } : null;
    if (!right) return { ...left };
    const rawFromLeft = left.bestScore >= right.bestScore;
    return {
      bestScore: Math.max(left.bestScore, right.bestScore),
      bestMaximum: rawFromLeft ? left.bestMaximum : right.bestMaximum,
      bestNormalized: Math.max(left.bestNormalized, right.bestNormalized),
      plays: Math.max(left.plays, right.plays)
    };
  };

  const officialRecord = (gameId) => progressSystem?.summarize()?.games?.[gameId] || null;

  const recordFor = (gameId, level = current(), state = read()) => {
    const selected = validLevel(level);
    const stored = sanitizeRecord(state.games?.[gameId]?.[selected]);
    return selected === DEFAULT_LEVEL ? mergeRecords(stored, officialRecord(gameId)) : stored;
  };

  const record = (gameId, result = {}) => {
    const level = current();
    if (!GAME_CONFIGS[gameId]) return { saved: false, level, record: null, rawImproved: false, normalizedImproved: false, officialUpdate: null };
    const state = read();
    const previous = recordFor(gameId, level, state);
    const score = Math.max(0, rounded(result.score));
    const maximum = Math.max(0, rounded(result.maximum));
    const normalized = clamp(rounded(result.normalized), 0, 1000);
    const rawImproved = !previous || score > previous.bestScore;
    const normalizedImproved = !previous || normalized > previous.bestNormalized;
    if (!state.games[gameId]) state.games[gameId] = {};
    state.games[gameId][level] = {
      bestScore: rawImproved ? score : previous.bestScore,
      bestMaximum: rawImproved ? maximum : previous.bestMaximum,
      bestNormalized: normalizedImproved ? normalized : previous.bestNormalized,
      plays: (previous?.plays || 0) + 1
    };
    const saved = write(state);
    const officialUpdate = level === DEFAULT_LEVEL
      ? progressSystem?.record(gameId, { score, maximum, normalized }) || null
      : null;
    return {
      saved: saved || Boolean(officialUpdate?.saved),
      level,
      record: recordFor(gameId, level, saved ? state : read()),
      rawImproved: (saved || officialUpdate?.saved) && rawImproved,
      normalizedImproved: (saved || officialUpdate?.saved) && normalizedImproved,
      officialUpdate
    };
  };

  const summarize = () => {
    const state = read();
    const games = {};
    Object.keys(GAME_CONFIGS).forEach((gameId) => {
      games[gameId] = {};
      LEVELS.forEach((level) => {
        const levelRecord = recordFor(gameId, level, state);
        if (levelRecord) games[gameId][level] = levelRecord;
      });
    });
    return { available, selected: current(), games };
  };

  const clearRecords = () => {
    if (!available) return false;
    const state = read();
    state.games = {};
    return write(state);
  };

  const withLevel = (href, level = current()) => {
    try {
      const target = new URL(href, window.location.href);
      const filename = target.pathname.split('/').pop();
      if (!GAME_FILES.has(filename)) return href;
      target.searchParams.set('difficulty', validLevel(level));
      target.searchParams.delete('run');
      return `${filename}${target.search}${target.hash}`;
    } catch (error) {
      return href;
    }
  };

  const withPlayTarget = (href, level = current()) => {
    try {
      const target = new URL(withLevel(href, level), window.location.href);
      const filename = target.pathname.split('/').pop();
      target.hash = PLAY_TARGET;
      return `${filename}${target.search}${target.hash}`;
    } catch (error) {
      return `${withLevel(href, level).split('#')[0]}#${PLAY_TARGET}`;
    }
  };

  const decorateLinks = (root = document) => {
    if (isRunMode()) return;
    root.querySelectorAll?.('a[href]').forEach((link) => {
      const updated = withLevel(link.getAttribute('href'));
      if (updated !== link.getAttribute('href')) link.setAttribute('href', updated);
    });
  };

  const createChoice = (level, name, fixed) => {
    const label = document.createElement('label');
    label.className = 'lab-difficulty-option';
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = name;
    input.value = level;
    input.checked = current() === level;
    input.disabled = fixed;
    const copy = document.createElement('span');
    const title = document.createElement('strong');
    const description = document.createElement('small');
    title.textContent = detail(level).label;
    description.textContent = detail(level).short;
    copy.append(title, description);
    label.append(input, copy);
    input.addEventListener('click', () => {
      if (fixed || !document.body?.dataset?.labGame || current() !== level) return;
      window.location.assign(withPlayTarget(window.location.href, level));
    });
    input.addEventListener('change', () => {
      if (!input.checked || fixed) return;
      const selected = set(level);
      document.body.dataset.labDifficultyLevel = selected;
      document.querySelectorAll('.lab-difficulty-description').forEach((node) => {
        node.textContent = descriptionFor(selected);
      });
      decorateLinks();
      document.dispatchEvent(new CustomEvent('impossiblelab:difficultychange', { detail: { level: selected } }));
      if (document.body?.dataset?.labGame) window.location.assign(withPlayTarget(window.location.href, selected));
    });
    return label;
  };

  const renderSelector = (target, index) => {
    const fixed = isRunMode();
    const section = document.createElement('section');
    section.className = `lab-difficulty${fixed ? ' is-fixed' : ''}`;
    section.setAttribute('aria-label', 'Challenge level');
    const intro = document.createElement('div');
    const eyebrow = document.createElement('p');
    const heading = document.createElement('h2');
    const description = document.createElement('p');
    description.className = 'lab-difficulty-description';
    eyebrow.className = 'eyebrow';
    eyebrow.textContent = fixed ? 'RUN RULES · FIXED LEVEL' : 'CHALLENGE LEVEL';
    heading.textContent = fixed ? 'Analyst mode' : 'Choose your mode';
    description.textContent = fixed
      ? 'Impossible Lab Run always uses Analyst rules so every four-stage score stays comparable.'
      : descriptionFor();
    intro.append(eyebrow, heading, description);

    const fieldset = document.createElement('fieldset');
    const legend = document.createElement('legend');
    legend.textContent = 'Select a difficulty level';
    fieldset.appendChild(legend);
    LEVELS.forEach((level) => fieldset.appendChild(createChoice(level, `lab-difficulty-${index}`, fixed)));
    section.append(intro, fieldset);
    target.replaceChildren(section);
  };

  const selected = current();
  if (document.body) document.body.dataset.labDifficultyLevel = selected;
  document.querySelectorAll?.('[data-lab-difficulty]').forEach(renderSelector);
  decorateLinks();

  window.ImpossibleLabDifficulty = Object.freeze({
    STORAGE_KEY,
    DEFAULT_LEVEL,
    LEVELS,
    LEVEL_DETAILS,
    GAME_CONFIGS,
    GAME_DESCRIPTIONS,
    available,
    current,
    detail,
    config,
    descriptionFor,
    set,
    read,
    summarize,
    recordFor,
    record,
    clearRecords,
    withLevel,
    withPlayTarget,
    decorateLinks,
    isRunMode
  });
})();
