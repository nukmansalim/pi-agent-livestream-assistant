# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a Python Flask REST API server ("Pi Agent") for managing a YouTube channel via natural language commands. It supports video upload, metadata editing, and livestream management.

### Running the application

```bash
source yt-agent-env/bin/activate
python pi_agent_rest_api.py
```

Server runs on `http://localhost:5000`. Key endpoints: `/health`, `/capabilities`, `/status`, `/execute`, `/upload`, `/edit`, `/livestream/*`.

### Running tests

```bash
source yt-agent-env/bin/activate
python -m pytest tests/ -v
```

All tests are fully mocked (no external services needed). The test suite patches OAuth and YouTube API at the `conftest.py` level.

### Important notes

- **No linter is configured** in this project (no flake8/ruff/pylint config files). Use `python -m py_compile <file>` for syntax checking if needed.
- **Google OAuth credentials** (`client_secrets.json`) are required for real YouTube API operations. Without them, the server runs but YouTube operations return "Belum autentikasi" (not authenticated). Tests pass without credentials since they use mocks.
- The virtual environment directory is `yt-agent-env/` (already in `.gitignore`).
- `python3.12-venv` system package must be installed for creating the venv (`sudo apt-get install -y python3.12-venv`).
- The app sets `OAUTHLIB_INSECURE_TRANSPORT=1` at startup to allow OAuth over HTTP in development.
