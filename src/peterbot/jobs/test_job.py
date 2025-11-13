from pathlib import Path


from peterbot.data_json import jobs_json


def run(data_path: Path):

    # jobs_json_path = data_path / "jobs.json"
    # job_id = jobs_json.max_job_id(jobs_json_path) + 1
    # job_folder_path = data_path / "jobs" / str(job_id)
    # job_folder_path.mkdir(parents=True, exist_ok=True)  # make any parent dirs

    job_id, job_folder_path, jobs_json_path = start_job(data_path)

    artifact_file = job_folder_path / "artifact.txt"
    artifact_file.write_text("Other data here.", encoding="utf-8")

    job_data = {"job_id": job_id, "job": "test_job"}

    jobs_json.save_job(job_data, jobs_json_path)

    return


def start_job(data_path):
    jobs_json_path = data_path / "jobs.json"
    job_id = jobs_json.max_job_id(jobs_json_path) + 1
    job_folder_path = data_path / "jobs" / str(job_id)
    job_folder_path.mkdir(parents=True, exist_ok=True)  # make any parent dirs
    print("starting job")

    return job_id, job_folder_path, jobs_json_path
