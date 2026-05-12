# Address Enrichment Example

This folder contains a starter pipeline for enriching a CSV or Excel workbook of addresses before cold-calling.

The pipeline can:

- Keep the original address columns.
- Add business/place name, phone, website, Google Maps URL, place type, rating, and status when Google Places is enabled.
- Mark likely government, school, university, landmark/non-business, invalid, and ambiguous rows.
- Return multiple Google Places matches per address for multi-tenant office buildings.
- Cache API responses so retries do not re-query the same addresses.

## Files

- `example_addresses.csv` - sample input data.
- `example_addresses.xlsx` - Excel version of the sample input data.
- `enrich_addresses.py` - enrichment pipeline.
- `address_enrichment_app.py` - desktop GUI wrapper for users who should not run commands.
- `PACKAGING.md` - instructions for creating standalone executables for users without Python.
- `requirements.txt` - Python package needed for Excel `.xlsx` input/output.
- `.cache/places_cache.json` - API response cache, created when the script runs.

## No-Python User App

For users whose computer setup is unknown, package the desktop app into a standalone executable. See `PACKAGING.md`.

During development, you can launch the GUI with:

```bash
/Users/nkasturi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 address_enrichment_app.py
```

The packaged app lets a user:

- Choose an Excel or CSV input file.
- Choose an output Excel or CSV file.
- Paste and save the Google Places API key.
- Run exact or expanded enrichment without opening a terminal.

## Quick Offline Run

This runs without an API key. It only uses the address/source text heuristics, so phone and website columns will be blank.

```bash
python3 enrich_addresses.py \
  --input example_addresses.csv \
  --output enriched_addresses.csv \
  --provider heuristic
```

## Excel Run

Excel files require `openpyxl`.

If you use your own Python:

```bash
python3 -m pip install -r requirements.txt
```

On this machine, the bundled Python already has the Excel dependency installed:

```bash
/Users/nkasturi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 enrich_addresses.py \
  --input example_addresses.xlsx \
  --output enriched_addresses.xlsx \
  --provider heuristic
```

## Google Places Enrichment

Use this when you want business names, phone numbers, websites, place IDs, ratings, and Google Maps URLs.

Create a local `.env` file first:

```bash
cp .env.example .env
```

Then edit `.env` and replace the placeholder:

```bash
GOOGLE_PLACES_API_KEY=your-api-key
```

The `.env` file is ignored by git.

```bash
python3 enrich_addresses.py \
  --input example_addresses.csv \
  --output enriched_addresses.csv \
  --provider google \
  --field-preset contact \
  --max-results 1 \
  --cache .cache/places_cache.json \
  --sleep 0.1
```

For multi-tenant buildings, ask for more than one result:

```bash
python3 enrich_addresses.py \
  --input example_addresses.xlsx \
  --output enriched_addresses.xlsx \
  --provider google \
  --field-preset contact \
  --max-results 5 \
  --search-strategy expanded \
  --limit 25
```

`--search-strategy expanded` is useful for office buildings and other multi-tenant addresses. It costs more API calls because the script tries address variants such as "business at {address}" and "tenants at {address}".

For a real 2,000-row file, run a small test first:

```bash
python3 enrich_addresses.py \
  --input your_addresses.csv \
  --output test_enriched_addresses.csv \
  --provider google \
  --field-preset basic \
  --limit 25
```

Then run the full file after checking the output quality.

## Troubleshooting 403 Forbidden

Run the cheapest Google request first:

```bash
python3 enrich_addresses.py \
  --input example_addresses.csv \
  --output google_basic_test.csv \
  --provider google \
  --field-preset basic \
  --limit 1
```

If `basic` also returns 403, check the Google Cloud project:

- Billing is enabled for the project that owns the API key.
- Places API (New) is enabled.
- API key restrictions allow the Places API.
- Application restrictions match this usage. For this local script, HTTP referrer browser restrictions will fail; use no application restriction during testing or an appropriate server/IP restriction.

If `basic` works but `contact` returns 403, the key/project can call Places, but the requested contact fields are the issue. The `contact` preset asks for phone, website, rating, and rating count, which use higher Places Text Search billing tiers.

The script writes the Google error body into the output `notes` column for `api_error` rows. API errors are not cached, so you can fix the key/project settings and rerun without clearing the cache.

## Expected Input Columns

The script requires an `address` column. These optional columns improve search quality:

- `city`
- `state`
- `postal_code`
- `source_notes`

Extra columns are preserved in the output.

## Output Columns

The script appends these enrichment columns:

- `business_name`
- `normalized_address`
- `category`
- `do_not_call`
- `exclude_reason`
- `phone`
- `international_phone`
- `website`
- `google_maps_url`
- `google_place_id`
- `google_business_status`
- `google_primary_type`
- `google_types`
- `rating`
- `rating_count`
- `confidence`
- `enrichment_status`
- `source_provider`
- `source_url`
- `notes`
- `address_match`
- `query_used`
- `match_rank`

## Review Guidance

Rows with `do_not_call=TRUE` should usually be removed from cold-calling lists. Rows with `category=ambiguous`, `invalid_or_unmatched`, or low `confidence` should be manually reviewed before use.
