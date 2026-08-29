(() => {
  'use strict';

  if (document.body.dataset.page !== 'explore') return;

  const status = document.getElementById('atlas-status');
  const summary = document.getElementById('atlas-summary');
  const classificationNote = document.getElementById('atlas-classification-note');
  const seasonRoutes = document.getElementById('atlas-season-routes');
  const subjectRoutes = document.getElementById('atlas-subject-routes');
  const hotspotRoutes = document.getElementById('atlas-hotspot-routes');
  const lcaRoutes = document.getElementById('atlas-lca-routes');
  const matrix = document.getElementById('atlas-matrix');
  const required = [status, summary, classificationNote, seasonRoutes, subjectRoutes, hotspotRoutes, lcaRoutes, matrix];
  if (required.some((element) => !element)) return;

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const titleCase = (value = '') => String(value)
    .split('-')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');

  const countValues = (values) => {
    const counts = new Map();
    values.filter(Boolean).forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
    return [...counts.entries()]
      .map(([value, count]) => ({ value, count }))
      .sort((a, b) => b.count - a.count || titleCase(a.value).localeCompare(titleCase(b.value)));
  };

  const archiveHref = (filters) => {
    const parameters = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) parameters.set(key, value);
    });
    return `archive.html?${parameters.toString()}`;
  };

  const routeBars = (items, denominator, labelFor, linkFor) => items.map((item) => {
    const label = labelFor(item.value);
    const share = denominator ? Math.min(100, (item.count / denominator) * 100) : 0;
    return `
      <div class="atlas-bar-row">
        <div class="atlas-bar-label"><a href="${escapeHtml(linkFor(item.value))}">${escapeHtml(label)} <span aria-hidden="true">→</span></a><strong>${item.count}</strong></div>
        <div class="atlas-bar-track" role="img" aria-label="${escapeHtml(label)}: ${item.count} ${item.count === 1 ? 'case' : 'cases'}">
          <span style="--atlas-share:${share.toFixed(3)}%"></span>
        </div>
      </div>`;
  }).join('');

  const metric = (label, value, note) => `
    <article class="atlas-metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(note)}</small></article>`;

  const renderMatrix = (episodes, subjects, hotspots) => {
    const counts = new Map();
    episodes.forEach((episode) => {
      const metadata = episode.structuredMetadata || {};
      const subject = metadata.subject?.entityType;
      const hotspot = metadata.impact?.hotspotStage;
      if (!subject || !hotspot) return;
      const key = `${subject}\u0000${hotspot}`;
      counts.set(key, (counts.get(key) || 0) + 1);
    });

    const rows = subjects.map((subject) => {
      const cells = hotspots.map((hotspot) => {
        const count = counts.get(`${subject.value}\u0000${hotspot.value}`) || 0;
        if (!count) return '<td><span class="atlas-matrix-zero" aria-label="No registered cases">—</span></td>';
        const href = archiveHref({ subject: subject.value, hotspot: hotspot.value });
        const label = `${titleCase(subject.value)} with ${titleCase(hotspot.value)} hotspot: ${count} ${count === 1 ? 'case' : 'cases'}`;
        return `<td><a href="${escapeHtml(href)}" aria-label="${escapeHtml(label)}">${count}</a></td>`;
      }).join('');
      return `<tr><th scope="row"><a href="${escapeHtml(archiveHref({ subject: subject.value }))}">${escapeHtml(titleCase(subject.value))}</a><span>${subject.count}</span></th>${cells}</tr>`;
    }).join('');

    const classified = episodes.filter((episode) => {
      const metadata = episode.structuredMetadata || {};
      return metadata.subject?.entityType && metadata.impact?.hotspotStage;
    }).length;
    matrix.innerHTML = `
      <table class="atlas-matrix">
        <caption>${classified} structurally classified ${classified === 1 ? 'case' : 'cases'} mapped. Select a value to open that intersection in the archive.</caption>
        <thead><tr><th scope="col">Subject type</th>${hotspots.map((hotspot) => `<th scope="col"><a href="${escapeHtml(archiveHref({ hotspot: hotspot.value }))}">${escapeHtml(titleCase(hotspot.value))}</a><span>${hotspot.count}</span></th>`).join('')}</tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  };

  const render = (episodes) => {
    const structured = episodes.filter((episode) => episode.structuredMetadata);
    const seasons = countValues(episodes.map((episode) => episode.seasonId));
    const seasonNames = new Map(episodes.map((episode) => [episode.seasonId, episode.seasonLabel]));
    const subjects = countValues(structured.map((episode) => episode.structuredMetadata?.subject?.entityType));
    const hotspots = countValues(structured.map((episode) => episode.structuredMetadata?.impact?.hotspotStage));
    const signals = countValues(episodes.flatMap((episode) => episode.lcaCharacteristics || []));

    summary.innerHTML = [
      metric('Published cases', episodes.length, 'Current registry'),
      metric('Seasons', seasons.length, 'Editorial identities'),
      metric('Subject types', subjects.length, 'Structured entities'),
      metric('Hotspot stages', hotspots.length, 'Dominant life-cycle stages'),
      metric('Model signals', signals.length, 'Non-exclusive LCA traits'),
    ].join('');

    seasonRoutes.innerHTML = routeBars(
      seasons,
      episodes.length,
      (seasonId) => seasonNames.get(seasonId) || titleCase(seasonId),
      (seasonId) => archiveHref({ season: seasonId }),
    );
    subjectRoutes.innerHTML = routeBars(
      subjects,
      structured.length,
      titleCase,
      (subject) => archiveHref({ subject }),
    );
    hotspotRoutes.innerHTML = routeBars(
      hotspots,
      structured.length,
      titleCase,
      (hotspot) => archiveHref({ hotspot }),
    );
    lcaRoutes.innerHTML = routeBars(
      signals,
      episodes.length,
      titleCase,
      (lca) => archiveHref({ lca }),
    );
    renderMatrix(episodes, subjects, hotspots);

    const unclassified = episodes.length - structured.length;
    classificationNote.textContent = unclassified
      ? `${structured.length} of ${episodes.length} cases currently carry structured Atlas metadata. ${unclassified} ${unclassified === 1 ? 'case remains' : 'cases remain'} visible in the full archive but is not assigned to subject or hotspot routes.`
      : `All ${episodes.length} cases carry structured Atlas metadata.`;
    const latestNumber = Math.max(...episodes.map((episode) => Number(episode.number)));
    status.textContent = `Registry-driven view · ${episodes.length} published cases · latest case #${latestNumber}`;
  };

  const fail = () => {
    status.textContent = 'The current registry could not be loaded.';
    document.querySelectorAll('[data-atlas-status]').forEach((element) => {
      element.innerHTML = '<p class="atlas-error">Atlas data are temporarily unavailable. The complete episode archive remains accessible.</p>';
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
