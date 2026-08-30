(() => {
  'use strict';

  const body = document.body;
  if (!body) return;

  const isEpisode = Boolean(body.dataset.episode);
  const rootPrefix = isEpisode ? '../' : '';
  const episodeRegistryUrl = `${rootPrefix}episodes.json`;
  const collectionsRegistryUrl = `${rootPrefix}collections.json`;

  const style = document.createElement('link');
  style.rel = 'stylesheet';
  style.href = `${rootPrefix}assets/engagement.css?v=20260830-subject-descriptions1`;
  document.head.appendChild(style);

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const pageUrl = (value = '') => /^https?:\/\//i.test(String(value))
    ? String(value)
    : `${rootPrefix}${String(value)}`;

  const randomIndex = (length) => {
    if (length <= 1) return 0;
    if (window.crypto?.getRandomValues) {
      const bucket = new Uint32Array(1);
      window.crypto.getRandomValues(bucket);
      return bucket[0] % length;
    }
    return Math.floor(Math.random() * length);
  };

  const copyText = async (text) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand('copy');
    area.remove();
    if (!ok) throw new Error('Copy command failed');
  };

  const canonicalEpisodeUrl = (episode) => new URL(pageUrl(episode.url), window.location.href).href;
  const editorialPathEpisodeUrl = (episode, slug) => {
    const url = new URL(pageUrl(episode.url), window.location.href);
    url.searchParams.set('path', slug);
    return url.href;
  };

  const randomCase = (episodes, allowedNumbers = null) => {
    const currentNumber = Number(body.dataset.episode);
    let pool = allowedNumbers
      ? allowedNumbers.map((number) => episodes.find((episode) => episode.number === number)).filter(Boolean)
      : [...episodes];
    if (pool.length > 1 && Number.isFinite(currentNumber)) {
      pool = pool.filter((episode) => episode.number !== currentNumber);
    }
    if (!pool.length) return;
    const chosen = pool[randomIndex(pool.length)];
    window.location.assign(pageUrl(chosen.url));
  };

  const textCaseCard = (episode) => `
    <a class="engagement-case-card" href="${escapeHtml(pageUrl(episode.url))}">
      <div>
        <p>${episode.seasonLabel ? `${escapeHtml(episode.seasonLabel)} · ` : ''}${escapeHtml(episode.categoryLabel)} · ${escapeHtml(episode.lcaLabel)}</p>
        <h3>#${episode.number} · ${escapeHtml(episode.title)}</h3>
        <span class="engagement-case-subject">${escapeHtml(episode.subjectDescription)}</span>
      </div>
      <div class="engagement-case-meta">
        <strong>${escapeHtml(episode.result)}</strong>
        <span>${escapeHtml(episode.hotspot)}</span>
      </div>
      <b>Open case →</b>
    </a>`;

  const renderSeasons = (episodes, seasons) => {
    if (body.dataset.page !== 'collections') return;
    const list = document.getElementById('season-list');
    if (!list) return;
    list.innerHTML = seasons.map((season) => {
      const cases = (season.episodes || [])
        .map((number) => episodes.find((episode) => episode.number === number))
        .filter(Boolean);
      const range = Array.isArray(season.episodeRange) && season.episodeRange.length === 2
        ? `Episodes #${season.episodeRange[0]}–${season.episodeRange[1]}`
        : 'Controlled episode range';
      return `<section class="collection-block season-collection" id="${escapeHtml(season.id)}">
        <div class="collection-heading">
          <div>
            <p class="eyebrow">${escapeHtml(range)}</p>
            <h2>${escapeHtml(season.label)}</h2>
            <p class="section-note">${escapeHtml(season.descriptor)}</p>
            <p class="section-note">${escapeHtml(season.editorialDescriptor)}</p>
          </div>
        </div>
        <div class="engagement-case-grid">${cases.map(textCaseCard).join('')}</div>
      </section>`;
    }).join('');
  };

  const renderHomeEngagement = (episodes, collections, editorialPaths, linkedinUrl) => {
    if (body.dataset.page !== 'home' || document.getElementById('discover-paths')) return;
    const recent = document.querySelector('.recent-section');
    if (!recent) return;

    const section = document.createElement('section');
    section.id = 'discover-paths';
    section.className = 'section engagement-home small-section-title';
    section.innerHTML = `
      <div class="section-heading">
        <div><p class="eyebrow">EXPLORE DIFFERENTLY</p><h2>Choose a path through the impossible</h2></div>
        <p class="section-note">Curated collections connect cases by engineering behaviour, not just publication order.</p>
      </div>
      <div class="collection-teaser-grid">
        ${collections.slice(0, 3).map((collection) => `
          <a class="collection-teaser" href="collections.html#${escapeHtml(collection.slug)}">
            <span>${escapeHtml(collection.eyebrow)}</span>
            <h3>${escapeHtml(collection.title)}</h3>
            <p>${escapeHtml(collection.description)}</p>
            <strong>${collection.episodes.length} cases · Explore →</strong>
          </a>`).join('')}
      </div>
      <div class="engagement-actions">
        <a class="button" href="collections.html">Browse collections →</a>
        ${editorialPaths.length ? '<a class="button secondary" href="collections.html#editorial-paths">Guided reading paths →</a>' : ''}
        <button class="button secondary" type="button" data-random-case>Random impossible case ↻</button>
        ${linkedinUrl ? `<a class="button secondary" href="${escapeHtml(linkedinUrl)}" target="_blank" rel="noopener noreferrer">Follow on LinkedIn ↗</a>` : ''}
      </div>`;
    recent.insertAdjacentElement('afterend', section);
  };

  const renderEditorialPaths = (episodes, editorialPaths, collections) => {
    if (body.dataset.page !== 'collections') return;
    const index = document.getElementById('editorial-path-index');
    const list = document.getElementById('editorial-path-list');
    if (!index || !list) return;
    if (!editorialPaths.length) {
      index.innerHTML = '<span class="section-note">No guided paths are currently registered.</span>';
      list.innerHTML = '';
      return;
    }

    const collectionsBySlug = new Map(collections.map((collection) => [collection.slug, collection]));
    index.innerHTML = editorialPaths.map((path) => `
      <a href="#path-${escapeHtml(path.slug)}">${escapeHtml(path.title)} <span>${path.steps.length}</span></a>`).join('');

    list.innerHTML = editorialPaths.map((path) => {
      const steps = path.steps
        .map((step) => ({ ...step, episodeData: episodes.find((episode) => episode.number === step.episode) }))
        .filter((step) => step.episodeData);
      const related = (path.relatedCollections || [])
        .map((slug) => collectionsBySlug.get(slug))
        .filter(Boolean);
      return `<article class="editorial-path" id="path-${escapeHtml(path.slug)}">
        <header class="editorial-path-heading">
          <div><p class="eyebrow">${escapeHtml(path.eyebrow)}</p><h2>${escapeHtml(path.title)}</h2><strong>${escapeHtml(path.question)}</strong><p>${escapeHtml(path.description)}</p></div>
          <div class="editorial-path-actions"><a class="button" href="${escapeHtml(editorialPathEpisodeUrl(steps[0].episodeData, path.slug))}">Start with #${steps[0].episodeData.number} →</a><button class="button secondary" type="button" data-copy-path="${escapeHtml(path.slug)}">Copy path link</button></div>
        </header>
        <div class="editorial-path-steps" role="list">${steps.map((step, stepIndex) => {
          const episode = step.episodeData;
          return `<a class="editorial-path-step" role="listitem" href="${escapeHtml(editorialPathEpisodeUrl(episode, path.slug))}">
            <span class="editorial-path-number">${String(stepIndex + 1).padStart(2, '0')}</span>
            <div><p>${escapeHtml(step.phase)}</p><h3>#${episode.number} · ${escapeHtml(episode.title)}</h3><span>${escapeHtml(step.note)}</span></div>
            <div class="editorial-path-meta"><strong>${escapeHtml(episode.result)}</strong><span>${escapeHtml(episode.lcaLabel)} · ${escapeHtml(episode.hotspot)}</span></div>
          </a>`;
        }).join('')}</div>
        ${related.length ? `<nav class="editorial-path-related" aria-label="Related collections"><span>Continue by collection</span>${related.map((collection) => `<a href="#${escapeHtml(collection.slug)}">${escapeHtml(collection.title)} →</a>`).join('')}</nav>` : ''}
        <p class="collection-status" data-path-status="${escapeHtml(path.slug)}" aria-live="polite"></p>
      </article>`;
    }).join('');
  };

  const placeEditorialPathNavigation = (episode, episodes, editorialPaths) => {
    if (!isEpisode || document.getElementById('editorial-path-progress')) return;
    const slug = new URL(window.location.href).searchParams.get('path');
    if (!slug) return;
    const path = editorialPaths.find((item) => item.slug === slug);
    if (!path || !Array.isArray(path.steps)) return;
    const stepIndex = path.steps.findIndex((step) => step.episode === episode.number);
    if (stepIndex < 0) return;
    const previous = stepIndex > 0 ? path.steps[stepIndex - 1] : null;
    const next = stepIndex + 1 < path.steps.length ? path.steps[stepIndex + 1] : null;
    const previousEpisode = previous ? episodes.find((item) => item.number === previous.episode) : null;
    const nextEpisode = next ? episodes.find((item) => item.number === next.episode) : null;
    const section = document.createElement('section');
    section.id = 'editorial-path-progress';
    section.className = 'editorial-path-progress';
    section.setAttribute('aria-labelledby', 'editorial-path-progress-title');
    section.innerHTML = `<div class="editorial-path-progress-copy"><p class="eyebrow">GUIDED READING PATH · STEP ${stepIndex + 1} OF ${path.steps.length}</p><h2 id="editorial-path-progress-title">${escapeHtml(path.title)}</h2><p>${escapeHtml(path.question)}</p></div>
      <div class="editorial-path-progress-track" role="img" aria-label="Step ${stepIndex + 1} of ${path.steps.length}">${path.steps.map((_, index) => `<span${index === stepIndex ? ' data-current="true"' : index < stepIndex ? ' data-complete="true"' : ''}></span>`).join('')}</div>
      <nav class="editorial-path-progress-nav" aria-label="Guided path navigation">
        ${previousEpisode ? `<a href="${escapeHtml(editorialPathEpisodeUrl(previousEpisode, path.slug))}">← #${previousEpisode.number} · ${escapeHtml(previousEpisode.title)}</a>` : '<span>Beginning of path</span>'}
        <a href="${rootPrefix}collections.html#path-${escapeHtml(path.slug)}">Path overview</a>
        ${nextEpisode ? `<a href="${escapeHtml(editorialPathEpisodeUrl(nextEpisode, path.slug))}">#${nextEpisode.number} · ${escapeHtml(nextEpisode.title)} →</a>` : '<span>End of path</span>'}
      </nav>`;
    const main = document.querySelector('main');
    const pager = main?.querySelector('.episode-pager');
    if (pager) pager.insertAdjacentElement('beforebegin', section);
    else main?.appendChild(section);
  };

  const augmentArchive = (linkedinUrl) => {
    if (body.dataset.page !== 'archive') return;
    const entry = document.querySelector('.archive-feature-entrypoints .cta-row');
    if (!entry || entry.querySelector('[data-phase4-entry]')) return;
    entry.insertAdjacentHTML('beforeend', `
      <a class="button secondary" data-phase4-entry href="collections.html">Collections →</a>
      <button class="button secondary" data-phase4-entry type="button" data-random-case>Random case ↻</button>
      ${linkedinUrl ? `<a class="button secondary" data-phase4-entry href="${escapeHtml(linkedinUrl)}" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a>` : ''}`);
  };

  const renderCollections = (episodes, collections) => {
    if (body.dataset.page !== 'collections') return;
    const index = document.getElementById('collection-index');
    const list = document.getElementById('collection-list');
    if (!index || !list) return;

    index.innerHTML = collections.map((collection) => `
      <a href="#${escapeHtml(collection.slug)}">${escapeHtml(collection.title)} <span>${collection.episodes.length}</span></a>`).join('');

    list.innerHTML = collections.map((collection) => {
      const cases = collection.episodes
        .map((number) => episodes.find((episode) => episode.number === number))
        .filter(Boolean);
      return `
        <section class="collection-block" id="${escapeHtml(collection.slug)}">
          <div class="collection-heading">
            <div>
              <p class="eyebrow">${escapeHtml(collection.eyebrow)}</p>
              <h2>${escapeHtml(collection.title)}</h2>
              <p class="section-note">${escapeHtml(collection.description)}</p>
            </div>
            <div class="collection-actions">
              <button class="button secondary" type="button" data-random-collection="${escapeHtml(collection.slug)}">Random from collection ↻</button>
              <button class="button secondary" type="button" data-copy-collection="${escapeHtml(collection.slug)}">Copy collection link</button>
            </div>
          </div>
          <div class="engagement-case-grid">${cases.map(textCaseCard).join('')}</div>
          <p class="collection-status" data-collection-status="${escapeHtml(collection.slug)}" aria-live="polite"></p>
        </section>`;
    }).join('');
  };

  const episodeShareCaption = (episode, url) => [
    `LCA of the Impossible #${episode.number} — ${episode.title}`,
    episode.seasonLabel || '',
    '',
    episode.subjectDescription,
    '',
    `Headline result: ${episode.result} · LCA lens: ${episode.lcaLabel}`,
    '',
    url,
    '',
    '#LCA #LifeCycleAssessment #Sustainability'
  ].filter((line, index, lines) => line || lines[index - 1] !== '').join('\n');

  const placeEpisodeShare = (episode, linkedinUrl) => {
    if (!isEpisode || document.getElementById('share-case')) return;
    const main = document.querySelector('main');
    const verdict = main?.querySelector('.verdict');
    if (!main || !verdict) return;

    const url = canonicalEpisodeUrl(episode);
    const section = document.createElement('section');
    section.id = 'share-case';
    section.className = 'section share-case small-section-title';
    section.innerHTML = `
      <div class="section-heading">
        <div><p class="eyebrow">SHARE THE CASE</p><h2>Carry the audit trail forward</h2></div>
        <p class="section-note">Share the canonical episode URL or copy a LinkedIn-ready caption with the headline result and LCA lens.</p>
      </div>
      <div class="share-actions">
        <button class="button" type="button" data-share-native>Share this case ↗</button>
        <button class="button secondary" type="button" data-copy-case-link>Copy link</button>
        <button class="button secondary" type="button" data-copy-linkedin-caption>Copy LinkedIn caption</button>
        <button class="button secondary" type="button" data-random-case>Random next case ↻</button>
        ${linkedinUrl ? `<a class="button secondary" href="${escapeHtml(linkedinUrl)}" target="_blank" rel="noopener noreferrer">Follow on LinkedIn ↗</a>` : ''}
      </div>
      <p class="share-status" aria-live="polite"></p>`;

    const pager = main.querySelector('.episode-pager');
    if (pager) pager.insertAdjacentElement('beforebegin', section);
    else verdict.insertAdjacentElement('afterend', section);

    const status = section.querySelector('.share-status');
    const setStatus = (message) => {
      if (status) status.textContent = message;
    };

    section.querySelector('[data-copy-case-link]')?.addEventListener('click', async () => {
      try {
        await copyText(url);
        setStatus('Canonical episode link copied.');
      } catch (_) {
        setStatus('Unable to copy automatically. Use the browser address bar.');
      }
    });

    section.querySelector('[data-copy-linkedin-caption]')?.addEventListener('click', async () => {
      try {
        await copyText(episodeShareCaption(episode, url));
        setStatus('LinkedIn-ready caption copied.');
      } catch (_) {
        setStatus('Unable to copy the caption automatically.');
      }
    });

    section.querySelector('[data-share-native]')?.addEventListener('click', async () => {
      if (!navigator.share) {
        try {
          await copyText(url);
          setStatus('Native sharing is unavailable here; the episode link was copied instead.');
        } catch (_) {
          setStatus('Native sharing is unavailable. Copy the URL from the browser address bar.');
        }
        return;
      }
      try {
        await navigator.share({
          title: `${episode.title} — LCA of the Impossible #${episode.number}${episode.seasonLabel ? ` | ${episode.seasonLabel}` : ''}`,
          text: episode.subjectDescription,
          url
        });
        setStatus('Share panel opened.');
      } catch (error) {
        if (error?.name !== 'AbortError') setStatus('Sharing was not completed.');
      }
    });
  };

  const addCollectionNavLink = () => {
    if (!['compare', 'explore'].includes(body.dataset.page || '')) return;
    const nav = document.querySelector('.site-header nav');
    if (nav && !nav.querySelector('[data-collections-nav]')) {
      nav.insertAdjacentHTML('beforeend', '<a data-collections-nav href="collections.html">Collections</a>');
    }
  };

  Promise.all([
    fetch(episodeRegistryUrl, { cache: 'no-store' }).then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    }),
    fetch(collectionsRegistryUrl, { cache: 'no-store' }).then((response) => {
      if (!response.ok) throw new Error(`Collections registry returned ${response.status}`);
      return response.json();
    })
  ])
    .then(([episodeData, collectionData]) => {
      const episodes = [...episodeData.episodes].sort((a, b) => b.number - a.number);
      const collections = Array.isArray(collectionData.collections) ? collectionData.collections : [];
      const seasons = Array.isArray(collectionData.seasons) ? collectionData.seasons : [];
      const editorialPaths = Array.isArray(collectionData.editorialPaths) ? collectionData.editorialPaths : [];
      const linkedinUrl = typeof collectionData.socialLinks?.linkedin === 'string'
        ? collectionData.socialLinks.linkedin.trim()
        : '';

      renderHomeEngagement(episodes, collections, editorialPaths, linkedinUrl);
      augmentArchive(linkedinUrl);
      renderSeasons(episodes, seasons);
      renderEditorialPaths(episodes, editorialPaths, collections);
      renderCollections(episodes, collections);
      addCollectionNavLink();

      if (isEpisode) {
        const current = episodes.find((episode) => episode.number === Number(body.dataset.episode));
        if (current) {
          requestAnimationFrame(() => requestAnimationFrame(() => {
            placeEpisodeShare(current, linkedinUrl);
            placeEditorialPathNavigation(current, episodes, editorialPaths);
          }));
        }
      }

      document.addEventListener('click', async (event) => {
        const randomButton = event.target.closest('[data-random-case]');
        if (randomButton) {
          randomCase(episodes);
          return;
        }

        const collectionButton = event.target.closest('[data-random-collection]');
        if (collectionButton) {
          const collection = collections.find((item) => item.slug === collectionButton.dataset.randomCollection);
          if (collection) randomCase(episodes, collection.episodes);
          return;
        }

        const copyCollection = event.target.closest('[data-copy-collection]');
        if (copyCollection) {
          const slug = copyCollection.dataset.copyCollection;
          const status = document.querySelector(`[data-collection-status="${CSS.escape(slug)}"]`);
          const link = new URL(window.location.href);
          link.hash = slug;
          try {
            await copyText(link.href);
            if (status) status.textContent = 'Collection link copied.';
          } catch (_) {
            if (status) status.textContent = 'Unable to copy automatically.';
          }
          return;
        }

        const copyPath = event.target.closest('[data-copy-path]');
        if (copyPath) {
          const slug = copyPath.dataset.copyPath;
          const status = document.querySelector(`[data-path-status="${CSS.escape(slug)}"]`);
          const link = new URL(`${rootPrefix}collections.html`, window.location.href);
          link.hash = `path-${slug}`;
          try {
            await copyText(link.href);
            if (status) status.textContent = 'Guided path link copied.';
          } catch (_) {
            if (status) status.textContent = 'Unable to copy automatically.';
          }
        }
      });
    })
    .catch((error) => {
      console.error('Unable to load Phase 4 engagement data:', error);
      document.querySelectorAll('[data-engagement-status]').forEach((node) => {
        node.textContent = 'Engagement features are temporarily unavailable.';
      });
    });
})();
