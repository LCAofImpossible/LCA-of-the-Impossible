# LCA of the Impossible

Static GitHub Pages archive for the **LCA of the Impossible** series.

## Canonical structure

- `index.html` — homepage and episode archive
- `episodes/` — individual episode pages and reusable episode template
- `assets/style.css` — global visual system
- `assets/images/episodes/` — canonical episode covers
- `assets/images/episode-graphics/` — editorial inventory, technical and hotspot graphics
- `assets/images/book/` — book artwork
- `assets/pdf/episodes/` — downloadable episode carousels

## Episode asset convention

Each episode uses one canonical cover plus three standard editorial graphics:

- `epNN-short-slug.ext` — canonical cover
- `epNN-inventory-map.svg` — visual map of the main life-cycle inputs
- `epNN-technical-plate.svg` — engineering / reconstruction plate
- `epNN-hotspot-breakdown.svg` — contribution / hotspot graphic

Current canonical covers:

- `ep35-flying-dutchman.jpg`
- `ep36-tower-of-babel.png`
- `ep43-sisyphus.webp`

Use the original source format for covers when it is the most reliable/high-quality web asset. Avoid duplicate `live`, `v2` or ad-hoc `hq` filenames.

## Editorial graphic system

All episode graphics follow the same visual language: deep navy background, cream typography, restrained bronze-gold technical linework, blueprint geometry and minimal dashboard styling. The graphics complement — rather than replace — the auditable inventory table and result cards.

The standard sequence is:

1. cover and subject framing;
2. quick facts;
3. **Inventory Map + Technical Plate**;
4. detailed life-cycle inventory;
5. **Hotspot Breakdown**;
6. results, sensitivities and verdict.

`episodes/template.html` is the canonical starting point for all future episodes.

## Page path convention

- From `index.html`: `assets/images/...`
- From files inside `episodes/`: `../assets/images/...`

## Publishing workflow

For each new episode, update the canonical cover, create the three editorial graphics, build the page from the standard template, add the downloadable PDF when available, update the homepage card, and verify the GitHub Pages deployment and live asset paths in one controlled release.
