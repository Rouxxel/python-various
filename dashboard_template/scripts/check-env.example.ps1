# Check if .env file has all required variables from .env.example (PowerShell)

$ErrorActionPreference = "Stop"

$backendDir = "backend"
$envFile = "$backendDir\.env"
$envExample = "$backendDir\.env.example"

if (-not (Test-Path $envFile)) {
    Write-Error "Error: $envFile not found. Copy $envExample to $envFile first."
    exit 1
}

Write-Host "Checking $envFile against $envExample..."

# Read required variables from .env.example
$requiredVars = @()
Get-Content $envExample | ForEach-Object {
    if ($_ -match '^[^#]*=') {
        $var = ($_ -split '=')[0].Trim()
        if ($var) {
            $requiredVars += $var
        }
    }
}

# Check which variables are missing in .env
$missingVars = @()
$envContent = Get-Content $envFile
$envVars = @()
$envContent | ForEach-Object {
    if ($_ -match '^[^#]*=') {
        $var = ($_ -split '=')[0].Trim()
        if ($var) {
            $envVars += $var
        }
    }
}

foreach ($var in $requiredVars) {
    if ($var -notin $envVars) {
        $missingVars += $var
    }
}

if ($missingVars.Count -eq 0) {
    Write-Host "✓ All required variables are set in $envFile"
    exit 0
} else {
    Write-Host "✗ Missing variables in $envFile:"
    foreach ($var in $missingVars) {
        Write-Host "  - $var"
    }
    Write-Host ""
    Write-Host "Add these variables to $envFile or copy from $envExample"
    exit 1
}
