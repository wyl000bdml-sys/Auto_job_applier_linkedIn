#!/usr/bin/env bash
# setup-for-beginners.sh  —  macOS / Linux first-run setup & launcher
# Equivalent of setup-for-beginners.ps1 on Windows.
set -euo pipefail
cd "$(dirname "$0")"

# ── colour helpers ───────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
say()  { printf "${CYAN}%s${NC}\n" "$*"; }
warn() { printf "${YELLOW}%s${NC}\n" "$*"; }
ok()   { printf "${GREEN}%s${NC}\n" "$*"; }
err()  { printf "${RED}%s${NC}\n" "$*" >&2; }

# ── trap errors ──────────────────────────────────────────────────────────────
on_error() {
    err ""
    err "Setup could not finish. Check the message above, then run START_HERE.command again."
    read -rp "Press Enter to close…" _
}
trap on_error ERR

echo ""
say "Job Application Assistant"
echo "Preparing the local control center. No application will be submitted."
echo ""

# ── locate Python 3.10+ ──────────────────────────────────────────────────────
PYTHON_CMD=""
for cmd in python3 python3.13 python3.12 python3.11 python3.10 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null || true)
        if [[ "$VER" == "True" ]]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    err "Python 3.10 or newer was not found."
    err "1. Install Python from https://www.python.org/downloads/"
    err "2. Restart this terminal, then run START_HERE.command again."
    read -rp "Press Enter to close…" _
    exit 1
fi

# ── create virtual environment ───────────────────────────────────────────────
VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
    warn "First-time setup: creating a private Python environment…"
    "$PYTHON_CMD" -m venv .venv
fi

# Verify venv Python version
"$VENV_PYTHON" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" || {
    err "The virtual environment Python is older than 3.10."
    err "Delete the '.venv' folder and run START_HERE.command again."
    exit 1
}

# ── install / skip dependencies ──────────────────────────────────────────────
MARKER_PATH=".venv/requirements.sha256"
if command -v shasum &>/dev/null; then
    REQUIREMENTS_HASH=$(shasum -a 256 requirements-local.txt | awk '{print $1}')
elif command -v sha256sum &>/dev/null; then
    REQUIREMENTS_HASH=$(sha256sum requirements-local.txt | awk '{print $1}')
else
    REQUIREMENTS_HASH="unknown"
fi

INSTALLED_HASH=""
[[ -f "$MARKER_PATH" ]] && INSTALLED_HASH=$(cat "$MARKER_PATH")

# Force reinstall if core packages are missing
"$VENV_PYTHON" -c "import flask, selenium, pyautogui, undetected_chromedriver" 2>/dev/null \
    || INSTALLED_HASH=""

if [[ "$REQUIREMENTS_HASH" != "$INSTALLED_HASH" ]]; then
    warn "Installing required components. This only runs when dependencies change…"
    PIP_CACHE_DIR="$(pwd)/.venv/pip-cache" \
        "$VENV_PYTHON" -m pip install --no-cache-dir --upgrade pip
    PIP_CACHE_DIR="$(pwd)/.venv/pip-cache" \
        "$VENV_PYTHON" -m pip install --no-cache-dir -r requirements-local.txt
    echo "$REQUIREMENTS_HASH" > "$MARKER_PATH"
else
    ok "Required components are already installed."
fi

# ── copy default secrets if missing ─────────────────────────────────────────
if [[ ! -f "config/secrets.py" ]]; then
    cp "config/secrets.example.py" "config/secrets.py"
fi

# ── launch ───────────────────────────────────────────────────────────────────
echo ""
ok "Opening the private setup page in your browser…"
echo "Keep this window open while using the assistant."
echo "Press Ctrl+C here when you are finished."
echo ""

"$VENV_PYTHON" beginner_app.py
