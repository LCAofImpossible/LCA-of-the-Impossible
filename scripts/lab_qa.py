#!/usr/bin/env python3
"""Validate Impossible Lab registry coverage, gameplay and publication wiring."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
LAB_CSS_VERSION = "20260911-run1"
HUB_VERSION = "20260911-run2"
GUESS_VERSION = "20260911-results1"
NAV_VERSION = "20260911-navigation1"
ACTION_VERSION = "20260911-navigation1"
RESULTS_VERSION = "20260911-run1"
PROGRESS_VERSION = "20260911-score1"
RUN_VERSION = "20260911-run1"
REQUIRED_FIELDS = (
    "number", "slug", "title", "url", "seasonLabel", "lcaLabel", "lcaCharacteristics",
    "result", "hotspot", "functionalUnit", "subjectDescription",
)
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"Missing file: {path}")
        return ""
    return target.read_text(encoding="utf-8")


def check_registry() -> int:
    try:
        registry = json.loads(read("episodes.json") or "{}")
    except json.JSONDecodeError as exc:
        fail(f"episodes.json is invalid JSON: {exc}")
        return 0
    episodes = registry.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        fail("episodes.json contains no playable episode records")
        return 0
    for episode in episodes:
        number = episode.get("number", "?") if isinstance(episode, dict) else "?"
        if not isinstance(episode, dict):
            fail("episodes.json contains a non-object episode record")
            continue
        for field in REQUIRED_FIELDS:
            value = episode.get(field)
            valid = bool(value) if not isinstance(value, list) else bool(value)
            if not valid:
                fail(f"Episode #{number}: Impossible Lab clue source {field} is missing")
    return len(episodes)


def check_page(episode_count: int) -> None:
    text = read("lab.html")
    required = (
        'data-page="lab"',
        "IMPOSSIBLE LAB · EXPERIMENT 01",
        "Guess the <span>Impossible.</span>",
        'id="lab-clue-list"',
        'id="lab-answer-form"',
        'id="lab-answer-input"',
        'id="lab-reveal"',
        'id="lab-result"',
        'aria-live="assertive"',
        'href="archive.html"',
        f"assets/lab.css?v={LAB_CSS_VERSION}",
        f"assets/lab.js?v={GUESS_VERSION}",
        f"assets/lab-nav.js?v={NAV_VERSION}",
        f"assets/lab-actions.js?v={ACTION_VERSION}",
        f"assets/lab-progress.js?v={PROGRESS_VERSION}",
        f"assets/lab-run.js?v={RUN_VERSION}",
        f"assets/lab-results.js?v={RESULTS_VERSION}",
        'data-lab-game="guess"',
        'data-lab-game-nav',
        'class="lab-route-bar"',
        'EXPERIMENT 01 OF 04 · CURRENT GAME',
        'id="lab-new-case"',
        'data-lab-another',
        'data-lab-result-scorecard',
        'href="impossible-lab.html"',
        "assets/telemetry.css?v=20260820-telemetry1",
        "assets/telemetry.js?v=20260820-telemetry1",
        'type="application/rss+xml"',
        'href="feed.xml"',
    )
    for token in required:
        if token not in text:
            fail(f"lab.html: required token missing: {token}")
    if text.count('data-clue-index=') != 5:
        fail("lab.html must expose exactly five ordered clue slots")
    body = text.split("<body", 1)[-1]
    if "assets/images/episodes/" in body:
        fail("lab.html renders a catalogue cover in the page body")
    if re.search(rf'>\s*{episode_count}\s*<', body):
        fail("lab.html hard-codes the current episode count")


def check_runtime() -> None:
    text = read("assets/lab.js")
    required = (
        "const SCORE_STEPS = [500, 400, 300, 200, 100]",
        "const CLUE_LABELS = ['Season', 'Inventory', 'Impact', 'Function', 'Final clue']",
        "registry.episodes",
        "fetch('episodes.json'",
        "episode.seasonLabel",
        "episode.lcaLabel",
        "episode.lcaCharacteristics",
        "episode.result",
        "episode.hotspot",
        "episode.functionalUnit",
        "episode.subjectDescription",
        "structuredMetadata?.model",
        "titlePattern(episode.title)",
        "replaceChildren(fragment)",
        "showResult(true, SCORE_STEPS[state.clueIndex])",
        "showResult(false)",
        "state.unused.splice",
        "credentials: 'same-origin'",
        "state.attempts += 1",
        "resultSystem?.render(elements.resultScorecard",
    )
    for token in required:
        if token not in text:
            fail(f"assets/lab.js: required gameplay token missing: {token}")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "assets/images/episodes/"):
        if forbidden in text:
            fail(f"assets/lab.js: forbidden persistence or cover token present: {forbidden}")
    registry = json.loads(read("episodes.json") or "{}")
    for episode in registry.get("episodes", []):
        title = episode.get("title")
        if isinstance(title, str) and len(title) > 3 and title in text:
            fail(f"assets/lab.js hard-codes an episode title: {title}")


def check_styles() -> None:
    text = read("assets/lab.css")
    for token in (
        ".lab-shell", ".lab-workspace", ".lab-clue.is-locked", ".lab-clue.is-current",
        ".lab-result[hidden]", ".lab-home-preview", ".lab-route-bar", ".lab-end-actions",
        ".lab-result-scorecard", ".lab-result-metrics", ".lab-case-debrief",
        ".lab-record-band", ".lab-record-state",
        ".lab-run-banner", ".lab-run-result",
        "@media(max-width:760px)",
        "@media(prefers-reduced-motion:reduce)",
    ):
        if token not in text:
            fail(f"assets/lab.css: required responsive token missing: {token}")


def check_shared_navigation_runtime() -> None:
    navigation = read("assets/lab-nav.js")
    actions = read("assets/lab-actions.js")
    results = read("assets/lab-results.js")
    progress = read("assets/lab-progress.js")
    for token in ("fetch('lab-games.json'", "aria-current", "status.textContent = 'Current'"):
        if token not in navigation:
            fail(f"assets/lab-nav.js: required current-game token missing: {token}")
    for token in (
        "fetch('lab-games.json'", "game.id !== currentGame", "game.status === 'live'",
        "window.location.assign(selected.url)", "window.location.assign('impossible-lab.html')",
        "credentials: 'same-origin'",
    ):
        if token not in actions:
            fail(f"assets/lab-actions.js: required routing token missing: {token}")
    for token in (
        "const SCALE_MAX = 1000", "normalizeScore", "finiteNumber(score) / safeMaximum",
        "scoreLabel || 'Game score'", "metric('Maximum obtainable'", "metric('Completion'",
        "metric('Accuracy'", "It does not compare the environmental results of different episodes",
        "target.replaceChildren(card)",
    ):
        if token not in results:
            fail(f"assets/lab-results.js: required result-system token missing: {token}")
    for token in (
        "const STORAGE_KEY = 'lca-impossible-lab-progress-v1'", "window.localStorage",
        "const GAME_IDS = Object.freeze(['guess', 'crossword', 'alphabet', 'spin'])",
        "const LAB_MAX = GAME_IDS.length * SCORE_SCALE", "bestScore", "bestNormalized",
        "previous.bestScore", "previous.bestNormalized", "summarize", "clear",
    ):
        if token not in progress:
            fail(f"assets/lab-progress.js: required personal-record token missing: {token}")
    for token in (
        "progressSystem?.record", "NEW GAME RECORD", "Best normalized", "Lab Score",
        "Experiments completed", "No record this time", "window.ImpossibleLabRun?.record",
        "IMPOSSIBLE LAB RUN COMPLETE", "Continue the Run",
    ):
        if token not in results:
            fail(f"assets/lab-results.js: required record-display token missing: {token}")
    for name, source in (("navigation", navigation), ("actions", actions), ("results", results)):
        for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML"):
            if forbidden in source:
                fail(f"Shared Lab {name} runtime contains forbidden persistence or injection token: {forbidden}")
    for forbidden in ("document.cookie", "sessionStorage", "innerHTML", "fetch(", "XMLHttpRequest"):
        if forbidden in progress:
            fail(f"assets/lab-progress.js: forbidden tracking, injection or network token present: {forbidden}")
    for asset in ("assets/lab-results.js", "assets/lab-progress.js"):
        syntax = subprocess.run(
            ["node", "--check", str(ROOT / asset)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if syntax.returncode:
            fail(f"{asset} syntax validation failed: {syntax.stderr or syntax.stdout}")

    behavior_script = r"""
const fs = require('fs');
const vm = require('vm');
const memory = new Map();
const localStorage = {
  setItem: (key, value) => memory.set(key, String(value)),
  getItem: (key) => memory.has(key) ? memory.get(key) : null,
  removeItem: (key) => memory.delete(key)
};
const context = { window: { localStorage }, console };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/lab-progress.js', 'utf8'), context);
const store = context.window.ImpossibleLabProgress;
const first = store.record('guess', { score: 250, maximum: 500, normalized: 500 });
const lower = store.record('guess', { score: 100, maximum: 500, normalized: 200 });
const second = store.record('crossword', { score: 400, maximum: 500, normalized: 800 });
if (!first.saved || first.summary.total !== 500) process.exit(1);
if (lower.summary.games.guess.bestScore !== 250 || lower.summary.games.guess.bestNormalized !== 500) process.exit(2);
if (second.summary.total !== 1300 || second.summary.completed !== 2 || second.summary.maximum !== 4000) process.exit(3);
if (!store.clear() || store.summarize().total !== 0) process.exit(4);
"""
    behavior = subprocess.run(
        ["node", "-e", behavior_script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if behavior.returncode:
        fail(f"assets/lab-progress.js behavior validation failed: {behavior.stderr or behavior.stdout}")


def check_run() -> None:
    page = read("impossible-lab-run.html")
    for token in (
        'data-lab-run-page', "Four games.<br><span>One run.</span>", "Run Score",
        'data-run-total', 'data-run-stages', 'data-run-start', 'data-run-continue',
        'data-run-restart', 'data-run-clear', "Run Score vs Lab Score",
        'href="impossible-lab.html"', f"assets/lab.css?v={LAB_CSS_VERSION}",
        f"assets/lab-run.css?v={RUN_VERSION}", f"assets/lab-progress.js?v={PROGRESS_VERSION}",
        f"assets/lab-run.js?v={RUN_VERSION}", f"assets/lab-run-page.js?v={RUN_VERSION}",
        "assets/telemetry.js?v=20260820-telemetry1", "LAB-RUN-SEO:START",
    ):
        if token not in page:
            fail(f"impossible-lab-run.html: required Run token missing: {token}")
    if page.count('data-run-stage') != 5:
        fail("impossible-lab-run.html must expose one stage container plus four static fallback stages")

    runtime = read("assets/lab-run.js")
    for token in (
        "const STORAGE_KEY = 'lca-impossible-lab-run-v1'", "window.localStorage",
        "new URLSearchParams(window.location.search).get('run') === '1'",
        "before.nextGameId !== gameId", "RUN_MAX", "summary.completed + 1",
        "Return to the Run", "createGameBanner", "removeItem(STORAGE_KEY)",
    ):
        if token not in runtime:
            fail(f"assets/lab-run.js: required sequential-Run token missing: {token}")
    for forbidden in ("document.cookie", "sessionStorage", "innerHTML", "fetch(", "XMLHttpRequest"):
        if forbidden in runtime:
            fail(f"assets/lab-run.js: forbidden tracking, injection or network token present: {forbidden}")

    page_runtime = read("assets/lab-run-page.js")
    for token in (
        "runSystem.summarize()", "runSystem.start()", "runSystem.clear()",
        "url.searchParams.set('run', '1')", "fetch('lab-games.json'",
        "stages.replaceChildren(fragment)", "Personal game records and the Lab Score will be preserved",
    ):
        if token not in page_runtime:
            fail(f"assets/lab-run-page.js: required Run-page token missing: {token}")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML", "XMLHttpRequest"):
        if forbidden in page_runtime:
            fail(f"assets/lab-run-page.js: forbidden persistence or injection token present: {forbidden}")

    styles = read("assets/lab-run.css")
    for token in (
        ".lab-run-shell", ".lab-run-board", ".lab-run-stage.is-current",
        ".lab-run-stage.is-complete", ".lab-run-explainer",
        "@media(max-width:620px)", "@media(prefers-reduced-motion:reduce)",
    ):
        if token not in styles:
            fail(f"assets/lab-run.css: required responsive token missing: {token}")

    for asset in ("assets/lab-run.js", "assets/lab-run-page.js"):
        syntax = subprocess.run(
            ["node", "--check", str(ROOT / asset)], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )
        if syntax.returncode:
            fail(f"{asset} syntax validation failed: {syntax.stderr or syntax.stdout}")

    behavior_script = r"""
const fs = require('fs');
const vm = require('vm');
const memory = new Map([['lca-impossible-lab-progress-v1', 'preserve-me']]);
const localStorage = {
  setItem: (key, value) => memory.set(key, String(value)),
  getItem: (key) => memory.has(key) ? memory.get(key) : null,
  removeItem: (key) => memory.delete(key)
};
const context = {
  window: {
    localStorage,
    location: { search: '?run=1' },
    ImpossibleLabProgress: {
      available: true,
      GAME_IDS: Object.freeze(['guess', 'crossword', 'alphabet', 'spin']),
      SCORE_SCALE: 1000
    }
  },
  document: { body: null },
  URLSearchParams,
  console
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/lab-run.js', 'utf8'), context);
const run = context.window.ImpossibleLabRun;
const started = run.start();
if (!started.saved || started.summary.nextGameId !== 'guess' || started.summary.total !== 0) process.exit(1);
const guess = run.record('guess', { score: 250, maximum: 500, normalized: 500 });
if (!guess.accepted || guess.summary.nextGameId !== 'crossword' || guess.summary.total !== 500) process.exit(2);
if (run.record('alphabet', { score: 600, maximum: 1000, normalized: 600 }).accepted) process.exit(3);
if (run.record('guess', { score: 500, maximum: 500, normalized: 1000 }).accepted) process.exit(4);
run.record('crossword', { score: 400, maximum: 500, normalized: 800 });
run.record('alphabet', { score: 900, maximum: 1500, normalized: 600 });
const final = run.record('spin', { score: 900, maximum: 1000, normalized: 900 });
if (!final.accepted || !final.summary.complete || final.summary.total !== 2800 || final.summary.maximum !== 4000) process.exit(5);
if (!run.clear() || run.summarize().total !== 0 || memory.get('lca-impossible-lab-progress-v1') !== 'preserve-me') process.exit(6);
"""
    behavior = subprocess.run(
        ["node", "-e", behavior_script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if behavior.returncode:
        fail(f"assets/lab-run.js behavior validation failed: {behavior.stderr or behavior.stdout}")


def check_hub() -> None:
    try:
        registry = json.loads(read("lab-games.json") or "{}")
    except json.JSONDecodeError as exc:
        fail(f"lab-games.json is invalid JSON: {exc}")
        registry = {}
    games = registry.get("games", [])
    if not isinstance(games, list) or len(games) != 4:
        fail("lab-games.json must expose exactly four live experiments")
        games = []
    for game in games:
        if not isinstance(game, dict):
            fail("lab-games.json contains a non-object game record")
            continue
        for field in ("id", "number", "title", "description", "summary", "duration", "category", "url", "status"):
            if not game.get(field):
                fail(f"lab-games.json: {game.get('id', '?')} is missing {field}")
        if game.get("status") != "live":
            fail(f"lab-games.json: {game.get('id', '?')} is not live")

    page = read("impossible-lab.html")
    for token in (
        'data-lab-hub', 'data-lab-hub-grid', 'data-random-game',
        'data-lab-score-panel', 'data-lab-score-total', 'data-lab-score-breakdown', 'data-lab-reset',
        "Impossible Lab Run", "Start Lab Run →", 'class="lab-hub-actions"', 'href="impossible-lab-run.html"',
        "Choose your <span>experiment.</span>", "REGISTRY-DRIVEN",
        'href="lab.html"', 'href="lab-crossword.html"', 'href="lab-alphabet.html"', 'href="lab-spin.html"',
        f"assets/lab-hub.css?v={HUB_VERSION}", f"assets/lab-progress.js?v={PROGRESS_VERSION}", f"assets/lab-hub.js?v={HUB_VERSION}",
        "assets/telemetry.css?v=20260820-telemetry1", "assets/telemetry.js?v=20260820-telemetry1",
        'type="application/rss+xml"', 'href="feed.xml"',
    ):
        if token not in page:
            fail(f"impossible-lab.html: required hub token missing: {token}")
    if page.count('class="lab-hub-card"') != 4:
        fail("impossible-lab.html must retain four static fallback game cards")

    runtime = read("assets/lab-hub.js")
    for token in (
        "fetch('lab-games.json'", "game.summary", "game.duration", "game.category",
        "replaceChildren(fragment)", "window.location.assign(url)", "credentials: 'same-origin'",
        "progressSystem.summarize()", "summary.total", "summary.games[game.id]", "progressSystem?.clear()",
    ):
        if token not in runtime:
            fail(f"assets/lab-hub.js: required catalogue token missing: {token}")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML"):
        if forbidden in runtime:
            fail(f"assets/lab-hub.js: forbidden persistence or injection token present: {forbidden}")

    styles = read("assets/lab-hub.css")
    for token in (".lab-hub-actions", ".lab-score-panel", ".lab-score-total", ".lab-score-breakdown", ".lab-reset-records", ".lab-run-entry", ".lab-hub-grid", ".lab-hub-card", ".lab-hub-note", "@media(max-width:620px)", "@media(prefers-reduced-motion:reduce)"):
        if token not in styles:
            fail(f"assets/lab-hub.css: required responsive token missing: {token}")


def check_discovery() -> None:
    home = read("index.html")
    for token in (
        "LAB-HOME:START", "IMPOSSIBLE LAB", 'href="impossible-lab.html"', "Four registry-driven experiments",
        f"assets/lab.css?v={LAB_CSS_VERSION}",
    ):
        if token not in home:
            fail(f"index.html: Impossible Lab entry point missing {token}")

    sitemap = read("sitemap.xml")
    try:
        root = ET.fromstring(sitemap)
    except ET.ParseError as exc:
        fail(f"sitemap.xml is invalid XML: {exc}")
    else:
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text for node in root.findall("sm:url/sm:loc", ns)]
        if urls.count(BASE_URL + "impossible-lab.html") != 1:
            fail("sitemap.xml must contain impossible-lab.html exactly once")
        if urls.count(BASE_URL + "impossible-lab-run.html") != 1:
            fail("sitemap.xml must contain impossible-lab-run.html exactly once")
        if urls.count(BASE_URL + "lab.html") != 1:
            fail("sitemap.xml must contain lab.html exactly once")
        if urls.count(BASE_URL + "lab-alphabet.html") != 1:
            fail("sitemap.xml must contain lab-alphabet.html exactly once")
        if urls.count(BASE_URL + "lab-spin.html") != 1:
            fail("sitemap.xml must contain lab-spin.html exactly once")

    manifest = read("site.webmanifest")
    if "/LCA-of-the-Impossible/impossible-lab.html" not in manifest:
        fail("site.webmanifest must expose the Impossible Lab shortcut")

    for script, tokens in {
        "scripts/phase5_sync.py": ('"impossible-lab.html"', '"impossible-lab-run.html"', 'href="{prefix}impossible-lab.html"'),
        "scripts/telemetry_sync.py": ('"impossible-lab.html"', '"impossible-lab-run.html"'),
        "scripts/rss_sync.py": ('"impossible-lab.html"', '"impossible-lab-run.html"'),
        "scripts/live_site_qa.py": ('"impossible-lab.html"', '"impossible-lab-run.html"', '"assets/lab-hub.css"', '"assets/lab-hub.js"', '"assets/lab-run.js"'),
        "scripts/publication_qa.py": ('"lab_sync.py"', '"lab_qa.py"'),
        ".github/workflows/seo-sync.yml": ("python scripts/lab_sync.py", "impossible-lab.html", "impossible-lab-run.html", "assets/lab-hub.css", "assets/lab-hub.js", "assets/lab-actions.js", "assets/lab-results.js", "assets/lab-progress.js", "assets/lab-run.js", "assets/lab-run-page.js"),
    }.items():
        source = read(script)
        for token in tokens:
            if token not in source:
                fail(f"{script}: Impossible Lab publication token missing: {token}")


def check_readme() -> None:
    text = read("README.md")
    for token in (
        "## 39. Impossible Lab and registry-driven games — mandatory",
        "Guess the Impossible",
        "Cross the Impossible",
        "The Impossible Alphabet",
        "Spin the Impossible",
        "`impossible-lab.html` is the canonical entry point",
        "summary", "duration", "category",
        "500 → 400 → 300 → 200 → 100",
        "Catalogue covers remain limited to Homepage and Archive",
        "scripts/lab_qa.py",
        "scripts/alphabet_qa.py",
        "scripts/spin_qa.py",
        "### 39.5 Shared result system",
        "normalized score",
        "game performance only",
        "Lab Score",
        "lca-impossible-lab-progress-v1",
        "Reset records",
        "### 39.6 Impossible Lab Run",
        "lca-impossible-lab-run-v1",
        "one consecutive circuit",
    ):
        if token not in text:
            fail(f"README.md: Impossible Lab rule missing: {token}")


def main() -> int:
    count = check_registry()
    check_page(count)
    check_runtime()
    check_shared_navigation_runtime()
    check_run()
    check_styles()
    check_hub()
    check_discovery()
    check_readme()

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nImpossible Lab QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Impossible Lab QA: PASS ({count} registry-driven cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
