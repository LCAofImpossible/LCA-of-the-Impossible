(() => {
  'use strict';

  const body = document.body;
  if (body.dataset.page !== 'season') return;

  const grid = document.getElementById('season-episode-grid');
  const count = document.getElementById('season-count');
  const loadMore = document.getElementById('season-load-more');
  const seasonId = body.dataset.seasonId || '';
  const rangeStart = Number(body.dataset.rangeStart);
  const rangeEnd = Number(body.dataset.rangeEnd);
  const pageSize = 9;
  let episodes = [];
  let visible = pageSize;

  const escapeHtml = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const card = (episode) => `
    <a class="card archive-card" href="${escapeHtml(episode.url)}">
      <img src="${escapeHtml(episode.cover)}" alt="${escapeHtml(episode.title)} cover" loading="lazy" decoding="async" width="1200" height="1500">
      <div class="card-copy">
        <p><span class="card-season">${escapeHtml(episode.seasonLabel)}</span><br>${escapeHtml(episode.categoryLabel)} · ${escapeHtml(episode.lcaLabel)}</p>
        <h3>${escapeHtml(episode.title)}</h3>
        <p class="card-subject">${escapeHtml(episode.subjectDescription)}</p>
        <div class="card-meta">
          <span>Episode #${Number(episode.number)}</span>
          <span>${escapeHtml(episode.result)}</span>
        </div>
        <span class="card-note">${escapeHtml(episode.hotspot)}</span>
        <strong class="card-cue">Explore the LCA →</strong>
      </div>
    </a>`;

  const render = () => {
    const shown = episodes.slice(0, visible);
    grid.innerHTML = shown.map(card).join('');
    const noun = episodes.length === 1 ? 'published episode' : 'published episodes';
    count.textContent = `${episodes.length} ${noun} · controlled range #${rangeStart}–${rangeEnd}`;
    loadMore.hidden = visible >= episodes.length;
    if (!loadMore.hidden) {
      loadMore.textContent = `Load more cases · ${shown.length} of ${episodes.length}`;
    }
  };

  const fail = () => {
    count.textContent = `Controlled range #${rangeStart}–${rangeEnd}`;
    grid.innerHTML = '<p class="season-error">The catalogue could not be loaded. Open the filtered archive to continue.</p>';
    loadMore.hidden = true;
  };

  loadMore.addEventListener('click', () => {
    visible += pageSize;
    render();
  });

  fetch('episodes.json', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Registry request failed: ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      const registered = Array.isArray(registry.episodes) ? registry.episodes : [];
      episodes = registered
        .filter((episode) => episode.seasonId === seasonId)
        .sort((a, b) => Number(b.number) - Number(a.number));
      if (!episodes.length) throw new Error(`No registered episodes for ${seasonId}`);
      render();
    })
    .catch(fail);
})();
