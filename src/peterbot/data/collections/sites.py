"""
sites.py

CRUD operations for the `sites` MongoDB collection.
"""

from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from peterbot.data.mongo import get_collection
from peterbot.data.collections.utils import sanitize_doc

# Collection handle
_sites = get_collection("sites")


# -----------------
# Create
# -----------------
def create_site(site: Dict[str, Any]) -> str:
    """
    Insert a new site document.

    Args:
        site (dict): Site data to insert

    Returns:
        str: Inserted document ID as a string
    """
    site = sanitize_doc(site)
    result: InsertOneResult = _sites.insert_one(site)
    return str(result.inserted_id)


# -----------------
# Read
# -----------------
def get_site(site_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single site by ID.
    Args:
        site_id (str): MongoDB ObjectId as a string

    Returns:
        dict | None: Site document if found, else None
    """
    return _sites.find_one({"_id": ObjectId(site_id)})


def list_sites(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    skip: int = 0,
) -> List[Dict[str, Any]]:
    """
    List sites with optional filtering and pagination.

    Args:
        filters (dict, optional): MongoDB query filters
        limit (int): Max number of results
        skip (int): Number of documents to skip

    Returns:
        list[dict]: List of site documents
    """
    cursor = _sites.find(filters or {}).skip(skip).limit(limit)
    return list(cursor)


# -----------------
# Update
# -----------------
def update_site(site_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update fields on an existing site.
    Args:
        site_id (str): MongoDB ObjectId as a string
        updates (dict): Fields to update

    Returns:
        bool: True if a document was modified
    """
    updates = sanitize_doc(updates)
    result: UpdateResult = _sites.update_one(
        {"_id": ObjectId(site_id)},
        {"$set": updates},
    )
    return result.modified_count == 1


# -----------------
# Delete
# -----------------
def delete_site(site_id: str) -> bool:
    """
    Delete a site by ID.

    Args:
        site_id (str): MongoDB ObjectId as a string

    Returns:
        bool: True if a document was deleted
    """
    result: DeleteResult = _sites.delete_one({"_id": ObjectId(site_id)})
    return result.deleted_count == 1


def delete_site_by_index(job_index: int) -> bool:
    """
    Delete a site by its application-level job index.

    Args:
        job_index (int): Sequential job number

    Returns:
        bool: True if a document was deleted
    """
    result: DeleteResult = _sites.delete_one({"job_index": job_index})
    return result.deleted_count == 1


# -----------------
# Business Logic
# -----------------
def get_max_site_index() -> int:
    """
    Get the maximum jobIndex value in the sites collection.

    Returns:
        int: Highest jobIndex found, or 0 if the collection is empty
    """
    doc = _sites.find_one(
        {},
        sort=[("site_index", -1)],
        projection={"site_index": 1},
    )

    if not doc:
        return 0

    return doc.get("site_index", 0)
