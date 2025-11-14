# todo - add docstring
import json
from pathlib import Path


def save_job(job: dict, jobs_json: Path):
    """Append a job record to a JSON jobs file.

    Reads the existing file at `jobs_json` if it exists and is non-empty.
    - If the file contains invalid JSON, treats it as empty (i.e., starts fresh).
    - If the existing JSON is a single object (dict), coerces it into a one-item list.
    - Ensures the final stored structure is a list of job objects and appends `job`.

    Parameters:
    - job: A JSON-serializable mapping representing the job to persist.
    - jobs_json: Path to the JSON file that stores a list of jobs.

    Raises:
    - TypeError: If the existing JSON payload is not a list/dict that can be coerced
      into a list of jobs.
    - OSError: If reading or writing the file fails.

    Returns:
    - None
    """

    # Load existing jobs data, handling empty or invalid JSON
    data = None
    if jobs_json.exists() and jobs_json.stat().st_size > 0:
        try:
            with jobs_json.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = None

    if data is None:
        data = []  # default to a list of job objects

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        raise TypeError("jobs data should be a list")

    # Insert the job
    data.append(job)

    with jobs_json.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def max_job_id(jobs_json: Path) -> int:
    """Return the maximum job_id found in the jobs file.

    Returns 0 if no jobs found or file missing/invalid.
    """
    try:
        if not jobs_json.exists() or jobs_json.stat().st_size == 0:
            return 0
        with jobs_json.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return 0

    ids = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "job_id" in item:
                try:
                    ids.append(int(item["job_id"]))
                except (ValueError, TypeError):
                    pass
    elif isinstance(data, dict):
        # Try mapping keys or values
        for k, v in data.items():
            # Numeric key
            try:
                ids.append(int(k))
                continue
            except (ValueError, TypeError):
                pass
            # Or nested job object
            if isinstance(v, dict) and "job_id" in v:
                try:
                    ids.append(int(v["job_id"]))
                except (ValueError, TypeError):
                    pass
    return max(ids) if ids else 0
