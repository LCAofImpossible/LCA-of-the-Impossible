# LCA of the Impossible

Static GitHub Pages archive for the **LCA of the Impossible** series.

## Canonical structure

- `index.html` — homepage and episode archive
- `episodes/` — individual episode pages
- `assets/style.css` — global stylesheet
- `assets/images/episodes/` — canonical episode covers
- `assets/images/book/` — book artwork
- `assets/pdf/episodes/` — downloadable episode carousels

## Episode asset convention

Use one canonical cover per episode with the naming pattern:

`epNN-short-slug.ext`

Current canonical covers:

- `ep35-flying-dutchman.jpg`
- `ep36-tower-of-babel.png`

Use the original source format when it is the most reliable/high-quality web asset. Avoid generating duplicate `live`, `v2`, `hq`, or wrapper files.

## Page path convention

- From `index.html`: `assets/images/...`
- From files inside `episodes/`: `../assets/images/...`

## Publishing workflow

For each new episode, update the cover asset, episode page, homepage card, and downloadable PDF in one controlled change, then verify the GitHub Pages deployment and live asset paths.
