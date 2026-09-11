(() => {
  'use strict';

  const SCALE_MAX = 1000;
  const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
  const finiteNumber = (value) => Number.isFinite(Number(value)) ? Number(value) : 0;
  const rounded = (value) => Math.round(finiteNumber(value));
  const percentage = (value) => `${rounded(clamp(finiteNumber(value), 0, 100))}%`;
  const points = (value) => `${rounded(Math.max(0, finiteNumber(value))).toLocaleString('en-US')} pts`;
  const scaledPoints = (value, maximum) => `${rounded(Math.max(0, finiteNumber(value))).toLocaleString('en-US')} / ${rounded(Math.max(0, finiteNumber(maximum))).toLocaleString('en-US')}`;

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
    const gameId = document.body?.dataset?.labGame || '';
    const progressSystem = window.ImpossibleLabProgress;
    const difficultySystem = window.ImpossibleLabDifficulty;
    const level = difficultySystem?.current() || 'analyst';
    const levelDetail = difficultySystem?.detail(level) || { label: 'Analyst' };
    const difficultyUpdate = summary.persist === false
      ? null
      : difficultySystem?.record(gameId, { score, maximum, normalized });
    const progressUpdate = difficultyUpdate
      ? difficultyUpdate.officialUpdate
      : (summary.persist === false ? null : progressSystem?.record(gameId, { score, maximum, normalized }));
    const gameRecord = difficultyUpdate?.record || progressUpdate?.summary?.games?.[gameId];
    const runUpdate = summary.persist === false || level !== 'analyst'
      ? null
      : window.ImpossibleLabRun?.record(gameId, { score, maximum, normalized });

    const card = document.createElement('section');
    card.className = `lab-result-scorecard is-level-${level}`;
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
    normalizedLabel.textContent = `${levelDetail.label.toUpperCase()} · NORMALIZED SCORE`;
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
    note.textContent = level === 'analyst'
      ? 'The 0–1,000 score normalizes game performance only. Analyst results can update the Lab Score; environmental results are never compared.'
      : `The 0–1,000 score normalizes ${levelDetail.label} game performance only. This level has a separate record and does not update the Analyst-based Lab Score.`;
    card.append(header, metrics);

    if ((difficultyUpdate?.saved || progressUpdate?.saved) && gameRecord) {
      const recordBand = document.createElement('section');
      recordBand.className = 'lab-record-band';
      recordBand.setAttribute('aria-label', 'Personal records');

      const recordHeading = document.createElement('div');
      const recordEyebrow = document.createElement('p');
      const recordTitle = document.createElement('h4');
      recordEyebrow.className = 'eyebrow';
      const rawImproved = difficultyUpdate?.rawImproved ?? progressUpdate?.rawImproved;
      const normalizedImproved = difficultyUpdate?.normalizedImproved ?? progressUpdate?.normalizedImproved;
      recordEyebrow.textContent = rawImproved ? `NEW ${levelDetail.label.toUpperCase()} RECORD` : `${levelDetail.label.toUpperCase()} PERSONAL BEST`;
      recordTitle.textContent = points(gameRecord.bestScore);
      recordHeading.append(recordEyebrow, recordTitle);

      const recordMetrics = document.createElement('dl');
      recordMetrics.append(metric(`Best ${levelDetail.label}`, scaledPoints(gameRecord.bestNormalized, progressSystem?.SCORE_SCALE || SCALE_MAX)));
      if (level === 'analyst' && progressUpdate?.summary) {
        recordMetrics.append(
          metric('Lab Score', scaledPoints(progressUpdate.summary.total, progressUpdate.summary.maximum)),
          metric('Experiments completed', `${progressUpdate.summary.completed} / ${progressSystem.GAME_IDS.length}`)
        );
      } else {
        recordMetrics.append(
          metric('Level plays', gameRecord.plays.toLocaleString('en-US')),
          metric('Lab Score', 'Analyst only')
        );
      }

      const recordState = document.createElement('p');
      recordState.className = 'lab-record-state';
      if (level !== 'analyst') {
        recordState.textContent = rawImproved || normalizedImproved
          ? `${levelDetail.label} personal best updated. The official Lab Score remains unchanged.`
          : `No ${levelDetail.label} record this time. The official Lab Score remains unchanged.`;
      } else if (rawImproved && normalizedImproved) {
        recordState.textContent = 'Game record and Lab Score updated.';
      } else if (rawImproved) {
        recordState.textContent = 'Game record updated. Your previous normalized contribution remains higher.';
      } else if (normalizedImproved) {
        recordState.textContent = 'Lab Score improved. Your original game-score record remains unbeaten.';
      } else {
        recordState.textContent = 'No record this time. Try again to improve both targets.';
      }

      recordBand.append(recordHeading, recordMetrics, recordState);
      card.appendChild(recordBand);
    } else if (summary.persist !== false && progressSystem && !progressSystem.available) {
      const unavailable = document.createElement('p');
      unavailable.className = 'lab-record-unavailable';
      unavailable.textContent = 'Personal records cannot be saved because browser storage is unavailable. This result remains visible for the current page only.';
      card.appendChild(unavailable);
    }

    if (runUpdate?.accepted) {
      const runBand = document.createElement('section');
      runBand.className = 'lab-run-result';
      runBand.setAttribute('aria-label', 'Impossible Lab Run progress');

      const runHeading = document.createElement('div');
      const runEyebrow = document.createElement('p');
      const runTitle = document.createElement('h4');
      runEyebrow.className = 'eyebrow';
      runEyebrow.textContent = runUpdate.summary.complete ? 'IMPOSSIBLE LAB RUN COMPLETE' : `RUN STAGE ${runUpdate.summary.completed} COMPLETE`;
      runTitle.textContent = scaledPoints(runUpdate.summary.total, runUpdate.summary.maximum);
      runHeading.append(runEyebrow, runTitle);

      const runMetrics = document.createElement('dl');
      runMetrics.append(
        metric('Stage contribution', scaledPoints(normalized, window.ImpossibleLabRun.SCORE_SCALE)),
        metric('Stages complete', `${runUpdate.summary.completed} / ${window.ImpossibleLabRun.GAME_IDS.length}`)
      );

      const runLink = document.createElement('a');
      runLink.className = 'button';
      runLink.href = 'impossible-lab-run.html';
      runLink.textContent = runUpdate.summary.complete ? 'View final Run result →' : 'Continue the Run →';
      runBand.append(runHeading, runMetrics, runLink);
      card.appendChild(runBand);
    }

    card.appendChild(note);
    target.replaceChildren(card);
    return { score: rounded(score), maximum: rounded(maximum), normalized, level, progress: progressUpdate?.summary || null };
  };

  window.ImpossibleLabResults = Object.freeze({ SCALE_MAX, normalizeScore, render });
})();
