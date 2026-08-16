# LCA of the Impossible — Website Editorial & Publishing Bible

Static GitHub Pages archive for the **LCA of the Impossible** series.

This README is the canonical editorial and publishing reference for building, updating and reviewing the website. Its purpose is to make the site reproducible in a future session with no prior conversational context. If a new approved episode PDF and this repository are available, the website episode and its catalogue metadata must be rebuildable without relying on memory.

---

## 1. Source-of-truth hierarchy

Use this hierarchy whenever sources disagree:

1. **Approved episode PDF / approved LinkedIn carousel** — source of truth for episode-specific facts, numbers, assumptions, results, sensitivities, narrative conclusions, wording and approved cover artwork.
2. **An explicitly user-approved replacement image** — overrides the PDF cover only when the user has specifically selected it as the catalogue cover.
3. **This README** — source of truth for website editorial structure, publishing rules, taxonomy, asset conventions and QA requirements.
4. **`episodes.json`** — canonical website catalogue registry for published episode metadata, ordering, search/filter taxonomy, related cases and navigation relationships. Its values must reconcile with the approved episode source.
5. **`assets/style.css`** — source of truth for the live visual system, palette, responsive behaviour and component styling.
6. **`assets/site.js`** — source of truth for registry-driven homepage/archive rendering, text-only episode hero normalisation, Related Cases and Previous/Next behaviour.
7. **`episodes/template.html`** — canonical implementation starter for new episode pages.
8. Existing episode pages — examples of execution, not authorities over the approved PDF or this README.

Do not silently replace, reconcile or “improve” approved episode content. If a website adaptation requires simplification, preserve the underlying meaning and disclose the simplification.

**Important structural rule:** approved cover artwork remains part of the episode package, but the website displays episode covers **only on the homepage and in the full Archive catalogue**. Individual episode pages are deliberately image-free at hero level.

If `episodes.json` conflicts with an approved PDF, correct the registry; do not change the approved episode fact to fit the registry.

---

## 2. Canonical repository structure

- `index.html` — concise homepage with project hero, Latest Case, recent episodes, Method, Series and Book
- `archive.html` — complete searchable/filterable episode catalogue
- `episodes.json` — central episode registry and navigation metadata
- `episodes/` — individual episode pages and reusable episode template
- `assets/site.js` — shared client-side catalogue, archive, text-only episode hero, related-case and Previous/Next logic
- `assets/style.css` — global visual system, including archive and navigation styling
- `assets/images/episodes/` — canonical **catalogue covers** used only by homepage and Archive
- `assets/images/episode-graphics/` — inventory, technical and hotspot graphics used inside episode pages
- `assets/images/book/` — book artwork
- `assets/pdf/episodes/` — downloadable episode carousels

Do not create parallel folders for temporary fixes. Avoid duplicate `live`, `v2`, `final`, `new`, `hq2`, `final-final` or similar filenames in the canonical tree. Temporary staging assets must be removed before publication.

The website must remain a simple static GitHub Pages site. Do not introduce a framework, package manager or build dependency unless explicitly required.

---

## 3. Central episode registry — mandatory

`episodes.json` is the single catalogue record used by the homepage, full archive and episode-to-episode navigation.

Every published episode must have one registry object containing at least:

- `number` — numerical episode identifier;
- `slug` — stable filename slug;
- `title` — displayed episode title;
- `url` — relative episode-page path from the repository root;
- `cover` — relative canonical catalogue-cover path from the repository root;
- `categoryLabel` — concise human-readable narrative category;
- `categories` — normalized filter tokens;
- `lcaLabel` — principal LCA characteristic shown on cards;
- `lcaCharacteristics` — normalized LCA filter tokens;
- `result` — approved headline result;
- `hotspot` — one concise approved/reconciled hotspot statement;
- `featuredDescription` — short description used when the episode is featured;
- `keywords` — meaningful search terms not already obvious from the title;
- `related` — ordered list of related episode numbers.

The `cover` field remains mandatory even though individual episode pages do not show a cover. It is consumed by the homepage and Archive only.

### 3.1 Ordering

The registry may be stored in newest-first order, but `assets/site.js` also sorts episodes by descending episode number. **Episode number is the canonical website ordering key unless the user explicitly defines a different release order.**

The highest published episode number becomes the Latest Case automatically.

### 3.2 Subject-category taxonomy

Subject categories answer **what kind of impossible subject is this?** Typical tokens include:

- `mythology`
- `legends`
- `structures`
- `science-fiction`
- `fantasy`

A subject may belong to more than one category when materially useful. Do not add empty speculative categories merely because they may be used later.

### 3.3 LCA-characteristic taxonomy

LCA characteristics answer **what life-cycle mechanism controls or meaningfully shapes this case?** Typical tokens include:

- `materials-driven`
- `operation-driven`
- `energy-driven`
- `mobility-driven`
- `process-energy-driven`
- `repetition-sensitive`
- `lifetime-sensitive`
- `proxy-sensitive`

The `lcaLabel` is the principal card label; `lcaCharacteristics` may contain multiple analytical descriptors.

Do not classify an episode for aesthetic symmetry. The classification must be defensible from the actual result or sensitivity analysis.

### 3.4 Related cases

`related` is editorially controlled, not algorithmically inferred. Choose up to three cases connected by subject, system behaviour, modelling issue or hotspot. Prefer meaningful analytical relationships over superficial visual similarity.

On individual episode pages, Related Cases are rendered as **text-only cards**. Cover images are intentionally not shown there.

---

## 4. Episode asset convention

Each episode uses one canonical catalogue cover plus three standard editorial graphics:

- `epNN-short-slug.ext` — canonical catalogue cover, used only on homepage and Archive
- `epNN-inventory-map.svg` — visual map of main life-cycle inputs
- `epNN-technical-plate.svg` — engineering / reconstruction plate
- `epNN-hotspot-breakdown.svg` — contribution / hotspot graphic
- `epNN-short-slug.pdf` — downloadable carousel when available

Current canonical catalogue covers include:

- `ep35-flying-dutchman.jpg`
- `ep36-tower-of-babel.png`
- `ep40-minotaur.jpg`
- `ep41-mjolnir.jpg`
- `ep42-talos.jpg`
- `ep43-sisyphus.webp`

### 4.1 Canonical-cover lock

When an approved PDF or approved LinkedIn carousel exists, **extract or rasterize the exact approved cover and use it as the canonical catalogue cover**. Do not redraw, regenerate, vectorize, reinterpret, restyle, clean up, crop away meaningful content or substitute the cover because another version appears more cinematic, technical, consistent or visually polished.

The only permitted reasons to use a different visual are:

1. the user explicitly requests a replacement; or
2. no approved cover exists.

If extraction quality is poor, improve the export/rasterization of the same approved cover, not the design.

### 4.2 Where covers are allowed

Covers may appear only in:

- Homepage **Latest Case**;
- Homepage **Recent Cases**;
- Full **Archive** episode cards.

Covers must **not** appear in:

- the hero of an individual episode page;
- the Life Cycle Inventory section;
- Related Cases inside an episode;
- Previous/Next navigation;
- analytical graphics as decorative backgrounds.

This rule deliberately reduces image-loading dependencies inside technical episode pages.

---

## 5. Mandatory editorial structure of every episode page

Every episode should follow this sequence unless the subject genuinely requires a justified deviation.

### 5.1 Text-only episode hero

The individual episode page begins with a **text-only hero**. It must contain:

- `EPISODE #NN · SERIES` eyebrow;
- title;
- one central narrative question;
- main result as the dominant metric;
- concise functional-unit / reporting-basis description.

**Do not include a cover `<img>`, `.cover-frame`, catalogue artwork or decorative hero image.**

For legacy pages that still contain old cover markup, `assets/site.js` removes `.cover-frame` at runtime and normalises the hero to one column. New pages must not rely on this compatibility safeguard; they must be authored without the cover markup from the start.

### 5.2 The Subject

A concise reconstruction of the subject, real analogue / evidence / engineering logic and explicit distinction between narrative source and modelling assumption where relevant.

Tone: technical, confident, cinematic. It must not read like a generic LCA report introduction.

### 5.3 Four Quick Facts

Use four compact cards covering different dimensions by default: geometry/scale, operation/function, main hotspot/result logic and modelling convention/uncertainty.

### 5.4 Visual Model

Always include before the detailed inventory:

- **Inventory Map**;
- **Technical Plate**.

These are analytical representations, not decorative illustrations.

### 5.5 Detailed Life Cycle Inventory

Use the standard columns:

`Stage | Component / activity | Activity data | Climate change | Modelling basis`

The table must reconcile with the approved episode and remain horizontally scrollable on mobile. Add model-note cards where useful: Included, Excluded/separate disclosure, Emission-factor logic, Supernatural rule and Main proxy/limitation.

### 5.6 Hotspot section

Always include the **Hotspot Breakdown** after the inventory and before result cards. The text must answer: **where does the footprint actually land, and why?**

### 5.7 Results

Use result cards only for decision-relevant outputs: principal stage/material contribution, operation/maintenance contribution, hotspot percentage, separate disclosures, DEFRA share where relevant and useful per-cycle/per-year/per-unit values.

### 5.8 Sensitivities and interpretation

Include sensitivities reported in the approved PDF and label them clearly as sensitivities.

### 5.9 Verdict

End with 3–5 short memorable lines or one compact statement that links the result to the nature of the subject. It must remain technically anchored in the actual hotspot.

### 5.10 Automatic episode navigation

Every published episode page must include `data-episode="NN"` on the `<body>` and load `../assets/site.js`.

The shared script automatically adds:

- sticky internal navigation: `Subject · Model · Inventory · Hotspots · Results · Verdict`;
- section anchors where required;
- **text-only Related Cases** after the Verdict;
- bottom **Previous episode / Full archive / Next episode** navigation;
- compatibility removal of legacy episode-cover markup.

Do not hard-code these navigation blocks inside individual episode pages unless the shared system is intentionally being replaced. Previous/Next relationships derive from registry ordering; Related Cases derive from the registry `related` field.

---

## 6. Functional unit and reporting basis

Reproduce the functional unit or reporting slice used in the approved episode. It must be quantified, understandable without the PDF, specific enough to explain the result, and include duration/service quantity when relevant. State construction allocation when material to interpretation.

For infinite, cyclic or unbounded subjects, use the finite reporting slice defined in the approved episode. Never present infinity itself as a calculable functional unit.

---

## 7. Numerical integrity rules

Website values and registry values must reconcile with the approved episode.

- Main result must match.
- Hotspot percentages must reconcile with the total.
- Phase/material contributions must not introduce double counting.
- Use no more precision than the inventory justifies.
- Do not invent missing percentages for visual balance.
- Sensitivities are not alternative main results.
- If explanatory sub-shares sum to a parent already counted, state that and do not add them again.

Keep separate where applicable: biogenic CO₂, outside-of-scopes values, avoided-production credits and other quantities excluded from headline GWP.

---

## 8. Inventory and modelling rules

Show enough information for a technically literate reader to understand the model. Preserve, when available: stage, component/process, quantity, unit, climate-change contribution and modelling basis/proxy/assumption.

The website need not reproduce every workbook row, but it must retain the principal audit trail. Analogues must be named. Engineering assumptions must remain recognisable as assumptions rather than historical or canonical facts.

---

## 9. Supernatural and fictional elements

Apply the project rule consistently:

**Magic is not a fuel.**

Assign emissions to supernatural elements only when they can be translated into a defensible physical flow. A curse that only changes behaviour has no emission flow by itself; repeated resurrection without defined material/energy is excluded and explained; a physical energy consequence may be modelled when the approved episode does so.

---

## 10. Emission-factor and DEFRA handling

Where UK Government GHG Conversion Factors are used, preserve the distinction between direct emissions, WTT, T&D where applicable, outside of scopes and biogenic reporting. Include DEFRA share where editorially useful.

Do not imply greater representativeness than the approved episode. Retain terms such as “accounting proxy”, “screening proxy” or “weak representativeness” where material.

---

## 11. Editorial graphic system

Every episode uses three graphics in the same design family.

### 11.1 Inventory Map

Show the main material/energy/operation blocks, logical flow, functional-unit context where useful and only the most important inventory categories.

### 11.2 Technical Plate

Communicate the physical reconstruction: geometry, dimensions, mass, route, capacity, key engineering parameters and schematic/sectional representation. It must be a legible engineering diagram, not decorative linework or a visually tangled abstraction.

### 11.3 Hotspot Breakdown

Use real episode values, make the dominant contributor immediately visible, group minor contributors only when appropriate, and never invent precise percentages for visual balance.

### 11.4 Technical requirement

Use **native self-contained SVG** for analytical graphics wherever practical. Do not embed raster images inside SVG wrappers for the three analytical graphics.

This SVG rule applies to analytical graphics, not to catalogue covers.

---

## 12. Visual language

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

Episode-specific cover colours do not need to be recoloured to match the website. Approved cover artwork takes precedence over global palette consistency on homepage/archive catalogue cards.

---

## 13. Catalogue-cover rules — mandatory

The cover is an approved **catalogue asset**, not an episode-page hero.

### Source rule

1. If page 1 of the approved episode PDF/carousel contains the final cover, use that exact cover for homepage/archive.
2. If the user explicitly supplies and approves a replacement cover, use that exact replacement.
3. Only when no approved cover exists may a new cover be created.

### Prohibited substitutions when an approved cover exists

Do not generate a new cinematic alternative, redraw the subject, vectorize or stylize the cover into a new design, “improve” composition/typography/palette, replace it for consistency with another episode, or use a schematic placeholder when the PDF cover is available.

### Mandatory cover verification

Before committing a new episode, visually compare the canonical catalogue cover with page 1 of the approved PDF or with the explicitly approved replacement image. Any visual mismatch is a publication blocker for homepage/archive.

**The cover is never required to render on the individual episode page because individual episode pages intentionally do not display covers.**

---

## 14. Homepage architecture

The homepage is an editorial entry point, not the full database.

Canonical sequence:

1. image-free project hero;
2. compact project-format strip;
3. **Latest Analysis / Latest Case**;
4. **Recent Cases** selection;
5. Method and process;
6. Series framing;
7. Book section.

### 14.1 Latest Case

`assets/site.js` reads `episodes.json`, sorts by episode number and automatically renders the newest episode as Latest Case. Do not manually duplicate the latest episode content in `index.html`.

The feature includes catalogue cover, title, featured description, episode number, result, principal LCA label, subject category and direct link.

### 14.2 Recent Cases

The homepage displays up to six episodes after the Latest Case. Each card may show the canonical catalogue cover. The complete catalogue lives on `archive.html`.

Do not reintroduce the entire archive into the homepage merely because the number of episodes grows.

---

## 15. Full archive architecture

`archive.html` is the canonical complete catalogue. Every published registry entry appears there, newest first.

### 15.1 Card design

Standard grid:

- **3 cards per row on desktop**;
- **2 cards per row on tablet / medium viewport**;
- **1 card per row on mobile**.

Each card contains square CSS crop of the canonical catalogue cover, `Category · LCA lens`, title, episode number, result, concise hotspot cue and `Explore the LCA →`.

Square cropping may use CSS `object-fit`, but must not alter the canonical cover asset itself.

### 15.2 Subject and LCA filters

The archive exposes two independent filter groups generated automatically from registry tokens:

- **Subject** — narrative category;
- **LCA lens** — life-cycle characteristic.

The two groups combine using AND logic. Only categories/characteristics actually present in `episodes.json` should appear. Do not maintain filter buttons manually.

### 15.3 Search

Search operates against title, episode number, human-readable labels, category tokens, LCA-characteristic tokens and registry keywords. A zero-result search must show a readable empty state.

### 15.4 Load More

The archive initially exposes up to **9 matching episodes**. When more than 9 match, show `Load more episodes ↓` and reveal the next batch of 9. Changing a filter or search resets the visible batch to 9.

All catalogue data remain local in `episodes.json`; this is display pagination only.

---

## 16. PDF, paths, responsive and accessibility rules

When the approved episode PDF is intended for download, store it in `assets/pdf/episodes/` with a canonical filename such as `epNN-short-slug.pdf` and add an `Open episode PDF →` button. Do not create broken links when the PDF is absent.

From root files such as `index.html` and `archive.html`, use `assets/...` and `episodes/slug.html`. From files inside `episodes/`, use `../assets/...`, `../archive.html` and `../index.html`. Avoid root-relative `/...` paths because this is a GitHub Pages project site.

Responsive/accessibility requirements:

- Inventory tables scroll horizontally on mobile.
- Visual grids and episode cards collapse appropriately.
- Archive grid is 3/2/1 columns desktop/tablet/mobile.
- Archive filters wrap cleanly; search becomes full width on mobile.
- Selected archive filters expose `aria-pressed` state.
- Archive search has an accessible label.
- Episode jump navigation is horizontally scrollable on narrow screens.
- Previous/Next navigation collapses to a vertical sequence on mobile.
- Analytical images use meaningful `alt` text.
- Editorial graphics use `loading="lazy"` and `decoding="async"` where appropriate.
- Archive-card covers use lazy loading; Latest Case may load normally.
- Headings must remain legible without horizontal scrolling.
- Essential information must not exist only inside images.
- No image may exceed its container.
- Individual episode pages must remain fully usable even if catalogue-cover assets are unavailable.

---

## 17. Editorial tone

Combine technical credibility, engineering reconstruction, epic storytelling, restrained irony, accessibility and transparent uncertainty. Use meaningful episode-specific headings rather than generic “Analysis”, “Data” or “Discussion”. Narrative language supports the analysis; it never replaces it.

---

## 18. Quality-assurance checklist before publication

A new episode is not complete merely because GitHub Pages reports a successful build.

### Content

- [ ] Main result matches the approved PDF.
- [ ] Functional unit/reporting slice matches.
- [ ] Hotspot percentage reconciles.
- [ ] Sensitivities are correct and clearly labelled.
- [ ] Facts and assumptions are not conflated.
- [ ] Separate disclosures are handled correctly.
- [ ] No unsupported numerical detail has been invented.

### Catalogue cover — homepage/archive only

- [ ] Canonical catalogue cover visually matches page 1 of the approved PDF/carousel or exact approved replacement.
- [ ] No redrawn, regenerated, vectorized or restyled substitute has replaced an approved cover.
- [ ] Resizing/compression preserves the approved composition.
- [ ] Cover renders in Homepage Latest/Recent as applicable.
- [ ] Cover renders in Archive.

### Registry

- [ ] New episode has exactly one `episodes.json` entry.
- [ ] Episode number, title, URL, cover, result and hotspot reconcile with the approved episode.
- [ ] Subject category is meaningful.
- [ ] Principal LCA label and LCA-characteristic tokens are analytically defensible.
- [ ] Search keywords are useful and not spam-like.
- [ ] Related episode numbers exist and are intentionally chosen.
- [ ] No stale duplicate registry entry remains.

### Episode page

- [ ] `<body data-episode="NN">` matches registry number.
- [ ] `../assets/site.js` is loaded.
- [ ] Hero is text-only: eyebrow, title, question, result and FU/reporting basis.
- [ ] No cover image is visible or required on the episode page.
- [ ] Sticky internal navigation appears and links to Subject, Model, Inventory, Hotspots, Results and Verdict.
- [ ] Related Cases render after the Verdict as text-only cards.
- [ ] Previous/Next order is correct.
- [ ] Full Archive link works.

### Inventory and graphics

- [ ] Standard inventory columns are present.
- [ ] Major flows reconcile with the approved episode.
- [ ] No double counting is introduced.
- [ ] Proxies and exclusions are disclosed.
- [ ] Inventory Map, Technical Plate and Hotspot Breakdown render correctly.
- [ ] Analytical SVGs are self-contained vector files.
- [ ] Technical Plate is visually legible and schematic, not a tangle of decorative lines.

### Homepage and archive

- [ ] Homepage Latest Case is the highest published episode number.
- [ ] Recent Cases render from the registry.
- [ ] `archive.html` contains every published episode.
- [ ] Archive ordering is newest first.
- [ ] Subject filters return intended episodes.
- [ ] LCA-lens filters return intended episodes.
- [ ] Combined filters use AND logic correctly.
- [ ] Search works by title and episode number and has a zero-result state.
- [ ] Archive result count updates correctly.
- [ ] Load More appears only when more than 9 matches exist.

### Deployment

- [ ] Changes are committed to `main`.
- [ ] GitHub Pages deploys the latest commit.
- [ ] Live homepage is inspected.
- [ ] Live archive is inspected.
- [ ] Live episode is inspected.
- [ ] Homepage/archive catalogue covers and all three episode analytical graphics are visible live.

A green build alone is not sufficient evidence that the page is correct.

---

## 19. Controlled publishing workflow

For each new episode:

1. Read the approved episode PDF completely.
2. Extract title, number, series, FU, main result, hotspot, inventory, exclusions, sensitivities and verdict.
3. Extract/rasterize page 1 as the canonical **catalogue cover** for homepage/archive, or use the exact explicitly approved replacement.
4. Visually compare the catalogue cover with the approved source.
5. Create native SVG Inventory Map.
6. Create native SVG Technical Plate.
7. Create native SVG Hotspot Breakdown.
8. Build the page from `episodes/template.html` and set `data-episode="NN"`.
9. Build a text-only episode hero. Do not insert the catalogue cover into the episode page.
10. Add Quick Facts and model-note cards.
11. Reconcile inventory and results.
12. Add sensitivities and verdict.
13. Upload the episode PDF when download is intended.
14. Add one new object to `episodes.json` with complete taxonomy, catalogue-cover path, keywords and related cases.
15. Do not manually edit Latest Case, Recent Cases, archive cards, filter buttons, Previous/Next or Related Cases: they are registry-driven.
16. Verify homepage Latest Case and Recent Cases, including their covers.
17. Verify full archive ordering, Subject filters, LCA-lens filters, search, count, Load More and covers.
18. Verify episode hero contains no cover, then verify jump navigation, text-only Related Cases and Previous/Next.
19. Verify analytical graphic paths and remove staging/temporary files.
20. Commit the controlled release to `main`.
21. Inspect the live homepage, full archive and episode after deployment.
22. Only then consider publication complete.

---

## 20. Future-episode reconstruction protocol

Minimum required inputs:

- this repository;
- this README;
- approved PDF of the new episode.

Optional: original high-resolution cover image, calculation workbook, LinkedIn post/source list and latest DEFRA workbook if the episode itself still needs to be produced.

With repository + README + approved PDF, the website episode and catalogue entry must be reconstructable without asking the user to restate established design rules. The default is to preserve the PDF cover exactly for **homepage/archive catalogue use**, while keeping the individual episode page hero text-only.

---

## 21. Relationship with the wider production workflow

LinkedIn remains the publishing channel; the website is the permanent technical archive. Upstream work may include historical/engineering research, FU definition, boundaries, inventory, factors, Excel model, carousel and LinkedIn post.

The website does not need to duplicate the full workbook but must preserve the core audit trail: **what was modelled, why, with which major flows, where the footprint lands, and what changes the result.**

The archive adds a second analytical layer: **what class of subject is this, and what LCA mechanism does the case teach?**

---

## 22. Non-negotiable principles

1. **The approved PDF controls episode-specific facts, numbers, wording and approved cover artwork.**
2. **Approved covers are catalogue assets displayed only on homepage and Archive. Individual episode pages are text-only at hero level.**
3. **If an approved cover exists, that exact visual is the catalogue cover unless the user explicitly requests a replacement.**
4. **A perceived opportunity to improve, harmonize or restyle a cover is not permission to replace it.**
5. **The README controls the web editorial system.**
6. **`episodes.json` is the single catalogue registry; homepage/archive/navigation metadata must not be duplicated manually.**
7. **Registry data must reconcile with the approved episode source.**
8. **The homepage is concise; the complete searchable catalogue belongs on `archive.html`.**
9. **Every new episode receives the three standard analytical graphics.**
10. **Every published episode participates in automatic internal navigation, text-only Related Cases and Previous/Next navigation.**
11. **Subject categories and LCA characteristics must be analytically meaningful, not decorative labels.**
12. **Every assumption must remain recognisable as an assumption.**
13. **Analytical graphics must be browser-safe, self-contained and legible.**
14. **No broken image, PDF, archive or episode-navigation link is acceptable at publication.**
15. **A successful GitHub Pages build is necessary but not sufficient: the live homepage, archive and episode must be visually checked.**
16. **Individual episode pages must never depend on catalogue-cover loading to remain visually complete.**
17. **Where others see fantasy, we see a functional unit.**
