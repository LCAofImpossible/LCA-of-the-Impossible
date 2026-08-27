#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SEASONS = {
    "season-i": {
        "number": 1,
        "label": "Season I — Machines & Worlds",
        "range": (1, 29),
    },
    "season-ii": {
        "number": 2,
        "label": "Season II — Myths & Legends",
        "range": (30, 71),
    },
}
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def require_token(text: str, token: str, label: str) -> None:
    if token not in text:
        fail(f"{label}: missing season-filter contract token {token!r}")


def main() -> int:
    registry_path = ROOT / "episodes.json"
    archive_path = ROOT / "archive.html"
    index_path = ROOT / "index.html"
    script_path = ROOT / "assets/site.js"
    style_path = ROOT / "assets/style.css"

    for path in (registry_path, archive_path, index_path, script_path, style_path):
        if not path.is_file():
            fail(f"Missing season-filter file: {path.relative_to(ROOT)}")

    counts = {season_id: 0 for season_id in EXPECTED_SEASONS}
    if registry_path.is_file():
        try:
            episodes = json.loads(registry_path.read_text(encoding="utf-8")).get("episodes", [])
        except (json.JSONDecodeError, OSError) as exc:
            fail(f"episodes.json is unavailable or invalid: {exc}")
            episodes = []
        for episode in episodes:
            season_id = episode.get("seasonId")
            if season_id not in EXPECTED_SEASONS:
                fail(f"Episode #{episode.get('number', '?')}: unsupported or missing seasonId {season_id!r}")
                continue
            expected = EXPECTED_SEASONS[season_id]
            number = episode.get("number")
            if episode.get("seasonNumber") != expected["number"]:
                fail(f"Episode #{number}: seasonNumber does not match {season_id}")
            if episode.get("seasonLabel") != expected["label"]:
                fail(f"Episode #{number}: seasonLabel does not match {season_id}")
            if not isinstance(number, int) or not expected["range"][0] <= number <= expected["range"][1]:
                fail(f"Episode #{number}: outside the controlled range for {season_id}")
            counts[season_id] += 1
        for season_id, total in counts.items():
            if total < 1:
                fail(f"{season_id}: no published episodes available for the filter")

    if archive_path.is_file():
        archive = archive_path.read_text(encoding="utf-8")
        require_token(archive, 'id="season-filters"', "archive.html")
        require_token(archive, 'aria-label="Filter episodes by season"', "archive.html")
        require_token(archive, 'assets/site.js?v=20260827-season-filters', "archive.html")

    if index_path.is_file():
        index = index_path.read_text(encoding="utf-8")
        require_token(index, 'href="archive.html?season=season-i"', "index.html")
        require_token(index, 'assets/site.js?v=20260827-season-filters', "index.html")

    if script_path.is_file():
        site_js = script_path.read_text(encoding="utf-8")
        for token in (
            "URLSearchParams(window.location.search)",
            "url.searchParams.set('season', activeSeason)",
            "url.searchParams.delete('season')",
            "window.history[method]",
            "window.addEventListener('popstate'",
            "filter-count",
            "seasonCounts",
            "aria-pressed",
            "archive.html?season=season-i",
        ):
            require_token(site_js, token, "assets/site.js")
        syntax = subprocess.run(
            ["node", "--check", str(script_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if syntax.returncode:
            fail(f"assets/site.js failed JavaScript syntax validation: {syntax.stdout.strip()}")

    if style_path.is_file():
        require_token(style_path.read_text(encoding="utf-8"), ".filter-count", "assets/style.css")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nSeason filter QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Season filter QA passed for "
        f"Season I ({counts['season-i']}) and Season II ({counts['season-ii']}) episodes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
