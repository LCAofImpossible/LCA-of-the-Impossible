(() => {
  'use strict';

  if (document.body.dataset.page !== 'statistics') return;

  const totalMetric = document.getElementById('stat-total');
  const seasonMetric = document.getElementById('stat-seasons');
  const lensMetric = document.getElementById('stat-lenses');
  const signalMetric = document.getElementById('stat-signals');
  const updated = document.getElementById('statistics-updated');
  const seasonDistribution = document.getElementById('season-distribution');
  const lensDistribution = document.getElementById('lens-distribution');
  const characteristicDistribution = document.getElementById('characteristic-distribution');
  const evidenceProfiles = document.getElementById('evidence-profiles');
  const subjectDistribution = document.getElementById('subject-distribution');

  const escapeHtml = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const titleCase = (value) => String(value ?? '')
    .split('-')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');

  const countValues = (values) => {
    const counts = new Map();
    values.filter(Boolean).forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
    return [...counts.entries()]
      .map(([label, count]) => ({ label, count }))
      .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
  };

  const bars = (items, total, labelFormatter = (value) => value, linkFor = () => '') => items.map((item) => {
    const share = total ? (item.count / total) * 100 : 0;
    const label = labelFormatter(item.label);
    const href = linkFor(item.label);
    const labelMarkup = href
      ? `<a href="${escapeHtml(href)}">${escapeHtml(label)} →</a>`
      : `<strong>${escapeHtml(label)}</strong>`;
    return `
      <div class="statistics-bar-row">
        <div class="statistics-bar-label">${labelMarkup}<span>${item.count} ${item.count === 1 ? 'case' : 'cases'}</span></div>
        <div class="statistics-bar-track" role="img" aria-label="${escapeHtml(label)}: ${item.count} of ${total} published cases">
          <span style="--bar-share:${share.toFixed(3)}%"></span>
        </div>
      </div>`;
  }).join('');

  const evidenceCard = (title, field, episodes) => {
    const levels = ['High', 'Medium', 'Low'];
    const counts = new Map(countValues(episodes.map((episode) => episode.evidence?.[field])).map((item) => [item.label, item.count]));
    const segments = levels.map((level) => {
      const count = counts.get(level) || 0;
      const share = episodes.length ? (count / episodes.length) * 100 : 0;
      return `<span class="evidence-segment evidence-${level.toLowerCase()}" style="--segment-share:${share.toFixed(3)}%" title="${level}: ${count}" aria-hidden="true"></span>`;
    }).join('');
    const legend = levels.map((level) => `<li><span class="evidence-key evidence-${level.toLowerCase()}"></span><strong>${level}</strong><b>${counts.get(level) || 0}</b></li>`).join('');
    const summary = levels.map((level) => `${level} ${counts.get(level) || 0}`).join(', ');
    return `
      <article class="statistics-evidence-card">
        <span>EDITORIAL INDICATOR</span>
        <h3>${escapeHtml(title)}</h3>
        <div class="evidence-stack" role="img" aria-label="${escapeHtml(title)}: ${escapeHtml(summary)}">${segments}</div>
        <ul class="evidence-legend">${legend}</ul>
      </article>`;
  };

  const render = (episodes) => {
    const seasons = countValues(episodes.map((episode) => episode.seasonId));
    const seasonNames = new Map(episodes.map((episode) => [episode.seasonId, episode.seasonLabel]));
    const lenses = countValues(episodes.map((episode) => episode.lcaLabel));
    const signals = countValues(episodes.flatMap((episode) => episode.lcaCharacteristics || []));
    const subjects = countValues(episodes.flatMap((episode) => episode.categories || []));

    totalMetric.textContent = String(episodes.length);
    seasonMetric.textContent = String(seasons.length);
    lensMetric.textContent = String(lenses.length);
    signalMetric.textContent = String(signals.length);

    const latestModified = episodes
      .map((episode) => episode.dateModified || episode.datePublished)
      .filter(Boolean)
      .sort()
      .at(-1);
    const latestNumber = Math.max(...episodes.map((episode) => Number(episode.number)));
    const formattedDate = latestModified
      ? new Intl.DateTimeFormat('en-GB', { dateStyle: 'long', timeZone: 'UTC' }).format(new Date(`${latestModified}T00:00:00Z`))
      : 'date not registered';
    updated.textContent = `Registry snapshot · latest case #${latestNumber} · updated ${formattedDate}`;

    seasonDistribution.innerHTML = bars(
      seasons,
      episodes.length,
      (seasonId) => seasonNames.get(seasonId) || titleCase(seasonId),
      (seasonId) => `${seasonId}.html`,
    );
    lensDistribution.innerHTML = bars(lenses, episodes.length);

    characteristicDistribution.innerHTML = signals.map((item, index) => `
      <article class="statistics-signal-card">
        <span>${String(index + 1).padStart(2, '0')}</span>
        <strong>${escapeHtml(titleCase(item.label))}</strong>
        <b>${item.count}</b>
        <small>${item.count === 1 ? 'published case' : 'published cases'}</small>
      </article>`).join('');

    evidenceProfiles.innerHTML = [
      evidenceCard('Evidence confidence', 'confidence', episodes),
      evidenceCard('Proxy dependence', 'proxyDependence', episodes),
      evidenceCard('Assumption sensitivity', 'assumptionSensitivity', episodes),
    ].join('');

    subjectDistribution.innerHTML = subjects.map((item) => `
      <div class="statistics-subject">
        <span>${escapeHtml(titleCase(item.label))}</span>
        <strong>${item.count}</strong>
        <small>${item.count === 1 ? 'case' : 'cases'}</small>
      </div>`).join('');
  };

  const fail = () => {
    updated.textContent = 'The current registry could not be loaded.';
    document.querySelectorAll('[data-statistics-status]').forEach((element) => {
      element.innerHTML = '<p class="statistics-error">Statistics are temporarily unavailable. The episode archive remains accessible.</p>';
    });
  };

  fetch('episodes.json', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Registry request failed: ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      const episodes = Array.isArray(registry.episodes) ? registry.episodes : [];
      if (!episodes.length) throw new Error('No published episodes in registry');
      render(episodes);
    })
    .catch(fail);
})();
