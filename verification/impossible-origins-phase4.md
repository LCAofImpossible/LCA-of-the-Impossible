# Impossible Origins — Phase 4 gameplay specification

Status: implemented prototype rules. This phase adds challenge levels, scoring and device-local level records without registering Experiment 07 in the public Lab catalogue, Lab Score or Lab Run.

## Challenge levels

| Level | Cases | Geographic assistance | Historical assistance | Subject evidence | Pool treatment |
|---|---:|---|---|---|---|
| Explorer | 8 | Four candidate macroregions, including every accepted answer | Period labels and year ranges | Approved title and description | Standard random pool with two Season I cases when available |
| Analyst | 10 | Complete 14-region map with labels | Period labels and year ranges | Approved title and description | Standard random pool with two Season I cases when available |
| Impossible | 12 | Complete 14-region map without labels | Period labels without year ranges | Approved title only | Qualified cultural origins are prioritised after two Season I cases |

The subject title remains visible at every level, as required by the Phase 1 separation rule. Difficulty changes presentation and case selection only; it never changes the accepted geographic evidence in `origins.json` or the time classification derived from `timeline.json`.

## Scoring

Every case has a fixed maximum of 250 points:

- correct macroregion: 100 points;
- correct historical period: 100 points;
- both components correct in the same case: 50-point perfect-origin bonus.

There are no negative points. A perfect answer extends the current perfect-origin streak; any partial or incorrect answer resets it. The streak is reported for feedback and does not increase the theoretical maximum.

| Level | Maximum raw score |
|---|---:|
| Explorer | 2,000 |
| Analyst | 2,500 |
| Impossible | 3,000 |

The shared result component converts the raw result to the Lab scale using `round(score / maximum × 1,000)`. Accuracy is calculated from the 16, 20 or 24 independently scored region/period components. Completion reaches 100% only after every case in the selected level has been confirmed.

## Record boundary

Explorer, Analyst and Impossible use separate device-local personal bests through the shared difficulty store. Phase 4 deliberately keeps Origins outside `ImpossibleLabProgress.GAME_IDS` and `ImpossibleLabRun.GAME_IDS`:

- an Origins result can update its level-specific raw and normalized personal best;
- it cannot change the existing six-game Lab Score;
- it cannot be accepted as a Lab Run stage;
- `lab-games.json`, the public hub, game navigation and sitemap remain unchanged.

Phase 5 will perform the coordinated public integration and migrate the combined systems from six to seven experiments.

## QA gate

Phase 4 passes only when:

- all three configurations expose the approved case counts and assistance rules;
- every round has a fixed 250-point maximum;
- Explorer candidates always include all accepted macroregions;
- Impossible keeps the subject title visible while hiding the description, map labels and numeric era ranges;
- normalized records are stored separately by level;
- Analyst Origins records do not enter the six-game Lab Score;
- the prototype remains absent from `lab-games.json` and `sitemap.xml`;
- the existing Lab, Timeline and Origins registry checks continue to pass.
