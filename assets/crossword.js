(() => {
  'use strict';

  const engine = window.ImpossibleCrossword;
  const resultSystem = window.ImpossibleLabResults;
  const difficultySystem = window.ImpossibleLabDifficulty;
  const difficulty = difficultySystem?.config('crossword') || { targetWords: 10, minWords: 8, freeInitials: false, revealLimit: null };
  const elements = {
    count: document.getElementById('crossword-case-count'),
    round: document.getElementById('crossword-round'),
    progress: document.getElementById('crossword-progress'),
    score: document.getElementById('crossword-score'),
    available: document.getElementById('crossword-available'),
    status: document.getElementById('crossword-status'),
    grid: document.getElementById('crossword-grid'),
    across: document.getElementById('crossword-across'),
    down: document.getElementById('crossword-down'),
    check: document.getElementById('crossword-check'),
    reveal: document.getElementById('crossword-reveal'),
    newGrid: document.getElementById('crossword-new'),
    replay: document.getElementById('crossword-replay'),
    feedback: document.getElementById('crossword-feedback'),
    result: document.getElementById('lab-result') || document.getElementById('crossword-result'),
    resultScorecard: document.querySelector('[data-lab-result-scorecard]'),
    resultState: document.getElementById('lab-result-state') || document.getElementById('crossword-result-state'),
    resultTitle: document.getElementById('lab-result-title') || document.getElementById('crossword-result-title'),
    resultSubject: document.getElementById('lab-result-subject') || document.getElementById('crossword-result-subject'),
    resultEpisode: document.getElementById('lab-result-episode') || document.getElementById('crossword-result-episode'),
    resultSeason: document.getElementById('lab-result-season') || document.getElementById('crossword-result-season'),
    resultImpact: document.getElementById('lab-result-impact') || document.getElementById('crossword-result-impact'),
    resultHotspot: document.getElementById('lab-result-hotspot') || document.getElementById('crossword-result-hotspot'),
    resultLink: document.getElementById('lab-result-link') || document.getElementById('crossword-result-link')
  };

  if (!engine || !elements.grid || !elements.across || !elements.down) return;

  const state = {
    pool: [],
    usedEpisodes: new Set(),
    layout: null,
    activeEntryId: null,
    correctEntries: new Set(),
    revealedCells: new Set(),
    inputByCell: new Map(),
    clueByEntry: new Map(),
    round: 0,
    complete: false,
    answerAttempts: 0
  };

  const keyOf = (row, col) => `${row},${col}`;
  const setText = (element, value) => { if (element) element.textContent = String(value); };
  const entryById = (id) => state.layout?.entries.find((entry) => entry.id === id);

  const cellsForEntry = (entry) => {
    const rowStep = entry.direction === 'down' ? 1 : 0;
    const colStep = entry.direction === 'across' ? 1 : 0;
    return [...entry.answer].map((_, index) => keyOf(entry.row + rowStep * index, entry.col + colStep * index));
  };

  const gridMaximum = () => (state.layout?.entries.length || difficulty.targetWords) * 50;
  const currentScore = () => Math.max(0, state.correctEntries.size * 50 - state.revealedCells.size * 10);
  const maximumPossible = () => Math.max(0, gridMaximum() - state.revealedCells.size * 10);
  const revealLimitReached = () => Number.isFinite(difficulty.revealLimit) && state.revealedCells.size >= difficulty.revealLimit;

  const updateScoreboard = () => {
    setText(elements.round, state.round);
    setText(elements.progress, `${state.correctEntries.size} / ${state.layout?.entries.length || 10}`);
    setText(elements.score, currentScore());
    setText(elements.available, maximumPossible());
    if (elements.reveal && state.layout) elements.reveal.disabled = state.complete || revealLimitReached();
  };

  const setFeedback = (message, type = '') => {
    elements.feedback.className = `crossword-feedback${type ? ` is-${type}` : ''}`;
    setText(elements.feedback, message);
  };

  const valueForEntry = (entry) => cellsForEntry(entry)
    .map((key) => state.inputByCell.get(key)?.value || '')
    .join('');

  const activateEntry = (entryId, focus = false) => {
    const entry = entryById(entryId);
    if (!entry) return;
    state.activeEntryId = entryId;
    document.querySelectorAll('.crossword-cell.is-active').forEach((cell) => cell.classList.remove('is-active'));
    document.querySelectorAll('.crossword-clue.is-active').forEach((clue) => clue.classList.remove('is-active'));
    cellsForEntry(entry).forEach((key) => state.inputByCell.get(key)?.parentElement.classList.add('is-active'));
    state.clueByEntry.get(entryId)?.classList.add('is-active');
    setText(elements.status, `${entry.number} ${entry.direction.toUpperCase()} · ${entry.answer.length} letters`);
    if (focus) {
      const target = cellsForEntry(entry).find((key) => !state.inputByCell.get(key)?.value) || cellsForEntry(entry)[0];
      state.inputByCell.get(target)?.focus();
    }
  };

  const selectEntryForCell = (cell, rotate = false) => {
    if (!cell?.entryIds?.length) return;
    if (cell.entryIds.length === 1) {
      activateEntry(cell.entryIds[0]);
      return;
    }
    const currentIndex = cell.entryIds.indexOf(state.activeEntryId);
    const nextIndex = rotate ? (currentIndex + 1) % cell.entryIds.length : Math.max(currentIndex, 0);
    activateEntry(cell.entryIds[nextIndex]);
  };

  const moveAlongEntry = (input, offset) => {
    const entry = entryById(state.activeEntryId);
    if (!entry) return;
    const keys = cellsForEntry(entry);
    const currentIndex = keys.indexOf(input.dataset.cellKey);
    const nextKey = keys[currentIndex + offset];
    if (nextKey) state.inputByCell.get(nextKey)?.focus();
  };

  const moveSpatially = (input, rowDelta, colDelta) => {
    let row = Number(input.dataset.row) + rowDelta;
    let col = Number(input.dataset.col) + colDelta;
    while (row >= 0 && col >= 0 && row < state.layout.rows && col < state.layout.cols) {
      const target = state.inputByCell.get(keyOf(row, col));
      if (target) {
        target.focus();
        return;
      }
      row += rowDelta;
      col += colDelta;
    }
  };

  const clearWrongState = (input) => {
    const cell = state.layout.cells.get(input.dataset.cellKey);
    cell.entryIds.forEach((entryId) => {
      const entry = entryById(entryId);
      if (entry) markEntry(entry, 'is-wrong', false);
    });
  };

  const bindCellEvents = (input, cell) => {
    let hadFocusBeforePointer = false;
    input.addEventListener('pointerdown', () => {
      hadFocusBeforePointer = document.activeElement === input;
    });
    input.addEventListener('focus', () => selectEntryForCell(cell, false));
    input.addEventListener('click', () => selectEntryForCell(cell, hadFocusBeforePointer));
    input.addEventListener('input', () => {
      input.value = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(-1);
      clearWrongState(input);
      if (input.value) moveAlongEntry(input, 1);
    });
    input.addEventListener('keydown', (event) => {
      if (input.readOnly && /^[A-Z0-9]$/i.test(event.key)) {
        event.preventDefault();
        moveAlongEntry(input, 1);
        return;
      }
      if (event.key === 'Backspace') {
        event.preventDefault();
        if (input.value && !input.readOnly) input.value = '';
        else moveAlongEntry(input, -1);
        clearWrongState(input);
      } else if (event.key === 'ArrowRight') {
        event.preventDefault(); moveSpatially(input, 0, 1);
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault(); moveSpatially(input, 0, -1);
      } else if (event.key === 'ArrowDown') {
        event.preventDefault(); moveSpatially(input, 1, 0);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault(); moveSpatially(input, -1, 0);
      } else if (event.key === 'Enter') {
        event.preventDefault(); checkGrid();
      } else if (event.key === ' ' && cell.entryIds.length > 1) {
        event.preventDefault(); selectEntryForCell(cell, true);
      }
    });
  };

  const renderGrid = () => {
    state.inputByCell.clear();
    elements.grid.style.setProperty('--crossword-cols', state.layout.cols);
    const fragment = document.createDocumentFragment();
    for (let row = 0; row < state.layout.rows; row += 1) {
      for (let col = 0; col < state.layout.cols; col += 1) {
        const key = keyOf(row, col);
        const cellData = state.layout.cells.get(key);
        const cell = document.createElement('div');
        cell.className = `crossword-cell${cellData ? '' : ' is-block'}`;
        if (cellData) {
          const number = state.layout.startNumbers.get(key);
          if (number) {
            const label = document.createElement('span');
            label.className = 'crossword-cell-number';
            label.textContent = number;
            cell.appendChild(label);
          }
          const input = document.createElement('input');
          input.maxLength = 1;
          input.autocomplete = 'off';
          input.spellcheck = false;
          input.inputMode = 'text';
          input.dataset.cellKey = key;
          input.dataset.row = row;
          input.dataset.col = col;
          input.setAttribute('aria-label', `Crossword row ${row + 1}, column ${col + 1}`);
          bindCellEvents(input, cellData);
          state.inputByCell.set(key, input);
          cell.appendChild(input);
        } else {
          cell.setAttribute('aria-hidden', 'true');
        }
        fragment.appendChild(cell);
      }
    }
    elements.grid.replaceChildren(fragment);
  };

  const makeClueButton = (entry) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'crossword-clue';
    button.dataset.entryId = entry.id;
    const number = document.createElement('span');
    number.textContent = entry.number;
    const text = document.createElement('p');
    text.textContent = entry.clue;
    const length = document.createElement('small');
    length.textContent = ` (${entry.answer.length})`;
    text.appendChild(length);
    button.append(number, text);
    button.addEventListener('click', () => activateEntry(entry.id, true));
    state.clueByEntry.set(entry.id, button);
    return button;
  };

  const renderClues = () => {
    state.clueByEntry.clear();
    const across = document.createDocumentFragment();
    const down = document.createDocumentFragment();
    state.layout.entries.forEach((entry) => {
      const item = document.createElement('li');
      item.appendChild(makeClueButton(entry));
      (entry.direction === 'across' ? across : down).appendChild(item);
    });
    elements.across.replaceChildren(across);
    elements.down.replaceChildren(down);
  };

  const markEntry = (entry, className, enabled) => {
    cellsForEntry(entry).forEach((key) => state.inputByCell.get(key)?.parentElement.classList.toggle(className, enabled));
    state.clueByEntry.get(entry.id)?.classList.toggle(className, enabled);
  };

  const showCase = (entry, complete = false) => {
    const episode = entry.episode;
    elements.result.hidden = false;
    elements.result.classList.toggle('is-complete', complete);
    setText(elements.resultState, complete ? `GRID COMPLETE · ${currentScore()} PTS` : 'CASE IDENTIFIED · +50 PTS');
    setText(elements.resultTitle, episode.title);
    setText(elements.resultSubject, episode.subjectDescription);
    setText(elements.resultEpisode, `#${episode.number}`);
    setText(elements.resultSeason, episode.seasonLabel);
    setText(elements.resultImpact, episode.result);
    setText(elements.resultHotspot, episode.hotspot);
    elements.resultLink.href = episode.url;
    if (elements.replay) elements.replay.hidden = !complete;
    const totalEntries = state.layout?.entries.length || 10;
    resultSystem?.render(elements.resultScorecard, {
      title: complete ? 'Grid complete' : 'Current grid performance',
      scoreLabel: 'Grid score',
      score: currentScore(),
      maximum: gridMaximum(),
      completion: (state.correctEntries.size / totalEntries) * 100,
      accuracy: state.answerAttempts ? (state.correctEntries.size / state.answerAttempts) * 100 : 0,
      persist: complete
    });
  };

  function checkGrid() {
    if (!state.layout || state.complete) return;
    const newlyCorrect = [];
    let hasCompleteWrongWord = false;
    state.layout.entries.forEach((entry) => {
      if (state.correctEntries.has(entry.id)) return;
      const value = valueForEntry(entry);
      if (value === entry.answer) {
        state.answerAttempts += 1;
        state.correctEntries.add(entry.id);
        newlyCorrect.push(entry);
        markEntry(entry, 'is-wrong', false);
        markEntry(entry, 'is-correct', true);
        cellsForEntry(entry).forEach((key) => {
          const input = state.inputByCell.get(key);
          input.readOnly = true;
          input.setAttribute('aria-readonly', 'true');
        });
      } else if (value.length === entry.answer.length) {
        state.answerAttempts += 1;
        hasCompleteWrongWord = true;
        markEntry(entry, 'is-wrong', true);
      }
    });

    state.complete = state.correctEntries.size === state.layout.entries.length;
    updateScoreboard();
    if (newlyCorrect.length) {
      showCase(newlyCorrect[newlyCorrect.length - 1], state.complete);
      setFeedback(
        state.complete
          ? `Grid solved. Final score: ${currentScore()} points.`
          : `${newlyCorrect.length} ${newlyCorrect.length === 1 ? 'case' : 'cases'} identified. The life-cycle record is now declassified below.`,
        'correct'
      );
    } else if (hasCompleteWrongWord) {
      setFeedback('At least one completed answer is incorrect. Review the highlighted cells.', 'wrong');
    } else {
      setFeedback('No new case is complete yet. Continue from the active clue.');
    }
    if (state.complete) {
      elements.check.disabled = true;
      elements.reveal.disabled = true;
      setText(elements.status, `All ${state.layout.entries.length} cases identified. The grid is complete.`);
    }
  }

  const revealLetter = () => {
    if (!state.layout || state.complete || revealLimitReached()) {
      if (revealLimitReached()) setFeedback(`The ${difficulty.revealLimit}-letter reveal limit has been reached.`, 'wrong');
      return;
    }
    let entry = entryById(state.activeEntryId);
    if (!entry || state.correctEntries.has(entry.id)) entry = state.layout.entries.find((item) => !state.correctEntries.has(item.id));
    if (!entry) return;
    const keys = cellsForEntry(entry);
    const targetKey = keys.find((key, index) => state.inputByCell.get(key)?.value !== entry.answer[index]);
    if (!targetKey) return;
    const index = keys.indexOf(targetKey);
    const input = state.inputByCell.get(targetKey);
    input.value = entry.answer[index];
    input.readOnly = true;
    input.setAttribute('aria-readonly', 'true');
    input.parentElement.classList.add('is-revealed');
    state.revealedCells.add(targetKey);
    clearWrongState(input);
    updateScoreboard();
    setFeedback(`One letter revealed in ${entry.number} ${entry.direction}. Ten points removed from the maximum score.`);
    input.focus();
  };

  const revealInitialLetters = () => {
    if (!difficulty.freeInitials) return;
    state.layout.entries.forEach((entry) => {
      const key = cellsForEntry(entry)[0];
      const input = state.inputByCell.get(key);
      if (!input) return;
      input.value = entry.answer[0];
      input.readOnly = true;
      input.setAttribute('aria-readonly', 'true');
      input.parentElement.classList.add('is-starter');
    });
  };

  const availablePool = () => {
    const unused = state.pool.filter((item) => !state.usedEpisodes.has(item.episodeNumber));
    const seasonOneRemaining = unused.some((item) => item.episode.seasonNumber === 1);
    const seasonTwoRemaining = unused.some((item) => item.episode.seasonNumber === 2);
    if (unused.length < 14 || !seasonOneRemaining || !seasonTwoRemaining) {
      state.usedEpisodes.clear();
      return state.pool;
    }
    return unused;
  };

  const startPuzzle = () => {
    const candidates = availablePool();
    state.round += 1;
    const day = new Date().toISOString().slice(0, 10);
    try {
      state.layout = engine.generate(candidates, { seed: `${day}:puzzle-${state.round}`, targetWords: difficulty.targetWords, minWords: difficulty.minWords });
    } catch (error) {
      console.warn('Crossword generation retried against the full case pool:', error);
      state.usedEpisodes.clear();
      state.layout = engine.generate(state.pool, { seed: `${day}:fallback-${state.round}`, targetWords: difficulty.targetWords, minWords: difficulty.minWords });
    }
    state.layout.entries.forEach((entry) => state.usedEpisodes.add(entry.episodeNumber));
    state.activeEntryId = null;
    state.correctEntries.clear();
    state.revealedCells.clear();
    state.complete = false;
    state.answerAttempts = 0;
    elements.result.hidden = true;
    elements.result.classList.remove('is-complete');
    if (elements.replay) elements.replay.hidden = true;
    elements.check.disabled = false;
    elements.reveal.disabled = false;
    elements.newGrid.disabled = false;
    renderGrid();
    revealInitialLetters();
    renderClues();
    updateScoreboard();
    const first = state.layout.entries.find((entry) => entry.direction === 'across') || state.layout.entries[0];
    activateEntry(first.id, false);
    setText(document.getElementById('grid-title'), `${state.layout.entries.length} CASES · ONE SYSTEM`);
    if (difficulty.freeInitials) {
      setFeedback('Every answer begins with one free letter. Select a clue or white cell to continue.');
    } else if (Number.isFinite(difficulty.revealLimit)) {
      setFeedback(`Select a clue or white cell to begin. Only ${difficulty.revealLimit} letter reveals are available.`);
    } else {
      setFeedback('Select a clue or a white cell and enter one letter at a time.');
    }
  };

  elements.check.addEventListener('click', checkGrid);
  elements.reveal.addEventListener('click', revealLetter);
  elements.newGrid.addEventListener('click', startPuzzle);
  elements.replay?.addEventListener('click', startPuzzle);

  Promise.all([
    fetch('episodes.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    }),
    fetch('crossword.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Crossword registry returned ${response.status}`);
      return response.json();
    })
  ]).then(([episodeRegistry, crosswordRegistry]) => {
    const episodes = new Map((episodeRegistry.episodes || []).map((episode) => [episode.number, episode]));
    const seenAnswers = new Set();
    state.pool = (crosswordRegistry.entries || []).map((entry) => {
      const answer = engine.normalizeAnswer(entry.answer);
      const episode = episodes.get(entry.episodeNumber);
      const clueLeaksAnswer = engine.normalizeAnswer(entry.clue).includes(answer);
      if (!episode || answer.length < 4 || answer.length > 20 || seenAnswers.has(answer) || clueLeaksAnswer) return null;
      seenAnswers.add(answer);
      return { ...entry, answer, episode };
    }).filter(Boolean);
    if (state.pool.length < difficulty.targetWords) throw new Error(`Fewer than ${difficulty.targetWords} complete crossword cases are available`);
    setText(elements.count, state.pool.length);
    startPuzzle();
  }).catch((error) => {
    console.warn('Cross the Impossible unavailable:', error);
    setText(elements.status, 'The crossword registries could not be loaded.');
    setFeedback('The experiment is temporarily unavailable. The complete episode archive remains accessible.', 'wrong');
    elements.check.disabled = true;
    elements.reveal.disabled = true;
    elements.newGrid.disabled = true;
  });
})();
