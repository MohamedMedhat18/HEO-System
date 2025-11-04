# PowerShell script to automate the installation of required libraries on Windows

# Check if Python is installed
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed. Please install Python 3.10+ from https://www.python.org/downloads/"
    exit
}

# Check if pip is installed
$pip = Get-Command pip -ErrorAction SilentlyContinue
if (-not $pip) {
    Write-Host "pip is not installed. Please ensure pip is installed with your Python installation."
    exit
}

# Install required libraries
$requirementsFile = "..\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Installing required libraries from requirements.txt..."
    pip install -r $requirementsFile
} else {
    Write-Host "requirements.txt not found. Please ensure it exists in the project root."
}