(() => {
  'use strict';

  const body = document.body;
  const isEpisode = Boolean(body && body.dataset.episode);
  const registryPath = isEpisode ? '../episodes.json' : 'episodes.json';
  const rootPrefix = isEpisode ? '../' : '';
  const compareStorageKey = 'lcaImpossibleCompare';

  const featureStyles = document.createElement('link');
  featureStyles.rel = 'stylesheet';
  featureStyles.href = `${rootPrefix}assets/features.css?v=20260829-atlas1`;
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
          <a class="button secondary" data-phase3-link href="explore.html">Open the Atlas →</a>`);
      }
    }

    if (isEpisode) {
      const nav = document.querySelector('.site-header nav');
      if (nav && !nav.querySelector('[data-phase3-link]')) {
        nav.insertAdjacentHTML('beforeend', `<a data-phase3-link href="${rootPrefix}compare.html">Compare</a><a data-phase3-link href="${rootPrefix}explore.html">Atlas</a>`);
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
    const subjectFilter = document.getElementById('subject-filter');
    const hotspotFilter = document.getElementById('hotspot-filter');
    const boundaryFilter = document.getElementById('boundary-filter');
    const confidenceFilter = document.getElementById('evidence-confidence-filter');
    const proxyFilter = document.getElementById('proxy-dependence-filter');
    const sensitivityFilter = document.getElementById('assumption-sensitivity-filter');
    const clearFilters = document.getElementById('clear-filters');
    const activeFilters = document.getElementById('active-filters');
    if (!grid || !search || !count || !empty || !loadMore || !categoryFilters || !lcaFilters || !seasonFilters
      || !subjectFilter || !hotspotFilter || !boundaryFilter || !confidenceFilter || !proxyFilter
      || !sensitivityFilter || !clearFilters || !activeFilters) return;

    const toolbar = document.querySelector('.archive-toolbar');
    if (toolbar && !document.querySelector('.archive-feature-entrypoints')) {
      toolbar.insertAdjacentHTML('beforebegin', `
        <div class="archive-feature-entrypoints">
          <div><p class="eyebrow">EXPLORE THE SERIES</p><p class="section-note">Compare modelling choices side by side or map the archive by season, subject, hotspot and model signal.</p></div>
          <div class="cta-row"><a class="button secondary" href="compare.html">Compare cases →</a><a class="button secondary" href="explore.html">Open the Atlas →</a></div>
        </div>`);
    }

    const byLabel = (a, b) => labelFor(a).localeCompare(labelFor(b));
    const uniqueValues = (values) => [...new Set(values.filter(Boolean))].sort(byLabel);
    const metadataFor = (episode) => episode.structuredMetadata || {};
    const categories = uniqueValues(episodes.flatMap((episode) => episode.categories || []));
    const lcaCharacteristics = uniqueValues(episodes.flatMap((episode) => episode.lcaCharacteristics || []));
    const subjectTypes = uniqueValues(episodes.map((episode) => metadataFor(episode).subject?.entityType));
    const hotspotStages = uniqueValues(episodes.map((episode) => metadataFor(episode).impact?.hotspotStage));
    const boundaryTypes = uniqueValues(episodes.map((episode) => metadataFor(episode).assessment?.boundaryType));
    const evidenceOrder = ['High', 'Medium', 'Low'];
    const evidenceValues = (field) => evidenceOrder.filter((value) => episodes.some((episode) => episode.evidence?.[field] === value));
    const confidenceValues = evidenceValues('confidence');
    const proxyValues = evidenceValues('proxyDependence');
    const sensitivityValues = evidenceValues('assumptionSensitivity');
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
    const knownValues = {
      category: new Set(categories),
      lca: new Set(lcaCharacteristics),
      subject: new Set(subjectTypes),
      hotspot: new Set(hotspotStages),
      boundary: new Set(boundaryTypes),
      confidence: new Set(confidenceValues),
      proxy: new Set(proxyValues),
      sensitivity: new Set(sensitivityValues)
    };
    const supportedValue = (params, key, values) => {
      const requested = params.get(key);
      return requested && values.has(requested) ? requested : 'all';
    };
    const archiveStateFromUrl = () => {
      const params = new URLSearchParams(window.location.search);
      const requestedSeason = params.get('season');
      return {
        query: String(params.get('q') || '').trim().slice(0, 160),
        season: requestedSeason && knownSeasonIds.has(requestedSeason) ? requestedSeason : 'all',
        category: supportedValue(params, 'category', knownValues.category),
        lca: supportedValue(params, 'lca', knownValues.lca),
        subject: supportedValue(params, 'subject', knownValues.subject),
        hotspot: supportedValue(params, 'hotspot', knownValues.hotspot),
        boundary: supportedValue(params, 'boundary', knownValues.boundary),
        confidence: supportedValue(params, 'confidence', knownValues.confidence),
        proxy: supportedValue(params, 'proxy', knownValues.proxy),
        sensitivity: supportedValue(params, 'sensitivity', knownValues.sensitivity)
      };
    };
    const initialState = archiveStateFromUrl();
    let activeQuery = initialState.query;
    let activeCategory = initialState.category;
    let activeLca = initialState.lca;
    let activeSeason = initialState.season;
    let activeSubject = initialState.subject;
    let activeHotspot = initialState.hotspot;
    let activeBoundary = initialState.boundary;
    let activeConfidence = initialState.confidence;
    let activeProxy = initialState.proxy;
    let activeSensitivity = initialState.sensitivity;
    let visibleLimit = 9;
    const selected = loadCompareSelection();

    const makeButtons = (tokens, group, allLabel, activeValue) => {
      const allSelected = activeValue === 'all';
      const all = `<button class="filter-button${allSelected ? ' active' : ''}" type="button" data-group="${group}" data-filter="all" aria-pressed="${allSelected ? 'true' : 'false'}">${allLabel}</button>`;
      const rest = tokens.map((token) => {
        const isSelected = activeValue === token;
        return `<button class="filter-button${isSelected ? ' active' : ''}" type="button" data-group="${group}" data-filter="${escapeHtml(token)}" aria-pressed="${isSelected ? 'true' : 'false'}">${escapeHtml(labelFor(token))}</button>`;
      }).join('');
      return all + rest;
    };

    const makeOptions = (tokens, allLabel) => `<option value="all">${escapeHtml(allLabel)}</option>`
      + tokens.map((token) => `<option value="${escapeHtml(token)}">${escapeHtml(labelFor(token))}</option>`).join('');

    categoryFilters.innerHTML = makeButtons(categories, 'category', 'All categories', activeCategory);
    lcaFilters.innerHTML = makeButtons(lcaCharacteristics, 'lca', 'All LCA lenses', activeLca);
    subjectFilter.innerHTML = makeOptions(subjectTypes, 'All subject types');
    hotspotFilter.innerHTML = makeOptions(hotspotStages, 'All hotspot stages');
    boundaryFilter.innerHTML = makeOptions(boundaryTypes, 'All boundaries');
    confidenceFilter.innerHTML = makeOptions(confidenceValues, 'Any confidence');
    proxyFilter.innerHTML = makeOptions(proxyValues, 'Any proxy dependence');
    sensitivityFilter.innerHTML = makeOptions(sensitivityValues, 'Any assumption sensitivity');
    const countLabel = (value) => `${value} ${value === 1 ? 'episode' : 'episodes'}`;
    const seasonButton = (id, label, total) => {
      const isActive = activeSeason === id;
      return `<button class="filter-button${isActive ? ' active' : ''}" type="button" data-group="season" data-filter="${escapeHtml(id)}" aria-pressed="${isActive ? 'true' : 'false'}" aria-label="${escapeHtml(label)}, ${countLabel(total)}">${escapeHtml(label)} <span class="filter-count" aria-hidden="true">${total}</span></button>`;
    };
    seasonFilters.innerHTML = seasonButton('all', 'All seasons', episodes.length)
      + seasons.map(({ id, label }) => seasonButton(id, label, seasonCounts.get(id) || 0)).join('');

    const writeArchiveToUrl = (mode = 'push') => {
      const url = new URL(window.location.href);
      if (activeSeason === 'all') url.searchParams.delete('season');
      else url.searchParams.set('season', activeSeason);
      const setOrDelete = (key, value) => {
        if (!value || value === 'all') url.searchParams.delete(key);
        else url.searchParams.set(key, value);
      };
      setOrDelete('q', activeQuery);
      setOrDelete('category', activeCategory);
      setOrDelete('lca', activeLca);
      setOrDelete('subject', activeSubject);
      setOrDelete('hotspot', activeHotspot);
      setOrDelete('boundary', activeBoundary);
      setOrDelete('confidence', activeConfidence);
      setOrDelete('proxy', activeProxy);
      setOrDelete('sensitivity', activeSensitivity);
      if (url.href === window.location.href) return;
      const method = mode === 'replace' ? 'replaceState' : 'pushState';
      window.history[method]({
        q: activeQuery,
        season: activeSeason,
        category: activeCategory,
        lca: activeLca,
        subject: activeSubject,
        hotspot: activeHotspot,
        boundary: activeBoundary,
        confidence: activeConfidence,
        proxy: activeProxy,
        sensitivity: activeSensitivity
      }, '', `${url.pathname}${url.search}${url.hash}`);
    };

    const syncButtons = (container, activeValue) => {
      container.querySelectorAll('.filter-button').forEach((item) => {
        const isSelected = item.dataset.filter === activeValue;
        item.classList.toggle('active', isSelected);
        item.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
      });
    };

    const syncControls = () => {
      search.value = activeQuery;
      subjectFilter.value = activeSubject;
      hotspotFilter.value = activeHotspot;
      boundaryFilter.value = activeBoundary;
      confidenceFilter.value = activeConfidence;
      proxyFilter.value = activeProxy;
      sensitivityFilter.value = activeSensitivity;
      syncButtons(seasonFilters, activeSeason);
      syncButtons(categoryFilters, activeCategory);
      syncButtons(lcaFilters, activeLca);
    };

    syncControls();
    writeArchiveToUrl('replace');

    const normalizeSearch = (value) => String(value || '')
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
    const searchableText = (episode) => {
      const metadata = metadataFor(episode);
      return normalizeSearch([
      episode.title,
      `episode ${episode.number}`,
      `#${episode.number}`,
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
      metadata.subject?.narrativeDomain,
      metadata.subject?.entityType,
      metadata.subject?.narrativeOrigin,
      metadata.assessment?.reportingBasisType,
      metadata.assessment?.referenceFlow,
      metadata.assessment?.boundaryType,
      metadata.assessment?.geographicContext,
      metadata.assessment?.technologyContext,
      ...(metadata.assessment?.includedStages || []),
      ...(metadata.assessment?.excludedStages || []),
      metadata.impact?.hotspotStage,
      metadata.model?.archetype,
      metadata.model?.primaryDriver,
      ...(metadata.model?.secondaryDrivers || []),
      episode.evidence?.confidence,
      episode.evidence?.proxyDependence,
      episode.evidence?.assumptionSensitivity,
      ...(episode.categories || []),
      ...(episode.lcaCharacteristics || []),
      ...(episode.taxonomy || []),
      ...(episode.collectionSlugs || []),
      ...(episode.keywords || [])
      ].join(' '));
    };

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
      const query = normalizeSearch(activeQuery);
      const matches = episodes.filter((episode) => {
        const metadata = metadataFor(episode);
        const categoryMatch = activeCategory === 'all' || (episode.categories || []).includes(activeCategory);
        const lcaMatch = activeLca === 'all' || (episode.lcaCharacteristics || []).includes(activeLca);
        const seasonMatch = activeSeason === 'all' || episode.seasonId === activeSeason;
        const subjectMatch = activeSubject === 'all' || metadata.subject?.entityType === activeSubject;
        const hotspotMatch = activeHotspot === 'all' || metadata.impact?.hotspotStage === activeHotspot;
        const boundaryMatch = activeBoundary === 'all' || metadata.assessment?.boundaryType === activeBoundary;
        const confidenceMatch = activeConfidence === 'all' || episode.evidence?.confidence === activeConfidence;
        const proxyMatch = activeProxy === 'all' || episode.evidence?.proxyDependence === activeProxy;
        const sensitivityMatch = activeSensitivity === 'all' || episode.evidence?.assumptionSensitivity === activeSensitivity;
        const textMatch = !query || searchableText(episode).includes(query);
        return categoryMatch && lcaMatch && seasonMatch && subjectMatch && hotspotMatch && boundaryMatch
          && confidenceMatch && proxyMatch && sensitivityMatch && textMatch;
      });

      grid.innerHTML = matches.slice(0, visibleLimit)
        .map((episode) => episodeCard(episode, { showCover: true, compareEnabled: true, selected }))
        .join('');
      const shown = Math.min(matches.length, visibleLimit);
      const selectedSeason = seasons.find((season) => season.id === activeSeason);
      count.textContent = matches.length
        ? `Showing ${shown} of ${countLabel(matches.length)}${selectedSeason ? ` · ${selectedSeason.label}` : ''}`
        : '0 episodes found';
      empty.hidden = matches.length !== 0;
      loadMore.hidden = matches.length <= visibleLimit;
      if (!loadMore.hidden) {
        const nextBatch = Math.min(9, matches.length - visibleLimit);
        loadMore.textContent = `Load ${nextBatch} more ${nextBatch === 1 ? 'episode' : 'episodes'} ↓`;
        loadMore.setAttribute('aria-label', `Load ${nextBatch} more episodes; ${matches.length - visibleLimit} remain`);
      }
      const summary = [];
      if (activeQuery) summary.push(`Search: “${activeQuery}”`);
      if (selectedSeason) summary.push(selectedSeason.label);
      if (activeCategory !== 'all') summary.push(`Category: ${labelFor(activeCategory)}`);
      if (activeLca !== 'all') summary.push(`LCA lens: ${labelFor(activeLca)}`);
      if (activeSubject !== 'all') summary.push(`Subject: ${labelFor(activeSubject)}`);
      if (activeHotspot !== 'all') summary.push(`Hotspot: ${labelFor(activeHotspot)}`);
      if (activeBoundary !== 'all') summary.push(`Boundary: ${labelFor(activeBoundary)}`);
      if (activeConfidence !== 'all') summary.push(`Confidence: ${activeConfidence}`);
      if (activeProxy !== 'all') summary.push(`Proxy dependence: ${activeProxy}`);
      if (activeSensitivity !== 'all') summary.push(`Assumption sensitivity: ${activeSensitivity}`);
      activeFilters.textContent = summary.length
        ? `Active filters · ${summary.join(' · ')}`
        : 'No filters active · newest episodes first';
      clearFilters.hidden = summary.length === 0;
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
      if (group === 'season') activeSeason = value;
      visibleLimit = 9;
      writeArchiveToUrl();
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
      activeQuery = search.value.trim().slice(0, 160);
      visibleLimit = 9;
      writeArchiveToUrl('replace');
      applyArchive();
    });

    [
      [subjectFilter, (value) => { activeSubject = value; }],
      [hotspotFilter, (value) => { activeHotspot = value; }],
      [boundaryFilter, (value) => { activeBoundary = value; }],
      [confidenceFilter, (value) => { activeConfidence = value; }],
      [proxyFilter, (value) => { activeProxy = value; }],
      [sensitivityFilter, (value) => { activeSensitivity = value; }]
    ].forEach(([control, update]) => {
      control.addEventListener('change', () => {
        update(control.value);
        visibleLimit = 9;
        writeArchiveToUrl();
        applyArchive();
      });
    });

    const resetArchive = () => {
      activeQuery = '';
      activeCategory = 'all';
      activeLca = 'all';
      activeSeason = 'all';
      activeSubject = 'all';
      activeHotspot = 'all';
      activeBoundary = 'all';
      activeConfidence = 'all';
      activeProxy = 'all';
      activeSensitivity = 'all';
      visibleLimit = 9;
      syncControls();
      writeArchiveToUrl();
      applyArchive();
    };

    clearFilters.addEventListener('click', resetArchive);
    empty.addEventListener('click', (event) => {
      if (event.target.closest('[data-clear-archive]')) resetArchive();
    });

    window.addEventListener('popstate', () => {
      const state = archiveStateFromUrl();
      activeQuery = state.query;
      activeSeason = state.season;
      activeCategory = state.category;
      activeLca = state.lca;
      activeSubject = state.subject;
      activeHotspot = state.hotspot;
      activeBoundary = state.boundary;
      activeConfidence = state.confidence;
      activeProxy = state.proxy;
      activeSensitivity = state.sensitivity;
      visibleLimit = 9;
      syncControls();
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

    const metadataFor = (episode) => episode.structuredMetadata || {};
    const metadataValue = (episode, ...path) => {
      let value = metadataFor(episode);
      for (const key of path) {
        if (!value || typeof value !== 'object') return null;
        value = value[key];
      }
      return value;
    };
    const hasValue = (value) => value !== null && value !== undefined && value !== '';
    const formatList = (value) => Array.isArray(value)
      ? (value.length ? value.map((item) => labelFor(String(item))).join(', ') : 'None registered')
      : 'Not structurally registered';
    const formatValue = (value, fallback = 'Not structurally registered') => {
      if (Array.isArray(value)) return formatList(value);
      if (typeof value === 'number' && Number.isFinite(value)) return String(value);
      const text = String(value ?? '').trim();
      return text || fallback;
    };
    const comparisonStatus = (chosen, label, resolver) => {
      const values = chosen.map(resolver);
      const present = values.filter(hasValue);
      if (present.length !== chosen.length) {
        return { label, state: 'incomplete', status: 'Incomplete record', note: 'At least one selected case has no registered value.' };
      }
      const normalized = new Set(present.map((value) => String(value).trim().toLowerCase()));
      if (normalized.size === 1) {
        return { label, state: 'aligned', status: 'Matching label', note: 'Matching wording does not establish equivalent service.' };
      }
      return { label, state: 'different', status: 'Different', note: 'The selected cases use different registered values.' };
    };
    const tableCell = (value, fallback = 'Not structurally registered') => {
      const text = formatValue(value, fallback);
      const missing = !hasValue(value);
      return `<td${missing ? ' class="comparison-value-missing"' : ''}>${escapeHtml(text)}</td>`;
    };
    const magnitudeBand = (resultKg) => {
      if (!Number.isFinite(resultKg) || resultKg <= 0) return 'Magnitude unavailable';
      if (resultKg < 1e3) return 'Kilogram scale';
      if (resultKg < 1e6) return 'Tonne scale';
      if (resultKg < 1e9) return 'Kilotonne scale';
      return 'Megatonne scale';
    };
    const evidenceSignal = (label, value) => {
      const registered = ['Low', 'Medium', 'High'].includes(value) ? value : null;
      const ariaLabel = registered ? `${label}: ${registered}` : `${label}: not rated`;
      return `<div class="comparison-evidence-signal"><div><span>${escapeHtml(label)}</span><strong>${escapeHtml(registered || 'Not rated')}</strong></div><div class="comparison-level-scale" role="img" aria-label="${escapeHtml(ariaLabel)}">${['Low', 'Medium', 'High'].map((level) => `<span${level === registered ? ' data-selected="true"' : ''}>${level.charAt(0)}</span>`).join('')}</div></div>`;
    };
    const visualSummaryCard = (episode) => {
      const resultKg = resultToKg(episode.result);
      const minLog = 0;
      const maxLog = 10;
      const position = Number.isFinite(resultKg) && resultKg > 0
        ? Math.max(0, Math.min(100, ((Math.log10(resultKg) - minLog) / (maxLog - minLog)) * 100))
        : null;
      const hotspotStage = metadataValue(episode, 'impact', 'hotspotStage');
      const hotspotShare = metadataValue(episode, 'impact', 'hotspotSharePercent');
      const registeredShare = Number.isFinite(hotspotShare);
      const sharePosition = registeredShare ? Math.max(0, Math.min(100, hotspotShare)) : 0;
      return `<article class="comparison-signal-card">
        <header><span>CASE #${episode.number}</span><h4><a href="${escapeHtml(episode.url)}">${escapeHtml(episode.title)}</a></h4></header>
        <div class="comparison-magnitude-block">
          <div class="comparison-signal-heading"><span>Headline magnitude</span><strong>${escapeHtml(episode.result)}</strong></div>
          <div class="comparison-magnitude-track" role="img" aria-label="${escapeHtml(`${episode.title}: ${episode.result}; ${magnitudeBand(resultKg)} on a fixed logarithmic scale from 1 kilogram to 10 megatonnes of carbon dioxide equivalent.`)}">${position === null ? '<span class="comparison-magnitude-missing">Not positionable</span>' : `<span class="comparison-magnitude-point" style="--comparison-position:${position.toFixed(3)}%" aria-hidden="true"></span>`}</div>
          <p>${escapeHtml(magnitudeBand(resultKg))} · descriptive position only</p>
          <details><summary>Case-specific reporting basis</summary><p>${escapeHtml(episode.functionalUnit || 'Not registered')}</p></details>
        </div>
        <div class="comparison-hotspot-block">
          <div class="comparison-signal-heading"><span>Registered hotspot stage</span><strong>${escapeHtml(hotspotStage ? labelFor(hotspotStage) : 'Not structurally registered')}</strong></div>
          <div class="comparison-hotspot-track${registeredShare ? '' : ' is-missing'}" role="img" aria-label="${escapeHtml(registeredShare ? `Registered hotspot share: ${hotspotShare}%` : 'Registered hotspot share unavailable')}"><span style="--hotspot-share:${sharePosition.toFixed(3)}%"></span></div>
          <p>${registeredShare ? `${escapeHtml(hotspotShare)}% of this case’s registered headline result` : 'Share not structurally registered'}${episode.hotspot ? ` · ${escapeHtml(episode.hotspot)}` : ''}</p>
        </div>
        <div class="comparison-evidence-block">
          <span class="comparison-block-label">Evidence signals · separate ordinal fields</span>
          ${evidenceSignal('Confidence', episode.evidence?.confidence)}
          ${evidenceSignal('Proxy dependence', episode.evidence?.proxyDependence)}
          ${evidenceSignal('Assumption sensitivity', episode.evidence?.assumptionSensitivity)}
        </div>
      </article>`;
    };

    const render = () => {
      picker.innerHTML = [0, 1, 2].map((index) => {
        const current = selectedNumbers[index] || '';
        const selectedElsewhere = new Set(selectedNumbers.filter((_, selectedIndex) => selectedIndex !== index));
        const options = [`<option value="">${index === 2 ? 'Optional third case' : `Select case ${index + 1}`}</option>`]
          .concat(episodes.map((episode) => `<option value="${episode.number}"${episode.number === current ? ' selected' : ''}${selectedElsewhere.has(episode.number) ? ' disabled' : ''}>#${episode.number} · ${escapeHtml(episode.title)}</option>`))
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

      const basisStatuses = [
        comparisonStatus(chosen, 'Functional unit', (episode) => episode.functionalUnit),
        comparisonStatus(chosen, 'Reporting basis', (episode) => metadataValue(episode, 'assessment', 'reportingBasisType')),
        comparisonStatus(chosen, 'Boundary type', (episode) => metadataValue(episode, 'assessment', 'boundaryType')),
        comparisonStatus(chosen, 'Headline unit', (episode) => metadataValue(episode, 'impact', 'unit')),
      ];
      const differences = basisStatuses.filter((item) => item.state !== 'aligned').map((item) => item.label.toLowerCase());
      const basisNote = differences.length
        ? `Differences or gaps detected in ${differences.join(', ')}. Interpret the cases structurally and retain every result with its own reporting basis.`
        : 'The registered labels match, but matching labels alone do not prove equivalent services, boundaries, scenarios or data quality.';

      const groups = [
        ['01 · CASE IDENTITY & REPORTING BASIS', [
          ['Season', (episode) => seasonLabel(episode, 'Not registered'), 'Not registered'],
          ['Narrative category', (episode) => episode.categoryLabel, 'Not registered'],
          ['Structured subject type', (episode) => metadataValue(episode, 'subject', 'entityType') ? labelFor(metadataValue(episode, 'subject', 'entityType')) : null],
          ['Narrative domain', (episode) => metadataValue(episode, 'subject', 'narrativeDomain') ? labelFor(metadataValue(episode, 'subject', 'narrativeDomain')) : null],
          ['Functional unit', (episode) => episode.functionalUnit, 'Not registered'],
          ['Reporting-basis type', (episode) => metadataValue(episode, 'assessment', 'reportingBasisType') ? labelFor(metadataValue(episode, 'assessment', 'reportingBasisType')) : null],
          ['Reference flow', (episode) => metadataValue(episode, 'assessment', 'referenceFlow')],
        ]],
        ['02 · SCOPE & SYSTEM BOUNDARY', [
          ['Boundary type', (episode) => metadataValue(episode, 'assessment', 'boundaryType') ? labelFor(metadataValue(episode, 'assessment', 'boundaryType')) : null],
          ['Included stages', (episode) => metadataValue(episode, 'assessment', 'includedStages')],
          ['Excluded stages', (episode) => metadataValue(episode, 'assessment', 'excludedStages')],
          ['Temporal context', (episode) => metadataValue(episode, 'assessment', 'temporalContext')],
          ['Geographic context', (episode) => metadataValue(episode, 'assessment', 'geographicContext')],
          ['Technology context', (episode) => metadataValue(episode, 'assessment', 'technologyContext') ? labelFor(metadataValue(episode, 'assessment', 'technologyContext')) : null],
          ['Registered lifetime', (episode) => Number.isFinite(metadataValue(episode, 'assessment', 'lifetimeYears')) ? `${metadataValue(episode, 'assessment', 'lifetimeYears')} years` : null],
          ['Cut-off summary', (episode) => metadataValue(episode, 'assessment', 'cutoffSummary')],
        ]],
        ['03 · HEADLINE INTERPRETATION', [
          ['Headline result', (episode) => episode.result, 'Not registered'],
          ['Impact indicator', (episode) => metadataValue(episode, 'impact', 'indicator') ? labelFor(metadataValue(episode, 'impact', 'indicator')) : null],
          ['Registered result unit', (episode) => metadataValue(episode, 'impact', 'unit')],
          ['Principal LCA lens', (episode) => episode.lcaLabel, 'Not registered'],
          ['Main hotspot', (episode) => episode.hotspot, 'Not registered'],
          ['Hotspot stage', (episode) => metadataValue(episode, 'impact', 'hotspotStage') ? labelFor(metadataValue(episode, 'impact', 'hotspotStage')) : null],
          ['Hotspot share', (episode) => Number.isFinite(metadataValue(episode, 'impact', 'hotspotSharePercent')) ? `${metadataValue(episode, 'impact', 'hotspotSharePercent')}%` : null],
        ]],
        ['04 · MODEL ARCHITECTURE', [
          ['Model archetype', (episode) => metadataValue(episode, 'model', 'archetype') ? labelFor(metadataValue(episode, 'model', 'archetype')) : null],
          ['Primary driver', (episode) => metadataValue(episode, 'model', 'primaryDriver') ? labelFor(metadataValue(episode, 'model', 'primaryDriver')) : null],
          ['Secondary drivers', (episode) => metadataValue(episode, 'model', 'secondaryDrivers')],
          ['Repetition class', (episode) => metadataValue(episode, 'model', 'repetitionClass') ? labelFor(metadataValue(episode, 'model', 'repetitionClass')) : null],
        ]],
        ['05 · EVIDENCE PROFILE', [
          ['Evidence confidence', (episode) => episode.evidence?.confidence, 'Not rated'],
          ['Proxy dependence', (episode) => episode.evidence?.proxyDependence, 'Not rated'],
          ['Assumption sensitivity', (episode) => episode.evidence?.assumptionSensitivity, 'Not rated'],
          ['Evidence basis', (episode) => episode.evidence?.basis, 'Not registered'],
          ['Main modelling uncertainty', (episode) => episode.evidence?.uncertainty, 'Not registered'],
          ['Structured metadata status', (episode) => metadataValue(episode, 'schemaVersion') ? `Registered · schema v${metadataValue(episode, 'schemaVersion')}` : null],
          ['Missing approved fields', (episode) => metadataValue(episode, 'provenance', 'missingApprovedFields')],
        ]],
      ];

      output.innerHTML = `
        <section class="comparison-basis" aria-labelledby="comparison-basis-title">
          <div class="comparison-basis-heading"><div><span>COMPARISON BASIS</span><h3 id="comparison-basis-title">Are these headline results directly comparable?</h3></div><div class="comparison-verdict"><span>Direct footprint comparison</span><strong>Not established</strong></div></div>
          <div class="comparison-basis-grid">${basisStatuses.map((item) => `<article class="comparison-basis-card" data-state="${item.state}"><span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.status)}</strong><small>${escapeHtml(item.note)}</small></article>`).join('')}</div>
          <p class="comparison-basis-note">${escapeHtml(basisNote)}</p>
        </section>
        <div class="comparison-warning"><strong>Interpretation rule</strong><p>Compare the reasoning freely. Compare absolute footprints only with extreme caution. This view exposes registered scope, model structure and evidence; it calculates no ratios, rankings, winners or comparative environmental claims.</p></div>
        <section class="comparison-visual-summary" aria-labelledby="comparison-visual-title">
          <div class="comparison-visual-heading"><div><span>VISUAL SYNTHESIS</span><h3 id="comparison-visual-title">Magnitude, hotspot and evidence signals</h3></div><p>Three separate readings. No composite score.</p></div>
          <div class="comparison-magnitude-axis" aria-hidden="true"><span style="--axis-position:0%">1 kg</span><span style="--axis-position:30%">1 t</span><span style="--axis-position:60%">1 kt</span><span style="--axis-position:90%">1 Mt</span><span style="--axis-position:100%">10 Mt</span></div>
          <div class="comparison-signal-grid">${chosen.map(visualSummaryCard).join('')}</div>
          <p class="comparison-visual-guardrail"><strong>How to read this synthesis.</strong> Unit prefixes are converted internally to kg CO₂e only to place each published headline result on the fixed logarithmic magnitude scale. Functional units, time horizons and boundaries are not harmonized. Hotspot shares remain within-case contributions. Evidence levels remain three independent editorial signals and are never combined into a score.</p>
        </section>
        <div class="comparison-table-wrap">
          <table class="comparison-table">
            <caption>All values are projected from the current episode registry. Missing structured values are shown explicitly and are never inferred.</caption>
            <thead><tr><th scope="col">Dimension</th>${chosen.map((episode) => `<th scope="col"><a href="${escapeHtml(episode.url)}">#${episode.number}<br>${escapeHtml(episode.title)}<small>${escapeHtml(seasonLabel(episode, 'Season not registered'))}</small></a></th>`).join('')}</tr></thead>
            <tbody>${groups.map(([groupLabel, rows]) => `<tr class="comparison-table-group"><th scope="rowgroup" colspan="${chosen.length + 1}">${escapeHtml(groupLabel)}</th></tr>${rows.map(([label, value, fallback]) => `<tr><th scope="row">${escapeHtml(label)}</th>${chosen.map((episode) => tableCell(value(episode), fallback)).join('')}</tr>`).join('')}`).join('')}</tbody>
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
