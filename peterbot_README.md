# Peterbot

Peterbot is a Python framework for analyzing Catholic organizations and their websites. New analyses begin in Jupyter notebooks; reusable operations are promoted into tested Python jobs. This document records the planned architecture, not necessarily implemented features.

## Design principles

- Keep notebooks for experimentation, orchestration, visualization, and reporting.
- Separate reusable business operations (`jobs`), generic utilities (`utils`), and persistence (`data`).
- Keep data outside the source repository and avoid machine-specific paths in code.
- Preserve historical HTTP captures and record exactly which captures each analysis used.
- Allow analyses to reuse previous captures without downloading or crawling again.
- Keep the archive format hidden behind a stable `HtmlStore` interface.

## Repository structure

```text
peterbot/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── analysis/
│   ├── 2026-11-01-parish-platforms/
│   │   ├── analysis.ipynb
│   │   └── README.md
│   └── 2026-12-01-parish-ministries/
│       ├── analysis.ipynb
│       └── README.md
├── src/peterbot/
│   ├── __init__.py
│   ├── config.py
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── get_all_parishes.py
│   │   ├── identify_web_platforms.py
│   │   └── crawl_website.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── storage.py
│   │   ├── html_store.py
│   │   └── analysis_runs.py
│   └── utils/
│       ├── __init__.py
│       ├── scrape.py
│       └── llm.py
└── tests/
    ├── jobs/
    ├── data/
    └── utils/
```

Install in editable mode for notebook development: `pip install -e ".[dev]"`.

## External data storage

Configure a data root in `.env` (excluded from Git):

```dotenv
PETERBOT_DATA_DIR=D:/peterbot-data
PETERBOT_WARC_MAX_SIZE_MB=1000
```

```text
peterbot-data/
├── archive/
│   └── warc/
│       ├── 2026-11-01-parish-platforms/
│       │   ├── 000001.warc.gz
│       │   ├── 000002.warc.gz
│       │   └── 000003.warc.gz
│       └── 2026-12-01-parish-ministries/
│           └── 000001.warc.gz
├── analyses/
│   ├── 2026-11-01-parish-platforms/
│   │   └── runs/
│   │       └── run-001/
│   │           ├── manifest.json
│   │           ├── pages.jsonl
│   │           ├── input/
│   │           ├── intermediate/
│   │           └── output/
│   └── 2026-12-01-parish-ministries/
│       └── runs/...
├── index/
│   └── cache.sqlite            # Optional, derived index
└── shared/
    ├── organizations/
    └── sites/
```

- **Archive:** Immutable raw HTTP captures in compressed WARC files, organized by analysis.
- **Analysis runs:** Parameters, capture references, inputs, intermediate results, and outputs for one logical execution.
- **Shared:** Curated reusable datasets, separate from raw captures.
- **Index:** Optional lookup acceleration; not the sole source of truth.

Prefer Parquet for substantial tabular datasets, CSV for interchange, JSON for run metadata, and JSONL for potentially large page inventories.

## WARC archive policy

**Decision:** Use `.warc.gz` as the long-term format for raw HTTP captures. Preserve the original response body and relevant HTTP/WARC headers. Use standard WARC tooling such as `warcio`.

**Decision:** Organize WARC files **by analysis**, not by batch or notebook session. Each analysis has a numbered sequence of archive files. A capture batch may continue writing to the current file, and a large batch may span several files. **Batch boundaries have no effect on archive naming or rotation.**

**Decision:** Rotate WARC files according to a configurable compressed-size target, default **1,000 MB (approximately 1 GB)**. Check the size at record boundaries; an oversized record may cause a file to exceed the target. Record-level gzip compression and byte offsets should support indexed retrieval. Coordinate writers to prevent concurrent append corruption. Once a file is finalized, do not modify it; the active file may be appended to safely across notebook sessions.

Different analyses can reference captures stored under another analysis's WARC directory without copying the content. Archive paths must remain stable; manifests refer to them relative to the archive root.

## HTML storage and acquisition

**Decision:** Cache at the **individual URL/page** level, not the whole-website level. A job may fetch one homepage, selected pages, or an entire site. The HTML store itself is domain-agnostic: it manages URLs and HTTP captures, not parish or diocese entities. Higher-level jobs associate pages with organizations and websites.

- `utils/scrape.py`: HTTP fetching, retries, timeouts, rate limiting, and redirect handling.
- `data/html_store.py`: WARC writing, lookup, retrieval, and cache policies.
- `data/analysis_runs.py`: Run creation, progress, page selections, and provenance.
- `jobs/crawl_website.py`: Link discovery and crawl decisions.
- Analysis jobs: Analyze the retrieved pages without requiring network access.

Retain requested and final URLs, timestamps, status codes, content type, encoding information, ETag/Last-Modified when available, WARC record ID, archive path, and record offset (when indexed). Record failed and missing pages explicitly. Use a documented URL normalization policy while retaining original URLs.

### Cache selection modes

| Mode | Behavior |
| --- | --- |
| `live` | Fetch current content and archive the result. |
| `latest` | Use the latest successful cached capture for a URL; fetch if missing. |
| `analysis` | Replay the exact captures selected by an earlier analysis run; **never** silently fetch or substitute newer pages. |

### Intended Python API (illustrative)

```python
from peterbot.data.html_store import HtmlStore

store = HtmlStore()
page = store.get("https://exampleparish.org", mode="live", analysis_run_id="run-001")
page = store.get("https://exampleparish.org", mode="latest")
page = store.get("https://exampleparish.org", mode="analysis", source_run_id="run-001")

# Replay a previous run's exact recorded page set without recrawling:
pages = store.iter_run_pages("run-001")
```

Run IDs must be globally unique or qualified by analysis ID. The API should expose HTML bytes, optional decoded text, response metadata, and capture provenance. Stream large page collections rather than loading all pages into memory.

## Analysis runs and manifests

An **analysis** is a dated notebook project; a **run** is one logical execution that may span multiple notebook sessions and capture batches. For example, a run can fetch 100 pages, later 100 more, then 4,800 more, while keeping one run identity. WARC rotation is **independent** of these batches and run boundaries.

Each run has:

- `manifest.json`: analysis ID, run ID, schema version, start/end timestamps, status, parameters, source-run references, input/output paths, and (eventually) code revision.
- `pages.jsonl`: the exact intended/selected URL inventory and capture references, including missing or failed URLs. Each record can include requested URL, WARC record ID, relative WARC path, timestamp, status, and optionally compressed offset.

Example `manifest.json`:

```json
{
  "schema_version": 1,
  "analysis_id": "2026-11-01-parish-platforms",
  "run_id": "run-001",
  "status": "completed",
  "parameters": {"scope": "homepage"},
  "html_source": {"mode": "live"},
  "pages_file": "pages.jsonl",
  "outputs": ["output/platforms.parquet"]
}
```

Example `pages.jsonl` (one JSON object per line):

```jsonl
{"requested_url":"https://parish-a.org/","record_id":"urn:uuid:11111111-1111-4111-8111-111111111111","warc_file":"2026-11-01-parish-platforms/000001.warc.gz","status":200}
{"requested_url":"https://parish-b.org/","record_id":"urn:uuid:22222222-2222-4222-8222-222222222222","warc_file":"2026-11-01-parish-platforms/000002.warc.gz","status":200}
```

When analysis 5 reuses captures from analysis 3, its manifest records analysis 3 as the source, **and its own `pages.jsonl` records exactly the subset it actually used**. No HTML is copied. A missing capture remains missing rather than triggering an implicit network request.

Write progress durably as work completes. Finalize the manifest only when the run is complete. Keep manifests and page inventories consistent using atomic updates or coordinated append/recovery mechanisms.

## Index strategy (not yet finalized)

SQLite is **optional**, not an architectural requirement. WARC archives plus durable run manifests/page inventories are the authoritative records. A lightweight JSONL catalog may be sufficient initially; a rebuildable SQLite index is the preferred upgrade for fast URL/latest-capture and WARC-offset lookups. DuckDB/Parquet are more appropriate for analytical datasets than incremental capture indexing. Do not require notebooks to know which index backend is used.

An index should support lookup by normalized URL, fetch timestamp, record ID, analysis/run, WARC path, and offset. Rebuilding the index must not require recapturing websites.

## Job and notebook workflow

Jobs accept explicit inputs and return results; they must not depend on notebook globals. Notebooks orchestrate jobs, inspect outputs, and prototype new capabilities. Promote proven logic into `src/peterbot/jobs/` and add tests. Keep acquisition separate from analysis, while permitting convenience wrappers.

```python
from peterbot.jobs.get_all_parishes import get_all_parishes
from peterbot.jobs.crawl_website import crawl_websites
from peterbot.jobs.identify_web_platforms import identify_web_platforms

parishes = get_all_parishes()
pages = crawl_websites(parishes, max_pages_per_site=100, cache_mode="live")
platforms = identify_web_platforms(pages)
```

For replay, use `store.iter_run_pages(...)` and pass the resulting pages directly to the analysis job. These examples are intended interfaces, not yet implemented code.

## Operational guidelines

- Respect site crawling policies; use rate limits, timeouts, and retry/backoff.
- Keep secrets in `.env`, not notebooks, archives, or manifests.
- Test archive rotation, safe append/restart, interrupted writes, concurrent writers, lookup/replay, and missing-page behavior.
- Back up WARC archives and manifests; retain any capture referenced by a historical run.
- Keep optional indexes rebuildable and establish explicit retention policies before deleting archives.
- Consider browser-rendered capture or ArchiveBox later if analyses require it; do not introduce ArchiveBox initially.
