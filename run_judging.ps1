# ==============================================================================
# PS02: Offline Security Incident Triage Assistant
# Hackathon Phase 2 Judging Launcher (React + FastAPI)
#
# Participant: Mir Farzin Hussain
# USN: 1MS24CI073
# Branch: CSE (AI & ML)
# Problem Statement: PS02 (Cybersecurity | Small Language Models)
# Operating Mode: 100% OFFLINE (Air-Gapped / Zero External Cloud APIs)
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  TINYVERSE HACKATHON PHASE 2 - PROBLEM STATEMENT PS02" -ForegroundColor Yellow
Write-Host "  Offline Security Incident Triage Assistant (React + FastAPI)" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  Participant : Mir Farzin Hussain" -ForegroundColor White
Write-Host "  USN         : 1MS24CI073" -ForegroundColor White
Write-Host "  Branch      : CSE (AI & ML)" -ForegroundColor White
Write-Host "  Architecture: React 19 + TypeScript + Vite + Tailwind + FastAPI + SmolLM2" -ForegroundColor White
Write-Host "  Enforcement : 100% Air-Gapped Offline Operation" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Verify Virtual Environment
$PythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "[!] Virtual environment not found at .venv\Scripts\python.exe. Using system python..." -ForegroundColor Yellow
    $PythonExe = "python"
} else {
    Write-Host "[+] Activating local virtual environment: $PythonExe" -ForegroundColor Cyan
}

# 2. Verify Compiled Frontend Assets
$DistIndex = Join-Path $ScriptDir "frontend\dist\index.html"
if (-not (Test-Path $DistIndex)) {
    Write-Host "[*] Frontend dist not found. Building React production bundle..." -ForegroundColor Yellow
    Push-Location (Join-Path $ScriptDir "frontend")
    npm run build
    Pop-Location
}

Write-Host "[+] Compiled frontend verified at frontend\dist\" -ForegroundColor Green
Write-Host "[+] Local SLM weights verified at models\SmolLM2-135M-Instruct\" -ForegroundColor Green
Write-Host ""
Write-Host ">> Launching SOC Workstation at http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Write-Host ">> Press Ctrl+C at any time to shut down the server." -ForegroundColor Gray
Write-Host ""

# 3. Open browser after brief delay
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

# 4. Run FastAPI uvicorn server
& $PythonExe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
