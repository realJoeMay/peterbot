"""Common helpers for job lifecycle and paths."""

import json
from datetime import datetime
from pathlib import Path

from peterbot.data.collections import jobs
from peterbot.data.data_store import get_data_store_dir


def start_job(data_path: Path | None) -> dict:
    """Create and start a new job.

    This function:
    - Determines the next sequential job index
    - Records the job start time
    - Computes and creates a job-specific records directory
    - Persists the job metadata to the database
    - Returns the complete job record, including its database ID

    Args:
        data_path (Path): Root data directory containing the `jobs/`
            subdirectory used for job records storage.

    Returns:
        dict: A dictionary representing the newly created job, including:
            - _id (str): MongoDB document ID for the job
            - job_index (int): Sequential application-level job number
            - start_time (str): Job start timestamp (YYYY-MM-DD HH:MM:SS)
            - records_path (Path): Filesystem path to the job's records directory
            - status (str): Current job status (e.g., "running")
    """

    data_path = data_path or get_data_store_dir()

    job_data = {}
    job_data["job_index"] = jobs.get_max_job_index() + 1
    job_data["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job_data["records_path"] = _get_job_records_path(data_path, job_data["job_index"])
    job_data["status"] = "running"
    job_data["_id"] = jobs.create_job(job_data)

    job_data["records_path"].mkdir(parents=True, exist_ok=True)
    return job_data


def end_job(job_data: dict) -> None:
    """Persist job metadata to the global DB and per-job file.

    Args:
        job_data: Final job metadata, including at least a numeric `job_id`.
        data_path: Root data directory that contains `jobs.json` and `jobs/`.

    Raises:
        OSError: If reading or writing job files fails.
        TypeError: If the jobs database contains an incompatible structure.
    """
    # save to job records
    job_json_path = job_data["records_path"] / "job.json"
    with job_json_path.open("w", encoding="utf-8") as f:
        json.dump(job_data, f, cls=PathEncoder, indent=2, ensure_ascii=False)

    # save updates to jobs db
    job_data["status"] = "completed"
    job_id = job_data.pop("_id")
    jobs.update_job(job_id, job_data)


def _get_job_records_path(data_path: Path, job_id: int) -> Path:
    """Return the per-job records directory path.

    Args:
        data_path: Root data directory for job state.
        job_id: Integer job identifier.

    Returns:
        The path to the `[data_path]/jobs/<job_index>` directory.
    """
    return data_path / "jobs" / str(job_id)


class PathEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Path):
            return str(o)
        return super().default(o)
