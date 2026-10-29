# Peterbot

This project is set up for Python development with a local editable install and a dedicated virtual environment.

## Quick start

1. Create and activate a virtual environment.
2. Install the project in editable mode with dev dependencies.
3. Copy the example environment settings and update the local path.
4. Run tests.

## Commands

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
copy .env.example .env
pytest
```

## Environment configuration

Set your local data directory in `.env`:

```dotenv
PETERBOT_DATA_DIR=D:/peterbot-data
PETERBOT_WARC_MAX_SIZE_MB=1000
```

The project expects `PETERBOT_DATA_DIR` to exist or to be created when the application uses it.
