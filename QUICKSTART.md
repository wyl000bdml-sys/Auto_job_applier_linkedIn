# Beginner Quick Start (Windows)

This project ships with a local control center. You don't need to edit any
Python files, and you don't need Codex, ChatGPT, or any other agent.

> **中文版**：请参阅 [QUICKSTART_ZH.md](QUICKSTART_ZH.md)。
> **macOS users**: see [QUICKSTART_MAC.md](QUICKSTART_MAC.md).

## Before you start

1. **Install Google Chrome**:
   - Go to the [Google Chrome site](https://www.google.com/chrome/) and click the
     blue **Download Chrome** button to install it.
2. **Install Python 3.10 or newer**:
   - Go to the [Python downloads page for Windows](https://www.python.org/downloads/windows/)
     and download the Windows installer.
   - When running the installer, **make sure to check "Add python.exe to PATH"** at
     the bottom of the install screen, then click **Install Now** at the top.

   ![Check Add Python to PATH during install](docs/python_download_page.png)

3. **A ready-to-use PDF resume.**

## First run and the control center

1. **Download this repository**:
   - On this project's GitHub page, click the green **Code** button, then click
     **Download ZIP** at the bottom of the dropdown.

   ![Click Download ZIP on GitHub](docs/github_code_download.png)

2. **Unzip the archive**:
   - After downloading, extract the ZIP into its own folder. **Never run a script
     from inside the archive — extract it first.**
3. **Double-click to run**:
   ```text
   START_HERE.bat
   ```

The first run automatically creates an isolated environment and installs the
components. When setup finishes, your browser opens the local control center:
```text
http://127.0.0.1:5050
```

![Local control center web UI](docs/beginner_ui_en.png)

### 🖱️ What each step does:

*   **Step 1: Fill in basic info and job targets**
    *   Enter your name, phone, and country, then set your **target roles** and
        **search location**.
    *   When done, click **Save profile**. This safely stores the data in
        `user_data/profile.json` on your machine.
*   **Step 2: Upload your resume**
    *   **Upload PDF resume**: choose your PDF file, then click **Upload PDF resume**.
    *   **Enable AI resume tailoring (optional)**: if you check **"One resume per
        company (AI auto-tailoring)"**, the page slides out a **"3.1 Upload Word
        master resume"** area. Choose your `.docx` master resume and click
        **Upload Word master resume**.
*   **Step 3: Set submission and tailoring options**
    *   **One resume per company**: the AI tailors the project descriptions in your
        Word resume based on the job description.
    *   **Collect only, don't submit**: only collects jobs and generates resumes
        locally without actually applying on LinkedIn.
    *   **Fully automatic submission**: confirms and submits automatically. If
        unchecked, it pauses at the final step for you to review and submit manually.
*   **Step 4: Preflight checks**
    *   The page automatically runs checks (Chrome, profile completeness, resume
        file presence, etc.).
    *   **Every check must be green** and the banner must say it's ready before you
        can run.
*   **Step 5: Log in and launch**
    *   Choose your LinkedIn login method (manual login / auto-fill).
    *   Type the uppercase word `REVIEW` in the text box.
    *   Finally, click **Start the assistant** to begin automation. To interrupt,
        click the red **Stop** button next to it.

## What you need to provide

Fill in on the page:

- name, phone, city, and country
- work authorization and sponsorship status
- LinkedIn, GitHub, or personal website
- target roles and search location
- a PDF resume

Then choose a LinkedIn login method:

1. **Manual login (recommended)**: log in yourself in the opened browser; no
   password is saved.
2. **Auto-fill for this run**: your username and password are passed only to the
   current child process and are never written to the config file.

## Running safely

The page must show all checks passing before you can start.

Before launch, type:

```text
REVIEW
```

Beginner mode always:

- keeps the browser visible
- pauses before every submission
- never runs continuously in the background
- never auto-follows companies
- blocks startup when the PDF resume is missing

The automation can fill in real application forms, but the final content must be
reviewed by you.

## Stopping

- Click "Stop" on the local page; or
- close the automation browser window; or
- press `Ctrl+C` in the black launcher window.

## Where your data is stored

Non-sensitive job data and resumes are stored in:

```text
user_data/
```

This directory is Git-ignored. Your LinkedIn password is not saved by default.

Do not publish:

- `user_data/`
- `config/secrets.py`
- `config/personals.py`
- browser profile directories
- resumes, application records, and API keys

## FAQ

### The page didn't open automatically

Open <http://127.0.0.1:5050> in your browser manually.

### Python was not found

Reinstall Python, check **Add Python to PATH**, restart your computer, and
double-click `START_HERE.bat` again.

### Installing components failed

Check your network, firewall, and VPN, then run `START_HERE.bat` again.

### LinkedIn asks for a CAPTCHA

Complete the verification manually. Do not try to bypass CAPTCHAs or account
security checks.

### Filling fails after LinkedIn changes its pages

Stop the automation immediately. Platform page changes can break browser
automation, and it must not run unattended.
