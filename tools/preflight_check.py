"""Command-line equivalent of the local control center's safety check."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.user_profile import load_profile, profile_path, validate_profile


def main() -> int:
    print("\nJob Application Assistant - Preflight")
    print("=" * 60)
    blocking = False

    python_ok = sys.version_info >= (3, 10)
    print(f"[{'OK' if python_ok else 'BLOCKED'}] Python {sys.version.split()[0]}")
    blocking |= not python_ok

    chrome_paths = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    chrome_ok = any(path.is_file() for path in chrome_paths) or bool(
        shutil.which("google-chrome")
    )
    print(f"[{'OK' if chrome_ok else 'BLOCKED'}] Google Chrome")
    blocking |= not chrome_ok

    path = profile_path()
    profile_exists = path.is_file()
    print(
        f"[{'OK' if profile_exists else 'BLOCKED'}] Private profile: "
        f"{path if profile_exists else 'complete setup at http://127.0.0.1:5050'}"
    )
    blocking |= not profile_exists

    if profile_exists:
        for issue in validate_profile(load_profile()):
            print(f"[BLOCKED] {issue['message']}")
            blocking = True

    print("=" * 60)
    if blocking:
        print("Not ready. No browser was started and no application was submitted.")
        return 1
    print("Ready. Manual review remains required before every submission.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
