<#
.SYNOPSIS
    Setup full patching environment for CVE auto-remediation on a fresh Windows VM.

.DESCRIPTION
    - Installs: Python, Git, AWS CLI v2, GitLab Runner
    - Configures GitLab Runner with Group Token
    - Clones project repo from GitHub
    - Installs Python dependencies
    - Validates all components
    - Optional: Write runner metadata to DynamoDB
#>

# ========== CONFIG ==========

#THAY THEO NHÓM MÌNH, t sử dụng script hôm qua với t  ko check đc hết
$RepoURL        = "https://github.com/Sskadii1/hackathon.git"
$InstallPath    = "C:\PatchCVE"
$GitlabURL      = "https://gitlab.com/"
$GitlabToken    = "REPLACE_WITH_YOUR_GITLAB_GROUP_TOKEN"  # Replace with your actual token
$RunnerName     = "$env:COMPUTERNAME-runner"
$RunnerTags     = "windows,cve,patch"
$AwsRegion      = "ap-southeast-1"  # Adjust to your AWS region
$DynamoTable    = "RunnerHosts"     # Table name as per project specification
# ============================

Write-Host "Initializing CVE Patch Environment for: $env:COMPUTERNAME" -ForegroundColor Cyan

function Install-ChocoIfNeeded {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = 'Tls12'
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        refreshenv
    }
}

function Install-PackageIfMissing {
    param ($name)
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Host "Installing $name..."
        choco install -y $name
    } else {
        Write-Host "$name is already installed."
    }
}

# Step 1: Install tools
Install-ChocoIfNeeded
Install-PackageIfMissing -name "python"
Install-PackageIfMissing -name "git"
Install-PackageIfMissing -name "awscli"
Install-PackageIfMissing -name "gitlab-runner"

# Step 2: Install Python dependencies
Write-Host "Installing Python libraries..."
pip install --upgrade pip
pip install boto3 openpyxl requests beautifulsoup4

# Step 3: Clone the repository
if (-not (Test-Path $InstallPath)) {
    Write-Host "Cloning project to $InstallPath"
    git clone $RepoURL $InstallPath
} else {
    Write-Host "Project directory exists. Skipping clone."
}

# Step 4: Register GitLab Runner
Write-Host "Registering GitLab Runner..."
& "C:\Program Files\GitLab-Runner\gitlab-runner.exe" unregister --all-runners | Out-Null
& "C:\Program Files\GitLab-Runner\gitlab-runner.exe" register --non-interactive `
    --url $GitlabURL `
    --registration-token $GitlabToken `
    --executor shell `
    --description $RunnerName `
    --tag-list $RunnerTags `
    --run-untagged=true `
    --locked=false

Start-Service gitlab-runner
Write-Host "GitLab Runner is registered and started."

# Step 5: Configure AWS
Write-Host "Checking AWS credentials..."
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "AWS CLI is already configured."
} catch {
    Write-Host "AWS credentials not found. Running aws configure..."
    aws configure
}

# Step 6: Write runner metadata to DynamoDB
Write-Host "Recording runner metadata to DynamoDB..."
$ip = (Invoke-RestMethod -Uri "https://api.ipify.org?format=json").ip
$os = (Get-CimInstance -ClassName Win32_OperatingSystem).Caption
$hostname = $env:COMPUTERNAME
$record = @{
    HostId = @{ S = $hostname }
    IPAddress = @{ S = $ip }
    OSVersion = @{ S = $os }
    Status = @{ S = "active" }
    RequiresReboot = @{ BOOL = $false }
    LastBatchId = @{ S = "None" }
}
$json = $record | ConvertTo-Json -Depth 10

aws dynamodb put-item `
    --table-name $DynamoTable `
    --region $AwsRegion `
    --item "$json"

Write-Host "Runner metadata stored."

# Step 7: Run verification test
Write-Host "Running test command:"
cd $InstallPath
python main.py

Write-Host "Environment setup complete for $hostname." -ForegroundColor Green
