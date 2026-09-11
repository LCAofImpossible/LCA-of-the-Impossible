#!/usr/bin/env python3
"""Validate The Impossible Alphabet data derivation, gameplay and publication wiring."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
LAB_VERSION = "20260911-mobile1"
ALPHABET_VERSION = "20260911-difficulty1"
NAV_VERSION = "20260911-difficulty1"
ACTION_VERSION = "20260911-difficulty1"
RESULTS_VERSION = "20260911-difficulty1"
PROGRESS_VERSION = "20260911-score1"
RUN_VERSION = "20260911-run1"
DIFFICULTY_VERSION = "20260911-mobile2"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"Missing file: {path}")
        return ""
    return target.read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    try:
        return json.loads(read(path) or "{}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is invalid JSON: {exc}")
        return {}


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", str(value).upper())
    without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return re.sub(r"[^A-Z0-9]", "", without_marks)


def check_data() -> tuple[int, int]:
    episode_registry = load_json("episodes.json")
    narrative_registry = load_json("crossword.json")
    episodes = episode_registry.get("episodes", [])
    entries = narrative_registry.get("entries", [])
    if not isinstance(episodes, list) or not isinstance(entries, list):
        fail("Episode and narrative registries must contain lists")
        return 0, 0

    episode_by_number = {episode.get("number"): episode for episode in episodes if isinstance(episode, dict)}
    initials: set[str] = set()
    seasons: set[int] = set()
    covered: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("crossword.json contains a non-object entry")
            continue
        number = entry.get("episodeNumber")
        answer = normalize(entry.get("answer", ""))
        clue = entry.get("clue", "")
        episode = episode_by_number.get(number)
        if not episode:
            fail(f"Alphabet source references unknown Episode #{number}")
            continue
        if not re.fullmatch(r"[A-Z][A-Z0-9]{3,19}", answer):
            fail(f"Episode #{number}: alphabet answer is invalid")
        else:
            initials.add(answer[0])
        if not isinstance(clue, str) or not clue.strip() or answer in normalize(clue):
            fail(f"Episode #{number}: alphabet clue is missing or reveals the answer")
        covered.add(number)
        season = episode.get("seasonNumber")
        if isinstance(season, int):
            seasons.add(season)

    expected = set(episode_by_number)
    if covered != expected:
        missing = sorted(expected - covered)
        extra = sorted(covered - expected)
        if missing:
            fail(f"Alphabet source is missing episodes: {missing}")
        if extra:
            fail(f"Alphabet source contains unknown episodes: {extra}")
    if len(initials) < 10:
        fail(f"The alphabet circuit requires at least ten distinct initials; found {len(initials)}")
    if seasons != {1, 2}:
        fail(f"The alphabet source must represent both seasons; found {sorted(seasons)}")
    return len(entries), len(initials)


def check_game_registry() -> None:
    registry = load_json("lab-games.json")
    games = registry.get("games", [])
    expected = {
        "guess": (1, "lab.html", "live"),
        "crossword": (2, "lab-crossword.html", "live"),
        "alphabet": (3, "lab-alphabet.html", "live"),
        "spin": (4, "lab-spin.html", "live"),
    }
    found = {
        game.get("id"): (game.get("number"), game.get("url"), game.get("status"))
        for game in games if isinstance(game, dict)
    }
    if found != expected:
        fail(f"lab-games.json does not expose the four canonical experiments: {found}")


def check_page() -> None:
    page = read("lab-alphabet.html")
    required = (
        'data-page="lab" data-lab-game="alphabet"',
        "IMPOSSIBLE LAB · EXPERIMENT 03",
        "The Impossible <span>Alphabet.</span>",
        'data-lab-game-nav',
        'id="alphabet-wheel"',
        'id="alphabet-start"',
        'id="alphabet-answer-form"',
        'id="alphabet-answer-input"',
        'id="alphabet-pass"',
        'id="alphabet-result"',
        'id="alphabet-review"',
        'id="alphabet-new-round"',
        'class="lab-route-bar"',
        'EXPERIMENT 03 OF 04 · CURRENT GAME',
        'data-lab-another',
        'data-lab-result-scorecard',
        'data-lab-difficulty',
        'id="lab-game-area"',
        'id="alphabet-case-debrief"',
        'id="alphabet-debrief-impact"',
        'aria-live="assertive"',
        "Start 3-minute round",
        f"assets/lab.css?v={LAB_VERSION}",
        f"assets/alphabet.css?v={ALPHABET_VERSION}",
        f"assets/lab-nav.js?v={NAV_VERSION}",
        f"assets/lab-actions.js?v={ACTION_VERSION}",
        f"assets/lab-progress.js?v={PROGRESS_VERSION}",
        f"assets/lab-difficulty.js?v={DIFFICULTY_VERSION}",
        f"assets/lab-run.js?v={RUN_VERSION}",
        f"assets/lab-results.js?v={RESULTS_VERSION}",
        f"assets/alphabet.js?v={ALPHABET_VERSION}",
        "ALPHABET-SEO:START",
        'type="application/rss+xml"',
        'href="feed.xml"',
        'href="archive.html"',
    )
    for token in required:
        if token not in page:
            fail(f"lab-alphabet.html: required token missing: {token}")
    body = page.split("<body", 1)[-1]
    if "assets/images/episodes/" in body:
        fail("lab-alphabet.html renders a catalogue cover in the page body")


def check_runtime() -> None:
    runtime = read("assets/alphabet.js")
    required = (
        "difficultySystem?.config('alphabet')",
        "const ROUND_SECONDS = difficulty.seconds",
        "const MAX_LETTERS = difficulty.letters",
        "const PASS_LIMIT = difficulty.passLimit",
        "const BASE_POINTS = 100",
        "const STREAK_STEP = 25",
        "const STREAK_CAP = 100",
        "fetch('episodes.json'",
        "fetch('crossword.json'",
        "state.groups.get(letter)",
        "state.streak - 1",
        ".status = 'passed'",
        "finishRound('time')",
        "finishRound('complete')",
        "entry.episode.url",
        "replaceChildren(fragment)",
        "credentials: 'same-origin'",
        "const maximumScore = ()",
        "const attemptedCount = ()",
        "resultSystem?.render(elements.resultScorecard",
        "debrief.episode.subjectDescription",
        "debrief.episode.result",
        "debrief.episode.hotspot",
        "state.passesUsed >= PASS_LIMIT",
    )
    for token in required:
        if token not in runtime:
            fail(f"assets/alphabet.js: required gameplay token missing: {token}")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML", "assets/images/episodes/"):
        if forbidden in runtime:
            fail(f"assets/alphabet.js: forbidden persistence, injection or cover token present: {forbidden}")

    episodes = load_json("episodes.json").get("episodes", [])
    for episode in episodes:
        title = episode.get("title") if isinstance(episode, dict) else None
        if isinstance(title, str) and len(title) > 3 and title in runtime:
            fail(f"assets/alphabet.js hard-codes an episode title: {title}")

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets/alphabet.js")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/alphabet.js syntax validation failed: {syntax.stderr or syntax.stdout}")


def check_styles() -> None:
    styles = read("assets/alphabet.css")
    for token in (
        ".alphabet-workspace",
        ".alphabet-wheel",
        ".alphabet-letter.is-active",
        ".alphabet-letter.is-passed",
        ".alphabet-time.is-low",
        ".alphabet-result[hidden]",
        ".alphabet-review-item",
        "@media(max-width:1050px)",
        "@media(max-width:760px)",
        "@media(prefers-reduced-motion:reduce)",
    ):
        if token not in styles:
            fail(f"assets/alphabet.css: required responsive style missing: {token}")


def check_publication_integration() -> None:
    sitemap = read("sitemap.xml")
    if sitemap.count(BASE_URL + "lab-alphabet.html") != 1:
        fail("sitemap.xml must contain lab-alphabet.html exactly once")

    home = read("index.html")
    for token in ('href="impossible-lab.html"', "four registry-driven experiments", "THREE-MINUTE LETTER CIRCUIT"):
        if token not in home:
            fail(f"index.html: The Impossible Alphabet discovery token missing: {token}")
    hub = read("impossible-lab.html")
    for token in ('href="lab-alphabet.html"', 'href="lab-spin.html"'):
        if token not in hub:
            fail(f"impossible-lab.html: alphabet discovery token missing: {token}")

    contracts = {
        "scripts/publication_qa.py": ('"alphabet_qa.py"',),
        "scripts/live_site_qa.py": ('"lab-alphabet.html"', '"assets/alphabet.css"', '"assets/alphabet.js"'),
        "scripts/phase5_sync.py": ('"lab-alphabet.html"',),
        "scripts/telemetry_sync.py": ('"lab-alphabet.html"',),
        "scripts/rss_sync.py": ('"lab-alphabet.html"',),
        "scripts/seo_qa.py": ('"lab-alphabet.html"',),
        ".github/workflows/seo-sync.yml": ("lab-alphabet.html",),
        "README.md": ("### 39.3 The Impossible Alphabet", "scripts/alphabet_qa.py"),
    }
    for path, tokens in contracts.items():
        source = read(path)
        for token in tokens:
            if token not in source:
                fail(f"{path}: alphabet publication token missing: {token}")


def main() -> int:
    cases, initials = check_data()
    check_game_registry()
    check_page()
    check_runtime()
    check_styles()
    check_publication_integration()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nThe Impossible Alphabet QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"The Impossible Alphabet QA: PASS ({cases} cases, {initials} active initials)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
