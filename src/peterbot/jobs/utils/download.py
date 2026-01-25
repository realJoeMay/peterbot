"""HTTP download utilities for job code."""

from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from requests.adapters import HTTPAdapter, Retry


def page_html(url: str, file_path: Path) -> None:
    """Download a page's HTML and write it to a local file.

    Automatically retries on transient network errors and creates parent
    directories if they do not exist. Uses a connect/read timeout tuple
    to avoid hanging connections.

    Args:
        url: URL of the web page to download.
        file_path: Destination path for the HTML content. Parent directories
            are created automatically if missing.

    Returns:
        None. Writes the HTML to `file_path` encoded as UTF-8.

    Raises:
        requests.HTTPError: If the response has an unsuccessful status.
        requests.RequestException: For other network-related errors.
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


def url_to_path(url: str) -> Path:
    """Convert a URL into a firectory path.

    Convert a URL into a pathlib.Path, where:
      - The top folder is the URL's netloc (domain).
      - Each layer in the URL path becomes a subfolder.
      - The file path preserves the hierarchical structure.

    Examples:
        >>> url_to_path("https://example.com/a/b/c.html")
        Path('https_example.com/a/b/c.html')

        >>> url_to_path("https://example.com/dir/subdir/")
        Path('https_example.com/dir/subdir/index.html')

    Args:
        url: A full or partial URL string.

    Returns:
        A pathlib.Path representing the URL's storage path.
    """
    parsed = urlparse(url)
    base_url_folder = f"{parsed.scheme}_{parsed.netloc}"
    path = unquote(parsed.path).lstrip("/")

    # If the URL ends with a slash or has no path, default to index.html
    if not path or path.endswith("/"):
        path = f"{path}index.html"

    return Path(base_url_folder) / Path(path)
