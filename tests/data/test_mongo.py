import pytest
from pymongo import MongoClient
from peterbot.data import mongo


def test_get_client_returns_client():
    """get_client() should return a MongoClient instance"""
    client = mongo.get_client()
    assert isinstance(client, MongoClient)


def test_get_database_returns_database():
    """get_database() should return a database object"""
    db = mongo.get_database()
    # Type check by verifying it has collection attribute
    assert hasattr(db, "list_collection_names")


def test_get_collection_returns_collection():
    """get_collection() should return a collection object"""
    coll = mongo.get_collection("test_collection")
    # A pymongo collection has a name attribute
    assert hasattr(coll, "name")
    assert coll.name == "test_collection"


def test_ping_returns_true(monkeypatch):
    """ping() should return True when MongoClient responds"""

    # monkeypatch the admin.command to always succeed
    class DummyAdmin:
        def command(self, cmd):
            return {"ok": 1}

    class DummyClient:
        admin = DummyAdmin()

    monkeypatch.setattr(mongo, "get_client", lambda: DummyClient())
    assert mongo.ping() is True


def test_close_connection_resets_client():
    """close_connection() should set _client to None"""
    mongo.get_client()  # ensure _client is initialized
    mongo.close_connection()
    # Access the internal variable directly to check reset
    assert getattr(mongo, "_client") is None
