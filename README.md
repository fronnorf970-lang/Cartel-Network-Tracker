[README.md](https://github.com/user-attachments/files/33928910/README.md)
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

## Expanding the directory (v3)

Run **Actions → Expand public-source directory → Run workflow**. This queries Wikidata
for selected organized-crime organization classes and two explicitly categorized
person occupations, scoped to Mexico and the United States, and proposes a **pull
request**. Review candidates before merging. The directory is not exhaustive:
Wikidata has incomplete and sometimes incorrect classifications, many organizations
lack country properties, and the query service has limits. Re-run after updating
categories or manually add sourced entities in `data/master_network.json`.

**Important:** A Wikidata occupation or organization label is a third-party
classification, not proof of criminal conduct, present activity, leadership,
location, or association. No person-to-organization edges are inferred, and no
real-time locations, routes or operational details are collected.

If GitHub Actions cannot open PRs, enable **Settings → Actions → General → Workflow
permissions → Read and write** and **Allow GitHub Actions to create pull requests**.
