(() => {
  'use strict';

  const grid = document.querySelector('[data-lab-hub-grid]');
  const randomButton = document.querySelector('[data-random-game]');
  const scorePanel = document.querySelector('[data-lab-score-panel]');
  const scoreTotal = document.querySelector('[data-lab-score-total]');
  const scoreCompletion = document.querySelector('[data-lab-score-completion]');
  const scorePercent = document.querySelector('[data-lab-score-percent]');
  const scoreTrack = document.querySelector('[data-lab-score-track]');
  const scoreFill = document.querySelector('[data-lab-score-fill]');
  const scoreBreakdown = document.querySelector('[data-lab-score-breakdown]');
  const scoreStatus = document.querySelector('[data-lab-score-status]');
  const resetButton = document.querySelector('[data-lab-reset]');
  const progressSystem = window.ImpossibleLabProgress;
  const difficultySystem = window.ImpossibleLabDifficulty;
  const dailySystem = window.ImpossibleDaily;
  const dailyStatus = document.querySelector('[data-daily-hub-status]');
  const dailyStreak = document.querySelector('[data-daily-hub-streak]');
  if (!grid) return;

  let playableUrls = [...grid.querySelectorAll('.lab-hub-card')].map((card) => card.getAttribute('href')).filter(Boolean);
  let activeGames = [...grid.querySelectorAll('.lab-hub-card')].map((card, index) => ({
    id: card.dataset.gameId,
    number: index + 1,
    title: card.querySelector('h2')?.textContent || `Experiment ${index + 1}`,
    url: card.getAttribute('href')
  })).filter((game) => game.id && game.url);

  const makeMeta = (label, value) => {
    const wrapper = document.createElement('div');
    const term = document.createElement('dt');
    const definition = document.createElement('dd');
    term.textContent = label;
    definition.textContent = value;
    wrapper.append(term, definition);
    return wrapper;
  };

  const makeCard = (game) => {
    const card = document.createElement('a');
    card.className = 'lab-hub-card';
    card.href = game.url;
    card.dataset.gameId = game.id;
    card.dataset.experiment = String(game.number).padStart(2, '0');

    const number = document.createElement('span');
    number.className = 'lab-hub-number';
    number.textContent = `EXPERIMENT ${String(game.number).padStart(2, '0')}`;

    const title = document.createElement('h2');
    title.textContent = game.title;

    const summary = document.createElement('p');
    summary.textContent = game.summary;

    const metadata = document.createElement('dl');
    metadata.append(
      makeMeta('Challenge', game.category),
      makeMeta('Duration', game.duration),
      makeMeta('Level', difficultySystem?.detail().label || 'Analyst')
    );

    const action = document.createElement('strong');
    action.textContent = 'Play now ';
    const arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '→';
    action.appendChild(arrow);

    card.append(number, title, summary, metadata, action);
    return card;
  };

  const render = (games) => {
    const fragment = document.createDocumentFragment();
    games.sort((left, right) => left.number - right.number).forEach((game) => fragment.appendChild(makeCard(game)));
    grid.replaceChildren(fragment);
    difficultySystem?.decorateLinks(grid);
    playableUrls = games.map((game) => game.url);
  };

  const makeContribution = (game, record) => {
    const link = document.createElement('a');
    link.href = game.url;

    const title = document.createElement('span');
    title.textContent = game.title;

    const value = document.createElement('strong');
    value.textContent = record
      ? `${record.bestNormalized.toLocaleString('en-US')} / ${progressSystem.SCORE_SCALE.toLocaleString('en-US')}`
      : 'Not played';

    link.append(title, value);
    return link;
  };

  const renderScore = (games, reset = false) => {
    if (!scorePanel || !progressSystem) return;
    const summary = progressSystem.summarize();
    const percentage = summary.maximum ? Math.round((summary.total / summary.maximum) * 100) : 0;
    const gameCount = progressSystem.GAME_IDS.length;
    const levelSummary = difficultySystem?.summarize();
    const hasLevelRecords = Object.values(levelSummary?.games || {}).some((records) => Object.keys(records).length > 0);

    if (scoreTotal) {
      scoreTotal.textContent = summary.total.toLocaleString('en-US');
      scoreTotal.parentElement?.setAttribute('aria-label', `Lab Score: ${summary.total.toLocaleString('en-US')} out of ${summary.maximum.toLocaleString('en-US')}`);
    }
    if (scoreCompletion) scoreCompletion.textContent = `${summary.completed} of ${gameCount} experiments completed`;
    if (scorePercent) scorePercent.textContent = `${percentage}%`;
    if (scoreTrack) {
      scoreTrack.setAttribute('aria-valuemax', String(summary.maximum));
      scoreTrack.setAttribute('aria-valuenow', String(summary.total));
    }
    if (scoreFill) scoreFill.style.width = `${percentage}%`;

    if (scoreBreakdown) {
      const fragment = document.createDocumentFragment();
      games
        .filter((game) => progressSystem.GAME_IDS.includes(game.id))
        .sort((left, right) => left.number - right.number)
        .forEach((game) => fragment.appendChild(makeContribution(game, summary.games[game.id])));
      scoreBreakdown.replaceChildren(fragment);
      difficultySystem?.decorateLinks(scoreBreakdown);
    }

    if (scoreStatus) {
      const selectedLevel = difficultySystem?.current() || 'analyst';
      const selectedLabel = difficultySystem?.detail(selectedLevel).label || 'Analyst';
      if (reset) {
        scoreStatus.textContent = 'All personal records have been reset on this browser.';
      } else if (!summary.available) {
        scoreStatus.textContent = 'Browser storage is unavailable. Game results can be viewed, but personal records cannot be retained.';
      } else if (!summary.completed) {
        scoreStatus.textContent = selectedLevel === 'analyst'
          ? 'Complete an Analyst experiment to establish your first Lab Score contribution. Scores are stored only in this browser.'
          : `${selectedLabel} results keep separate records. Switch to Analyst to establish the official Lab Score.`;
      } else if (summary.completed === gameCount) {
        scoreStatus.textContent = 'All four experiments now contribute to your Lab Score. Improve any personal best to raise the total.';
      } else {
        scoreStatus.textContent = `${summary.completed} personal ${summary.completed === 1 ? 'record is' : 'records are'} active. Complete the remaining experiments to unlock the full 4,000-point scale.`;
      }
    }

    if (resetButton) resetButton.hidden = !summary.available || (!summary.completed && !hasLevelRecords);
  };

  const renderDaily = () => {
    if (!dailySystem) return;
    const loaded = dailySystem.loadRecord();
    const today = dailySystem.dayKey();
    const record = dailySystem.recordForDate(loaded.record, today);
    const completedToday = record.result?.date === today;
    if (dailyStreak) {
      const days = Number(record.currentStreak) || 0;
      dailyStreak.textContent = `${days} ${days === 1 ? 'day' : 'days'}`;
    }
    if (dailyStatus) {
      if (!loaded.available) {
        dailyStatus.textContent = 'Today’s case is ready. Browser storage is unavailable.';
      } else if (completedToday) {
        dailyStatus.textContent = `Completed today · ${record.result.score} / 500 pts`;
      } else {
        dailyStatus.textContent = 'Today’s case is ready.';
      }
    }
  };

  if (randomButton) {
    randomButton.addEventListener('click', () => {
      if (!playableUrls.length) return;
      const rawUrl = playableUrls[Math.floor(Math.random() * playableUrls.length)];
      const url = difficultySystem?.withLevel(rawUrl) || rawUrl;
      window.location.assign(url);
    });
  }

  if (resetButton) {
    resetButton.addEventListener('click', () => {
      if (!window.confirm('Reset all Impossible Lab game records at every difficulty on this browser?')) return;
      const progressCleared = progressSystem?.clear();
      const levelsCleared = difficultySystem?.clearRecords() ?? true;
      if (progressCleared && levelsCleared) renderScore(activeGames, true);
    });
  }

  document.addEventListener('impossiblelab:difficultychange', () => {
    document.querySelectorAll('[data-card-difficulty]').forEach((node) => {
      node.textContent = difficultySystem?.detail().label || 'Analyst';
    });
    render(activeGames);
    renderScore(activeGames);
  });

  renderDaily();
  renderScore(activeGames);

  fetch('lab-games.json', { cache: 'no-store', credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`Game registry returned ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      const games = Array.isArray(registry.games)
        ? registry.games.filter((game) => game && game.id && game.title && game.url && game.summary && game.duration && game.category && game.status === 'live')
        : [];
      if (games.length) {
        activeGames = games;
        render(games);
        renderScore(activeGames);
      }
    })
    .catch((error) => console.warn('Impossible Lab catalogue unavailable:', error));
})();
