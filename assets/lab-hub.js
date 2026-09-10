(() => {
  'use strict';

  const grid = document.querySelector('[data-lab-hub-grid]');
  const randomButton = document.querySelector('[data-random-game]');
  if (!grid) return;

  let playableUrls = [...grid.querySelectorAll('.lab-hub-card')].map((card) => card.getAttribute('href')).filter(Boolean);

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
    metadata.append(makeMeta('Challenge', game.category), makeMeta('Duration', game.duration));

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
    playableUrls = games.map((game) => game.url);
  };

  if (randomButton) {
    randomButton.addEventListener('click', () => {
      if (!playableUrls.length) return;
      const url = playableUrls[Math.floor(Math.random() * playableUrls.length)];
      window.location.assign(url);
    });
  }

  fetch('lab-games.json', { cache: 'no-store', credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`Game registry returned ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      const games = Array.isArray(registry.games)
        ? registry.games.filter((game) => game && game.id && game.title && game.url && game.summary && game.duration && game.category && game.status === 'live')
        : [];
      if (games.length) render(games);
    })
    .catch((error) => console.warn('Impossible Lab catalogue unavailable:', error));
})();
