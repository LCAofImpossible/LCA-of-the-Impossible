(() => {
  'use strict';
  const isEpisode = Boolean(document.body && document.body.dataset.episode);
  const script = document.createElement('script');
  script.src = `${isEpisode ? '../assets/' : 'assets/'}site-v2.js?v=20260816-6`;
  script.defer = true;
  document.head.appendChild(script);
})();
