# HEO System - Minimal PowerShell Startup Script
# This script creates/reuses venv, installs packages, and starts backend + frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HEO System - Minimal Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Extract version number
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
$majorVersion = [int]$matches[1]
$minorVersion = [int]$matches[2]

if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 10)) {
    Write-Host "ERROR: Python 3.10+ is required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create or activate virtual environment
$venvPath = "venv"
if (Test-Path $venvPath) {
    Write-Host "Found existing virtual environment at '$venvPath'" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
} else {
    Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

# Activate venv
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "ERROR: Could not find activation script at $activateScript" -ForegroundColor Red
    exit 1
}

# Install/upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "pip upgraded successfully" -ForegroundColor Green
} else {
    Write-Host "WARNING: Failed to upgrade pip, continuing anyway..." -ForegroundColor Yellow
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first run..." -ForegroundColor Cyan

# Check if we should build from source (for older Python versions)
$buildFromSource = $false
if ($majorVersion -eq 3 -and $minorVersion -lt 11) {
    Write-Host "Python version is 3.10.x - will use prebuilt wheels where available" -ForegroundColor Yellow
    $buildFromSource = $false
} elseif ($majorVersion -eq 3 -and $minorVersion -lt 12) {
    Write-Host "Python version is 3.11.x - using prebuilt wheels" -ForegroundColor Green
} else {
    Write-Host "Python version is 3.12+ - using prebuilt wheels" -ForegroundColor Green
}

# Install packages
if ($buildFromSource) {
    Write-Host "Note: Some packages may need to build from source" -ForegroundColor Yellow
    pip install -r requirements.txt --no-cache-dir
} else {
    pip install -r requirements.txt
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Try running: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "Dependencies installed successfully" -ForegroundColor Green

# Create necessary directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$directories = @("db", "invoices", "logs", "assets", "assets/fonts", "assets/signatures")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Exists: $dir" -ForegroundColor Gray
    }
}

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
python -c "from backend.services.database import init_db; from backend.services.auth import create_default_admin; init_db(); create_default_admin()"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Database initialized successfully" -ForegroundColor Green
} else {
    Write-Host "WARNING: Database initialization had issues, but continuing..." -ForegroundColor Yellow
}

# Start backend in background
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Backend API..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

# Start backend as a background job
$backendJob = Start-Job -ScriptBlock {
    param($workingDir)
    Set-Location $workingDir
    & "venv\Scripts\python.exe" -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
} -ArgumentList $PWD

Write-Host "Backend started (Job ID: $($backendJob.Id))" -ForegroundColor Green

# Wait for backend to be ready
Write-Host "Waiting for backend to be ready..." -ForegroundColor Yellow
$maxRetries = 30
$retries = 0
$backendReady = $false

while ($retries -lt $maxRetries -and -not $backendReady) {
    Start-Sleep -Seconds 1
    $retries++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 1 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "Backend is ready!" -ForegroundColor Green
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if (-not $backendReady) {
    Write-Host ""
    Write-Host "WARNING: Backend did not respond within 30 seconds" -ForegroundColor Yellow
    Write-Host "Check backend job status with: Get-Job -Id $($backendJob.Id) | Receive-Job" -ForegroundColor Yellow
} else {
    Write-Host ""
}

# Start frontend
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend will run on: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Default login credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin1" -ForegroundColor White
Write-Host "  Password: admin_password" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow
Write-Host ""

# Run frontend (blocking, in foreground)
try {
    & "venv\Scripts\streamlit.exe" run unified_app.py --server.port 8501 --server.address 0.0.0.0
} finally {
    # Cleanup: stop backend job
    Write-Host ""
    Write-Host "Stopping backend..." -ForegroundColor Yellow
    Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    Write-Host "Backend stopped" -ForegroundColor Green
    Write-Host ""
    Write-Host "Thank you for using HEO System!" -ForegroundColor Cyan
}
