# File Structure

This document explains the repository layout and where to find or place things when working on .
## Top-level
- README.md — project entry point.
- pyproject.toml — build system, dependencies, and tool configs (pytest, ruff, mypy).
- src/ — application and library code (installed package peterbot).
- tests/ — test suite executed with pytest.
- notebooks/ — exploratory work and runnable notebooks/scripts.
- data/ — input/output data snapshots tracked in the repo (keep small/anon).
- docs/ — developer documentation, including this guide.

## src/ (package code)
Python package code lives under src/peterbot/ so that imports work both in development and when installed.

- src/peterbot/__init__.py — marks the package. Keep exports minimal and explicit.
- src/peterbot/data/ — reserved for packaged data helpers or datasets (currently empty).
- src/peterbot/jobs/ — job definitions and utilities.
  - src/peterbot/jobs/__init__.py — namespace for jobs.
  - src/peterbot/jobs/download_site.py — Scrapy-based site crawler utilities.
    - FullSiteSpider — follows internal links and saves HTML to a local folder.
    - crawl_site(start_url, output_dir, depth_limit) — programmatic entry point to run a crawl.

Import example:
~~~python
from peterbot.jobs.download_site import crawl_site
crawl_site("https://example.org", output_dir="data/jobs", depth_limit=3)
~~~

## notebooks/
- notebooks/jobs.ipynb — analysis or orchestration for job-related workflows.
- notebooks/download_site.py — minimal script that calls crawl_site.
  - Writes output by default under data/jobs (configurable in code).
  - You can change output_dir to keep notebook artifacts under notebooks/.

Tip: When using Jupyter, register the environment kernel so the notebooks use your venv.

## Folder Tree
~~~text
peterbot/
├─ src/
│  └─ peterbot/
│     ├─ __init__.py
│     ├─ data/
│     │  └─ __init__.py
│     └─ jobs/
│        ├─ __init__.py
│        └─ download_site.py
├─ notebooks/
│  ├─ jobs.ipynb
│  └─ download_site.py
├─ data/
│  └─ jobs.json
├─ docs/
│  ├─ 00_getting_started.md
│  └─ 01_file_structure.md
├─ tests/
│  └─ test_sanity.py
├─ pyproject.toml
├─ README.md
└─ .vscode/
   └─ settings.json
~~~
