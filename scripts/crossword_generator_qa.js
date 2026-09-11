#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const engine = require('../assets/crossword-generator.js');

const root = path.resolve(__dirname, '..');
const episodes = new Map(JSON.parse(fs.readFileSync(path.join(root, 'episodes.json'), 'utf8')).episodes
  .map((episode) => [episode.number, episode]));
const entries = JSON.parse(fs.readFileSync(path.join(root, 'crossword.json'), 'utf8')).entries
  .map((entry) => ({ ...entry, episode: episodes.get(entry.episodeNumber) }));

const failures = [];
let smallestGrid = Infinity;
let largestRows = 0;
let largestColumns = 0;
const profiles = [
  { level: 'explorer', targetWords: 8, minWords: 6 },
  { level: 'analyst', targetWords: 10, minWords: 8 },
  { level: 'impossible', targetWords: 12, minWords: 10 }
];

for (const profile of profiles) {
  for (let index = 0; index < 24; index += 1) {
    const layout = engine.generate(entries, {
      seed: `${profile.level}-crossword-qa-${index}`,
      targetWords: profile.targetWords,
      minWords: profile.minWords,
      attempts: 20
    });
    const errors = engine.validate(layout);
    if (layout.entries.length !== profile.targetWords) errors.push(`Expected ${profile.targetWords} entries, found ${layout.entries.length}`);
    if (layout.rows > 25 || layout.cols > 25) errors.push(`Grid is too large: ${layout.rows} x ${layout.cols}`);
    if (errors.length) failures.push(`${profile.level} seed ${index}: ${errors.join('; ')}`);
    smallestGrid = Math.min(smallestGrid, layout.entries.length);
    largestRows = Math.max(largestRows, layout.rows);
    largestColumns = Math.max(largestColumns, layout.cols);
  }
}

if (failures.length) {
  failures.forEach((failure) => console.error(`ERROR: ${failure}`));
  process.exit(1);
}

console.log(`Crossword generator QA: PASS (72 level-aware seeds, ${smallestGrid}–12 words, max ${largestRows} x ${largestColumns})`);
