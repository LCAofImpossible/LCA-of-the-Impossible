#!/usr/bin/env python3
"""Validate the Phase 5 Impossible Origins public Lab integration."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_VERSION = "20260918-ascent1"
RESULTS_VERSION = "20260918-ascent1"
ORIGINS_VERSION = "20260917-origins-map1"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"Missing file: {path}")
        return ""
    return target.read_text(encoding="utf-8")


def main() -> int:
    page = read("lab-origins.html")
    for token in (
        'data-lab-game="origins"',
        'data-origins-phase="5"',
        '<meta name="robots" content="index,follow,max-image-preview:large">',
        "ORIGINS-SEO:START",
        "EXPERIMENT 07 OF 08 · CURRENT GAME",
        "Impossible <span>Origins.</span>",
        'id="lab-game-area"',
        'id="origins-map"',
        'class="origins-map-frame"',
        'id="origins-map-hud-name"',
        'id="origins-map-beacon"',
        "public-domain Natural Earth geometry",
        'id="origins-score"',
        'id="origins-region-select"',
        'id="origins-era-options"',
        'id="origins-confirm"',
        'id="origins-reveal"',
        'id="origins-final"',
        'id="origins-final-perfect"',
        'data-lab-difficulty',
        'data-lab-result-scorecard',
        'tabindex="-1" role="button" aria-label="North America" aria-pressed="false" aria-disabled="true"',
        'href="impossible-lab.html"',
        'data-lab-game-nav',
        f"assets/origins.css?v={ORIGINS_VERSION}",
        f"assets/origins.js?v={ORIGINS_VERSION}",
        f"assets/lab-nav.js?v={SHARED_VERSION}",
        f"assets/lab-actions.js?v={SHARED_VERSION}",
        f"assets/lab-progress.js?v={SHARED_VERSION}",
        f"assets/lab-difficulty.js?v={SHARED_VERSION}",
        f"assets/lab-run.js?v={SHARED_VERSION}",
        f"assets/lab-results.js?v={RESULTS_VERSION}",
        "assets/telemetry.js?v=20260820-telemetry1",
    ):
        if token not in page:
            fail(f"lab-origins.html: required token missing: {token}")
    for region in (
        "northern-europe",
        "western-europe",
        "southern-europe-mediterranean",
        "eastern-europe",
        "north-africa",
        "sub-saharan-africa",
        "west-asia",
        "central-asia",
        "south-asia",
        "east-asia",
        "southeast-asia",
        "north-america",
        "latin-america-caribbean",
        "oceania",
    ):
        if f'data-region="{region}"' not in page:
            fail(f"lab-origins.html: map region missing: {region}")
    if "assets/images/episodes/" in page.split("<body", 1)[-1]:
        fail("lab-origins.html must not render catalogue covers in its body")
    if read("sitemap.xml").count("lab-origins.html") != 1:
        fail("Phase 5 Origins route must occur exactly once in the public sitemap")
    games = read("lab-games.json")
    for token in ('"id": "origins"', '"number": 7', '"url": "lab-origins.html"', '"status": "live"'):
        if token not in games:
            fail(f"Phase 5 live Origins registry token missing: {token}")

    runtime = read("assets/origins.js")
    for token in (
        "const SESSION_ROUNDS = 10",
        "const POINTS_PER_COMPONENT = 100",
        "const PERFECT_ORIGIN_BONUS = 50",
        "difficultySystem?.config('origins')",
        "rules.regionChoices",
        "rules.qualifiedFirst",
        "state.score += gained",
        "state.perfectOrigins += 1",
        "ImpossibleLabResults?.render",
        "scoreLabel: 'Origin score'",
        "fetch('episodes.json'",
        "fetch('timeline.json'",
        "fetch('origins.json'",
        "entry?.eligible",
        "episode: episodes.get",
        "timeline: timeline.get",
        "acceptedMapRegions.includes",
        "eraFor(entry.timeline.orderYear)",
        "const REGION_ANCHORS = Object.freeze({",
        "const setMapFocus =",
        "const setMapBeacon =",
        "path.addEventListener('pointerenter'",
        "path.addEventListener('keydown'",
        "elements.regionSelect.addEventListener('change'",
        "replaceChildren",
        "setControlState(true)",
        "entry.episode.subjectDescription",
        "entry.locationBasis",
        "entry.timeline.source",
        "entry.episode.url",
        "Review your result and record status below",
    ):
        if token not in runtime:
            fail(f"assets/origins.js: required runtime token missing: {token}")
    for forbidden in (
        "document.cookie",
        "localStorage",
        "sessionStorage",
        "innerHTML",
        "datePublished",
        "publicationDate",
        "lcaCharacteristics",
        "hotspot",
    ):
        if forbidden in runtime:
            fail(f"assets/origins.js contains forbidden persistence, injection or unrelated data token: {forbidden}")

    styles = read("assets/origins.css")
    for token in (
        ".origins-workspace",
        ".origins-map-regions path",
        ".origins-map-frame",
        ".origins-map-hud",
        ".origins-map-regions [data-region].is-selected",
        ".origins-map-regions [data-region].is-correct",
        ".origins-map-regions [data-region].is-wrong",
        ".origins-map-regions [data-region].is-unavailable",
        ".origins-map-beacon",
        ".origins-era-option",
        ".origins-reveal",
        ".origins-final",
        "@media(max-width:760px)",
        "@media(max-width:480px)",
        "@media(prefers-reduced-motion:reduce)",
    ):
        if token not in styles:
            fail(f"assets/origins.css: required responsive token missing: {token}")

    difficulty = read("assets/lab-difficulty.js")
    for token in (
        "'lab-origins.html'",
        "origins: Object.freeze({",
        "rounds: 8, regionChoices: 4",
        "rounds: 10, regionChoices: 0",
        "rounds: 12, regionChoices: 0",
        "subjectDescription: false",
        "mapLabels: false",
        "eraRanges: false",
        "qualifiedFirst: true",
        "progressSystem?.GAME_IDS?.includes(gameId)",
    ):
        if token not in difficulty:
            fail(f"assets/lab-difficulty.js: required Origins level token missing: {token}")

    results = read("assets/lab-results.js")
    for token in (
        "const officialGame = Boolean(progressSystem?.GAME_IDS?.includes(gameId))",
        "Game record and Lab Score updated.",
        "window.ImpossibleLabRun?.record",
    ):
        if token not in results:
            fail(f"assets/lab-results.js: required official-record token missing: {token}")

    progress = read("assets/lab-progress.js")
    if "'origins'" not in progress:
        fail("assets/lab-progress.js does not include the Origins Lab Score contribution")
    run = read("assets/lab-run.js")
    if "const SCHEMA_VERSION = 3" not in run or "'origins'" not in run:
        fail("assets/lab-run.js does not expose the eight-stage Ascent extension")

    registry_qa = subprocess.run(
        [sys.executable, str(ROOT / "scripts/origins_qa.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if registry_qa.returncode:
        fail(f"Origins registry QA failed: {registry_qa.stderr or registry_qa.stdout}")

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets/origins.js")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/origins.js syntax validation failed: {syntax.stderr or syntax.stdout}")

    behavior_script = r"""
const fs = require('fs');
const vm = require('vm');
const memory = new Map();
const localStorage = {
  setItem: (key, value) => memory.set(key, String(value)),
  getItem: (key) => memory.has(key) ? memory.get(key) : null,
  removeItem: (key) => memory.delete(key)
};
const document = { body: { dataset: { labGame: 'origins' } }, querySelectorAll: () => [] };
const window = { localStorage, location: { search: '?difficulty=analyst', href: 'https://example.test/lab-origins.html?difficulty=analyst' } };
const context = { window, document, console, URL, URLSearchParams, CustomEvent: class CustomEvent {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/lab-progress.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('assets/lab-difficulty.js', 'utf8'), context);
const official = context.window.ImpossibleLabProgress;
const levels = context.window.ImpossibleLabDifficulty;
if (levels.config('origins', 'explorer').rounds !== 8) process.exit(1);
if (levels.config('origins', 'analyst').rounds !== 10) process.exit(2);
if (levels.config('origins', 'impossible').rounds !== 12) process.exit(3);
const update = levels.record('origins', { score: 1750, maximum: 2500, normalized: 700 });
if (!update.saved || update.record.bestNormalized !== 700) process.exit(4);
if (!update.officialUpdate?.saved || official.summarize().games.origins.bestNormalized !== 700) process.exit(5);
if (official.summarize().maximum !== 8000 || official.summarize().completed !== 1) process.exit(6);
if (levels.withPlayTarget('lab-origins.html', 'impossible') !== 'lab-origins.html?difficulty=impossible#lab-game-area') process.exit(7);
"""
    behavior = subprocess.run(
        ["node", "-e", behavior_script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if behavior.returncode:
        fail(f"Impossible Origins level behavior validation failed: {behavior.stderr or behavior.stdout}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nImpossible Origins UI QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Impossible Origins UI QA: PASS (Phase 5 public catalogue, Lab Score and Run integration)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
