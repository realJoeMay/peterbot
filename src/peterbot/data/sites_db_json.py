import json
from pathlib import Path
from typing import Any


def get_site_info(site_id: int, site_json: Path) -> dict[str, Any]:
    """
    Read a JSON file containing a list of site dictionaries and return
    the one matching the given site_id.

    Args:
        site_id: The site ID to search for.
        site_json: Path to the JSON file containing a list of site dictionaries.

    Returns:
        The dictionary corresponding to the matching site_id.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        ValueError: If the JSON content is invalid or no matching site_id is found.
    """
    # Read JSON file
    data = json.loads(site_json.read_text(encoding="utf-8"))

    # Validate JSON structure
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Expected a JSON file containing a list of dictionaries.")

    # Search for matching site_id
    for site in data:
        if site.get("site_id") == site_id:
            return site

    # If no match found
    raise ValueError(f"No site found with site_id={site_id}")
