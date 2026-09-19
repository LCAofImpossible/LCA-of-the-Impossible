#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const registries = Object.fromEntries(
  ['episodes.json', 'crossword.json', 'origins.json', 'timeline.json']
    .map((filename) => [filename, JSON.parse(fs.readFileSync(filename, 'utf8'))])
);
const runtime = fs.readFileSync('assets/ascent.js', 'utf8');

class Node {
  constructor(tag = 'div') {
    this.tag = tag;
    this.id = tag;
    this.children = [];
    this.dataset = {};
    this.style = {};
    this.listeners = {};
    this.classList = { add() {}, toggle() {} };
    this.hidden = false;
  }
  addEventListener(name, listener) { this.listeners[name] = listener; }
  click() { assert(this.listeners.click, `No click handler for ${this.tag}`); this.listeners.click(); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) {
    this.children = nodes.flatMap((node) => node.tag === 'fragment' ? node.children : [node]);
  }
  querySelector() { return new Node(); }
  querySelectorAll(tag) { return this.children.filter((child) => child.tag === tag); }
  setAttribute(name, value) { this[name] = String(value); }
  scrollIntoView() {}
  focus() {}
}

async function load(level) {
  const nodes = new Map();
  const reports = [];
  const get = (id) => {
    if (!nodes.has(id)) nodes.set(id, new Node(id));
    return nodes.get(id);
  };
  const document = {
    getElementById: get,
    createElement: (tag) => new Node(tag),
    createDocumentFragment: () => new Node('fragment'),
    createTextNode: (value) => Object.assign(new Node('text'), { textContent: value })
  };
  const window = {
    ImpossibleLabDifficulty: {
      current: () => level,
      config: () => ({ questions: { explorer: 8, analyst: 12, impossible: 15 }[level] }),
      withLevel: (url) => url
    },
    ImpossibleLabResults: { render: (_target, result) => reports.push(result) },
    matchMedia: () => ({ matches: true }),
    location: { assign() {} }
  };
  const fetch = async (url) => ({ ok: true, json: async () => registries[url] });
  const context = { window, document, fetch, console, Date, Math, Set, Map, Promise };
  vm.createContext(context);
  vm.runInContext(runtime, context);
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(get('ascent-start-button').disabled, false, `${level} failed to load`);
  return { get, reports, questions: window.ImpossibleAscent };
}

function answerCorrect(game, answer) {
  const choices = game.get('ascent-choices').children;
  const button = choices.find((option) => option.dataset.answer === answer);
  assert(button && !button.disabled, 'Correct answer missing or disabled');
  button.click();
  assert(!game.get('ascent-feedback').hidden, 'No sourced feedback shown');
  game.get('ascent-next').click();
}

(async () => {
  const day = new Date().toISOString().slice(0, 10);
  for (const [level, length] of [['explorer', 8], ['analyst', 12], ['impossible', 15]]) {
    const game = await load(level);
    const args = [registries['episodes.json'], registries['crossword.json'], registries['origins.json'], registries['timeline.json'], `${day}:${level}:ascent-v1`];
    const first = game.questions.buildBank(...args);
    const second = game.questions.buildBank(...args);
    assert.equal(first.deck.length, length);
    assert.equal(new Set(first.deck.map((question) => question.number)).size, length);
    assert.deepEqual(first.deck.map((question) => [question.number, question.options]),
      second.deck.map((question) => [question.number, question.options]), 'Daily challenge changed within one archive snapshot');
    first.deck.forEach((question) => {
      assert.equal(question.options.length, 4);
      assert.equal(new Set(question.options).size, 4);
      assert.equal(question.options.filter((option) => option === question.answer).length, 1);
      assert.equal(question.source, question.episode.url);
      if (question.type === 'lens') assert.equal(question.answer, question.episode.lcaLabel);
      if (question.type === 'hotspot') assert.equal(question.answer, question.episode.hotspot);
    });
  }

  const analyst = await load('analyst');
  const deck = analyst.questions.buildBank(registries['episodes.json'], registries['crossword.json'], registries['origins.json'], registries['timeline.json'], `${day}:analyst:ascent-v1`).deck;
  analyst.get('ascent-start-button').click();
  deck.forEach((question) => answerCorrect(analyst, question.answer));
  assert.equal(analyst.reports.length, 1);
  assert.deepEqual([analyst.reports[0].score, analyst.reports[0].maximum, analyst.reports[0].completion, analyst.reports[0].accuracy], [1200, 1200, 100, 100]);
  assert.equal(analyst.get('ascent-final').hidden, false);
  assert.equal(analyst.get('ascent-review-list').children.length, 12);

  const explorer = await load('explorer');
  const challenge = explorer.questions.buildBank(registries['episodes.json'], registries['crossword.json'], registries['origins.json'], registries['timeline.json'], `${day}:explorer:ascent-v1`);
  explorer.get('ascent-start-button').click();
  explorer.get('ascent-half').click();
  assert.equal(explorer.get('ascent-choices').children.filter((choice) => choice.disabled).length, 2);
  explorer.get('ascent-hint').click();
  assert.equal(explorer.get('ascent-assist-hint').hidden, false);
  explorer.get('ascent-swap').click();
  const replacement = challenge.reserve.find((question) => question.type === challenge.deck[0].type);
  answerCorrect(explorer, replacement.answer);
  challenge.deck.slice(1, 4).forEach((question) => answerCorrect(explorer, question.answer));
  assert.equal(explorer.get('ascent-secured').textContent, '325 pts');
  const wrong = explorer.get('ascent-choices').children.find((choice) => choice.dataset.answer !== challenge.deck[4].answer);
  wrong.click();
  explorer.get('ascent-next').click();
  assert.equal(explorer.reports[0].score, 325, 'Checkpoint and assists must both affect the result');
  assert.equal(explorer.reports[0].maximum, 800);
  assert.equal(explorer.get('ascent-review-list').children.length, 5);
  console.log('Impossible Ascent QA: PASS (deterministic 8/12/15 questions, assists, checkpoints, result, source review)');
})().catch((error) => { console.error(error); process.exitCode = 1; });
