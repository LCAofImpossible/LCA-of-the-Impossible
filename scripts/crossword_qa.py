#!/usr/bin/env python3
"""Validate Cross the Impossible data, interface and generated layouts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
VERSION = "20260909-crossword1"
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


def check_data() -> int:
    episode_registry = load_json("episodes.json")
    crossword_registry = load_json("crossword.json")
    episodes = episode_registry.get("episodes", [])
    entries = crossword_registry.get("entries", [])
    if crossword_registry.get("schemaVersion") != 1:
        fail("crossword.json: schemaVersion must be 1")
    if not isinstance(episodes, list) or not isinstance(entries, list):
        fail("Episode and crossword registries must contain lists")
        return 0

    episode_by_number = {episode.get("number"): episode for episode in episodes if isinstance(episode, dict)}
    episode_numbers = set(episode_by_number)
    crossword_numbers: list[int] = []
    answers: set[str] = set()
    technical_terms = re.compile(r"\b(?:CO2e?|carbon|emissions?|footprint|kilograms?|tonnes?|percent|life[ -]?cycle|LCA)\b", re.I)

    for entry in entries:
        if not isinstance(entry, dict):
            fail("crossword.json contains a non-object entry")
            continue
        number = entry.get("episodeNumber")
        answer = entry.get("answer", "")
        clue = entry.get("clue", "")
        crossword_numbers.append(number)
        if not isinstance(answer, str) or not re.fullmatch(r"[A-Z0-9]{4,20}", answer):
            fail(f"Episode #{number}: answer must contain 4–20 uppercase letters or digits")
        episode = episode_by_number.get(number, {})
        normalized_title = normalize(episode.get("title", ""))
        if answer and normalized_title and answer not in normalized_title and normalized_title not in answer:
            fail(f"Episode #{number}: answer does not match the registered episode title")
        if answer in answers:
            fail(f"Episode #{number}: duplicate answer {answer}")
        answers.add(answer)
        if not isinstance(clue, str) or len(clue.strip()) < 45 or not clue.strip().endswith("."):
            fail(f"Episode #{number}: clue must be a complete sentence of at least 45 characters")
        elif normalize(answer) in normalize(clue):
            fail(f"Episode #{number}: clue reveals the answer")
        if isinstance(clue, str) and (re.search(r"\d", clue) or technical_terms.search(clue)):
            fail(f"Episode #{number}: clue contains numerical or technical LCA language")

    if len(entries) != len(episodes):
        fail(f"crossword.json must cover all {len(episodes)} episodes; found {len(entries)}")
    if len(crossword_numbers) != len(set(crossword_numbers)):
        fail("crossword.json repeats an episode number")
    missing = sorted(episode_numbers - set(crossword_numbers))
    extra = sorted(set(crossword_numbers) - episode_numbers)
    if missing:
        fail(f"crossword.json is missing episodes: {missing}")
    if extra:
        fail(f"crossword.json references unknown episodes: {extra}")
    return len(entries)


def check_game_registry() -> None:
    registry = load_json("lab-games.json")
    games = registry.get("games", [])
    expected = {
        "guess": ("lab.html", "live"),
        "crossword": ("lab-crossword.html", "live"),
    }
    found = {game.get("id"): (game.get("url"), game.get("status")) for game in games if isinstance(game, dict)}
    for game_id, contract in expected.items():
        if found.get(game_id) != contract:
            fail(f"lab-games.json: {game_id} must be registered as {contract}")
    if len(found) != len(games):
        fail("lab-games.json contains duplicate or invalid game records")


def check_page() -> None:
    page = read("lab-crossword.html")
    required = (
        'data-page="lab" data-lab-game="crossword"',
        'data-lab-game-nav',
        'id="crossword-grid"',
        'id="crossword-across"',
        'id="crossword-down"',
        'id="crossword-check"',
        'id="crossword-reveal"',
        'id="crossword-new"',
        'id="crossword-result"',
        'aria-live="assertive"',
        "Reveal a letter · −10 pts",
        f"assets/lab.css?v={VERSION}",
        f"assets/crossword.css?v={VERSION}",
        f"assets/lab-nav.js?v={VERSION}",
        f"assets/crossword-generator.js?v={VERSION}",
        f"assets/crossword.js?v={VERSION}",
        "CROSSWORD-SEO:START",
        'type="application/rss+xml"',
        'href="feed.xml"',
    )
    for token in required:
        if token not in page:
            fail(f"lab-crossword.html: required token missing: {token}")
    body = page.split("<body", 1)[-1]
    if "assets/images/episodes/" in body:
        fail("lab-crossword.html renders an episode cover in the page body")
    if "Preview" in body:
        fail("lab-crossword.html still exposes a preview label")

    guess_page = read("lab.html")
    for token in ('data-lab-game="guess"', 'data-lab-game-nav', f"assets/lab-nav.js?v={VERSION}"):
        if token not in guess_page:
            fail(f"lab.html: shared navigation token missing: {token}")


def check_publication_integration() -> None:
    sitemap = read("sitemap.xml")
    if sitemap.count(BASE_URL + "lab-crossword.html") != 1:
        fail("sitemap.xml must contain lab-crossword.html exactly once")

    home = read("index.html")
    for token in ('href="lab-crossword.html"', "Two registry-driven experiments"):
        if token not in home:
            fail(f"index.html: Cross the Impossible discovery token missing: {token}")

    manifest = load_json("site.webmanifest")
    lab_shortcuts = [
        item for item in manifest.get("shortcuts", [])
        if isinstance(item, dict) and item.get("url") == "/LCA-of-the-Impossible/lab.html"
    ]
    if len(lab_shortcuts) != 1 or "experiments" not in lab_shortcuts[0].get("description", "").lower():
        fail("site.webmanifest must describe the shared Impossible Lab experiments")

    contracts = {
        "scripts/publication_qa.py": ('"crossword_qa.py"',),
        "scripts/live_site_qa.py": ('"lab-crossword.html"', '"crossword.json"', '"assets/crossword.js"'),
        "scripts/phase5_sync.py": ('"lab-crossword.html"',),
        "scripts/telemetry_sync.py": ('"lab-crossword.html"',),
        "scripts/rss_sync.py": ('"lab-crossword.html"',),
        ".github/workflows/seo-sync.yml": ("lab-crossword.html",),
        "README.md": ("### 39.2 Cross the Impossible", "scripts/crossword_qa.py"),
    }
    for path, tokens in contracts.items():
        source = read(path)
        for token in tokens:
            if token not in source:
                fail(f"{path}: crossword publication token missing: {token}")


def check_runtime() -> None:
    controller = read("assets/crossword.js")
    generator = read("assets/crossword-generator.js")
    navigation = read("assets/lab-nav.js")
    for token in (
        "fetch('episodes.json'",
        "fetch('crossword.json'",
        "engine.generate(candidates",
        "state.correctEntries.size * 50",
        "state.revealedCells.size * 10",
        "maximumPossible",
        "episode.subjectDescription",
        "episode.result",
        "episode.hotspot",
        "episode.url",
        "input.readOnly = true",
    ):
        if token not in controller:
            fail(f"assets/crossword.js: required gameplay token missing: {token}")
    for token in ("seededRandom", "canPlace", "fallbackLayout", "validate", "seasonNumber"):
        if token not in generator:
            fail(f"assets/crossword-generator.js: required generator token missing: {token}")
    for token in ("fetch('lab-games.json'", "textContent", "aria-current"):
        if token not in navigation:
            fail(f"assets/lab-nav.js: required navigation token missing: {token}")
    for source_name, source in (("controller", controller), ("navigation", navigation)):
        for forbidden in ("document.cookie", "localStorage", "sessionStorage", "innerHTML"):
            if forbidden in source:
                fail(f"Crossword {source_name} contains forbidden persistence or HTML injection token: {forbidden}")


def check_styles() -> None:
    shared = read("assets/lab.css")
    crossword = read("assets/crossword.css")
    for token in (".lab-game-nav", '.lab-game-link[aria-current="page"]', "@media(max-width:760px)"):
        if token not in shared:
            fail(f"assets/lab.css: shared game navigation style missing: {token}")
    for token in (
        ".crossword-workspace", ".crossword-grid", ".crossword-cell.is-active",
        ".crossword-cell.is-revealed", ".crossword-clue.is-correct", "@media(max-width:1180px)",
    ):
        if token not in crossword:
            fail(f"assets/crossword.css: required responsive style missing: {token}")


def check_generator() -> None:
    try:
        completed = subprocess.run(
            ["node", str(ROOT / "scripts/crossword_generator_qa.js")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"Crossword generator QA could not run: {exc}")
        return
    if completed.returncode:
        fail((completed.stderr or completed.stdout).strip() or "Crossword generator QA failed")
    elif completed.stdout.strip():
        print(completed.stdout.strip())


def main() -> int:
    count = check_data()
    check_game_registry()
    check_page()
    check_runtime()
    check_styles()
    check_publication_integration()
    check_generator()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nCross the Impossible QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Cross the Impossible QA: PASS ({count} narrative cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
