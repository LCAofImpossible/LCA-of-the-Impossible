# LCA of the Impossible — Website Editorial & Publishing Bible

Static GitHub Pages archive for the **LCA of the Impossible** series.

This README is the canonical editorial and publishing reference for building, updating and reviewing episode pages. Its purpose is to make the website reproducible in a future session with no prior conversational context. If a new approved episode PDF and this repository are available, the website episode must be rebuildable without relying on memory.

---

## 1. Source-of-truth hierarchy

Use this hierarchy whenever sources disagree:

1. **Approved episode PDF / approved LinkedIn carousel** — source of truth for episode-specific facts, numbers, assumptions, results, sensitivities, narrative conclusions, wording **and cover artwork**.
2. **An explicitly user-approved replacement image** — overrides the PDF cover only when the user has specifically selected it as the new cover.
3. **This README** — source of truth for website editorial structure, publishing rules, asset conventions and QA requirements.
4. **`assets/style.css`** — source of truth for the live visual system, palette, responsive behaviour and component styling.
5. **`episodes/template.html`** — canonical implementation starter for new episode pages.
6. Existing episode pages — examples of execution, not authorities over the approved PDF or this README.

Do not silently replace, reconcile or “improve” approved episode content. If a website adaptation requires simplification, preserve the underlying meaning and disclose the simplification.

**Cover artwork is part of the approved episode content. If page 1 of an approved PDF contains the final cover, that exact visual composition is mandatory for the website unless the user explicitly asks for a different cover.**

---

## 2. Canonical repository structure

- `index.html` — homepage, Latest Case and searchable/filterable episode archive
- `episodes/` — individual episode pages and reusable episode template
- `assets/style.css` — global visual system, including archive-grid and filter/search styling
- `assets/images/episodes/` — canonical episode covers
- `assets/images/episode-graphics/` — inventory, technical and hotspot graphics
- `assets/images/book/` — book artwork
- `assets/pdf/episodes/` — downloadable episode carousels

Do not create parallel folders for temporary fixes. Avoid duplicate `live`, `v2`, `final`, `new`, `hq2`, `final-final` or similar filenames in the canonical tree. Temporary staging assets must be removed before publication.

---

## 3. Episode asset convention

Each episode uses one canonical cover plus three standard editorial graphics:

- `epNN-short-slug.ext` — canonical cover
- `epNN-inventory-map.svg` — visual map of main life-cycle inputs
- `epNN-technical-plate.svg` — engineering / reconstruction plate
- `epNN-hotspot-breakdown.svg` — contribution / hotspot graphic
- `epNN-short-slug.pdf` — downloadable carousel when available

Current canonical covers include:

- `ep35-flying-dutchman.jpg`
- `ep36-tower-of-babel.png`
- `ep42-talos.jpg`
- `ep43-sisyphus.webp`

### Canonical-cover lock

When an approved PDF or approved LinkedIn carousel exists, **extract or rasterize the exact approved cover and use it as the canonical website cover**. Do not redraw, regenerate, vectorize, reinterpret, restyle, clean up, crop away meaningful content, or substitute the cover because another version appears more cinematic, technical, consistent or visually polished.

The only permitted reasons to use a different visual are:

1. the user explicitly requests a replacement; or
2. no approved cover exists.

If extraction quality is poor, improve the **export/rasterization of the same approved cover**, not the design. Use the source format or a high-quality raster derivative that preserves the exact composition.

---

## 4. Mandatory editorial structure of every episode page

Every episode should follow this sequence unless the subject genuinely requires a justified deviation.

### 4.1 Cover hero

Must contain:

- canonical approved cover;
- `EPISODE #NN · SERIES` eyebrow;
- episode title;
- one central narrative question;
- main result as the dominant metric;
- short explanation of the functional unit / reporting basis.

The hero should communicate the problem in seconds. Do not overload it with methodology.

### 4.2 The Subject

A short editorial framing section containing:

- one strong subheading;
- concise reconstruction of the subject;
- real analogue, evidence or engineering logic used;
- explicit distinction between narrative source and modelling assumption when relevant.

Tone: technical, confident, cinematic. It must not read like a generic LCA report introduction.

### 4.3 Four Quick Facts

Use four compact cards covering different dimensions by default:

1. geometry / scale;
2. operation / function;
3. main hotspot / result logic;
4. modelling convention / uncertainty.

Do not repeat the same fact four ways.

### 4.4 Visual Model

Always include before the detailed inventory:

- **Inventory Map**;
- **Technical Plate**.

These are compact analytical representations of the reconstructed system, not decorative illustrations.

### 4.5 Detailed Life Cycle Inventory

Use the standard columns:

`Stage | Component / activity | Activity data | Climate change | Modelling basis`

The table must reconcile with the approved episode and remain horizontally scrollable on mobile. After it, add model-note cards where useful, typically Included, Excluded / separate disclosure, Emission-factor logic, Supernatural rule, Main proxy / limitation.

### 4.6 Hotspot section

Always include the **Hotspot Breakdown** after the inventory and before result cards. The text must answer: **where does the footprint actually land, and why?**

### 4.7 Results

Use result cards only for decision-relevant outputs: principal stage/material contribution, operation/maintenance contribution, main hotspot percentage, separate biogenic disclosure, DEFRA share where relevant, and useful per-cycle/per-year/per-unit values.

### 4.8 Sensitivities and interpretation

Include sensitivities reported in the approved PDF and label them clearly as sensitivities. Typical cases: lifetime, energy/material factor, mass/geometry, efficiency, recovery rate and alternative modelling convention.

### 4.9 Verdict

End with 3–5 short memorable lines or one compact statement that links the result to the nature of the subject. It must remain technically anchored in the actual hotspot.

---

## 5. Functional unit and reporting basis

Reproduce the functional unit or reporting slice used in the approved episode. It must be quantified, understandable without the PDF, specific enough to explain the result, and include duration/service quantity when relevant. State construction allocation when material to interpretation.

For infinite, cyclic or unbounded subjects, use the finite reporting slice defined in the approved episode. Never present infinity itself as a calculable functional unit.

---

## 6. Numerical integrity rules

Website values must reconcile with the approved episode.

- Main result must match.
- Hotspot percentages must reconcile with the total.
- Phase/material contributions must not introduce double counting.
- Use no more precision than the inventory justifies.
- Do not invent missing percentages for visual balance.
- Sensitivities are not alternative main results.
- If explanatory sub-shares sum to a parent already counted, state that and do not add them again.

Keep separate where applicable: biogenic CO₂, outside-of-scopes values, avoided-production credits and other quantities excluded from headline GWP.

---

## 7. Inventory and modelling rules

Show enough information for a technically literate reader to understand the model. Preserve, when available: stage, component/process, quantity, unit, climate-change contribution and modelling basis/proxy/assumption.

The website need not reproduce every workbook row, but it must retain the principal audit trail. Analogues must be named. Engineering assumptions must remain recognisable as assumptions rather than historical or canonical facts.

---

## 8. Supernatural and fictional elements

Apply the project rule consistently:

**Magic is not a fuel.**

Assign emissions to supernatural elements only when they can be translated into a defensible physical flow. A curse that only changes behaviour has no emission flow by itself; repeated resurrection without defined material/energy is excluded and explained; a physical energy consequence may be modelled when the approved episode does so.

---

## 9. Emission-factor and DEFRA handling

Where UK Government GHG Conversion Factors are used, preserve the distinction between direct emissions, WTT, T&D where applicable, outside of scopes and biogenic reporting. Include DEFRA share where editorially useful.

Do not imply greater representativeness than the approved episode. Retain terms such as “accounting proxy”, “screening proxy” or “weak representativeness” where material.

---

## 10. Editorial graphic system

Every episode uses three graphics in the same design family.

### 10.1 Inventory Map

Show the main material / energy / operation blocks, logical flow, functional-unit context where useful and only the most important inventory categories. It is not a decorative mood board.

### 10.2 Technical Plate

Communicate the physical reconstruction: geometry, dimensions, mass, route, capacity, key engineering parameters and schematic/sectional representation. It should look like an editorial engineering plate, not a corporate infographic.

### 10.3 Hotspot Breakdown

Use real episode values, make the dominant contributor immediately visible, group minor contributors only when appropriate, and never invent precise percentages for visual balance.

### 10.4 Technical requirement

Use **native self-contained SVG** for editorial graphics wherever practical. Do not embed raster images inside SVG wrappers for the three analytical graphics. SVGs should contain their own paths, shapes, text and vector geometry.

This SVG rule applies to analytical graphics, **not to canonical episode covers**. Approved covers may and often should remain raster images when that is the faithful way to preserve the source artwork.

---

## 11. Visual language

The live visual system is defined by `assets/style.css`.

Core palette:

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

Direction: dark technical / blueprint atmosphere, restrained palette, fine linework, minimal dashboard styling, serious engineering tone with an epic editorial layer. Avoid generic Excel charts, rainbow palettes, stock-dashboard visuals, purposeless icons, cartoon styling and excessive gradients/glow.

Episode-specific cover colours do not need to be recoloured to match the website. **Approved cover artwork takes precedence over global palette consistency.**

---

## 12. Cover rules — mandatory

The cover is an approved editorial asset, not a placeholder and not an invitation to redesign.

### Source rule

1. If page 1 of the approved episode PDF / approved carousel contains the final cover, **use that exact cover**.
2. If the user explicitly supplies and approves a replacement cover, use that exact replacement.
3. Only when no approved cover exists may a new cover be created.

### Prohibited substitutions when an approved cover exists

Do **not**:

- generate a new cinematic alternative;
- redraw the subject;
- vectorize or stylize the cover into a new design;
- “improve” composition, typography, palette or subject appearance;
- replace it for consistency with another episode;
- use a schematic placeholder when the PDF cover is available.

A different file format or resolution is acceptable only if the rendered visual remains faithful to the approved cover.

### Mandatory cover verification

Before committing a new episode, visually compare the canonical website cover with page 1 of the approved PDF or with the explicitly approved replacement image. **Any visual mismatch is a publication blocker.**

If a cover mismatch is reported, correct the asset first, then update references if required, then repeat the visual comparison.

---

## 13. Homepage and episode-library rules

The homepage is a scalable editorial archive, not a chronological stack of full-width episode blocks. Its canonical sequence is:

1. main image-free project hero;
2. compact project-format strip;
3. **Latest Analysis / Latest Case** feature;
4. **Episode Library** archive grid;
5. Method, process, Series and Book sections.

### 13.1 Latest Case

The newest published episode becomes `LATEST CASE` unless explicitly decided otherwise. The feature includes the canonical cover, title, concise reconstruction description, episode number, headline result, hotspot/theme badges and direct episode link.

The Latest Case is a feature, not a substitute for the archive card: **the newest episode must also remain in the Episode Library**.

### 13.2 Episode Library grid

Every published website episode must appear in the archive, ordered **newest to oldest**.

The standard responsive grid is:

- **3 cards per row on desktop**;
- **2 cards per row on tablet / medium viewport**;
- **1 card per row on mobile**.

Each card contains:

- square CSS crop of the canonical cover;
- one concise primary category label;
- episode title;
- episode number;
- headline result;
- one short hotspot / inventory cue;
- `Explore the LCA →` interaction cue.

Square card cropping may use CSS `object-fit`, but must not alter the canonical cover asset itself. The Latest Case cover should be displayed without destructive cropping.

### 13.3 Search and filters

The Episode Library includes a lightweight client-side search and thematic filters. Search must work against at least title, episode number, category and meaningful subject keywords.

Archive cards therefore use:

- `data-category="..."` for one or more normalized category tokens;
- `data-search="..."` for meaningful search terms not necessarily visible in the card.

Current taxonomy may include categories such as `mythology`, `legends`, `structures`, `science-fiction`, `fantasy` or other clearly justified themes. A subject may belong to more than one filter category. **Only expose filter buttons that are useful for the currently published archive; do not create empty categories merely for future use.**

The selected filter must remain visually obvious and must expose `aria-pressed` state. A zero-result search must produce a readable empty-state message rather than an apparently broken blank grid.

### 13.4 Archive pagination / Load More

The archive initially exposes up to **9 matching episodes**. When more than 9 cards match the active filter/search, show `Load more episodes ↓` and reveal the next batch of 9 on activation.

When 9 or fewer results exist, the Load More control remains hidden. Filtering or changing the search resets the visible batch to the first 9 matching episodes.

This is a display rule only: every published card remains present in the HTML so search, accessibility and future maintenance do not depend on remote pagination.

### 13.5 Adding a future episode to the homepage

For every new episode:

1. update the Latest Case feature if it is the newest release;
2. add the new archive card at the beginning of the grid;
3. assign appropriate `data-category` token(s);
4. add useful `data-search` terms;
5. preserve all older cards;
6. add a new filter button only if the category is materially useful and represented in the archive;
7. verify filtering, search, archive count and Load More behaviour after insertion.

The homepage archive interaction currently lives directly in `index.html`; do not introduce a framework or build dependency unless explicitly required. The page must remain a simple static GitHub Pages site.

---

## 14. PDF handling

When the approved episode PDF is intended for download, store it in `assets/pdf/episodes/` with a canonical filename such as `epNN-short-slug.pdf` and add an `Open episode PDF →` button. Do not create broken links when the PDF is not in the repository.

---

## 15. Page path convention

From `index.html` use `assets/images/...` and `episodes/slug.html`.

From files inside `episodes/` use `../assets/images/...`, `../assets/pdf/...` and `../index.html#episodes`.

Avoid root-relative `/...` paths because this is a GitHub Pages project site.

---

## 16. Responsive and accessibility rules

- Inventory tables scroll horizontally on mobile.
- Visual grids and episode-page cards collapse to one column where appropriate.
- Homepage Episode Library uses the canonical 3-column desktop / 2-column tablet / 1-column mobile layout.
- Archive filter controls wrap cleanly on narrow screens; search becomes full width on mobile.
- Selected archive filters expose `aria-pressed` state.
- Archive search has an accessible label even when the visible interface relies on placeholder text.
- Images use meaningful `alt` text.
- Editorial graphics use `loading="lazy"` and `decoding="async"` where appropriate.
- Archive-card cover images should use lazy loading where practical; the featured Latest Case may load normally.
- Headings must remain legible without horizontal scrolling.
- Essential information must not exist only inside images.
- No image may exceed its container.

---

## 17. Editorial tone

Combine technical credibility, engineering reconstruction, epic storytelling, restrained irony, accessibility and transparent uncertainty. Use meaningful episode-specific headings rather than generic “Analysis”, “Data” or “Discussion”. Narrative language supports the analysis; it never replaces it.

---

## 18. Quality-assurance checklist before publication

A new episode is not complete merely because GitHub Pages reports a successful build.

### Content

- [ ] Main result matches the approved PDF.
- [ ] Functional unit / reporting slice matches.
- [ ] Hotspot percentage reconciles.
- [ ] Sensitivities are correct and clearly labelled.
- [ ] Facts and assumptions are not conflated.
- [ ] Separate disclosures are handled correctly.
- [ ] No unsupported numerical detail has been invented.

### Cover — publication blocker

- [ ] Canonical cover visually matches page 1 of the approved PDF / approved carousel, or the exact explicitly user-approved replacement.
- [ ] No AI-generated, redrawn, vectorized, restyled or otherwise reinterpreted substitute has replaced an approved cover.
- [ ] Cover text, composition, subject, background and meaningful visual elements match the approved source.
- [ ] Any resizing/compression preserves the approved composition.

### Inventory

- [ ] Standard inventory columns are present.
- [ ] Major flows reconcile with the approved episode.
- [ ] No double counting is introduced.
- [ ] Proxies and exclusions are disclosed.

### Graphics

- [ ] Inventory Map renders correctly.
- [ ] Technical Plate renders correctly.
- [ ] Hotspot Breakdown renders correctly.
- [ ] Analytical SVGs are self-contained vector files.
- [ ] Graphics use correct episode values.

### Links and homepage archive

- [ ] Homepage archive card opens the correct episode.
- [ ] Featured Latest Case opens the correct episode.
- [ ] Newest episode appears both as Latest Case and as the first archive card.
- [ ] Archive cards remain ordered newest to oldest.
- [ ] `data-category` and `data-search` metadata are present and meaningful.
- [ ] All visible thematic filters return the intended episodes.
- [ ] Search works by title and episode number and returns a readable zero-result state.
- [ ] Archive result count updates correctly.
- [ ] Load More appears only when more than 9 matching episodes exist and reveals the next batch correctly.
- [ ] Cover paths work from homepage and episode page.
- [ ] PDF link works if present.
- [ ] Back-to-archive link works.

### Responsive behaviour

- [ ] Page is readable on mobile.
- [ ] Episode Library is 3 columns on desktop, 2 on medium viewports and 1 on mobile.
- [ ] Filter controls wrap correctly and archive search becomes usable at narrow width.
- [ ] Visual grid collapses correctly.
- [ ] Inventory table scrolls horizontally.
- [ ] No image exceeds its container.

### Deployment

- [ ] Changes are committed to `main`.
- [ ] GitHub Pages build reports `built` / workflow success.
- [ ] Live homepage archive is inspected after deployment.
- [ ] Live episode is inspected after deployment.
- [ ] Canonical cover and all three editorial graphics are confirmed visible live.

A green build alone is not sufficient evidence that the page is correct.

---

## 19. Controlled publishing workflow

For each new episode:

1. Read the approved episode PDF completely.
2. Extract title, number, series, FU, main result, hotspot, inventory, exclusions, sensitivities and verdict.
3. **Extract/rasterize page 1 as the canonical cover, or use the exact explicitly user-approved replacement. Create a new cover only if no approved cover exists.**
4. Visually compare the extracted cover with the approved source before proceeding.
5. Create native SVG Inventory Map.
6. Create native SVG Technical Plate.
7. Create native SVG Hotspot Breakdown.
8. Build the episode from `episodes/template.html`.
9. Add Quick Facts and model-note cards.
10. Reconcile the inventory table with the approved result.
11. Add sensitivities and verdict.
12. Upload the episode PDF when download is intended.
13. Update `LATEST CASE` where applicable.
14. Add the new episode as the first archive card without removing older episodes.
15. Add/verify `data-category` and `data-search` metadata and expose a new filter only when useful.
16. Verify archive ordering, filter/search behaviour, result count and Load More logic.
17. Commit the release in a controlled set of changes.
18. Verify paths and remove all staging/temporary assets.
19. Wait for GitHub Pages deployment.
20. Inspect the live homepage archive, episode, cover and all three analytical graphics.
21. Only then consider publication complete.

---

## 20. Future-episode reconstruction protocol

Minimum required inputs:

- this repository;
- this README;
- approved PDF of the new episode.

Optional: original high-resolution cover image, calculation workbook, LinkedIn post/source list and latest DEFRA workbook if the episode itself still needs to be produced.

With repository + README + approved PDF, the website episode must be reconstructable without asking the user to restate established design rules. **The default is to preserve the PDF cover exactly, not to create a new one.**

---

## 21. Relationship with the wider production workflow

LinkedIn remains the publishing channel; the website is the permanent technical archive. Upstream work may include historical/engineering research, FU definition, boundaries, inventory, factors, Excel model, 13-page carousel and LinkedIn post.

The website does not need to duplicate the full workbook but must preserve the core audit trail: **what was modelled, why, with which major flows, where the footprint lands, and what changes the result.**

---

## 22. Non-negotiable principles

1. **The approved PDF controls episode-specific facts, numbers, wording and cover artwork.**
2. **If an approved cover exists, that exact cover is the website cover unless the user explicitly requests a replacement.**
3. **A perceived opportunity to improve, harmonize or restyle a cover is not permission to replace it.**
4. **The README controls the web editorial system.**
5. **The website must remain technically auditable even when the storytelling is epic.**
6. **Every assumption must remain recognisable as an assumption.**
7. **Every new episode receives the three standard analytical graphics.**
8. **Analytical graphics must be browser-safe and self-contained.**
9. **The newest episode is featured and also retained as the first card of the complete archive.**
10. **The homepage archive must remain scalable: newest-first grid, working search/filter metadata and Load More behaviour when required.**
11. **Older published episodes are never removed merely to reduce homepage length.**
12. **No broken image or PDF link is acceptable at publication.**
13. **A successful GitHub Pages build is necessary but not sufficient: the live homepage, episode and canonical cover must be visually checked.**
14. **Where others see fantasy, we see a functional unit.**
