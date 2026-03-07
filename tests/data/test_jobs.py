from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from peterbot.data.collections import jobs


# -----------------
# Fixtures
# -----------------
@pytest.fixture
def mock_collection(monkeypatch):
    """
    Replace the `_jobs` collection with a MagicMock.
    """
    mock = MagicMock()
    monkeypatch.setattr(jobs, "_jobs", mock)
    return mock


# -----------------
# Create
# -----------------
def test_create_job_sanitizes_path_and_returns_id(mock_collection):
    inserted_id = ObjectId()
    mock_collection.insert_one.return_value = SimpleNamespace(inserted_id=inserted_id)

    job = {
        "job_index": 1,
        "records_path": Path("data/jobs/1"),
    }

    result = jobs.create_job(job)

    assert result == str(inserted_id)

    mock_collection.insert_one.assert_called_once()
    inserted_doc = mock_collection.insert_one.call_args[0][0]

    assert inserted_doc["records_path"] == "data/jobs/1"


# -----------------
# Read
# -----------------
def test_get_job_by_id(mock_collection):
    job_id = ObjectId()
    expected = {"_id": job_id, "job_index": 1}

    mock_collection.find_one.return_value = expected

    result = jobs.get_job(str(job_id))

    assert result == expected
    mock_collection.find_one.assert_called_once_with({"_id": job_id})


def test_get_job_not_found(mock_collection):
    mock_collection.find_one.return_value = None

    result = jobs.get_job(str(ObjectId()))

    assert result is None


def test_list_jobs(mock_collection):
    docs = [{"job_index": 1}, {"job_index": 2}]
    mock_collection.find.return_value.skip.return_value.limit.return_value = docs

    result = jobs.list_jobs()

    assert result == docs
    mock_collection.find.assert_called_once_with({})


# -----------------
# Update
# -----------------
def test_update_job_success(mock_collection):
    mock_collection.update_one.return_value = SimpleNamespace(modified_count=1)

    job_id = ObjectId()
    updates = {"records_path": Path("data/jobs/1")}

    result = jobs.update_job(str(job_id), updates)

    assert result is True

    _, update_doc = mock_collection.update_one.call_args[0]
    assert update_doc["$set"]["records_path"] == "data/jobs/1"


def test_update_job_no_change(mock_collection):
    mock_collection.update_one.return_value = SimpleNamespace(modified_count=0)

    result = jobs.update_job(str(ObjectId()), {"status": "running"})

    assert result is False


# -----------------
# Delete
# -----------------
def test_delete_job_success(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)

    result = jobs.delete_job(str(ObjectId()))

    assert result is True


def test_delete_job_not_found(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=0)

    result = jobs.delete_job(str(ObjectId()))

    assert result is False


def test_delete_job_by_index_success(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)

    result = jobs.delete_job_by_index(3)

    assert result is True
    mock_collection.delete_one.assert_called_once_with({"job_index": 3})


def test_delete_job_by_index_not_found(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=0)

    result = jobs.delete_job_by_index(999)

    assert result is False


# -----------------
# Business Logic
# -----------------
def test_get_max_job_index(mock_collection):
    mock_collection.find_one.return_value = {"job_index": 42}

    result = jobs.get_max_job_index()

    assert result == 42
    mock_collection.find_one.assert_called_once()


def test_get_max_job_index_empty_collection(mock_collection):
    mock_collection.find_one.return_value = None

    result = jobs.get_max_job_index()

    assert result == 0
