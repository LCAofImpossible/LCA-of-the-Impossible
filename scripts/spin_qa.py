#!/usr/bin/env python3
"""Validate Spin the Impossible phrase derivation, wheel gameplay and publication wiring."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
LAB_VERSION = "20260910-spin1"
NAV_VERSION = "20260909-alphabet2"
SPIN_VERSION = "20260910-spin1"
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


def normalize(value: object) -> str:
    decomposed = unicodedata.normalize("NFD", str(value).upper())
    without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return re.sub(r"[^A-Z0-9]", "", without_marks)


def check_data() -> int:
    episodes = load_json("episodes.json").get("episodes", [])
    entries = load_json("crossword.json").get("entries", [])
    if not isinstance(episodes, list) or not isinstance(entries, list):
        fail("Episode and narrative registries must contain lists")
        return 0

    episode_by_number = {episode.get("number"): episode for episode in episodes if isinstance(episode, dict)}
    covered: set[int] = set()
    seasons: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("crossword.json contains a non-object entry")
            continue
        number = entry.get("episodeNumber")
        phrase = entry.get("clue", "")
        answer = entry.get("answer", "")
        episode = episode_by_number.get(number)
        if not episode:
            fail(f"Spin phrase references unknown Episode #{number}")
            continue
        if not isinstance(phrase, str) or not 45 <= len(phrase.strip()) <= 120 or not phrase.strip().endswith("."):
            fail(f"Episode #{number}: hidden phrase must be a complete 45–120 character sentence")
        elif normalize(answer) in normalize(phrase):
            fail(f"Episode #{number}: hidden phrase reveals its subject answer")
        if not all(char.isalpha() or char in " .,'-" for char in str(phrase)):
            fail(f"Episode #{number}: hidden phrase contains an unsupported character")
        for field in ("title", "url", "seasonLabel", "subjectDescription", "result", "hotspot"):
            if not episode.get(field):
                fail(f"Episode #{number}: Spin result field {field} is missing")
        if isinstance(episode.get("seasonNumber"), int):
            seasons.add(episode["seasonNumber"])
        covered.add(number)

    expected = set(episode_by_number)
    if covered != expected:
        missing = sorted(expected - covered)
        extra = sorted(covered - expected)
        if missing:
            fail(f"Spin phrase pool is missing episodes: {missing}")
        if extra:
            fail(f"Spin phrase pool contains unknown episodes: {extra}")
    if seasons != {1, 2}:
        fail(f"Spin phrase pool must represent both seasons; found {sorted(seasons)}")
    if len(entries) < 5:
        fail("Spin the Impossible requires at least five phrases")
    return len(entries)


def check_game_registry() -> None:
    games = load_json("lab-games.json").get("games", [])
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
    page = read("lab-spin.html")
    required = (
        'data-page="lab" data-lab-game="spin"',
        "IMPOSSIBLE LAB · EXPERIMENT 04",
        "Spin the <span>Impossible.</span>",
        'data-lab-game-nav',
        'id="spin-wheel"',
        'id="spin-start"',
        'id="spin-action"',
        'id="spin-vowel"',
        'id="spin-hint"',
        'id="spin-puzzle"',
        'id="spin-keyboard"',
        'id="spin-solve-form"',
        'id="spin-reveal"',
        'id="spin-result"',
        'aria-live="assertive"',
        "Start round 1",
        f"assets/lab.css?v={LAB_VERSION}",
        f"assets/spin.css?v={SPIN_VERSION}",
        f"assets/lab-nav.js?v={NAV_VERSION}",
        f"assets/spin.js?v={SPIN_VERSION}",
        "SPIN-SEO:START",
        'type="application/rss+xml"',
        'href="feed.xml"',
        'href="archive.html"',
    )
    for token in required:
        if token not in page:
            fail(f"lab-spin.html: required token missing: {token}")
    body = page.split("<body", 1)[-1]
    if "assets/images/episodes/" in body:
        fail("lab-spin.html renders a catalogue cover in the page body")


def check_runtime() -> None:
    runtime = read("assets/spin.js")
    required = (
        "const ROUNDS_PER_SESSION = 5",
        "const MAX_SPINS = 15",
        "const SOLVE_ATTEMPTS = 3",
        "const VOWEL_COST = 150",
        "const HINT_COST = 300",
        "const WRONG_SOLUTION_COST = 200",
        "const BASE_SOLVE_BONUS = 500",
        "type: 'free-vowel'",
        "type: 'miss'",
        "type: 'reset'",
        "occurrences * state.pendingValue",
        "hiddenBeforeSolve * 25",
        "fetch('episodes.json'",
        "fetch('crossword.json'",
        "state.entry.episode.subjectDescription",
        "state.entry.episode.result",
        "state.entry.episode.hotspot",
        "elements.resultLink.href = state.entry.episode.url",
        "replaceChildren(fragment)",
        "credentials: 'same-origin'",
    )
    for token in required:
        if token not in runtime:
            fail(f"assets/spin.js: required gameplay token missing: {token}")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML", "assets/images/episodes/"):
        if forbidden in runtime:
            fail(f"assets/spin.js: forbidden persistence, injection or cover token present: {forbidden}")

    episodes = load_json("episodes.json").get("episodes", [])
    for episode in episodes:
        title = episode.get("title") if isinstance(episode, dict) else None
        if isinstance(title, str) and len(title) > 3 and title in runtime:
            fail(f"assets/spin.js hard-codes an episode title: {title}")

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets/spin.js")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/spin.js syntax validation failed: {syntax.stderr or syntax.stdout}")


def check_styles() -> None:
    styles = read("assets/spin.css")
    for token in (
        ".spin-workspace",
        ".spin-wheel",
        ".spin-pointer",
        ".spin-puzzle",
        ".spin-character.is-hidden",
        ".spin-keyboard",
        ".spin-result[hidden]",
        "@media(max-width:1120px)",
        "@media(max-width:760px)",
        "@media(prefers-reduced-motion:reduce)",
    ):
        if token not in styles:
            fail(f"assets/spin.css: required responsive style missing: {token}")


def check_publication_integration() -> None:
    sitemap = read("sitemap.xml")
    if sitemap.count(BASE_URL + "lab-spin.html") != 1:
        fail("sitemap.xml must contain lab-spin.html exactly once")

    home = read("index.html")
    for token in ('href="lab-spin.html"', "Four registry-driven experiments", "FIVE HIDDEN PHRASES"):
        if token not in home:
            fail(f"index.html: Spin the Impossible discovery token missing: {token}")

    contracts = {
        "scripts/publication_qa.py": ('"spin_qa.py"',),
        "scripts/live_site_qa.py": ('"lab-spin.html"', '"assets/spin.css"', '"assets/spin.js"'),
        "scripts/phase5_sync.py": ('"lab-spin.html"',),
        "scripts/telemetry_sync.py": ('"lab-spin.html"',),
        "scripts/rss_sync.py": ('"lab-spin.html"',),
        "scripts/seo_qa.py": ('"lab-spin.html"',),
        ".github/workflows/seo-sync.yml": ("lab-spin.html", "assets/spin.css", "assets/spin.js"),
        "README.md": ("### 39.4 Spin the Impossible", "scripts/spin_qa.py"),
    }
    for path, tokens in contracts.items():
        source = read(path)
        for token in tokens:
            if token not in source:
                fail(f"{path}: Spin the Impossible publication token missing: {token}")


def main() -> int:
    phrases = check_data()
    check_game_registry()
    check_page()
    check_runtime()
    check_styles()
    check_publication_integration()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nSpin the Impossible QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Spin the Impossible QA: PASS ({phrases} registry-driven phrases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
