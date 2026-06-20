"""Private, JSON-backed user configuration for the beginner control center."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE_PATH = ROOT / "user_data" / "profile.json"

DEFAULT_PROFILE: dict[str, Any] = {
    "version": 1,
    "personal": {
        "first_name": "",
        "middle_name": "",
        "last_name": "",
        "phone_number": "",
        "current_city": "",
        "street": "",
        "state": "",
        "zipcode": "",
        "country": "United States",
        "ethnicity": "Decline",
        "gender": "Decline",
        "disability_status": "Decline",
        "veteran_status": "Decline",
    },
    "questions": {
        "default_resume_path": "user_data/resume/resume.pdf",
        "years_of_experience": "0",
        "require_visa": "Yes",
        "website": "",
        "linkedIn": "",
        "us_citizenship": "Non-citizen seeking work authorization",
        "desired_salary": 0,
        "current_ctc": 0,
        "notice_period": 0,
        "linkedin_headline": "",
        "linkedin_summary": "",
        "cover_letter": "",
        "user_information_all": "",
        "recent_employer": "Not Applicable",
        "confidence_level": "5",
        "pause_before_submit": True,
        "pause_at_failed_question": True,
        "overwrite_previous_answers": False,
    },
    "search": {
        "search_terms": [],
        "search_location": "United States",
        "switch_number": 10,
        "randomize_search_order": False,
        "sort_by": "Most recent",
        "date_posted": "Past week",
        "salary": "",
        "easy_apply_only": True,
        "experience_level": ["Internship", "Entry level"],
        "job_type": ["Full-time", "Internship"],
        "on_site": ["On-site", "Remote", "Hybrid"],
        "companies": [],
        "location": [],
        "industry": [],
        "job_function": [],
        "job_titles": [],
        "benefits": [],
        "commitments": [],
        "under_10_applicants": False,
        "in_your_network": False,
        "fair_chance_employer": False,
        "pause_after_filters": True,
        "about_company_bad_words": ["Staffing", "Recruiting"],
        "about_company_good_words": [],
        "bad_words": ["Security Clearance", "U.S. Citizenship"],
        "security_clearance": False,
        "did_masters": False,
        "current_experience": 0,
    },
    "settings": {
        "close_tabs": False,
        "follow_companies": False,
        "run_non_stop": False,
        "alternate_sortby": False,
        "cycle_date_posted": False,
        "stop_date_cycle_at_24hr": True,
        "generated_resume_path": "all resumes/",
        "file_name": "all excels/all_applied_applications_history.csv",
        "failed_file_name": "all excels/all_failed_applications_history.csv",
        "logs_folder_path": "logs/",
        "click_gap": 1,
        "run_in_background": False,
        "disable_extensions": False,
        "safe_mode": True,
        "smooth_scroll": False,
        "keep_screen_awake": True,
        "stealth_mode": True,
        "browser_engine": "selenium",
        "showAiErrorAlerts": False,
        "use_AI_resume_tailoring": False,
        "shortlist_only": False,
    },
}


def profile_path() -> Path:
    custom = os.environ.get("JOB_AGENT_PROFILE_PATH", "").strip()
    return Path(custom).expanduser().resolve() if custom else DEFAULT_PROFILE_PATH


def _merge(defaults: dict[str, Any], saved: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(defaults)
    for key, value in saved.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_profile() -> dict[str, Any]:
    path = profile_path()
    if not path.is_file():
        return deepcopy(DEFAULT_PROFILE)
    try:
        saved = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return deepcopy(DEFAULT_PROFILE)
    return _merge(DEFAULT_PROFILE, saved if isinstance(saved, dict) else {})


def save_profile(profile: dict[str, Any]) -> Path:
    path = profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _merge(DEFAULT_PROFILE, profile)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


def apply_section(namespace: dict[str, Any], section: str) -> None:
    """Overlay a saved section onto a legacy config module namespace."""
    if not profile_path().is_file():
        return
    values = load_profile().get(section, {})
    if not isinstance(values, dict):
        return
    for key, value in values.items():
        if key in namespace:
            namespace[key] = value


def public_summary(profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a credential-free summary suitable for the local web interface."""
    current = profile or load_profile()
    return {
        "version": current.get("version", 1),
        "personal": current.get("personal", {}),
        "questions": current.get("questions", {}),
        "search": current.get("search", {}),
        "settings": current.get("settings", {}),
    }


def validate_profile(profile: dict[str, Any] | None = None) -> list[dict[str, str]]:
    current = profile or load_profile()
    personal = current.get("personal", {})
    questions = current.get("questions", {})
    search = current.get("search", {})
    issues: list[dict[str, str]] = []

    required = [
        ("first_name", personal.get("first_name"), "First name is required."),
        ("last_name", personal.get("last_name"), "Last name is required."),
        ("phone_number", personal.get("phone_number"), "Phone number is required."),
        ("country", personal.get("country"), "Country is required."),
        ("search_terms", search.get("search_terms"), "Add at least one target role."),
        ("search_location", search.get("search_location"), "Search location is required."),
    ]
    for field, value, message in required:
        if not value:
            issues.append({"level": "error", "field": field, "message": message})

    resume_value = str(questions.get("default_resume_path", "")).strip()
    resume = Path(resume_value)
    if resume_value and not resume.is_absolute():
        resume = ROOT / resume
    if not resume.is_file():
        issues.append(
            {
                "level": "error",
                "field": "resume",
                "message": "Upload a PDF resume before starting.",
            }
        )


    if current.get("settings", {}).get("run_in_background", False):
        issues.append(
            {
                "level": "error",
                "field": "run_in_background",
                "message": "The browser must remain visible in beginner mode.",
            }
        )
    return issues
