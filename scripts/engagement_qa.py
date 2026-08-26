#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def require(relative: str) -> Path:
    path = ROOT / relative
    if not path.is_file():
        fail(f"Missing Phase 4 file: {relative}")
    return path


def main() -> int:
    episode_path = require("episodes.json")
    collection_path = require("collections.json")
    page = require("collections.html")
    engagement_js = require("assets/engagement.js")
    require("assets/engagement.css")
    sitemap = require("sitemap.xml")
    readme = require("README.md")

    episode_data = json.loads(episode_path.read_text(encoding="utf-8")) if episode_path.is_file() else {}
    episodes = episode_data.get("episodes", [])
    published = {episode.get("number") for episode in episodes if isinstance(episode, dict)}

    collection_data = json.loads(collection_path.read_text(encoding="utf-8")) if collection_path.is_file() else {}
    seasons = collection_data.get("seasons", [])
    if not isinstance(seasons, list):
        fail("collections.json: seasons must be an array")
        seasons = []
    seen_seasons: set[str] = set()
    for season in seasons:
        season_id = season.get("id")
        if not isinstance(season_id, str) or not SLUG.fullmatch(season_id):
            fail(f"Invalid season id: {season_id!r}")
        elif season_id in seen_seasons:
            fail(f"Duplicate season id: {season_id}")
        else:
            seen_seasons.add(season_id)
        for field in ("label", "title", "descriptor", "editorialDescriptor"):
            if not isinstance(season.get(field), str) or len(season.get(field, "").strip()) < 5:
                fail(f"Season {season_id!r}: missing meaningful {field}")
        episode_range = season.get("episodeRange")
        if not isinstance(episode_range, list) or len(episode_range) != 2 or not all(isinstance(value, int) for value in episode_range):
            fail(f"Season {season_id!r}: episodeRange must contain two integers")
        numbers = season.get("episodes")
        if not isinstance(numbers, list) or not numbers:
            fail(f"Season {season_id!r}: at least one published episode is required")
        else:
            for number in numbers:
                if number not in published:
                    fail(f"Season {season_id!r}: episode #{number} is not published")
            registered_numbers = {
                episode.get("number")
                for episode in episodes
                if episode.get("seasonId") == season_id
            }
            if set(numbers) != registered_numbers:
                fail(f"Season {season_id!r}: listed episodes do not match registry season metadata")
    collections = collection_data.get("collections")
    if not isinstance(collections, list) or not collections:
        fail("collections.json: collections must be a non-empty array")
        collections = []

    seen: set[str] = set()
    for item in collections:
        slug = item.get("slug")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            fail(f"Invalid collection slug: {slug!r}")
        elif slug in seen:
            fail(f"Duplicate collection slug: {slug}")
        else:
            seen.add(slug)

        for field in ("title", "eyebrow", "description"):
            value = item.get(field)
            if not isinstance(value, str) or len(value.strip()) < (20 if field == "description" else 3):
                fail(f"Collection {slug!r}: {field} is missing or too short")

        numbers = item.get("episodes")
        if not isinstance(numbers, list) or len(numbers) < 2:
            fail(f"Collection {slug!r}: at least two episode numbers are required")
            continue
        if len(numbers) != len(set(numbers)):
            fail(f"Collection {slug!r}: episode numbers must be unique")
        for number in numbers:
            if number not in published:
                fail(f"Collection {slug!r}: episode #{number} is not published")

    by_slug = {item.get("slug"): item for item in collections if isinstance(item, dict)}
    for episode in episodes:
        for slug in episode.get("collectionSlugs", []):
            collection = by_slug.get(slug)
            if not collection:
                fail(f"Episode #{episode.get('number')}: collectionSlugs references unknown collection {slug!r}")
            elif episode.get("number") not in collection.get("episodes", []):
                fail(f"Episode #{episode.get('number')}: collection membership is not reciprocal for {slug!r}")

    linkedin = collection_data.get("socialLinks", {}).get("linkedin")
    if linkedin is not None:
        if not isinstance(linkedin, str) or not linkedin.startswith("https://www.linkedin.com/"):
            fail("socialLinks.linkedin must be null or an explicit https://www.linkedin.com/ URL")

    if engagement_js.is_file():
        text = engagement_js.read_text(encoding="utf-8")
        for token in (
            "renderCollections",
            "renderSeasons",
            "randomCase",
            "data-copy-linkedin-caption",
            "data-random-collection",
            "canonicalEpisodeUrl",
        ):
            if token not in text:
                fail(f"assets/engagement.js missing Phase 4 token: {token}")
        if "episode.cover" in text:
            fail("assets/engagement.js must not render episode covers on the Collections page")

    if page.is_file():
        text = page.read_text(encoding="utf-8")
        canonical = BASE_URL + "collections.html"
        if canonical not in text:
            fail("collections.html: canonical URL missing")
        if "<!-- ENGAGEMENT-SEO:START -->" not in text or "<!-- ENGAGEMENT-SEO:END -->" not in text:
            fail("collections.html: Phase 4 SEO block missing")
        if 'data-page="collections"' not in text:
            fail("collections.html: data-page=collections missing")
        if 'id="season-list"' not in text:
            fail("collections.html: season route container missing")
        if re.search(r'<img\b[^>]*assets/images/episodes/', text, flags=re.I):
            fail("collections.html must remain text-only and must not render episode cover images")

    public_pages = [
        ROOT / "index.html",
        ROOT / "archive.html",
        ROOT / "compare.html",
        ROOT / "explore.html",
        ROOT / "collections.html",
        *[ROOT / episode["url"] for episode in episodes],
    ]
    for public in public_pages:
        if not public.is_file():
            continue
        text = public.read_text(encoding="utf-8")
        if len(re.findall(r'assets/engagement\.js', text)) != 1:
            fail(f"{public.relative_to(ROOT)}: expected exactly one engagement.js script")

    if sitemap.is_file():
        url = BASE_URL + "collections.html"
        if sitemap.read_text(encoding="utf-8").count(url) != 1:
            fail("sitemap.xml must contain exactly one collections.html entry")

    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        if "<!-- PHASE4-RULES:START -->" not in text or "<!-- PHASE4-RULES:END -->" not in text:
            fail("README.md: Phase 4 rules block missing")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nPhase 4 QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(f"Phase 4 QA passed for {len(seasons)} seasons, {len(collections)} collections and {len(episodes)} episodes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
