(() => {
  'use strict';

  const removeLegacyEpisodeExports = (root = document) => {
    root.querySelectorAll?.('.episode-pdf-action-static').forEach((node) => node.remove());

    root.querySelectorAll?.('a[href*="assets/pdf/episodes/"][href$=".pdf"], a[href*="assets/pdf/episodes/"][href*=".pdf?"]').forEach((link) => {
      const wrapper = link.closest('.cta-row, .episode-pdf-action-static');
      if (wrapper) wrapper.remove();
      else link.remove();
    });

    root.querySelectorAll?.('.passport-raw, .passport-raw-download').forEach((node) => node.remove());

    root.querySelectorAll?.('button, a').forEach((node) => {
      const label = (node.textContent || '').trim().toLowerCase();
      if (label.includes('download episode pdf') || label.includes('raw text')) node.remove();
    });
  };

  removeLegacyEpisodeExports();

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType !== Node.ELEMENT_NODE) return;
        removeLegacyEpisodeExports(node);
        if (node.matches?.('.episode-pdf-action-static, .passport-raw, .passport-raw-download')) node.remove();
      });
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
})();
