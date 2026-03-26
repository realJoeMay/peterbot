"""Test job implementation for peterbot.

This module demonstrates a minimal job lifecycle:
- allocate a new job id and records directory
- create a simple artifact under that directory
"""

import logging
from pathlib import Path

from peterbot.jobs.utils import job

logger = logging.getLogger(__name__)


def run(data_path: Path | None = None) -> None:
    """Run the test job.

    Parameters:
    - data_path: Base directory for all job data, containing `jobs.json` and
      the `jobs/` subdirectory for per-job records.
    """
    logger.info("Starting test job")
    job_data = job.start_job(data_path)

    try:
        records_path = job_data["records_path"]
        artifact_file = records_path / "artifact.txt"
        artifact_file.write_text("This is a job artifact.", encoding="utf-8")
        job_data["result"] = "success"
        logger.info(
            "Test job tasks finished",
            extra={
                "job_index": job_data.get("job_index"),
                "db_id": job_data.get("_id"),
                "artifact": str(artifact_file),
            },
        )

    except Exception as e:
        job_data["result"] = "error"
        job_data["error"] = str(e)
        logger.exception(
            "Test job failed",
            extra={
                "job_index": job_data.get("job_index"),
                "db_id": job_data.get("_id"),
            },
        )

    finally:
        job.end_job(job_data)
        logger.info(
            "Completed test job",
            extra={
                "job_index": job_data.get("job_index"),
                "db_id": job_data.get("_id"),
                "result": job_data.get("result"),
            },
        )
