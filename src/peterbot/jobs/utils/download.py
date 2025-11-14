from pathlib import Path
import requests
from requests.adapters import HTTPAdapter, Retry


def page_html(url: str, file_path: Path) -> None:
    """
    Download the HTML content of a web page and save it to a local file.

    Automatically retries on transient network errors and creates
    parent directories if they do not exist.

    Args:
        url: The URL of the web page to download.
        file_path: Path to the file where the HTML content will be saved.
            Parent directories are created automatically if they do not exist.

    Raises:
        requests.HTTPError: If the HTTP request returns an unsuccessful status code.
        requests.RequestException: For network-related errors.
    """

    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    response = session.get(url, timeout=(3, 10))
    response.raise_for_status()

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(response.text, encoding="utf-8")
