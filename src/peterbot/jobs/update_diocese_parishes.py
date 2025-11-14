from pathlib import Path
from urllib.parse import urljoin

from peterbot.jobs.utils import job
from peterbot.jobs.utils import download
from peterbot.data import sites_db_json


def run(data_dir: Path, diocese_site_id: int) -> None:

    # start job
    job_id, records_path = job.start_job(data_dir)

    # download page
    site_json = data_dir / "sites.json"
    site_info = sites_db_json.get_site_info(diocese_site_id, site_json)
    # base_url = site_info["base_url"]

    url = urljoin(site_info["base_url"], site_info["parishes_page_path"])
    # url = "https://example.com"

    downloads_path = records_path / "html"
    html_path = downloads_path / "index.html"
    download.page_html(url, html_path)

    # job meta
    job_data = dict()
    job_data["job_id"] = job_id
    job_data["job_description"] = "Get new links from Diocese's parish page."

    # end job
    job.end_job(job_data, data_dir)
