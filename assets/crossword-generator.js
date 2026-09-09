(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.ImpossibleCrossword = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, () => {
  'use strict';

  const keyOf = (row, col) => `${row},${col}`;

  const normalizeAnswer = (value = '') => String(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '');

  const hashSeed = (value) => {
    let hash = 2166136261;
    for (const char of String(value)) {
      hash ^= char.charCodeAt(0);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  };

  const seededRandom = (seed) => {
    let state = hashSeed(seed) || 1;
    return () => {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  };

  const shuffled = (items, random) => {
    const result = [...items];
    for (let index = result.length - 1; index > 0; index -= 1) {
      const swap = Math.floor(random() * (index + 1));
      [result[index], result[swap]] = [result[swap], result[index]];
    }
    return result;
  };

  const boundsFor = (grid) => {
    const cells = [...grid.values()];
    if (!cells.length) return { minRow: 0, maxRow: 0, minCol: 0, maxCol: 0, rows: 1, cols: 1, area: 1 };
    const rows = cells.map((cell) => cell.row);
    const cols = cells.map((cell) => cell.col);
    const minRow = Math.min(...rows);
    const maxRow = Math.max(...rows);
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);
    return {
      minRow,
      maxRow,
      minCol,
      maxCol,
      rows: maxRow - minRow + 1,
      cols: maxCol - minCol + 1,
      area: (maxRow - minRow + 1) * (maxCol - minCol + 1)
    };
  };

  const cloneGrid = (grid) => new Map([...grid].map(([key, cell]) => [key, {
    ...cell,
    directions: new Set(cell.directions),
    entryIds: new Set(cell.entryIds)
  }]));

  const canPlace = (grid, answer, row, col, direction) => {
    const rowStep = direction === 'down' ? 1 : 0;
    const colStep = direction === 'across' ? 1 : 0;
    const endRow = row + rowStep * (answer.length - 1);
    const endCol = col + colStep * (answer.length - 1);
    if (grid.has(keyOf(row - rowStep, col - colStep)) || grid.has(keyOf(endRow + rowStep, endCol + colStep))) return null;

    let crossings = 0;
    for (let index = 0; index < answer.length; index += 1) {
      const cellRow = row + rowStep * index;
      const cellCol = col + colStep * index;
      const existing = grid.get(keyOf(cellRow, cellCol));
      if (existing) {
        if (existing.char !== answer[index] || existing.directions.has(direction)) return null;
        crossings += 1;
        continue;
      }
      const neighbours = direction === 'across'
        ? [[cellRow - 1, cellCol], [cellRow + 1, cellCol]]
        : [[cellRow, cellCol - 1], [cellRow, cellCol + 1]];
      if (neighbours.some(([nextRow, nextCol]) => grid.has(keyOf(nextRow, nextCol)))) return null;
    }
    return crossings > 0 ? { crossings } : null;
  };

  const placeWord = (grid, item, row, col, direction, entryId) => {
    const next = cloneGrid(grid);
    const rowStep = direction === 'down' ? 1 : 0;
    const colStep = direction === 'across' ? 1 : 0;
    for (let index = 0; index < item.answer.length; index += 1) {
      const cellRow = row + rowStep * index;
      const cellCol = col + colStep * index;
      const key = keyOf(cellRow, cellCol);
      const existing = next.get(key);
      if (existing) {
        existing.directions.add(direction);
        existing.entryIds.add(entryId);
      } else {
        next.set(key, {
          row: cellRow,
          col: cellCol,
          char: item.answer[index],
          directions: new Set([direction]),
          entryIds: new Set([entryId])
        });
      }
    }
    return next;
  };

  const placementOptions = (grid, item) => {
    const options = [];
    for (const cell of grid.values()) {
      for (let index = 0; index < item.answer.length; index += 1) {
        if (item.answer[index] !== cell.char) continue;
        for (const direction of ['across', 'down']) {
          const row = cell.row - (direction === 'down' ? index : 0);
          const col = cell.col - (direction === 'across' ? index : 0);
          const verdict = canPlace(grid, item.answer, row, col, direction);
          if (!verdict) continue;
          options.push({ row, col, direction, crossings: verdict.crossings });
        }
      }
    }
    const unique = new Map();
    for (const option of options) unique.set(`${option.row}:${option.col}:${option.direction}`, option);
    return [...unique.values()];
  };

  const layoutScore = (grid, placements) => {
    const bounds = boundsFor(grid);
    const totalLetters = placements.reduce((sum, placement) => sum + placement.item.answer.length, 0);
    const crossings = totalLetters - grid.size;
    const imbalance = Math.abs(bounds.rows - bounds.cols);
    const longestSide = Math.max(bounds.rows, bounds.cols);
    return placements.length * 100000 + crossings * 850 - bounds.area * 18 - imbalance * 65 - longestSide * 80;
  };

  const makeAttempt = (items, random, targetWords, attemptIndex) => {
    const seasonOne = items.filter((item) => item.episode?.seasonNumber === 1);
    const preferred = items.filter((item) => item.answer.length >= 5 && item.answer.length <= 14);
    const firstPool = seasonOne.length && attemptIndex % 3 !== 2 ? seasonOne : (preferred.length ? preferred : items);
    const first = shuffled(firstPool, random)[0];
    if (!first) return null;

    const firstDirection = random() > 0.5 ? 'across' : 'down';
    let grid = placeWord(new Map(), first, 0, 0, firstDirection, `entry-${first.episodeNumber}`);
    const placements = [{ item: first, row: 0, col: 0, direction: firstDirection, crossings: 0 }];
    const remaining = shuffled(items.filter((item) => item !== first), random)
      .slice(0, Math.min(20, items.length - 1));

    while (placements.length < targetWords && remaining.length) {
      const candidates = [];
      for (const item of remaining) {
        for (const option of placementOptions(grid, item)) {
          const entryId = `entry-${item.episodeNumber}`;
          const nextGrid = placeWord(grid, item, option.row, option.col, option.direction, entryId);
          const bounds = boundsFor(nextGrid);
          const seasonBonus = item.episode?.seasonNumber === 1 && !placements.some((placement) => placement.item.episode?.seasonNumber === 1) ? 500 : 0;
          const score = option.crossings * 160 - bounds.area * 0.22 - Math.max(bounds.rows, bounds.cols) * 1.5 + seasonBonus + random() * 7;
          candidates.push({ item, option, nextGrid, score });
        }
      }
      if (!candidates.length) break;
      candidates.sort((a, b) => b.score - a.score);
      const selected = candidates[0];
      grid = selected.nextGrid;
      placements.push({ item: selected.item, ...selected.option });
      remaining.splice(remaining.indexOf(selected.item), 1);
    }
    return { grid, placements, score: layoutScore(grid, placements) };
  };

  const fallbackLayout = (items) => {
    const fallback = [
      [43, 0, 1, 'across'], [32, 0, 5, 'down'], [44, 2, 1, 'down'],
      [56, 2, 3, 'down'], [48, 2, 7, 'down'], [46, 2, 10, 'down'],
      [49, 3, 5, 'across'], [4, 4, 0, 'across'], [36, 7, 6, 'across'], [45, 9, 6, 'across']
    ];
    const lookup = new Map(items.map((item) => [item.episodeNumber, item]));
    if (!fallback.every(([number]) => lookup.has(number))) return null;
    let grid = new Map();
    const placements = [];
    for (const [number, row, col, direction] of fallback) {
      const item = lookup.get(number);
      grid = placeWord(grid, item, row, col, direction, `entry-${number}`);
      placements.push({ item, row, col, direction, crossings: 1 });
    }
    return { grid, placements, score: layoutScore(grid, placements) };
  };

  const finalize = (candidate) => {
    const bounds = boundsFor(candidate.grid);
    const startNumbers = new Map();
    const ordered = [...candidate.placements].sort((left, right) => left.row - right.row || left.col - right.col || left.direction.localeCompare(right.direction));
    let nextNumber = 1;
    for (const placement of ordered) {
      const startKey = keyOf(placement.row, placement.col);
      if (!startNumbers.has(startKey)) startNumbers.set(startKey, nextNumber++);
    }

    const entries = candidate.placements.map((placement) => ({
      id: `entry-${placement.item.episodeNumber}`,
      episodeNumber: placement.item.episodeNumber,
      answer: placement.item.answer,
      clue: placement.item.clue,
      episode: placement.item.episode,
      row: placement.row - bounds.minRow,
      col: placement.col - bounds.minCol,
      direction: placement.direction,
      number: startNumbers.get(keyOf(placement.row, placement.col))
    })).sort((left, right) => left.number - right.number || left.direction.localeCompare(right.direction));

    const cells = new Map();
    for (const entry of entries) {
      const rowStep = entry.direction === 'down' ? 1 : 0;
      const colStep = entry.direction === 'across' ? 1 : 0;
      for (let index = 0; index < entry.answer.length; index += 1) {
        const row = entry.row + rowStep * index;
        const col = entry.col + colStep * index;
        const key = keyOf(row, col);
        const cell = cells.get(key) || { row, col, char: entry.answer[index], entryIds: [] };
        if (!cell.entryIds.includes(entry.id)) cell.entryIds.push(entry.id);
        cells.set(key, cell);
      }
    }
    const normalizedStarts = new Map(entries.map((entry) => [keyOf(entry.row, entry.col), entry.number]));
    return { rows: bounds.rows, cols: bounds.cols, entries, cells, startNumbers: normalizedStarts };
  };

  const generate = (rawItems, options = {}) => {
    const items = rawItems.map((item) => ({ ...item, answer: normalizeAnswer(item.answer) }))
      .filter((item) => item.answer.length >= 4 && item.answer.length <= 20 && item.clue && item.episode);
    const targetWords = Math.min(Math.max(Number(options.targetWords) || 10, 6), items.length);
    const minWords = Math.min(Math.max(Number(options.minWords) || 8, 5), targetWords);
    const attempts = Math.max(Number(options.attempts) || 42, 16);
    const random = seededRandom(options.seed || 'impossible-crossword');
    let best = null;
    for (let attempt = 0; attempt < attempts; attempt += 1) {
      const candidate = makeAttempt(items, random, targetWords, attempt);
      if (!candidate || candidate.placements.length < minWords) continue;
      const seasons = new Set(candidate.placements.map((placement) => placement.item.episode?.seasonNumber));
      if (items.some((item) => item.episode?.seasonNumber === 1) && !seasons.has(1)) continue;
      if (items.some((item) => item.episode?.seasonNumber === 2) && !seasons.has(2)) continue;
      if (!best || candidate.score > best.score) best = candidate;
    }
    if (!best || best.placements.length < minWords) best = fallbackLayout(items);
    if (!best) throw new Error('Unable to generate a connected crossword from the available cases');
    return finalize(best);
  };

  const validate = (layout) => {
    const errors = [];
    const seen = new Set();
    for (const entry of layout.entries || []) {
      if (seen.has(entry.episodeNumber)) errors.push(`Episode #${entry.episodeNumber} is repeated`);
      seen.add(entry.episodeNumber);
      const rowStep = entry.direction === 'down' ? 1 : 0;
      const colStep = entry.direction === 'across' ? 1 : 0;
      for (let index = 0; index < entry.answer.length; index += 1) {
        const cell = layout.cells.get(keyOf(entry.row + rowStep * index, entry.col + colStep * index));
        if (!cell || cell.char !== entry.answer[index]) errors.push(`Entry ${entry.id} has an invalid cell at ${index}`);
      }
    }
    if (!(layout.entries || []).some((entry) => entry.episode?.seasonNumber === 1)) errors.push('No Season I case is present');
    if (!(layout.entries || []).some((entry) => entry.episode?.seasonNumber === 2)) errors.push('No Season II case is present');
    return errors;
  };

  return { generate, validate, normalizeAnswer, seededRandom };
});
