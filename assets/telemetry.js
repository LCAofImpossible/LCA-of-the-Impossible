(() => {
  'use strict';

  const NAMESPACE = 'lcaofimpossible.github.io';
  const API_ROOT = 'https://counterapi.com/api';
  const OFFICIAL_HOSTS = new Set(['lcaofimpossible.github.io']);
  const body = document.body;
  const episodeNumber = body?.dataset?.episode || '';
  const isOfficialHost = OFFICIAL_HOSTS.has(window.location.hostname);

  const formatCount = (value) => {
    const number = Number(value);
    if (!Number.isFinite(number)) return '—';
    return new Intl.NumberFormat(document.documentElement.lang || 'en').format(number);
  };

  const counterUrl = (key) => {
    const ns = encodeURIComponent(NAMESPACE);
    const action = encodeURIComponent('visit');
    const counterKey = encodeURIComponent(key);
    return `${API_ROOT}/${ns}/${action}/${counterKey}?unique=true&noFormatting=true`;
  };

  const fetchCount = async (key) => {
    if (!isOfficialHost) return null;
    const response = await fetch(counterUrl(key), {
      method: 'GET',
      mode: 'cors',
      cache: 'no-store',
      credentials: 'omit',
      referrerPolicy: 'no-referrer'
    });
    if (!response.ok) throw new Error(`Telemetry counter returned ${response.status}`);
    const data = await response.json();
    return Number(data.value);
  };

  const renderSiteCounter = (value) => {
    const footer = document.querySelector('body > footer, footer:not(.passport-sheet-footer)');
    if (!footer || footer.querySelector('.site-telemetry')) return;
    const node = document.createElement('span');
    node.className = 'site-telemetry';
    node.setAttribute('aria-label', value == null ? 'Site visitor counter available on the live site' : `${formatCount(value)} site visitors recorded since telemetry activation`);
    node.innerHTML = `
      <span class="telemetry-code">SITE TELEMETRY</span>
      <strong>${value == null ? 'LIVE ONLY' : formatCount(value)}</strong>
      <span class="telemetry-unit">VISITORS</span>`;
    footer.appendChild(node);
  };

  const caseCounterMarkup = (value) => {
    const formatted = value == null ? 'LIVE ONLY' : formatCount(value);
    return `
      <div class="case-telemetry" aria-label="${value == null ? 'Episode visitor counter available on the live site' : `${formatted} visitors recorded for this episode since telemetry activation`}">
        <span class="telemetry-code">CASE TELEMETRY</span>
        <strong>${formatted}</strong>
        <span class="telemetry-unit">VISITORS</span>
      </div>`;
  };

  const renderEpisodeCounter = (value) => {
    if (!episodeNumber || document.querySelector('.case-telemetry')) return true;
    const passport = document.querySelector('.model-passport');
    if (!passport) return false;
    const actions = passport.querySelector('.passport-actions');
    if (actions) actions.insertAdjacentHTML('beforebegin', caseCounterMarkup(value));
    else passport.insertAdjacentHTML('beforeend', caseCounterMarkup(value));
    return true;
  };

  const waitForEpisodePassport = (value) => {
    if (!episodeNumber || renderEpisodeCounter(value)) return;
    const observer = new MutationObserver(() => {
      if (renderEpisodeCounter(value)) observer.disconnect();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  };

  const init = async () => {
    if (!isOfficialHost) {
      renderSiteCounter(null);
      waitForEpisodePassport(null);
      return;
    }

    const requests = [fetchCount('site-total')];
    if (episodeNumber) requests.push(fetchCount(`episode-${episodeNumber}`));

    try {
      const [siteCount, episodeCount] = await Promise.all(requests);
      renderSiteCounter(siteCount);
      if (episodeNumber) waitForEpisodePassport(episodeCount);
    } catch (error) {
      console.warn('Visitor telemetry unavailable:', error);
      renderSiteCounter(null);
      if (episodeNumber) waitForEpisodePassport(null);
    }
  };

  init();
})();
