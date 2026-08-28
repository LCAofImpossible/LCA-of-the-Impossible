#!/usr/bin/env python3
"""Validate the versioned episode metadata contract and its staged migration.

The validator intentionally uses only the Python standard library so the same
checks run locally and in GitHub Actions. It validates every populated
``structuredMetadata`` object and permits an absent object only when the
episode is explicitly listed in the controlled migration manifest.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "episode-structured-metadata.schema.json"
MIGRATION_PATH = ROOT / "verification" / "structured-metadata-migration.json"
REGISTRY_PATH = ROOT / "episodes.json"

ROOT_GROUPS = ("schemaVersion", "subject", "assessment", "impact", "model", "provenance")
EXPECTED_BATCHES = (
    ("season-ii-30-39", 30, 39),
    ("season-ii-40-49", 40, 49),
    ("season-ii-50-59", 50, 59),
    ("season-ii-60-71", 60, 71),
)
UNIT_TO_KG = {
    "kg CO₂e": 1.0,
    "t CO₂e": 1_000.0,
    "kt CO₂e": 1_000_000.0,
    "Mt CO₂e": 1_000_000_000.0,
}
LCA_LABEL_TO_DRIVER = {
    "Materials-driven": "materials",
    "Operation-driven": "operation",
    "Energy-driven": "energy",
    "Process-energy-driven": "process-energy",
    "Biology-driven": "biology",
}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"Missing file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
        return {}
    return value


def exact_keys(value: Any, expected: set[str], label: str) -> bool:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"unexpected {extra}")
        fail(f"{label} fields are invalid ({'; '.join(details)})")
        return False
    return True


def schema_enum(schema: dict[str, Any], definition: str, field: str) -> set[Any]:
    try:
        values = schema["$defs"][definition]["properties"][field]["enum"]
    except (KeyError, TypeError):
        fail(f"Schema enum is missing: {definition}.{field}")
        return set()
    if not isinstance(values, list) or len(values) != len({json.dumps(item) for item in values}):
        fail(f"Schema enum must be a unique array: {definition}.{field}")
        return set()
    return set(values)


def array_item_enum(schema: dict[str, Any], definition: str, field: str) -> set[str]:
    try:
        node = schema["$defs"][definition]["properties"][field]
        if "items" in node:
            values = node["items"]["enum"]
        else:
            array_node = node["anyOf"][0]
            if "$ref" in array_node:
                referenced_definition = array_node["$ref"].rsplit("/", 1)[-1]
                values = schema["$defs"][referenced_definition]["items"]["enum"]
            else:
                values = array_node["items"]["enum"]
    except (KeyError, IndexError, TypeError):
        fail(f"Schema array enum is missing: {definition}.{field}")
        return set()
    if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
        fail(f"Schema array enum is invalid: {definition}.{field}")
        return set()
    return set(values)


def check_schema(schema: dict[str, Any]) -> int | None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail("Structured metadata schema must use JSON Schema draft 2020-12")
    if schema.get("$id") != (
        "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
        "schemas/episode-structured-metadata.schema.json"
    ):
        fail("Structured metadata schema has an unexpected canonical $id")
    if schema.get("additionalProperties") is not False:
        fail("Structured metadata schema must reject unknown root fields")
    if schema.get("required") != list(ROOT_GROUPS):
        fail("Structured metadata schema root groups or ordering changed unexpectedly")
    try:
        version = schema["properties"]["schemaVersion"]["const"]
    except (KeyError, TypeError):
        fail("Structured metadata schema does not declare a fixed schemaVersion")
        return None
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        fail("Structured metadata schemaVersion must be a positive integer")
        return None

    definitions = schema.get("$defs", {})
    for group in ROOT_GROUPS[1:]:
        definition = definitions.get(group)
        if not isinstance(definition, dict):
            fail(f"Structured metadata schema is missing $defs.{group}")
            continue
        if definition.get("additionalProperties") is not False:
            fail(f"$defs.{group} must reject unknown fields")
        properties = definition.get("properties", {})
        if not isinstance(properties, dict) or set(definition.get("required", [])) != set(properties):
            fail(f"Every $defs.{group} field must be explicitly required")

    serialized = json.dumps(schema, ensure_ascii=False)
    for forbidden in ("shortDescription", "subjectDescription", "featuredDescription"):
        if forbidden in serialized:
            fail(f"Schema must not absorb the separate subject-description task: {forbidden}")
    return version


def enum_value(value: Any, allowed: set[Any], label: str, nullable: bool = True) -> None:
    if value is None and nullable:
        return
    if value not in allowed or (value is None and not nullable):
        fail(f"{label} has unsupported value {value!r}")


def text_or_null(value: Any, label: str) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        fail(f"{label} must be null or a non-empty string")


def number(value: Any, label: str, *, nullable: bool = False, minimum: float | None = None) -> None:
    if value is None and nullable:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail(f"{label} must be {'null or ' if nullable else ''}a finite number")
        return
    if minimum is not None and value < minimum:
        fail(f"{label} must be at least {minimum:g}")


def enum_array(value: Any, allowed: set[str], label: str, *, nullable: bool = False, nonempty: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, list):
        fail(f"{label} must be {'null or ' if nullable else ''}an array")
        return
    if nonempty and not value:
        fail(f"{label} must not be empty")
    if len(value) != len(set(item for item in value if isinstance(item, str))):
        fail(f"{label} must not contain duplicates")
    for item in value:
        if not isinstance(item, str) or item not in allowed:
            fail(f"{label} contains unsupported value {item!r}")


def nested_value(metadata: dict[str, Any], path: str) -> Any:
    group, field = path.split(".", 1)
    return metadata[group][field]


def validate_metadata(episode: dict[str, Any], schema: dict[str, Any], version: int) -> None:
    number_value = episode.get("number")
    label = f"Episode #{number_value} structuredMetadata"
    metadata = episode.get("structuredMetadata")
    if not exact_keys(metadata, set(ROOT_GROUPS), label):
        return
    if metadata["schemaVersion"] != version:
        fail(f"{label}.schemaVersion must be {version}")

    group_fields: dict[str, set[str]] = {}
    for group in ROOT_GROUPS[1:]:
        expected = set(schema["$defs"][group]["properties"])
        if exact_keys(metadata[group], expected, f"{label}.{group}"):
            group_fields[group] = expected
    if len(group_fields) != len(ROOT_GROUPS) - 1:
        return

    subject = metadata["subject"]
    for field in ("narrativeDomain", "entityType", "scaleClass", "mobilityClass"):
        enum_value(subject[field], schema_enum(schema, "subject", field), f"{label}.subject.{field}")
    text_or_null(subject["narrativeOrigin"], f"{label}.subject.narrativeOrigin")

    assessment = metadata["assessment"]
    for field in ("reportingBasisType", "boundaryType", "technologyContext"):
        enum_value(assessment[field], schema_enum(schema, "assessment", field), f"{label}.assessment.{field}")
    for field in ("referenceFlow", "temporalContext", "geographicContext", "cutoffSummary"):
        text_or_null(assessment[field], f"{label}.assessment.{field}")
    number(assessment["lifetimeYears"], f"{label}.assessment.lifetimeYears", nullable=True, minimum=0)
    stages = array_item_enum(schema, "assessment", "includedStages")
    enum_array(
        assessment["includedStages"],
        stages,
        f"{label}.assessment.includedStages",
        nullable=True,
        nonempty=True,
    )
    enum_array(
        assessment["excludedStages"],
        array_item_enum(schema, "assessment", "excludedStages"),
        f"{label}.assessment.excludedStages",
        nullable=True,
    )
    if isinstance(assessment["includedStages"], list) and isinstance(assessment["excludedStages"], list):
        overlap = sorted(set(assessment["includedStages"]) & set(assessment["excludedStages"]))
        if overlap:
            fail(f"{label} includes and excludes the same life-cycle stages: {overlap}")

    impact = metadata["impact"]
    if impact["indicator"] != "climate-change-total":
        fail(f"{label}.impact.indicator must be 'climate-change-total'")
    number(impact["value"], f"{label}.impact.value")
    enum_value(impact["unit"], schema_enum(schema, "impact", "unit"), f"{label}.impact.unit", nullable=False)
    number(impact["normalizedKgCO2e"], f"{label}.impact.normalizedKgCO2e")
    enum_value(impact["hotspotStage"], schema_enum(schema, "impact", "hotspotStage"), f"{label}.impact.hotspotStage")
    number(impact["hotspotSharePercent"], f"{label}.impact.hotspotSharePercent", nullable=True, minimum=0)
    share = impact["hotspotSharePercent"]
    if isinstance(share, (int, float)) and not isinstance(share, bool) and share > 100:
        fail(f"{label}.impact.hotspotSharePercent must not exceed 100")
    if (
        isinstance(impact["value"], (int, float))
        and not isinstance(impact["value"], bool)
        and isinstance(impact["normalizedKgCO2e"], (int, float))
        and not isinstance(impact["normalizedKgCO2e"], bool)
        and impact["unit"] in UNIT_TO_KG
    ):
        expected_kg = impact["value"] * UNIT_TO_KG[impact["unit"]]
        if not math.isclose(impact["normalizedKgCO2e"], expected_kg, rel_tol=1e-9, abs_tol=1e-6):
            fail(
                f"{label}.impact.normalizedKgCO2e must equal value converted from {impact['unit']} "
                f"({expected_kg:g} kg CO₂e)"
            )

    model = metadata["model"]
    enum_value(model["archetype"], schema_enum(schema, "model", "archetype"), f"{label}.model.archetype")
    driver_values = schema_enum(schema, "model", "primaryDriver")
    enum_value(model["primaryDriver"], driver_values, f"{label}.model.primaryDriver", nullable=False)
    enum_array(model["secondaryDrivers"], array_item_enum(schema, "model", "secondaryDrivers"), f"{label}.model.secondaryDrivers")
    enum_value(
        model["repetitionClass"],
        schema_enum(schema, "model", "repetitionClass"),
        f"{label}.model.repetitionClass",
    )
    if model["primaryDriver"] in model["secondaryDrivers"]:
        fail(f"{label}.model.primaryDriver must not be repeated in secondaryDrivers")
    expected_driver = LCA_LABEL_TO_DRIVER.get(episode.get("lcaLabel"))
    if expected_driver is None:
        fail(f"Episode #{number_value} has an unsupported lcaLabel for structured metadata")
    elif model["primaryDriver"] != expected_driver:
        fail(
            f"{label}.model.primaryDriver must be {expected_driver!r} "
            f"for lcaLabel {episode.get('lcaLabel')!r}"
        )

    provenance = metadata["provenance"]
    if provenance["sourceStatus"] != "approved-episode-only":
        fail(f"{label}.provenance.sourceStatus must be 'approved-episode-only'")
    if provenance["approvedEpisodeNumber"] != number_value:
        fail(f"{label}.provenance.approvedEpisodeNumber must match the registry episode number")
    missing_values = provenance["missingApprovedFields"]
    allowed_missing = array_item_enum(schema, "provenance", "missingApprovedFields")
    enum_array(missing_values, allowed_missing, f"{label}.provenance.missingApprovedFields")
    if isinstance(missing_values, list):
        if missing_values != sorted(missing_values):
            fail(f"{label}.provenance.missingApprovedFields must be alphabetically sorted")
        actual_nulls = sorted(path for path in allowed_missing if nested_value(metadata, path) is None)
        if missing_values != actual_nulls:
            fail(
                f"{label}.provenance.missingApprovedFields must exactly list null approved fields; "
                f"expected {actual_nulls}"
            )


def integer_list(value: Any, label: str) -> list[int]:
    if not isinstance(value, list):
        fail(f"{label} must be an array")
        return []
    if any(not isinstance(item, int) or isinstance(item, bool) or item < 1 for item in value):
        fail(f"{label} must contain positive integers only")
        return []
    if value != sorted(set(value)):
        fail(f"{label} must be unique and numerically sorted")
    return value


def check_migration(
    migration: dict[str, Any],
    episodes: list[dict[str, Any]],
    schema_version: int,
) -> tuple[set[int], int]:
    expected_keys = {
        "schemaVersion",
        "metadataField",
        "schemaPath",
        "introducedOn",
        "sourcePolicy",
        "seasonIPolicy",
        "seasonIIBatches",
        "allowedMissingEpisodeNumbers",
    }
    if not exact_keys(migration, expected_keys, "Structured metadata migration manifest"):
        return set(), 0
    if migration["schemaVersion"] != schema_version:
        fail("Migration manifest schemaVersion must match the structured metadata schema")
    if migration["metadataField"] != "structuredMetadata":
        fail("Migration manifest metadataField must be 'structuredMetadata'")
    if migration["schemaPath"] != str(SCHEMA_PATH.relative_to(ROOT)):
        fail("Migration manifest schemaPath must point to the canonical schema")
    if migration["sourcePolicy"] != "approved-episode-only":
        fail("Migration manifest must retain the approved-episode-only source policy")

    by_number = {episode.get("number"): episode for episode in episodes}
    season_i = migration["seasonIPolicy"]
    if exact_keys(season_i, {"mode", "currentLegacyExceptions"}, "seasonIPolicy"):
        if season_i["mode"] != "populate-on-republication":
            fail("Season I metadata must be populated only on re-publication")
        season_i_exceptions = integer_list(
            season_i["currentLegacyExceptions"],
            "seasonIPolicy.currentLegacyExceptions",
        )
    else:
        season_i_exceptions = []
    for number_value in season_i_exceptions:
        episode = by_number.get(number_value)
        if episode is None or episode.get("seasonId") != "season-i":
            fail(f"Season I legacy exception #{number_value} is not a published Season I episode")

    batches = migration["seasonIIBatches"]
    if not isinstance(batches, list) or len(batches) != len(EXPECTED_BATCHES):
        fail("Migration manifest must retain the four approved Season II batches")
        batches = []
    remaining_numbers: list[int] = []
    seen_batch_numbers: set[int] = set()
    for index, expected in enumerate(EXPECTED_BATCHES):
        if index >= len(batches):
            break
        batch = batches[index]
        label = f"seasonIIBatches[{index}]"
        if not exact_keys(batch, {"id", "episodeRange", "status", "remainingEpisodeNumbers"}, label):
            continue
        expected_id, start, end = expected
        if batch["id"] != expected_id or batch["episodeRange"] != [start, end]:
            fail(f"{label} must remain the approved {expected_id} range #{start}–{end}")
        remaining = integer_list(batch["remainingEpisodeNumbers"], f"{label}.remainingEpisodeNumbers")
        if any(number_value < start or number_value > end for number_value in remaining):
            fail(f"{label}.remainingEpisodeNumbers contains a number outside #{start}–{end}")
        duplicate = seen_batch_numbers & set(remaining)
        if duplicate:
            fail(f"Season II migration numbers appear in more than one batch: {sorted(duplicate)}")
        seen_batch_numbers.update(remaining)
        remaining_numbers.extend(remaining)
        published_in_range = {
            number_value
            for number_value, episode in by_number.items()
            if isinstance(number_value, int)
            and start <= number_value <= end
            and episode.get("seasonId") == "season-ii"
        }
        for number_value in remaining:
            episode = by_number.get(number_value)
            if episode is None or episode.get("seasonId") != "season-ii":
                fail(f"{label} remaining episode #{number_value} is not a published Season II episode")
            elif "structuredMetadata" in episode:
                fail(f"{label} still lists episode #{number_value} after metadata was populated")
        status = batch["status"]
        expected_status = "complete" if not remaining else (
            "pending" if set(remaining) == published_in_range else "partial"
        )
        if status != expected_status:
            fail(f"{label}.status must be {expected_status!r} for its remaining episodes")

    allowed = integer_list(
        migration["allowedMissingEpisodeNumbers"],
        "allowedMissingEpisodeNumbers",
    )
    expected_allowed = sorted(season_i_exceptions + remaining_numbers)
    if allowed != expected_allowed:
        fail("allowedMissingEpisodeNumbers must equal Season I exceptions plus all batch remainders")
    return set(allowed), len(batches)


def check_publication_integration() -> None:
    publication_path = ROOT / "scripts" / "publication_qa.py"
    live_path = ROOT / "scripts" / "live_site_qa.py"
    try:
        publication = publication_path.read_text(encoding="utf-8")
        live = live_path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Unable to inspect structured metadata publication integration: {exc}")
        return
    if '"structured_metadata_qa.py"' not in publication:
        fail("scripts/publication_qa.py must run structured_metadata_qa.py")
    for relative in (SCHEMA_PATH.relative_to(ROOT), MIGRATION_PATH.relative_to(ROOT)):
        if f'"{relative}"' not in live:
            fail(f"scripts/live_site_qa.py must verify the deployed {relative}")


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    migration = load_json(MIGRATION_PATH)
    registry = load_json(REGISTRY_PATH)
    schema_version = check_schema(schema)
    if schema_version is None:
        schema_version = -1

    if registry.get("structuredMetadataSchemaVersion") != schema_version:
        fail("episodes.json structuredMetadataSchemaVersion must match the canonical schema")
    episodes = registry.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        fail("episodes.json must contain a non-empty episodes array")
        episodes = []
    if any(not isinstance(episode, dict) for episode in episodes):
        fail("Every episodes.json episode must be an object")
        episodes = [episode for episode in episodes if isinstance(episode, dict)]

    allowed_missing, batch_count = check_migration(migration, episodes, schema_version)
    check_publication_integration()
    populated = 0
    actual_missing: set[int] = set()
    for episode in episodes:
        number_value = episode.get("number")
        if not isinstance(number_value, int) or isinstance(number_value, bool):
            continue
        if "structuredMetadata" in episode:
            populated += 1
            if number_value in allowed_missing:
                fail(f"Episode #{number_value} has metadata but remains in the migration exemption list")
            validate_metadata(episode, schema, schema_version)
        else:
            actual_missing.add(number_value)

    if actual_missing != allowed_missing:
        unexpected = sorted(actual_missing - allowed_missing)
        stale = sorted(allowed_missing - actual_missing)
        if unexpected:
            fail(f"Episodes missing required structuredMetadata without an exemption: {unexpected}")
        if stale:
            fail(f"Migration exemptions no longer missing structuredMetadata: {stale}")

    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        print(f"\nStructured metadata QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(
        "Structured metadata QA passed: "
        f"schema v{schema_version}; {populated}/{len(episodes)} populated; "
        f"{len(actual_missing)} controlled migration exemptions across {batch_count} Season II batches."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
