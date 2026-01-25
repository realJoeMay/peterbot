"""Test job implementation for peterbot.

This module demonstrates a minimal job lifecycle:
- allocate a new job id and records directory
- create a simple artifact under that directory
"""

from pathlib import Path

from peterbot.jobs.utils import job


def run(data_path: Path) -> None:
    """Run the test job.

    Parameters:
    - data_path: Base directory for all job data, containing `jobs.json` and
      the `jobs/` subdirectory for per-job records.
    """
    job_data = job.start_job(data_path)

    records_path = job_data["records_path"]
    artifact_file = records_path / "artifact.txt"
    artifact_file.write_text("Other data here.", encoding="utf-8")

    job.end_job(job_data, data_path)
