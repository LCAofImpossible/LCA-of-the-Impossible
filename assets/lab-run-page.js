(() => {
  'use strict';

  const page = document.querySelector('[data-lab-run-page]');
  const runSystem = window.ImpossibleLabRun;
  if (!page || !runSystem) return;

  const total = document.querySelector('[data-run-total]');
  const stateLabel = document.querySelector('[data-run-state]');
  const completion = document.querySelector('[data-run-completion]');
  const percent = document.querySelector('[data-run-percent]');
  const track = document.querySelector('[data-run-track]');
  const fill = document.querySelector('[data-run-fill]');
  const stages = document.querySelector('[data-run-stages]');
  const status = document.querySelector('[data-run-status]');
  const startButton = document.querySelector('[data-run-start]');
  const continueLink = document.querySelector('[data-run-continue]');
  const restartButton = document.querySelector('[data-run-restart]');
  const clearButton = document.querySelector('[data-run-clear]');
  let games = [];

  const fallbackGames = [...document.querySelectorAll('[data-run-stage]')].map((item, index) => ({
    id: item.dataset.gameId,
    number: index + 1,
    title: item.querySelector('h3')?.textContent || `Experiment ${index + 1}`,
    description: item.querySelector('p')?.textContent || '',
    url: item.querySelector('a')?.getAttribute('href') || ''
  })).filter((game) => game.id && game.url);

  const gameUrl = (game) => {
    const url = new URL(game.url, window.location.href);
    url.searchParams.set('run', '1');
    return `${url.pathname.split('/').pop()}${url.search}`;
  };

  const makeStage = (game, index, summary) => {
    const result = summary.results[game.id];
    const isNext = summary.active && summary.nextGameId === game.id;
    const item = document.createElement('article');
    item.className = `lab-run-stage${result ? ' is-complete' : ''}${isNext ? ' is-current' : ''}`;
    item.dataset.runStage = '';
    item.dataset.gameId = game.id;

    const number = document.createElement('span');
    number.className = 'lab-run-stage-number';
    number.textContent = String(index + 1).padStart(2, '0');

    const copy = document.createElement('div');
    const label = document.createElement('small');
    const title = document.createElement('h3');
    const description = document.createElement('p');
    label.textContent = result ? 'STAGE COMPLETE' : isNext ? 'NEXT STAGE' : 'PENDING';
    title.textContent = game.title;
    description.textContent = game.description;
    copy.append(label, title, description);

    const score = document.createElement('div');
    score.className = 'lab-run-stage-score';
    const scoreValue = document.createElement('strong');
    const scoreLabel = document.createElement('span');
    scoreValue.textContent = result ? result.normalized.toLocaleString('en-US') : '—';
    scoreLabel.textContent = result ? '/ 1,000 normalized' : 'Awaiting result';
    score.append(scoreValue, scoreLabel);

    const link = document.createElement(result || isNext ? 'a' : 'span');
    link.className = result || isNext ? '' : 'lab-run-stage-waiting';
    if (result || isNext) link.href = isNext ? gameUrl(game) : game.url;
    link.textContent = isNext ? 'Play this stage →' : result ? 'Play outside the Run →' : 'Complete previous stage';

    item.append(number, copy, score, link);
    return item;
  };

  const updateActionUrl = (summary) => {
    const next = games.find((game) => game.id === summary.nextGameId);
    if (continueLink) {
      continueLink.hidden = !summary.active || !next;
      if (next) continueLink.href = gameUrl(next);
    }
  };

  const render = (message = '') => {
    const summary = runSystem.summarize();
    const percentage = summary.maximum ? Math.round((summary.total / summary.maximum) * 100) : 0;

    if (total) {
      total.textContent = summary.total.toLocaleString('en-US');
      total.parentElement?.setAttribute('aria-label', `Run Score: ${summary.total.toLocaleString('en-US')} out of ${summary.maximum.toLocaleString('en-US')}`);
    }
    if (stateLabel) stateLabel.textContent = summary.complete ? 'RUN COMPLETE' : summary.active ? 'RUN IN PROGRESS' : 'READY TO START';
    if (completion) completion.textContent = `${summary.completed} of ${runSystem.GAME_IDS.length} stages complete`;
    if (percent) percent.textContent = `${percentage}%`;
    if (track) track.setAttribute('aria-valuenow', String(summary.total));
    if (fill) fill.style.width = `${percentage}%`;

    if (stages && games.length) {
      const fragment = document.createDocumentFragment();
      games
        .filter((game) => runSystem.GAME_IDS.includes(game.id))
        .sort((left, right) => left.number - right.number)
        .forEach((game, index) => fragment.appendChild(makeStage(game, index, summary)));
      stages.replaceChildren(fragment);
    }

    updateActionUrl(summary);
    if (startButton) {
      startButton.hidden = summary.active;
      startButton.disabled = !summary.available;
      startButton.textContent = summary.complete ? 'Start a new Run →' : 'Start the Run →';
    }
    if (restartButton) restartButton.hidden = !summary.active;
    if (clearButton) clearButton.hidden = summary.status === 'idle';

    if (status) {
      if (message) {
        status.textContent = message;
      } else if (!summary.available) {
        status.textContent = 'Browser storage is unavailable. The four-stage Run cannot continue between pages on this device.';
      } else if (summary.complete) {
        status.textContent = 'Run complete. This score combines one consecutive result from each game; your separate Lab Score still uses all-time personal bests.';
      } else if (summary.active) {
        status.textContent = `Stage ${summary.completed + 1} is ready. Complete it once to lock its normalized score into this Run.`;
      } else {
        status.textContent = 'Start a Run to play one complete round of each game in sequence.';
      }
    }
  };

  const start = (restart = false) => {
    if (restart && !window.confirm('Restart the current Impossible Lab Run? Its four-stage progress will be replaced.')) return;
    const started = runSystem.start();
    if (started.saved) {
      const first = games.find((game) => game.id === started.summary.nextGameId);
      if (first) {
        window.location.assign(gameUrl(first));
        return;
      }
    }
    render('The Run could not be started because its first stage is unavailable.');
  };

  startButton?.addEventListener('click', () => start(false));
  restartButton?.addEventListener('click', () => start(true));
  clearButton?.addEventListener('click', () => {
    if (!window.confirm('Exit and clear the current Impossible Lab Run? Personal game records and the Lab Score will be preserved.')) return;
    if (runSystem.clear()) render('Run cleared. Personal game records and the Lab Score were preserved.');
  });

  games = fallbackGames;
  render();

  fetch('lab-games.json', { cache: 'no-store', credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`Game registry returned ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      const registered = Array.isArray(registry.games)
        ? registry.games.filter((game) => game && game.id && game.number && game.title && game.description && game.url && game.status === 'live')
        : [];
      if (registered.length) {
        games = registered;
        render();
      }
    })
    .catch((error) => console.warn('Impossible Lab Run registry unavailable:', error));
})();
