[README.md](https://github.com/user-attachments/files/33928541/README.md)
# Faction Network Tracker v2 — Map-first public view

GitHub Pages static dashboard. No public admin/settings/import/export/CRUD controls. The public site displays a searchable graph, read-only inspector, source links, and event markers.

## Upgrade an existing repository

Upload the contents of this folder **into the root** of your existing repository, replacing `index.html`, `app.js`, `styles.css`, `data/master_network.json`, and `README.md`. Keep `.github/workflows/` and `scripts/` in place. Commit to `main`; the existing Pages workflow deploys the update. Do not create a new repository.

## Admin publishing

Edit `data/master_network.json` on GitHub using the repository's normal access controls, ideally through a pull request. No credentials are embedded in the public site. The existing Wikidata refresh workflow opens review pull requests; it does not publish new network relationships.

## Data quality

This directory includes 20 publicly named entities (the original four plus 16 additions). Wikipedia links are entity references, not evidence of current activity, control, or specific relationships. The original three links remain explicitly illustrative and unverified. The timeline is an event-marker view, not historical state reconstruction. Check every source before treating a claim as factual.

## Cost

GitHub Pages and Actions on eligible free public repositories; usage limits and GitHub policies apply. D3 loads from a free public CDN.
