from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List
from bs4 import BeautifulSoup
import csv

from peterbot.data import sites_db_json
from peterbot.jobs.utils import download, job


def run(data_dir: Path, diocese_site_id: int) -> None:
    """Run the job to fetch and archive a Diocese's parish page.

    Workflow:
    1) Allocate a new job ID and records directory under `data_dir/jobs/`.
    2) Load site configuration from `data_dir/sites.json` using `diocese_site_id`.
    3) Build the parish page URL from `parishes_page`.
    4) Download the page HTML under job downloads.
    5) Save basic job metadata and update the global jobs database.

    Args:
        data_dir: Root data directory containing `sites.json`, `jobs.json`, and
            the `jobs/` subdirectory where per-job artifacts are stored.
        diocese_site_id: Identifier used to look up the Diocese configuration in
            `sites.json`.

    Raises:
        FileNotFoundError: If `sites.json` is missing.
        json.JSONDecodeError: If `sites.json` is not valid JSON.
        ValueError: If no site with `diocese_site_id` exists or structure is invalid.
        requests.RequestException: If the page download fails due to network issues.
        requests.HTTPError: If the HTTP response indicates an error status.
        OSError: If writing job artifacts to disk fails.

    Returns:
        None. Side effects include creating a new job folder and writing
        artifacts/metadata as described above.
    """
    job_data = job.start_job(data_dir)

    # get download url
    site_json = data_dir / "sites.json"
    site_info = sites_db_json.get_site_info(diocese_site_id, site_json)
    url = site_info["parishes_page"]

    # download page
    downloads_dir = job_data["records_path"] / "downloads"
    html_path = downloads_dir / download.url_to_path(url)
    download.page_html(url, html_path)

    # map all external links
    links_map = map_links(downloads_dir)

    # save unique links to CSV
    unique_links = list({link for links in links_map.values() for link in links})
    csv_path = job_data["records_path"] / "external_links.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for value in unique_links:
            writer.writerow([value])

    # end job
    job.end_job(job_data)


def map_links(downloads_dir: Path) -> dict[str, list[str]]:

    links_map = {}
    for item in downloads_dir.iterdir():
        base_url_folder = item.name
        print(base_url_folder)
        for file_path in item.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() == ".html":
                print(file_path)
                url = path_to_url(file_path, base_url_folder)
                print(url)
                links_map[url] = get_external_links(file_path, base_url_folder)

    return links_map


def get_external_links(html_file: Path, base_url_folder: str) -> List[str]:
    """Extract all external links from an HTML file.

    A link is considered external if its domain does NOT match base_url.

    Args:
        html_file: Path to the .html file to analyze.
        base_url: The base URL (e.g., 'https://diocesefwsb.org').

    Returns:
        A list of external URLs found in the page.
    """
    # Read HTML
    html = html_file.read_text(encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")

    # Normalize base domain
    scheme, netloc = base_url_folder.split("_", 1)
    base_url = f"{scheme}://{netloc}/"
    base_domain = urlparse(base_url).netloc

    external_links = []

    for tag in soup.find_all("a", href=True):
        href = str(tag["href"])

        # Convert relative URL → absolute URL
        full_url = urljoin(base_domain, href)

        parsed = urlparse(full_url)
        domain = parsed.netloc

        # Skip non-http(s) links entirely
        if parsed.scheme not in ("http", "https"):
            continue

        # External = domain does not match the base domain
        if domain and domain.lower() != base_domain.lower():
            external_links.append(full_url)

    return external_links


def path_to_url(file_path: Path, base_url_folder: str) -> str:
    """Reconstructs URL from path to a mirrored HTML file.

    Example:
        file_path = Path(".../downloads/diocesefwsb.org/find/index.html")
        base_url_folder = "https_diocesefwsb.org"
        → "https://diocesefwsb.org/find/"
    """
    parts = list(file_path.parts)

    # Find the domain in the path
    try:
        domain_index = parts.index(base_url_folder)
    except ValueError:
        raise ValueError(f"'{base_url_folder}' not found in path: {file_path}")

    # Extract the path *after* the domain
    rel_parts = parts[domain_index + 1 :]

    # If last part is index.html → it's a directory URL
    if rel_parts and rel_parts[-1] == "index.html":
        rel_parts = rel_parts[:-1]  # remove index.html
        rel_url = "/".join(rel_parts) + "/" if rel_parts else ""
    else:
        rel_url = "/".join(rel_parts)

    scheme, netloc = base_url_folder.split("_", 1)
    return f"{scheme}://{netloc}/{rel_url}"
