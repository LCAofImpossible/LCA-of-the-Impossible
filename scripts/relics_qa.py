#!/usr/bin/env python3
"""Validate Impossible Relics archive pairing, scoring and Lab integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260915-relics1"
SHARED_VERSION = "20260916-origins3"
RESULTS_VERSION = "20260917-leaderboards1"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"Missing file: {path}")
        return ""
    return target.read_text(encoding="utf-8")


def load(path: str) -> dict:
    try:
        return json.loads(read(path) or "{}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is invalid JSON: {exc}")
        return {}


def main() -> int:
    episodes = load("episodes.json").get("episodes", [])
    clues = load("crossword.json").get("entries", [])
    episode_numbers = {
        int(item["number"])
        for item in episodes
        if isinstance(item, dict) and item.get("number")
    }
    clue_numbers = {
        int(item["episodeNumber"])
        for item in clues
        if isinstance(item, dict) and item.get("episodeNumber") and item.get("clue")
    }
    if len(clue_numbers) < 8:
        fail("Impossible Relics requires at least eight curated narrative pairs")
    if clue_numbers != episode_numbers:
        fail(f"Relic pool coverage mismatch: {len(clue_numbers)} clues for {len(episode_numbers)} published episodes")

    page = read("lab-relics.html")
    for token in (
        'data-lab-game="relics"', "Impossible <span>Relics.</span>",
        "EXPERIMENT 06 OF 07 · CURRENT GAME", 'id="lab-game-area"',
        'id="relics-start"', 'id="relics-board"', 'id="relics-hint"',
        'id="relics-final"', 'id="relics-review"', 'data-lab-result-scorecard',
        'data-lab-another', 'data-lab-difficulty', 'href="impossible-lab.html"',
        f"assets/relics.css?v={VERSION}", f"assets/relics.js?v={VERSION}",
        f"assets/lab-progress.js?v={SHARED_VERSION}", f"assets/lab-difficulty.js?v={SHARED_VERSION}",
        f"assets/lab-run.js?v={SHARED_VERSION}", f"assets/lab-results.js?v={RESULTS_VERSION}",
        "RELICS-SEO:START", "100 points", "10 points", "50 points",
    ):
        if token not in page:
            fail(f"lab-relics.html: required token missing: {token}")
    if "assets/images/episodes/" in page.split("<body", 1)[-1]:
        fail("lab-relics.html must not render catalogue covers in its body")

    runtime = read("assets/relics.js")
    for token in (
        "const POINTS_PER_MATCH = 100", "const MISMATCH_COST = 10", "const HINT_COST = 50",
        "fetch('episodes.json'", "fetch('crossword.json'", "difficultySystem?.config('relics')",
        "session.matched.size * POINTS_PER_MATCH", "session.penalty += MISMATCH_COST",
        "session.penalty += HINT_COST", "Math.max(0", "session.matched.add",
        "button.addEventListener('click'", "aria-pressed", "replaceChildren",
        "entry.episode.url", "Open Episode #", "window.ImpossibleLabResults?.render",
        "scoreLabel: 'Relic score'", "accuracy = session.attempts ? (pairs / session.attempts) * 100",
    ):
        if token not in runtime:
            fail(f"assets/relics.js: required gameplay token missing: {token}")
    for forbidden in (
        "document.cookie", "localStorage", "sessionStorage", "innerHTML",
        "assets/images/episodes/", "datePublished", "functionalUnit", "hotspot",
    ):
        if forbidden in runtime:
            fail(f"assets/relics.js contains forbidden persistence, injection, cover or technical token: {forbidden}")
    for episode in episodes:
        title = episode.get("title") if isinstance(episode, dict) else None
        if isinstance(title, str) and len(title) > 3 and title in runtime:
            fail(f"assets/relics.js hard-codes an episode title: {title}")

    styles = read("assets/relics.css")
    for token in (
        ".relics-workspace", ".relics-board", ".relic-card", ".relic-card.is-open",
        ".relic-card.is-matched", ".relics-review", ".relics-final",
        "@media(max-width:760px)", "@media(prefers-reduced-motion:reduce)",
    ):
        if token not in styles:
            fail(f"assets/relics.css: required responsive token missing: {token}")

    games = load("lab-games.json").get("games", [])
    record = next((game for game in games if game.get("id") == "relics"), None)
    if not record or record.get("number") != 6 or record.get("url") != "lab-relics.html" or record.get("status") != "live":
        fail("lab-games.json does not expose Impossible Relics as live Experiment 06")

    difficulty = read("assets/lab-difficulty.js")
    for token in (
        "'lab-relics.html'", "pairs: 4, hints: 2", "pairs: 6, hints: 1", "pairs: 8, hints: 0",
    ):
        if token not in difficulty:
            fail(f"assets/lab-difficulty.js: Relics configuration missing: {token}")
    if "'relics'" not in read("assets/lab-progress.js"):
        fail("assets/lab-progress.js does not include the Relics Lab Score contribution")
    if 'data-game-id="relics"' not in read("impossible-lab-run.html"):
        fail("Impossible Lab Run does not include the Relics stage")
    if 'data-game-id="relics"' not in read("impossible-lab.html"):
        fail("Impossible Lab hub does not include the Relics card")

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets/relics.js")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/relics.js syntax validation failed: {syntax.stderr or syntax.stdout}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nImpossible Relics QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Impossible Relics QA: PASS ({len(clue_numbers)} archive pairs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
