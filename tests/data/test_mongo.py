import os

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


def test_backup_runs_mongodump(monkeypatch, tmp_path):
    """backup() should call mongodump with correct arguments and return path."""
    # Force env vars
    monkeypatch.setenv("MONGODB_URI", "mongodb://example:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "testdb")
    monkeypatch.setattr(mongo, "get_data_store_dir", lambda: tmp_path)

    calls = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)
        # Create the directory mongodump would produce to satisfy return checks
        (tmp_path / "db_backups" / "testdb_19700101_000000" / "testdb").mkdir(
            parents=True, exist_ok=True
        )

    monkeypatch.setattr(mongo.subprocess, "run", fake_run)

    # Freeze timestamp for deterministic folder name
    from datetime import datetime as real_dt

    class FakeDateTime:
        @staticmethod
        def now():
            return real_dt(1970, 1, 1, 0, 0, 0)

    monkeypatch.setattr(mongo, "datetime", FakeDateTime)

    backup_dir = mongo.backup()

    assert calls, "mongodump was not invoked"
    cmd = calls[0]
    assert cmd[:2] == ["mongodump", "--uri"]
    assert "--db" in cmd
    assert str(backup_dir).endswith("db_backups\\testdb_19700101_000000") or str(
        backup_dir
    ).endswith("db_backups/testdb_19700101_000000")
    assert backup_dir.exists()


def test_restore_uses_latest_backup_and_drops(monkeypatch, tmp_path):
    """restore() should pick newest backup when none provided and include --drop."""
    monkeypatch.setenv("MONGODB_URI", "mongodb://example:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "testdb")
    monkeypatch.setattr(mongo, "get_data_store_dir", lambda: tmp_path)

    root = tmp_path / "db_backups"
    old = root / "testdb_20200101_000000"
    new = root / "testdb_20200102_000000"
    (old / "testdb").mkdir(parents=True, exist_ok=True)
    (new / "testdb").mkdir(parents=True, exist_ok=True)
    os.utime(old, (1, 1))
    os.utime(new, (2, 2))  # newest

    calls = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)

    monkeypatch.setattr(mongo.subprocess, "run", fake_run)

    restored_dir = mongo.restore()

    assert restored_dir == new
    assert calls, "mongorestore was not invoked"
    cmd = calls[0]
    assert cmd[0] == "mongorestore"
    assert "--drop" in cmd
    assert "--dir" in cmd
    # dir should point to the inner db folder
    dir_arg = cmd[cmd.index("--dir") + 1]
    assert dir_arg.endswith(str(new / "testdb"))


def test_restore_specific_backup_no_drop(monkeypatch, tmp_path):
    """restore() should honor provided backup_dir and drop=False."""
    monkeypatch.setenv("MONGODB_URI", "mongodb://example:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "testdb")

    backup_dir = tmp_path / "db_backups" / "testdb_custom"
    inner = backup_dir / "testdb"
    inner.mkdir(parents=True, exist_ok=True)

    calls = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)

    monkeypatch.setattr(mongo.subprocess, "run", fake_run)

    restored_dir = mongo.restore(backup_dir=backup_dir, drop=False)

    assert restored_dir == backup_dir
    assert calls, "mongorestore was not invoked"
    cmd = calls[0]
    assert "--drop" not in cmd
    dir_arg = cmd[cmd.index("--dir") + 1]
    assert dir_arg.endswith(str(inner))


def test_export_all_collections_pretty(monkeypatch, tmp_path):
    """export() should call mongoexport for each collection with pretty/jsonArray."""
    monkeypatch.setenv("MONGODB_URI", "mongodb://example:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "testdb")
    monkeypatch.setattr(mongo, "get_data_store_dir", lambda: tmp_path)

    class FakeDb:
        @staticmethod
        def list_collection_names():
            return ["sites", "jobs"]

    monkeypatch.setattr(mongo, "get_database", lambda: FakeDb())

    # deterministic timestamp
    from datetime import datetime as real_dt

    class FakeDateTime:
        @staticmethod
        def now():
            return real_dt(1970, 1, 1, 0, 0, 0)

    monkeypatch.setattr(mongo, "datetime", FakeDateTime)

    calls = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)

    monkeypatch.setattr(mongo.subprocess, "run", fake_run)

    export_dir = mongo.export()

    assert export_dir == tmp_path / "db_exports" / "testdb_19700101_000000"
    assert export_dir.exists()
    assert len(calls) == 2
    for cmd in calls:
        assert cmd[0] == "mongoexport"
        assert "--pretty" in cmd
        assert "--jsonArray" in cmd
        assert "--collection" in cmd
        coll = cmd[cmd.index("--collection") + 1]
        outfile = cmd[cmd.index("--out") + 1]
        assert outfile.endswith(f"{coll}.json")


def test_export_selected_collections_plain(monkeypatch, tmp_path):
    """export() should respect provided collections and flag toggles."""
    monkeypatch.setenv("MONGODB_URI", "mongodb://example:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "testdb")
    monkeypatch.setattr(mongo, "get_data_store_dir", lambda: tmp_path)

    calls = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)

    monkeypatch.setattr(mongo.subprocess, "run", fake_run)

    export_dir = mongo.export(pretty=False, json_array=False, collections=["only"])

    assert len(calls) == 1
    cmd = calls[0]
    assert "--pretty" not in cmd
    assert "--jsonArray" not in cmd
    assert cmd[cmd.index("--collection") + 1] == "only"
    outfile = cmd[cmd.index("--out") + 1]
    assert outfile.endswith("only.json")
    assert export_dir.exists()
