
"""Expand a public-source organization and person directory.

Wikidata classifications are discovery leads, not verification of
criminal activity, affiliations, or current operational status.
No relationships are created or modified.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "master_network.json"

CLASSES = {
    "Q275186": "Gang",
    "Q1788992": "Criminal organization",
    "Q4335775": "Organized crime group",
    "Q5308925": "Drug trafficking organization",
    "Q21234891": "Mexican cartel",
    "Q18550": "Mafia",
    "Q1849110": "Outlaw motorcycle club",
}

PERSON_OCCUPATIONS = {
    "Q2429253": "Gangster",
    "Q1254956": "Drug lord",
}

QUERY_ENDPOINT = "https://query.wikidata.org/sparql"

HEADERS = {
    "User-Agent": (
        "CartelNetworkTracker/4.0 "
        "(public research project; contact via GitHub repository issues)"
    ),
    "Accept": "application/sparql-results+json",
}

MAX_ATTEMPTS = 2
REQUEST_DELAY = 65


def fetch(query):
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
    })

    request = urllib.request.Request(
        QUERY_ENDPOINT + "?" + params,
        headers=HEADERS,
    )

    for attempt in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)["results"]["bindings"]

        except urllib.error.HTTPError as error:
            if error.code in (429, 503):
                print(
                    f"NOTICE: Wikidata unavailable (HTTP {error.code})."
                )
                raise

            if attempt == MAX_ATTEMPTS - 1:
                raise

        except Exception:
            if attempt == MAX_ATTEMPTS - 1:
                raise

        time.sleep(10)

    return []


def query_class(qid, person=False):
    predicate = "wdt:P106" if person else "wdt:P31/wdt:P279*"

    geographic = (
        "?item wdt:P27 ?country ."
        if person
        else """
        {
          ?item wdt:P17 ?country .
        }
        UNION
        {
          ?item wdt:P131/wdt:P17 ?country .
        }
        UNION
        {
          ?item wdt:P495 ?country .
        }
        """
    )

    return f"""
    SELECT DISTINCT ?item ?itemLabel ?description ?country WHERE {{
        ?item {predicate} wd:{qid} .
        {geographic}
        VALUES ?country {{ wd:Q96 wd:Q30 }}

        OPTIONAL {{
            ?item schema:description ?description .
            FILTER(LANG(?description) = "en")
        }}

        SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en,es".
        }}
    }}
    LIMIT 500
    """


def main():
    if not DEST.exists():
        raise FileNotFoundError(
            f"Missing master network dataset: {DEST}"
        )

    obj = json.loads(DEST.read_text(encoding="utf-8"))

    if not isinstance(obj.get("nodes"), list):
        raise ValueError("master_network.json has no nodes array")

    old = {node["id"]: node for node in obj["nodes"]}

    results = {}
    failures = []
    processed = 0

    categories = list(CLASSES.items()) + list(
        PERSON_OCCUPATIONS.items()
    )

    print(f"Existing network nodes: {len(old)}")

    for qid, category in categories:
        person = qid in PERSON_OCCUPATIONS

        print(f"Searching {category} ({qid})...", flush=True)

        try:
            rows = fetch(query_class(qid, person))
            processed += 1

            print(f"  Retrieved {len(rows)} rows", flush=True)

            for row in rows:
                uri = row.get("item", {}).get("value", "")
                ident = uri.rsplit("/", 1)[-1]

                if not (
                    ident.startswith("Q")
                    and ident[1:].isdigit()
                ):
                    continue

                name = row.get("itemLabel", {}).get(
                    "value", ident
                )

                if name == ident:
                    continue

                country_uri = row.get("country", {}).get(
                    "value", ""
                )

                country = country_uri.rsplit("/", 1)[-1]

                if country not in ("Q96", "Q30"):
                    continue

                key = "wd_" + ident

                region = (
                    "Mexico" if country == "Q96"
                    else "United States"
                )

                if key in results:
                    if region not in results[key]["regions"]:
                        results[key]["regions"].append(region)
                    continue

                results[key] = {
                    "id": key,
                    "name": name,
                    "tier": (
                        "Person — " + category
                        if person else category
                    ),
                    "entity_type": (
                        "person" if person else "organization"
                    ),
                    "regions": [region],
                    "description": row.get(
                        "description", {}
                    ).get("value", ""),
                    "source_urls": [uri],
                    "verification": (
                        "Unreviewed Wikidata classification; "
                        "not independently verified; "
                        "historical/current status unknown"
                    ),
                    "source_type": "Wikidata",
                    "wikidata_id": ident,
                }

        except Exception as error:
            failures.append(f"{category}: {error}")
            print(
                f"  NOTICE: Skipped {category}: {error}",
                flush=True,
            )

            if isinstance(error, urllib.error.HTTPError):
                if error.code in (429, 503):
                    print(
                        "Stopping requests to respect "
                        "Wikidata rate limits.",
                        flush=True,
                    )
                    break

        time.sleep(REQUEST_DELAY)

    print("\nDISCOVERY SUMMARY")
    print(f"Categories completed: {processed}/{len(categories)}")
    print(f"Unique candidates discovered: {len(results)}")
    print(f"Failed categories: {len(failures)}")

    if failures:
        print(
            "NOTICE: Discovery incomplete. "
            "Existing dataset preserved; no partial import."
        )

        for failure in failures:
            print(f"  - {failure}")

        return

    added = 0
    skipped = 0

    for key, node in results.items():
        if key in old:
            skipped += 1
            continue

        old[key] = node
        added += 1

    print(f"New records added: {added}")
    print(f"Existing records skipped: {skipped}")

    if added == 0:
        print("No new records. Master dataset unchanged.")
        return

    obj["nodes"] = sorted(
        old.values(),
        key=lambda node: node["name"].casefold(),
    )

    obj.setdefault("metadata", {})[
        "discovery_note"
    ] = (
        "Wikidata candidates are unreviewed. "
        "No relationships or current status inferred."
    )

    DEST.write_text(
        json.dumps(
            obj,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(f"Updated total nodes: {len(obj['nodes'])}")
    print("Master dataset successfully updated.")


if __name__ == "__main__":
    main()
