(() => {
  'use strict';

  const board = document.getElementById('relics-board');
  if (!board) return;

  const caseCount = document.getElementById('relics-case-count');
  const matchesValue = document.getElementById('relics-matches');
  const scoreValue = document.getElementById('relics-score');
  const attemptsValue = document.getElementById('relics-attempts');
  const streakValue = document.getElementById('relics-streak');
  const status = document.getElementById('relics-status');
  const startPanel = document.getElementById('relics-start-panel');
  const startButton = document.getElementById('relics-start');
  const hintButton = document.getElementById('relics-hint');
  const feedback = document.getElementById('relics-feedback');
  const finalPanel = document.getElementById('relics-final');
  const finalCopy = document.getElementById('relics-final-copy');
  const finalMatches = document.getElementById('relics-final-matches');
  const finalAttempts = document.getElementById('relics-final-attempts');
  const finalHints = document.getElementById('relics-final-hints');
  const finalTime = document.getElementById('relics-final-time');
  const review = document.getElementById('relics-review');
  const playAgain = document.getElementById('relics-again');
  const resultTarget = finalPanel?.querySelector('[data-lab-result-scorecard]');
  const difficultySystem = window.ImpossibleLabDifficulty;

  const POINTS_PER_MATCH = 100;
  const MISMATCH_COST = 10;
  const HINT_COST = 50;
  const fallbackConfig = Object.freeze({ pairs: 6, hints: 1 });
  const session = {
    pool: [],
    entries: [],
    cards: [],
    open: [],
    matched: new Set(),
    score: 0,
    penalty: 0,
    attempts: 0,
    streak: 0,
    bestStreak: 0,
    hintsRemaining: 0,
    hintsUsed: 0,
    locked: false,
    startedAt: 0,
    timer: null
  };

  const config = () => ({ ...fallbackConfig, ...(difficultySystem?.config('relics') || {}) });
  const shuffle = (values) => {
    const copy = [...values];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const target = Math.floor(Math.random() * (index + 1));
      [copy[index], copy[target]] = [copy[target], copy[index]];
    }
    return copy;
  };
  const formatTime = (milliseconds) => {
    const totalSeconds = Math.max(0, Math.floor(milliseconds / 1000));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };
  const elapsed = () => session.startedAt ? Date.now() - session.startedAt : 0;
  const setFeedback = (message, success = false) => {
    if (!feedback) return;
    feedback.textContent = message;
    feedback.classList.toggle('is-success', success);
  };
  const pairKey = (entry) => String(entry.episodeNumber);
  const updateScore = () => {
    session.score = Math.max(0, (session.matched.size * POINTS_PER_MATCH) - session.penalty);
  };

  const updateStats = () => {
    const pairs = config().pairs;
    if (matchesValue) matchesValue.textContent = `${session.matched.size} / ${pairs}`;
    if (scoreValue) scoreValue.textContent = session.score.toLocaleString('en-US');
    if (attemptsValue) attemptsValue.textContent = String(session.attempts);
    if (streakValue) streakValue.textContent = String(session.streak);
    if (hintButton) {
      hintButton.disabled = session.locked || session.hintsRemaining < 1 || session.matched.size >= pairs;
      hintButton.textContent = session.hintsRemaining === 1
        ? 'Reveal a pair · 1 left'
        : `Reveal a pair · ${session.hintsRemaining} left`;
    }
  };

  const cardIsOpen = (card) => session.open.includes(card.id) || session.matched.has(pairKey(card.entry));

  const createCard = (card, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'relic-card';
    button.dataset.cardId = card.id;
    button.classList.toggle('is-open', cardIsOpen(card));
    button.classList.toggle('is-matched', session.matched.has(pairKey(card.entry)));
    button.classList.toggle('is-hint', card.hint === true);
    button.disabled = session.locked || session.matched.has(pairKey(card.entry));
    button.setAttribute('aria-pressed', String(cardIsOpen(card)));
    button.setAttribute('aria-label', cardIsOpen(card)
      ? `${card.kind === 'subject' ? 'Subject' : 'Archive trace'} card: ${card.kind === 'subject' ? card.entry.episode.title : card.entry.clue}`
      : `Face-down relic card ${index + 1}`);

    const inner = document.createElement('span');
    inner.className = 'relic-card-inner';
    const front = document.createElement('span');
    front.className = 'relic-card-face relic-card-front';
    const frontLabel = document.createElement('small');
    frontLabel.textContent = 'ARCHIVE RELIC';
    const seal = document.createElement('strong');
    const sealMark = document.createElement('span');
    sealMark.textContent = String(index + 1).padStart(2, '0');
    seal.appendChild(sealMark);
    const frontAction = document.createElement('small');
    frontAction.textContent = 'OPEN';
    front.append(frontLabel, seal, frontAction);

    const back = document.createElement('span');
    back.className = 'relic-card-face relic-card-back';
    back.dataset.kind = card.kind;
    const kind = document.createElement('small');
    kind.textContent = card.kind === 'subject' ? 'SUBJECT' : 'ARCHIVE TRACE';
    if (card.kind === 'subject') {
      const title = document.createElement('strong');
      const season = document.createElement('em');
      title.textContent = card.entry.episode.title;
      season.textContent = card.entry.episode.seasonLabel;
      back.append(kind, title, season);
    } else {
      const clue = document.createElement('p');
      const source = document.createElement('em');
      clue.textContent = card.entry.clue;
      source.textContent = 'CURATED NARRATIVE CLUE';
      back.append(kind, clue, source);
    }
    inner.append(front, back);
    button.appendChild(inner);
    button.addEventListener('click', () => openCard(card.id));
    return button;
  };

  const renderBoard = () => {
    const fragment = document.createDocumentFragment();
    session.cards.forEach((card, index) => fragment.appendChild(createCard(card, index)));
    board.replaceChildren(fragment);
  };

  const closeSelection = () => {
    session.open = [];
    session.locked = false;
    session.cards.forEach((card) => { card.hint = false; });
    renderBoard();
    updateStats();
  };

  const finishGame = () => {
    window.clearInterval(session.timer);
    session.timer = null;
    session.locked = true;
    if (hintButton) hintButton.disabled = true;
    if (status) status.textContent = 'Vault complete. Every subject has been reunited with its archive trace.';
    setFeedback('All relics recovered. Your memory report is ready.', true);

    const pairs = config().pairs;
    const maximum = pairs * POINTS_PER_MATCH;
    const accuracy = session.attempts ? (pairs / session.attempts) * 100 : 0;
    if (finalCopy) finalCopy.textContent = `${pairs} narrative pairs recovered in ${session.attempts} attempts. Best streak: ${session.bestStreak}.`;
    if (finalMatches) finalMatches.textContent = `${pairs} / ${pairs}`;
    if (finalAttempts) finalAttempts.textContent = String(session.attempts);
    if (finalHints) finalHints.textContent = String(session.hintsUsed);
    if (finalTime) finalTime.textContent = formatTime(elapsed());

    const fragment = document.createDocumentFragment();
    [...session.entries].sort((left, right) => right.episodeNumber - left.episodeNumber).forEach((entry) => {
      const item = document.createElement('li');
      const copy = document.createElement('div');
      const title = document.createElement('h4');
      const clue = document.createElement('p');
      const link = document.createElement('a');
      title.textContent = entry.episode.title;
      clue.textContent = entry.clue;
      link.href = entry.episode.url;
      link.textContent = `Open Episode #${String(entry.episode.number).padStart(2, '0')} →`;
      copy.append(title, clue, link);
      item.appendChild(copy);
      fragment.appendChild(item);
    });
    review.replaceChildren(fragment);

    window.ImpossibleLabResults?.render(resultTarget, {
      title: 'Impossible Relics complete',
      score: session.score,
      maximum,
      completion: 100,
      accuracy,
      scoreLabel: 'Relic score'
    });
    finalPanel.hidden = false;
    finalPanel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  };

  function openCard(cardId) {
    if (session.locked || session.open.includes(cardId)) return;
    const card = session.cards.find((candidate) => candidate.id === cardId);
    if (!card || session.matched.has(pairKey(card.entry))) return;
    session.open.push(cardId);
    renderBoard();
    if (session.open.length < 2) {
      setFeedback(`${card.kind === 'subject' ? 'Subject' : 'Archive trace'} revealed. Choose its matching relic.`);
      return;
    }

    session.locked = true;
    session.attempts += 1;
    const [firstId, secondId] = session.open;
    const first = session.cards.find((candidate) => candidate.id === firstId);
    const second = session.cards.find((candidate) => candidate.id === secondId);
    const match = first.entry.episodeNumber === second.entry.episodeNumber && first.kind !== second.kind;
    if (match) {
      session.streak += 1;
      session.bestStreak = Math.max(session.bestStreak, session.streak);
      session.matched.add(pairKey(first.entry));
      updateScore();
      setFeedback(`Recovered: ${first.entry.episode.title}. +${POINTS_PER_MATCH} points.`, true);
      updateStats();
      window.setTimeout(() => {
        closeSelection();
        if (session.matched.size === config().pairs) finishGame();
      }, 520);
      return;
    }

    session.penalty += MISMATCH_COST;
    updateScore();
    session.streak = 0;
    setFeedback(`The relics do not match. −${MISMATCH_COST} points.`);
    updateStats();
    window.setTimeout(closeSelection, 1050);
  }

  const revealPair = () => {
    if (session.locked || session.hintsRemaining < 1) return;
    if (session.open.length) session.open = [];
    const candidates = session.entries.filter((entry) => !session.matched.has(pairKey(entry)));
    const entry = candidates[Math.floor(Math.random() * candidates.length)];
    if (!entry) return;
    const pairCards = session.cards.filter((card) => card.entry.episodeNumber === entry.episodeNumber);
    session.open = pairCards.map((card) => card.id);
    pairCards.forEach((card) => { card.hint = true; });
    session.hintsRemaining -= 1;
    session.hintsUsed += 1;
    session.penalty += HINT_COST;
    updateScore();
    session.streak = 0;
    session.locked = true;
    renderBoard();
    updateStats();
    setFeedback(`Archive assistance: remember ${entry.episode.title}. −${HINT_COST} points.`);
    window.setTimeout(closeSelection, 1500);
  };

  const startGame = () => {
    window.clearInterval(session.timer);
    const rules = config();
    session.entries = shuffle(session.pool).slice(0, Math.min(rules.pairs, session.pool.length));
    session.cards = shuffle(session.entries.flatMap((entry) => [
      { id: `subject-${entry.episodeNumber}`, kind: 'subject', entry, hint: false },
      { id: `trace-${entry.episodeNumber}`, kind: 'trace', entry, hint: false }
    ]));
    session.open = [];
    session.matched.clear();
    session.score = 0;
    session.penalty = 0;
    session.attempts = 0;
    session.streak = 0;
    session.bestStreak = 0;
    session.hintsRemaining = rules.hints;
    session.hintsUsed = 0;
    session.locked = false;
    session.startedAt = Date.now();
    session.timer = null;
    startPanel.hidden = true;
    finalPanel.hidden = true;
    if (status) status.textContent = `${rules.pairs} subject-and-trace pairs are sealed in the vault.`;
    setFeedback('Open any two cards to begin the recovery.');
    renderBoard();
    updateStats();
  };

  hintButton?.addEventListener('click', revealPair);
  startButton?.addEventListener('click', startGame);
  playAgain?.addEventListener('click', () => {
    startGame();
    document.getElementById('lab-game-area')?.focus({ preventScroll: true });
    document.getElementById('lab-game-area')?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  });

  Promise.all([
    fetch('episodes.json', { cache: 'no-store' }).then((response) => {
      if (!response.ok) throw new Error(`Episode registry request failed: ${response.status}`);
      return response.json();
    }),
    fetch('crossword.json', { cache: 'no-store' }).then((response) => {
      if (!response.ok) throw new Error(`Clue registry request failed: ${response.status}`);
      return response.json();
    })
  ]).then(([episodeData, clueData]) => {
    const episodes = new Map((episodeData.episodes || []).map((episode) => [Number(episode.number), episode]));
    session.pool = (clueData.entries || []).map((entry) => ({
      ...entry,
      episodeNumber: Number(entry.episodeNumber),
      episode: episodes.get(Number(entry.episodeNumber))
    })).filter((entry) => entry.episode && entry.clue);
    if (session.pool.length < 8) throw new Error('The relic pool does not contain enough matched archive records.');
    if (caseCount) caseCount.textContent = String(session.pool.length).padStart(2, '0');
    if (status) status.textContent = 'Archive traces ready. Select a level and open the vault.';
    startButton.disabled = false;
  }).catch(() => {
    if (status) status.textContent = 'The archive traces could not be loaded.';
    setFeedback('Impossible Relics is temporarily unavailable. Reload the page to try again.');
  });
})();
