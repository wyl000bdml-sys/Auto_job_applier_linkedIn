# Local Deployment Notes

Repository deployed: https://github.com/GodsScion/Auto_job_applier_linkedIn

Chosen because it is the most popular actively maintained GitHub project found for LinkedIn auto job application with resume customization support. The original AIHawk project is larger by stars, but its main repository is archived.

## What is installed

- Project path: `E:\tools\auto job\Auto_job_applier_linkedIn`
- Python virtual environment: `.venv`
- Python version used: 3.13.9
- Chrome detected at: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Dependencies installed from `requirements-local.txt`

## Configure before running

Edit these files first:

- `config/personals.py`: your legal name, phone, address, EEOC answers.
- `config/questions.py`: resume path, salary, experience, visa, portfolio, LinkedIn profile, cover letter.
- `config/search.py`: job titles, location, filters, blacklist/skip rules.
- `config/secrets.py`: LinkedIn login and optional AI provider/API settings.

For AI-tailored resumes and cover letters, set `use_AI = True` in `config/secrets.py` and configure the provider/key/model there. Without AI, the bot can still fill applications using static config answers.

Put your default resume at the path configured by `default_resume_path`, which defaults to:

```text
all resumes/default/resume.pdf
```

## Run

From this folder:

```powershell
.\.venv\Scripts\python.exe runAiBot.py
```

This opens Chrome and may submit real LinkedIn applications. Keep `pause_before_submit = True` in `config/questions.py` until you trust the setup.

## Applied jobs history UI

```powershell
.\.venv\Scripts\python.exe app.py
```

Then open:

```text
http://localhost:5000
```

On Windows, you can also start the UI with:

```powershell
.\start-history-ui.ps1
```

### Email reply tracking

The local UI now includes an `Email Replies` panel. It scans your inbox in read-only mode and matches company replies to the locally saved target-job shortlist in `data/target_jobs.json`.

Set these environment variables before starting `app.py`:

```powershell
$env:JOB_AGENT_IMAP_HOST="imap.gmail.com"
$env:JOB_AGENT_IMAP_PORT="993"
$env:JOB_AGENT_IMAP_USER="your_email@gmail.com"
$env:JOB_AGENT_IMAP_PASSWORD="your_app_password"
$env:JOB_AGENT_IMAP_MAILBOX="INBOX"
.\.venv\Scripts\python.exe app.py
```

For Gmail, use an app password or another IMAP-specific credential. Do not put email passwords in repo files.

## Verified

- Dependencies installed successfully.
- `python -m compileall -q .` completed successfully.
- Chrome exists in the expected Windows install location.
- The history UI is configured to run on `http://127.0.0.1:5000` without Flask's debug reloader for stable background startup on Windows.

## Notes

The tool automates LinkedIn and uses scraping/browser automation. Review LinkedIn's policies and use cautiously.
