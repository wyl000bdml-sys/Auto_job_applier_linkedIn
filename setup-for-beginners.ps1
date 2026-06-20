$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Set-Location -Path $PSScriptRoot

function Wait-ForUser {
    param([string]$Message = "Press Enter to close")
    Read-Host $Message | Out-Null
}

trap {
    Write-Host ""
    Write-Host "Setup could not finish: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Check your internet connection, then run START_HERE.bat again."
    Wait-ForUser
    exit 1
}

Write-Host ""
Write-Host "Job Application Assistant" -ForegroundColor Cyan
Write-Host "Preparing the local control center. No application will be submitted."
Write-Host ""

$pythonCommand = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = "py"
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = "python"
}

if (-not $pythonCommand) {
    Write-Host "Python 3.10 or newer was not found." -ForegroundColor Red
    Write-Host "1. Install Python from https://www.python.org/downloads/"
    Write-Host "2. Select 'Add Python to PATH' during installation."
    Write-Host "3. Double-click START_HERE.bat again."
    Wait-ForUser
    exit 1
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "First-time setup: creating a private Python environment..." -ForegroundColor Yellow
    if ($pythonCommand -eq "py") {
        & py -3 -m venv .venv
    }
    else {
        & python -m venv .venv
    }
    if ($LASTEXITCODE -ne 0) { throw "Could not create the Python environment." }
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $venvPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) {
    throw "Python 3.10 or newer is required."
}

$requirementsHash = (Get-FileHash "requirements-local.txt" -Algorithm SHA256).Hash
$markerPath = Join-Path $PSScriptRoot ".venv\requirements.sha256"
$installedHash = if (Test-Path $markerPath) { (Get-Content $markerPath -Raw).Trim() } else { "" }
& $venvPython -c "import flask, selenium, pyautogui, undetected_chromedriver"
$coreDependenciesAvailable = $LASTEXITCODE -eq 0
if (-not $coreDependenciesAvailable) {
    $installedHash = ""
}
elseif (-not $installedHash) {
    Set-Content -Path $markerPath -Value $requirementsHash -Encoding ASCII
    $installedHash = $requirementsHash
}

if ($requirementsHash -ne $installedHash) {
    Write-Host "Installing required components. This only runs when dependencies change..." -ForegroundColor Yellow
    $env:PIP_CACHE_DIR = Join-Path $PSScriptRoot ".venv\pip-cache"
    & $venvPython -m pip install --no-cache-dir --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "Could not update pip." }
    & $venvPython -m pip install --no-cache-dir -r requirements-local.txt
    if ($LASTEXITCODE -ne 0) { throw "Could not install required packages." }
    Set-Content -Path $markerPath -Value $requirementsHash -Encoding ASCII
}
else {
    Write-Host "Required components are already installed." -ForegroundColor Green
}

if (-not (Test-Path "config\secrets.py")) {
    Copy-Item "config\secrets.example.py" "config\secrets.py"
}

Write-Host ""
Write-Host "Opening the private setup page in your browser..." -ForegroundColor Green
Write-Host "Keep this window open while using the assistant."
Write-Host "Press Ctrl+C here when you are finished."
Write-Host ""

& $venvPython beginner_app.py
