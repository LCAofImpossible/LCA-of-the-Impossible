(() => {
  'use strict';

  const containers = [...document.querySelectorAll('[data-lab-game-nav]')];
  if (!containers.length) return;
  const currentGame = document.body.dataset.labGame || '';

  const render = (games) => {
    for (const container of containers) {
      const fragment = document.createDocumentFragment();
      games.sort((left, right) => left.number - right.number).forEach((game) => {
        const link = document.createElement('a');
        link.className = 'lab-game-link';
        link.href = game.url;
        link.dataset.gameId = game.id;
        if (game.id === currentGame) link.setAttribute('aria-current', 'page');

        const number = document.createElement('span');
        number.textContent = `EXPERIMENT ${String(game.number).padStart(2, '0')}`;
        const title = document.createElement('strong');
        title.textContent = game.title;
        const description = document.createElement('small');
        description.textContent = game.description;
        link.append(number, title, description);

        if (game.id === currentGame) {
          const status = document.createElement('em');
          status.textContent = 'Current';
          link.appendChild(status);
        } else if (game.status === 'preview') {
          const status = document.createElement('em');
          status.textContent = 'Preview';
          link.appendChild(status);
        }
        fragment.appendChild(link);
      });
      container.replaceChildren(fragment);
    }
  };

  fetch('lab-games.json', { cache: 'no-store', credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`Game registry returned ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      const games = Array.isArray(registry.games)
        ? registry.games.filter((game) => game && game.id && game.title && game.url && game.status !== 'retired')
        : [];
      if (games.length) render(games);
    })
    .catch((error) => console.warn('Impossible Lab navigation unavailable:', error));
})();
