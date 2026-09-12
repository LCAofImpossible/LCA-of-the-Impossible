#!/usr/bin/env python3
"""Validate Impossible Timeline chronology, scoring and Lab integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260912-timeline1"
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
    episode_numbers = {int(item["number"]) for item in episodes if isinstance(item, dict) and item.get("number")}
    timeline = load("timeline.json")
    entries = timeline.get("entries", [])
    if not isinstance(entries, list) or len(entries) < 12:
        fail("timeline.json must expose a useful cross-season historical pool")
        entries = []
    seen: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("timeline.json contains a non-object entry")
            continue
        for field in ("episodeNumber", "orderYear", "dateLabel", "eraLabel", "event", "source"):
            if entry.get(field) in (None, ""):
                fail(f"timeline.json entry is missing {field}: {entry}")
        number = int(entry.get("episodeNumber", 0))
        if number in seen:
            fail(f"timeline.json duplicates Episode #{number}")
        seen.add(number)
        if number not in episode_numbers:
            fail(f"timeline.json references unpublished Episode #{number}")
    if seen != episode_numbers:
        fail(f"timeline.json coverage mismatch: {len(seen)} historical records for {len(episode_numbers)} published episodes")
    raw_registry = read("timeline.json")
    for forbidden in ("datePublished", "dateModified", "publicationDate", "lcaCharacteristics", "hotspot"):
        if forbidden in raw_registry:
            fail(f"timeline.json contains forbidden non-historical field: {forbidden}")

    page = read("lab-timeline.html")
    for token in (
        'data-lab-game="timeline"', "Impossible <span>Timeline.</span>",
        "EXPERIMENT 05 OF 05 · CURRENT GAME", 'id="lab-game-area"',
        'id="timeline-start"', 'id="timeline-list"', 'id="timeline-submit"',
        'id="timeline-reveal-list"', 'id="timeline-final"', 'data-lab-result-scorecard',
        'data-lab-another', 'data-lab-difficulty', 'href="impossible-lab.html"',
        f"assets/timeline.css?v={VERSION}", f"assets/timeline.js?v={VERSION}",
        f"assets/lab-progress.js?v={VERSION}", f"assets/lab-difficulty.js?v={VERSION}",
        f"assets/lab-run.js?v={VERSION}", f"assets/lab-results.js?v={VERSION}",
        "TIMELINE-SEO:START", "earlier/later controls",
    ):
        if token not in page:
            fail(f"lab-timeline.html: required token missing: {token}")
    if "assets/images/episodes/" in page.split("<body", 1)[-1]:
        fail("lab-timeline.html must not render catalogue covers in its body")

    runtime = read("assets/timeline.js")
    for token in (
        "const POINTS_PER_PAIR = 100", "fetch('episodes.json'", "fetch('timeline.json'",
        "difficultySystem?.config('timeline')", "rules.spreadYears", "chooseCloseSet",
        "session.order[left].orderYear < session.order[right].orderYear", "session.correctPairs += correct",
        "window.ImpossibleLabResults?.render", "scoreLabel: 'Chronology score'",
        "item.addEventListener('dragstart'", "makeMoveButton", "replaceChildren",
        "Historical basis:", "entry.episode.url", "Open Episode #",
    ):
        if token not in runtime:
            fail(f"assets/timeline.js: required gameplay token missing: {token}")
    for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML", "datePublished", "lcaCharacteristics", "hotspot"):
        if forbidden in runtime:
            fail(f"assets/timeline.js contains forbidden persistence, injection or non-historical token: {forbidden}")

    styles = read("assets/timeline.css")
    for token in (".timeline-workspace", ".timeline-card", ".timeline-move", ".timeline-reveal", ".timeline-episode-link", ".timeline-final", "@media(max-width:760px)", "@media(prefers-reduced-motion:reduce)"):
        if token not in styles:
            fail(f"assets/timeline.css: required responsive token missing: {token}")

    games = load("lab-games.json").get("games", [])
    record = next((game for game in games if game.get("id") == "timeline"), None)
    if not record or record.get("number") != 5 or record.get("url") != "lab-timeline.html" or record.get("status") != "live":
        fail("lab-games.json does not expose Impossible Timeline as live Experiment 05")

    difficulty = read("assets/lab-difficulty.js")
    for token in ("'lab-timeline.html'", "cards: 3, rounds: 4", "cards: 4, rounds: 5", "cards: 5, rounds: 5"):
        if token not in difficulty:
            fail(f"assets/lab-difficulty.js: Timeline configuration missing: {token}")
    if "'timeline'" not in read("assets/lab-progress.js"):
        fail("assets/lab-progress.js does not include the Timeline Lab Score contribution")
    if 'data-game-id="timeline"' not in read("impossible-lab-run.html"):
        fail("Impossible Lab Run does not include the Timeline stage")

    syntax = subprocess.run(["node", "--check", str(ROOT / "assets/timeline.js")], cwd=ROOT, capture_output=True, text=True, check=False)
    if syntax.returncode:
        fail(f"assets/timeline.js syntax validation failed: {syntax.stderr or syntax.stdout}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nImpossible Timeline QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Impossible Timeline QA: PASS ({len(entries)} historical records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
