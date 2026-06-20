$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# Email reply tracking is optional. Credentials exist only in this process.
if (-not $env:JOB_AGENT_IMAP_HOST) { $env:JOB_AGENT_IMAP_HOST = "imap.gmail.com" }
if (-not $env:JOB_AGENT_IMAP_PORT) { $env:JOB_AGENT_IMAP_PORT = "993" }
if (-not $env:JOB_AGENT_IMAP_MAILBOX) { $env:JOB_AGENT_IMAP_MAILBOX = "INBOX" }

$enableEmail = Read-Host "Enable read-only email reply tracking? (y/N)"
if ($enableEmail -match "^[Yy]$") {
    if (-not $env:JOB_AGENT_IMAP_USER) {
        $env:JOB_AGENT_IMAP_USER = Read-Host "Email address"
    }
    if (-not $env:JOB_AGENT_IMAP_PASSWORD) {
        $securePassword = Read-Host "Email app password (hidden)" -AsSecureString
        $passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        try {
            $env:JOB_AGENT_IMAP_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
        }
        finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
        }
    }
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "The virtual environment is missing. Run START_HERE.bat first." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

& $python app.py
