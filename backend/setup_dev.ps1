# setup_dev.ps1 - Automated Development Environment Setup
# EquiTracker v0.3 - Windows/PowerShell

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host -ForegroundColor Cyan "`n[STEP] $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host -ForegroundColor Green "[SUCCESS] $Message"
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host -ForegroundColor Red "[ERROR] $Message"
}

# 1. Check Python Version
Write-Step "Checking Python Version..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(1[0-9]|[2-9][0-9])") {
        Write-Success "Found $pythonVersion"
    }
    else {
        throw "Python 3.10+ is required. Found: $pythonVersion"
    }
}
catch {
    Write-ErrorMsg "Python check failed. Ensure Python 3.10+ is installed and in your PATH."
    exit 1
}

# 2. Create Virtual Environment
Write-Step "Creating Virtual Environment (venv)..."
if (Test-Path "venv") {
    Write-Host "venv directory already exists. Skipping creation."
}
else {
    python -m venv venv
    Write-Success "Virtual environment created."
}

# 3. Activate Virtual Environment & Install Dependencies
Write-Step "Activating venv and installing dependencies..."
$venvScript = ".\venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvScript)) {
    Write-ErrorMsg "venv activation script not found at $venvScript"
    exit 1
}

# We invoke a new process to run the activation and install in that context context/scope
# But for a setup script, usually it's better to run the python executable from the venv directly
# to ensure packages go to the right place without complex shell activation logic in the script scope.
$venvPython = ".\venv\Scripts\python.exe"
$venvPip = ".\venv\Scripts\pip.exe"
$venvPlaywright = ".\venv\Scripts\playwright.exe"


# Upgrade pip
Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements from requirements.txt..."
& $venvPip install -r requirements.txt
Write-Success "Dependencies installed."

# 4. Install Playwright Browsers (for crawl4ai)
Write-Step "Installing Playwright browsers..."
try {
    & $venvPython -m playwright install
    Write-Success "Playwright browsers installed."
}
catch {
    Write-ErrorMsg "Failed to install Playwright browsers. Please run 'playwright install' manually in venv."
}

Write-Host -ForegroundColor Green "`n[DONE] Development environment setup complete!"
Write-Host -ForegroundColor Green "To start the backend:"
Write-Host "1. .\venv\Scripts\Activate.ps1"
Write-Host "2. uvicorn main:app --reload"
