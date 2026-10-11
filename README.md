# Flashscore tennis results to CSV with Python

A standard-library Python example from DataSmithLab. Export a completed [Flashscore Tennis Scraper](https://apify.com/datasmithlab/flashscore-tennis-scraper) dataset to CSV while preserving set scores as JSON in one cell.

[Walkthrough](https://datasmith-lab.github.io/datasmithlab-tennis-csv/) · [Download ZIP](https://github.com/Datasmith-lab/datasmithlab-tennis-csv/releases/latest/download/tennis-results-csv-starter.zip)

## Setup

1. Open the Actor on Apify and use `actor-input.json`: today and yesterday UTC, finished matches, up to 20 rows, optional details off, monitoring off. Use a $0.10 run charge cap for this small example. Current Store prices are authoritative; a run cap is not an all-service cost guarantee.
2. Run the Actor. Verify SUCCEEDED, HEALTH and DAYS before exporting. Confirm the HEALTH item count matches the dataset and there are no failed days or charge-limit truncation.
3. Download the dataset as a JSON array named `dataset.json`.
4. Run with Python 3.10 or newer, no external packages:

```sh
python export_matches.py --input dataset.json --output matches.csv --max-rows 20
```

Alternatively fetch a completed run's dataset directly. Set `APIFY_TOKEN` privately in your terminal environment; never commit it or paste it into the script. Obtain the dataset ID from your own successful Actor run.

```sh
python export_matches.py --dataset-id YOUR_DATASET_ID --output matches.csv --max-rows 20
```

The dataset command reads existing data; it does not launch an Actor or automatically verify that run's HEALTH/DAYS. Read and validate those reports first. Dataset pages are fetched until an empty page or the maximum-row check. Input exceeding the maximum or containing duplicate/missing IDs stops before CSV creation. Existing output files are not overwritten.

## What the CSV contains

Match ID, startTime, status, tour, tournament, surface, singles/doubles, players, score, winner, resultType, sets and source URL. Nested set data remains JSON so tiebreak values are not discarded. Missing fields stay blank. Cells starting with spreadsheet formula characters are escaped for safer spreadsheet import.

On 11 October 2026, one real 20-match run exported 20 unique IDs. CSV IDs and nested set scores matched the JSON; duplicate-input and formula-cell checks passed. This verifies the small sample, not comprehensive tour coverage.

## Scope

The Actor's main lists reach up to seven days back and two ahead in UTC. This is not a historical archive, ranking feed, odds feed or continuous live stream. The default does not request paid statistics, point-by-point or H2H. Optional details need your own input and cost checks. Player names follow Flashscore's short display forms.

Designed for analysts who want a small reproducible results table. The demo contains only synthetic rows. No tokens or customer data are included. Independent of Flashscore/Livesport; no affiliation claimed.
