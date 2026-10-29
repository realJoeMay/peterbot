from pathlib import Path

from peterbot.config import get_data_dir, get_warc_max_size_mb


def test_get_data_dir_uses_env(monkeypatch):
    monkeypatch.setenv("PETERBOT_DATA_DIR", "D:/peterbot-data")
    assert get_data_dir() == Path("D:/peterbot-data").resolve()


def test_get_warc_max_size_mb_uses_env(monkeypatch):
    monkeypatch.setenv("PETERBOT_WARC_MAX_SIZE_MB", "750")
    assert get_warc_max_size_mb() == 750
