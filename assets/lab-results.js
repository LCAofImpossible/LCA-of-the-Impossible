(() => {
  'use strict';

  const SCALE_MAX = 1000;
  const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
  const finiteNumber = (value) => Number.isFinite(Number(value)) ? Number(value) : 0;
  const rounded = (value) => Math.round(finiteNumber(value));
  const percentage = (value) => `${rounded(clamp(finiteNumber(value), 0, 100))}%`;
  const points = (value) => `${rounded(Math.max(0, finiteNumber(value))).toLocaleString('en-US')} pts`;

  const normalizeScore = (score, maximum) => {
    const safeMaximum = Math.max(0, finiteNumber(maximum));
    if (!safeMaximum) return 0;
    return rounded(clamp(finiteNumber(score) / safeMaximum, 0, 1) * SCALE_MAX);
  };

  const metric = (label, value) => {
    const wrapper = document.createElement('div');
    const term = document.createElement('dt');
    const description = document.createElement('dd');
    term.textContent = label;
    description.textContent = value;
    wrapper.append(term, description);
    return wrapper;
  };

  const render = (target, summary = {}) => {
    if (!target) return null;
    const score = Math.max(0, finiteNumber(summary.score));
    const maximum = Math.max(0, finiteNumber(summary.maximum));
    const normalized = normalizeScore(score, maximum);

    const card = document.createElement('section');
    card.className = 'lab-result-scorecard';
    card.setAttribute('aria-label', 'Experiment performance summary');

    const header = document.createElement('header');
    const heading = document.createElement('div');
    const eyebrow = document.createElement('p');
    const title = document.createElement('h3');
    eyebrow.className = 'eyebrow';
    eyebrow.textContent = 'PERFORMANCE SUMMARY';
    title.textContent = summary.title || 'Experiment result';
    heading.append(eyebrow, title);

    const normalizedScore = document.createElement('p');
    normalizedScore.className = 'lab-normalized-score';
    const normalizedLabel = document.createElement('span');
    const normalizedValue = document.createElement('strong');
    const normalizedScale = document.createElement('small');
    normalizedLabel.textContent = 'NORMALIZED SCORE';
    normalizedValue.textContent = normalized.toLocaleString('en-US');
    normalizedScale.textContent = ' / 1,000';
    normalizedScore.append(normalizedLabel, normalizedValue, normalizedScale);
    header.append(heading, normalizedScore);

    const metrics = document.createElement('dl');
    metrics.className = 'lab-result-metrics';
    metrics.append(
      metric(summary.scoreLabel || 'Game score', points(score)),
      metric('Maximum obtainable', points(maximum)),
      metric('Completion', percentage(summary.completion)),
      metric('Accuracy', percentage(summary.accuracy))
    );

    const note = document.createElement('p');
    note.className = 'lab-result-scale-note';
    note.textContent = 'The 0–1,000 score normalizes game performance only. It does not compare the environmental results of different episodes.';
    card.append(header, metrics, note);
    target.replaceChildren(card);
    return { score: rounded(score), maximum: rounded(maximum), normalized };
  };

  window.ImpossibleLabResults = Object.freeze({ SCALE_MAX, normalizeScore, render });
})();
