(() => {
  'use strict';

  const body = document.body;
  const isEpisode = Boolean(body.dataset.episode);
  const registryPath = isEpisode ? '../episodes.json' : 'episodes.json';
  const rootPrefix = isEpisode ? '../' : '';
  const rawAssetBase = 'https://raw.githubusercontent.com/LCAofImpossible/LCA-of-the-Impossible/main/';

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const cleanAssetPath = (value = '') => String(value)
    .split('?')[0]
    .replace(/^https?:\/\/raw\.githubusercontent\.com\/LCAofImpossible\/LCA-of-the-Impossible\/main\//, '')
    .replace(/^(\.\.\/)+/, '')
    .replace(/^\.\//, '')
    .replace(/^\//, '');

  const rawAssetUrl = (value = '') => {
    const path = cleanAssetPath(value);
    return `${rawAssetBase}${path}?rev=20260816-coverfix`;
  };

  const isEpisodeCoverPath = (value = '') => cleanAssetPath(value).startsWith('assets/images/episodes/');

  const coverUrl = (value = '') => {
    const stringValue = String(value);
    if (stringValue.startsWith('data:')) return stringValue;
    if (isEpisodeCoverPath(stringValue)) return rawAssetUrl(stringValue);
    if (/^https?:\/\//i.test(stringValue)) return stringValue;
    return `${rootPrefix}${stringValue}`;
  };

  const fallbackImage = (img) => {
    if (!img || img.dataset.rawFallbackApplied === 'true') return;
    const source = img.getAttribute('src') || '';
    if (!source || source.startsWith('data:') || source.includes('raw.githubusercontent.com')) return;
    const clean = cleanAssetPath(source);
    if (!clean.startsWith('assets/')) return;
    img.dataset.rawFallbackApplied = 'true';
    img.src = rawAssetUrl(clean);
  };

  document.addEventListener('error', (event) => {
    const target = event.target;
    if (target && target.tagName === 'IMG') fallbackImage(target);
  }, true);

  const forceCanonicalCoverSources = () => {
    document.querySelectorAll('.cover-frame img').forEach((img) => {
      const source = img.getAttribute('src') || '';
      if (isEpisodeCoverPath(source) && !source.includes('raw.githubusercontent.com')) {
        img.src = rawAssetUrl(source);
      }
    });

    document.querySelectorAll('img').forEach((img) => {
      if (img.complete && img.naturalWidth === 0) fallbackImage(img);
    });
  };

  forceCanonicalCoverSources();
  window.setTimeout(forceCanonicalCoverSources, 250);

  const tokenLabels = {
    mythology: 'Mythology',
    legends: 'Legends',
    structures: 'Structures',
    'science-fiction': 'Science Fiction',
    fantasy: 'Fantasy',
    'operation-driven': 'Operation-driven',
    'materials-driven': 'Materials-driven',
    'energy-driven': 'Energy-driven',
    'mobility-driven': 'Mobility-driven',
    'process-energy-driven': 'Process-energy-driven',
    'repetition-sensitive': 'Repetition-sensitive',
    'lifetime-sensitive': 'Lifetime-sensitive',
    'proxy-sensitive': 'Proxy-sensitive'
  };

  const labelFor = (token) => tokenLabels[token] || token
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  const pageUrl = (episodeUrl = '') => {
    if (/^https?:\/\//i.test(episodeUrl)) return episodeUrl;
    return `${rootPrefix}${episodeUrl}`;
  };

  const episodeCard = (episode, compact = false) => {
    const category = escapeHtml(episode.categoryLabel);
    const lca = escapeHtml(episode.lcaLabel);
    return `
      <a class="card archive-card${compact ? ' compact-card' : ''}" href="${escapeHtml(pageUrl(episode.url))}">
        <img src="${escapeHtml(coverUrl(episode.cover))}" alt="${escapeHtml(episode.title)} cover" loading="lazy" decoding="async">
        <div class="card-copy">
          <p>${category} · ${lca}</p>
          <h3>${escapeHtml(episode.title)}</h3>
          <div class="card-meta">
            <span>Episode #${episode.number}</span>
            <span>${escapeHtml(episode.result)}</span>
          </div>
          <span class="card-note">${escapeHtml(episode.hotspot)}</span>
          <strong class="card-cue">Explore the LCA →</strong>
        </div>
      </a>`;
  };

  const renderHome = (episodes) => {
    const latest = episodes[0];
    const latestTarget = document.getElementById('latest-case');
    const recentTarget = document.getElementById('recent-episodes');
    if (!latest || !latestTarget || !recentTarget) return;

    latestTarget.innerHTML = `
      <div class="featured-cover">
        <img src="${escapeHtml(coverUrl(latest.cover))}" alt="${escapeHtml(latest.title)} cover">
      </div>
      <div class="featured-copy">
        <p class="eyebrow">LATEST CASE · EPISODE #${latest.number}</p>
        <h3>${escapeHtml(latest.title)}</h3>
        <p>${escapeHtml(latest.featuredDescription)}</p>
        <div class="badge-row">
          <span class="badge">${escapeHtml(latest.result)}</span>
          <span class="badge">${escapeHtml(latest.lcaLabel)}</span>
          <span class="badge">${escapeHtml(latest.categoryLabel)}</span>
        </div>
        <a class="button" href="${escapeHtml(pageUrl(latest.url))}">Explore the LCA →</a>
      </div>`;

    recentTarget.innerHTML = episodes.slice(1, 7).map((episode) => episodeCard(episode)).join('');
  };

  const renderArchive = (episodes) => {
    const grid = document.getElementById('episode-grid');
    const search = document.getElementById('episode-search');
    const count = document.getElementById('archive-count');
    const empty = document.getElementById('archive-empty');
    const loadMore = document.getElementById('load-more');
    const categoryFilters = document.getElementById('category-filters');
    const lcaFilters = document.getElementById('lca-filters');
    if (!grid || !search || !count || !empty || !loadMore || !categoryFilters || !lcaFilters) return;

    const categories = [...new Set(episodes.flatMap((episode) => episode.categories))];
    const lcaCharacteristics = [...new Set(episodes.flatMap((episode) => episode.lcaCharacteristics))];
    let activeCategory = 'all';
    let activeLca = 'all';
    let visibleLimit = 9;

    const makeButtons = (tokens, group, allLabel) => {
      const all = `<button class="filter-button active" type="button" data-group="${group}" data-filter="all" aria-pressed="true">${allLabel}</button>`;
      const rest = tokens.map((token) => `<button class="filter-button" type="button" data-group="${group}" data-filter="${escapeHtml(token)}" aria-pressed="false">${escapeHtml(labelFor(token))}</button>`).join('');
      return all + rest;
    };

    categoryFilters.innerHTML = makeButtons(categories, 'category', 'All subjects');
    lcaFilters.innerHTML = makeButtons(lcaCharacteristics, 'lca', 'All LCA lenses');

    const searchableText = (episode) => [
      episode.title,
      `episode ${episode.number}`,
      episode.categoryLabel,
      episode.lcaLabel,
      ...episode.categories,
      ...episode.lcaCharacteristics,
      ...episode.keywords
    ].join(' ').toLowerCase();

    const applyArchive = () => {
      const query = search.value.trim().toLowerCase();
      const matches = episodes.filter((episode) => {
        const categoryMatch = activeCategory === 'all' || episode.categories.includes(activeCategory);
        const lcaMatch = activeLca === 'all' || episode.lcaCharacteristics.includes(activeLca);
        const textMatch = !query || searchableText(episode).includes(query);
        return categoryMatch && lcaMatch && textMatch;
      });

      grid.innerHTML = matches.slice(0, visibleLimit).map((episode) => episodeCard(episode)).join('');
      count.textContent = `${matches.length} ${matches.length === 1 ? 'episode' : 'episodes'}`;
      empty.hidden = matches.length !== 0;
      loadMore.hidden = matches.length <= visibleLimit;
    };

    const selectFilter = (button) => {
      const group = button.dataset.group;
      const value = button.dataset.filter;
      const container = group === 'category' ? categoryFilters : lcaFilters;
      container.querySelectorAll('.filter-button').forEach((item) => {
        const selected = item === button;
        item.classList.toggle('active', selected);
        item.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
      if (group === 'category') activeCategory = value;
      if (group === 'lca') activeLca = value;
      visibleLimit = 9;
      applyArchive();
    };

    [categoryFilters, lcaFilters].forEach((container) => {
      container.addEventListener('click', (event) => {
        const button = event.target.closest('.filter-button');
        if (button) selectFilter(button);
      });
    });

    search.addEventListener('input', () => {
      visibleLimit = 9;
      applyArchive();
    });

    loadMore.addEventListener('click', () => {
      visibleLimit += 9;
      applyArchive();
    });

    applyArchive();
  };

  const renderEpisodeNavigation = (episodes) => {
    const currentNumber = Number(body.dataset.episode);
    const currentIndex = episodes.findIndex((episode) => episode.number === currentNumber);
    if (currentIndex < 0) return;

    const current = episodes[currentIndex];
    const older = episodes[currentIndex + 1] || null;
    const newer = episodes[currentIndex - 1] || null;
    const header = document.querySelector('.site-header');
    const main = document.querySelector('main');
    if (!header || !main) return;

    const subject = main.querySelector(':scope > .split');
    const model = main.querySelector('.episode-visual-section');
    const inventory = document.getElementById('inventory');
    const hotspot = main.querySelector('.hotspot-visual-section');
    const results = document.getElementById('results');
    const verdict = main.querySelector('.verdict');

    if (subject) subject.id = subject.id || 'subject';
    if (model) model.id = model.id || 'model';
    if (hotspot) hotspot.id = hotspot.id || 'hotspot';
    if (verdict) verdict.id = verdict.id || 'verdict';

    const jumpLinks = [
      ['subject', 'Subject', subject],
      ['model', 'Model', model],
      ['inventory', 'Inventory', inventory],
      ['hotspot', 'Hotspots', hotspot],
      ['results', 'Results', results],
      ['verdict', 'Verdict', verdict]
    ].filter(([, , element]) => Boolean(element));

    const jumpNav = document.createElement('nav');
    jumpNav.className = 'episode-jumpnav';
    jumpNav.setAttribute('aria-label', 'Episode sections');
    jumpNav.innerHTML = `<div class="episode-jumpnav-inner">${jumpLinks.map(([id, label]) => `<a href="#${id}">${label}</a>`).join('')}</div>`;
    header.insertAdjacentElement('afterend', jumpNav);

    const relatedEpisodes = (current.related || [])
      .map((number) => episodes.find((episode) => episode.number === number))
      .filter(Boolean)
      .slice(0, 3);

    if (relatedEpisodes.length && verdict) {
      const relatedSection = document.createElement('section');
      relatedSection.className = 'section related-section small-section-title';
      relatedSection.innerHTML = `
        <div class="section-heading">
          <div><p class="eyebrow">KEEP EXPLORING</p><h2>Related cases</h2></div>
          <p class="section-note">Cases connected by subject, system behaviour or LCA hotspot.</p>
        </div>
        <div class="cards episode-grid related-grid">${relatedEpisodes.map((episode) => episodeCard(episode, true)).join('')}</div>`;
      verdict.insertAdjacentElement('afterend', relatedSection);
    }

    const pager = document.createElement('section');
    pager.className = 'episode-pager';
    pager.setAttribute('aria-label', 'Episode navigation');
    pager.innerHTML = `
      ${older ? `<a class="pager-link pager-prev" href="${escapeHtml(pageUrl(older.url))}"><span>← Previous episode</span><strong>#${older.number} · ${escapeHtml(older.title)}</strong></a>` : '<span class="pager-link pager-placeholder"></span>'}
      <a class="pager-archive" href="${rootPrefix}archive.html">Full archive</a>
      ${newer ? `<a class="pager-link pager-next" href="${escapeHtml(pageUrl(newer.url))}"><span>Next episode →</span><strong>#${newer.number} · ${escapeHtml(newer.title)}</strong></a>` : '<span class="pager-link pager-placeholder"></span>'}`;
    main.appendChild(pager);
  };

  fetch(registryPath)
    .then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    })
    .then((data) => {
      const episodes = [...data.episodes].sort((a, b) => b.number - a.number);
      if (body.dataset.page === 'home') renderHome(episodes);
      if (body.dataset.page === 'archive') renderArchive(episodes);
      if (isEpisode) renderEpisodeNavigation(episodes);
      forceCanonicalCoverSources();
    })
    .catch((error) => {
      console.error('Unable to load episode registry:', error);
      document.querySelectorAll('[data-registry-status]').forEach((node) => {
        node.textContent = 'Episode catalogue is temporarily unavailable.';
      });
    });
})();