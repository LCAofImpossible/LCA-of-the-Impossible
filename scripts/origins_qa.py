#!/usr/bin/env python3
"""Validate the Impossible Origins geographic registry and canonical joins."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

ORIGIN_TYPES = {"public-debut", "documented-attestation", "cultural-tradition"}
PRECISIONS = {"country", "cultural-area", "macroregion", "indeterminate"}
CONFIDENCE_LEVELS = {"documented", "qualified", "contested"}
ENTRY_FIELDS = {
    "episodeNumber",
    "originType",
    "mapRegion",
    "acceptedMapRegions",
    "originLabel",
    "countryCodes",
    "culturalArea",
    "precision",
    "confidence",
    "eligible",
    "locationBasis",
    "ambiguityNote",
}
FORBIDDEN_ENTRY_FIELDS = {
    "title",
    "slug",
    "url",
    "orderYear",
    "dateLabel",
    "eraLabel",
    "event",
    "source",
    "datePublished",
    "publicationDate",
}


def fail(message: str) -> None:
    errors.append(message)


def load(path: str) -> dict:
    target = ROOT / path
    if not target.is_file():
        fail(f"Missing file: {path}")
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path} is invalid JSON: {exc}")
        return {}


def validate_era_bands(bands: list[dict]) -> None:
    expected_ids = [
        "ancient",
        "medieval",
        "early-modern",
        "nineteenth-century",
        "twentieth-century",
        "contemporary",
    ]
    if [band.get("id") for band in bands] != expected_ids:
        fail("origins.json era bands do not match the approved Phase 1 sequence")
        return
    previous_max: int | None = None
    for index, band in enumerate(bands):
        if not band.get("label"):
            fail(f"Era band {band.get('id', index)} has no label")
        minimum = band.get("minimumOrderYear")
        maximum = band.get("maximumOrderYear")
        if index == 0 and minimum is not None:
            fail("The ancient era band must remain open-ended below")
        if index == len(bands) - 1 and maximum is not None:
            fail("The contemporary era band must remain open-ended above")
        if previous_max is not None and minimum != previous_max + 1:
            fail(f"Era bands are not contiguous before {band.get('id')}")
        if minimum is not None and maximum is not None and minimum > maximum:
            fail(f"Era band {band.get('id')} has an inverted range")
        previous_max = maximum


def main() -> int:
    episodes = load("episodes.json").get("episodes", [])
    timeline_entries = load("timeline.json").get("entries", [])
    registry = load("origins.json")

    episode_numbers = {
        int(item["number"])
        for item in episodes
        if isinstance(item, dict) and item.get("number") is not None
    }
    timeline_numbers = {
        int(item["episodeNumber"])
        for item in timeline_entries
        if isinstance(item, dict) and item.get("episodeNumber") is not None
    }

    if registry.get("schemaVersion") != 1:
        fail("origins.json schemaVersion must be 1")
    if not registry.get("originDefinition"):
        fail("origins.json must state the canonical origin definition")

    regions = registry.get("macroRegions", [])
    if not isinstance(regions, list) or len(regions) != 14:
        fail("origins.json must expose the 14 approved macroregions")
        regions = []
    region_ids = [item.get("id") for item in regions if isinstance(item, dict)]
    if len(region_ids) != len(set(region_ids)):
        fail("origins.json contains duplicate macroregion IDs")
    for region in regions:
        if not isinstance(region, dict) or not region.get("id") or not region.get("label"):
            fail(f"origins.json contains an incomplete macroregion: {region}")
    valid_regions = set(region_ids)

    bands = registry.get("eraBands", [])
    if not isinstance(bands, list) or len(bands) != 6:
        fail("origins.json must expose the six approved era bands")
        bands = []
    validate_era_bands(bands)

    entries = registry.get("entries", [])
    if not isinstance(entries, list):
        fail("origins.json entries must be an array")
        entries = []

    seen: set[int] = set()
    eligible_numbers: set[int] = set()
    used_regions: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("origins.json contains a non-object entry")
            continue
        missing = ENTRY_FIELDS - set(entry)
        if missing:
            fail(f"Origins entry is missing fields {sorted(missing)}: {entry}")
        forbidden = FORBIDDEN_ENTRY_FIELDS & set(entry)
        if forbidden:
            fail(f"Origins entry duplicates canonical fields {sorted(forbidden)}: {entry}")

        number = int(entry.get("episodeNumber", 0))
        if number in seen:
            fail(f"origins.json duplicates Episode #{number}")
        seen.add(number)
        if number not in episode_numbers:
            fail(f"origins.json references unpublished Episode #{number}")
        if number not in timeline_numbers:
            fail(f"origins.json Episode #{number} has no Timeline record")

        if entry.get("originType") not in ORIGIN_TYPES:
            fail(f"Episode #{number} has an invalid originType")
        if entry.get("precision") not in PRECISIONS:
            fail(f"Episode #{number} has an invalid precision")
        if entry.get("confidence") not in CONFIDENCE_LEVELS:
            fail(f"Episode #{number} has an invalid confidence")
        if not isinstance(entry.get("eligible"), bool):
            fail(f"Episode #{number} eligible must be boolean")

        accepted = entry.get("acceptedMapRegions")
        if not isinstance(accepted, list) or len(accepted) != len(set(accepted)):
            fail(f"Episode #{number} must have a unique acceptedMapRegions array")
            accepted = []
        unknown = set(accepted) - valid_regions
        if unknown:
            fail(f"Episode #{number} uses unknown regions: {sorted(unknown)}")

        map_region = entry.get("mapRegion")
        if entry.get("eligible"):
            eligible_numbers.add(number)
            if map_region not in valid_regions:
                fail(f"Eligible Episode #{number} has no valid mapRegion")
            if map_region not in accepted:
                fail(f"Eligible Episode #{number} does not accept its canonical mapRegion")
            if entry.get("precision") == "indeterminate":
                fail(f"Eligible Episode #{number} cannot have indeterminate precision")
            used_regions.update(accepted)
        else:
            if map_region is not None or accepted:
                fail(f"Ineligible Episode #{number} must not expose accepted regions")

        country_codes = entry.get("countryCodes")
        if not isinstance(country_codes, list) or len(country_codes) != len(set(country_codes)):
            fail(f"Episode #{number} must have a unique countryCodes array")
        else:
            for code in country_codes:
                if not isinstance(code, str) or not re.fullmatch(r"[A-Z]{2}", code):
                    fail(f"Episode #{number} has invalid country code: {code}")

        for field in ("originLabel", "culturalArea", "locationBasis"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                fail(f"Episode #{number} has no usable {field}")
        note = entry.get("ambiguityNote")
        if note is not None and (not isinstance(note, str) or not note.strip()):
            fail(f"Episode #{number} ambiguityNote must be null or a non-empty string")
        if entry.get("confidence") in {"qualified", "contested"} and not note:
            fail(f"Episode #{number} requires an ambiguityNote for {entry.get('confidence')} confidence")
        if entry.get("confidence") == "contested" and entry.get("eligible"):
            fail(f"Contested Episode #{number} cannot be eligible")
        if number <= 29 and entry.get("originType") != "public-debut":
            fail(f"Season I Episode #{number} must use public-debut originType")

    if seen != episode_numbers:
        missing = sorted(episode_numbers - seen)
        extra = sorted(seen - episode_numbers)
        fail(f"origins.json coverage mismatch; missing={missing}, extra={extra}")
    if timeline_numbers != episode_numbers:
        fail("Origins cannot be complete while timeline.json and episodes.json coverage differ")
    if not ({1, 2, 3, 4} <= eligible_numbers):
        fail("Origins must retain all currently published Season I cases")
    if len(eligible_numbers) < 12:
        fail("Origins does not expose a useful playable pool")
    if len(used_regions) < 8:
        fail("Origins playable pool does not provide sufficient geographic variety")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nImpossible Origins registry QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Impossible Origins registry QA: PASS "
        f"({len(entries)} records, {len(eligible_numbers)} eligible, {len(used_regions)} regions used)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
