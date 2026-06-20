# Local Job Application Assistant (Customized Fork)

[English](README.md) | [中文说明](README_ZH.md)

This is a customized fork of the open-source job application assistant, modified from the original project [GodsScion/Auto_job_applier_linkedIn](https://github.com/GodsScion/Auto_job_applier_linkedIn) (licensed under AGPLv3).

## Key Customizations & Upgrades

This fork introduces several advanced features tailored for research/academic job hunting (such as Ph.D. positions) and a much friendlier local onboarding experience:

1. **Local Web Control Center:** Includes a Flask-based local web dashboard (`beginner_app.py` at `127.0.0.1:5050`) allowing users to configure parameters, target roles, upload resumes, and choose login styles visually without modifying code.
2. **AI-Powered Suitability Evaluator ("Brain Upgrade"):** Integrates with Google Gemini API to analyze job descriptions against a structured **Ph.D./Research Project Inventory** (`career_project_inventory.md`). The bot calculates an alignment score (0-100) and decides to skip jobs that fall below a suitability threshold (<50), reducing account ban risks and ensuring higher application quality.
3. **Tailored Textarea Answers:** Automatically generates customized summaries matching the job description and injects them into application essay questions (e.g., summaries, cover letters).
4. **Persistent Skip Memory:** Checks both applied and failed/skipped history files during initialization to avoid repeating or re-opening job listings that were previously processed.
5. **Self-Healing Version Matcher:** Automatically detects the installed Google Chrome version on Windows and matches the ChromeDriver major version at run time to prevent browser version mismatch crashes.

## Start here

1. Install [Google Chrome](https://www.google.com/chrome/).
2. Install [Python 3.10+](https://www.python.org/downloads/) and select
   **Add Python to PATH**.
3. Download and extract this repository.
4. Double-click:

```text
START_HERE.bat
```

The script installs required components when needed and opens a private local
page at <http://127.0.0.1:5050>.

See the Chinese beginner guide: [QUICKSTART.md](QUICKSTART.md).

## What the user provides

- contact and location information
- work authorization and sponsorship status
- target roles and search location
- LinkedIn/profile links
- a PDF resume
- a LinkedIn login choice

Manual LinkedIn login is recommended. If credentials are entered in the local
page, the password is passed only to the current child process and is not
written to the profile JSON.

## Safety defaults

Beginner mode always:

- keeps the browser visible
- pauses before every final submission
- prevents continuous background operation
- disables automatic company following
- disables optional AI/API integrations
- blocks startup until a PDF resume and required profile fields exist
- requires the exact confirmation text `REVIEW`

Browser automation can make mistakes when LinkedIn changes its interface.
Review every field and never leave it unattended.

## Architecture

```text
START_HERE.bat
  -> setup-for-beginners.ps1
  -> beginner_app.py (127.0.0.1 only)
  -> user_data/profile.json + uploaded resume
  -> safety preflight
  -> runAiBot.py
```

Detailed design: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Private files

The following must never be published:

- `user_data/`
- `config/secrets.py`
- `config/personals.py`
- browser profiles and cookies
- resumes and generated application documents
- application history and API keys

Review `git status` before every commit or push.

## Advanced use

- `python app.py` — application-history dashboard
- `python tools/preflight_check.py` — command-line safety check
- `runAiBot.py` — legacy direct entry; the local control center is preferred
- `modules/ai/` — optional advanced integrations, disabled in beginner mode
- `requirements-optional.txt` — packages for AI, DOCX, and Playwright tools

## Limitations

- LinkedIn verification and CAPTCHA must be completed manually.
- UI changes may break browser selectors.
- The tool does not guarantee application accuracy or job-search outcomes.
- Users are responsible for following platform terms and applicable law.

## License

AGPLv3. See [LICENSE](LICENSE).
