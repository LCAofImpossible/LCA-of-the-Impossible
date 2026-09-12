(() => {
  'use strict';

  const timelineList = document.getElementById('timeline-list');
  if (!timelineList) return;

  const caseCount = document.getElementById('timeline-case-count');
  const roundValue = document.getElementById('timeline-round');
  const scoreValue = document.getElementById('timeline-score');
  const perfectValue = document.getElementById('timeline-perfect');
  const elapsedValue = document.getElementById('timeline-elapsed');
  const status = document.getElementById('timeline-status');
  const startPanel = document.getElementById('timeline-start-panel');
  const startButton = document.getElementById('timeline-start');
  const submitButton = document.getElementById('timeline-submit');
  const nextButton = document.getElementById('timeline-next');
  const feedback = document.getElementById('timeline-feedback');
  const reveal = document.getElementById('timeline-reveal');
  const revealList = document.getElementById('timeline-reveal-list');
  const finalPanel = document.getElementById('timeline-final');
  const finalCopy = document.getElementById('timeline-final-copy');
  const finalPairs = document.getElementById('timeline-final-pairs');
  const finalPerfect = document.getElementById('timeline-final-perfect');
  const finalRounds = document.getElementById('timeline-final-rounds');
  const finalTime = document.getElementById('timeline-final-time');
  const playAgain = document.getElementById('timeline-again');
  const resultTarget = finalPanel?.querySelector('[data-lab-result-scorecard]');
  const difficultySystem = window.ImpossibleLabDifficulty;

  const POINTS_PER_PAIR = 100;
  const fallbackConfig = Object.freeze({ cards: 4, rounds: 5, eraHints: false, spreadYears: 0 });
  const session = {
    pool: [],
    order: [],
    used: new Set(),
    round: 0,
    score: 0,
    correctPairs: 0,
    possiblePairs: 0,
    perfectRounds: 0,
    locked: false,
    startedAt: 0,
    timer: null,
    dragIndex: null
  };

  const config = () => ({ ...fallbackConfig, ...(difficultySystem?.config('timeline') || {}) });
  const shuffle = (values) => {
    const copy = [...values];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const target = Math.floor(Math.random() * (index + 1));
      [copy[index], copy[target]] = [copy[target], copy[index]];
    }
    return copy;
  };
  const pairCount = (count) => (count * (count - 1)) / 2;
  const formatTime = (milliseconds) => {
    const totalSeconds = Math.max(0, Math.floor(milliseconds / 1000));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };
  const elapsed = () => session.startedAt ? Date.now() - session.startedAt : 0;
  const updateElapsed = () => {
    if (elapsedValue) elapsedValue.textContent = formatTime(elapsed());
  };
  const setFeedback = (message, success = false) => {
    if (!feedback) return;
    feedback.textContent = message;
    feedback.classList.toggle('is-success', success);
  };

  const chooseWideSet = (available, count, minimumGap) => {
    const candidates = shuffle(available);
    for (let attempt = 0; attempt < 160; attempt += 1) {
      const selected = [];
      for (const candidate of shuffle(candidates)) {
        const separate = selected.every((item) => Math.abs(item.orderYear - candidate.orderYear) >= minimumGap);
        if (separate) selected.push(candidate);
        if (selected.length === count) return selected;
      }
    }
    return [];
  };

  const chooseCloseSet = (available, count) => {
    const unique = [...available]
      .sort((left, right) => left.orderYear - right.orderYear)
      .filter((item, index, all) => index === 0 || item.orderYear !== all[index - 1].orderYear);
    if (unique.length < count) return [];
    const windows = [];
    for (let index = 0; index <= unique.length - count; index += 1) {
      const window = unique.slice(index, index + count);
      windows.push({ window, span: window[window.length - 1].orderYear - window[0].orderYear });
    }
    windows.sort((left, right) => left.span - right.span);
    const shortlist = windows.slice(0, Math.max(1, Math.ceil(windows.length / 3)));
    return shortlist[Math.floor(Math.random() * shortlist.length)]?.window || [];
  };

  const chooseRound = () => {
    const rules = config();
    const needed = Math.min(rules.cards, session.pool.length);
    let available = session.pool.filter((entry) => !session.used.has(entry.episodeNumber));
    const uniqueYears = new Set(available.map((entry) => entry.orderYear));
    if (available.length < needed || uniqueYears.size < needed) {
      session.used.clear();
      available = [...session.pool];
    }

    let selected = [];
    if (rules.spreadYears > 0) selected = chooseWideSet(available, needed, rules.spreadYears);
    if (!selected.length && difficultySystem?.current() === 'impossible') selected = chooseCloseSet(available, needed);
    if (!selected.length) {
      const seenYears = new Set();
      selected = shuffle(available).filter((entry) => {
        if (seenYears.has(entry.orderYear)) return false;
        seenYears.add(entry.orderYear);
        return true;
      }).slice(0, needed);
    }
    selected.forEach((entry) => session.used.add(entry.episodeNumber));

    const chronological = [...selected].sort((left, right) => left.orderYear - right.orderYear);
    let mixed = shuffle(selected);
    if (mixed.every((entry, index) => entry.episodeNumber === chronological[index]?.episodeNumber)) {
      mixed = [...mixed.slice(1), mixed[0]];
    }
    return mixed;
  };

  const makeMoveButton = (label, symbol, index, direction) => {
    const button = document.createElement('button');
    button.className = 'timeline-move';
    button.type = 'button';
    button.textContent = symbol;
    button.setAttribute('aria-label', label);
    button.disabled = session.locked || (direction < 0 ? index === 0 : index === session.order.length - 1);
    button.addEventListener('click', () => move(index, index + direction));
    return button;
  };

  const renderCards = () => {
    const fragment = document.createDocumentFragment();
    const rules = config();
    session.order.forEach((entry, index) => {
      const item = document.createElement('li');
      item.className = 'timeline-card';
      item.draggable = !session.locked;
      item.dataset.index = String(index);

      const copy = document.createElement('div');
      copy.className = 'timeline-card-copy';
      const meta = document.createElement('div');
      meta.className = 'timeline-card-meta';
      const season = document.createElement('span');
      season.textContent = entry.episode.seasonLabel;
      const clue = document.createElement('span');
      clue.textContent = rules.eraHints ? entry.eraLabel : 'Historical date classified';
      const title = document.createElement('h3');
      title.textContent = entry.episode.title;
      meta.append(season, clue);
      copy.append(meta, title);

      const controls = document.createElement('div');
      controls.className = 'timeline-card-controls';
      controls.append(
        makeMoveButton(`Move ${entry.episode.title} earlier`, '↑', index, -1),
        makeMoveButton(`Move ${entry.episode.title} later`, '↓', index, 1)
      );
      item.append(copy, controls);

      item.addEventListener('dragstart', (event) => {
        if (session.locked) return;
        session.dragIndex = index;
        item.classList.add('is-dragging');
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', String(index));
      });
      item.addEventListener('dragend', () => {
        session.dragIndex = null;
        item.classList.remove('is-dragging');
        document.querySelectorAll('.timeline-card.is-drop-target').forEach((node) => node.classList.remove('is-drop-target'));
      });
      item.addEventListener('dragover', (event) => {
        if (session.locked) return;
        event.preventDefault();
        item.classList.add('is-drop-target');
      });
      item.addEventListener('dragleave', () => item.classList.remove('is-drop-target'));
      item.addEventListener('drop', (event) => {
        if (session.locked) return;
        event.preventDefault();
        item.classList.remove('is-drop-target');
        const from = Number(event.dataTransfer.getData('text/plain'));
        if (Number.isInteger(from)) move(from, index);
      });

      fragment.appendChild(item);
    });
    timelineList.replaceChildren(fragment);
  };

  function move(from, to) {
    if (session.locked || from === to || from < 0 || to < 0 || from >= session.order.length || to >= session.order.length) return;
    const [entry] = session.order.splice(from, 1);
    session.order.splice(to, 0, entry);
    renderCards();
    setFeedback(`${entry.episode.title} moved ${to < from ? 'earlier' : 'later'}.`);
  }

  const renderReveal = () => {
    const chronological = [...session.order].sort((left, right) => left.orderYear - right.orderYear);
    const fragment = document.createDocumentFragment();
    chronological.forEach((entry) => {
      const item = document.createElement('li');
      const copy = document.createElement('div');
      const title = document.createElement('h3');
      const event = document.createElement('p');
      const source = document.createElement('p');
      const episodeLink = document.createElement('a');
      const date = document.createElement('span');
      title.textContent = entry.episode.title;
      event.textContent = entry.event;
      source.className = 'timeline-source';
      source.textContent = `Historical basis: ${entry.source}`;
      episodeLink.className = 'timeline-episode-link';
      episodeLink.href = entry.episode.url;
      episodeLink.textContent = `Open Episode #${String(entry.episode.number).padStart(2, '0')} →`;
      date.className = 'timeline-date';
      date.textContent = entry.dateLabel;
      copy.append(title, event, source, episodeLink);
      item.append(copy, date);
      fragment.appendChild(item);
    });
    revealList.replaceChildren(fragment);
    reveal.hidden = false;
  };

  const assessRound = () => {
    if (session.locked || !session.order.length) return;
    session.locked = true;
    let correct = 0;
    for (let left = 0; left < session.order.length; left += 1) {
      for (let right = left + 1; right < session.order.length; right += 1) {
        if (session.order[left].orderYear < session.order[right].orderYear) correct += 1;
      }
    }
    const possible = pairCount(session.order.length);
    const gained = correct * POINTS_PER_PAIR;
    session.correctPairs += correct;
    session.possiblePairs += possible;
    session.score += gained;
    if (correct === possible) session.perfectRounds += 1;
    if (scoreValue) scoreValue.textContent = session.score.toLocaleString('en-US');
    if (perfectValue) perfectValue.textContent = String(session.perfectRounds);
    renderCards();
    renderReveal();
    submitButton.disabled = true;
    nextButton.hidden = false;
    const summary = correct === possible
      ? `Perfect chronology: ${correct} of ${possible} pairs correct. +${gained} points.`
      : `${correct} of ${possible} historical pairs correct. +${gained} points.`;
    setFeedback(summary, correct === possible);
    if (status) status.textContent = 'Chronology revealed. Review the historical evidence before continuing.';
    nextButton.textContent = session.round >= config().rounds ? 'View final result →' : 'Next timeline →';
  };

  const prepareRound = () => {
    session.round += 1;
    session.locked = false;
    session.order = chooseRound();
    if (roundValue) roundValue.textContent = `${session.round} / ${config().rounds}`;
    if (status) status.textContent = `Round ${session.round}: arrange ${session.order.length} subjects from earliest to latest.`;
    reveal.hidden = true;
    revealList.replaceChildren();
    submitButton.disabled = false;
    nextButton.hidden = true;
    renderCards();
    setFeedback('Move the cards into chronological order, then confirm once.');
  };

  const finishGame = () => {
    window.clearInterval(session.timer);
    session.timer = null;
    updateElapsed();
    timelineList.replaceChildren();
    reveal.hidden = true;
    submitButton.disabled = true;
    nextButton.hidden = true;
    if (status) status.textContent = 'Timeline complete. Your historical ordering score is ready.';

    const totalRounds = config().rounds;
    const accuracy = session.possiblePairs ? (session.correctPairs / session.possiblePairs) * 100 : 0;
    const maximum = session.possiblePairs * POINTS_PER_PAIR;
    if (finalCopy) finalCopy.textContent = `${session.correctPairs} of ${session.possiblePairs} historical pairs were placed in the correct order.`;
    if (finalPairs) finalPairs.textContent = `${session.correctPairs} / ${session.possiblePairs}`;
    if (finalPerfect) finalPerfect.textContent = `${session.perfectRounds} / ${totalRounds}`;
    if (finalRounds) finalRounds.textContent = String(totalRounds);
    if (finalTime) finalTime.textContent = formatTime(elapsed());
    window.ImpossibleLabResults?.render(resultTarget, {
      title: 'Impossible Timeline complete',
      score: session.score,
      maximum,
      completion: 100,
      accuracy,
      scoreLabel: 'Chronology score'
    });
    finalPanel.hidden = false;
    finalPanel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  };

  const startGame = () => {
    window.clearInterval(session.timer);
    session.order = [];
    session.used.clear();
    session.round = 0;
    session.score = 0;
    session.correctPairs = 0;
    session.possiblePairs = 0;
    session.perfectRounds = 0;
    session.startedAt = Date.now();
    session.locked = false;
    if (scoreValue) scoreValue.textContent = '0';
    if (perfectValue) perfectValue.textContent = '0';
    if (elapsedValue) elapsedValue.textContent = '00:00';
    if (startPanel) startPanel.hidden = true;
    finalPanel.hidden = true;
    session.timer = window.setInterval(updateElapsed, 1000);
    prepareRound();
  };

  startButton?.addEventListener('click', startGame);
  submitButton?.addEventListener('click', assessRound);
  nextButton?.addEventListener('click', () => {
    if (!session.locked) return;
    if (session.round >= config().rounds) finishGame();
    else prepareRound();
  });
  playAgain?.addEventListener('click', () => {
    finalPanel.hidden = true;
    startGame();
    document.getElementById('lab-game-area')?.focus({ preventScroll: true });
    document.getElementById('lab-game-area')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  Promise.all([
    fetch('episodes.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    }),
    fetch('timeline.json', { cache: 'no-store', credentials: 'same-origin' }).then((response) => {
      if (!response.ok) throw new Error(`Timeline registry returned ${response.status}`);
      return response.json();
    })
  ]).then(([episodeRegistry, timelineRegistry]) => {
    const episodes = new Map((Array.isArray(episodeRegistry.episodes) ? episodeRegistry.episodes : [])
      .filter((episode) => episode && Number.isFinite(Number(episode.number)) && episode.title && episode.url && episode.seasonLabel)
      .map((episode) => [Number(episode.number), episode]));
    session.pool = (Array.isArray(timelineRegistry.entries) ? timelineRegistry.entries : [])
      .filter((entry) => entry && Number.isFinite(Number(entry.episodeNumber)) && Number.isFinite(Number(entry.orderYear)) && entry.dateLabel && entry.eraLabel && entry.event && entry.source)
      .map((entry) => ({ ...entry, episode: episodes.get(Number(entry.episodeNumber)), orderYear: Number(entry.orderYear) }))
      .filter((entry) => entry.episode);
    if (new Set(session.pool.map((entry) => entry.orderYear)).size < fallbackConfig.cards) throw new Error('Too few distinct historical dates');
    if (caseCount) caseCount.textContent = String(session.pool.length);
    if (status) status.textContent = `${session.pool.length} historical records ready. Choose a level and start when ready.`;
    startButton.disabled = false;
  }).catch((error) => {
    console.warn('Impossible Timeline unavailable:', error);
    if (status) status.textContent = 'The historical record is temporarily unavailable. The episode archive remains accessible.';
    setFeedback('Unable to assemble a timeline. Please return to the Lab or open the episode archive.');
  });
})();
