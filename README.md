# LCA of the Impossible — Website

Static GitHub Pages archive for the **LCA of the Impossible** series.

## Repository structure

```text
/
├── index.html
├── assets/
│   ├── style.css
│   ├── images/
│   │   ├── episodes/
│   │   │   ├── ep35-flying-dutchman.jpg
│   │   │   └── ep36-tower-of-babel.jpg
│   │   └── book/
│   │       └── where-others-see-fantasy.png
│   └── pdf/
│       └── episodes/
│           └── ep36-tower-of-babel.pdf
└── episodes/
    ├── flying-dutchman.html
    ├── tower-of-babel.html
    └── template.html
```

## Conventions for new episodes

- Episode pages: `episodes/<slug>.html`
- Episode covers: `assets/images/episodes/epNN-<slug>.jpg`
- Episode PDFs: `assets/pdf/episodes/epNN-<slug>.pdf`
- Use one canonical cover per episode; do not keep `v2`, `live`, `final`, `hq2` or similar duplicates.
- Update the homepage and the episode page in the same change.
- Verify the GitHub Pages deployment and asset paths after each release.

## Publishing workflow

1. Prepare the episode page from `episodes/template.html`.
2. Add the canonical episode cover and PDF.
3. Add or update the homepage card.
4. Commit the complete episode as one coherent change.
5. Verify the live GitHub Pages deployment.

The website is an independent archive of narrative LCA reconstructions and is not presented as a verified ISO study.
