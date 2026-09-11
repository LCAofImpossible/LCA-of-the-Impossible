(() => {
  'use strict';

  const buttons = [...document.querySelectorAll('[data-lab-another]')];
  if (!buttons.length) return;

  const currentGame = document.body.dataset.labGame || '';
  let registryRequest;

  const loadAlternatives = () => {
    if (!registryRequest) {
      registryRequest = fetch('lab-games.json', { cache: 'no-store', credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw new Error(`Game registry returned ${response.status}`);
          return response.json();
        })
        .then((registry) => (Array.isArray(registry.games) ? registry.games : [])
          .filter((game) => game && game.id !== currentGame && game.url && game.status === 'live'));
    }
    return registryRequest;
  };

  buttons.forEach((button) => {
    button.addEventListener('click', async () => {
      button.disabled = true;
      button.setAttribute('aria-busy', 'true');
      try {
        const alternatives = await loadAlternatives();
        if (!alternatives.length) throw new Error('No alternative live game is available');
        const selected = alternatives[Math.floor(Math.random() * alternatives.length)];
        window.location.assign(window.ImpossibleLabDifficulty?.withLevel(selected.url) || selected.url);
      } catch (error) {
        console.warn('Impossible Lab game selection unavailable:', error);
        window.location.assign('impossible-lab.html');
      }
    });
  });
})();
