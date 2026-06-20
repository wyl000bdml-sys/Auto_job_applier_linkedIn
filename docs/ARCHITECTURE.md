# Project Architecture

## Product goal

The default experience is a local, beginner-friendly application assistant:

```text
START_HERE.bat
  -> setup-for-beginners.ps1
  -> local Python environment
  -> beginner_app.py
  -> http://127.0.0.1:5050
  -> private profile + resume
  -> safety preflight
  -> runAiBot.py
```

No external AI agent is required. The beginner path disables optional LLM
features and uses the existing deterministic browser automation engine.

## Layers

### 1. Installation and launch

- `START_HERE.bat`: the only file a Windows beginner needs to double-click.
- `setup-for-beginners.ps1`: creates `.venv`, installs dependencies only when
  `requirements-local.txt` changes, and starts the local control center.

### 2. Local control center

- `beginner_app.py`: local-only Flask API bound to `127.0.0.1`.
- `templates/beginner.html`: profile, target-role, resume, login, preflight,
  start, and stop interface.

The server never exposes itself on the LAN. LinkedIn passwords are accepted
only for the current run and are passed to the child process through its
environment. Manual login is the recommended default.

### 3. Private user data

- `user_data/profile.json`: structured non-password user profile.
- `user_data/resume/resume.pdf`: uploaded default resume.
- `modules/user_profile.py`: defaults, atomic JSON storage, validation, and
  compatibility overlays.

The entire `user_data/` directory is ignored by Git.

### 4. Legacy compatibility

The existing engine imports settings from:

- `config/personals.py`
- `config/questions.py`
- `config/search.py`
- `config/settings.py`

Each module now applies the corresponding private JSON section after its
legacy defaults are defined. This preserves the mature browser workflow while
removing the need for users to edit Python.

### 5. Automation engine

- `runAiBot.py`: LinkedIn search, form filling, review pause, and application
  history.
- `modules/open_chrome.py`: Selenium/Chrome session.
- `modules/clickers_and_finders.py`: browser interaction helpers.
- `modules/validator.py`: legacy configuration validation.

Beginner mode enforces:

- visible browser
- manual review before submission
- no continuous background operation
- no automatic company following
- no optional AI/API dependency

### 6. Optional/advanced tools

- `app.py`: application-history and reply dashboard.
- `tools/`: CLI checks and document utilities.
- `modules/ai/`: optional provider integrations for advanced users.

These are not required for the beginner path.
Their packages are listed separately in `requirements-optional.txt`.

## Security boundaries

- The web server binds only to `127.0.0.1`.
- Passwords and API keys are excluded from profile responses and JSON storage.
- Resume presence is a blocking preflight requirement.
- Starting requires the exact confirmation text `REVIEW`.
- The child process receives only the credentials needed for that run.
- Browser verification and CAPTCHA remain manual.

## Future refactoring

The compatibility overlay is intentionally incremental. A later major version
can replace wildcard imports and module-level browser creation with explicit
dependency injection, but that rewrite should be tested separately from the
beginner onboarding work.
