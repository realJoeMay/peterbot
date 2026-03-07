from pathlib import Path
from typing import Any, Dict, List, Optional

# from bson import ObjectId


def sanitize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {}

    for key, value in doc.items():
        if isinstance(value, Path):
            sanitized[key] = value.as_posix()
        else:
            sanitized[key] = value

    return sanitized
