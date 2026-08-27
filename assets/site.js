(() => {
  'use strict';

  const body = document.body;
  const isEpisode = Boolean(body && body.dataset.episode);
  const registryPath = isEpisode ? '../episodes.json' : 'episodes.json';
  const rootPrefix = isEpisode ? '../' : '';
  const compareStorageKey = 'lcaImpossibleCompare';

  const featureStyles = document.createElement('link');
  featureStyles.rel = 'stylesheet';
  featureStyles.href = `${rootPrefix}assets/features.css?v=20260816-phase3`;
  document.head.appendChild(featureStyles);

  const ensureAccessibilityScaffold = () => {
    const main = document.querySelector('main');
    if (main) {
      if (!main.id) main.id = 'main-content';
      if (!main.hasAttribute('tabindex')) main.setAttribute('tabindex', '-1');
    }

    if (main && !document.querySelector('.skip-link')) {
      const skipLink = document.createElement('a');
      skipLink.className = 'skip-link';
      skipLink.href = '#main-content';
      skipLink.textContent = 'Skip to content';
      body.insertBefore(skipLink, body.firstChild);
    }

    const primaryNav = document.querySelector('.site-header nav');
    if (primaryNav && !primaryNav.hasAttribute('aria-label')) {
      primaryNav.setAttribute('aria-label', 'Primary navigation');
    }
  };

  ensureAccessibilityScaffold();

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const tokenLabels = {
    mythology: 'Mythology',
    legends: 'Legends',
    structures: 'Structures',
    'science-fiction': 'Science Fiction',
    machines: 'Machines',
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

  const pageUrl = (value = '') => {
    const stringValue = String(value);
    if (/^https?:\/\//i.test(stringValue)) return stringValue;
    return `${rootPrefix}${stringValue}`;
  };

  const assetUrl = (value = '') => {
    const stringValue = String(value);
    if (stringValue.startsWith('data:') || /^https?:\/\//i.test(stringValue)) return stringValue;
    return `${rootPrefix}${stringValue}`;
  };

  const seasonLabel = (episode, fallback = '') => String(episode?.seasonLabel || fallback).trim();

  const loadCompareSelection = () => {
    try {
      const parsed = JSON.parse(sessionStorage.getItem(compareStorageKey) || '[]');
      return new Set((Array.isArray(parsed) ? parsed : []).map(Number).filter(Number.isFinite).slice(0, 3));
    } catch (_) {
      return new Set();
    }
  };

  const saveCompareSelection = (selected) => {
    try {
      sessionStorage.setItem(compareStorageKey, JSON.stringify([...selected].slice(0, 3)));
    } catch (_) {
      // Session storage is an enhancement only.
    }
  };

  const episodeCard = (episode, options = {}) => {
    const compact = Boolean(options.compact);
    const showCover = options.showCover !== false;
    const compareEnabled = Boolean(options.compareEnabled);
    const selected = options.selected instanceof Set ? options.selected.has(episode.number) : false;
    const category = escapeHtml(episode.categoryLabel);
    const lca = escapeHtml(episode.lcaLabel);
    const season = seasonLabel(episode);
    const coverMarkup = showCover
      ? `<img src="${escapeHtml(assetUrl(episode.cover))}" alt="${escapeHtml(episode.title)} cover" loading="lazy" decoding="async" width="1200" height="1500">`
      : '';
    const copyMarkup = `
        <div class="card-copy">
          <p>${season ? `<span class="card-season">${escapeHtml(season)}</span><br>` : ''}${category} · ${lca}</p>
          <h3>${escapeHtml(episode.title)}</h3>
          <div class="card-meta">
            <span>Episode #${episode.number}</span>
            <span>${escapeHtml(episode.result)}</span>
          </div>
          <span class="card-note">${escapeHtml(episode.hotspot)}</span>
          <strong class="card-cue">Explore the LCA →</strong>
        </div>`;

    if (compareEnabled) {
      return `
        <article class="card archive-card compare-card" data-card-episode="${episode.number}">
          <a class="card-main-link" href="${escapeHtml(pageUrl(episode.url))}">
            ${coverMarkup}
            ${copyMarkup}
          </a>
          <div class="card-actions">
            <button class="compare-toggle${selected ? ' active' : ''}" type="button" data-compare-episode="${episode.number}" aria-pressed="${selected ? 'true' : 'false'}">${selected ? '✓ Selected' : '+ Compare'}</button>
          </div>
        </article>`;
    }

    return `
      <a class="card archive-card${compact ? ' compact-card' : ''}${showCover ? '' : ' text-only-card'}" href="${escapeHtml(pageUrl(episode.url))}">
        ${coverMarkup}
        ${copyMarkup}
      </a>`;
  };

  const addFeatureEntryPoints = () => {
    if (body.dataset.page === 'home') {
      const row = document.querySelector('#series .cta-row');
      if (row && !row.querySelector('[data-phase3-link]')) {
        row.insertAdjacentHTML('beforeend', `
          <a class="button secondary" data-phase3-link href="compare.html">Compare cases →</a>
          <a class="button secondary" data-phase3-link href="explore.html">Explore impact scale →</a>`);
      }
    }

    if (isEpisode) {
      const nav = document.querySelector('.site-header nav');
      if (nav && !nav.querySelector('[data-phase3-link]')) {
        nav.insertAdjacentHTML('beforeend', `<a data-phase3-link href="${rootPrefix}compare.html">Compare</a><a data-phase3-link href="${rootPrefix}explore.html">Impact map</a>`);
      }
    }
  };

  addFeatureEntryPoints();

  const renderHome = (episodes) => {
    const latest = episodes[0];
    const latestTarget = document.getElementById('latest-case');
    const recentTarget = document.getElementById('recent-episodes');
    if (!latest || !latestTarget || !recentTarget) return;

    latestTarget.innerHTML = `
      <div class="featured-cover">
        <img src="${escapeHtml(assetUrl(latest.cover))}" alt="${escapeHtml(latest.title)} cover" width="1200" height="1500">
      </div>
      <div class="featured-copy">
        <p class="eyebrow">LATEST CASE · EPISODE #${latest.number}${seasonLabel(latest) ? ` · ${escapeHtml(seasonLabel(latest))}` : ''}</p>
        <h3>${escapeHtml(latest.title)}</h3>
        <p>${escapeHtml(latest.featuredDescription)}</p>
        <div class="badge-row">
          <span class="badge">${escapeHtml(latest.result)}</span>
          <span class="badge">${escapeHtml(latest.lcaLabel)}</span>
          <span class="badge">${escapeHtml(latest.categoryLabel)}</span>
        </div>
        <a class="button" href="${escapeHtml(pageUrl(latest.url))}">Explore the LCA →</a>
      </div>`;

    recentTarget.innerHTML = episodes.slice(1, 7)
      .map((episode) => episodeCard(episode, { showCover: true }))
      .join('');
  };

  const renderSeasonSpotlight = (episodes) => {
    const target = document.getElementById('season-i-episodes');
    if (!target) return;
    const seasonEpisodes = episodes
      .filter((episode) => episode.seasonId === 'season-i')
      .sort((a, b) => b.number - a.number);
    const episode = seasonEpisodes[0];
    if (!episode) {
      target.innerHTML = '<p class="section-note">Season I cases are being prepared.</p>';
      return;
    }
    target.innerHTML = `
      <div class="featured-cover">
        <img src="${escapeHtml(assetUrl(episode.cover))}" alt="${escapeHtml(episode.title)} — ${escapeHtml(episode.seasonLabel)} cover" width="1200" height="1500">
      </div>
      <div class="featured-copy">
        <p class="eyebrow">${escapeHtml(episode.seasonLabel)} · EPISODE #${episode.number}</p>
        <h3>${escapeHtml(episode.title)}</h3>
        <p>${escapeHtml(episode.seasonDescriptor)}</p>
        <p>${escapeHtml(episode.featuredDescription)}</p>
        <div class="badge-row">
          <span class="badge">${escapeHtml(episode.result)}</span>
          <span class="badge">${escapeHtml(episode.lcaLabel)}</span>
          <span class="badge">${escapeHtml(episode.categoryLabel)}</span>
        </div>
        <div class="cta-row">
          <a class="button" href="${escapeHtml(pageUrl(episode.url))}">Explore episode →</a>
          <a class="button secondary" href="${escapeHtml(pageUrl('archive.html?season=season-i'))}">Browse Season I →</a>
        </div>
      </div>`;
  };

  const renderArchive = (episodes) => {
    const grid = document.getElementById('episode-grid');
    const search = document.getElementById('episode-search');
    const count = document.getElementById('archive-count');
    const empty = document.getElementById('archive-empty');
    const loadMore = document.getElementById('load-more');
    const categoryFilters = document.getElementById('category-filters');
    const lcaFilters = document.getElementById('lca-filters');
    const seasonFilters = document.getElementById('season-filters');
    if (!grid || !search || !count || !empty || !loadMore || !categoryFilters || !lcaFilters || !seasonFilters) return;

    const toolbar = document.querySelector('.archive-toolbar');
    if (toolbar && !document.querySelector('.archive-feature-entrypoints')) {
      toolbar.insertAdjacentHTML('beforebegin', `
        <div class="archive-feature-entrypoints">
          <div><p class="eyebrow">EXPLORE THE SERIES</p><p class="section-note">Compare modelling choices side by side or place every headline result on a logarithmic impact scale.</p></div>
          <div class="cta-row"><a class="button secondary" href="compare.html">Compare cases →</a><a class="button secondary" href="explore.html">Impact map →</a></div>
        </div>`);
    }

    const categories = [...new Set(episodes.flatMap((episode) => episode.categories || []))];
    const lcaCharacteristics = [...new Set(episodes.flatMap((episode) => episode.lcaCharacteristics || []))];
    const seasons = [...new Map(episodes
      .filter((episode) => episode.seasonId && episode.seasonLabel)
      .map((episode) => [episode.seasonId, {
        id: episode.seasonId,
        label: episode.seasonLabel,
        number: Number.isFinite(episode.seasonNumber) ? episode.seasonNumber : Number.MAX_SAFE_INTEGER
      }])).values()]
      .sort((a, b) => a.number - b.number || a.label.localeCompare(b.label));
    const knownSeasonIds = new Set(seasons.map((season) => season.id));
    const seasonCounts = new Map(seasons.map((season) => [
      season.id,
      episodes.filter((episode) => episode.seasonId === season.id).length
    ]));
    const seasonFromUrl = () => {
      const requested = new URLSearchParams(window.location.search).get('season');
      return requested && knownSeasonIds.has(requested) ? requested : 'all';
    };
    let activeCategory = 'all';
    let activeLca = 'all';
    let activeSeason = seasonFromUrl();
    let visibleLimit = 9;
    const selected = loadCompareSelection();

    const makeButtons = (tokens, group, allLabel) => {
      const all = `<button class="filter-button active" type="button" data-group="${group}" data-filter="all" aria-pressed="true">${allLabel}</button>`;
      const rest = tokens.map((token) => `<button class="filter-button" type="button" data-group="${group}" data-filter="${escapeHtml(token)}" aria-pressed="false">${escapeHtml(labelFor(token))}</button>`).join('');
      return all + rest;
    };

    categoryFilters.innerHTML = makeButtons(categories, 'category', 'All subjects');
    lcaFilters.innerHTML = makeButtons(lcaCharacteristics, 'lca', 'All LCA lenses');
    const countLabel = (value) => `${value} ${value === 1 ? 'episode' : 'episodes'}`;
    const seasonButton = (id, label, total) => {
      const isActive = activeSeason === id;
      return `<button class="filter-button${isActive ? ' active' : ''}" type="button" data-group="season" data-filter="${escapeHtml(id)}" aria-pressed="${isActive ? 'true' : 'false'}" aria-label="${escapeHtml(label)}, ${countLabel(total)}">${escapeHtml(label)} <span class="filter-count" aria-hidden="true">${total}</span></button>`;
    };
    seasonFilters.innerHTML = seasonButton('all', 'All seasons', episodes.length)
      + seasons.map(({ id, label }) => seasonButton(id, label, seasonCounts.get(id) || 0)).join('');

    const writeSeasonToUrl = (mode = 'push') => {
      const url = new URL(window.location.href);
      if (activeSeason === 'all') url.searchParams.delete('season');
      else url.searchParams.set('season', activeSeason);
      if (url.href === window.location.href) return;
      const method = mode === 'replace' ? 'replaceState' : 'pushState';
      window.history[method]({ season: activeSeason }, '', `${url.pathname}${url.search}${url.hash}`);
    };

    const syncSeasonButtons = () => {
      seasonFilters.querySelectorAll('.filter-button').forEach((item) => {
        const isSelected = item.dataset.filter === activeSeason;
        item.classList.toggle('active', isSelected);
        item.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
      });
    };

    const requestedSeason = new URLSearchParams(window.location.search).get('season');
    if (requestedSeason && !knownSeasonIds.has(requestedSeason)) writeSeasonToUrl('replace');

    const searchableText = (episode) => [
      episode.title,
      `episode ${episode.number}`,
      episode.result,
      episode.hotspot,
      episode.featuredDescription,
      episode.functionalUnit,
      episode.evidence?.basis,
      episode.evidence?.uncertainty,
      episode.categoryLabel,
      episode.lcaLabel,
      episode.seasonId,
      episode.seasonLabel,
      episode.seasonTitle,
      episode.seasonDescriptor,
      episode.editorialDescriptor,
      ...(episode.categories || []),
      ...(episode.lcaCharacteristics || []),
      ...(episode.taxonomy || []),
      ...(episode.collectionSlugs || []),
      ...(episode.keywords || [])
    ].join(' ').toLowerCase();

    const compareBar = document.createElement('div');
    compareBar.className = 'compare-bar';
    compareBar.hidden = true;
    compareBar.setAttribute('aria-live', 'polite');
    body.appendChild(compareBar);

    const updateCompareBar = () => {
      const chosen = [...selected]
        .map((number) => episodes.find((episode) => episode.number === number))
        .filter(Boolean)
        .slice(0, 3);
      compareBar.hidden = chosen.length === 0;
      if (!chosen.length) return;
      const query = chosen.map((episode) => episode.number).join(',');
      compareBar.innerHTML = `
        <div class="compare-bar-copy"><strong>${chosen.length}/3 selected</strong><span>${chosen.map((episode) => escapeHtml(episode.title)).join(' · ')}</span></div>
        <div class="compare-bar-actions">
          <button class="compare-clear" type="button">Clear</button>
          <a class="button" href="compare.html?cases=${query}">${chosen.length >= 2 ? 'Compare now →' : 'Select one more case'}</a>
        </div>`;
      const link = compareBar.querySelector('a.button');
      if (link && chosen.length < 2) {
        link.setAttribute('aria-disabled', 'true');
        link.addEventListener('click', (event) => event.preventDefault(), { once: true });
      }
      compareBar.querySelector('.compare-clear')?.addEventListener('click', () => {
        selected.clear();
        saveCompareSelection(selected);
        applyArchive();
      });
    };

    const applyArchive = () => {
      const query = search.value.trim().toLowerCase();
      const matches = episodes.filter((episode) => {
        const categoryMatch = activeCategory === 'all' || (episode.categories || []).includes(activeCategory);
        const lcaMatch = activeLca === 'all' || (episode.lcaCharacteristics || []).includes(activeLca);
        const seasonMatch = activeSeason === 'all' || episode.seasonId === activeSeason;
        const textMatch = !query || searchableText(episode).includes(query);
        return categoryMatch && lcaMatch && seasonMatch && textMatch;
      });

      grid.innerHTML = matches.slice(0, visibleLimit)
        .map((episode) => episodeCard(episode, { showCover: true, compareEnabled: true, selected }))
        .join('');
      const selectedSeason = seasons.find((season) => season.id === activeSeason);
      count.textContent = `${countLabel(matches.length)}${selectedSeason ? ` · ${selectedSeason.label}` : ''}`;
      empty.hidden = matches.length !== 0;
      loadMore.hidden = matches.length <= visibleLimit;
      updateCompareBar();
    };

    const selectFilter = (button) => {
      const group = button.dataset.group;
      const value = button.dataset.filter;
      const container = group === 'category' ? categoryFilters : group === 'lca' ? lcaFilters : seasonFilters;
      container.querySelectorAll('.filter-button').forEach((item) => {
        const isSelected = item === button;
        item.classList.toggle('active', isSelected);
        item.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
      });
      if (group === 'category') activeCategory = value;
      if (group === 'lca') activeLca = value;
      if (group === 'season') {
        activeSeason = value;
        writeSeasonToUrl();
      }
      visibleLimit = 9;
      applyArchive();
    };

    [seasonFilters, categoryFilters, lcaFilters].forEach((container) => {
      container.addEventListener('click', (event) => {
        const button = event.target.closest('.filter-button');
        if (button) selectFilter(button);
      });
    });

    grid.addEventListener('click', (event) => {
      const button = event.target.closest('.compare-toggle');
      if (!button) return;
      const number = Number(button.dataset.compareEpisode);
      if (selected.has(number)) {
        selected.delete(number);
      } else if (selected.size < 3) {
        selected.add(number);
      } else {
        compareBar.hidden = false;
        compareBar.innerHTML = '<div class="compare-bar-copy"><strong>Maximum 3 cases</strong><span>Remove one selected case before adding another.</span></div>';
        return;
      }
      saveCompareSelection(selected);
      applyArchive();
    });

    search.addEventListener('input', () => {
      visibleLimit = 9;
      applyArchive();
    });

    window.addEventListener('popstate', () => {
      activeSeason = seasonFromUrl();
      syncSeasonButtons();
      visibleLimit = 9;
      applyArchive();
    });

    loadMore.addEventListener('click', () => {
      visibleLimit += 9;
      applyArchive();
    });

    applyArchive();
  };

  const renderEvidenceProfile = (episode) => {
    const evidence = episode.evidence;
    const quickFacts = document.querySelector('.episode-quickfacts');
    if (!evidence || !quickFacts || document.getElementById('evidence')) return;

    const section = document.createElement('section');
    section.id = 'evidence';
    section.className = 'section evidence-section small-section-title';
    section.innerHTML = `
      <div class="section-heading">
        <div><p class="eyebrow">EVIDENCE PROFILE</p><h2>How much of the impossible is reconstructed?</h2></div>
        <p class="section-note">Qualitative editorial indicators — not a formal LCA data-quality rating.</p>
      </div>
      <div class="evidence-grid">
        <article class="evidence-card"><span>Evidence confidence</span><strong>${escapeHtml(evidence.confidence)}</strong><p>Strength of the narrative, historical or physical basis used to constrain the reconstruction.</p></article>
        <article class="evidence-card"><span>Proxy dependence</span><strong>${escapeHtml(evidence.proxyDependence)}</strong><p>How strongly the result depends on modern emission factors or analogue processes standing in for impossible conditions.</p></article>
        <article class="evidence-card"><span>Assumption sensitivity</span><strong>${escapeHtml(evidence.assumptionSensitivity)}</strong><p>How strongly the interpretation can move when key engineering assumptions or boundaries are changed.</p></article>
      </div>
      <div class="evidence-details">
        <details open><summary>Evidence basis</summary><p>${escapeHtml(evidence.basis)}</p></details>
        <details><summary>Main modelling uncertainty</summary><p>${escapeHtml(evidence.uncertainty)}</p></details>
        <details><summary>Audit-trail principle</summary><p>The episode result remains tied to its own functional unit and assumptions. These indicators help explain modelling confidence; they do not make unlike cases directly comparable.</p></details>
      </div>`;
    quickFacts.insertAdjacentElement('afterend', section);
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

    const heroEyebrow = main.querySelector('.episode-title .eyebrow');
    if (heroEyebrow && current.seasonLabel) {
      heroEyebrow.textContent = `EPISODE #${current.number} · ${String(current.seasonLabel).toUpperCase()}`;
    }

    const subject = main.querySelector(':scope > .split');
    const evidence = document.getElementById('evidence');
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
      ['evidence', 'Evidence', evidence],
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
        <div class="cards episode-grid related-grid">${relatedEpisodes.map((episode) => episodeCard(episode, { compact: true, showCover: false })).join('')}</div>`;
      verdict.insertAdjacentElement('afterend', relatedSection);
    }

    const pager = document.createElement('section');
    pager.className = 'episode-pager';
    pager.setAttribute('aria-label', 'Episode navigation');
    pager.innerHTML = `
      ${older ? `<a class="pager-link pager-prev" href="${escapeHtml(pageUrl(older.url))}"><span>← Previous episode</span><strong>#${older.number} · ${escapeHtml(older.title)}</strong></a>` : '<span class="pager-link pager-placeholder"></span>'}
      <a class="pager-archive" href="${rootPrefix}archive.html">Full archive${current.seasonLabel ? `<span class="pager-archive-season">${escapeHtml(current.seasonLabel)}</span>` : ''}</a>
      ${newer ? `<a class="pager-link pager-next" href="${escapeHtml(pageUrl(newer.url))}"><span>Next episode →</span><strong>#${newer.number} · ${escapeHtml(newer.title)}</strong></a>` : '<span class="pager-link pager-placeholder"></span>'}`;
    main.appendChild(pager);
  };

  const parseCasesFromUrl = (episodes) => {
    const valid = new Set(episodes.map((episode) => episode.number));
    const params = new URLSearchParams(window.location.search);
    return (params.get('cases') || '')
      .split(',')
      .map(Number)
      .filter((number, index, array) => valid.has(number) && array.indexOf(number) === index)
      .slice(0, 3);
  };

  const renderCompare = (episodes) => {
    const picker = document.getElementById('compare-picker');
    const output = document.getElementById('comparison-output');
    if (!picker || !output) return;

    let selectedNumbers = parseCasesFromUrl(episodes);
    if (selectedNumbers.length < 2) selectedNumbers = episodes.slice(0, 3).map((episode) => episode.number);

    const updateUrl = () => {
      const url = new URL(window.location.href);
      if (selectedNumbers.length) url.searchParams.set('cases', selectedNumbers.join(','));
      else url.searchParams.delete('cases');
      history.replaceState({}, '', url);
      saveCompareSelection(new Set(selectedNumbers));
    };

    const render = () => {
      picker.innerHTML = [0, 1, 2].map((index) => {
        const current = selectedNumbers[index] || '';
        const options = [`<option value="">${index === 2 ? 'Optional third case' : `Select case ${index + 1}`}</option>`]
          .concat(episodes.map((episode) => `<option value="${episode.number}"${episode.number === current ? ' selected' : ''}>#${episode.number} · ${escapeHtml(episode.title)}</option>`))
          .join('');
        return `<label class="compare-select"><span>Case ${index + 1}${index === 2 ? ' · optional' : ''}</span><select data-compare-slot="${index}">${options}</select></label>`;
      }).join('');

      const chosen = selectedNumbers
        .map((number) => episodes.find((episode) => episode.number === number))
        .filter(Boolean);

      if (chosen.length < 2) {
        output.innerHTML = '<p class="archive-empty">Select at least two different cases to build a comparison.</p>';
        return;
      }

      const rows = [
        ['Season / collection', (episode) => seasonLabel(episode, 'Not registered')],
        ['Functional unit / reporting basis', (episode) => episode.functionalUnit || 'Not registered'],
        ['Headline result', (episode) => episode.result],
        ['Narrative category', (episode) => episode.categoryLabel],
        ['Principal LCA lens', (episode) => episode.lcaLabel],
        ['Main hotspot', (episode) => episode.hotspot],
        ['Evidence confidence', (episode) => episode.evidence?.confidence || 'Not rated'],
        ['Proxy dependence', (episode) => episode.evidence?.proxyDependence || 'Not rated'],
        ['Assumption sensitivity', (episode) => episode.evidence?.assumptionSensitivity || 'Not rated'],
        ['Main modelling uncertainty', (episode) => episode.evidence?.uncertainty || 'Not registered']
      ];

      output.innerHTML = `
        <div class="comparison-warning"><strong>Interpretation rule</strong><p>Headline footprints use different functional units and system boundaries. This table compares modelling structure and hotspot behaviour; it is not a comparative environmental claim and does not rank cases as better or worse.</p></div>
        <div class="comparison-table-wrap">
          <table class="comparison-table">
            <thead><tr><th scope="col">Dimension</th>${chosen.map((episode) => `<th scope="col"><a href="${escapeHtml(episode.url)}">#${episode.number}<br>${escapeHtml(episode.title)}</a></th>`).join('')}</tr></thead>
            <tbody>${rows.map(([label, value]) => `<tr><th scope="row">${escapeHtml(label)}</th>${chosen.map((episode) => `<td>${escapeHtml(value(episode))}</td>`).join('')}</tr>`).join('')}</tbody>
          </table>
        </div>
        <div class="compare-open-row">${chosen.map((episode) => `<a class="button secondary" href="${escapeHtml(episode.url)}">Open #${episode.number} →</a>`).join('')}</div>`;
    };

    picker.addEventListener('change', (event) => {
      const select = event.target.closest('select[data-compare-slot]');
      if (!select) return;
      const slot = Number(select.dataset.compareSlot);
      const number = Number(select.value);
      const next = [...selectedNumbers];
      if (number) next[slot] = number;
      else next.splice(slot, 1);
      selectedNumbers = next.filter((item, index, array) => Number.isFinite(item) && array.indexOf(item) === index).slice(0, 3);
      updateUrl();
      render();
    });

    updateUrl();
    render();
  };

  const resultToKg = (result = '') => {
    const numberMatch = String(result).match(/[\d.,]+/);
    const unitMatch = String(result).match(/\b(Mt|kt|t|kg)\s*CO/i);
    if (!numberMatch || !unitMatch) return null;
    const value = Number(numberMatch[0].replaceAll(',', ''));
    const unit = unitMatch[1].toLowerCase();
    const multiplier = unit === 'mt' ? 1e9 : unit === 'kt' ? 1e6 : unit === 't' ? 1e3 : 1;
    return Number.isFinite(value) ? value * multiplier : null;
  };

  const renderExplore = (episodes) => {
    const filters = document.getElementById('impact-filters');
    const plot = document.getElementById('impact-plot');
    const count = document.getElementById('impact-count');
    if (!filters || !plot || !count) return;

    const data = episodes
      .map((episode) => ({ ...episode, resultKg: resultToKg(episode.result) }))
      .filter((episode) => episode.resultKg && episode.resultKg > 0)
      .sort((a, b) => a.resultKg - b.resultKg);
    const lenses = [...new Set(data.map((episode) => episode.lcaLabel))];
    let activeLens = 'all';

    filters.innerHTML = `<button class="filter-button active" type="button" data-impact-lens="all" aria-pressed="true">All lenses</button>${lenses.map((lens) => `<button class="filter-button" type="button" data-impact-lens="${escapeHtml(lens)}" aria-pressed="false">${escapeHtml(lens)}</button>`).join('')}`;

    const minLog = 1;
    const maxLog = 10;
    const axisLabels = [
      [1, '10 kg'], [2, '100 kg'], [3, '1 t'], [4, '10 t'], [5, '100 t'],
      [6, '1 kt'], [7, '10 kt'], [8, '100 kt'], [9, '1 Mt'], [10, '10 Mt']
    ];

    const render = () => {
      const visible = data.filter((episode) => activeLens === 'all' || episode.lcaLabel === activeLens);
      count.textContent = `${visible.length} ${visible.length === 1 ? 'case' : 'cases'} shown`;
      plot.innerHTML = `
        <div class="impact-axis" aria-hidden="true">${axisLabels.map(([power, label]) => `<span style="--axis-pos:${((power - minLog) / (maxLog - minLog)) * 100}%">${label}</span>`).join('')}</div>
        <div class="impact-rows">${visible.map((episode) => {
          const log = Math.log10(episode.resultKg);
          const pos = Math.max(0, Math.min(100, ((log - minLog) / (maxLog - minLog)) * 100));
          return `<article class="impact-row">
            <div class="impact-row-label"><a href="${escapeHtml(episode.url)}"><strong>#${episode.number} · ${escapeHtml(episode.title)}</strong></a><span>${episode.seasonLabel ? `${escapeHtml(episode.seasonLabel)} · ` : ''}${escapeHtml(episode.lcaLabel)}</span></div>
            <div class="impact-track">
              <a class="impact-point" style="--impact-pos:${pos}%" href="${escapeHtml(episode.url)}" aria-label="${escapeHtml(episode.title)}: ${escapeHtml(episode.result)}"><span>${escapeHtml(episode.result)}</span></a>
            </div>
          </article>`;
        }).join('')}</div>`;
    };

    filters.addEventListener('click', (event) => {
      const button = event.target.closest('[data-impact-lens]');
      if (!button) return;
      activeLens = button.dataset.impactLens;
      filters.querySelectorAll('[data-impact-lens]').forEach((item) => {
        const selected = item === button;
        item.classList.toggle('active', selected);
        item.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
      render();
    });

    render();
  };

  fetch(registryPath, { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    })
    .then((data) => {
      const episodes = [...data.episodes].sort((a, b) => b.number - a.number);
      if (body.dataset.page === 'home') renderHome(episodes);
      if (body.dataset.page === 'home') renderSeasonSpotlight(episodes);
      if (body.dataset.page === 'archive') renderArchive(episodes);
      if (body.dataset.page === 'compare') renderCompare(episodes);
      if (body.dataset.page === 'explore') renderExplore(episodes);
      if (isEpisode) {
        const current = episodes.find((episode) => episode.number === Number(body.dataset.episode));
        if (current) renderEvidenceProfile(current);
        renderEpisodeNavigation(episodes);
      }
    })
    .catch((error) => {
      console.error('Unable to load episode registry:', error);
      document.querySelectorAll('[data-registry-status]').forEach((node) => {
        node.textContent = 'Episode catalogue is temporarily unavailable.';
      });
    });
})();
