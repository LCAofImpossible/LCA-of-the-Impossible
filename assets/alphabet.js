(() => {
  'use strict';

  const ROUND_SECONDS = 90;
  const MAX_LETTERS = 18;
  const BASE_POINTS = 100;
  const STREAK_STEP = 25;
  const STREAK_CAP = 100;

  const elements = {
    count: document.getElementById('alphabet-case-count'),
    time: document.getElementById('alphabet-time'),
    score: document.getElementById('alphabet-score'),
    progress: document.getElementById('alphabet-progress'),
    streak: document.getElementById('alphabet-streak'),
    status: document.getElementById('alphabet-status'),
    wheel: document.getElementById('alphabet-wheel'),
    currentLetter: document.getElementById('alphabet-current-letter'),
    wheelState: document.getElementById('alphabet-wheel-state'),
    start: document.getElementById('alphabet-start'),
    prefix: document.getElementById('alphabet-prefix'),
    clue: document.getElementById('alphabet-clue'),
    form: document.getElementById('alphabet-answer-form'),
    input: document.getElementById('alphabet-answer-input'),
    submit: document.getElementById('alphabet-submit'),
    pass: document.getElementById('alphabet-pass'),
    feedback: document.getElementById('alphabet-feedback'),
    result: document.getElementById('alphabet-result'),
    resultCopy: document.getElementById('alphabet-result-copy'),
    resultScore: document.getElementById('alphabet-result-score'),
    resultCorrect: document.getElementById('alphabet-result-correct'),
    resultMissed: document.getElementById('alphabet-result-missed'),
    resultStreak: document.getElementById('alphabet-result-streak'),
    review: document.getElementById('alphabet-review'),
    newRound: document.getElementById('alphabet-new-round')
  };

  const state = {
    pool: [],
    groups: new Map(),
    usedByLetter: new Map(),
    entries: [],
    currentIndex: -1,
    running: false,
    score: 0,
    streak: 0,
    bestStreak: 0,
    remainingSeconds: ROUND_SECONDS,
    deadline: 0,
    timer: null
  };

  const setText = (element, value) => {
    if (element) element.textContent = String(value);
  };

  const normalize = (value) => String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '');

  const normalizeWithoutArticle = (value) => normalize(String(value || '').trim().replace(/^(?:the|a|an)\s+/i, ''));

  const titleWords = (title) => String(title || '').match(/[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?/g) || [];

  const deriveAnswerLabel = (answer, title) => {
    const words = titleWords(title);
    for (let length = 1; length <= words.length; length += 1) {
      for (let start = 0; start + length <= words.length; start += 1) {
        const candidate = words.slice(start, start + length).join(' ');
        if (normalize(candidate) === answer) return candidate;
      }
    }
    return String(title || answer).replace(/^(?:The|A|An)\s+/i, '');
  };

  const shuffled = (items) => {
    const copy = [...items];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const swap = Math.floor(Math.random() * (index + 1));
      [copy[index], copy[swap]] = [copy[swap], copy[index]];
    }
    return copy;
  };

  const formatTime = (seconds) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;

  const setFeedback = (message, type = '') => {
    setText(elements.feedback, message);
    elements.feedback.className = `alphabet-feedback${type ? ` is-${type}` : ''}`;
  };

  const correctCount = () => state.entries.filter((entry) => entry.status === 'correct').length;

  const updateScoreboard = () => {
    setText(elements.time, formatTime(state.remainingSeconds));
    setText(elements.score, state.score);
    setText(elements.progress, `${correctCount()} / ${state.entries.length || '—'}`);
    setText(elements.streak, state.streak);
    const timeBox = elements.time?.closest('.alphabet-time');
    if (timeBox) timeBox.classList.toggle('is-low', state.running && state.remainingSeconds <= 15);
  };

  const wheelItems = () => [...elements.wheel.querySelectorAll('.alphabet-letter')];

  const updateWheel = () => {
    for (const item of wheelItems()) {
      const index = Number(item.dataset.index);
      const entry = state.entries[index];
      item.className = 'alphabet-letter';
      if (entry?.status && entry.status !== 'pending') item.classList.add(`is-${entry.status}`);
      if (index === state.currentIndex && state.running) item.classList.add('is-active');
      const status = index === state.currentIndex && state.running ? 'current' : (entry?.status || 'pending');
      item.setAttribute('aria-label', `${entry?.letter || ''}: ${status}`);
    }
  };

  const renderWheel = () => {
    wheelItems().forEach((item) => item.remove());
    const total = state.entries.length;
    const fragment = document.createDocumentFragment();
    state.entries.forEach((entry, index) => {
      const letter = document.createElement('span');
      const angle = (360 / total) * index;
      letter.className = 'alphabet-letter';
      letter.dataset.index = String(index);
      letter.style.setProperty('--angle', `${angle}deg`);
      letter.style.setProperty('--negative-angle', `${-angle}deg`);
      letter.setAttribute('role', 'listitem');
      letter.setAttribute('aria-label', `${entry.letter}: pending`);
      letter.textContent = entry.letter;
      fragment.appendChild(letter);
    });
    elements.wheel.appendChild(fragment);
    elements.wheel.style.setProperty('--alphabet-count', total);
    updateWheel();
  };

  const chooseEntry = (letter, choices) => {
    let used = state.usedByLetter.get(letter) || new Set();
    let available = choices.filter((entry) => !used.has(entry.episode.number));
    if (!available.length) {
      used = new Set();
      available = choices;
    }
    const selected = shuffled(available)[0];
    used.add(selected.episode.number);
    state.usedByLetter.set(letter, used);
    return { ...selected, letter, status: 'pending' };
  };

  const prepareRound = () => {
    window.clearInterval(state.timer);
    const activeLetters = shuffled([...state.groups.keys()]).slice(0, MAX_LETTERS).sort();
    state.entries = activeLetters.map((letter) => chooseEntry(letter, state.groups.get(letter)));
    state.currentIndex = -1;
    state.running = false;
    state.score = 0;
    state.streak = 0;
    state.bestStreak = 0;
    state.remainingSeconds = ROUND_SECONDS;
    elements.result.hidden = true;
    elements.start.hidden = false;
    elements.start.disabled = false;
    elements.input.disabled = true;
    elements.submit.disabled = true;
    elements.pass.disabled = true;
    elements.input.value = '';
    setText(elements.currentLetter, '—');
    setText(elements.wheelState, 'STANDBY');
    setText(elements.prefix, 'READY SIGNAL');
    setText(elements.clue, 'Start the round when you are ready. The first definition will appear here.');
    setText(elements.status, `${state.entries.length}-letter circuit ready from ${state.pool.length} published cases.`);
    setFeedback('One case has been selected for each active initial in this circuit.');
    renderWheel();
    updateScoreboard();
  };

  const nextUnresolvedIndex = (afterIndex) => {
    for (let offset = 1; offset <= state.entries.length; offset += 1) {
      const index = (afterIndex + offset + state.entries.length) % state.entries.length;
      if (['pending', 'passed'].includes(state.entries[index].status)) return index;
    }
    return -1;
  };

  const activateEntry = (index) => {
    state.currentIndex = index;
    const entry = state.entries[index];
    setText(elements.currentLetter, entry.letter);
    setText(elements.wheelState, entry.status === 'passed' ? 'RETURNED' : 'ACTIVE');
    setText(elements.prefix, `BEGINS WITH ${entry.letter}`);
    setText(elements.clue, entry.clue);
    setText(elements.status, `Letter ${index + 1} of ${state.entries.length}. Pass to return later.`);
    elements.input.value = '';
    elements.input.disabled = false;
    elements.submit.disabled = false;
    elements.pass.disabled = false;
    updateWheel();
    elements.input.focus({ preventScroll: true });
  };

  const buildReview = () => {
    const fragment = document.createDocumentFragment();
    for (const entry of state.entries) {
      const item = document.createElement('li');
      item.className = `alphabet-review-item is-${entry.status}`;

      const letter = document.createElement('span');
      letter.className = 'alphabet-review-letter';
      letter.textContent = entry.letter;

      const copy = document.createElement('div');
      const title = document.createElement('strong');
      title.textContent = entry.answerLabel;
      const meta = document.createElement('small');
      meta.textContent = `Episode #${entry.episode.number} · ${entry.episode.seasonLabel}`;
      copy.append(title, meta);

      const outcome = document.createElement('span');
      outcome.className = 'alphabet-review-outcome';
      outcome.textContent = entry.status === 'correct' ? 'CORRECT' : 'MISSED';

      const link = document.createElement('a');
      link.href = entry.episode.url;
      link.textContent = 'Open LCA →';
      link.setAttribute('aria-label', `Open the LCA record for ${entry.episode.title}`);

      item.append(letter, copy, outcome, link);
      fragment.appendChild(item);
    }
    elements.review.replaceChildren(fragment);
  };

  const finishRound = (reason) => {
    if (!state.running) return;
    state.running = false;
    window.clearInterval(state.timer);
    state.timer = null;
    state.entries.forEach((entry) => {
      if (entry.status === 'pending' || entry.status === 'passed') entry.status = 'missed';
    });
    state.currentIndex = -1;
    elements.input.disabled = true;
    elements.submit.disabled = true;
    elements.pass.disabled = true;
    setText(elements.currentLetter, '—');
    setText(elements.wheelState, 'COMPLETE');
    setText(elements.prefix, 'CIRCUIT CLOSED');
    setText(elements.clue, 'The complete answer review is now available below.');
    setText(elements.status, reason === 'time' ? 'Time expired. Circuit complete.' : 'Every letter has been resolved.');
    setFeedback(`Final score: ${state.score} points.`, correctCount() ? 'correct' : 'wrong');
    setText(elements.resultCopy, reason === 'time'
      ? 'Time expired. Review every subject and continue into its complete life-cycle record.'
      : 'Circuit completed before time expired. Review every subject and its complete life-cycle record.');
    setText(elements.resultScore, state.score);
    setText(elements.resultCorrect, correctCount());
    setText(elements.resultMissed, state.entries.length - correctCount());
    setText(elements.resultStreak, state.bestStreak);
    buildReview();
    elements.result.hidden = false;
    updateWheel();
    updateScoreboard();
  };

  const moveNext = () => {
    if (!state.running) return;
    const next = nextUnresolvedIndex(state.currentIndex);
    if (next === -1) {
      finishRound('complete');
      return;
    }
    activateEntry(next);
  };

  const submitAnswer = (event) => {
    event.preventDefault();
    if (!state.running || state.currentIndex < 0) return;
    const value = elements.input.value.trim();
    if (!value) {
      setFeedback('Enter an answer or pass to return to this letter later.', 'wrong');
      return;
    }
    const entry = state.entries[state.currentIndex];
    if (!['pending', 'passed'].includes(entry.status)) return;
    elements.input.disabled = true;
    elements.submit.disabled = true;
    elements.pass.disabled = true;
    const attempt = normalizeWithoutArticle(value);
    const accepted = new Set([
      normalize(entry.answer),
      normalizeWithoutArticle(entry.answerLabel),
      normalizeWithoutArticle(entry.episode.title)
    ]);
    if (accepted.has(attempt)) {
      state.streak += 1;
      state.bestStreak = Math.max(state.bestStreak, state.streak);
      const bonus = Math.min(Math.max(0, state.streak - 1) * STREAK_STEP, STREAK_CAP);
      const gained = BASE_POINTS + bonus;
      state.score += gained;
      entry.status = 'correct';
      setFeedback(`Correct · +${gained} points${bonus ? `, including a ${bonus}-point streak bonus` : ''}.`, 'correct');
    } else {
      entry.status = 'wrong';
      state.streak = 0;
      setFeedback(`Not this time. The answer was ${entry.answerLabel}.`, 'wrong');
    }
    updateScoreboard();
    updateWheel();
    window.setTimeout(moveNext, 420);
  };

  const passEntry = () => {
    if (!state.running || state.currentIndex < 0) return;
    state.entries[state.currentIndex].status = 'passed';
    setFeedback('Passed. This letter will return after the rest of the circuit.');
    updateWheel();
    moveNext();
  };

  const tick = () => {
    if (!state.running) return;
    state.remainingSeconds = Math.max(0, Math.ceil((state.deadline - Date.now()) / 1000));
    updateScoreboard();
    if (state.remainingSeconds === 0) finishRound('time');
  };

  const startRound = () => {
    if (state.running || !state.entries.length) return;
    state.running = true;
    state.deadline = Date.now() + ROUND_SECONDS * 1000;
    state.remainingSeconds = ROUND_SECONDS;
    elements.start.hidden = true;
    elements.input.disabled = false;
    elements.submit.disabled = false;
    elements.pass.disabled = false;
    setFeedback('The circuit is live. Correct answers build your streak.');
    activateEntry(0);
    updateScoreboard();
    state.timer = window.setInterval(tick, 250);
  };

  elements.start.addEventListener('click', startRound);
  elements.form.addEventListener('submit', submitAnswer);
  elements.pass.addEventListener('click', passEntry);
  elements.newRound.addEventListener('click', () => {
    prepareRound();
    startRound();
  });

  Promise.all([
    fetch('episodes.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    }),
    fetch('crossword.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Narrative registry returned ${response.status}`);
      return response.json();
    })
  ]).then(([episodeRegistry, crosswordRegistry]) => {
    const episodes = new Map((episodeRegistry.episodes || []).map((episode) => [episode.number, episode]));
    state.pool = (crosswordRegistry.entries || []).map((entry) => {
      const episode = episodes.get(entry.episodeNumber);
      const answer = normalize(entry.answer);
      if (!episode || !/^[A-Z]/.test(answer) || !entry.clue || normalize(entry.clue).includes(answer)) return null;
      return {
        ...entry,
        answer,
        answerLabel: deriveAnswerLabel(answer, episode.title),
        episode
      };
    }).filter(Boolean);

    for (const entry of state.pool) {
      const letter = entry.answer[0];
      if (!state.groups.has(letter)) state.groups.set(letter, []);
      state.groups.get(letter).push(entry);
    }
    if (state.pool.length < 10 || state.groups.size < 10) throw new Error('The narrative registry does not provide enough distinct initials');
    setText(elements.count, state.pool.length);
    prepareRound();
  }).catch((error) => {
    console.warn('The Impossible Alphabet unavailable:', error);
    setText(elements.status, 'The episode registries could not be loaded.');
    setText(elements.clue, 'The experiment is temporarily unavailable. The complete episode archive remains accessible.');
    setFeedback('Unable to assemble the letter circuit.', 'wrong');
    elements.start.disabled = true;
  });
})();
