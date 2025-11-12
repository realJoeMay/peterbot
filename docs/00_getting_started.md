# Getting Started

Follow these steps to recreate a clean peterbot development environment.

## 1. Prerequisites
- **Python 3.11+** with the python and pip executables available on your PATH.
- **Git** for cloning the repository and collaborating.
- **Optional helpers** such as uv, pyenv, or pipx are fine, but the commands below assume the built-in venv module.

## 2. Clone the repository
~~~bash
git clone https://github.com/<your-org>/peterbot.git
cd peterbot
~~~
Replace the URL if you are working from a fork or different remote.

## 3. Create and activate a virtual environment
Pick the snippet that matches your platform:
~~~bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
~~~
~~~powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
~~~
Feel free to use Conda, uv, Poetry, or another manager as long as it targets Python 3.11 or newer.

## 4. Install dependencies
With the environment active, install the project in editable mode:
~~~bash
pip install -e .
~~~
For full development tooling (tests, linting, formatting, typing) add the optional extras defined in pyproject.toml:
~~~bash
pip install -e ".[dev]"
~~~

## 5. Optional notebook setup
Install Jupyter support if you plan to run the notebooks under notebooks/: 
~~~bash
pip install notebook ipykernel
python -m ipykernel install --user --name peterbot
~~~

## 6. Verify the installation
Run the core quality checks to make sure everything is wired correctly:
~~~bash
pytest
ruff check .
ruff format --check .
~~~
All commands should exit with status 0; fix any issues they report before committing changes.

## 7. Next steps
- Keep the virtual environment active while developing; deactivate later with the appropriate command for your shell.
- Store secrets in environment variables or an untracked .env file—never commit them.
- Explore the source code under src/ and the sample workflows in notebooks/ to understand the project layout.
