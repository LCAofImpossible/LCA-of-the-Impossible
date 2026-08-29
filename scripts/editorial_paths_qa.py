#!/usr/bin/env python3
"""Validate ordered editorial reading paths and their episode context navigation."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SCRIPT_VERSION = "20260829-editorial-paths1"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(relative: str) -> str:
    try:
        return (ROOT / relative).read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Unable to read {relative}: {exc}")
        return ""


def require_tokens(text: str, relative: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        if token not in text:
            fail(f"{relative}: missing editorial-path token {token!r}")


def main() -> int:
    try:
        episode_data = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
        collection_data = json.loads((ROOT / "collections.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Episode or collection registry is unavailable: {exc}")
        episode_data = {}
        collection_data = {}

    episodes = episode_data.get("episodes", [])
    published = {
        episode.get("number"): episode
        for episode in episodes
        if isinstance(episode, dict) and isinstance(episode.get("number"), int)
    }
    collections = collection_data.get("collections", [])
    seasons = collection_data.get("seasons", [])
    editorial_paths = collection_data.get("editorialPaths", [])

    if collection_data.get("schemaVersion") != 2:
        fail("collections.json: schemaVersion must be exactly 2 for guided editorial paths")
    if not isinstance(editorial_paths, list) or not editorial_paths:
        fail("collections.json: editorialPaths must be a non-empty array")
        editorial_paths = []

    collection_by_slug = {
        item.get("slug"): item for item in collections if isinstance(item, dict) and isinstance(item.get("slug"), str)
    }
    reserved_slugs = set(collection_by_slug)
    reserved_slugs.update(
        item.get("id") for item in seasons if isinstance(item, dict) and isinstance(item.get("id"), str)
    )
    seen_paths: set[str] = set()
    total_steps = 0
    for path in editorial_paths:
        if not isinstance(path, dict):
            fail("collections.json: every editorial path must be an object")
            continue
        slug = path.get("slug")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            fail(f"Invalid editorial path slug: {slug!r}")
            slug = "<invalid>"
        elif slug in reserved_slugs:
            fail(f"Editorial path slug collides with a season or collection: {slug}")
        elif slug in seen_paths:
            fail(f"Duplicate editorial path slug: {slug}")
        else:
            seen_paths.add(slug)

        minimum_lengths = {"title": 5, "eyebrow": 10, "question": 20, "description": 60}
        for field, minimum in minimum_lengths.items():
            value = path.get(field)
            if not isinstance(value, str) or len(value.strip()) < minimum:
                fail(f"Editorial path {slug!r}: {field} is missing or too short")
        if isinstance(path.get("question"), str) and not path["question"].strip().endswith("?"):
            fail(f"Editorial path {slug!r}: guiding question must end with a question mark")

        related = path.get("relatedCollections")
        if not isinstance(related, list) or not related:
            fail(f"Editorial path {slug!r}: at least one related collection is required")
            related = []
        elif len(related) != len(set(related)):
            fail(f"Editorial path {slug!r}: related collection links must be unique")
        for collection_slug in related:
            if collection_slug not in collection_by_slug:
                fail(f"Editorial path {slug!r}: unknown related collection {collection_slug!r}")

        steps = path.get("steps")
        if not isinstance(steps, list) or len(steps) < 3:
            fail(f"Editorial path {slug!r}: at least three ordered steps are required")
            continue
        if len(steps) > 6:
            fail(f"Editorial path {slug!r}: more than six steps weakens the guided sequence")
        step_numbers: list[int] = []
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                fail(f"Editorial path {slug!r} step {index}: step must be an object")
                continue
            if set(step) != {"episode", "phase", "note"}:
                fail(
                    f"Editorial path {slug!r} step {index}: only episode, phase and note may be stored; "
                    "episode data must remain registry-derived"
                )
            number = step.get("episode")
            if not isinstance(number, int) or number not in published:
                fail(f"Editorial path {slug!r} step {index}: episode #{number} is not published")
            else:
                step_numbers.append(number)
                if related and not any(number in collection_by_slug[item].get("episodes", []) for item in related):
                    fail(
                        f"Editorial path {slug!r} step {index}: episode #{number} is not connected "
                        "to any declared related collection"
                    )
            phase = step.get("phase")
            note = step.get("note")
            if not isinstance(phase, str) or len(phase.strip()) < 8:
                fail(f"Editorial path {slug!r} step {index}: progression phase is missing or too short")
            if not isinstance(note, str) or len(note.strip()) < 40:
                fail(f"Editorial path {slug!r} step {index}: editorial transition note is missing or too short")
        if len(step_numbers) != len(set(step_numbers)):
            fail(f"Editorial path {slug!r}: episode steps must be unique")
        total_steps += len(steps)

    collections_html = read("collections.html")
    engagement_js = read("assets/engagement.js")
    engagement_css = read("assets/engagement.css")
    engagement_sync = read("scripts/engagement_sync.py")
    publication_qa = read("scripts/publication_qa.py")
    live_qa = read("scripts/live_site_qa.py")

    require_tokens(
        collections_html,
        "collections.html",
        (
            'id="editorial-paths"',
            'id="editorial-path-index"',
            'id="editorial-path-list"',
            "GUIDED READING PATHS",
            "ordered editorial sequence, not a new taxonomy",
            f"assets/engagement.js?v={SCRIPT_VERSION}",
        ),
    )
    require_tokens(
        engagement_js,
        "assets/engagement.js",
        (
            "editorialPathEpisodeUrl",
            "renderEditorialPaths",
            "placeEditorialPathNavigation",
            "collectionData.editorialPaths",
            "searchParams.get('path')",
            "editorial-path-progress",
            "data-copy-path",
            "Guided reading paths",
            "Path overview",
            f"assets/engagement.css?v={SCRIPT_VERSION}",
        ),
    )
    if "episode.cover" in engagement_js:
        fail("assets/engagement.js must keep collection and path cards text-only")
    navigation_match = re.search(
        r"  const placeEditorialPathNavigation = .*?\n  const augmentArchive", engagement_js, flags=re.S
    )
    if not navigation_match:
        fail("assets/engagement.js: unable to isolate path-context navigation")
    else:
        navigation_block = navigation_match.group(0)
        for forbidden in ("location.assign", "location.replace", "history.pushState", "history.replaceState"):
            if forbidden in navigation_block:
                fail(f"Path-context navigation must not redirect or rewrite history: {forbidden!r}")

    require_tokens(
        engagement_css,
        "assets/engagement.css",
        (
            ".editorial-path-index",
            ".editorial-path-heading",
            ".editorial-path-steps",
            ".editorial-path-step",
            ".editorial-path-progress",
            ".editorial-path-progress-track",
            ".editorial-path-progress-nav",
            "@media(max-width:900px)",
            "@media(max-width:560px)",
        ),
    )
    require_tokens(
        engagement_sync,
        "scripts/engagement_sync.py",
        (
            'SCRIPT_VERSION = "20260829-editorial-paths1"',
            "### 26.2 Guided editorial paths",
            "Paths do not create a new taxonomy",
            "Invalid, unknown or mismatched path parameters",
        ),
    )
    require_tokens(publication_qa, "scripts/publication_qa.py", ('"editorial_paths_qa.py"',))
    require_tokens(live_qa, "scripts/live_site_qa.py", ("Guided editorial paths", "editorial-path-progress"))

    current_script = f"assets/engagement.js?v={SCRIPT_VERSION}"
    for page in [ROOT / "index.html", ROOT / "archive.html", ROOT / "compare.html", ROOT / "explore.html", ROOT / "collections.html"]:
        if page.is_file() and current_script not in page.read_text(encoding="utf-8"):
            fail(f"{page.relative_to(ROOT)}: guided-path engagement script version is stale")
    for episode in episodes:
        page = ROOT / str(episode.get("url", ""))
        if page.is_file() and f"../{current_script}" not in page.read_text(encoding="utf-8"):
            fail(f"{page.relative_to(ROOT)}: guided-path episode navigation script version is stale")

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets" / "engagement.js")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/engagement.js: JavaScript syntax validation failed: {syntax.stdout.strip()}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nEditorial paths QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Editorial paths QA passed: "
        f"{len(editorial_paths)} guided paths; {total_steps} ordered steps; "
        "registry-derived episode data; valid context navigation; text-only presentation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
