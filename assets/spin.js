(() => {
  'use strict';

  const ROUNDS_PER_SESSION = 5;
  const MAX_SPINS = 15;
  const SOLVE_ATTEMPTS = 3;
  const VOWEL_COST = 150;
  const HINT_COST = 300;
  const WRONG_SOLUTION_COST = 200;
  const BASE_SOLVE_BONUS = 500;
  const resultSystem = window.ImpossibleLabResults;
  const VOWELS = new Set(['A', 'E', 'I', 'O', 'U']);
  const WHEEL_SECTORS = [
    { label: '50', type: 'points', value: 50 },
    { label: '100', type: 'points', value: 100 },
    { label: '150', type: 'points', value: 150 },
    { label: '200', type: 'points', value: 200 },
    { label: '250', type: 'points', value: 250 },
    { label: '50', type: 'points', value: 50 },
    { label: '100', type: 'points', value: 100 },
    { label: '150', type: 'points', value: 150 },
    { label: '200', type: 'points', value: 200 },
    { label: '250', type: 'points', value: 250 },
    { label: '×2', type: 'double', value: 400 },
    { label: 'FREE\nVOWEL', type: 'free-vowel', value: 0 },
    { label: 'MISS', type: 'miss', value: 0 },
    { label: 'RESET', type: 'reset', value: 0 }
  ];

  const elements = {
    count: document.getElementById('spin-case-count'),
    round: document.getElementById('spin-round'),
    score: document.getElementById('spin-score'),
    spins: document.getElementById('spin-spins'),
    attempts: document.getElementById('spin-attempts'),
    status: document.getElementById('spin-status'),
    wheel: document.getElementById('spin-wheel'),
    wheelResult: document.getElementById('spin-wheel-result'),
    wheelState: document.getElementById('spin-wheel-state'),
    start: document.getElementById('spin-start'),
    spin: document.getElementById('spin-action'),
    vowel: document.getElementById('spin-vowel'),
    hint: document.getElementById('spin-hint'),
    category: document.getElementById('spin-category'),
    subjectSignal: document.getElementById('spin-subject-signal'),
    puzzle: document.getElementById('spin-puzzle'),
    keyboard: document.getElementById('spin-keyboard'),
    solveForm: document.getElementById('spin-solve-form'),
    solveInput: document.getElementById('spin-solve-input'),
    solveSubmit: document.getElementById('spin-solve-submit'),
    reveal: document.getElementById('spin-reveal'),
    feedback: document.getElementById('spin-feedback'),
    result: document.getElementById('spin-result'),
    resultScorecard: document.querySelector('[data-lab-result-scorecard]'),
    resultTitle: document.getElementById('spin-result-title'),
    resultCopy: document.getElementById('spin-result-copy'),
    resultRoundScore: document.getElementById('spin-result-round-score'),
    resultSessionScore: document.getElementById('spin-result-session-score'),
    resultBonus: document.getElementById('spin-result-bonus'),
    resultLength: document.getElementById('spin-result-length'),
    resultMeta: document.getElementById('spin-result-meta'),
    resultSubject: document.getElementById('spin-result-subject'),
    resultDescription: document.getElementById('spin-result-description'),
    resultImpact: document.getElementById('spin-result-impact'),
    resultHotspot: document.getElementById('spin-result-hotspot'),
    resultLink: document.getElementById('spin-result-link'),
    next: document.getElementById('spin-next')
  };

  const state = {
    pool: [],
    entry: null,
    usedEpisodes: new Set(),
    guessedLetters: new Set(),
    roundNumber: 1,
    sessionScore: 0,
    roundScore: 0,
    spinsRemaining: MAX_SPINS,
    solveAttempts: SOLVE_ATTEMPTS,
    pendingMode: '',
    pendingValue: 0,
    hintUsed: false,
    running: false,
    spinning: false,
    revealAll: false,
    rotation: 0,
    letterAttempts: 0,
    correctLetterAttempts: 0,
    phraseAttempts: 0,
    correctPhraseAttempts: 0
  };

  const setText = (element, value) => {
    if (element) element.textContent = String(value);
  };

  const normalize = (value) => String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '');

  const normalizedCharacter = (value) => normalize(value).slice(0, 1);
  const isLetter = (value) => /^[A-Z]$/.test(normalizedCharacter(value));
  const letterCount = (phrase) => [...String(phrase || '')].filter(isLetter).length;

  const setFeedback = (message, type = '') => {
    setText(elements.feedback, message);
    elements.feedback.className = `spin-feedback${type ? ` is-${type}` : ''}`;
  };

  const difficultyMultiplier = () => {
    const length = letterCount(state.entry?.phrase);
    if (length <= 45) return 1;
    if (length <= 70) return 1.5;
    return 2;
  };

  const maximumRoundScore = () => {
    const consonantCounts = new Map();
    for (const character of String(state.entry?.phrase || '')) {
      const letter = normalizedCharacter(character);
      if (/^[A-Z]$/.test(letter) && !VOWELS.has(letter)) {
        consonantCounts.set(letter, (consonantCounts.get(letter) || 0) + 1);
      }
    }
    const bestOccurrences = [...consonantCounts.values()]
      .sort((left, right) => right - left)
      .slice(0, MAX_SPINS)
      .reduce((total, count) => total + count, 0);
    const solveBonus = Math.round(BASE_SOLVE_BONUS * difficultyMultiplier())
      + Math.max(0, letterCount(state.entry?.phrase) - bestOccurrences) * 25;
    return bestOccurrences * 400 + solveBonus;
  };

  const hiddenLetterCount = () => [...state.entry.phrase].filter((character) => {
    const letter = normalizedCharacter(character);
    return /^[A-Z]$/.test(letter) && !state.guessedLetters.has(letter);
  }).length;

  const renderScoreboard = () => {
    setText(elements.round, `${state.roundNumber} / ${ROUNDS_PER_SESSION}`);
    setText(elements.score, state.roundScore);
    setText(elements.spins, state.spinsRemaining);
    setText(elements.attempts, state.solveAttempts);
  };

  const renderPuzzle = () => {
    const fragment = document.createDocumentFragment();
    const words = String(state.entry?.phrase || '').split(/\s+/).filter(Boolean);
    words.forEach((word) => {
      const group = document.createElement('span');
      group.className = 'spin-word';
      [...word].forEach((character) => {
        const tile = document.createElement('span');
        const letter = normalizedCharacter(character);
        tile.className = 'spin-character';
        if (!isLetter(character)) {
          tile.classList.add('is-mark');
          tile.textContent = character;
        } else if (state.revealAll || state.guessedLetters.has(letter)) {
          tile.textContent = character;
        } else {
          tile.classList.add('is-hidden');
          tile.textContent = '\u00a0';
        }
        group.appendChild(tile);
      });
      fragment.appendChild(group);
    });
    elements.puzzle.replaceChildren(fragment);
    elements.puzzle.classList.toggle('is-revealed', state.revealAll);
    const revealed = state.revealAll ? 'complete phrase revealed' : `${hiddenLetterCount()} letters still hidden`;
    elements.puzzle.setAttribute('aria-label', `Hidden phrase board: ${revealed}`);
  };

  const availableVowels = () => [...VOWELS].filter((letter) => !state.guessedLetters.has(letter));

  const controlsLocked = () => !state.running || state.spinning || Boolean(state.pendingMode);

  const renderControls = () => {
    const locked = controlsLocked();
    elements.spin.disabled = locked || state.spinsRemaining <= 0;
    elements.vowel.disabled = locked || state.roundScore < VOWEL_COST || !availableVowels().length;
    elements.hint.disabled = locked || state.hintUsed || state.roundScore < HINT_COST;
    elements.solveInput.disabled = !state.running || state.spinning;
    elements.solveSubmit.disabled = !state.running || state.spinning || state.solveAttempts <= 0;
    elements.reveal.disabled = !state.running || state.spinning;

    for (const button of elements.keyboard.querySelectorAll('.spin-key')) {
      const letter = button.dataset.letter;
      const vowel = VOWELS.has(letter);
      const allowed = state.pendingMode === 'vowel' ? vowel : state.pendingMode === 'consonant' ? !vowel : false;
      button.disabled = !state.running || state.spinning || state.guessedLetters.has(letter) || !allowed;
      button.classList.toggle('is-used', state.guessedLetters.has(letter));
    }
  };

  const renderKeyboard = () => {
    const fragment = document.createDocumentFragment();
    for (const letter of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `spin-key${VOWELS.has(letter) ? ' is-vowel' : ''}`;
      button.dataset.letter = letter;
      button.textContent = letter;
      button.setAttribute('aria-label', `Choose letter ${letter}`);
      button.addEventListener('click', () => chooseLetter(letter));
      fragment.appendChild(button);
    }
    elements.keyboard.replaceChildren(fragment);
    renderControls();
  };

  const renderWheel = () => {
    const labels = document.createDocumentFragment();
    const sectorAngle = 360 / WHEEL_SECTORS.length;
    const colors = ['#153844', '#5f4930', '#12303b', '#745637'];
    const stops = WHEEL_SECTORS.map((sector, index) => {
      const start = index * sectorAngle;
      const end = (index + 1) * sectorAngle;
      return `${colors[index % colors.length]} ${start}deg ${end}deg`;
    });
    elements.wheel.style.background = `conic-gradient(from -90deg, ${stops.join(',')})`;
    WHEEL_SECTORS.forEach((sector, index) => {
      const label = document.createElement('span');
      const angle = index * sectorAngle + sectorAngle / 2;
      label.className = 'spin-sector-label';
      label.style.setProperty('--sector-angle', `${angle}deg`);
      label.style.setProperty('--sector-counter-angle', `${-angle}deg`);
      label.textContent = sector.label.replace('\n', ' ');
      labels.appendChild(label);
    });
    elements.wheel.replaceChildren(labels);
  };

  const selectEntry = () => {
    let available = state.pool.filter((entry) => !state.usedEpisodes.has(entry.episode.number));
    if (!available.length) {
      state.usedEpisodes.clear();
      available = [...state.pool];
    }
    const selected = available[Math.floor(Math.random() * available.length)];
    state.usedEpisodes.add(selected.episode.number);
    return selected;
  };

  const prepareRound = () => {
    state.entry = selectEntry();
    state.guessedLetters = new Set();
    state.roundScore = 0;
    state.spinsRemaining = MAX_SPINS;
    state.solveAttempts = SOLVE_ATTEMPTS;
    state.pendingMode = '';
    state.pendingValue = 0;
    state.hintUsed = false;
    state.running = false;
    state.spinning = false;
    state.revealAll = false;
    state.letterAttempts = 0;
    state.correctLetterAttempts = 0;
    state.phraseAttempts = 0;
    state.correctPhraseAttempts = 0;
    elements.result.hidden = true;
    elements.start.hidden = false;
    elements.spin.hidden = true;
    elements.start.disabled = false;
    elements.start.textContent = `Start round ${state.roundNumber}`;
    elements.solveInput.value = '';
    setText(elements.category, state.entry.episode.seasonLabel);
    setText(elements.subjectSignal, 'CLASSIFIED');
    setText(elements.wheelResult, '—');
    setText(elements.wheelState, 'STANDBY');
    setText(elements.status, `Round ${state.roundNumber} phrase ready. The subject remains classified.`);
    setFeedback('Start the round to activate the wheel and letter controls.');
    renderPuzzle();
    renderScoreboard();
    renderControls();
  };

  const startRound = () => {
    if (!state.entry || state.running) return;
    state.running = true;
    elements.start.hidden = true;
    elements.spin.hidden = false;
    setText(elements.wheelState, 'READY');
    setText(elements.status, 'Spin for a value, then select an available letter.');
    setFeedback('The round is live. Consonants require a spin; vowels cost 150 points.');
    renderControls();
    elements.spin.focus({ preventScroll: true });
  };

  const settleWheel = (sector) => {
    state.spinning = false;
    setText(elements.wheelResult, sector.label.replace('\n', ' '));
    if (sector.type === 'points' || sector.type === 'double') {
      state.pendingMode = 'consonant';
      state.pendingValue = sector.value;
      setText(elements.wheelState, 'CHOOSE');
      setFeedback(`${sector.label} points per occurrence. Choose one consonant.`);
    } else if (sector.type === 'free-vowel') {
      state.pendingMode = 'vowel';
      state.pendingValue = 0;
      setText(elements.wheelState, 'VOWEL');
      setFeedback('Free vowel. Choose one available vowel.');
    } else if (sector.type === 'miss') {
      setText(elements.wheelState, 'MISSED');
      setFeedback('Miss a turn. No letter may be selected from this spin.', 'wrong');
    } else {
      state.roundScore = 0;
      setText(elements.wheelState, 'RESET');
      setFeedback('Round score reset to zero. Previous session points remain safe.', 'wrong');
    }
    elements.wheel.setAttribute('aria-label', `Scoring wheel result: ${sector.label.replace('\n', ' ')}`);
    renderScoreboard();
    renderControls();
  };

  const spinWheel = () => {
    if (controlsLocked() || state.spinsRemaining <= 0) return;
    state.spinning = true;
    state.spinsRemaining -= 1;
    const index = Math.floor(Math.random() * WHEEL_SECTORS.length);
    const sectorAngle = 360 / WHEEL_SECTORS.length;
    const current = ((state.rotation % 360) + 360) % 360;
    const target = (360 - ((index + 0.5) * sectorAngle)) % 360;
    const delta = (target - current + 360) % 360;
    state.rotation += 1440 + delta;
    elements.wheel.style.setProperty('--spin-rotation', `${state.rotation}deg`);
    setText(elements.wheelResult, '…');
    setText(elements.wheelState, 'SPINNING');
    setText(elements.status, `${state.spinsRemaining} spins remain after this result.`);
    setFeedback('The wheel is selecting the next action.');
    renderScoreboard();
    renderControls();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.setTimeout(() => settleWheel(WHEEL_SECTORS[index]), reducedMotion ? 120 : 3250);
  };

  function chooseLetter(letter) {
    if (!state.running || state.spinning || !state.pendingMode || state.guessedLetters.has(letter)) return;
    const vowel = VOWELS.has(letter);
    if ((state.pendingMode === 'vowel') !== vowel) return;
    state.guessedLetters.add(letter);
    const occurrences = [...state.entry.phrase].filter((character) => normalizedCharacter(character) === letter).length;
    state.letterAttempts += 1;
    if (occurrences) state.correctLetterAttempts += 1;
    if (occurrences && state.pendingMode === 'consonant') {
      const gained = occurrences * state.pendingValue;
      state.roundScore += gained;
      setFeedback(`${letter} appears ${occurrences} ${occurrences === 1 ? 'time' : 'times'} · +${gained} points.`, 'correct');
    } else if (occurrences) {
      setFeedback(`${letter} appears ${occurrences} ${occurrences === 1 ? 'time' : 'times'}.`, 'correct');
    } else {
      setFeedback(`${letter} does not appear in the phrase.`, 'wrong');
    }
    state.pendingMode = '';
    state.pendingValue = 0;
    setText(elements.wheelState, 'READY');
    renderPuzzle();
    renderScoreboard();
    renderControls();
    if (hiddenLetterCount() === 0) {
      finishRound(true);
    } else if (state.spinsRemaining === 0) {
      setText(elements.status, 'No spins remain. Solve the phrase, buy an available vowel or reveal it.');
    }
  }

  const buyVowel = () => {
    if (controlsLocked() || state.roundScore < VOWEL_COST || !availableVowels().length) return;
    state.roundScore -= VOWEL_COST;
    state.pendingMode = 'vowel';
    state.pendingValue = 0;
    setText(elements.wheelResult, 'VOWEL');
    setText(elements.wheelState, 'PURCHASED');
    setFeedback('150 points deducted. Choose one available vowel.');
    renderScoreboard();
    renderControls();
  };

  const revealSubjectHint = () => {
    if (controlsLocked() || state.hintUsed || state.roundScore < HINT_COST) return;
    state.roundScore -= HINT_COST;
    state.hintUsed = true;
    setText(elements.subjectSignal, state.entry.episode.title);
    setFeedback('Subject signal unlocked for 300 points.');
    renderScoreboard();
    renderControls();
  };

  const finishRound = (solved) => {
    if (!state.running) return;
    const hiddenBeforeSolve = hiddenLetterCount();
    let solveBonus = 0;
    if (solved) {
      solveBonus = Math.round(BASE_SOLVE_BONUS * difficultyMultiplier()) + hiddenBeforeSolve * 25;
      state.roundScore += solveBonus;
    }
    const finalRoundScore = state.roundScore;
    state.sessionScore += finalRoundScore;
    state.roundScore = 0;
    state.running = false;
    state.spinning = false;
    state.pendingMode = '';
    state.revealAll = true;
    renderPuzzle();
    setText(elements.subjectSignal, state.entry.episode.title);
    setText(elements.wheelState, 'COMPLETE');
    setText(elements.status, solved ? 'Phrase solved. Life-cycle record unlocked.' : 'Phrase revealed. Life-cycle record unlocked.');
    setText(elements.resultTitle, solved ? 'Phrase solved' : 'Phrase revealed');
    setText(elements.resultCopy, solved
      ? 'The hidden narrative record has been reconstructed. Continue into the subject and its life-cycle result.'
      : 'The round ended without a solution. Review the phrase, subject and life-cycle result.');
    setText(elements.resultRoundScore, finalRoundScore);
    setText(elements.resultSessionScore, state.sessionScore);
    setText(elements.resultBonus, solveBonus);
    setText(elements.resultLength, `${letterCount(state.entry.phrase)} letters`);
    setText(elements.resultMeta, `EPISODE #${state.entry.episode.number} · ${state.entry.episode.seasonLabel}`);
    setText(elements.resultSubject, state.entry.episode.title);
    setText(elements.resultDescription, state.entry.episode.subjectDescription);
    setText(elements.resultImpact, state.entry.episode.result);
    setText(elements.resultHotspot, state.entry.episode.hotspot);
    elements.resultLink.href = state.entry.episode.url;
    elements.resultLink.setAttribute('aria-label', `Open the complete LCA for ${state.entry.episode.title}`);
    setText(elements.next, 'Play again →');
    const totalAttempts = state.letterAttempts + state.phraseAttempts;
    const correctAttempts = state.correctLetterAttempts + state.correctPhraseAttempts;
    const totalLetters = letterCount(state.entry.phrase);
    resultSystem?.render(elements.resultScorecard, {
      title: solved ? 'Phrase solved' : 'Phrase revealed',
      scoreLabel: 'Round score',
      score: finalRoundScore,
      maximum: maximumRoundScore(),
      completion: solved ? 100 : (totalLetters ? ((totalLetters - hiddenBeforeSolve) / totalLetters) * 100 : 0),
      accuracy: totalAttempts ? (correctAttempts / totalAttempts) * 100 : 0
    });
    elements.result.hidden = false;
    setFeedback(solved ? `Correct · +${solveBonus} solve bonus.` : 'No solve bonus awarded.', solved ? 'correct' : 'wrong');
    renderScoreboard();
    renderControls();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    elements.result.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
  };

  const solvePhrase = (event) => {
    event.preventDefault();
    if (!state.running || state.spinning || state.solveAttempts <= 0) return;
    const attempt = elements.solveInput.value.trim();
    if (!attempt) {
      setFeedback('Enter the complete phrase before submitting a solution.', 'wrong');
      return;
    }
    state.phraseAttempts += 1;
    if (normalize(attempt) === normalize(state.entry.phrase)) {
      state.correctPhraseAttempts += 1;
      finishRound(true);
      return;
    }
    state.solveAttempts -= 1;
    state.roundScore = Math.max(0, state.roundScore - WRONG_SOLUTION_COST);
    elements.solveInput.value = '';
    setFeedback(`Incorrect solution · −${WRONG_SOLUTION_COST} points.`, 'wrong');
    renderScoreboard();
    renderControls();
    if (state.solveAttempts === 0) finishRound(false);
  };

  const nextRound = () => {
    if (state.roundNumber >= ROUNDS_PER_SESSION) {
      state.roundNumber = 1;
      state.sessionScore = 0;
      state.usedEpisodes.clear();
    } else {
      state.roundNumber += 1;
    }
    prepareRound();
    elements.start.focus({ preventScroll: true });
  };

  elements.start.addEventListener('click', startRound);
  elements.spin.addEventListener('click', spinWheel);
  elements.vowel.addEventListener('click', buyVowel);
  elements.hint.addEventListener('click', revealSubjectHint);
  elements.solveForm.addEventListener('submit', solvePhrase);
  elements.reveal.addEventListener('click', () => finishRound(false));
  elements.next.addEventListener('click', nextRound);

  renderWheel();
  renderKeyboard();

  Promise.all([
    fetch('episodes.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    }),
    fetch('crossword.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Narrative registry returned ${response.status}`);
      return response.json();
    })
  ]).then(([episodeRegistry, narrativeRegistry]) => {
    const episodes = new Map((episodeRegistry.episodes || []).map((episode) => [episode.number, episode]));
    state.pool = (narrativeRegistry.entries || []).map((entry) => {
      const episode = episodes.get(entry.episodeNumber);
      const phrase = String(entry.clue || '').trim();
      if (!episode || letterCount(phrase) < 35 || normalize(phrase).includes(normalize(entry.answer))) return null;
      return { phrase, episode };
    }).filter(Boolean);
    if (state.pool.length < ROUNDS_PER_SESSION) throw new Error('The narrative registry does not provide enough hidden phrases');
    setText(elements.count, state.pool.length);
    prepareRound();
  }).catch((error) => {
    console.warn('Spin the Impossible unavailable:', error);
    setText(elements.status, 'The episode registries could not be loaded.');
    setFeedback('Unable to assemble the hidden phrase. The complete archive remains available.', 'wrong');
    elements.start.disabled = true;
  });
})();
