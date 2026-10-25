# Faction Network Tracker — GitHub Pages

Free static, interactive network research sandbox. **All initial edges are illustrative and unverified.** The app does not claim to provide law-enforcement intelligence, current territory, operational routes, or live alliance data.

## Deploy in GitHub (no terminal or paid service)
1. Create a **public** GitHub repository (GitHub Pages free plan requires public repositories).
2. Upload **all** contents of this project folder to the repository root, including `.github/workflows` and `data`.
3. On GitHub, open **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Open **Actions → Deploy GitHub Pages → Run workflow**, or push to `main`.
5. Open the Pages URL shown in the deployment job. It normally resembles `https://USERNAME.github.io/REPOSITORY/`.

## Features
- D3 force-directed graph: pan, zoom, drag, search, relationship filtering.
- Node inspector: regions, source links, verification flags; add region, delete node.
- Edge inspector: change type, delete relationship.
- Create faction and optional parent splinter connection; add other relationships.
- Sandbox reset and JSON import/export.
- Share sandbox by URL fragment (small graphs only). URL contains the entire scenario and may expose its contents to recipients.
- Timeline markers from `data/timeline_ledger.json`. **Historical state reconstruction is not included until sourced dated state deltas are added**; moving the slider shows event history without falsely presenting unverified past states.
- GitHub-based admin publishing: use the Admin publishing link to edit `data/master_network.json` in GitHub; commit or create a pull request. Only repository users with write permission can publish. GitHub Pages is read-only; no client-side privileged tokens.
- Optional Wikidata metadata sync via Actions; output to `data/wiki_entities.json` and creates a review PR if GitHub Actions has permission. Sync is not an automated merge into the master network.

## Wikidata synchronization
Edit `data/wikidata_ids.json` to add **manually verified** Wikidata entity IDs (e.g. `"Q12345"`); do not guess QIDs. Run **Actions → Refresh Wikidata descriptions → Run workflow**. Review the resulting PR. GitHub repository settings may require enabling Actions to create pull requests. No external Python packages required.

## Editing master data
Edit `data/master_network.json` on GitHub. Every link must reference existing node IDs. Valid relationship types: `Active Conflict`, `Tactical Alliance`, `Splinter Faction`, `Proxy Franchise`, `Neutral / Unknown`. Add `source_urls`, `verification`, and dated event evidence for all published claims. Run `python scripts/validate_network.py` locally or in a CI workflow before publishing.

## Limits and security
- GitHub Pages hosts static files only. Do not embed API secrets or tokens.
- Browser sandbox edits do not affect the master JSON. Changes disappear on reload unless shared/exported.
- Wikipedia/Wikidata is not a reliable real-time source for criminal-group relationships. Review every substantive claim.
- GitHub Actions minutes and Pages bandwidth are subject to GitHub's free-tier limits and policies.
- D3 is loaded from jsDelivr CDN; users need internet access.
- For local development, run `python -m http.server 8000` and visit `http://localhost:8000` (opening `index.html` as a file will not load JSON via fetch).
