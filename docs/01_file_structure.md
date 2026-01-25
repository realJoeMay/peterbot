# File Structure

This document explains the repository layout and where to find or place things when working on.

## Overview
~~~text
peterbot/
├─ src/               # application and library code (installed package peterbot).
│  └─ peterbot/
├─ notebooks/         # exploratory work and runnable notebooks/scripts.
├─ data/              # input/output data snapshots tracked in the repo
├─ docs/              # developer documentation, including this guide.
├─ tests/             # test suite executed with pytest.
├─ pyproject.toml     # build system, dependencies, and tool configs.
└─ README.md          # project entry point.
~~~

## src/ (package code)
Python package code lives under src/peterbot/ so that imports work both in development and when installed.

- src/peterbot/data/ — reserved for packaged data helpers or datasets (currently empty).
- src/peterbot/jobs/ — job definitions and utilities.

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

