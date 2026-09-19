(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  if (!$('ascent-start-button')) return;
  const levelSystem = window.ImpossibleLabDifficulty;
  const LEVEL_LENGTHS = Object.freeze({ explorer: 8, analyst: 12, impossible: 15 });
  const PATTERN = Object.freeze([
    'clue', 'clue', 'lens', 'clue', 'origin', 'lens', 'hotspot', 'origin',
    'lens', 'clue', 'hotspot', 'hotspot', 'origin', 'hotspot', 'hotspot'
  ]);
  const POINTS = 100;
  const ASSIST_COST = 25;
  const CHECKPOINT_SPAN = 4;
  const level = levelSystem?.current() || 'analyst';
  const count = levelSystem?.config('ascent')?.questions || LEVEL_LENGTHS[level] || LEVEL_LENGTHS.analyst;
  const day = new Date().toISOString().slice(0, 10);
  const elements = {
    start: $('ascent-start'), startButton: $('ascent-start-button'), count: $('ascent-question-count'),
    status: $('ascent-status'), game: $('lab-game-area'), final: $('ascent-final'),
    progress: $('ascent-progress'), tier: $('ascent-tier'), secured: $('ascent-secured'),
    track: $('ascent-track'), fill: $('ascent-track-fill'), category: $('ascent-category'),
    prompt: $('ascent-prompt'), choices: $('ascent-choices'), feedback: $('ascent-feedback'),
    next: $('ascent-next'), half: $('ascent-half'), hint: $('ascent-hint'), swap: $('ascent-swap'),
    assistHint: $('ascent-assist-hint'), finalCopy: $('ascent-final-copy'),
    finalReached: $('ascent-final-reached'), finalCorrect: $('ascent-final-correct'),
    finalAssists: $('ascent-final-assists'), finalTime: $('ascent-final-time'),
    review: $('ascent-review-list'), again: $('ascent-again')
  };
  const resultTarget = elements.final.querySelector('[data-lab-result-scorecard]');
  const state = { deck: [], reserve: [], index: 0, correct: 0, answered: 0, used: new Set(), removed: new Set(), review: [], locked: false, startedAt: 0, finished: false };

  const hash = (value) => {
    let h = 2166136261;
    for (const char of value) { h ^= char.charCodeAt(0); h = Math.imul(h, 16777619); }
    return h >>> 0;
  };
  const random = (seed) => () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const shuffle = (values, rng) => {
    const copy = [...values];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const other = Math.floor(rng() * (index + 1));
      [copy[index], copy[other]] = [copy[other], copy[index]];
    }
    return copy;
  };
  const uniqueOptions = (answer, alternatives, rng) => {
    const other = [...new Set(alternatives.filter((value) => value && value !== answer))];
    if (other.length < 3) return null;
    return shuffle([answer, ...shuffle(other, rng).slice(0, 3)], rng);
  };

  const buildBank = (episodes, crossword, origins, timeline, seedKey) => {
    const rng = random(hash(seedKey));
    const clues = new Map(crossword.entries.map((entry) => [entry.episodeNumber, entry.clue]));
    const regions = new Map(origins.macroRegions.map((region) => [region.id, region.label]));
    const locations = new Map(origins.entries
      .filter((entry) => entry.eligible && entry.acceptedMapRegions?.length === 1 && regions.has(entry.mapRegion))
      .map((entry) => [entry.episodeNumber, entry]));
    const dates = new Map(timeline.entries.map((entry) => [entry.episodeNumber, entry]));
    const archive = episodes.episodes
      .filter((episode) => episode.number && episode.title && episode.url && clues.has(episode.number))
      .sort((left, right) => left.number - right.number);
    if (archive.length < count + 3) throw new Error('The published archive is too small for this challenge.');

    const byType = (type, episode) => {
      const base = { type, number: episode.number, episode, source: episode.url };
      if (type === 'clue') {
        const answer = episode.title;
        const options = uniqueOptions(answer, archive.map((item) => item.title), rng);
        return options && { ...base, category: 'IDENTIFY THE SUBJECT', prompt: clues.get(episode.number),
          answer, options, hint: episode.seasonLabel,
          explanation: episode.subjectDescription || `The archive identifies this subject as ${answer}.` };
      }
      if (type === 'lens') {
        const answer = episode.lcaLabel;
        const options = uniqueOptions(answer, archive.map((item) => item.lcaLabel), rng);
        return options && { ...base, category: 'LIFE-CYCLE LENS', prompt: `Which published LCA lens is assigned to ${episode.title}?`,
          answer, options, hint: episode.subjectDescription,
          explanation: `The episode identifies its LCA lens as “${answer}”.` };
      }
      if (type === 'origin') {
        const origin = locations.get(episode.number);
        if (!origin) return null;
        const answer = regions.get(origin.mapRegion);
        const options = uniqueOptions(answer, [...regions.values()], rng);
        return options && { ...base, category: 'CULTURAL ORIGIN',
          prompt: `Where does the archive place the analysed version of ${episode.title}?`,
          answer, options, hint: dates.get(episode.number)?.dateLabel || episode.seasonLabel,
          explanation: origin.locationBasis || origin.originLabel };
      }
      if (type === 'hotspot') {
        const answer = episode.hotspot;
        if (!answer || answer.length > 190) return null;
        const others = archive.map((item) => item.hotspot).filter((item) => item && item.length <= 190);
        const options = uniqueOptions(answer, others, rng);
        return options && { ...base, category: 'MODEL FINDING',
          prompt: `Which finding belongs to the published model for ${episode.title}?`,
          answer, options, hint: `Published LCA lens: ${episode.lcaLabel}.`, explanation: answer };
      }
      return null;
    };
    const used = new Set();
    const reserve = [];
    const deck = PATTERN.slice(0, count).map((type) => {
      const candidates = shuffle(archive.filter((episode) => !used.has(episode.number)), rng);
      const question = candidates.map((episode) => byType(type, episode)).find(Boolean);
      if (!question) throw new Error(`Cannot assemble an approved ${type} question.`);
      used.add(question.number);
      return question;
    });
    // Same-family replacement questions preserve the difficulty of a swapped rung.
    [...new Set(PATTERN.slice(0, count))].forEach((type) => {
      const replacement = shuffle(archive.filter((episode) => !used.has(episode.number)), rng)
        .map((episode) => byType(type, episode)).find(Boolean);
      if (replacement) { reserve.push(replacement); used.add(replacement.number); }
    });
    return { deck, reserve };
  };

  const current = () => state.deck[state.index];
  const checkpoints = () => Math.floor(state.correct / CHECKPOINT_SPAN) * CHECKPOINT_SPAN;
  const assistsUsed = () => state.used.size;
  const score = (won) => Math.max(0, (won ? state.correct : checkpoints()) * POINTS - assistsUsed() * ASSIST_COST);
  const refreshSecured = () => { elements.secured.textContent = `${score(false)} pts`; };
  const formatTime = (milliseconds) => {
    const seconds = Math.floor(milliseconds / 1000);
    return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  };
  const tier = () => state.index < 4 ? 'THE FIRST SIGNAL' : state.index < 8 ? 'BEYOND THE GATE' : state.index < 12 ? 'THE FINAL FRONTIER' : 'THE IMPOSSIBLE SUMMIT';

  const renderQuestion = () => {
    const question = current();
    state.locked = false;
    state.removed.clear();
    elements.progress.textContent = `Question ${state.index + 1} of ${count}`;
    elements.tier.textContent = tier();
    refreshSecured();
    elements.category.textContent = question.category;
    elements.prompt.textContent = question.prompt;
    elements.track.setAttribute('aria-valuemax', String(count));
    elements.track.setAttribute('aria-valuenow', String(state.index));
    elements.fill.style.width = `${(state.index / count) * 100}%`;
    elements.feedback.hidden = true;
    elements.feedback.replaceChildren();
    elements.next.hidden = true;
    elements.assistHint.hidden = true;
    elements.assistHint.textContent = '';
    [elements.half, elements.hint, elements.swap].forEach((button) => {
      button.disabled = state.used.has(button.id);
    });
    const fragment = document.createDocumentFragment();
    question.options.forEach((option, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.answer = option;
      const letter = document.createElement('span');
      letter.className = 'ascent-choice-letter';
      letter.textContent = `${String.fromCharCode(65 + index)}.`;
      const copy = document.createElement('span');
      copy.textContent = option;
      button.append(letter, copy);
      button.addEventListener('click', () => answer(option));
      fragment.append(button);
    });
    elements.choices.replaceChildren(fragment);
  };

  const reveal = (correct) => {
    const question = current();
    elements.choices.querySelectorAll('button').forEach((button) => {
      button.disabled = true;
      if (button.dataset.answer === question.answer) button.classList.add('is-correct');
      else if (button.dataset.answer === state.review.at(-1).selected) button.classList.add('is-wrong');
    });
    [elements.half, elements.hint, elements.swap].forEach((button) => { button.disabled = true; });
    const heading = document.createElement('strong');
    heading.textContent = correct ? `Correct. +${POINTS} points.` : `The ascent stops here. Answer: ${question.answer}.`;
    const explanation = document.createElement('p');
    explanation.textContent = question.explanation;
    const link = document.createElement('a');
    link.href = question.source;
    link.textContent = `Read Episode #${question.number} →`;
    elements.feedback.classList.toggle('is-wrong', !correct);
    elements.feedback.append(heading, explanation, link);
    elements.feedback.hidden = false;
    elements.next.textContent = !correct || state.correct === count ? 'View the archive report →' : 'Continue the ascent →';
    elements.next.hidden = false;
  };

  function answer(selected) {
    if (state.locked || state.finished || state.removed.has(selected)) return;
    state.locked = true;
    const question = current();
    const correct = selected === question.answer;
    state.answered += 1;
    if (correct) state.correct += 1;
    state.review.push({ ...question, selected, correct });
    reveal(correct);
    if (correct && state.correct % CHECKPOINT_SPAN === 0) {
      refreshSecured();
    }
    if (correct) {
      elements.track.setAttribute('aria-valuenow', String(state.correct));
      elements.fill.style.width = `${(state.correct / count) * 100}%`;
    }
  }

  const renderReport = () => {
    if (state.finished) return;
    state.finished = true;
    const won = state.correct === count;
    const finalScore = score(won);
    elements.game.hidden = true;
    elements.final.hidden = false;
    elements.finalCopy.textContent = won
      ? `You reached the summit. ${count} published cases recovered across the archive.`
      : `${state.correct} correct answer${state.correct === 1 ? '' : 's'}. Your last secured checkpoint determines the result.`;
    elements.finalReached.textContent = `${state.answered} / ${count}`;
    elements.finalCorrect.textContent = String(state.correct);
    elements.finalAssists.textContent = String(assistsUsed());
    elements.finalTime.textContent = formatTime(Date.now() - state.startedAt);
    const fragment = document.createDocumentFragment();
    state.review.forEach((item, index) => {
      const row = document.createElement('li');
      const eyebrow = document.createElement('span');
      eyebrow.textContent = `QUESTION ${index + 1} · ${item.correct ? 'CORRECT' : 'MISSED'}`;
      const title = document.createElement('strong');
      title.textContent = item.episode.title;
      const detail = document.createElement('p');
      detail.textContent = item.explanation;
      const link = document.createElement('a');
      link.href = item.source;
      link.textContent = `Open Episode #${item.number} →`;
      row.append(eyebrow, title, detail, link);
      fragment.append(row);
    });
    elements.review.replaceChildren(fragment);
    window.ImpossibleLabResults?.render(resultTarget, {
      title: won ? 'Impossible Ascent conquered' : 'Impossible Ascent checkpoint',
      score: finalScore, maximum: count * POINTS,
      completion: (state.correct / count) * 100,
      accuracy: state.answered ? (state.correct / state.answered) * 100 : 0,
      scoreLabel: 'Ascent score'
    });
    elements.final.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  };

  const useAssist = (button) => {
    if (state.locked || state.finished || state.used.has(button.id)) return false;
    state.used.add(button.id);
    button.disabled = true;
    refreshSecured();
    return true;
  };
  elements.half.addEventListener('click', () => {
    if (!useAssist(elements.half)) return;
    const question = current();
    const wrong = question.options.filter((option) => option !== question.answer).slice(0, 2);
    wrong.forEach((option) => state.removed.add(option));
    elements.choices.querySelectorAll('button').forEach((button) => {
      if (state.removed.has(button.dataset.answer)) { button.disabled = true; button.classList.add('is-removed'); }
    });
  });
  elements.hint.addEventListener('click', () => {
    if (!useAssist(elements.hint)) return;
    elements.assistHint.textContent = current().hint || 'The published archive has no further hint for this case.';
    elements.assistHint.hidden = false;
  });
  elements.swap.addEventListener('click', () => {
    const replacementIndex = state.reserve.findIndex((item) => item.type === current().type);
    if (replacementIndex < 0 || !useAssist(elements.swap)) return;
    state.deck[state.index] = state.reserve.splice(replacementIndex, 1)[0];
    renderQuestion();
  });
  elements.next.addEventListener('click', () => {
    if (!state.locked) return;
    if (state.correct !== state.answered || state.correct === count) return renderReport();
    state.index += 1;
    renderQuestion();
    elements.prompt.focus();
  });
  elements.again.addEventListener('click', () => window.location.assign(levelSystem?.withLevel('lab-ascent.html') || 'lab-ascent.html'));

  elements.count.textContent = String(count);
  Promise.all(['episodes.json', 'crossword.json', 'origins.json', 'timeline.json'].map(async (url) => {
    const response = await fetch(url, { cache: 'no-store', credentials: 'same-origin' });
    if (!response.ok) throw new Error(`Archive returned ${response.status}`);
    return response.json();
  })).then(([episodes, crossword, origins, timeline]) => {
    const challenge = buildBank(episodes, crossword, origins, timeline, `${day}:${level}:ascent-v1`);
    state.deck = challenge.deck;
    state.reserve = challenge.reserve;
    elements.startButton.disabled = false;
    elements.startButton.textContent = 'Begin the ascent →';
    elements.status.textContent = `Archive ready · ${episodes.episodes.length} published subjects · ${day} UTC challenge.`;
  }).catch((error) => {
    console.error('Impossible Ascent archive unavailable:', error);
    elements.status.replaceChildren();
    const message = document.createTextNode('The archive cannot be loaded right now. ');
    const link = document.createElement('a');
    link.href = 'archive.html';
    link.textContent = 'Explore the episodes →';
    elements.status.append(message, link);
    elements.startButton.textContent = 'Archive unavailable';
  });
  elements.startButton.addEventListener('click', () => {
    if (!state.deck.length) return;
    state.startedAt = Date.now();
    elements.start.hidden = true;
    elements.status.hidden = true;
    elements.game.hidden = false;
    renderQuestion();
    elements.game.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  });

  window.ImpossibleAscent = Object.freeze({ buildBank, LEVEL_LENGTHS, PATTERN });
})();
