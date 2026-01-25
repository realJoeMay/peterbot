# Data Stores and Schemas

This document describes the JSON files used as lightweight data stores.

## Locations
- `data/sites.json` — registry of sites (e.g., diocesan sites) to crawl or query.
- `data/jobs.json` — append-only log of job runs with minimal metadata.

## sites.json
Purpose: Configure known sites and key URLs used by jobs.

Structure: A JSON array. Each element is an object describing one site.

Example:
~~~json
[
  {
    "site_id": 1,
    "base_url": "https://diocesefwsb.org",
    "diocese_site": true,
    "diocese": "Diocese of Fort Wayne-South Bend",
    "parishes_page": "https://diocesefwsb.org/find/"
  }
]
~~~

Fields:
- `site_id` (integer, required) — unique identifier for the site.
- `base_url` (string, required) — canonical base URL for the site.
- `diocese_site` (boolean, optional) — helper flag for categorization.
- `diocese` (string, optional) — human-readable name of the diocese.
- `parishes_page` (string, required) — absolute URL to the parishes listing page. Used by jobs like `update_diocese_parishes`.

Notes:
- The code expects `sites.json` to be a list of objects and looks up entries by `site_id`.
- Additional fields are allowed; jobs should read only the keys they need.

## jobs.json
Purpose: Global, append-only ledger of job runs created by `peterbot.jobs.utils.job`.

Structure: A JSON array. Each element is an object representing one job run.

Typical example (recommended shape):
~~~json
[
  {
    "job_id": 5,
    "timestamp": "2025-11-15 07:13:23",
    "records_path": "data/jobs/5",
    "job_description": "Get new links from Diocese parish page."
  }
]
~~~

Fields:
- `job_id` (integer, required) — monotonically increasing identifier assigned at start.
- `timestamp` (string, required) — job start time in `YYYY-MM-DD HH:MM:SS` local time.
- `records_path` (string, required) — filesystem path to the per-job records directory (`data/jobs/<job_id>`). Store as a string in JSON.
- `job_description` (string, optional) — human-friendly description of what the job did.

Notes:
- The helper `start_job()` allocates a new `job_id` and records directory; `end_job()` appends the finalized job object to `jobs.json` and writes `data/jobs/<id>/job.json`.
- When persisting to JSON, ensure all values (e.g., paths) are JSON-serializable strings.
- `jobs.json` is treated as a list; if it ever contained a single object, it is coerced to a one-item list on write.


## Validation and Conventions
- Keep IDs numeric and unique within their file.
- Use absolute URLs for site pages (e.g., `parishes_page`).
- Use UTF‑8 encoding; files are expected to be valid JSON.
- Prefer adding new fields over changing meanings of existing keys; jobs should tolerate extra fields.
