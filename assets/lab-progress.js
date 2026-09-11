(() => {
  'use strict';

  const STORAGE_KEY = 'lca-impossible-lab-progress-v1';
  const SCHEMA_VERSION = 1;
  const SCORE_SCALE = 1000;
  const GAME_IDS = Object.freeze(['guess', 'crossword', 'alphabet', 'spin']);
  const LAB_MAX = GAME_IDS.length * SCORE_SCALE;

  const finiteNumber = (value) => Number.isFinite(Number(value)) ? Number(value) : 0;
  const rounded = (value) => Math.round(finiteNumber(value));
  const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
  const isGame = (gameId) => GAME_IDS.includes(gameId);

  const emptyProgress = () => ({ version: SCHEMA_VERSION, games: {} });

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

  const sanitizeRecord = (record) => {
    if (!record || typeof record !== 'object') return null;
    const bestScore = Math.max(0, rounded(record.bestScore));
    const bestMaximum = Math.max(0, rounded(record.bestMaximum));
    const bestNormalized = clamp(rounded(record.bestNormalized), 0, SCORE_SCALE);
    const plays = Math.max(1, rounded(record.plays));
    return { bestScore, bestMaximum, bestNormalized, plays };
  };

  const sanitize = (candidate) => {
    const clean = emptyProgress();
    if (!candidate || typeof candidate !== 'object' || candidate.version !== SCHEMA_VERSION) return clean;
    GAME_IDS.forEach((gameId) => {
      const record = sanitizeRecord(candidate.games?.[gameId]);
      if (record) clean.games[gameId] = record;
    });
    return clean;
  };

  const read = () => {
    if (!available) return emptyProgress();
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      return stored ? sanitize(JSON.parse(stored)) : emptyProgress();
    } catch (error) {
      return emptyProgress();
    }
  };

  const write = (progress) => {
    if (!available) return false;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(sanitize(progress)));
      return true;
    } catch (error) {
      return false;
    }
  };

  const summarize = (progress = read()) => {
    const clean = sanitize(progress);
    const games = {};
    GAME_IDS.forEach((gameId) => {
      const record = clean.games[gameId];
      if (record) games[gameId] = { ...record };
    });
    const completed = Object.keys(games).length;
    const total = GAME_IDS.reduce((sum, gameId) => sum + (games[gameId]?.bestNormalized || 0), 0);
    return { available, completed, total, maximum: LAB_MAX, games };
  };

  const record = (gameId, result = {}) => {
    if (!isGame(gameId)) return { saved: false, rawImproved: false, normalizedImproved: false, summary: summarize() };

    const score = Math.max(0, rounded(result.score));
    const maximum = Math.max(0, rounded(result.maximum));
    const normalized = clamp(rounded(result.normalized), 0, SCORE_SCALE);
    const progress = read();
    const previous = progress.games[gameId];
    const rawImproved = !previous || score > previous.bestScore;
    const normalizedImproved = !previous || normalized > previous.bestNormalized;

    progress.games[gameId] = {
      bestScore: rawImproved ? score : previous.bestScore,
      bestMaximum: rawImproved ? maximum : previous.bestMaximum,
      bestNormalized: normalizedImproved ? normalized : previous.bestNormalized,
      plays: (previous?.plays || 0) + 1
    };

    const saved = write(progress);
    return {
      saved,
      rawImproved: saved && rawImproved,
      normalizedImproved: saved && normalizedImproved,
      summary: summarize(saved ? progress : emptyProgress())
    };
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

  window.ImpossibleLabProgress = Object.freeze({
    STORAGE_KEY,
    SCORE_SCALE,
    LAB_MAX,
    GAME_IDS,
    available,
    read,
    summarize,
    record,
    clear
  });
})();
