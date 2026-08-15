# LCA of the Impossible — Website Editorial & Publishing Bible

Static GitHub Pages archive for the **LCA of the Impossible** series.

This README is the canonical editorial and publishing reference for building, updating and reviewing episode pages. Its purpose is to make the website reproducible even in a future session with no prior conversational context.

If a new episode PDF and this repository are available, the page should be rebuildable without relying on memory.

---

## 1. Source-of-truth hierarchy

Use the following hierarchy whenever sources disagree or a future episode is reconstructed.

1. **Episode PDF / approved carousel** — source of truth for episode-specific facts, numbers, assumptions, results, sensitivities, narrative conclusions and wording.
2. **This README** — source of truth for website editorial structure, publishing rules, asset conventions and QA requirements.
3. **`assets/style.css`** — source of truth for the live visual system, palette, responsive behaviour and component styling.
4. **`episodes/template.html`** — canonical implementation starter for a new episode page.
5. Existing episode pages — examples of execution, not authorities over the PDF or this README.

Do not silently replace, reconcile or “improve” numerical content from an approved episode PDF. If a website adaptation requires simplification, preserve the underlying meaning and disclose the simplification.

---

## 2. Canonical repository structure

- `index.html` — homepage and episode archive
- `episodes/` — individual episode pages and reusable episode template
- `assets/style.css` — global visual system
- `assets/images/episodes/` — canonical episode covers
- `assets/images/episode-graphics/` — editorial inventory, technical and hotspot graphics
- `assets/images/book/` — book artwork
- `assets/pdf/episodes/` — downloadable episode carousels

Do not create parallel folders for temporary fixes. Avoid duplicate `live`, `v2`, `final`, `new`, `hq2` or similar filenames in the canonical tree.

---

## 3. Episode asset convention

Each episode uses one canonical cover plus three standard editorial graphics:

- `epNN-short-slug.ext` — canonical cover
- `epNN-inventory-map.svg` — visual map of the main life-cycle inputs
- `epNN-technical-plate.svg` — engineering / reconstruction plate
- `epNN-hotspot-breakdown.svg` — contribution / hotspot graphic
- `epNN-short-slug.pdf` — downloadable carousel when available

Current canonical covers:

- `ep35-flying-dutchman.jpg`
- `ep36-tower-of-babel.png`
- `ep43-sisyphus.svg`

Use the original source format for covers when it is the most reliable and highest-quality web asset. A cover may later be replaced with a better raster image without changing page structure or naming conventions.

---

## 4. Mandatory editorial structure of every episode page

Every episode should follow this sequence unless the subject genuinely requires a justified deviation.

### 4.1 Cover hero

Must contain:

- canonical episode cover;
- `EPISODE #NN · SERIES` eyebrow;
- episode title;
- one central narrative question;
- main result as the dominant metric;
- short description of the functional unit / reporting basis.

The hero should communicate the problem in seconds. Do not overload it with methodology.

### 4.2 The Subject

A short editorial framing section containing:

- one strong subheading;
- concise reconstruction of the subject;
- explanation of the real analogue, evidence or engineering logic used;
- explicit distinction between narrative source and modelling assumption when relevant.

Tone: technical, confident, cinematic. It must not read like a generic LCA report introduction.

### 4.3 Four Quick Facts

Use four compact cards. As a default, cover four different dimensions:

1. **Geometry / scale** — dimensions, mass, capacity, route, energy scale or equivalent.
2. **Operation / function** — what the subject does and how the FU is delivered.
3. **Main hotspot / result logic** — dominant contributor or key physical insight.
4. **Modelling convention / uncertainty** — lifetime allocation, reporting slice, proxy, supernatural rule or major assumption.

Do not repeat the same fact four ways.

### 4.4 Visual Model

Always include two graphics before the detailed inventory:

- **Inventory Map**
- **Technical Plate**

The section heading should explain that these are compact representations of the reconstructed system, not decorative illustrations.

### 4.5 Detailed Life Cycle Inventory

Use the standard table columns:

`Stage | Component / activity | Activity data | Climate change | Modelling basis`

The table should reconcile with the approved episode result and must remain horizontally scrollable on mobile.

After the table, add model-note cards where useful. Typical categories:

- Included
- Excluded / separate disclosure
- Emission-factor logic
- Supernatural rule
- Main proxy / limitation

### 4.6 Hotspot section

Always include the **Hotspot Breakdown** graphic after the inventory and before the result cards.

The surrounding text should answer one question: **where does the footprint actually land, and why?**

### 4.7 Results

Use result cards for the most decision-relevant outputs. Examples:

- main stage / material contribution;
- operation or maintenance contribution;
- main hotspot percentage;
- separate biogenic disclosure;
- DEFRA share when relevant;
- per-cycle / per-year / per-unit result when analytically useful.

Do not use result cards for trivia.

### 4.8 Sensitivities and interpretation

Include sensitivities reported in the approved episode PDF. Typical cases:

- lifetime / annualisation;
- alternative energy or material factor;
- mass or geometry variation;
- efficiency;
- recovery rate;
- alternative allocation / modelling convention.

Sensitivity results must be visually and verbally separated from the main result.

### 4.9 Verdict

End with a short, memorable interpretation linking the LCA result to the nature of the subject.

The verdict should normally contain 3–5 short lines or one compact editorial statement. It should be memorable but technically anchored in the actual hotspot.

---

## 5. Functional unit and reporting basis

The website must reproduce the functional unit or reporting slice used in the approved episode.

Requirements:

- quantified;
- understandable without reading the PDF;
- sufficiently specific to explain the main result;
- duration / service quantity stated when relevant;
- construction allocation convention stated when it materially affects interpretation.

For infinite, cyclic or otherwise unbounded subjects, use the finite reporting slice defined in the approved episode. Never present infinity itself as a calculable functional unit.

---

## 6. Numerical integrity rules

Website values must reconcile with the episode PDF.

### Mandatory rules

- Main result must match the approved episode.
- Hotspot percentages must reconcile with the total.
- Phase and material contributions must not introduce double counting.
- Use no more precision than justified by the underlying inventory.
- Do not invent missing percentages merely to make a chart look complete.
- Sensitivity values must be labelled as sensitivities, not alternatives to the main result.
- If explanatory sub-shares sum to a parent flow already counted in the total, state that they are explanatory and do not add them again.

### Separate disclosures

Where applicable, keep separate:

- biogenic CO₂;
- outside-of-scopes values;
- avoided-production credits;
- other quantities excluded from the main GWP result.

Do not silently fold separate disclosures into the headline result.

---

## 7. Inventory and modelling rules

The website inventory should show enough information for a technically literate reader to understand how the result was built.

For each significant flow, preserve when available:

- stage;
- component / process;
- quantity;
- unit;
- climate-change contribution;
- modelling basis, proxy or assumption.

The website is not required to reproduce every workbook row, but it must retain the principal audit trail.

When the episode uses analogues, state them clearly. When a value is an engineering assumption, do not present it as historical or canonical fact.

---

## 8. Supernatural and fictional elements

Apply the project rule consistently:

**Magic is not a fuel.**

A supernatural element is only assigned emissions when it can be translated into a defensible physical flow.

Examples:

- a curse that only changes narrative behaviour → no emission flow by itself;
- magical propulsion replacing combustion → model the physical system actually used, not an invented fuel;
- repeated resurrection with no defined material or energy flow → exclude and explain;
- supernatural return that dissipates mechanical energy → model the physical energy consequence if the approved episode does so.

Never add emissions simply because an element is “magical”.

---

## 9. Emission-factor and DEFRA handling

Where the approved episode uses UK Government GHG Conversion Factors, preserve the distinction between:

- direct emissions;
- WTT;
- T&D where applicable;
- outside of scopes;
- biogenic reporting.

If the episode reports the proportion of the result based on DEFRA factors, include it where editorially useful.

Do not imply that a DEFRA proxy is more representative than the source episode states. Phrases such as “accounting proxy”, “screening proxy” or “weak representativeness” should be retained when material to interpretation.

---

## 10. Editorial graphic system

Every episode uses three graphics in the same design family.

### 10.1 Inventory Map

Purpose: explain the model logic at a glance.

Should show:

- main material / energy / operation blocks;
- logical flow or grouped inputs;
- functional-unit or reporting-slice context when useful;
- only the most important inventory categories.

It is not a decorative mood board.

### 10.2 Technical Plate

Purpose: communicate the physical reconstruction.

Typical content:

- geometry;
- dimensions;
- mass;
- route;
- capacity;
- key engineering parameters;
- sectional / silhouette / schematic representation.

It should look like an editorial engineering plate, not a corporate infographic.

### 10.3 Hotspot Breakdown

Purpose: show the quantitative contribution structure.

Rules:

- use real episode values;
- make the dominant contributor immediately visible;
- minor contributors may be grouped when individual percentages are not material;
- never invent precise percentages for visual balance;
- main result may be repeated if it helps interpretation.

### 10.4 Technical requirement for graphics

Use **native self-contained SVG** wherever practical.

Do not embed WebP, PNG or other raster images inside SVG wrappers. Previous embedded-image wrappers caused inconsistent rendering across browsers.

SVGs should contain their own shapes, paths, text and vector geometry and should render independently.

---

## 11. Visual language

The live visual system is defined by `assets/style.css`.

Current core palette:

- Background: `#071019`
- Secondary background: `#0b1622`
- Panel: `#0d1b27`
- Secondary panel: `#112232`
- Main text: `#eef7fb`
- Muted text: `#9ab0bc`
- Lines: `#234557`
- Primary accent: `#6de7ff`
- Light accent: `#c4f7ff`
- Gold accent: `#d0a563`

Graphic direction:

- dark technical / blueprint atmosphere;
- restrained palette;
- fine technical linework;
- minimal dashboard styling;
- high information density without clutter;
- serious engineering tone with an epic editorial layer.

Avoid:

- generic Excel charts;
- rainbow palettes;
- stock-dashboard visuals;
- decorative icons without analytical purpose;
- cartoon styling;
- excessive gradients or glow effects.

Episode-specific accent colours may appear in covers or graphics when justified by the episode identity, but they must remain compatible with the global dark technical system.

---

## 12. Cover rules

The cover is a major editorial asset, not a placeholder.

Preference order:

1. approved PDF / LinkedIn cover if visually strong and high quality;
2. improved cover derived from the same visual concept;
3. newly generated cinematic cover consistent with the series.

Cover requirements:

- vertical composition;
- strong subject recognition;
- cinematic / epic atmosphere;
- readable episode title;
- no visual clutter;
- no low-resolution placeholders;
- no visibly schematic temporary artwork when a final cover is available.

If the canonical cover changes, replace only the canonical asset and the necessary references. Do not create chains of `v2`, `live`, `hq`, `final-final` files.

---

## 13. Homepage rules

When a new episode is published:

### Latest Case

The newest episode becomes the featured `LATEST CASE` unless explicitly decided otherwise.

The feature contains:

- cover;
- title;
- short reconstruction description;
- episode number;
- headline result;
- hotspot badge;
- link to the episode page.

### Archive cards

The new episode must also remain in the archive grid.

Each card contains:

- square crop of the canonical cover;
- series label;
- episode title;
- episode number;
- headline result;
- concise hotspot / inventory cue.

Do not remove older episodes when adding a new one.

The homepage hero remains image-free unless the site design is explicitly changed.

---

## 14. PDF handling

When the approved episode PDF is available and intended for download:

- store it in `assets/pdf/episodes/`;
- use a canonical filename such as `epNN-short-slug.pdf`;
- add an `Open episode PDF →` button in the episode page;
- open in a new tab where appropriate.

If the PDF has not yet been uploaded to the repository, do not create a broken download link.

---

## 15. Page path convention

From `index.html`:

- `assets/images/...`
- `episodes/slug.html`

From files inside `episodes/`:

- `../assets/images/...`
- `../assets/pdf/...`
- `../index.html#episodes`

Avoid root-relative paths beginning with `/` because this site is a GitHub Pages project site rather than a domain-root site.

---

## 16. Responsive and accessibility rules

The site must remain usable on mobile.

Requirements:

- inventory tables use horizontal scrolling rather than compressed unreadable text;
- visual model grid collapses to one column on smaller screens;
- episode cards collapse to one column;
- images use meaningful `alt` text;
- editorial graphics use `loading="lazy"` and `decoding="async"` where appropriate;
- headings remain legible without forcing horizontal scrolling;
- do not place essential information only inside an image if the page text does not communicate it elsewhere.

---

## 17. Editorial tone

The website is not a conventional corporate LCA portal.

Tone should combine:

- technical credibility;
- engineering reconstruction;
- epic storytelling;
- restrained irony where appropriate;
- accessibility for non-specialists;
- transparent uncertainty.

Use strong editorial headings such as:

- “Architecture against the sky.”
- “The material mountain.”
- “The burden is in the fire.”
- “A finite slice of eternity.”

Avoid generic headings such as “Analysis”, “Data” or “Discussion” when a more meaningful episode-specific heading is possible.

Narrative language must support the analysis, never replace it.

---

## 18. Quality-assurance checklist before publication

A new episode is not complete merely because GitHub Pages reports a successful build.

Check all of the following.

### Content

- [ ] Main result matches the approved PDF.
- [ ] Functional unit / reporting slice matches the approved PDF.
- [ ] Hotspot percentage reconciles with the result.
- [ ] Sensitivities are correct and clearly labelled.
- [ ] Facts and assumptions are not conflated.
- [ ] Biogenic / outside-of-scopes / separate disclosures are handled correctly.
- [ ] No unsupported numerical detail has been invented.

### Inventory

- [ ] Standard inventory columns are present.
- [ ] Major flows reconcile with the approved episode.
- [ ] No double counting is introduced.
- [ ] Proxies and exclusions are disclosed.

### Graphics

- [ ] Inventory Map renders correctly.
- [ ] Technical Plate renders correctly.
- [ ] Hotspot Breakdown renders correctly.
- [ ] SVGs are self-contained vector files.
- [ ] Graphics use the correct episode values.
- [ ] Cover is readable and sufficiently high quality.

### Links and paths

- [ ] Homepage card opens the correct episode.
- [ ] Featured Latest Case opens the correct episode.
- [ ] Cover paths work from both homepage and episode page.
- [ ] PDF link works if present.
- [ ] Back-to-archive link works.

### Responsive behaviour

- [ ] Page is readable on mobile.
- [ ] Visual grid collapses correctly.
- [ ] Inventory table scrolls horizontally.
- [ ] No image exceeds its container.

### Deployment

- [ ] Changes are committed to `main`.
- [ ] GitHub Pages workflow completes with `success`.
- [ ] Pages build reports `built`.
- [ ] Live page is checked after deployment.
- [ ] At least the cover and all three editorial graphics are confirmed visible live.

A green build alone is not sufficient evidence that image paths or browser rendering are correct.

---

## 19. Controlled publishing workflow

For each new episode:

1. Read the approved episode PDF completely.
2. Extract title, episode number, series, FU, main result, hotspot, inventory, exclusions, sensitivities and verdict.
3. Identify or create the canonical cover.
4. Create native SVG Inventory Map.
5. Create native SVG Technical Plate.
6. Create native SVG Hotspot Breakdown.
7. Build the episode from `episodes/template.html`.
8. Add Quick Facts and model-note cards.
9. Reconcile the inventory table with the approved result.
10. Add sensitivities and verdict.
11. Upload the episode PDF when a download is intended.
12. Update `LATEST CASE` on the homepage.
13. Add the episode to the archive cards.
14. Commit the release in a controlled set of changes.
15. Verify all repository paths.
16. Wait for GitHub Pages deployment.
17. Inspect the live episode and all visual assets.
18. Only then consider publication complete.

Avoid experimental live-site edits when a staging or locally verified asset can be used first.

---

## 20. Future-episode reconstruction protocol

If a future session begins without prior conversation history, the minimum required inputs are:

- this repository;
- this README;
- the approved PDF of the new episode.

Optional but useful:

- original high-resolution cover image;
- calculation workbook;
- LinkedIn post / source list;
- latest DEFRA workbook if the episode itself still needs to be produced rather than merely published.

With the repository + README + approved PDF, the website episode should be reconstructable without asking the user to restate established design rules.

---

## 21. Relationship with the wider LCA of the Impossible production workflow

The website is the permanent archive. LinkedIn remains the publishing channel for the carousel, while the website exposes a more durable technical narrative.

The upstream episode-production workflow may include:

- historical / engineering research;
- functional-unit definition;
- system boundaries;
- inventory reconstruction;
- DEFRA and literature factors;
- Excel calculation model;
- 13-page LinkedIn carousel;
- LinkedIn post.

The website does not need to duplicate the full workbook, but it must preserve the episode’s core audit trail: **what was modelled, why, with which major flows, where the footprint lands, and what changes the result.**

---

## 22. Non-negotiable principles

1. **The approved PDF controls the numbers.**
2. **The README controls the web editorial system.**
3. **The website must remain technically auditable even when the storytelling is epic.**
4. **Every assumption must remain recognisable as an assumption.**
5. **Every new episode receives the three standard editorial graphics.**
6. **Graphics must be browser-safe and self-contained.**
7. **The newest episode is featured without removing the archive.**
8. **No broken image or PDF link is acceptable at publication.**
9. **A successful GitHub Pages build is necessary but not sufficient: the live page must be visually checked.**
10. **Where others see fantasy, we see a functional unit.**
