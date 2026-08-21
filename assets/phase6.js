(() => {
  'use strict';

  const body = document.body;
  const isEpisode = Boolean(body?.dataset?.episode);
  const prefix = isEpisode ? '../' : '';
  const registryPath = `${prefix}episodes.json`;

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const safeText = (value, fallback = 'Not registered') => {
    const text = String(value || '').trim();
    return text || fallback;
  };

  const episodeAsset = (value = '') => {
    const text = String(value || '');
    if (/^https?:\/\//i.test(text) || text.startsWith('data:')) return text;
    return `${prefix}${text}`;
  };

  const canonicalEpisode = (episode) => `https://lcaofimpossible.github.io/LCA-of-the-Impossible/${episode.url}`;

  const passportSheetMarkup = (episode) => {
    const evidence = episode.evidence || {};
    return `
      <article class="passport-sheet" aria-label="Model Passport for ${escapeHtml(episode.title)}">
        <div class="passport-sheet-grid" aria-hidden="true"></div>
        <header class="passport-sheet-hero">
          <div class="passport-sheet-ident">
            <p class="passport-kicker">LCA OF THE IMPOSSIBLE // MODEL PASSPORT</p>
            <div class="passport-record-line">
              <span>EP-${String(episode.number).padStart(3, '0')}</span>
              <span>${escapeHtml(safeText(episode.categoryLabel, 'Unclassified'))}</span>
              <span>${escapeHtml(safeText(episode.lcaLabel, 'LCA case'))}</span>
            </div>
            <h2>${escapeHtml(episode.title)}</h2>
            <p class="passport-declaration">An impossible subject. A traceable model. A footprint with its assumptions left visible.</p>
          </div>
          <figure class="passport-cover-frame">
            <img src="${escapeHtml(episodeAsset(episode.cover))}" alt="${escapeHtml(episode.title)} cover" width="1200" height="1500">
            <figcaption>ARCHIVE RECORD #${episode.number}</figcaption>
          </figure>
        </header>

        <section class="passport-result-band" aria-label="Headline result">
          <div><span>HEADLINE RESULT</span><strong>${escapeHtml(safeText(episode.result))}</strong></div>
          <div><span>PRIMARY LCA LENS</span><strong>${escapeHtml(safeText(episode.lcaLabel))}</strong></div>
        </section>

        <section class="passport-sheet-section">
          <p class="passport-section-code">01 // REPORTING BASIS</p>
          <div class="passport-feature-block">
            <span>FUNCTIONAL UNIT / REPORTING BASIS</span>
            <strong>${escapeHtml(safeText(episode.functionalUnit))}</strong>
          </div>
          <div class="passport-feature-block hotspot-block">
            <span>MAIN HOTSPOT</span>
            <strong>${escapeHtml(safeText(episode.hotspot))}</strong>
          </div>
        </section>

        <section class="passport-sheet-section">
          <p class="passport-section-code">02 // EVIDENCE PROFILE</p>
          <div class="passport-evidence-triad">
            <div><span>Evidence confidence</span><strong>${escapeHtml(safeText(evidence.confidence, 'Not rated'))}</strong></div>
            <div><span>Proxy dependence</span><strong>${escapeHtml(safeText(evidence.proxyDependence, 'Not rated'))}</strong></div>
            <div><span>Assumption sensitivity</span><strong>${escapeHtml(safeText(evidence.assumptionSensitivity, 'Not rated'))}</strong></div>
          </div>
        </section>

        <section class="passport-sheet-section passport-two-column">
          <div>
            <p class="passport-section-code">03 // EVIDENCE BASIS</p>
            <p class="passport-long-copy">${escapeHtml(safeText(evidence.basis))}</p>
          </div>
          <div>
            <p class="passport-section-code">04 // MODEL UNCERTAINTY</p>
            <p class="passport-long-copy">${escapeHtml(safeText(evidence.uncertainty))}</p>
          </div>
        </section>

        <footer class="passport-sheet-footer">
          <div class="passport-seal" aria-hidden="true"><span>LCA</span><small>IMPOSSIBLE</small></div>
          <div>
            <strong>TRACEABILITY OVER CERTAINTY.</strong>
            <p>This passport is generated exclusively from registered episode metadata. It introduces no additional system boundary, factor list, allocation rule or modelling assumption. It is not a verification statement or formal data-quality rating.</p>
          </div>
          <div class="passport-canonical">
            <span>CANONICAL RECORD</span>
            <small>${escapeHtml(canonicalEpisode(episode))}</small>
          </div>
        </footer>
      </article>`;
  };

  const closePassport = () => {
    const overlay = document.querySelector('.passport-overlay');
    if (!overlay) return;
    overlay.remove();
    body.classList.remove('passport-open', 'passport-printing');
  };

  const printPassport = (episode) => {
    if (!document.querySelector('.passport-overlay')) openPassport(episode);
    body.classList.add('passport-printing');
    const cleanup = () => body.classList.remove('passport-printing');
    window.addEventListener('afterprint', cleanup, { once: true });
    requestAnimationFrame(() => window.print());
  };

  const openPassport = (episode) => {
    closePassport();
    const overlay = document.createElement('div');
    overlay.className = 'passport-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', `${episode.title} Model Passport`);
    overlay.innerHTML = `
      <div class="passport-overlay-bar">
        <div><span>MODEL PASSPORT</span><strong>#${episode.number} · ${escapeHtml(episode.title)}</strong></div>
        <div class="passport-overlay-actions">
          <button class="button secondary passport-print" type="button">Print / Save as PDF</button>
          <button class="passport-close" type="button" aria-label="Close Model Passport">×</button>
        </div>
      </div>
      <div class="passport-overlay-scroll">${passportSheetMarkup(episode)}</div>`;
    body.appendChild(overlay);
    body.classList.add('passport-open');

    overlay.querySelector('.passport-close')?.addEventListener('click', closePassport);
    overlay.querySelector('.passport-print')?.addEventListener('click', () => printPassport(episode));
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) closePassport();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && document.querySelector('.passport-overlay')) closePassport();
    }, { once: true });
    overlay.querySelector('.passport-close')?.focus();
  };

  const ensurePassportJumpLink = () => {
    const inner = document.querySelector('.episode-jumpnav-inner');
    if (!inner) return false;
    if (inner.querySelector('a[href="#model-passport"]')) return true;
    const link = document.createElement('a');
    link.href = '#model-passport';
    link.textContent = 'Passport';
    const evidenceLink = inner.querySelector('a[href="#evidence"]');
    if (evidenceLink) evidenceLink.insertAdjacentElement('afterend', link);
    else inner.appendChild(link);
    return true;
  };

  const watchForPassportJumpLink = () => {
    if (ensurePassportJumpLink()) return;
    const observer = new MutationObserver(() => {
      if (ensurePassportJumpLink()) observer.disconnect();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  };

  const renderPassport = (episode) => {
    if (!isEpisode || document.querySelector('.model-passport')) return;
    const quickFacts = document.querySelector('.episode-quickfacts');
    if (!quickFacts) return;
    const evidence = episode.evidence || {};
    const section = document.createElement('section');
    section.className = 'model-passport small-section-title';
    section.id = 'model-passport';
    section.innerHTML = `
      <div class="passport-preview-frame">
        <div class="passport-preview-copy">
          <p class="passport-kicker">EP-${String(episode.number).padStart(3, '0')} // TECHNICAL RECORD</p>
          <p class="eyebrow">MODEL PASSPORT</p>
          <h2>${escapeHtml(episode.title)}</h2>
          <p class="passport-preview-line">${escapeHtml(safeText(episode.functionalUnit))}</p>
          <div class="passport-preview-result"><span>Headline result</span><strong>${escapeHtml(safeText(episode.result))}</strong></div>
          <div class="passport-preview-evidence">
            <span>Evidence <strong>${escapeHtml(safeText(evidence.confidence, 'Not rated'))}</strong></span>
            <span>Proxy <strong>${escapeHtml(safeText(evidence.proxyDependence, 'Not rated'))}</strong></span>
            <span>Sensitivity <strong>${escapeHtml(safeText(evidence.assumptionSensitivity, 'Not rated'))}</strong></span>
          </div>
        </div>
        <div class="passport-preview-cover">
          <img src="${escapeHtml(episodeAsset(episode.cover))}" alt="${escapeHtml(episode.title)} cover" loading="lazy" decoding="async" width="1200" height="1500">
          <span>LCA // IMPOSSIBLE</span>
        </div>
      </div>
      <div class="passport-actions">
        <button class="button passport-view" type="button">View epic passport →</button>
        <button class="button secondary passport-print-direct" type="button">Print / Save as PDF</button>
      </div>
      <p class="passport-note">The visual passport is generated only from registered episode metadata. No unregistered boundary, factor list or assumption is added for presentation.</p>`;
    const anchor = document.getElementById('evidence') || quickFacts;
    anchor.insertAdjacentElement('afterend', section);
    section.querySelector('.passport-view')?.addEventListener('click', () => openPassport(episode));
    section.querySelector('.passport-print-direct')?.addEventListener('click', () => printPassport(episode));
    watchForPassportJumpLink();
  };

  const enrichImpactRows = (episodes) => {
    const plot = document.getElementById('impact-plot');
    if (!plot) return;
    const byUrl = new Map(episodes.map((episode) => [episode.url.replace(/^\.\//, ''), episode]));

    const apply = () => {
      plot.querySelectorAll('.impact-row').forEach((row) => {
        if (row.nextElementSibling?.classList.contains('impact-detail')) return;
        const link = row.querySelector('.impact-row-label a');
        if (!link) return;
        const raw = link.getAttribute('href') || '';
        const key = raw.replace(/^\.\//, '').replace(/^\//, '');
        const episode = byUrl.get(key);
        if (!episode) return;
        const evidence = episode.evidence || {};
        const details = document.createElement('details');
        details.className = 'impact-detail';
        details.dataset.episode = String(episode.number);
        details.innerHTML = `
          <summary>Technical context</summary>
          <div class="impact-detail-grid">
            <div><span>Functional unit</span><p>${escapeHtml(safeText(episode.functionalUnit))}</p></div>
            <div><span>Main hotspot</span><p>${escapeHtml(safeText(episode.hotspot))}</p></div>
            <div><span>Evidence profile</span><p>${escapeHtml(safeText(evidence.confidence, 'Not rated'))} evidence · ${escapeHtml(safeText(evidence.proxyDependence, 'Not rated'))} proxy dependence · ${escapeHtml(safeText(evidence.assumptionSensitivity, 'Not rated'))} assumption sensitivity</p></div>
          </div>
          <div class="impact-detail-actions"><a class="text-link" href="${escapeHtml(episode.url)}">Open case →</a></div>`;
        row.insertAdjacentElement('afterend', details);
      });
    };

    apply();
    const observer = new MutationObserver(() => apply());
    observer.observe(plot, { childList: true, subtree: true });
  };

  fetch(registryPath, { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    })
    .then((data) => {
      const episodes = [...(data.episodes || [])].sort((a, b) => b.number - a.number);
      if (isEpisode) {
        const episode = episodes.find((item) => item.number === Number(body.dataset.episode));
        if (episode) renderPassport(episode);
      }
      if (body.dataset.page === 'explore') enrichImpactRows(episodes);
    })
    .catch((error) => console.error('Phase 6 enhancement unavailable:', error));
})();
