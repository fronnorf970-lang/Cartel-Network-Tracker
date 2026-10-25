
name: Clean Directory PR 2

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  cleanup:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout candidate branch
        uses: actions/checkout@v4
        with:
          ref: wikidata-directory-candidates
          persist-credentials: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Download cleanup and validator
        run: |
          curl --fail --location --silent --show-error \
            https://raw.githubusercontent.com/fronnorf970-lang/Cartel-Network-Tracker/main/scripts/cleanup_directory.py \
            --output /tmp/cleanup_directory.py

          curl --fail --location --silent --show-error \
            https://raw.githubusercontent.com/fronnorf970-lang/Cartel-Network-Tracker/main/scripts/validate_directory.py \
            --output /tmp/validate_directory.py

      - name: Clean candidate directory
        run: |
          python /tmp/cleanup_directory.py

      - name: Validate cleaned directory
        run: |
          python /tmp/validate_directory.py \
            data/master_network.json \
            --report directory_validation_report.json

      - name: Verify expected results
        run: |
          python - <<'PY'
          import json
          from pathlib import Path

          report = json.loads(
              Path("directory_validation_report.json").read_text()
          )
          summary = report["summary"]

          assert summary["nodes"] == 226, summary
          assert summary["imported_wikidata_nodes"] == 206, summary
          assert summary["links"] == 3, summary
          assert summary["errors"] == 0, summary

          print("Cleanup verification passed.")
          PY

      - name: Save cleaned directory to PR branch
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add data/master_network.json

          if git diff --cached --quiet; then
            echo "No changes to commit."
          else
            git commit -m "Clean Wikidata directory candidates"
            git push origin HEAD:wikidata-directory-candidates
          fi

      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: cleaned-directory-validation
          path: directory_validation_report.json
          if-no-files-found: ignore
