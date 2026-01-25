"""Common helpers for job lifecycle and paths.

This module provides utilities to:
- Allocate a new job identifier and ensure the corresponding records directory
  exists on disk.
- Persist finalized job metadata both to the global jobs database and into the
  per-job records directory.
- Resolve canonical paths for the global jobs JSON file and per-job folders.
"""

import json
from datetime import datetime
from pathlib import Path

from peterbot.data import jobs_db_json


def start_job(data_path: Path) -> dict:
    """Start a new job and create its records directory.

    Args:
        data_path: Root data directory that contains `jobs.json` and the
            `jobs/` subdirectory.

    Returns:
        A dictionary containing:
        - `job_id`: The newly allocated integer identifier.
        - `timestamp`: The creation timestamp for this job.
        - `records_path`: The directory for this job's artifacts.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job_id = jobs_db_json.max_job_id(_jobs_json_path(data_path)) + 1
    records_path = _get_job_records_path(data_path, job_id)
    records_path.mkdir(parents=True, exist_ok=True)

    return {
        "job_id": job_id,
        "timestamp": timestamp,
        "records_path": records_path,
    }


def end_job(job_data: dict, data_path: Path) -> None:
    """Persist job metadata to the global DB and per-job file.

    Args:
        job_data: Final job metadata, including at least a numeric `job_id`.
        data_path: Root data directory that contains `jobs.json` and `jobs/`.

    Raises:
        OSError: If reading or writing job files fails.
        TypeError: If the jobs database contains an incompatible structure.
    """
    # save to jobs json db
    jobs_db_json.save_job(job_data, _jobs_json_path(data_path))

    # when to use path vs dir?
    # isn't recordspath in the job data?
    job_id = job_data["job_id"]
    records_path = _get_job_records_path(data_path, job_id)
    job_json_path = records_path / "job.json"

    # save to job records
    with job_json_path.open("w", encoding="utf-8") as f:
        json.dump(job_data, f, cls=PathEncoder, indent=2, ensure_ascii=False)


def _jobs_json_path(data_path: Path) -> Path:
    """Return the canonical path to the global `jobs.json` file.

    Args:
        data_path: Root data directory for job state.

    Returns:
        The full path to `jobs.json` under `data_path`.
    """
    return data_path / "jobs.json"


def _get_job_records_path(data_path: Path, job_id: int) -> Path:
    """Return the per-job records directory path.

    Args:
        data_path: Root data directory for job state.
        job_id: Integer job identifier.

    Returns:
        The path to the `data_path/jobs/<job_id>` directory.
    """
    return data_path / "jobs" / str(job_id)


class PathEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Path):
            return str(o)
        return super().default(o)
