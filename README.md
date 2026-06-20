# Local Job Application Assistant — macOS (Customized Fork)

[English](README.md) | [中文说明](README_ZH.md)

> 🍎 **This is the macOS branch (`mac_branch`).** Setup and Chrome detection are
> tuned for macOS. **Windows users:** switch to the [`main`](../../tree/main) branch.

![Local Control Center Web UI](docs/beginner_ui_en.png)

This is a customized fork of the open-source job application assistant, modified from the original project [GodsScion/Auto_job_applier_linkedIn](https://github.com/GodsScion/Auto_job_applier_linkedIn) (licensed under AGPLv3).

## Key Customizations & Upgrades

This fork introduces several advanced features tailored for research/academic job hunting (such as Ph.D. positions) and a much friendlier local onboarding experience:

1. **Local Web Control Center:** Includes a Flask-based local web dashboard (`beginner_app.py` at `127.0.0.1:5050`) allowing users to configure parameters, target roles, upload resumes, and choose login styles visually without modifying code.
2. **AI-Powered Suitability Evaluator ("Brain Upgrade"):** Integrates with Google Gemini API to analyze job descriptions against your uploaded **Word format master resume (`resume.docx`)** (or optionally a custom structured project experience inventory file `career_project_inventory.md` if present in the root folder). The bot calculates an alignment score (0-100) and decides to skip jobs that fall below a suitability threshold (<50), reducing account ban risks and ensuring higher application quality.
3. **Tailored Textarea Answers:** Automatically generates customized summaries matching the job description and injects them into application essay questions (e.g., summaries, cover letters).
4. **Persistent Skip Memory:** Checks both applied and failed/skipped history files during initialization to avoid repeating or re-opening job listings that were previously processed.
5. **Cross-Platform Chrome Auto-Detection:** Reliably locates Google Chrome on macOS (via Spotlight), Windows (via the registry), and Linux — even when Chrome is installed outside the default location or run straight from `~/Downloads` instead of `/Applications` — and matches the ChromeDriver version at run time to prevent version-mismatch crashes.

## Start here

1. Install [Google Chrome](https://www.google.com/chrome/) and drag it into
   **Applications** (don't run it straight from the disk image).
2. Install [Python 3.10+](https://www.python.org/downloads/macos/) — run the
   `.pkg` installer (no PATH setup is needed on macOS).
3. Download and extract this repository.
4. Launch:

| OS | File to run | How |
|----|-----------|---------|
| **macOS** | `START_HERE.command` | Right-click → Open (first time only) |
| **Windows** | `START_HERE.bat` | Double-click |

The script installs required components when needed and opens a private local
page at <http://127.0.0.1:5050>.

- macOS guide: [QUICKSTART_MAC.md](QUICKSTART_MAC.md)
- Windows guide: [QUICKSTART.md](QUICKSTART.md)

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
macOS:   START_HERE.command  →  setup-for-beginners.sh
Windows: START_HERE.bat  →  setup-for-beginners.ps1
  both  →  beginner_app.py (127.0.0.1 only)
          →  user_data/profile.json + uploaded resume
          →  safety preflight
          →  runAiBot.py
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

- `python3 app.py` — application-history dashboard
- `python3 tools/preflight_check.py` — command-line safety check
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
