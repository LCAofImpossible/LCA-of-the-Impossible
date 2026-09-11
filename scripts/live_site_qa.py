#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
GRAPHIC_PATTERNS = (
    "ep{number:02d}-inventory-map.svg",
    "ep{number:02d}-technical-plate.svg",
    "ep{number:02d}-hotspot-breakdown.svg",
)
CORE_PATHS = {
    "index.html",
    "archive.html",
    "impossible-lab.html",
    "impossible-lab-run.html",
    "lab-daily.html",
    "lab.html",
    "lab-crossword.html",
    "lab-alphabet.html",
    "lab-spin.html",
    "collections.html",
    "compare.html",
    "explore.html",
    "method.html",
    "sources.html",
    "about.html",
    "glossary.html",
    "season-i.html",
    "season-ii.html",
    "statistics.html",
    "updates.html",
    "feed.xml",
    "episodes.json",
    "crossword.json",
    "lab-games.json",
    "collections.json",
    "schemas/episode-structured-metadata.schema.json",
    "verification/structured-metadata-migration.json",
    "sitemap.xml",
    "robots.txt",
    "site.webmanifest",
    "assets/favicon.svg",
    "assets/style.css",
    "assets/features.css",
    "assets/engagement.css",
    "assets/editorial.css",
    "assets/method.css",
    "assets/seasons.css",
    "assets/statistics.css",
    "assets/lab.css",
    "assets/lab-hub.css",
    "assets/lab-run.css",
    "assets/crossword.css",
    "assets/alphabet.css",
    "assets/spin.css",
    "assets/atlas.css",
    "assets/compare.css",
    "assets/phase6.css",
    "assets/telemetry.css",
    "assets/site.js",
    "assets/seasons.js",
    "assets/statistics.js",
    "assets/lab.js",
    "assets/lab-hub.js",
    "assets/lab-nav.js",
    "assets/lab-actions.js",
    "assets/lab-results.js",
    "assets/lab-progress.js",
    "assets/lab-run.js",
    "assets/lab-run-page.js",
    "assets/daily.css",
    "assets/daily.js",
    "assets/crossword-generator.js",
    "assets/crossword.js",
    "assets/alphabet.js",
    "assets/spin.js",
    "assets/atlas.js",
    "assets/engagement.js",
    "assets/phase6.js",
    "assets/passport-cleanup.js",
    "assets/telemetry.js",
    "assets/updates.css",
    "assets/updates.js",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_url(base_url: str, path: str, cache_key: str) -> str:
    url = urljoin(base_url, quote(path, safe="/"))
    return f"{url}?live-qa={quote(cache_key, safe='')}" if cache_key else url


def fetch(
    base_url: str,
    path: str,
    cache_key: str,
    timeout: float,
    retries: int = 3,
) -> bytes:
    url = build_url(base_url, path, cache_key)
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = Request(
                url,
                headers={
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "User-Agent": "LCA-of-the-Impossible-Live-QA",
                },
            )
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = exc
            if isinstance(exc, HTTPError) and exc.code < 500:
                break
            if attempt + 1 < retries:
                time.sleep(min(2**attempt, 4))
    raise RuntimeError(f"{path}: {last_error}")


def wait_for_registry(
    base_url: str,
    cache_key: str,
    timeout: float,
    attempts: int,
    delay: float,
) -> None:
    expected = (ROOT / "episodes.json").read_bytes()
    last_detail = "not requested"
    for attempt in range(1, attempts + 1):
        try:
            actual = fetch(base_url, "episodes.json", cache_key, timeout, retries=2)
        except RuntimeError as exc:
            last_detail = str(exc)
        else:
            if actual == expected:
                return
            last_detail = (
                f"registry hash {sha256(actual)}; expected {sha256(expected)}"
            )
        if attempt < attempts:
            time.sleep(delay)
    raise RuntimeError(
        f"Live deployment did not reach the checked-out registry after {attempts} attempts: "
        f"{last_detail}"
    )


def expected_paths(episodes: list[dict[str, object]]) -> set[str]:
    paths = set(CORE_PATHS)
    for episode in episodes:
        number = int(episode["number"])
        paths.add(str(episode["url"]))
        paths.add(str(episode["cover"]))
        for pattern in GRAPHIC_PATTERNS:
            paths.add(f"assets/images/episode-graphics/{pattern.format(number=number)}")
    return paths


def fetch_all(
    base_url: str,
    paths: set[str],
    cache_key: str,
    timeout: float,
    workers: int,
) -> tuple[dict[str, bytes], list[str]]:
    downloaded: dict[str, bytes] = {}
    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(fetch, base_url, path, cache_key, timeout): path
            for path in sorted(paths)
        }
        for future in concurrent.futures.as_completed(futures):
            path = futures[future]
            try:
                downloaded[path] = future.result()
            except Exception as exc:
                errors.append(str(exc))
    return downloaded, errors


def validate(
    episodes: list[dict[str, object]],
    downloaded: dict[str, bytes],
    paths: set[str],
) -> list[str]:
    errors: list[str] = []

    for path in sorted(paths):
        local_path = ROOT / path
        if not local_path.is_file():
            errors.append(f"Local publication path is missing: {path}")
            continue
        actual = downloaded.get(path)
        if actual is None:
            continue
        expected = local_path.read_bytes()
        if actual != expected:
            errors.append(
                f"Live bytes differ for {path}: {sha256(actual)}; expected {sha256(expected)}"
            )

    try:
        registry = json.loads(downloaded["episodes.json"])
    except (KeyError, json.JSONDecodeError) as exc:
        errors.append(f"Live episodes.json is unavailable or invalid: {exc}")
        return errors

    live_episodes = registry.get("episodes", [])
    if any(isinstance(episode, dict) and "pdf" in episode for episode in live_episodes):
        errors.append("Live episodes.json contains a prohibited pdf field")
    for episode in live_episodes:
        if not isinstance(episode, dict):
            errors.append("Live episodes.json contains a non-object episode record")
            continue
        description = episode.get("subjectDescription")
        if not isinstance(description, str) or not 100 <= len(description) <= 190:
            errors.append(
                f"Episode #{episode.get('number')} has no valid live subjectDescription"
            )

    try:
        sitemap = downloaded["sitemap.xml"].decode("utf-8")
    except (KeyError, UnicodeDecodeError) as exc:
        errors.append(f"Live sitemap.xml is unavailable or invalid: {exc}")
        sitemap = ""

    advanced_archive_contract = {
        "archive.html": (
            'id="subject-filter"',
            'id="hotspot-filter"',
            'id="boundary-filter"',
            'id="evidence-confidence-filter"',
            'id="clear-filters"',
            "data-clear-archive",
            "20260830-subject-descriptions1",
        ),
        "assets/site.js": (
            "archiveStateFromUrl",
            "writeArchiveToUrl",
            "activeSubject",
            "activeHotspot",
            "activeBoundary",
            "activeConfidence",
            "activeProxy",
            "activeSensitivity",
            "visibleLimit += 9",
            "resetArchive",
        ),
        "assets/style.css": (
            ".advanced-filter-grid",
            ".archive-search-row",
            ".archive-active-filters",
        ),
    }
    for path, required_tokens in advanced_archive_contract.items():
        source = downloaded.get(path, b"").decode("utf-8", errors="replace")
        for token in required_tokens:
            if token not in source:
                errors.append(f"Advanced archive live contract is missing {token!r} from {path}")

    atlas_contract = {
        "explore.html": (
            "THE IMPOSSIBLE ATLAS",
            'id="atlas-overview"',
            'id="atlas-routes"',
            'id="atlas-relationships"',
            'id="impact-scale"',
            "assets/atlas.css?v=20260829-atlas1",
            "assets/atlas.js?v=20260829-atlas1",
            "Compare the reasoning freely.",
        ),
        "assets/atlas.js": (
            "structuredMetadata",
            "subject?.entityType",
            "impact?.hotspotStage",
            "lcaCharacteristics",
            "archiveHref",
            "URLSearchParams",
            "renderMatrix",
        ),
        "assets/atlas.css": (
            ".atlas-summary-grid",
            ".atlas-route-grid",
            ".atlas-matrix-wrap",
            "overflow-x:auto",
        ),
    }
    for path, required_tokens in atlas_contract.items():
        source = downloaded.get(path, b"").decode("utf-8", errors="replace")
        for token in required_tokens:
            if token not in source:
                errors.append(f"Impossible Atlas live contract is missing {token!r} from {path}")

    comparison_contract = {
        "compare.html": (
            "METHODOLOGICAL VIEW",
            "visual synthesis adds headline magnitude",
            "assets/compare.css?v=20260829-compare-synthesis1",
            "assets/site.js?v=20260830-subject-descriptions1",
            'id="comparison-output"',
        ),
        "assets/site.js": (
            "comparisonStatus",
            "comparison-basis-grid",
            "Direct footprint comparison",
            "Not established",
            "Reference flow",
            "Included stages",
            "Excluded stages",
            "Cut-off summary",
            "MODEL ARCHITECTURE",
            "Missing approved fields",
            "comparison-visual-summary",
            "Magnitude, hotspot and evidence signals",
            "comparison-magnitude-axis",
            "comparison-hotspot-track",
            "Evidence signals · separate ordinal fields",
            "No composite score",
        ),
        "assets/compare.css": (
            ".comparison-basis",
            ".comparison-basis-grid",
            ".comparison-visual-summary",
            ".comparison-signal-grid",
            ".comparison-magnitude-track",
            ".comparison-hotspot-track",
            ".comparison-level-scale",
            ".comparison-table-group",
            ".comparison-value-missing",
        ),
    }
    for path, required_tokens in comparison_contract.items():
        source = downloaded.get(path, b"").decode("utf-8", errors="replace")
        for token in required_tokens:
            if token not in source:
                errors.append(f"Comparison visual synthesis live contract is missing {token!r} from {path}")

    editorial_paths_contract = {
        "collections.json": (
            '"schemaVersion": 2',
            '"editorialPaths"',
            '"scaling-the-impossible"',
            '"when-time-becomes-inventory"',
            '"following-the-gold-assumption"',
            '"drawing-the-boundary-around-magic"',
            '"relatedCollections"',
            '"steps"',
        ),
        "collections.html": (
            'id="editorial-paths"',
            'id="editorial-path-index"',
            'id="editorial-path-list"',
            "GUIDED READING PATHS",
            "assets/engagement.js?v=20260830-subject-descriptions1",
        ),
        "assets/engagement.js": (
            "renderEditorialPaths",
            "placeEditorialPathNavigation",
            "searchParams.get('path')",
            "editorial-path-progress",
            "data-copy-path",
            "Path overview",
            "assets/engagement.css?v=20260830-subject-descriptions1",
        ),
        "assets/engagement.css": (
            ".editorial-path-index",
            ".editorial-path-steps",
            ".editorial-path-step",
            ".editorial-path-progress",
            ".editorial-path-progress-track",
            ".editorial-path-progress-nav",
        ),
    }
    for path, required_tokens in editorial_paths_contract.items():
        source = downloaded.get(path, b"").decode("utf-8", errors="replace")
        for token in required_tokens:
            if token not in source:
                errors.append(f"Guided editorial paths live contract is missing {token!r} from {path}")

    subject_descriptions_contract = {
        "index.html": (
            "assets/style.css?v=20260830-subject-descriptions1",
            "assets/site.js?v=20260830-subject-descriptions1",
        ),
        "archive.html": (
            "assets/style.css?v=20260830-subject-descriptions1",
            "assets/site.js?v=20260830-subject-descriptions1",
        ),
        "season-i.html": ("assets/seasons.js?v=20260830-subject-descriptions1",),
        "season-ii.html": ("assets/seasons.js?v=20260830-subject-descriptions1",),
        "assets/site.js": (
            "episode.subjectDescription",
            "current.subjectDescription",
            "Subject in brief",
            'class="card-subject"',
        ),
        "assets/seasons.js": ("episode.subjectDescription",),
        "assets/engagement.js": ("episode.subjectDescription",),
        "assets/style.css": (
            ".card-subject",
            ".featured-subject",
            ".episode-subject-summary",
        ),
    }
    for path, required_tokens in subject_descriptions_contract.items():
        source = downloaded.get(path, b"").decode("utf-8", errors="replace")
        for token in required_tokens:
            if token not in source:
                errors.append(f"Subject-description live contract is missing {token!r} from {path}")

    accessory_contract = {
        "updates.html": (
            "Updates &amp; RSS",
            'href="feed.xml"',
            'data-updates-telemetry',
            'id="updates-case-list"',
            'href="episodes.json"',
            'href="site.webmanifest"',
            "assets/updates.css?v=20260830-accessories1",
            "assets/updates.js?v=20260830-accessories1",
        ),
        "feed.xml": (
            "LCA of the Impossible — New episodes",
            f'href="{DEFAULT_BASE_URL}feed.xml" rel="self"',
            "<item>",
        ),
        "assets/updates.js": (
            "registry.episodes",
            ".slice(0, 12)",
            "episode.subjectDescription",
            "data-site-visitors",
            "MutationObserver",
        ),
        "assets/updates.css": (
            ".updates-hero",
            ".updates-case",
            ".updates-utility-grid",
            "@media(max-width:620px)",
        ),
        "index.html": (
            'type="application/rss+xml"',
            'href="feed.xml"',
            'href="updates.html"',
        ),
    }
    for path, required_tokens in accessory_contract.items():
        source = downloaded.get(path, b"").decode("utf-8", errors="replace")
        for token in required_tokens:
            if token not in source:
                errors.append(f"RSS/accessory live contract is missing {token!r} from {path}")

    lab_contract = {
        "impossible-lab.html": (
            "Choose your <span>experiment.</span>",
            'data-lab-hub-grid',
            'data-random-game',
            'href="lab.html"',
            'href="lab-crossword.html"',
            'href="lab-alphabet.html"',
            'href="lab-spin.html"',
            'data-lab-score-panel',
            'data-lab-score-total',
            'data-lab-score-breakdown',
            'data-lab-reset',
            "Impossible Lab Run",
            "Start Lab Run →",
            'class="lab-hub-actions"',
            'href="impossible-lab-run.html"',
            "Daily Impossible",
            'href="lab-daily.html"',
            'data-daily-entry',
            "assets/lab-hub.css?v=20260911-daily1",
            "assets/lab-progress.js?v=20260911-score1",
            "assets/daily.js?v=20260911-daily1",
            "assets/lab-hub.js?v=20260911-daily1",
        ),
        "lab-daily.html": (
            'data-lab-daily',
            "One day.<br><span>One impossible case.</span>",
            'id="daily-answer-form"',
            'id="daily-clue-list"',
            'id="daily-result"',
            'href="impossible-lab.html"',
            "assets/lab.css?v=20260911-run1",
            "assets/daily.css?v=20260911-daily1",
            "assets/daily.js?v=20260911-daily1",
        ),
        "impossible-lab-run.html": (
            'data-lab-run-page',
            "Four games.<br><span>One run.</span>",
            "Run Score",
            'data-run-total',
            'data-run-stages',
            'data-run-start',
            'data-run-continue',
            "Run Score vs Lab Score",
            "assets/lab.css?v=20260911-run1",
            "assets/lab-run.css?v=20260911-run1",
            "assets/lab-progress.js?v=20260911-score1",
            "assets/lab-run.js?v=20260911-run1",
            "assets/lab-run-page.js?v=20260911-run1",
        ),
        "lab.html": (
            "IMPOSSIBLE LAB · EXPERIMENT 01",
            "Guess the <span>Impossible.</span>",
            'id="lab-clue-list"',
            'id="lab-answer-form"',
            'id="lab-result"',
            'class="lab-route-bar"',
            "EXPERIMENT 01 OF 04 · CURRENT GAME",
            'data-lab-another',
            'data-lab-result-scorecard',
            "assets/lab.css?v=20260911-run1",
            "assets/lab-nav.js?v=20260911-navigation1",
            "assets/lab-actions.js?v=20260911-navigation1",
            "assets/lab-progress.js?v=20260911-score1",
            "assets/lab-run.js?v=20260911-run1",
            "assets/lab-results.js?v=20260911-run1",
            "assets/lab.js?v=20260911-results1",
        ),
        "lab-crossword.html": (
            "IMPOSSIBLE LAB · EXPERIMENT 02",
            "Cross the <span>Impossible.</span>",
            'id="crossword-grid"',
            'id="crossword-across"',
            'id="crossword-result"',
            'id="crossword-replay"',
            'class="lab-route-bar"',
            "EXPERIMENT 02 OF 04 · CURRENT GAME",
            'data-lab-another',
            'data-lab-result-scorecard',
            "assets/lab.css?v=20260911-run1",
            "assets/lab-nav.js?v=20260911-navigation1",
            "assets/lab-actions.js?v=20260911-navigation1",
            "assets/lab-progress.js?v=20260911-score1",
            "assets/lab-run.js?v=20260911-run1",
            "assets/lab-results.js?v=20260911-run1",
            "assets/crossword.css?v=20260911-score1",
            "assets/crossword-generator.js?v=20260911-score1",
            "assets/crossword.js?v=20260911-score1",
        ),
        "lab-alphabet.html": (
            "IMPOSSIBLE LAB · EXPERIMENT 03",
            "The Impossible <span>Alphabet.</span>",
            'id="alphabet-wheel"',
            'id="alphabet-answer-form"',
            'id="alphabet-result"',
            'class="lab-route-bar"',
            "EXPERIMENT 03 OF 04 · CURRENT GAME",
            'data-lab-another',
            'data-lab-result-scorecard',
            'id="alphabet-case-debrief"',
            "assets/lab.css?v=20260911-run1",
            "assets/alphabet.css?v=20260911-results1",
            "assets/lab-nav.js?v=20260911-navigation1",
            "assets/lab-actions.js?v=20260911-navigation1",
            "assets/lab-progress.js?v=20260911-score1",
            "assets/lab-run.js?v=20260911-run1",
            "assets/lab-results.js?v=20260911-run1",
            "assets/alphabet.js?v=20260911-results1",
        ),
        "lab-spin.html": (
            "IMPOSSIBLE LAB · EXPERIMENT 04",
            "Spin the <span>Impossible.</span>",
            'id="spin-wheel"',
            'id="spin-puzzle"',
            'id="spin-solve-form"',
            'id="spin-result"',
            'class="lab-route-bar"',
            "EXPERIMENT 04 OF 04 · CURRENT GAME",
            'data-lab-another',
            'data-lab-result-scorecard',
            "assets/lab.css?v=20260911-run1",
            "assets/spin.css?v=20260911-results1",
            "assets/lab-nav.js?v=20260911-navigation1",
            "assets/lab-actions.js?v=20260911-navigation1",
            "assets/lab-progress.js?v=20260911-score1",
            "assets/lab-run.js?v=20260911-run1",
            "assets/lab-results.js?v=20260911-run1",
            "assets/spin.js?v=20260911-results1",
        ),
        "assets/lab.js": (
            "registry.episodes",
            "const SCORE_STEPS = [500, 400, 300, 200, 100]",
            "episode.seasonLabel",
            "episode.lcaCharacteristics",
            "episode.result",
            "episode.functionalUnit",
            "episode.subjectDescription",
            "titlePattern(episode.title)",
            "state.unused.splice",
            "state.attempts += 1",
            "resultSystem?.render(elements.resultScorecard",
        ),
        "assets/lab.css": (
            ".lab-route-bar",
            ".lab-game-nav",
            ".lab-workspace",
            ".lab-clue.is-current",
            ".lab-result[hidden]",
            ".lab-end-actions",
            ".lab-result-scorecard",
            ".lab-result-metrics",
            ".lab-record-band",
            ".lab-run-banner",
            ".lab-run-result",
            ".lab-case-debrief",
            ".lab-home-preview",
            "grid-auto-rows:1fr",
            "@media(max-width:760px)",
        ),
        "assets/lab-hub.js": (
            "fetch('lab-games.json'",
            "game.summary",
            "game.duration",
            "game.category",
            "replaceChildren(fragment)",
            "window.location.assign(url)",
            "progressSystem.summarize()",
            "summary.games[game.id]",
            "progressSystem?.clear()",
        ),
        "assets/lab-hub.css": (
            ".lab-hub-actions",
            ".lab-hub-grid",
            ".lab-hub-card",
            ".lab-score-panel",
            ".lab-score-breakdown",
            ".lab-run-entry",
            ".lab-hub-note",
            "@media(max-width:620px)",
        ),
        "index.html": (
            "LAB-HOME:START",
            'href="impossible-lab.html"',
            "assets/lab.css?v=20260911-run1",
        ),
        "assets/crossword-generator.js": (
            "seededRandom",
            "fallbackLayout",
            "seasonNumber",
            "validate",
        ),
        "assets/crossword.js": (
            "fetch('crossword.json'",
            "state.correctEntries.size * 50",
            "state.revealedCells.size * 10",
            "episode.subjectDescription",
            "episode.result",
            "episode.hotspot",
            "state.answerAttempts += 1",
            "resultSystem?.render(elements.resultScorecard",
            "persist: complete",
        ),
        "assets/crossword.css": (
            ".crossword-grid",
            ".crossword-cell.is-revealed",
            ".crossword-clue.is-correct",
            "@media(max-width:1180px)",
        ),
        "assets/alphabet.js": (
            "const ROUND_SECONDS = 180",
            "const MAX_LETTERS = 18",
            "const BASE_POINTS = 100",
            "const STREAK_STEP = 25",
            "fetch('crossword.json'",
            ".status = 'passed'",
            "finishRound('time')",
            "entry.episode.url",
            "const maximumScore = ()",
            "resultSystem?.render(elements.resultScorecard",
            "debrief.episode.subjectDescription",
        ),
        "assets/alphabet.css": (
            ".alphabet-wheel",
            ".alphabet-letter.is-active",
            ".alphabet-letter.is-passed",
            ".alphabet-result[hidden]",
            "@media(max-width:760px)",
        ),
        "assets/spin.js": (
            "const ROUNDS_PER_SESSION = 5",
            "const MAX_SPINS = 15",
            "const SOLVE_ATTEMPTS = 3",
            "const VOWEL_COST = 150",
            "const HINT_COST = 300",
            "const WRONG_SOLUTION_COST = 200",
            "const BASE_SOLVE_BONUS = 500",
            "fetch('crossword.json'",
            "state.entry.episode.result",
            "state.entry.episode.hotspot",
            "setText(elements.next, 'Play again →')",
            "const maximumRoundScore = ()",
            "state.letterAttempts += 1",
            "state.phraseAttempts += 1",
            "resultSystem?.render(elements.resultScorecard",
        ),
        "assets/lab-actions.js": (
            "fetch('lab-games.json'",
            "game.id !== currentGame",
            "game.status === 'live'",
            "window.location.assign(selected.url)",
            "window.location.assign('impossible-lab.html')",
        ),
        "assets/lab-results.js": (
            "const SCALE_MAX = 1000",
            "finiteNumber(score) / safeMaximum",
            "metric('Maximum obtainable'",
            "metric('Completion'",
            "metric('Accuracy'",
            "It does not compare the environmental results of different episodes",
            "progressSystem?.record",
            "NEW GAME RECORD",
            "Best normalized",
            "Lab Score",
            "window.ImpossibleLabRun?.record",
            "IMPOSSIBLE LAB RUN COMPLETE",
            "target.replaceChildren(card)",
        ),
        "assets/lab-progress.js": (
            "const STORAGE_KEY = 'lca-impossible-lab-progress-v1'",
            "window.localStorage",
            "const GAME_IDS = Object.freeze(['guess', 'crossword', 'alphabet', 'spin'])",
            "const LAB_MAX = GAME_IDS.length * SCORE_SCALE",
            "bestScore",
            "bestNormalized",
            "summarize",
            "clear",
        ),
        "assets/lab-run.js": (
            "const STORAGE_KEY = 'lca-impossible-lab-run-v1'",
            "window.localStorage",
            "before.nextGameId !== gameId",
            "new URLSearchParams(window.location.search).get('run') === '1'",
            "RUN_MAX",
            "createGameBanner",
        ),
        "assets/lab-run-page.js": (
            "runSystem.summarize()",
            "runSystem.start()",
            "runSystem.clear()",
            "url.searchParams.set('run', '1')",
            "fetch('lab-games.json'",
            "stages.replaceChildren(fragment)",
        ),
        "assets/lab-run.css": (
            ".lab-run-shell",
            ".lab-run-board",
            ".lab-run-stage.is-current",
            ".lab-run-stage.is-complete",
            ".lab-run-explainer",
            "@media(max-width:620px)",
        ),
        "assets/spin.css": (
            ".spin-wheel",
            ".spin-puzzle",
            ".spin-keyboard",
            ".spin-result[hidden]",
            "@media(max-width:760px)",
        ),
    }
    for path, required_tokens in lab_contract.items():
        source = downloaded.get(path, b"").decode("utf-8", errors="replace")
        for token in required_tokens:
            if token not in source:
                errors.append(f"Impossible Lab live contract is missing {token!r} from {path}")

    lab_runtime = downloaded.get("assets/lab.js", b"").decode("utf-8", errors="replace")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "assets/images/episodes/"):
        if forbidden in lab_runtime:
            errors.append(f"Impossible Lab runtime violates its privacy or cover contract with {forbidden!r}")
    crossword_runtime = "\n".join(
        downloaded.get(path, b"").decode("utf-8", errors="replace")
        for path in ("assets/crossword.js", "assets/alphabet.js", "assets/spin.js", "assets/lab-nav.js", "assets/lab-actions.js", "assets/lab-results.js", "assets/lab-hub.js")
    )
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML"):
        if forbidden in crossword_runtime:
            errors.append(f"Crossword runtime violates its privacy or injection contract with {forbidden!r}")
    progress_runtime = downloaded.get("assets/lab-progress.js", b"").decode("utf-8", errors="replace")
    for forbidden in ("document.cookie", "sessionStorage", "innerHTML", "fetch(", "XMLHttpRequest"):
        if forbidden in progress_runtime:
            errors.append(f"Lab record runtime violates its local-only privacy contract with {forbidden!r}")
    run_runtime = downloaded.get("assets/lab-run.js", b"").decode("utf-8", errors="replace")
    for forbidden in ("document.cookie", "sessionStorage", "innerHTML", "fetch(", "XMLHttpRequest"):
        if forbidden in run_runtime:
            errors.append(f"Lab Run runtime violates its local-only privacy contract with {forbidden!r}")
    run_page_runtime = downloaded.get("assets/lab-run-page.js", b"").decode("utf-8", errors="replace")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML", "XMLHttpRequest"):
        if forbidden in run_page_runtime:
            errors.append(f"Lab Run page runtime violates its privacy or injection contract with {forbidden!r}")
    daily_runtime = downloaded.get("assets/daily.js", b"").decode("utf-8", errors="replace")
    for forbidden in ("document.cookie", "sessionStorage", "innerHTML", "XMLHttpRequest"):
        if forbidden in daily_runtime:
            errors.append(f"Daily Impossible runtime violates its local-only privacy contract with {forbidden!r}")
    try:
        crossword_registry = json.loads(downloaded["crossword.json"])
        game_registry = json.loads(downloaded["lab-games.json"])
    except (KeyError, json.JSONDecodeError) as exc:
        errors.append(f"Live Impossible Lab registries are unavailable or invalid: {exc}")
    else:
        crossword_entries = crossword_registry.get("entries", [])
        if len(crossword_entries) != len(live_episodes):
            errors.append("Live crossword registry does not cover every published episode")
        game_status = {
            game.get("id"): game.get("status")
            for game in game_registry.get("games", [])
            if isinstance(game, dict)
        }
        if any(game_status.get(game) != "live" for game in ("guess", "crossword", "alphabet", "spin")):
            errors.append("All four live Impossible Lab experiments are not registered")
        for game in game_registry.get("games", []):
            if isinstance(game, dict) and any(not game.get(field) for field in ("summary", "duration", "category")):
                errors.append(f"Impossible Lab game {game.get('id', '?')} is missing hub card metadata")
    if sitemap.count("/impossible-lab.html") != 1:
        errors.append("Impossible Lab hub does not occur exactly once in the live sitemap")
    if sitemap.count("/impossible-lab-run.html") != 1:
        errors.append("Impossible Lab Run does not occur exactly once in the live sitemap")
    if sitemap.count("/lab-daily.html") != 1:
        errors.append("Daily Impossible does not occur exactly once in the live sitemap")
    if sitemap.count(f"/{'lab.html'}") != 1:
        errors.append("Impossible Lab does not occur exactly once in the live sitemap")
    if sitemap.count("/lab-crossword.html") != 1:
        errors.append("Cross the Impossible does not occur exactly once in the live sitemap")
    if sitemap.count("/lab-alphabet.html") != 1:
        errors.append("The Impossible Alphabet does not occur exactly once in the live sitemap")
    if sitemap.count("/lab-spin.html") != 1:
        errors.append("Spin the Impossible does not occur exactly once in the live sitemap")

    updates_script = downloaded.get("assets/updates.js", b"").decode(
        "utf-8", errors="replace"
    )
    for forbidden in ("counterapi.com", "site-total", "document.cookie", "localStorage"):
        if forbidden in updates_script:
            errors.append(f"RSS/accessory runtime violates telemetry privacy with {forbidden!r}")

    for episode in episodes:
        number = int(episode["number"])
        url = str(episode["url"])
        title = str(episode["title"])
        result = str(episode["result"])
        try:
            html = downloaded[url].decode("utf-8")
        except (KeyError, UnicodeDecodeError) as exc:
            errors.append(f"Episode #{number} live HTML is unavailable or invalid: {exc}")
            continue

        required = (
            f'data-episode="{number}"',
            title,
            result,
            "application/ld+json",
            "og:image",
            "twitter:image",
            "../assets/site.js",
            "../assets/phase6.js",
            "../assets/passport-cleanup.js",
        )
        for token in required:
            if token not in html:
                errors.append(f"Episode #{number} live HTML is missing {token!r}")

        lower = html.lower()
        if "raw text" in lower:
            errors.append(f"Episode #{number} exposes Raw text")
        if "download episode pdf" in lower or "assets/pdf/episodes/" in lower:
            errors.append(f"Episode #{number} exposes a source-PDF control or link")
        if sitemap.count(f"/{url}") != 1:
            errors.append(f"Episode #{number} does not occur exactly once in the live sitemap")

    phase6 = downloaded.get("assets/phase6.js", b"").decode("utf-8", errors="replace")
    cleanup = downloaded.get("assets/passport-cleanup.js", b"").decode(
        "utf-8", errors="replace"
    )
    for token in ("View epic passport →", "Print / Save as PDF"):
        if token not in phase6:
            errors.append(f"Live Epic Passport runtime is missing {token!r}")
    for token in (
        "Raw text",
        "downloadRawPassport",
        "passport-raw",
        "systemBoundary:",
        "factorList:",
        "allocationRule:",
    ):
        if token in phase6:
            errors.append(f"Live Epic Passport runtime reintroduces {token!r}")
    if "allowedPassportActions" not in cleanup:
        errors.append("Live Passport-only cleanup guard is missing")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that GitHub Pages serves the checked-out static publication exactly."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--cache-key", default="")
    parser.add_argument("--attempts", type=int, default=24)
    parser.add_argument("--delay", type=float, default=5.0)
    parser.add_argument("--verify-attempts", type=int, default=6)
    parser.add_argument("--verify-delay", type=float, default=10.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/") + "/"
    registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    episodes = registry.get("episodes", [])
    if not isinstance(episodes, list) or not episodes:
        print("ERROR: Local episodes.json contains no episodes", file=sys.stderr)
        return 1

    print("## Live Site QA")
    print()
    print(f"- Target: `{base_url}`")
    print(f"- Registered episodes: **{len(episodes)}**")

    try:
        wait_for_registry(
            base_url,
            args.cache_key,
            args.timeout,
            args.attempts,
            args.delay,
        )
    except RuntimeError as exc:
        print(f"- Result: **FAIL** — {exc}", file=sys.stderr)
        return 1

    paths = expected_paths(episodes)
    errors: list[str] = []
    for attempt in range(1, max(1, args.verify_attempts) + 1):
        downloaded, fetch_errors = fetch_all(
            base_url,
            paths,
            args.cache_key,
            args.timeout,
            max(1, args.workers),
        )
        errors = fetch_errors + validate(episodes, downloaded, paths)
        if not errors:
            break
        if attempt < max(1, args.verify_attempts):
            time.sleep(args.verify_delay)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"- Result: **FAIL** — {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"- Exact deployed paths verified: **{len(paths)}**")
    print(f"- Exact cover assets verified: **{len(episodes)}**")
    print("- Registry, collections, sitemap, SEO pages and analytical graphics: **PASS**")
    print("- Advanced archive search, combined filters and URL-state contract: **PASS**")
    print("- Impossible Atlas routes, relationship map and impact-scale guardrail: **PASS**")
    print("- Comparison visual synthesis, methodological fields and non-comparability verdict: **PASS**")
    print("- Guided editorial paths, ordered steps and episode context navigation: **PASS**")
    print("- RSS discovery, updates hub and single-request readership telemetry: **PASS**")
    print("- Impossible Lab games, persistent records and four-stage Run contracts: **PASS**")
    print("- Epic Passport-only runtime and source-PDF link policy: **PASS**")
    print("- Result: **PASS**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
