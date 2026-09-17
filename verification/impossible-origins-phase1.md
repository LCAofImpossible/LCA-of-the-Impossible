# Impossible Origins — Phase 1 editorial specification

Status: approved design baseline. This document defines the content rules for the future Experiment 07. It does not register a live game, change the Lab Score or alter the Lab Run.

Phase 2 implementation note: `origins.json` now applies this specification to all 44 published episodes and `scripts/origins_qa.py` validates the registry. The ten-record file remains the historical Phase 1 sample. Its provisional exclusion of Episode #35 was resolved during the full source review: the approved 1790 account places the sailors' story at the Cape of Good Hope, so the production registry admits the subject as a qualified South African geographic record.

## 1. Purpose and separation from existing games

Impossible Origins asks **where an impossible subject entered human culture** and uses its already curated real-world chronology as a secondary time classification.

- The subject title remains visible. The player is not asked to identify it, keeping the mechanic distinct from Guess the Impossible.
- The player selects a geographic origin rather than arranging several subjects, keeping the mechanic distinct from Impossible Timeline.
- No subject-to-clue pairs are hidden or matched, keeping the mechanic distinct from Impossible Relics.
- Episode publication dates and fictional in-universe chronology are never eligible evidence.

Canonical prompt:

> Every impossible story began somewhere. Find its origin.

## 2. Canonical origin rule

For game purposes, `origin` means:

> The geographic area associated with the earliest documented attestation or public debut of the specific subject version analysed by the episode.

The rule is applied by season as follows.

### Season I — Machines & Worlds

Use the place associated with the first public release of the fictional machine or system in the work that introduced the analysed version. Do not use:

- the fictional place where the machine was built or operates;
- the real manufacturing location of a physical prop or product when it differs from the narrative work's origin;
- a later adaptation, sequel or remake;
- the LCA of the Impossible episode publication location or date.

Example: the DeLorean Time Machine is assigned to the United States and 1985 because the analysed time-machine version debuted in the American film *Back to the Future*. The DMC-12 production location in Northern Ireland is not the answer to this game.

### Season II — Myths & Legends

Use the cultural or geographic area established by the same earliest documented source already selected for Impossible Timeline. Do not replace a documented source with a speculative place of oral origin.

When a tradition spans several modern states, the record must use a cultural area and macroregion rather than force a modern country. Modern borders are descriptive aids only and must not be presented as historical ownership.

## 3. Geographic taxonomy

The first implementation uses macroregions rather than exact map coordinates. This keeps the map usable on mobile and avoids false precision.

| ID | Player-facing label | Typical scope |
|---|---|---|
| `northern-europe` | Northern Europe | British Isles, Scandinavia, Iceland and the Baltic area |
| `western-europe` | Western Europe | France, Benelux, Germany, Austria and Switzerland |
| `southern-europe-mediterranean` | Southern Europe & Mediterranean | Iberia, Italy, Greece, the Balkans and Mediterranean islands |
| `eastern-europe` | Eastern Europe | Eastern European and broader Slavic cultural areas |
| `north-africa` | North Africa | Mediterranean Africa and the Sahara's northern cultural areas |
| `sub-saharan-africa` | Sub-Saharan Africa | West, Central, East and Southern Africa south of the Sahara |
| `west-asia` | West Asia | Anatolia, the Levant, Mesopotamia, Arabia and Iran |
| `central-asia` | Central Asia | The Central Asian steppe and adjacent cultural areas |
| `south-asia` | South Asia | The Indian subcontinent and associated traditions |
| `east-asia` | East Asia | China, Japan, Korea and adjacent cultural areas |
| `southeast-asia` | Southeast Asia | Mainland and maritime Southeast Asia |
| `north-america` | North America | Canada, the United States, Mexico and associated areas |
| `latin-america-caribbean` | Latin America & Caribbean | Central America, South America and the Caribbean |
| `oceania` | Oceania | Australia, New Zealand, Melanesia, Micronesia and Polynesia |

`indeterminate` is reserved as an editorial status and is not a selectable map region. A record with an indeterminate origin is not eligible for play.

Country codes and human-readable locations may be stored for the reveal, but the MVP scores the macroregion only. A future exact-country mode may use those fields only where the evidence supports that precision.

## 4. Time classification

Impossible Origins must join `timeline.json`; it must not duplicate `orderYear`, `dateLabel`, `eraLabel`, `event` or `source` in its own runtime registry.

The player-facing period is derived deterministically from `timeline.json.orderYear`:

| Period ID | Player-facing label | Rule |
|---|---|---|
| `ancient` | Ancient world | before 500 CE |
| `medieval` | Medieval world | 500–1499 |
| `early-modern` | Early modern world | 1500–1799 |
| `nineteenth-century` | Nineteenth century | 1800–1899 |
| `twentieth-century` | Twentieth century | 1900–1999 |
| `contemporary` | Contemporary | 2000 onward |

If a future Timeline record cannot provide a defensible effective year, the subject remains ineligible for Origins until the chronology is resolved. The period is secondary to geography and must not become another ordering exercise.

## 5. Ambiguity and eligibility rules

| Evidence condition | Treatment |
|---|---|
| One documented country or cultural area | Eligible at country precision and macroregion scoring |
| One documented cultural area spanning modern borders | Eligible at macroregion precision; reveal the cultural area |
| Several accepted locations inside the same macroregion | Eligible; store all documented labels but score the shared macroregion |
| Several accepted locations in different macroregions | Eligible only if every documented macroregion can be accepted without changing the episode's subject version |
| A global motif with one specific version selected by the episode | Eligible for the documented version; disclose the broader tradition in `ambiguityNote` |
| Disputed attribution without a stable geographic basis | Not eligible |
| Location inferred only from a fictional setting, prop manufacture or episode publication | Not eligible |
| Missing matching entry in `episodes.json` or `timeline.json` | Not eligible |

No approximate neighbouring region is stored as a correct answer merely to make the game easier. Any Explorer tolerance belongs to gameplay configuration, not to the content record.

## 6. Canonical data join and future registry boundary

The future runtime will use three joined sources:

1. `episodes.json` — title, season, canonical URL and approved episode data;
2. `timeline.json` — authoritative year, date label, historical event and source basis;
3. `origins.json` — geographic classification and its editorial rationale only.

The proposed Origins-specific record contains:

- `episodeNumber` — unique join key;
- `originType` — `public-debut`, `documented-attestation` or `cultural-tradition`;
- `mapRegion` — one canonical selectable macroregion or `null`;
- `acceptedMapRegions` — documented alternatives only;
- `originLabel` — concise reveal label;
- `countryCodes` — optional ISO alpha-2 codes used for context, never as historical ownership claims;
- `culturalArea` — historical or editorial cultural label;
- `precision` — `country`, `cultural-area`, `macroregion` or `indeterminate`;
- `confidence` — `documented`, `qualified` or `contested`;
- `eligible` — runtime inclusion gate;
- `locationBasis` — concise reason for the geographic assignment;
- `ambiguityNote` — required when qualification or competing interpretations must be disclosed.

Titles, dates, source names and episode URLs must not be copied into `origins.json`.

## 7. Phase 1 sample

The machine-readable sample is stored in `verification/impossible-origins-phase1-sample.json`. It covers all four currently published Season I cases and six Season II cases, including macroregion-only and excluded examples.

| Episode | Subject | Geographic result | Precision | Eligibility |
|---|---|---|---|---|
| #1 | UFO Robot | Japan / East Asia | Country | Eligible |
| #2 | Millennium Falcon | United States / North America | Country | Eligible |
| #3 | DeLorean Time Machine | United States / North America | Country | Eligible |
| #4 | TARDIS | United Kingdom / Northern Europe | Country | Eligible |
| #35 | The Flying Dutchman | Contested maritime tradition | Indeterminate | Excluded pending review |
| #40 | The Minotaur's Labyrinth | Crete, Greece / Southern Europe & Mediterranean | Country | Eligible |
| #46 | Nautilus | France / Western Europe | Country | Eligible |
| #53 | Baba Yaga's Hut | Slavic cultural sphere / Eastern Europe | Cultural area | Eligible |
| #70 | El Dorado | Muisca territory, present-day Colombia / Latin America & Caribbean | Country | Eligible |
| #71 | The Cosmic Turtle | South Asian Sanskrit tradition / South Asia | Macroregion | Eligible with qualification |

## 8. Gate for Phase 2

Phase 2 may begin only when the following conditions remain true:

- the origin definition is applied consistently across both seasons;
- temporal metadata is reused from `timeline.json` rather than duplicated;
- macroregions are the scored geographic unit for the MVP;
- modern countries are not imposed on transnational ancient or folkloric traditions;
- ambiguous records can be excluded without weakening the rest of the pool;
- subject titles remain visible throughout play;
- future episode maintenance requires at most one geographic record after its Timeline entry is approved;
- the sample parses correctly, has unique episode numbers and joins to both canonical registries.
