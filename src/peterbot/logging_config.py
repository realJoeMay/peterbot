import logging
import os
from datetime import datetime

from peterbot.data.data_store import get_data_store_dir


def setup_logging(run_name: str):

    log_dir = get_data_store_dir() / "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{run_name}.log"
    filepath = os.path.join(log_dir, filename)

    # Clear existing handlers (important if reused in tests or notebooks)
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    file_handler = logging.FileHandler(filepath)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    return filepath
