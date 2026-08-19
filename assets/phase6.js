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

  const downloadPassport = (episode) => {
    const evidence = episode.evidence || {};
    const lines = [
      'LCA OF THE IMPOSSIBLE — MODEL PASSPORT',
      `Episode #${episode.number} — ${episode.title}`,
      '',
      `Functional unit / reporting basis: ${safeText(episode.functionalUnit)}`,
      `Headline result: ${safeText(episode.result)}`,
      `Principal LCA lens: ${safeText(episode.lcaLabel)}`,
      `Main hotspot: ${safeText(episode.hotspot)}`,
      `Evidence confidence: ${safeText(evidence.confidence, 'Not rated')}`,
      `Proxy dependence: ${safeText(evidence.proxyDependence, 'Not rated')}`,
      `Assumption sensitivity: ${safeText(evidence.assumptionSensitivity, 'Not rated')}`,
      `Evidence basis: ${safeText(evidence.basis)}`,
      `Main modelling uncertainty: ${safeText(evidence.uncertainty)}`,
      '',
      'Interpretation note: This model passport summarizes registered episode metadata. It is not a verification statement, a formal data-quality rating or a substitute for the full episode and its approved source material.',
      '',
      `Canonical episode: https://lcaofimpossible.github.io/LCA-of-the-Impossible/${episode.url}`,
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ep${String(episode.number).padStart(2, '0')}-${episode.slug}-model-passport.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
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
      <div class="model-passport-heading">
        <div><p class="eyebrow">MODEL PASSPORT</p><h2>The episode in one technical card</h2></div>
        <p class="section-note">Registry-derived transparency summary — no additional assumptions are introduced here.</p>
      </div>
      <div class="passport-grid">
        <article class="passport-field wide"><span>Functional unit / reporting basis</span><strong>${escapeHtml(safeText(episode.functionalUnit))}</strong></article>
        <article class="passport-field"><span>Headline result</span><strong>${escapeHtml(safeText(episode.result))}</strong></article>
        <article class="passport-field"><span>Principal LCA lens</span><strong>${escapeHtml(safeText(episode.lcaLabel))}</strong></article>
        <article class="passport-field wide"><span>Main hotspot</span><strong>${escapeHtml(safeText(episode.hotspot))}</strong></article>
        <article class="passport-field"><span>Evidence confidence</span><strong>${escapeHtml(safeText(evidence.confidence, 'Not rated'))}</strong></article>
        <article class="passport-field"><span>Proxy dependence</span><strong>${escapeHtml(safeText(evidence.proxyDependence, 'Not rated'))}</strong></article>
        <article class="passport-field"><span>Assumption sensitivity</span><strong>${escapeHtml(safeText(evidence.assumptionSensitivity, 'Not rated'))}</strong></article>
        <article class="passport-field wide"><span>Evidence basis</span><strong>${escapeHtml(safeText(evidence.basis))}</strong></article>
        <article class="passport-field wide"><span>Main modelling uncertainty</span><strong>${escapeHtml(safeText(evidence.uncertainty))}</strong></article>
      </div>
      <div class="passport-actions">
        <button class="button secondary passport-download" type="button">Download model passport ↓</button>
        <a class="button secondary" href="${prefix}method.html">Read the method →</a>
        <a class="button secondary" href="${prefix}sources.html">Sources & data →</a>
      </div>
      <p class="passport-note">This passport summarizes fields already registered for the episode. It deliberately does not invent a system boundary, factor list or assumption set when those details are not structured in the registry; consult the episode inventory and approved PDF for the full model.</p>`;
    quickFacts.insertAdjacentElement('afterend', section);
    section.querySelector('.passport-download')?.addEventListener('click', () => downloadPassport(episode));
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
