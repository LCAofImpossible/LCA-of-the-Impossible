# LCA of the Impossible — Website Editorial & Publishing Bible

Static GitHub Pages archive for the **LCA of the Impossible** series.

This README is the canonical editorial and publishing reference for building, updating and reviewing the website. Its purpose is to make the site reproducible in a future session with no prior conversational context. If a new approved episode PDF and this repository are available, the website episode and its catalogue metadata must be rebuildable without relying on memory.

---

## 1. Source-of-truth hierarchy

Use this hierarchy whenever sources disagree:

1. **Approved episode PDF / approved LinkedIn carousel** — source of truth for episode-specific facts, numbers, assumptions, results, sensitivities, narrative conclusions, wording and approved cover artwork.
2. **An explicitly user-approved replacement image** — overrides the PDF cover only when the user has specifically selected it as the catalogue cover.
3. **This README** — source of truth for website editorial structure, publishing rules, taxonomy, asset conventions and QA requirements.
4. **`episodes.json`** — canonical website registry for published episode metadata, ordering, catalogue assets, PDF availability, taxonomy, related cases and navigation relationships.
5. **`assets/style.css`** — source of truth for the live visual system and responsive behaviour.
6. **`assets/site.js`** — source of truth for registry-driven homepage/archive rendering, text-only episode heroes, automatic PDF download actions, Related Cases and Previous/Next behaviour.
7. **`episodes/template.html`** — canonical implementation starter for new episode pages.
8. Existing episode pages — examples of execution, not authorities over the approved PDF or this README.

Do not silently replace, reconcile or “improve” approved episode content. If a website adaptation requires simplification, preserve the underlying meaning and disclose the simplification.

**Structural rule:** approved cover artwork remains part of the episode package, but the website displays episode covers **only on the homepage and in the full Archive catalogue**. Individual episode pages are deliberately image-free at hero level.

If `episodes.json` conflicts with an approved PDF, correct the registry; do not change the approved episode fact to fit the registry.

---

## 2. Canonical repository structure

- `index.html` — concise homepage with project hero, Latest Case, recent episodes, Method, Series and Book
- `archive.html` — complete searchable/filterable episode catalogue
- `episodes.json` — central episode registry and navigation/download metadata
- `episodes/` — individual episode pages and reusable episode template
- `assets/site.js` — shared catalogue, archive, PDF-action and episode-navigation logic
- `assets/style.css` — global visual system
- `assets/images/episodes/` — canonical catalogue covers used only by homepage and Archive
- `assets/images/episode-graphics/` — Inventory Map, Technical Plate and Hotspot Breakdown graphics
- `assets/images/book/` — book artwork
- `assets/pdf/episodes/` — approved downloadable episode carousels

Do not create parallel folders for temporary fixes. Avoid duplicate `live`, `v2`, `final`, `new`, `hq2`, `final-final` or similar filenames in the canonical tree. Temporary staging assets must be removed before publication.

The website must remain a simple static GitHub Pages site. Do not introduce a framework, package manager or build dependency unless explicitly required.

---

## 3. Central episode registry — mandatory

`episodes.json` is the single catalogue record used by the homepage, full archive, episode PDF action and episode-to-episode navigation.

Every published episode must contain:

- `number` — numerical episode identifier;
- `slug` — stable filename slug;
- `title` — displayed episode title;
- `url` — relative episode-page path from repository root;
- `cover` — relative canonical catalogue-cover path from repository root;
- `categoryLabel` — concise human-readable narrative category;
- `categories` — normalized subject-filter tokens;
- `lcaLabel` — principal LCA characteristic shown on cards;
- `lcaCharacteristics` — normalized LCA filter tokens;
- `result` — approved headline result;
- `hotspot` — concise approved/reconciled hotspot statement;
- `featuredDescription` — short description used when featured;
- `keywords` — useful search terms;
- `related` — ordered list of related episode numbers.

Optional field:

- `pdf` — relative path to the approved carousel in `assets/pdf/episodes/`. **Add this field only after the PDF file exists at that exact path.**

The `cover` field remains mandatory even though individual episode pages do not show a cover. It is consumed by homepage and Archive only.

### 3.1 Ordering

Episode number is the canonical website ordering key unless the user explicitly defines another release order. `assets/site.js` sorts by descending episode number. The highest published number becomes Latest Case automatically.

### 3.2 Subject-category taxonomy

Typical tokens include `mythology`, `legends`, `structures`, `science-fiction` and `fantasy`. A subject may belong to more than one category when materially useful. Do not add speculative categories for aesthetic symmetry.

### 3.3 LCA-characteristic taxonomy

Typical tokens include `materials-driven`, `operation-driven`, `energy-driven`, `mobility-driven`, `process-energy-driven`, `repetition-sensitive`, `lifetime-sensitive` and `proxy-sensitive`.

The principal label and all secondary tokens must be defensible from the actual result or sensitivity analysis.

### 3.4 Related cases

`related` is editorially controlled. Choose up to three cases connected by subject, system behaviour, modelling issue or hotspot. On individual episode pages, Related Cases are **text-only cards**.

---

## 4. Episode asset convention

Each episode may have:

- `epNN-short-slug.ext` — canonical catalogue cover, homepage/Archive only;
- `epNN-inventory-map.svg` — life-cycle input map;
- `epNN-technical-plate.svg` — engineering/reconstruction plate;
- `epNN-hotspot-breakdown.svg` — contribution/hotspot graphic;
- `epNN-short-slug.pdf` — approved downloadable carousel.

Canonical PDF naming must be stable and simple. Do not publish PDFs with temporary suffixes such as `(1)`, `rev-final`, `v2`, `copy` or similar. Normalize them to `epNN-short-slug.pdf` before adding the registry `pdf` field.

### 4.1 Canonical-cover lock

When an approved PDF/carousel exists, extract or rasterize the exact approved cover and use it as the catalogue cover. Do not redraw, regenerate, reinterpret, restyle or substitute it unless the user explicitly requests a replacement.

### 4.2 Where covers are allowed

Covers may appear only in:

- Homepage Latest Case;
- Homepage Recent Cases;
- Full Archive cards.

Covers must not appear in the individual episode hero, inventory, Related Cases, Previous/Next navigation or as decorative backgrounds in analytical graphics.

---

## 5. Mandatory editorial structure of every episode page

### 5.1 Text-only episode hero

Must contain:

- `EPISODE #NN · SERIES` eyebrow;
- title;
- central narrative question;
- main result as dominant metric;
- concise functional-unit/reporting-basis description;
- automatic **Download episode PDF ↓** action when the registry contains a valid `pdf` field.

Do not hard-code the PDF button in individual HTML pages. `assets/site.js` owns the download action so position, wording and behaviour remain consistent across all episodes.

Legacy cover markup may still exist in old episode HTML; `assets/site.js` removes `.cover-frame` at runtime. New pages must be authored without cover markup.

### 5.2 The Subject

Provide a concise reconstruction of the subject, analogue/evidence/engineering logic and explicit distinction between narrative source and modelling assumption.

### 5.3 Four Quick Facts

Use four compact cards covering different dimensions by default: geometry/scale, operation/function, main hotspot/result logic and modelling convention/uncertainty.

### 5.4 Visual Model

Always include before the detailed inventory:

- **Inventory Map**;
- **Technical Plate**.

These are analytical representations, not decorative illustrations.

### 5.5 Detailed Life Cycle Inventory

Use standard columns:

`Stage | Component / activity | Activity data | Climate change | Modelling basis`

The table must reconcile with the approved episode and remain horizontally scrollable on mobile. Add model-note cards where useful.

### 5.6 Hotspot

Always include the Hotspot Breakdown after the inventory and before result cards. Explain where the footprint lands and why.

### 5.7 Results

Use result cards only for decision-relevant outputs: principal stage/material contribution, operation/maintenance, hotspot percentage, separate disclosures, DEFRA share and useful normalized values.

### 5.8 Sensitivities and interpretation

Include sensitivities reported in the approved PDF and label them clearly as sensitivities.

### 5.9 Verdict

End with 3–5 short memorable lines or one compact statement linked to the actual hotspot.

### 5.10 Automatic episode navigation and actions

Every published episode page must include `data-episode="NN"` on `<body>` and load `../assets/site.js`.

The shared script automatically adds or manages:

- text-only hero normalization;
- registry-driven **Download episode PDF ↓** button when `pdf` exists;
- removal of obsolete legacy hard-coded PDF buttons;
- sticky internal navigation: `Subject · Model · Inventory · Hotspots · Results · Verdict`;
- section anchors;
- text-only Related Cases after Verdict;
- Previous episode / Full archive / Next episode navigation.

Do not duplicate these blocks manually.

---

## 6. Functional unit and reporting basis

Reproduce the functional unit or reporting slice used in the approved episode. It must be quantified, understandable without the PDF, specific enough to explain the result and include duration/service quantity when relevant.

For infinite, cyclic or unbounded subjects, use the finite reporting slice defined in the approved episode. Never present infinity itself as a calculable functional unit.

---

## 7. Numerical integrity rules

- Main result must match the approved episode.
- Hotspot percentages must reconcile with the total.
- Phase/material contributions must not introduce double counting.
- Use no more precision than the inventory justifies.
- Do not invent missing percentages for visual balance.
- Sensitivities are not alternative main results.
- If explanatory sub-shares sum to a parent already counted, do not add them again.
- Keep biogenic CO₂, outside-of-scopes values, avoided-production credits and other excluded quantities separate where applicable.

---

## 8. Inventory and modelling rules

Show enough information for a technically literate reader to understand the model. Preserve, when available: stage, component/process, quantity, unit, climate-change contribution and modelling basis/proxy/assumption.

The website need not reproduce every workbook row, but it must retain the principal audit trail. Analogues must be named. Engineering assumptions must remain recognizable as assumptions.

---

## 9. Supernatural and fictional elements

**Magic is not a fuel.**

Assign emissions to supernatural elements only when they can be translated into a defensible physical flow. Behaviour-only curses do not create an emission flow by themselves. Relevant physical processes with insufficient evidence should remain visible as exclusions, limitations, NQ/NM or separate scenarios as appropriate.

---

## 10. Emission-factor and DEFRA handling

Where UK Government GHG Conversion Factors are used, preserve distinctions between direct emissions, WTT, T&D where applicable, outside of scopes and biogenic reporting. Include DEFRA share where editorially useful.

Do not imply greater representativeness than the approved episode. Retain proxy-status language where material.

---

## 11. Editorial graphic system

### 11.1 Inventory Map

Show the main material/energy/operation blocks, logical flow, FU context where useful and only important inventory categories.

### 11.2 Technical Plate

Communicate physical reconstruction: geometry, dimensions, mass, route, capacity and key engineering parameters. It must be a legible schematic, not decorative linework or a tangled abstraction.

### 11.3 Hotspot Breakdown

Use real episode values, make the dominant contributor immediately visible and never invent precise percentages for visual balance.

### 11.4 Technical requirement

Use native self-contained SVG for analytical graphics wherever practical. Do not embed raster images inside SVG wrappers for the three analytical graphics.

---

## 12. Visual language

Core palette in `assets/style.css`:

- Background `#071019`
- Secondary background `#0b1622`
- Panel `#0d1b27`
- Secondary panel `#112232`
- Main text `#eef7fb`
- Muted text `#9ab0bc`
- Lines `#234557`
- Primary accent `#6de7ff`
- Light accent `#c4f7ff`
- Gold accent `#d0a563`

Direction: dark technical/blueprint atmosphere, restrained palette, fine linework, minimal dashboard styling, serious engineering tone with an epic editorial layer. Avoid generic Excel charts, rainbow palettes, purposeless icons, cartoon styling and excessive glow.

---

## 13. Catalogue-cover rules — mandatory

The cover is an approved catalogue asset, not an episode-page hero.

1. If page 1 of the approved PDF contains the final cover, use that exact cover for homepage/archive.
2. If the user explicitly approves a replacement, use that exact replacement.
3. Only when no approved cover exists may a new cover be created.

Before publication, visually compare the catalogue cover with the approved source. Any mismatch is a homepage/archive publication blocker.

---

## 14. Homepage architecture

Canonical sequence:

1. image-free project hero;
2. compact project-format strip;
3. Latest Analysis / Latest Case;
4. Recent Cases;
5. Method and process;
6. Series framing;
7. Book section.

`assets/site.js` reads `episodes.json`; do not manually duplicate Latest Case or Recent Cases content in `index.html`.

---

## 15. Full archive architecture

`archive.html` is the complete catalogue, newest first.

- 3 cards per row desktop;
- 2 tablet;
- 1 mobile.

Each card contains the canonical catalogue cover, Category · LCA lens, title, episode number, result, hotspot cue and `Explore the LCA →`.

Subject and LCA filters are generated from registry tokens and combine with AND logic. Search covers title, episode number, labels, tokens and keywords. Initial display is up to 9 matches with Load More in batches of 9.

---

## 16. PDF publishing system — mandatory

PDF download is a **registry-driven feature**.

### 16.1 File rule

The approved carousel must be stored in:

`assets/pdf/episodes/epNN-short-slug.pdf`

Use the exact approved PDF. Do not regenerate, recompress, rasterize or redesign it merely to make website upload easier unless the user explicitly approves that change.

### 16.2 Registry rule

After the file is confirmed in the repository, add:

`"pdf": "assets/pdf/episodes/epNN-short-slug.pdf"`

to that episode object in `episodes.json`.

Never add a `pdf` field before the target file exists. A missing `pdf` field means **no download button**; it must never create a broken link.

### 16.3 Rendering rule

`assets/site.js` reads the optional `pdf` field and automatically places one standardized **Download episode PDF ↓** button in the text-only episode hero.

Do not hard-code PDF buttons inside episode HTML. Legacy hard-coded PDF links are removed at runtime to prevent duplicates and inconsistent placement.

### 16.4 Publication expectation

When an approved carousel exists and is intended for public download, publication is not complete until:

1. the exact PDF is stored in `assets/pdf/episodes/`;
2. the registry `pdf` field points to it;
3. the live episode shows the download button;
4. the button opens/downloads the intended PDF successfully.

---

## 17. Paths, responsive and accessibility rules

From root files use `assets/...` and `episodes/slug.html`. From files inside `episodes/`, use `../assets/...`, `../archive.html` and `../index.html`. Avoid root-relative `/...` paths because this is a GitHub Pages project site.

Responsive/accessibility requirements:

- inventory tables scroll horizontally on mobile;
- visual grids and episode cards collapse appropriately;
- archive grid is 3/2/1 columns;
- filters wrap and search becomes full width on mobile;
- selected filters expose `aria-pressed`;
- jump navigation is horizontally scrollable;
- Previous/Next stacks on mobile;
- analytical images use meaningful alt text;
- essential information does not exist only inside images;
- no image exceeds its container;
- episode pages remain usable without catalogue-cover assets;
- PDF button text clearly states that the action downloads the episode PDF.

---

## 18. Editorial tone

Combine technical credibility, engineering reconstruction, epic storytelling, restrained irony, accessibility and transparent uncertainty. Narrative language supports the analysis; it never replaces it.

---

## 19. Quality-assurance checklist before publication

### Content

- [ ] Main result matches approved PDF.
- [ ] Functional unit/reporting slice matches.
- [ ] Hotspot percentage reconciles.
- [ ] Sensitivities are correct and labelled.
- [ ] Facts and assumptions are not conflated.
- [ ] Separate disclosures are handled correctly.

### Catalogue cover — homepage/archive only

- [ ] Cover matches page 1 or approved replacement.
- [ ] No unauthorized redraw/restyle.
- [ ] Cover renders in homepage/archive.

### Registry

- [ ] Exactly one registry entry exists for the episode.
- [ ] Number, title, URL, cover, result and hotspot reconcile.
- [ ] Categories/LCA lenses are meaningful.
- [ ] Related episode numbers exist.
- [ ] If a PDF is published, `pdf` exists and exactly matches the repository path.
- [ ] No `pdf` field points to a missing file.

### Episode page

- [ ] `<body data-episode="NN">` matches registry number.
- [ ] `../assets/site.js` loads.
- [ ] Hero is text-only.
- [ ] No cover is required on the episode page.
- [ ] If `pdf` exists, exactly one **Download episode PDF ↓** button appears in the hero.
- [ ] No obsolete hard-coded PDF button remains visible.
- [ ] Jump navigation works.
- [ ] Related Cases are text-only.
- [ ] Previous/Next order is correct.

### Inventory and graphics

- [ ] Standard inventory columns are present.
- [ ] Major flows reconcile.
- [ ] Proxies and exclusions are disclosed.
- [ ] Inventory Map, Technical Plate and Hotspot Breakdown render.
- [ ] Analytical SVGs are self-contained and legible.

### Homepage/archive

- [ ] Highest episode number is Latest Case.
- [ ] Recent Cases and Archive render from registry.
- [ ] Ordering, filters, search, count and Load More work.

### PDF download

- [ ] Approved PDF file exists in `assets/pdf/episodes/`.
- [ ] Canonical filename is used.
- [ ] Registry `pdf` path matches exact case-sensitive filename.
- [ ] Live button resolves successfully.
- [ ] Downloaded/opened file is the approved carousel, not a placeholder or altered export.

### Deployment

- [ ] Changes are on `main`.
- [ ] GitHub Pages deploys latest commit.
- [ ] Live homepage inspected.
- [ ] Live archive inspected.
- [ ] Live episode inspected.
- [ ] Live PDF action tested when applicable.

A green build alone is not sufficient evidence that the page is correct.

---

## 20. Controlled publishing workflow

For each new episode:

1. Read approved episode PDF completely.
2. Extract title, number, series, FU, result, hotspot, inventory, exclusions, sensitivities and verdict.
3. Extract/rasterize page 1 as canonical catalogue cover.
4. Visually compare cover with approved source.
5. Create Inventory Map SVG.
6. Create Technical Plate SVG.
7. Create Hotspot Breakdown SVG.
8. Build page from `episodes/template.html` and set `data-episode="NN"`.
9. Build text-only episode hero.
10. Add Quick Facts and model notes.
11. Reconcile inventory/results.
12. Add sensitivities and verdict.
13. If public download is intended, upload the **exact approved PDF** to `assets/pdf/episodes/epNN-short-slug.pdf`.
14. Add one object to `episodes.json`, including `pdf` only after the file exists.
15. Do not manually edit Latest Case, Recent Cases, archive cards, PDF buttons, filters, Previous/Next or Related Cases; they are registry-driven.
16. Verify homepage Latest/Recent and covers.
17. Verify Archive ordering, filters, search, count, Load More and covers.
18. Verify episode has no cover, navigation works and PDF action appears when registered.
19. Verify all analytical graphic paths and remove staging files.
20. Commit controlled release to `main`.
21. Inspect live homepage, archive and episode.
22. Test PDF download when applicable.
23. Only then consider publication complete.

---

## 21. Future-episode reconstruction protocol

Minimum inputs:

- this repository;
- this README;
- approved PDF of the new episode.

Optional: original high-resolution cover image, calculation workbook, LinkedIn post/source list and latest DEFRA workbook if the episode itself still needs to be produced.

With repository + README + approved PDF, the website episode and catalogue entry must be reconstructable without asking the user to restate established design rules.

---

## 22. Relationship with wider production workflow

LinkedIn remains the publishing channel; the website is the permanent technical archive. Upstream work may include historical/engineering research, FU definition, boundaries, inventory, factors, Excel model, carousel and LinkedIn post.

The website need not duplicate the full workbook but must preserve the core audit trail: **what was modelled, why, with which major flows, where the footprint lands, and what changes the result.**

---

## 23. Non-negotiable principles

1. **The approved PDF controls episode-specific facts, numbers, wording and approved cover artwork.**
2. **Approved covers are catalogue assets displayed only on homepage and Archive.**
3. **Individual episode heroes are text-only.**
4. **The README controls the web editorial system.**
5. **`episodes.json` is the single registry for catalogue metadata, navigation relationships and PDF availability.**
6. **PDF download buttons are generated by `assets/site.js`; never hard-code them per episode.**
7. **A `pdf` registry field is allowed only when the exact file exists in `assets/pdf/episodes/`.**
8. **No broken PDF link is acceptable.**
9. **Registry data must reconcile with the approved episode.**
10. **The homepage is concise; the full searchable catalogue belongs on `archive.html`.**
11. **Every episode receives the three standard analytical graphics.**
12. **Every published episode participates in automatic navigation and text-only Related Cases.**
13. **Every assumption remains recognizable as an assumption.**
14. **Analytical graphics must be browser-safe, self-contained and legible.**
15. **A successful GitHub Pages build is necessary but not sufficient: live pages and any registered PDF download must be checked.**
16. **Where others see fantasy, we see a functional unit.**
