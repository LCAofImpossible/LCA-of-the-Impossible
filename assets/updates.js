(() => {
  'use strict';

  if (document.body?.dataset?.page !== 'updates') return;

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

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
    const copied = document.execCommand('copy');
    area.remove();
    if (!copied) throw new Error('Copy command failed');
  };

  const copyButton = document.querySelector('[data-copy-feed]');
  const copyStatus = document.querySelector('[data-copy-status]');
  copyButton?.addEventListener('click', async () => {
    try {
      await copyText(new URL('feed.xml', window.location.href).href);
      copyStatus.textContent = 'Canonical RSS feed link copied.';
    } catch (_) {
      copyStatus.textContent = 'Unable to copy automatically. Open the feed and copy its address.';
    }
  });

  const mirrorTelemetry = () => {
    const source = document.querySelector('.site-telemetry strong');
    const target = document.querySelector('[data-site-visitors]');
    const panel = document.querySelector('[data-updates-telemetry]');
    if (!source || !target || !panel) return false;
    target.textContent = source.textContent;
    panel.setAttribute('aria-label', source.textContent === 'LIVE ONLY'
      ? 'Site visitor count is available only on the live site'
      : `${source.textContent} visitors recorded since telemetry activation`);
    return true;
  };

  if (!mirrorTelemetry()) {
    const observer = new MutationObserver(() => {
      if (mirrorTelemetry()) observer.disconnect();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  const list = document.getElementById('updates-case-list');
  fetch('episodes.json', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Episode registry returned ${response.status}`);
      return response.json();
    })
    .then((registry) => {
      const episodes = Array.isArray(registry.episodes) ? registry.episodes.slice(0, 12) : [];
      if (!episodes.length) throw new Error('Episode registry contains no episodes');
      list.innerHTML = episodes.map((episode) => `
        <a class="updates-case" href="${escapeHtml(episode.url)}">
          <span class="updates-case-number">#${Number(episode.number)}</span>
          <div class="updates-case-copy">
            <span>${escapeHtml(episode.seasonLabel || episode.categoryLabel)} · ${escapeHtml(episode.lcaLabel)}</span>
            <h3>${escapeHtml(episode.title)}</h3>
            <p>${escapeHtml(episode.subjectDescription)}</p>
          </div>
          <div class="updates-case-meta">
            <strong>${escapeHtml(episode.result)}</strong>
            <span>${escapeHtml(episode.hotspot)}</span>
            <b>Open case →</b>
          </div>
        </a>`).join('');
    })
    .catch((error) => {
      console.error('Unable to load updates:', error);
      list.innerHTML = '<p class="archive-empty"><strong>Updates are temporarily unavailable.</strong><span>The RSS feed and complete archive remain accessible.</span></p>';
    });
})();
