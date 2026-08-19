# LCA of the Impossible — Website Editorial & Publishing Bible

Static GitHub Pages archive for the **LCA of the Impossible** series.

This README is the canonical editorial and publishing reference for building, updating and reviewing the website. Its purpose is to make the site reproducible in a future session with no prior conversational context. If a new approved episode PDF and this repository are available, the website episode and its catalogue metadata must be rebuildable without relying on memory. The approved PDF is an editorial/technical source, not a public website download. The approved PDF is an editorial/technical source, not a public website download.

---

## 1. Source-of-truth hierarchy

Use this hierarchy whenever sources disagree:

1. **Approved episode PDF / approved LinkedIn carousel** — source of truth for episode-specific facts, numbers, assumptions, results, sensitivities, narrative conclusions and wording. Website catalogue-cover style is governed separately by Section 4.
2. **An explicitly user-approved replacement image** — overrides the source PDF/carousel cover only when the user has specifically selected it as the catalogue cover.
3. **This README and the currently approved catalogue-cover family (#35, #36, #38, #40, #41, #42, #43)** — source of truth for website editorial structure, cover style, publishing rules, taxonomy, asset conventions and QA requirements.
4. **`episodes.json`** — canonical website registry for published episode metadata, ordering, catalogue assets, taxonomy, Evidence Profile data, related cases and navigation relationships. It must not contain public source-PDF fields.
5. **`assets/style.css`** — source of truth for the live visual system and responsive behaviour.
6. **`assets/site.js`** — source of truth for registry-driven homepage/archive rendering, text-only episode heroes, Related Cases and Previous/Next behaviour.
7. **`episodes/template.html`** — canonical implementation starter for new episode pages.
8. Existing episode pages — examples of execution, not authorities over the approved PDF or this README.

Do not silently replace, reconcile or “improve” approved episode content. If a website adaptation requires simplification, preserve the underlying meaning and disclose the simplification.

**Structural rule:** approved cover artwork remains part of the episode package, but the website displays episode covers **only on the homepage and in the full Archive catalogue**. Individual episode pages are deliberately image-free at hero level.

If `episodes.json` conflicts with an approved PDF, correct the registry; do not change the approved episode fact to fit the registry.

---

## 2. Canonical repository structure

- `index.html` — concise homepage with project hero, Latest Case, recent episodes, Method, Series and Book
- `archive.html` — complete searchable/filterable episode catalogue
- `episodes.json` — central episode registry, taxonomy, evidence and navigation metadata; no public source-PDF fields
- `episodes/` — individual episode pages and reusable episode template
- `assets/site.js` — shared catalogue, archive and episode-navigation logic
- `assets/style.css` — global visual system
- `assets/images/episodes/` — canonical catalogue covers used only by homepage and Archive
- `assets/images/episode-graphics/` — Inventory Map, Technical Plate and Hotspot Breakdown graphics
- `assets/images/book/` — book artwork
- `assets/pdf/episodes/` — optional editorial/technical archive for approved source PDFs; these files are not exposed by the public website

Do not create parallel folders for temporary fixes. Avoid duplicate `live`, `v2`, `final`, `new`, `hq2`, `final-final` or similar filenames in the canonical tree. Temporary staging assets must be removed before publication.

The website must remain a simple static GitHub Pages site. Do not introduce a framework, package manager or build dependency unless explicitly required.

---

## 3. Central episode registry — mandatory

`episodes.json` is the single catalogue record used by the homepage, full archive, Evidence Profile / Epic Passport data and episode-to-episode navigation.

Every published episode must contain:

- `number` — numerical episode identifier;
- `slug` — stable filename slug;
- `title` — displayed episode title;
- `url` — relative episode-page path from repository root;
- `cover` — relative path to the approved website catalogue cover from repository root. For new episodes, the cover must follow the canonical catalogue-cover family defined in Section 4; an explicitly user-approved exact replacement always overrides the generated/default cover.
- `categoryLabel` — concise human-readable narrative category;
- `categories` — normalized subject-filter tokens;
- `lcaLabel` — principal LCA characteristic shown on cards;
- `lcaCharacteristics` — normalized LCA filter tokens;
- `result` — approved headline result;
- `hotspot` — concise approved/reconciled hotspot statement;
- `featuredDescription` — short description used when featured;
- `keywords` — useful search terms;
- `related` — ordered list of related episode numbers.

The public registry must **not** contain a `pdf` field or any other source-PDF download reference. Source PDFs may exist only as editorial/technical archive material outside the public registry contract.

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

- `epNN-short-slug-cover.png` — canonical high-resolution website catalogue cover, homepage/Archive only;
- `epNN-inventory-map.svg` — life-cycle input map;
- `epNN-technical-plate.svg` — engineering/reconstruction plate;
- `epNN-hotspot-breakdown.svg` — contribution/hotspot graphic;
- `epNN-short-slug.pdf` — optional approved source PDF retained only as editorial/technical archive material; never linked from the public site or registry.

A cache-safe revision suffix such as `-cover-YYYYMMDD.png` is allowed and recommended when replacing an already published cover. Do not overwrite a live cover in place if doing so could leave stale CDN/browser content.

If a source PDF is retained in the repository archive, use a stable canonical name such as `epNN-short-slug.pdf`. Do not expose it through episode pages, navigation, `episodes.json`, metadata or public download controls.

### 4.1 Canonical catalogue-cover family — mandatory

All new episode covers must belong to the same visual family as the currently approved catalogue set. The canonical style references are the live covers for:

- Episode #35 — The Flying Dutchman;
- Episode #36 — The Tower of Babel;
- Episode #38 — Trojan Horse, especially as the reference for **realistic central-subject rendering**;
- Episode #40 — The Minotaur's Labyrinth;
- Episode #41 — Mjölnir;
- Episode #42 — Talos;
- Episode #43 — Sisyphus.

These covers are the **style source of truth** for future catalogue artwork. New covers must look like another issue from the same designed series, not merely use similar colours.

The cover must be created specifically for the website catalogue unless the user supplies and explicitly approves an exact replacement image. An approved PDF/carousel cover may be reused only when it already belongs to this same visual family or the user explicitly instructs that it be used.

If the user provides or approves a specific cover image, use **that exact image**. Do not redraw, regenerate, reinterpret, crop, recolour, retouch, recompress or substitute it unless explicitly requested.

### 4.2 Required cover design language

Mandatory characteristics:

- portrait **4:5** composition;
- high-resolution raster output, preferably PNG, with the full artwork visible and no catalogue crop;
- near-black charcoal / deep navy background with subtle paper/engraving texture;
- thin aged bronze/gold outer frame with small geometric/technical registration marks;
- centered top line `LCA OF THE IMPOSSIBLE` in widely tracked classical serif capitals;
- a smaller centered `EPISODE #NN` line below it, using one restrained episode-specific accent colour;
- a very large off-white / warm ivory serif title dominating the upper third;
- one unmistakable central subject rendered **realistically**: convincing three-dimensional form, physically plausible materials, surface texture, construction details, depth, lighting and scale. The preferred treatment is technical-archaeological / engineering realism, comparable to the approved Episode #38 Trojan Horse cover;
- blueprint, engraving or technical-drawing language may frame and annotate the subject, but **must not replace the realistic central illustration**. The subject itself must not read as a flat icon, simple line drawing, abstract schematic or generic vector silhouette;
- restrained blueprint/engineering construction geometry behind or around the subject: circles, axes, measurement marks, technical panels, trajectories, diagrams or equations as appropriate to the case;
- analytical decoration must remain secondary to the subject and title; never turn the cover into a dashboard or collage;
- bottom-center small geometric series mark and an italic principal LCA lens such as `Materials-driven`, `Operation-driven` or `Energy-driven`;
- optional recurring micro-elements such as `CYCLE ∞`, a side technical panel, route line, work/energy notation or resource-accounting schematic when they are relevant to the episode;
- muted bronze/gold and warm ivory as the common palette, with **only one restrained episode-specific accent** (for example cyan, green or red) used consistently for episode number and selected technical cues;
- dark, serious, archaeological/engineering atmosphere with an epic editorial layer;
- typography, border proportions, title scale, visual density and subject treatment must remain recognizably consistent with the reference covers.

Do **not** use:

- generic website-blue/neon styling as the dominant cover language;
- bright multi-colour palettes;
- flat vector poster art or a schematic-only central subject;
- clean modern corporate infographic styling;
- generic photorealistic movie-poster composition with no technical/editorial structure;
- multiple competing subjects or busy collage layouts;
- soft focus, intentional blur, low-resolution rasterization or illegible microtext;
- a square crop or any other aspect ratio for the canonical catalogue asset.

The composition may adapt to the subject — ship, structure, object, automaton, landscape or figure — but it must preserve the same editorial grammar. Consistency of **series identity** takes priority over forcing every subject into the exact same geometry.

### 4.3 Cover production, approval and exact-file rule

For every new episode:

1. Determine the principal visual subject from the approved episode content.
2. Determine the principal LCA lens (`Materials-driven`, `Operation-driven`, `Energy-driven`, etc.) from the actual result.
3. Create a new 4:5 cover using the canonical family above and the current covers as direct style references. **The central subject must be realistic, not merely technical or stylized.**
4. Keep the episode-specific accent restrained and subordinate to bronze/gold and ivory.
5. Check spelling, episode number, title, diacritics and LCA lens before publication.
6. Compare the new cover side-by-side with at least three existing reference covers, including Episode #38 when assessing realism. It must look like the next issue of the same series.
7. Once the cover image shown in the creation/approval step is accepted, **freeze that exact raster file as the approved asset**. From this point onward, do not call image generation again for the cover and do not create a visually similar replacement merely to facilitate upload.
8. Publish **the exact file produced and approved in Step 7** to `assets/images/episodes/`. The repository asset must be byte-for-byte identical to the approved image whenever the transfer path permits it. Renaming the file is allowed; changing its image bytes is not.
9. If the generated/approved image cannot be transferred directly by the available connector, ask the user to upload **that exact file** to the repository. After the upload, link `episodes.json` to the uploaded file; do not regenerate the image as a workaround.
10. When normalizing a manually uploaded filename, preserve the uploaded blob unchanged. A Git tree rename/copy that keeps the same blob SHA is preferred; do not decode/re-encode, recompress or convert the image.
11. Point `episodes.json` to the exact canonical asset path only after confirming the file exists in the repository.
12. Render Homepage and Archive at desktop and mobile widths and confirm the entire 4:5 artwork is visible without cropping.
13. Verify the live GitHub Pages asset, not only the repository commit or build status. Publication is incomplete until the displayed cover is the approved image.

When a cover is replaced after publication, use a cache-safe new filename/revision, update `episodes.json`, deploy, and verify what GitHub Pages actually serves before considering the replacement complete. **Never solve a cache or transfer problem by regenerating the artwork.**

### 4.4 Where covers are allowed

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
- no source-PDF download action. The only episode export is the Epic Model Passport through `Print / Save as PDF`.

Do not hard-code or dynamically inject links to the source episode PDF. Legacy source-PDF controls must be removed by synchronization and defensively suppressed by `assets/passport-cleanup.js`.

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

1. Every new episode requires a 4:5 catalogue cover in the canonical visual family defined in Section 4.
2. The live covers for Episodes #35, #36, #38, #40, #41, #42 and #43 are the mandatory style references; Episode #38 is the explicit reference for realistic rendering of the main subject.
3. The main subject must be realistically rendered with credible form, materiality and depth; blueprint/technical elements are supporting graphics, not a substitute for the realistic illustration.
4. If the user explicitly approves or supplies a specific replacement, use that exact image without alteration.
5. Once a generated cover is approved in the creation step, the exact generated file becomes the immutable publication asset. Do not regenerate a look-alike for GitHub upload.
6. A PDF/carousel cover is not automatically the website catalogue cover; reuse it only when it already matches the canonical family or the user explicitly requests it.
7. Homepage and Archive must show the full cover with no crop.

Before publication, compare the new cover with the reference family and with any explicitly approved source image. A style mismatch, insufficiently realistic central subject, wrong episode number/title, unauthorized image alteration or visible crop is a homepage/archive publication blocker.

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

PDF availability is **registry-declared**, while the visible download action is **static HTML** in the episode page.

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

When a valid `pdf` field exists, the episode HTML must contain exactly one standardized **Download episode PDF ↓** button in the text-only hero. The button is static HTML and must not depend on `assets/site.js`.

Use a local project path to the approved file. For cache safety with older site-script versions, the live href may use the equivalent `../assets/pdf/./episodes/epNN-short-slug.pdf` form; the registry itself must retain the canonical `assets/pdf/episodes/epNN-short-slug.pdf` path.

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

- [ ] Cover is portrait 4:5 and follows the canonical #35/#36/#38/#40/#41/#42/#43 visual family.
- [ ] Central subject is realistically rendered with credible form, materiality, depth and construction detail; technical graphics remain secondary.
- [ ] Title, episode number, diacritics and principal LCA lens are correct.
- [ ] Bronze/gold + ivory remain the common palette; episode accent is restrained.
- [ ] One clear central subject and technical/blueprint framing are present without becoming a collage.
- [ ] The published cover is **the exact image approved during the creation/approval step**, not a subsequent regeneration or look-alike.
- [ ] If the user supplied/approved an exact cover, the published file is byte-for-byte that image unless alteration was explicitly requested.
- [ ] If a manually uploaded file was renamed/normalized, the repository blob SHA is unchanged or the binary identity has otherwise been verified.
- [ ] Full artwork renders in Homepage and Archive without cropping on desktop and mobile.
- [ ] The live GitHub Pages image has been visually checked against the approved source image.

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
3. Create the 4:5 catalogue cover in the canonical #35/#36/#38/#40/#41/#42/#43 visual family, with a **realistic central illustration**; unless the user has supplied an explicitly approved exact cover.
4. Validate title, episode number, diacritics, LCA lens, style continuity, realistic subject treatment and no-crop rendering.
5. Obtain explicit or contextual approval of the displayed cover and **freeze that exact generated/uploaded raster file**. Do not regenerate it after approval.
6. Upload/publish that exact approved image to `assets/images/episodes/`. If direct transfer is unavailable, have the user upload the exact file and then normalize only the filename/path while preserving the binary/blob.
7. Verify the repository file and update `episodes.json` to that exact path.
8. Create Inventory Map SVG.
9. Create Technical Plate SVG.
10. Create Hotspot Breakdown SVG.
11. Build page from `episodes/template.html` and set `data-episode="NN"`.
12. Build text-only episode hero.
13. Add Quick Facts and model notes.
14. Reconcile inventory/results.
15. Add sensitivities and verdict.
16. If public download is intended, upload the **exact approved PDF** to `assets/pdf/episodes/epNN-short-slug.pdf`.
17. Add one object to `episodes.json`, including `pdf` only after the file exists.
18. Do not manually edit Latest Case, Recent Cases, archive cards, filters, Previous/Next or Related Cases; they are registry-driven. Add the standardized static PDF button to the episode hero when a public PDF has been registered.
19. Verify homepage Latest/Recent and covers against the exact approved cover source.
20. Verify Archive ordering, filters, search, count, Load More and covers.
21. Verify episode has no cover, navigation works and PDF action appears when registered.
22. Verify all analytical graphic paths and remove staging files.
23. Commit controlled release to `main`.
24. Inspect live homepage, archive and episode.
25. Verify that the live cover is the exact approved image; do not rely on a successful build alone.
26. Test PDF download when applicable.
27. Only then consider publication complete.

---

## 21. Future-episode reconstruction protocol

Minimum inputs:

- this repository;
- this README;
- approved PDF of the new episode.

Optional: an explicitly user-approved exact cover image, calculation workbook, LinkedIn post/source list and latest DEFRA workbook if the episode itself still needs to be produced. If no exact cover is supplied, the live covers for Episodes #35, #36, #38, #40, #41, #42 and #43 provide the mandatory visual reference family; Episode #38 is the preferred realism reference for the central subject.

With repository + README + approved PDF, the website episode and catalogue entry must be reconstructable without asking the user to restate established design rules.

---

## 22. Relationship with wider production workflow

LinkedIn remains the publishing channel; the website is the permanent technical archive. Upstream work may include historical/engineering research, FU definition, boundaries, inventory, factors, Excel model, carousel and LinkedIn post.

The website need not duplicate the full workbook but must preserve the core audit trail: **what was modelled, why, with which major flows, where the footprint lands, and what changes the result.**

---

## 23. Non-negotiable principles

1. **The approved PDF controls episode-specific facts, numbers and wording; the website catalogue cover follows the canonical visual family unless an exact cover is explicitly approved by the user.**
2. **Approved catalogue covers are 4:5 assets in the canonical #35/#36/#38/#40/#41/#42/#43 visual family and are displayed only on Homepage and Archive.**
3. **The central cover illustration must be realistic; blueprint/technical graphics support it but do not replace it.**
4. **Once a cover is approved during the image-creation step, that exact image file is the publication asset. Never regenerate a substitute merely to upload it to GitHub.**
5. **If direct connector transfer of the approved image is unavailable, the user uploads the exact image and the publishing workflow links that exact repository file without re-encoding or reinterpretation.**
6. **Individual episode heroes are text-only.**
7. **The README controls the web editorial system.**
8. **`episodes.json` is the single registry for catalogue metadata, navigation relationships and PDF availability.**
9. **PDF download buttons are static HTML in each eligible episode hero; they must remain usable without JavaScript.**
10. **A `pdf` registry field is allowed only when the exact file exists in `assets/pdf/episodes/`.**
11. **No broken PDF link is acceptable.**
12. **Registry data must reconcile with the approved episode.**
13. **The homepage is concise; the full searchable catalogue belongs on `archive.html`.**
14. **Every episode receives the three standard analytical graphics.**
15. **Every published episode participates in automatic navigation and text-only Related Cases.**
16. **Every assumption remains recognizable as an assumption.**
17. **Analytical graphics must be browser-safe, self-contained and legible.**
18. **A successful GitHub Pages build is necessary but not sufficient: live pages, the exact live cover asset and any registered PDF download must be checked.**
19. **Where others see fantasy, we see a functional unit.**


### Catalogue-cover QA

- Verify the `cover` path in `episodes.json`.
- Verify the high-resolution 4:5 cover asset exists and renders correctly.
- Compare it side-by-side with the canonical reference covers #35, #36, #38, #40, #41, #42 and #43.
- Verify that the central subject is realistically rendered; reject a flat, schematic-only or icon-like replacement.
- Verify the full artwork is visible with no square crop or `object-fit: cover` loss.
- Inspect Latest Case, Recent Cases and Archive on desktop and mobile.
- Reject wrong titles/numbers, blurred, soft, broken, over-coloured, flat-vector, generic-poster or visibly inconsistent cover assets.
- Verify that the repository/live asset is the **exact image approved in the creation step**. A visually similar regenerated image is not acceptable.
- If an exact user-approved image was supplied, verify no transformation occurred.
- When replacing a live cover, use a cache-safe publication path and confirm the new asset is what GitHub Pages serves.

---

<!-- SEO-RULES:START -->

## 24. SEO, social sharing and discovery — mandatory

Every public page must be self-describing in its static HTML. Do not rely on client-side JavaScript for search-engine or social-preview metadata.

Required on `index.html`, `archive.html`, `method.html` and every published episode page:

- one absolute canonical URL under `https://lcaofimpossible.github.io/LCA-of-the-Impossible/`;
- a concise meta description;
- `robots` set to `index,follow,max-image-preview:large`;
- Open Graph metadata: `og:site_name`, `og:type`, `og:title`, `og:description`, `og:url`, `og:image`, `og:image:alt`, `og:locale`;
- Twitter/X card metadata using `summary_large_image`, with title, description, image and image alt text;
- one parseable JSON-LD block. Use `WebSite` for the homepage, `CollectionPage` for the Archive, `WebPage` for the Method page and `Article` for episode pages;
- shared favicon and web manifest links.

For episode pages, the Open Graph/Twitter image must point to the **exact approved catalogue cover already registered in `episodes.json`**. This use is metadata for link previews and does not change the rule that the cover is not visually displayed in the episode-page hero.

`robots.txt` must allow crawling and reference the canonical `sitemap.xml`. `sitemap.xml` must contain the homepage, Archive, Method page and every published episode URL, and must exclude `episodes/template.html`.

`episodes/template.html` must remain `noindex,nofollow` until instantiated as a real episode.

SEO metadata, sitemap, robots, favicon and manifest are maintained deterministically by `scripts/apply_seo.py`. `scripts/seo_qa.py` verifies that the committed site matches `episodes.json`. When a new episode is added, publication is incomplete until these checks pass and the live deployment contains the updated canonical/social metadata.

### SEO/social QA

- [ ] Canonical URL is absolute and correct.
- [ ] Meta description is present and episode-specific where applicable.
- [ ] Open Graph and Twitter card fields are complete.
- [ ] Episode social image is the exact registered cover path.
- [ ] JSON-LD parses and uses the correct page type.
- [ ] Sitemap contains every published episode exactly once.
- [ ] `robots.txt` references the live sitemap.
- [ ] Favicon and manifest are linked from public pages.
- [ ] Template is excluded from indexing.
- [ ] LinkedIn/social preview metadata exists in static HTML before publication.

<!-- SEO-RULES:END -->

---

<!-- PHASE3-RULES:START -->

## 25. Interactive exploration, comparison and evidence profiles — mandatory

Phase 3 adds analytical exploration without turning unlike functional units into comparative environmental claims.

### 25.1 Registry fields

`episodes.json` uses `schemaVersion: 2`. Every published episode must additionally contain:

- `functionalUnit` — the exact or faithfully normalized functional unit / reporting basis shown in the episode hero;
- `evidence.confidence` — `Low`, `Medium` or `High` qualitative confidence in the narrative, historical or physical evidence constraining the reconstruction;
- `evidence.proxyDependence` — `Low`, `Medium` or `High` dependence on analogue processes or modern emission-factor proxies;
- `evidence.assumptionSensitivity` — `Low`, `Medium` or `High` sensitivity to key engineering assumptions, boundaries or scenario choices;
- `evidence.basis` — concise description of the source/analogue basis and what is reconstructed;
- `evidence.uncertainty` — the main modelling uncertainty that materially affects interpretation.

These evidence fields are editorial transparency indicators. They are **not** a formal ISO data-quality rating, uncertainty analysis or verification statement.

### 25.2 Compare Cases

`compare.html` allows selection of two or three published episodes. The table may compare functional unit, headline result, narrative category, LCA lens, hotspot, evidence confidence, proxy dependence, assumption sensitivity and principal modelling uncertainty.

The comparison must always display an explicit warning that headline results have different functional units and system boundaries. Do not calculate ratios, rankings, winners/losers or comparative environmental claims between unlike cases.

The selected episode numbers may be encoded in the URL as `compare.html?cases=43,42,41` so a comparison can be shared. Archive cards may expose `+ Compare`; no more than three cases may be selected at once.

### 25.3 Explore the Impossible / impact map

`explore.html` places published headline results on a logarithmic climate-impact scale. Result strings may be normalized internally to kg CO₂e **only to calculate position on the logarithmic axis**. This normalization does not harmonize functional units and must never be described as a like-for-like comparison.

The map must:

- retain the published result text beside each point;
- link every point back to the episode;
- allow filtering by principal LCA lens;
- display a persistent explanation that scale position is descriptive, not a ranking;
- remain usable on mobile without horizontal page overflow.

### 25.4 Episode Evidence Profile

Every episode receives an Evidence Profile immediately after Quick Facts and before the Visual Model. It displays Evidence confidence, Proxy dependence and Assumption sensitivity plus expandable Evidence basis and Main modelling uncertainty notes.

The Evidence Profile is generated from `episodes.json` by `assets/site.js`; do not duplicate these values manually inside individual episode HTML. The episode jump navigation must include `Evidence` when the profile is present.

### 25.5 Phase 3 files and QA

Canonical Phase 3 files:

- `compare.html` — side-by-side technical comparison;
- `explore.html` — logarithmic impact-scale exploration;
- `assets/features.css` — styles for comparison, impact map and evidence profiles;
- `scripts/feature_sync.py` — synchronizes Phase 3 metadata, sitemap entries and these README rules;
- `scripts/feature_qa.py` — validates registry evidence fields and Phase 3 page integrity.

`SEO Sync` must run `scripts/feature_sync.py` after `scripts/apply_seo.py`. `Site QA` must run both feature synchronization in its temporary QA workspace and `scripts/feature_qa.py`.

### Phase 3 QA

- [ ] Every published episode has a meaningful `functionalUnit`.
- [ ] Every published episode has all five `evidence` fields.
- [ ] Evidence levels use only `Low`, `Medium` or `High`.
- [ ] Compare Cases accepts 2–3 unique cases and never presents a better/worse ranking.
- [ ] Archive compare selection is capped at three cases.
- [ ] Impact map uses a logarithmic magnitude scale and retains original published result labels.
- [ ] Both interactive pages contain the functional-unit/non-comparability warning.
- [ ] Every episode renders its Evidence Profile before the Visual Model.
- [ ] `compare.html` and `explore.html` are present exactly once in `sitemap.xml`.
- [ ] Phase 3 pages carry canonical/social metadata and remain responsive.

<!-- PHASE3-RULES:END -->

---

<!-- PHASE4-RULES:START -->

## 26. Engagement, collections and sharing — mandatory

Phase 4 improves discovery and sharing without weakening the technical framing of the series.

### 26.1 Curated collections

Editorial collections are stored in `collections.json`, not hard-coded into individual pages. Every collection must contain:

- a unique lowercase kebab-case `slug`;
- a concise `title`;
- an uppercase editorial `eyebrow`;
- a meaningful `description`;
- at least two unique published episode numbers.

Collections may overlap. They are editorial routes through the archive and are not mutually exclusive classifications.

The canonical Phase 4 collection page is `collections.html`. It renders collection membership from `collections.json` and `episodes.json`. Because the established catalogue-cover rule limits episode covers to Homepage and Archive, **collection cards are text-only**.

### 26.2 Random discovery

`Random impossible case` may appear on Homepage, Archive, Collections and episode pages. It must always resolve to an already published registry entry. On an episode page, the current episode should be excluded when another case is available.

A collection-specific random action must select only from the episode numbers registered for that collection.

### 26.3 Sharing

Every episode receives a `Share the case` block generated by `assets/engagement.js`. It may provide:

- native Web Share where supported;
- copy canonical episode link;
- copy a LinkedIn-ready caption containing episode number, title, short description, headline result, LCA lens and canonical URL;
- random next case.

Sharing tools must use the canonical episode URL and must not rewrite the technical result, functional unit or LCA lens.

### 26.4 LinkedIn follow link

`collections.json` contains `socialLinks.linkedin`. Keep it `null` until the exact public LinkedIn profile/page URL is explicitly known. Never guess or infer a profile URL.

When a valid URL is registered, `assets/engagement.js` may expose `Follow on LinkedIn` CTAs. The absence of a LinkedIn URL must not create a broken or placeholder link.

### 26.5 Phase 4 files and automation

Canonical Phase 4 files:

- `collections.json` — editorial collection registry and optional social links;
- `collections.html` — curated collection browser;
- `assets/engagement.js` — random discovery, collection rendering and episode sharing;
- `assets/engagement.css` — Phase 4 styling;
- `scripts/engagement_sync.py` — synchronizes Phase 4 scripts, metadata, sitemap and these README rules;
- `scripts/engagement_qa.py` — validates collection integrity, sharing hooks and publication wiring.

`SEO Sync` must run `scripts/engagement_sync.py` after Phase 3 synchronization. `Site QA` must run the same synchronization in its temporary workspace and then run `scripts/engagement_qa.py`.

### Phase 4 QA

- [ ] Every collection slug is unique and valid.
- [ ] Every collection contains at least two unique published episodes.
- [ ] Collection cards remain text-only.
- [ ] `collections.html` has canonical/social metadata and exactly one sitemap entry.
- [ ] Homepage and Archive expose collection/random discovery entry points.
- [ ] Episode pages load `assets/engagement.js`.
- [ ] Episode sharing uses canonical URLs.
- [ ] Random case selection uses only published episodes.
- [ ] LinkedIn follow CTA is hidden while `socialLinks.linkedin` is null.
- [ ] No placeholder social URL is published.
- [ ] Phase 4 remains usable on mobile and respects existing cover-rendering rules.

<!-- PHASE4-RULES:END -->

---

<!-- METHOD-RULES:START -->

## 27. Dedicated Method page and methodological transparency — mandatory

The site now contains a dedicated methodology layer. The canonical files are:

- `method.html` — full public methodology page;
- `assets/method.css` — isolated styling for the methodology page and the homepage Method preview.

The homepage must remain concise. Its Method section is a **preview**, not the full methodology. It must retain the headline `Fantasy in. Inventory out.`, show the four macro-phases `Define → Reconstruct → Quantify → Interpret`, and link to `method.html` with a visible `Explore the full methodology →` action.

`method.html` is the canonical public explanation of how impossible subjects are translated into traceable life-cycle models. It must remain a static, framework-free page and must not require JavaScript for core content.

### 27.1 Canonical methodology pipeline

The full Method page must present these seven stages in this order:

1. **Define the subject** — establish what is actually being assessed.
2. **Establish the evidence** — distinguish source evidence, reconstruction, inference and assumptions.
3. **Define the functional unit** — translate the narrative into a quantified service, event, journey, lifetime or reporting basis.
4. **Reconstruct the system** — translate form and function into geometry, materials, energy, movement, operation and maintenance.
5. **Build the inventory** — assign activity data, boundaries, proxies, quantities and modelling bases.
6. **Calculate the footprint** — connect activity data to the best available defensible emission factors while preserving traceability.
7. **Interpret the result** — identify hotspots, sensitivities and uncertainty and explain what the result means within the scenario.

Do not collapse the methodology into a simplistic “pick subject / calculate number” narrative. Interpretation and evidence transparency are part of the method, not optional editorial decoration.

### 27.2 Evidence Ladder

The Method page uses the provenance ladder:

`Known → Reconstructed → Inferred → Assumed`

These labels describe how an input enters the model; they are not a numeric ranking or formal data-quality score.

- **Known** — directly stated, measured, historically documented or otherwise supported by explicit source evidence.
- **Reconstructed** — derived from dimensions, mechanics, engineering relationships or defensible physical reconstruction.
- **Inferred** — supported by contextual evidence, comparable systems or a reasoned analogue but not directly stated.
- **Assumed** — a declared scenario choice required to close the model where evidence cannot.

The public Method explanation of Evidence confidence, Proxy dependence and Assumption sensitivity must remain aligned with the registry fields defined in Section 25. Levels remain only `Low`, `Medium` or `High`. These are transparency indicators, not formal ISO data-quality ratings, verification statements or uncertainty distributions.

### 27.3 Assumption Ledger

The Method page must explain that assumptions are accounted for rather than hidden. The canonical illustrative statuses are:

- `Reconstruction` for geometry/mass derived through physical or engineering logic;
- `Inference` for material/technology choices based on historical, canonical or comparable-system evidence;
- `Assumption` for declared transport, operation, duration, frequency or other scenario choices;
- `Factor` for the dataset applied to an activity flow.

This ledger is illustrative methodology, not an episode-specific inventory. Do not insert invented episode values into it.

### 27.4 Emission-factor hierarchy

The public methodology expresses the selection logic as:

`Specific → Representative → Proxy`

Use the most specific defensible factor available for the activity being modelled. Where a representative dataset or proxy is required, the loss of specificity and proxy dependence must remain visible. This hierarchy does not override episode-specific factor choices in an approved PDF and does not authorize silently replacing an approved factor.

### 27.5 System boundary and result interpretation

The Method page may illustrate the life cycle as:

`Raw materials → Construction / manufacture → Transport → Operation → Maintenance / repetition → End of life`

This is an illustrative boundary only. Individual episodes define their own reporting slice and do not automatically include every stage.

The Method page must also make three interpretive principles explicit:

1. the result is **not a claim that the fictional or legendary subject physically exists exactly as modelled**;
2. the result must **not imply false precision beyond the inventory and evidence quality**;
3. the reconstructed scenario can still support a meaningful LCA question using functional units, inventories, boundaries, factors, hotspots and sensitivities.

### 27.6 Audit trail

The canonical public chain is:

`Subject → Source → Assumption → Activity data → Factor → Result`

The Method page must reinforce the principle that every published result should retain a path back to the model that produced it. This is consistent with the inventory and modelling rules in Section 8 and the Evidence Profile requirements in Section 25.

### 27.7 Visual and accessibility rules

The Method page uses the existing dark technical/blueprint visual language, with cyan/light-cyan and restrained gold accents. It should read as a technical manifesto or laboratory protocol rather than a corporate dashboard.

Required:

- responsive layouts with no horizontal page overflow; intentional horizontal scrolling is allowed only for bounded analytical flows/tables;
- semantic headings and meaningful `aria-label` use for process diagrams;
- essential methodological meaning must exist as HTML text, not only as decoration;
- no framework, package manager or build dependency;
- `assets/method.css` must remain isolated from episode-specific styling as far as practical;
- no decorative cover artwork is required on `method.html`.

### 27.8 SEO and discovery

`method.html` must have its own absolute canonical URL, meta description, robots directive, Open Graph metadata, Twitter metadata, favicon/manifest links and parseable `WebPage` JSON-LD. It must appear exactly once in `sitemap.xml`.

### Method QA

- [ ] Homepage Method preview contains exactly the four macro-phases `Define`, `Reconstruct`, `Quantify`, `Interpret`.
- [ ] Homepage links to `method.html`.
- [ ] Full Method page contains the seven-stage canonical pipeline in the correct order.
- [ ] Evidence Ladder uses exactly `Known`, `Reconstructed`, `Inferred`, `Assumed`.
- [ ] Evidence Profile terminology matches `episodes.json` and Section 25.
- [ ] Evidence levels are only `Low`, `Medium`, `High`.
- [ ] Factor hierarchy is `Specific → Representative → Proxy` and is described as a modelling preference, not an override of approved episode data.
- [ ] System-boundary graphic is explicitly labelled illustrative.
- [ ] Audit trail is `Subject → Source → Assumption → Activity data → Factor → Result`.
- [ ] Method content remains usable without JavaScript.
- [ ] `method.html` is present exactly once in `sitemap.xml`.
- [ ] Desktop and mobile rendering show no unintended overflow or clipped content.

<!-- METHOD-RULES:END -->

---

<!-- PHASE5-RULES:START -->

## 28. Phase 5 — global navigation, Sources & Data, About and LCA Glossary — mandatory

Phase 5 turns the website from an episode archive into a self-explaining editorial and technical project.

### 28.1 Canonical global navigation

Every public page and every episode page uses the same primary navigation:

`Episodes · Explore · Method · About`

`Explore` contains:

- `Collections`;
- `Compare`;
- `Impact map`;
- `Sources & data`;
- `Glossary`.

The brand remains the Home link. Navigation must be keyboard-accessible, responsive and valid without a framework. `scripts/phase5_sync.py` normalizes this header across root pages and all published episode HTML so older pages cannot retain a divergent menu.

### 28.2 Sources & Data

`sources.html` is the canonical public data-policy page. It explains source provenance, emission-factor selection, proxies and versioning without inventing episode-specific source lists.

Canonical hierarchy:

`Direct evidence → Engineering reconstruction → Representative data → Declared proxy`

Canonical emission-factor preference:

`Specific → Representative → Proxy`

Where UK Government / DEFRA factors are used, distinctions such as direct emissions, WTT, T&D, outside-of-scopes and biogenic treatment must remain separate when relevant. The page describes selection logic; it never overrides the factor choices in an approved episode.

Published episodes are not silently recalculated when a newer dataset is released. A methodological or numerical revision must be explicit and traceable.

### 28.3 About

`about.html` explains why the project exists, its independent status and its limits. It must make clear that:

- impossible subjects are used to make LCA reasoning visible and memorable;
- the work is analytical reconstruction, not certification of fictional products;
- Evidence Profile indicators are not formal ISO data-quality ratings or verification statements;
- unlike functional units must not be turned into better/worse environmental rankings;
- storytelling supports the analysis and never replaces it.

### 28.4 LCA Glossary

`glossary.html` is a searchable plain-language glossary of terminology actually used by the project. It must retain precise meanings while remaining readable to non-specialists.

The glossary is explanatory, not normative. It does not replace ISO standards, GHG accounting standards, official dataset documentation or programme rules.

### 28.5 Homepage project infrastructure

The homepage includes a compact `PROJECT INFRASTRUCTURE` block linking to:

- Method;
- Sources & Data;
- LCA Glossary;
- About.

This block is text-only and must not compete visually with Latest Case or Recent Cases.

### 28.6 Canonical files and automation

Phase 5 canonical files:

- `sources.html`;
- `about.html`;
- `glossary.html`;
- `assets/editorial.css`;
- `scripts/phase5_sync.py`;
- `scripts/phase5_qa.py`.

`SEO Sync` must run `scripts/phase5_sync.py` after Phase 4 synchronization. `Site QA` must run the same Phase 5 synchronization in the QA workspace and then execute `scripts/phase5_qa.py`.

### Phase 5 QA

- [ ] Every public root page uses the canonical global navigation.
- [ ] Every published episode page uses the canonical global navigation after synchronization.
- [ ] `Explore` links to Collections, Compare, Impact map, Sources & Data and Glossary.
- [ ] `sources.html`, `about.html` and `glossary.html` are public, responsive and linked from the site.
- [ ] All three pages contain complete static canonical/social metadata.
- [ ] `sources.html` states both source hierarchy and `Specific → Representative → Proxy` factor preference.
- [ ] Glossary contains at least 20 meaningful project terms and remains usable without the search enhancement.
- [ ] Homepage exposes the four Project Infrastructure links.
- [ ] `method.html`, `sources.html`, `about.html` and `glossary.html` each appear exactly once in `sitemap.xml`.
- [ ] Phase 5 pages load `assets/editorial.css` and have no broken local references.

<!-- PHASE5-RULES:END -->

---

<!-- PHASE6-RULES:START -->

## 29. Phase 6 — Model Passport, richer Impact Map and methodology versioning — mandatory

Phase 6 adds a compact transparency layer without introducing new episode facts that are not already registered.

### 29.1 Model Passport

Every published episode receives a registry-derived `MODEL PASSPORT` generated by `assets/phase6.js`.

The passport may display only fields already present in `episodes.json`:

- functional unit / reporting basis;
- headline result;
- principal LCA lens;
- main hotspot;
- Evidence confidence;
- Proxy dependence;
- Assumption sensitivity;
- Evidence basis;
- Main modelling uncertainty.

The passport must explicitly state that it introduces no additional assumptions. It must not fabricate system boundaries, factor lists, allocation rules or detailed assumptions that are not structured in the registry. Readers are directed to the episode inventory and registered source/model notes for the full public interpretation.

The user-facing export is the visual Epic Passport through `Print / Save as PDF`. Raw-text export is retired, and the original episode PDF is not exposed as a website download.

### 29.2 Richer Impact Map

`explore.html` retains the existing logarithmic positioning and non-comparability warning. Phase 6 adds expandable technical context for each plotted case using only registry fields:

- functional unit;
- main hotspot;
- Evidence confidence;
- Proxy dependence;
- Assumption sensitivity;
- direct link to the episode.

The added context must never convert the scale into a better/worse ranking.

### 29.3 Methodology versioning

`method.html` contains a visible methodology-version block. Current public version:

`Methodology version 1.0 · Updated August 2026`

Version changes must be substantive and documented in a short changelog. Do not increment the methodology version for purely visual, typographic or copy-editing changes.

Versioning does not silently reclassify or recalculate previously published episodes. Where a later methodological change affects interpretation of older cases, that relationship must be disclosed explicitly.

### 29.4 Canonical files and automation

Phase 6 canonical files:

- `assets/phase6.css`;
- `assets/phase6.js`;
- `scripts/phase6_sync.py`;
- `scripts/phase6_qa.py`.

`SEO Sync` must run `scripts/phase6_sync.py` after Phase 5 synchronization. `Site QA` must run the same synchronization in the QA workspace and then execute `scripts/phase6_qa.py`.

### Phase 6 QA

- [ ] Every published episode loads Phase 6 CSS and JavaScript after synchronization.
- [ ] Model Passport fields are registry-derived only.
- [ ] Printed/saved Passport retains the canonical episode URL and the interpretation disclaimer.
- [ ] No passport invents an unregistered system boundary, factor list or assumption set.
- [ ] Impact Map retains the non-comparability warning and gains expandable technical context.
- [ ] Method page displays `Methodology version 1.0` and `Updated August 2026`.
- [ ] Method changelog contains at least one explicit version entry.
- [ ] Phase 6 remains usable on mobile and does not alter catalogue-cover rules.

<!-- PHASE6-RULES:END -->

---

<!-- EPIC-PASSPORT-RULES:START -->

## 30. Epic Model Passport presentation — mandatory

The canonical Model Passport presentation is the **Epic Passport**. This rule extends Section 29 without changing its data-governance constraints.

Every published episode exposes only two Passport actions:

1. `View epic passport →` — opens the full-screen technical dossier;
2. `Print / Save as PDF` — uses the dedicated A4 print layout defined in `assets/phase6.css`.

The former raw-text export is retired. The original episode PDF is also no longer a public website download: episode pages, the episode template and `episodes.json` must not expose or link a source PDF. Source PDF artefacts may remain in the repository as editorial/technical archive material, but they are not part of the public website navigation or registry contract.

The Epic Passport uses the registered episode cover and the existing registry fields only. Its visual language is dark technical/blueprint with cyan accents, restrained gold, archive-record identifiers, evidence blocks and a traceability seal. It must feel epic and collectible without weakening methodological readability.

No visual element may introduce an unregistered system boundary, factor list, allocation rule, assumption or numerical value. The Passport remains a transparency summary, not a verification statement or formal data-quality rating.

The shared implementation in `assets/phase6.js` and `assets/phase6.css` applies to all currently published and future episode pages. `scripts/epic_passport_sync.py` propagates the current versioned assets, removes legacy PDF download CTAs and removes legacy `pdf` fields from the public registry. `assets/passport-cleanup.js` is a defensive runtime safeguard: if stale or legacy markup injects a source-PDF CTA or raw-text control, it removes it from the rendered episode page.

### Epic Passport QA

- [ ] All episode pages reference the current versioned Phase 6 assets.
- [ ] Full-screen Passport includes registered cover, episode number/title/category/LCA lens and headline result.
- [ ] Reporting basis, hotspot and Evidence Profile remain visible.
- [ ] Evidence basis and main modelling uncertainty remain visible.
- [ ] `Print / Save as PDF` uses the dedicated A4 print stylesheet.
- [ ] No raw-text Passport export is exposed.
- [ ] No episode page or episode template exposes a source-PDF download link.
- [ ] `episodes.json` contains no public `pdf` field.
- [ ] Every episode loads `assets/passport-cleanup.js` as a defensive safeguard against stale/legacy export controls.
- [ ] Mobile Passport remains readable with no unintended page overflow.

<!-- EPIC-PASSPORT-RULES:END -->
