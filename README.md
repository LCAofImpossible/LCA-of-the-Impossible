# LCA of the Impossible — Website

Static website starter for GitHub Pages.

## Structure
- `index.html` — homepage and episode archive
- `episodes/` — one HTML page per episode
- `assets/style.css` — shared visual style

## Publish on GitHub Pages
1. Create a public GitHub repository.
2. Upload all files preserving the folders.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select `main` and `/ (root)`.
6. Save.

## Update a new episode
Duplicate one of the files in `episodes/`, change the title/content, then add a new card in `index.html`.

## To customize
Replace all `href="#"` placeholders with:
- LinkedIn episode URL
- PDF/carousel URL
- Payhip book URL
