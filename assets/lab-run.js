(() => {
  'use strict';

  const STORAGE_KEY = 'lca-impossible-lab-run-v1';
  const SCHEMA_VERSION = 1;
  const progressSystem = window.ImpossibleLabProgress;
  const GAME_IDS = progressSystem?.GAME_IDS || Object.freeze(['guess', 'crossword', 'alphabet', 'spin']);
  const SCORE_SCALE = progressSystem?.SCORE_SCALE || 1000;
  const RUN_MAX = GAME_IDS.length * SCORE_SCALE;
  const available = Boolean(progressSystem?.available);

  const rounded = (value) => Math.round(Number.isFinite(Number(value)) ? Number(value) : 0);
  const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
  const emptyRun = () => ({ version: SCHEMA_VERSION, status: 'idle', results: {} });

  const sanitizeResult = (result) => {
    if (!result || typeof result !== 'object') return null;
    return {
      score: Math.max(0, rounded(result.score)),
      maximum: Math.max(0, rounded(result.maximum)),
      normalized: clamp(rounded(result.normalized), 0, SCORE_SCALE)
    };
  };

  const sanitize = (candidate) => {
    if (!candidate || typeof candidate !== 'object' || candidate.version !== SCHEMA_VERSION) return emptyRun();
    const clean = { version: SCHEMA_VERSION, status: 'active', results: {} };
    let sequenceOpen = true;
    GAME_IDS.forEach((gameId) => {
      const result = sequenceOpen ? sanitizeResult(candidate.results?.[gameId]) : null;
      if (result) {
        clean.results[gameId] = result;
      } else {
        sequenceOpen = false;
      }
    });
    const completed = Object.keys(clean.results).length;
    if (!completed && candidate.status !== 'active') return emptyRun();
    clean.status = completed === GAME_IDS.length ? 'complete' : 'active';
    return clean;
  };

  const read = () => {
    if (!available) return emptyRun();
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      return stored ? sanitize(JSON.parse(stored)) : emptyRun();
    } catch (error) {
      return emptyRun();
    }
  };

  const write = (run) => {
    if (!available) return false;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(sanitize(run)));
      return true;
    } catch (error) {
      return false;
    }
  };

  const summarize = (run = read()) => {
    const clean = sanitize(run);
    const completed = Object.keys(clean.results).length;
    const total = GAME_IDS.reduce((sum, gameId) => sum + (clean.results[gameId]?.normalized || 0), 0);
    return {
      available,
      status: clean.status,
      active: clean.status === 'active',
      complete: clean.status === 'complete',
      completed,
      total,
      maximum: RUN_MAX,
      nextGameId: completed < GAME_IDS.length ? GAME_IDS[completed] : null,
      results: { ...clean.results }
    };
  };

  const start = () => {
    const run = { version: SCHEMA_VERSION, status: 'active', results: {} };
    return { saved: write(run), summary: summarize(run) };
  };

  const isRunMode = () => new URLSearchParams(window.location.search).get('run') === '1';

  const record = (gameId, result = {}) => {
    const run = read();
    const before = summarize(run);
    if (!available || !isRunMode() || !before.active || before.nextGameId !== gameId) {
      return { accepted: false, saved: false, summary: before };
    }

    run.results[gameId] = sanitizeResult(result);
    const saved = write(run);
    return { accepted: saved, saved, summary: summarize(saved ? run : read()) };
  };

  const clear = () => {
    if (!available) return false;
    try {
      window.localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      return false;
    }
  };

  const createGameBanner = () => {
    if (!document.body?.dataset?.labGame || !isRunMode()) return;
    const shell = document.querySelector('.lab-shell');
    if (!shell) return;

    const gameId = document.body.dataset.labGame;
    const summary = summarize();
    const validStage = summary.active && summary.nextGameId === gameId;
    const banner = document.createElement('aside');
    banner.className = `lab-run-banner${validStage ? '' : ' is-paused'}`;
    banner.setAttribute('aria-label', 'Impossible Lab Run status');

    const copy = document.createElement('div');
    const label = document.createElement('span');
    const message = document.createElement('strong');
    if (validStage) {
      label.textContent = `IMPOSSIBLE LAB RUN · STAGE ${summary.completed + 1} OF ${GAME_IDS.length}`;
      message.textContent = 'Complete this experiment once. Its normalized result will be locked into the current Run.';
    } else {
      label.textContent = 'IMPOSSIBLE LAB RUN · PAUSED';
      message.textContent = summary.available
        ? 'This is not the current stage. Return to the Run route to continue in order.'
        : 'Browser storage is unavailable, so a multi-page Run cannot be retained.';
    }
    copy.append(label, message);

    const link = document.createElement('a');
    link.href = 'impossible-lab-run.html';
    link.textContent = validStage ? 'View Run progress →' : 'Return to the Run →';
    banner.append(copy, link);

    const routeBar = shell.querySelector('.lab-route-bar');
    if (routeBar) routeBar.insertAdjacentElement('afterend', banner);
    else shell.prepend(banner);
  };

  window.ImpossibleLabRun = Object.freeze({
    STORAGE_KEY,
    GAME_IDS,
    SCORE_SCALE,
    RUN_MAX,
    available,
    read,
    summarize,
    start,
    record,
    clear,
    isRunMode
  });

  createGameBanner();
})();
