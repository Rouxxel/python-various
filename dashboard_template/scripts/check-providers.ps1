# Check provider-related env vars when feature flags are enabled.

$ErrorActionPreference = "Stop"

$backendDir = Join-Path $PSScriptRoot ".." "backend"
$envFile = Join-Path $backendDir ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "No backend/.env found. Run scripts/init-template.ps1 first."
    exit 1
}

Push-Location $backendDir
try {
    uv run python -m app.tools.verify_providers
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
