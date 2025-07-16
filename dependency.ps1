<#
.SYNOPSIS
    Lightweight environment init script for CVE patch pipeline (Windows VM)

.DESCRIPTION
    - Checks and installs: Python, Git, AWS CLI
    - Installs Python dependencies if needed
    - Clones repo if missing
    - Optional: Configure AWS if not already
#>

# ========== CONFIG ==========
$RepoURL     = "https://github.com/Sskadii1/hackathon.git"
$InstallPath = "C:\PatchCVE"
# ============================

Write-Host "Initializing environment for patch pipeline..." -ForegroundColor Cyan

function Install-ChocoIfNeeded {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = 'Tls12'
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    }
}

function Install-IfMissing($pkg) {
    if (-not (Get-Command $pkg -ErrorAction SilentlyContinue)) {
        Write-Host "Installing $pkg..."
        choco install -y $pkg
    } else {
        Write-Host "$pkg already installed."
    }
}

# Step 1: Ensure required tools
Install-ChocoIfNeeded
Install-IfMissing "python"
Install-IfMissing "git"
Install-IfMissing "awscli"

# Step 2: Ensure Python packages
Write-Host "Ensuring Python libraries..."
pip install --upgrade pip
pip install boto3 openpyxl requests beautifulsoup4

# Step 3: Clone repo if missing
if (-not (Test-Path $InstallPath)) {
    Write-Host "Cloning patch repo..."
    git clone $RepoURL $InstallPath
} else {
    Write-Host "Patch code directory already exists. Skipping clone."
}

# Step 4: Optional AWS CLI config check
Write-Host "Checking AWS credentials..."
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "AWS CLI already configured."
} catch {
    Write-Host "AWS not configured. Launching aws configure..."
    aws configure
}

Write-Host "Environment initialized. Ready to run pipeline." -ForegroundColor Green
