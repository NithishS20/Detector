# start_servers.ps1
# Starts the AI backend, automated reporter, and React frontend.
# Usage: .\start_servers.ps1

$python = Join-Path $PSScriptRoot ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Output "Virtualenv python not found at $python"
    Write-Output "Activate your virtualenv or adjust the path in this script."
    exit 1
}

function Is-Up($url) {
    try {
        $r = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec 3
        return $true
    } catch {
        return $false
    }
}

Write-Output "========================================="
Write-Output "Detector: Starting Backend Services"
Write-Output "========================================="

Write-Output "`nChecking AI backend at http://127.0.0.1:8000/api/alerts ..."
if (Is-Up "http://127.0.0.1:8000/api/alerts") {
    Write-Output "✓ AI backend already running."
} else {
    Write-Output "✓ Starting AI backend on :8000..."
    Start-Process -NoNewWindow -FilePath $python -ArgumentList '-m','uvicorn','backend.main:app','--port','8000','--host','127.0.0.1' -PassThru
    Start-Sleep -Seconds 2
}

Write-Output "`nChecking automated reporter at http://127.0.0.1:8100/health ..."
if (Is-Up "http://127.0.0.1:8100/health") {
    Write-Output "✓ Automated reporter already running."
} else {
    Write-Output "✓ Starting automated reporter on :8100..."
    Start-Process -NoNewWindow -FilePath $python -ArgumentList '-m','uvicorn','automated_reporter.main:app','--port','8100','--host','127.0.0.1' -PassThru
    Start-Sleep -Seconds 2
}

Write-Output "`n========================================="
Write-Output "Starting React Frontend"
Write-Output "========================================="
Write-Output "`nLaunching frontend (npm start on :3000)..."
$frontendPath = Join-Path $PSScriptRoot "frontend"
Push-Location $frontendPath
Start-Process -NoNewWindow cmd -ArgumentList "/c npm start" -PassThru
Pop-Location

Write-Output "`n========================================="
Write-Output "All services started!"
Write-Output "========================================="
Write-Output "`nAccess the dashboard at: http://localhost:3000"
Write-Output "Backend API: http://localhost:8000"
Write-Output "Reporter API: http://localhost:8100"
Write-Output ""
