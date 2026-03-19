from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from peterbot.data.collections import sites


# -----------------
# Fixtures
# -----------------
@pytest.fixture
def mock_collection(monkeypatch):
    """
    Replace the `_sites` collection with a MagicMock.
    """
    mock = MagicMock()
    monkeypatch.setattr(sites, "_sites", mock)
    return mock


# -----------------
# Create
# -----------------
def test_create_site_sanitizes_path_and_returns_id(mock_collection):
    inserted_id = ObjectId()
    mock_collection.insert_one.return_value = SimpleNamespace(inserted_id=inserted_id)

    site = {
        "site_id": 1,
        "static_path": Path("data/sites/1"),
    }

    result = sites.create_site(site)

    assert result == str(inserted_id)

    mock_collection.insert_one.assert_called_once()
    inserted_doc = mock_collection.insert_one.call_args[0][0]

    assert inserted_doc["static_path"] == "data/sites/1"


# -----------------
# Read
# -----------------
def test_get_site_by_id(mock_collection):
    site_id = ObjectId()
    expected = {"_id": site_id, "site_id": 1}

    mock_collection.find_one.return_value = expected

    result = sites.get_site(str(site_id))

    assert result == expected
    mock_collection.find_one.assert_called_once_with({"_id": site_id})


def test_get_site_not_found(mock_collection):
    mock_collection.find_one.return_value = None

    result = sites.get_site(str(ObjectId()))

    assert result is None


def test_list_sites(mock_collection):
    docs = [{"site_id": 1}, {"site_id": 2}]
    mock_collection.find.return_value.skip.return_value.limit.return_value = docs

    result = sites.list_sites()

    assert result == docs
    mock_collection.find.assert_called_once_with({})


# -----------------
# Update
# -----------------
def test_update_site_success(mock_collection):
    mock_collection.update_one.return_value = SimpleNamespace(modified_count=1)

    site_id = ObjectId()
    updates = {"parishes_page": Path("/parishes")}

    result = sites.update_site(str(site_id), updates)

    assert result is True

    _, update_doc = mock_collection.update_one.call_args[0]
    assert update_doc["$set"]["parishes_page"] == "/parishes"


def test_update_site_no_change(mock_collection):
    mock_collection.update_one.return_value = SimpleNamespace(modified_count=0)

    result = sites.update_site(str(ObjectId()), {"diocese_site": True})

    assert result is False


# -----------------
# Delete
# -----------------
def test_delete_site_success(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)

    result = sites.delete_site(str(ObjectId()))

    assert result is True


def test_delete_site_not_found(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=0)

    result = sites.delete_site(str(ObjectId()))

    assert result is False


def test_delete_site_by_id_success(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)

    result = sites.delete_site_by_id(3)

    assert result is True
    mock_collection.delete_one.assert_called_once_with({"site_id": 3})


def test_delete_site_by_id_not_found(mock_collection):
    mock_collection.delete_one.return_value = SimpleNamespace(deleted_count=0)

    result = sites.delete_site_by_id(999)

    assert result is False


# -----------------
# Business Logic
# -----------------
def test_get_max_site_id(mock_collection):
    mock_collection.find_one.return_value = {"site_id": 7}

    result = sites.get_max_site_id()

    assert result == 7
    mock_collection.find_one.assert_called_once()


def test_get_max_site_id_empty_collection(mock_collection):
    mock_collection.find_one.return_value = None

    result = sites.get_max_site_id()

    assert result == 0
