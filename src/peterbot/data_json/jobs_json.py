import json
from pathlib import Path


def save_job(job: dict, jobs_path: Path):

    # Load existing jobs data, handling empty or invalid JSON
    data = None
    if jobs_path.exists() and jobs_path.stat().st_size > 0:
        try:
            with jobs_path.open("r", encoding="utf-8") as f:
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

    with jobs_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return


def max_job_id(jobs_path: Path):
    """Return the maximum job_id found in the jobs file.
    Supports list of job dicts, dict with 'jobs' list, or id->job mapping.
    Returns 0 if no jobs found or file missing/invalid.
    """

    try:
        if not jobs_path.exists() or jobs_path.stat().st_size == 0:
            return 0
        with jobs_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0

    ids = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "job_id" in item:
                try:
                    ids.append(int(item["job_id"]))
                except Exception:
                    pass
    elif isinstance(data, dict):
        if "jobs" in data and isinstance(data["jobs"], list):
            for item in data["jobs"]:
                if isinstance(item, dict) and "job_id" in item:
                    try:
                        ids.append(int(item["job_id"]))
                    except Exception:
                        pass
        else:
            # Try mapping keys or values
            for k, v in data.items():
                # Numeric key
                try:
                    ids.append(int(k))
                    continue
                except Exception:
                    pass
                # Or nested job object
                if isinstance(v, dict) and "job_id" in v:
                    try:
                        ids.append(int(v["job_id"]))
                    except Exception:
                        pass
    return max(ids) if ids else 0
