"""
mongo.py

Provides centralized MongoDB connection management for the project.

Responsibilities:
- Establish and reuse a MongoClient connection
- Return database and collection references
- Provide a health check for the MongoDB server
- Safely close the MongoClient connection

Usage Example:
----------------
from peterbot.data.mongo import get_collection, ping

# Get a collection reference
users_collection = get_collection("users")

# Check MongoDB health
if ping():
    print("MongoDB is reachable")

"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

from peterbot.data.data_store import get_data_store_dir

load_dotenv()

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """
    Get a singleton MongoClient instance.

    Lazily initializes the client on first call and reuses it thereafter.

    Returns:
        MongoClient: A connected MongoClient instance

    Raises:
        RuntimeError: If the environment variable MONGODB_URI is not set
    """
    global _client

    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI not set")

        _client = MongoClient(uri)

    return _client


def get_database():
    """
    Get the MongoDB database instance configured in the environment.

    Returns:
        Database: A reference to the MongoDB database

    Raises:
        RuntimeError: If the environment variable MONGODB_DB_NAME is not set
    """
    db_name = os.getenv("MONGODB_DB_NAME")
    if not db_name:
        raise RuntimeError("MONGODB_DB_NAME not set")

    return get_client()[db_name]


def get_collection(name: str):
    """
    Get a MongoDB collection by name.

    Args:
        name (str): The name of the collection

    Returns:
        Collection: A reference to the requested MongoDB collection
    """
    return get_database()[name]


def ping() -> bool:
    """
    Check if the MongoDB server is reachable.

    Returns:
        bool: True if the server responds to a ping command, False otherwise
    """
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False


def close_connection():
    """
    Close the MongoClient connection if it exists.

    This function resets the singleton _client to None.
    Useful for cleanup in scripts or tests.
    """
    global _client
    if _client:
        _client.close()
        _client = None


def backup() -> Path:
    """
    Run `mongodump` to create a BSON backup of the configured database.

    Backups are written under DATA_STORE_DIR/db_backups/<db>_<timestamp>/.

    Returns:
        Path: Directory containing the backup files.

    Raises:
        RuntimeError: If required env vars are missing or mongodump fails.
        OSError: If the backup directory cannot be created.
    """
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    if not uri:
        raise RuntimeError("MONGODB_URI not set")
    if not db_name:
        raise RuntimeError("MONGODB_DB_NAME not set")

    backup_root = get_data_store_dir() / "db_backups"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"{db_name}_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "mongodump",
        "--uri",
        uri,
        "--db",
        db_name,
        "--out",
        str(backup_dir),
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("mongodump not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        error_msg = exc.stderr or exc.stdout or "mongodump failed"
        raise RuntimeError(error_msg) from exc

    return backup_dir


def _get_latest_backup_dir(db_name: str) -> Path:
    """
    Return the most recently modified backup directory for the given DB.
    """
    backup_root = get_data_store_dir() / "db_backups"
    if not backup_root.exists():
        raise RuntimeError("No backups found (db_backups directory missing)")

    candidates = [
        p
        for p in backup_root.iterdir()
        if p.is_dir() and p.name.startswith(f"{db_name}_")
    ]
    if not candidates:
        raise RuntimeError(f"No backups found for database '{db_name}'")

    return max(candidates, key=lambda p: p.stat().st_mtime)


def restore(backup_dir: Path | None = None, drop: bool = True) -> Path:
    """
    Restore the configured database from a mongodump backup.

    Args:
        backup_dir: Path to a specific backup directory; defaults to the latest.
        drop: If True (default), existing collections are dropped before restore.

    Returns:
        Path: The backup directory that was restored.

    Raises:
        RuntimeError: If env vars are missing, backup not found, or mongorestore fails.
    """
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    if not uri:
        raise RuntimeError("MONGODB_URI not set")
    if not db_name:
        raise RuntimeError("MONGODB_DB_NAME not set")

    backup_dir = backup_dir or _get_latest_backup_dir(db_name)
    if not backup_dir.exists() or not backup_dir.is_dir():
        raise RuntimeError(f"Backup directory not found: {backup_dir}")

    # mongodump placed files under <backup_dir>/<db_name>/...
    restore_source = (
        backup_dir / db_name if (backup_dir / db_name).exists() else backup_dir
    )

    cmd = [
        "mongorestore",
        "--uri",
        uri,
        "--nsInclude",
        f"{db_name}.*",
        "--dir",
        str(restore_source),
    ]
    if drop:
        cmd.insert(1, "--drop")

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("mongorestore not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        error_msg = exc.stderr or exc.stdout or "mongorestore failed"
        raise RuntimeError(error_msg) from exc

    return backup_dir


def export(
    pretty: bool = True, json_array: bool = True, collections: list[str] | None = None
) -> Path:
    """
    Export collections to human-readable JSON using `mongoexport`.

    Args:
        pretty: When True, adds --pretty for formatted JSON (default True).
        json_array: When True, writes a single JSON array (--jsonArray) (default True).
        collections: Optional list of collection names to export; defaults to all.

    Returns:
        Path: Directory containing the exported JSON files.

    Raises:
        RuntimeError: If env vars are missing, mongoexport is not found, or a command fails.
    """
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    if not uri:
        raise RuntimeError("MONGODB_URI not set")
    if not db_name:
        raise RuntimeError("MONGODB_DB_NAME not set")

    export_root = get_data_store_dir() / "db_exports"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = export_root / f"{db_name}_{timestamp}"
    export_dir.mkdir(parents=True, exist_ok=True)

    collection_names = collections or get_database().list_collection_names()

    for coll in collection_names:
        outfile = export_dir / f"{coll}.json"
        cmd = [
            "mongoexport",
            "--uri",
            uri,
            "--db",
            db_name,
            "--collection",
            coll,
            "--out",
            str(outfile),
        ]
        if json_array:
            cmd.append("--jsonArray")
        if pretty:
            cmd.append("--pretty")

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except FileNotFoundError as exc:
            raise RuntimeError("mongoexport not found on PATH") from exc
        except subprocess.CalledProcessError as exc:
            error_msg = (
                exc.stderr
                or exc.stdout
                or f"mongoexport failed for collection '{coll}'"
            )
            raise RuntimeError(error_msg) from exc

    return export_dir
