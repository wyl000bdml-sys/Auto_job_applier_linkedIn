"""Robust cross-platform Google Chrome / Chromium binary detection.

The preflight checks (web UI in ``beginner_app.py`` and CLI in
``tools/preflight_check.py``) need to know whether a real Chrome binary is
installed on disk, because the automation drives Chrome through Selenium /
undetected-chromedriver.

Checking a handful of hardcoded install paths is fragile: users who installed
Chrome to a custom directory (or via certain enterprise / packaged installers)
were being told "Chrome is not installed" even though it clearly was. On
Windows the authoritative source is the registry ``App Paths\\chrome.exe`` key,
which records the real ``chrome.exe`` path regardless of install location, so we
consult that in addition to the common paths and ``PATH`` lookup.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _registry_chrome_paths() -> list[Path]:
    """Return chrome.exe paths recorded in the Windows registry, if any."""
    if not sys.platform.startswith("win"):
        return []
    try:
        import winreg
    except ImportError:
        return []

    paths: list[Path] = []
    subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
    # Check the native view, the 32-bit redirected view, and the per-user hive.
    targets = [
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_READ),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_READ | getattr(winreg, "KEY_WOW64_32KEY", 0)),
        (winreg.HKEY_CURRENT_USER, winreg.KEY_READ),
    ]
    for root, access in targets:
        try:
            with winreg.OpenKey(root, subkey, 0, access) as key:
                value, _ = winreg.QueryValueEx(key, None)  # default value = full path
                if value:
                    paths.append(Path(value))
        except OSError:
            continue
    return paths


def _spotlight_chrome_paths() -> list[Path]:
    """Locate ``Google Chrome.app`` anywhere on macOS via Spotlight (mdfind).

    This is the macOS analogue of the Windows registry lookup: it finds Chrome
    no matter where it was installed (e.g. run from ~/Downloads or the Desktop
    instead of being dragged into /Applications).
    """
    if sys.platform != "darwin":
        return []
    try:
        result = subprocess.run(
            ["mdfind", "kMDItemCFBundleIdentifier == 'com.google.Chrome'"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    paths: list[Path] = []
    for line in result.stdout.splitlines():
        app = line.strip()
        if app.endswith(".app"):
            paths.append(Path(app) / "Contents/MacOS/Google Chrome")
    return paths


def find_chrome() -> str | None:
    """Return the path to an installed Chrome/Chromium binary, or ``None``."""
    candidates = [
        # Windows default install locations
        Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
        # macOS
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # Linux
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/opt/google/chrome/chrome"),
    ]
    candidates.extend(_registry_chrome_paths())
    candidates.extend(_spotlight_chrome_paths())

    for path in candidates:
        try:
            if path and path.is_file():
                return str(path)
        except OSError:
            continue

    for name in (
        "google-chrome",
        "google-chrome-stable",
        "chrome",
        "chromium-browser",
        "chromium",
    ):
        found = shutil.which(name)
        if found:
            return found

    return None


def chrome_available() -> bool:
    """Convenience wrapper: ``True`` if a Chrome/Chromium binary was found."""
    return find_chrome() is not None
