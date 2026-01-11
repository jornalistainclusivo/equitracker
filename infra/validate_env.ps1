Write-Host "Validating environment..." -ForegroundColor Cyan

# 1. Check for Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: docker is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 2. Check for Docker Compose (suporta 'docker-compose' antigo ou 'docker compose' novo)
$composeV1 = Get-Command docker-compose -ErrorAction SilentlyContinue
$dockerComposeV2 = docker compose version 2>$null

if (-not $composeV1 -and -not $dockerComposeV2) {
    Write-Host "Error: docker-compose is not installed." -ForegroundColor Red
    exit 1
}

# 3. Check for .env file
if (-not (Test-Path .env)) {
    Write-Host "Error: .env file not found. Please copy .env.example to .env and configure it." -ForegroundColor Red
    exit 1
}

Write-Host "Environment validation successful. Ready for Lift Off!" -ForegroundColor Green