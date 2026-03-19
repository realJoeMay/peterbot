"""
jobs.py

CRUD operations for the `jobs` MongoDB collection.
"""

from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from peterbot.data.mongo import get_collection
from peterbot.data.collections.utils import sanitize_doc

# Collection handle
_jobs = get_collection("jobs")


# -----------------
# Create
# -----------------
def create_job(job: Dict[str, Any]) -> str:
    """
    Insert a new job document.

    Args:
        job (dict): Job data to insert

    Returns:
        str: Inserted document ID as a string
    """
    job = sanitize_doc(job)
    result: InsertOneResult = _jobs.insert_one(job)
    return str(result.inserted_id)


# -----------------
# Read
# -----------------
def get_job(doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single job by ID.

    Args:
        doc_id (str): MongoDB ObjectId as a string

    Returns:
        dict | None: Job document if found, else None
    """
    return _jobs.find_one({"_id": ObjectId(doc_id)})


def list_jobs(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    skip: int = 0,
) -> List[Dict[str, Any]]:
    """
    List jobs with optional filtering and pagination.

    Args:
        filters (dict, optional): MongoDB query filters
        limit (int): Max number of results
        skip (int): Number of documents to skip

    Returns:
        list[dict]: List of job documents
    """
    cursor = _jobs.find(filters or {}).skip(skip).limit(limit)
    return list(cursor)


# -----------------
# Update
# -----------------
def update_job(job_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update fields on an existing job.

    Args:
        job_id (str): MongoDB ObjectId as a string
        updates (dict): Fields to update

    Returns:
        bool: True if a document was modified
    """
    updates = sanitize_doc(updates)
    result: UpdateResult = _jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": updates},
    )
    return result.modified_count == 1


# -----------------
# Delete
# -----------------
def delete_job(job_id: str) -> bool:
    """
    Delete a job by ID.

    Args:
        job_id (str): MongoDB ObjectId as a string

    Returns:
        bool: True if a document was deleted
    """
    result: DeleteResult = _jobs.delete_one({"_id": ObjectId(job_id)})
    return result.deleted_count == 1


def delete_job_by_index(job_index: int) -> bool:
    """
    Delete a job by its application-level job index.

    Args:
        job_index (int): Sequential job number

    Returns:
        bool: True if a document was deleted
    """
    result: DeleteResult = _jobs.delete_one({"job_index": job_index})
    return result.deleted_count == 1


# -----------------
# Business Logic
# -----------------
def get_max_job_index() -> int:
    """
    Get the maximum jobIndex value in the jobs collection.

    Returns:
        int: Highest jobIndex found, or 0 if the collection is empty
    """
    doc = _jobs.find_one(
        {},
        sort=[("job_index", -1)],
        projection={"job_index": 1},
    )

    if not doc:
        return 0

    return doc.get("job_index", 0)
