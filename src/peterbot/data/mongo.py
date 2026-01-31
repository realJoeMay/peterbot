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

from dotenv import load_dotenv
from pymongo import MongoClient

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
