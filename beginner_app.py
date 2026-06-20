"""Local, credential-conscious control center for non-technical users."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from modules.chrome_detect import chrome_available
from modules.user_profile import (
    DEFAULT_PROFILE,
    ROOT,
    load_profile,
    public_summary,
    save_profile,
    validate_profile,
)


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

BOT_PROCESS: subprocess.Popen[str] | None = None
BOT_LOG_HANDLE = None
PROCESS_LOCK = threading.Lock()
ALLOWED_SECTIONS = {"personal", "questions", "search", "settings"}


def _bot_running() -> bool:
    return BOT_PROCESS is not None and BOT_PROCESS.poll() is None


def _safe_profile_update(payload: dict[str, Any]) -> dict[str, Any]:
    current = load_profile()
    for section in ALLOWED_SECTIONS:
        incoming = payload.get(section)
        if not isinstance(incoming, dict):
            continue
        allowed = DEFAULT_PROFILE[section]
        for key, value in incoming.items():
            if key in allowed:
                current[section][key] = value

    # Beginner mode safety invariants cannot be disabled from the UI.
    current["questions"]["pause_at_failed_question"] = True
    current["questions"]["overwrite_previous_answers"] = False
    current["settings"]["run_in_background"] = False
    current["settings"]["run_non_stop"] = False
    current["settings"]["follow_companies"] = False
    current["settings"]["browser_engine"] = "selenium"

    terms = current["search"].get("search_terms", [])
    if isinstance(terms, str):
        current["search"]["search_terms"] = [
            term.strip() for term in terms.split(",") if term.strip()
        ]
    try:
        experience = max(0, int(current["questions"].get("years_of_experience", "0")))
    except (TypeError, ValueError):
        experience = 0
    current["questions"]["years_of_experience"] = str(experience)
    current["search"]["current_experience"] = experience
    return current


def _preflight() -> dict[str, Any]:
    profile = load_profile()
    issues = validate_profile(profile)
    chrome_ok = chrome_available()
    if not chrome_ok:
        issues.append(
            {
                "level": "error",
                "field": "chrome",
                "message": "Install Google Chrome before starting.",
            }
        )
    checks = [
        {"name": "Google Chrome", "ok": chrome_ok},
        {
            "name": "Personal information",
            "ok": not any(item["field"] in {"first_name", "last_name", "phone_number", "country"} for item in issues),
        },
        {
            "name": "Target roles and location",
            "ok": not any(item["field"] in {"search_terms", "search_location"} for item in issues),
        },
        {
            "name": "PDF resume",
            "ok": not any(item["field"] == "resume" for item in issues),
        },
        {
            "name": "Manual review safety",
            "ok": not any(
                item["field"] in {"pause_before_submit", "run_in_background"}
                for item in issues
            ),
        },
    ]
    use_ai_tailor = profile.get("settings", {}).get("use_AI_resume_tailoring", False)
    if use_ai_tailor:
        checks.append(
            {
                "name": "Word master resume (.docx)",
                "ok": not any(item["field"] == "docx_resume" for item in issues),
            }
        )
    return {"ready": not issues, "checks": checks, "issues": issues}


@app.get("/")
def home():
    return render_template("beginner.html")


@app.get("/api/profile")
def get_profile():
    return jsonify(public_summary())


@app.post("/api/profile")
def update_profile():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid profile data."}), 400
    profile = _safe_profile_update(payload)
    save_profile(profile)
    return jsonify({"saved": True, "profile": public_summary(profile), **_preflight()})


@app.post("/api/resume")
def upload_resume():
    uploaded = request.files.get("resume")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "Choose a PDF resume first."}), 400
    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF resumes are accepted."}), 400

    private_root = Path(
        os.environ.get("JOB_AGENT_USER_DATA_DIR", str(ROOT / "user_data"))
    ).expanduser().resolve()
    destination_dir = private_root / "resume"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "resume.pdf"
    uploaded.save(destination)
    try:
        os.chmod(destination, 0o600)
    except OSError:
        pass

    profile = load_profile()
    profile["questions"]["default_resume_path"] = str(destination)
    save_profile(profile)
    return jsonify({"uploaded": True, "filename": filename, **_preflight()})


@app.post("/api/resume_docx")
def upload_resume_docx():
    uploaded = request.files.get("resume_docx")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "Choose a Word (.docx) resume first."}), 400
    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".docx"):
        return jsonify({"error": "Only Word (.docx) resumes are accepted."}), 400

    private_root = Path(
        os.environ.get("JOB_AGENT_USER_DATA_DIR", str(ROOT / "user_data"))
    ).expanduser().resolve()
    destination_dir = private_root / "resume"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "resume.docx"
    uploaded.save(destination)
    try:
        os.chmod(destination, 0o600)
    except OSError:
        pass

    return jsonify({"uploaded": True, "filename": filename, **_preflight()})


@app.get("/api/preflight")
def preflight():
    return jsonify(_preflight())


@app.get("/api/status")
def status():
    running = _bot_running()
    return jsonify(
        {
            "running": running,
            "pid": BOT_PROCESS.pid if running and BOT_PROCESS else None,
            "exit_code": None if running or BOT_PROCESS is None else BOT_PROCESS.returncode,
        }
    )


@app.post("/api/start")
def start_bot():
    global BOT_PROCESS, BOT_LOG_HANDLE
    payload = request.get_json(silent=True) or {}
    if payload.get("confirmation") != "REVIEW":
        return jsonify({"error": "Type REVIEW to confirm manual review mode."}), 400

    checks = _preflight()
    if not checks["ready"]:
        return jsonify({"error": "Complete the required setup first.", **checks}), 400

    login_mode = payload.get("login_mode", "manual")
    if login_mode not in {"manual", "credentials"}:
        return jsonify({"error": "Invalid login mode."}), 400
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if login_mode == "credentials" and (not username or not password):
        return jsonify({"error": "Email and password are required for automatic login."}), 400

    with PROCESS_LOCK:
        if _bot_running():
            return jsonify({"error": "The assistant is already running."}), 409

        profile = load_profile()
        use_AI_tailor = profile.get("settings", {}).get("use_AI_resume_tailoring", False)
        env = os.environ.copy()
        env["JOB_AGENT_LOGIN_MODE"] = login_mode
        env["JOB_AGENT_DISABLE_AI"] = "0" if use_AI_tailor else "1"
        if login_mode == "credentials":
            env["JOB_AGENT_LINKEDIN_USERNAME"] = username
            env["JOB_AGENT_LINKEDIN_PASSWORD"] = password
        else:
            env.pop("JOB_AGENT_LINKEDIN_USERNAME", None)
            env.pop("JOB_AGENT_LINKEDIN_PASSWORD", None)

        log_path = ROOT / "logs" / "beginner-launcher.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        BOT_LOG_HANDLE = log_path.open("a", encoding="utf-8")
        creationflags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
        BOT_PROCESS = subprocess.Popen(
            [sys.executable, "runAiBot.py"],
            cwd=ROOT,
            env=env,
            stdout=BOT_LOG_HANDLE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creationflags,
        )
    return jsonify(
        {
            "started": True,
            "pid": BOT_PROCESS.pid,
            "message": "Browser automation started. Review every application before submission.",
        }
    )


@app.post("/api/stop")
def stop_bot():
    global BOT_LOG_HANDLE
    with PROCESS_LOCK:
        if not _bot_running():
            return jsonify({"stopped": False, "message": "The assistant is not running."})
        assert BOT_PROCESS is not None
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(BOT_PROCESS.pid), "/T", "/F"],
                capture_output=True,
                check=False,
            )
        else:
            BOT_PROCESS.terminate()
            try:
                BOT_PROCESS.wait(timeout=8)
            except subprocess.TimeoutExpired:
                return jsonify(
                    {
                        "stopped": False,
                        "message": "Close the visible bot window to finish stopping.",
                    }
                ), 409
        if BOT_LOG_HANDLE:
            BOT_LOG_HANDLE.close()
            BOT_LOG_HANDLE = None
    return jsonify({"stopped": True})


def main() -> None:
    port = int(os.environ.get("JOB_AGENT_BEGINNER_PORT", "5050"))
    url = f"http://127.0.0.1:{port}"
    if os.environ.get("JOB_AGENT_NO_BROWSER") != "1":
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"Beginner control center: {url}")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
