from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_data_dir() -> Path:
    """Return the configured data root for Peterbot artifacts."""
    value = os.getenv("PETERBOT_DATA_DIR")
    if not value:
        raise RuntimeError(
            "PETERBOT_DATA_DIR is not configured. Copy .env.example to .env and set it."
        )
    return Path(value).expanduser().resolve()


def get_warc_max_size_mb() -> int:
    value = os.getenv("PETERBOT_WARC_MAX_SIZE_MB", "1000")
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover
        raise RuntimeError("PETERBOT_WARC_MAX_SIZE_MB must be an integer in MB.") from exc
