# Impossible Origins — Phase 5 Lab integration

Status: implemented in the publication source. This phase promotes Experiment 07 from an isolated prototype to a complete Impossible Lab game. Live deployment and final browser acceptance remain Phase 6 work.

## Public catalogue and navigation

`lab-games.json` registers Impossible Origins as live Experiment 07 with its public route, concise card description, full summary, estimated duration and Geography category. The registry now drives seven cards and seven links across:

- the Impossible Lab hub;
- the shared selector on every game page;
- random game selection and end-of-game actions;
- sitemap, SEO, RSS discovery and telemetry propagation.

The static hub and game navigation retain the same seven entries as an accessible fallback when JavaScript is unavailable.

## Lab Score migration

Impossible Origins is the seventh official contribution in `assets/lab-progress.js`. A completed Analyst round can contribute up to 1,000 normalized points, increasing the combined maximum from 6,000 to 7,000.

The existing `lca-impossible-lab-progress-v1` storage key and record schema are preserved. Consequently:

- every previously saved score remains unchanged;
- the new Origins contribution begins at zero until the player completes it;
- Explorer and Impossible records remain separate and do not affect the official Lab Score;
- a lower later result cannot reduce either the Origins record or the combined Lab Score.

## Seven-stage Lab Run

Impossible Origins is the final stage after Impossible Relics. A complete Run now combines seven current Analyst results for a maximum of 7,000 points.

The Run schema version advances from 1 to 2. An unfinished six-stage Run is reset once because it cannot be compared safely with the new seven-stage circuit. Personal game records and the persistent Lab Score are never cleared by this migration.

## Automation contract

`scripts/lab_sync.py` is the canonical generator for:

- the seven-game static navigation and experiment counters;
- Lab hub, Run and Origins metadata;
- shared asset cache versions;
- the public sitemap entries;
- the Impossible Lab README contract.

The global navigation, telemetry, RSS, SEO, publication and live-site scripts now include the Origins route and its runtime assets. The mandatory publication gate includes both Origins registry QA and Origins UI QA.

## Phase 5 QA gate

Phase 5 passes only when:

- all 44 published episodes have eligible Origins records;
- all seven live games appear in the registry, hub and shared selector;
- Analyst Origins results update the official Lab Score and the maximum is 7,000;
- the Lab Run accepts Origins only after Relics and completes at a maximum of 7,000;
- the old six-stage Run payload is rejected through the schema-version migration;
- Origins has indexable metadata and occurs exactly once in the sitemap;
- the Lab synchronizer is idempotent;
- all seven game QA suites and the Lab-only discovery, telemetry, RSS and SEO checks pass.

Badges remain intentionally outside this phase.
