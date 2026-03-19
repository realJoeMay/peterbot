"""
data_store.py

Helpers for resolving the data_store directory.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_data_store_dir() -> Path:
    """
    Return the data_store directory configured in the environment.

    Returns:
        Path: Absolute path to the data_store directory.

    Raises:
        RuntimeError: If DATA_STORE_DIR is not set in the environment.
    """
    data_store_dir = os.getenv("DATA_STORE_DIR")
    if not data_store_dir:
        raise RuntimeError("DATA_STORE_DIR not set")

    return Path(data_store_dir)
