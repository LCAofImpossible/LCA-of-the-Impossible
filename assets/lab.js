(() => {
  'use strict';

  const SCORE_STEPS = [500, 400, 300, 200, 100];
  const CLUE_LABELS = ['Season', 'Inventory', 'Impact', 'Function', 'Final clue'];
  const requiredFields = [
    'number', 'slug', 'title', 'url', 'seasonLabel', 'lcaLabel', 'lcaCharacteristics',
    'result', 'hotspot', 'functionalUnit', 'subjectDescription'
  ];

  const elements = {
    count: document.getElementById('lab-case-count'),
    round: document.getElementById('lab-round'),
    score: document.getElementById('lab-score'),
    streak: document.getElementById('lab-streak'),
    points: document.getElementById('lab-points'),
    status: document.getElementById('lab-status'),
    clueList: document.getElementById('lab-clue-list'),
    form: document.getElementById('lab-answer-form'),
    input: document.getElementById('lab-answer-input'),
    options: document.getElementById('lab-answer-options'),
    submit: document.getElementById('lab-submit'),
    feedback: document.getElementById('lab-feedback'),
    reveal: document.getElementById('lab-reveal'),
    newCase: document.getElementById('lab-new-case'),
    result: document.getElementById('lab-result'),
    resultState: document.getElementById('lab-result-state'),
    resultTitle: document.getElementById('lab-result-title'),
    resultSubject: document.getElementById('lab-result-subject'),
    resultEpisode: document.getElementById('lab-result-episode'),
    resultSeason: document.getElementById('lab-result-season'),
    resultImpact: document.getElementById('lab-result-impact'),
    resultHotspot: document.getElementById('lab-result-hotspot'),
    resultLink: document.getElementById('lab-result-link')
  };

  if (!elements.form || !elements.clueList) return;

  const state = {
    episodes: [],
    unused: [],
    current: null,
    clues: [],
    clueIndex: 0,
    round: 0,
    score: 0,
    streak: 0,
    resolved: false
  };

  const normalize = (value = '') => String(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/^(the|a|an)\s+/, '');

  const eligible = (episode) => episode
    && requiredFields.every((field) => {
      const value = episode[field];
      return Array.isArray(value) ? value.length > 0 : String(value ?? '').trim().length > 0;
    });

  const titlePattern = (title) => {
    const withoutArticle = String(title).replace(/^(the|a|an)\s+/i, '');
    const alternatives = [title, withoutArticle]
      .filter(Boolean)
      .sort((a, b) => b.length - a.length)
      .map((value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    return new RegExp(`\\b(?:${alternatives.join('|')})\\b`, 'gi');
  };

  const redactSubject = (episode) => {
    const redacted = String(episode.subjectDescription).replace(titlePattern(episode.title), '[SUBJECT REDACTED]');
    return redacted === episode.subjectDescription
      ? `The final case note reads: ${redacted}`
      : redacted;
  };

  const inventoryClue = (episode) => {
    const model = episode.structuredMetadata?.model;
    const primary = model?.primaryDriver
      ? `${model.primaryDriver.replaceAll('-', ' ')} is the registered primary driver`
      : `the approved case is classified as ${episode.lcaLabel.toLowerCase()}`;
    const signals = (model?.secondaryDrivers?.length ? model.secondaryDrivers : episode.lcaCharacteristics)
      .map((value) => String(value).replaceAll('-', ' '))
      .filter((value) => !normalize(value).includes(normalize(model?.primaryDriver || episode.lcaLabel)))
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

  const randomIndex = (length) => {
    if (window.crypto?.getRandomValues) {
      const values = new Uint32Array(1);
      window.crypto.getRandomValues(values);
      return values[0] % length;
    }
    return Math.floor(Math.random() * length);
  };

  const setText = (element, value) => {
    if (element) element.textContent = String(value);
  };

  const updateScoreboard = () => {
    setText(elements.round, state.round);
    setText(elements.score, state.score);
    setText(elements.streak, state.streak);
    setText(elements.points, state.resolved ? 0 : SCORE_STEPS[state.clueIndex]);
  };

  const setFeedback = (message, type = '') => {
    elements.feedback.className = `lab-feedback${type ? ` is-${type}` : ''}`;
    setText(elements.feedback, message);
  };

  const renderClues = () => {
    [...elements.clueList.querySelectorAll('[data-clue-index]')].forEach((item, index) => {
      const paragraph = item.querySelector('p');
      item.classList.toggle('is-locked', index > state.clueIndex);
      item.classList.toggle('is-current', !state.resolved && index === state.clueIndex);
      if (paragraph) paragraph.textContent = index <= state.clueIndex ? state.clues[index] : 'Encrypted';
    });
  };

  const answerVariants = (episode) => {
    const title = String(episode.title);
    return new Set([
      normalize(title),
      normalize(title.replace(/^(the|a|an)\s+/i, '')),
      normalize(String(episode.slug).replaceAll('-', ' '))
    ]);
  };

  const isCorrectAnswer = (answer) => answerVariants(state.current).has(normalize(answer));

  const showResult = (solved, points = 0) => {
    const episode = state.current;
    state.resolved = true;
    state.streak = solved ? state.streak + 1 : 0;
    if (solved) state.score += points;
    updateScoreboard();

    elements.input.disabled = true;
    elements.submit.disabled = true;
    elements.reveal.disabled = true;
    elements.newCase.hidden = false;
    elements.result.hidden = false;
    setText(elements.resultState, solved ? `CASE IDENTIFIED · +${points} PTS` : 'CASE DECLASSIFIED · 0 PTS');
    setText(elements.resultTitle, episode.title);
    setText(elements.resultSubject, episode.subjectDescription);
    setText(elements.resultEpisode, `#${episode.number}`);
    setText(elements.resultSeason, episode.seasonLabel);
    setText(elements.resultImpact, episode.result);
    setText(elements.resultHotspot, episode.hotspot);
    elements.resultLink.href = episode.url;
    setText(elements.status, solved ? 'Identity confirmed against the registry.' : 'Identity revealed after the final clue.');
    setFeedback(
      solved ? `Correct. You identified the case from clue ${state.clueIndex + 1}.` : `The classified subject was ${episode.title}.`,
      solved ? 'correct' : 'wrong'
    );
    elements.result.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'nearest' });
  };

  const revealNext = (fromWrongGuess = false) => {
    if (state.resolved) return;
    if (state.clueIndex >= state.clues.length - 1) {
      showResult(false);
      return;
    }
    state.clueIndex += 1;
    renderClues();
    updateScoreboard();
    elements.reveal.textContent = state.clueIndex === state.clues.length - 1 ? 'Reveal answer' : 'Reveal next clue';
    setText(elements.status, `Clue ${String(state.clueIndex + 1).padStart(2, '0')} of 05 unlocked.`);
    setFeedback(fromWrongGuess ? 'Not this case. The next clue has been unlocked.' : `${CLUE_LABELS[state.clueIndex]} clue unlocked.`, fromWrongGuess ? 'wrong' : '');
    elements.input.focus();
  };

  const chooseEpisode = () => {
    if (!state.unused.length) state.unused = [...state.episodes];
    const index = randomIndex(state.unused.length);
    return state.unused.splice(index, 1)[0];
  };

  const startRound = () => {
    state.current = chooseEpisode();
    state.clues = buildClues(state.current);
    state.clueIndex = 0;
    state.round += 1;
    state.resolved = false;

    elements.result.hidden = true;
    elements.newCase.hidden = true;
    elements.input.disabled = false;
    elements.submit.disabled = false;
    elements.reveal.disabled = false;
    elements.input.value = '';
    elements.reveal.textContent = 'Reveal next clue';
    setText(elements.status, 'Clue 01 of 05 unlocked. Subject identity remains classified.');
    setFeedback('Submit a title now for 500 points, or reveal another clue.');
    renderClues();
    updateScoreboard();
    elements.input.focus();
  };

  const renderOptions = () => {
    const fragment = document.createDocumentFragment();
    [...state.episodes]
      .sort((a, b) => a.title.localeCompare(b.title))
      .forEach((episode) => {
        const option = document.createElement('option');
        option.value = episode.title;
        fragment.appendChild(option);
      });
    elements.options.replaceChildren(fragment);
  };

  elements.form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (state.resolved || !state.current) return;
    const answer = elements.input.value.trim();
    if (!answer) {
      setFeedback('Enter an episode title before submitting.', 'wrong');
      return;
    }
    if (isCorrectAnswer(answer)) {
      showResult(true, SCORE_STEPS[state.clueIndex]);
      return;
    }
    elements.input.select();
    revealNext(true);
  });

  elements.reveal.addEventListener('click', () => revealNext(false));
  elements.newCase.addEventListener('click', startRound);

  fetch('episodes.json', { cache: 'no-store', credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`Registry request returned ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      state.episodes = Array.isArray(registry.episodes) ? registry.episodes.filter(eligible) : [];
      if (!state.episodes.length) throw new Error('No complete episode records are available');
      state.unused = [...state.episodes];
      setText(elements.count, state.episodes.length);
      renderOptions();
      startRound();
    })
    .catch((error) => {
      console.warn('Impossible Lab unavailable:', error);
      setText(elements.status, 'The case registry could not be loaded.');
      setFeedback('The experiment is temporarily unavailable. The complete episode archive remains accessible.', 'wrong');
      elements.input.disabled = true;
      elements.submit.disabled = true;
      elements.reveal.disabled = true;
    });
})();
