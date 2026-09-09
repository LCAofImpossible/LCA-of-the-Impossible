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

for (let index = 0; index < 120; index += 1) {
  const layout = engine.generate(entries, {
    seed: `crossword-qa-${index}`,
    targetWords: 10,
    minWords: 8,
    attempts: 20
  });
  const errors = engine.validate(layout);
  if (layout.entries.length !== 10) errors.push(`Expected 10 entries, found ${layout.entries.length}`);
  if (layout.rows > 22 || layout.cols > 22) errors.push(`Grid is too large: ${layout.rows} x ${layout.cols}`);
  if (errors.length) failures.push(`Seed ${index}: ${errors.join('; ')}`);
  smallestGrid = Math.min(smallestGrid, layout.entries.length);
  largestRows = Math.max(largestRows, layout.rows);
  largestColumns = Math.max(largestColumns, layout.cols);
}

if (failures.length) {
  failures.forEach((failure) => console.error(`ERROR: ${failure}`));
  process.exit(1);
}

console.log(`Crossword generator QA: PASS (120 seeds, ${smallestGrid} words, max ${largestRows} x ${largestColumns})`);
