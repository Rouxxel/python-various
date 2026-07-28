# Initialize template: copy .env.example to .env and print next steps (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "Initializing Analytics Dashboard Template..."
Write-Host ""

# Copy backend .env.example to .env
$backendDir = "backend"
$envExample = "$backendDir\.env.example"
$envFile = "$backendDir\.env"

if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "✓ Created $envFile from .env.example"
} else {
    Write-Host "! $envFile already exists (skipping)"
}

# Copy frontend .env.example to .env
$frontendDir = "frontend"
$frontendEnvExample = "$frontendDir\.env.example"
$frontendEnvFile = "$frontendDir\.env"

if ((Test-Path $frontendEnvExample) -and (-not (Test-Path $frontendEnvFile))) {
    Copy-Item $frontendEnvExample $frontendEnvFile
    Write-Host "✓ Created $frontendEnvFile from .env.example"
} else {
    Write-Host "! $frontendEnvFile already exists or .env.example not found (skipping)"
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit backend/.env to set your API key and other variables"
Write-Host "2. Edit frontend/.env to set VITE_DASHBOARD_API_URL"
Write-Host "3. Install backend dependencies: cd backend; uv sync"
Write-Host "4. Install frontend dependencies: cd frontend; npm install"
Write-Host "5. Start backend: cd backend; uv run python -m app.main"
Write-Host "6. Start frontend: cd frontend; npm run dev"
Write-Host ""
Write-Host "For more information, see README.md"
