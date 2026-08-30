#!/usr/bin/env pwsh
# Novahaku Installer for Windows
# Agent: Haku — Unified Security Research Agent
# https://github.com/novaestellar/novahaku

$ErrorActionPreference = 'Stop'

$HERMES_HOME = Join-Path $HOME '.hermes' 'skills'
$TARGET_DIR = Join-Path $HERMES_HOME 'novahaku'
$REPO_URL = 'https://github.com/novaestellar/novahaku.git'

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Novahaku Installer (Haku Agent)" -ForegroundColor Cyan
Write-Host "  Unified Security Research Agent" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git is not installed." -ForegroundColor Red
    Write-Host "Install from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = 'python'
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = 'python3'
} else {
    Write-Host "[WARN] Python not found. Some features may not work." -ForegroundColor Yellow
}

# Create directory
if (-not (Test-Path $HERMES_HOME)) {
    Write-Host "[*] Creating ~/.hermes/skills/ directory..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path $HERMES_HOME -Force | Out-Null
}

# Remove existing installation
if (Test-Path $TARGET_DIR) {
    Write-Host "[*] Removing existing installation..." -ForegroundColor Yellow
    Remove-Item -Path $TARGET_DIR -Recurse -Force
}

# Clone repository
Write-Host "[*] Cloning novahaku repository..." -ForegroundColor Gray
git clone --depth 1 $REPO_URL $TARGET_DIR

if (-not (Test-Path (Join-Path $TARGET_DIR 'SKILL.md'))) {
    Write-Host "[ERROR] Installation failed: SKILL.md not found" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
if ($pythonCmd) {
    Write-Host "[*] Installing Python dependencies..." -ForegroundColor Gray
    & $pythonCmd -m pip install --quiet pycryptodome requests 2>$null
}

# Cleanup git metadata
Remove-Item -Path (Join-Path $TARGET_DIR '.git') -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Location: $TARGET_DIR" -ForegroundColor Gray
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "  # Web testing" -ForegroundColor Gray
Write-Host "  python $TARGET_DIR\testing\scripts\webtest.py https://target.com" -ForegroundColor White
Write-Host ""
Write-Host "  # Prompt techniques" -ForegroundColor Gray
Write-Host "  cat $TARGET_DIR\techniques\methods\01-boundary\m-01003-delimiter-injection.md" -ForegroundColor White
Write-Host ""
Write-Host "  # Reframe" -ForegroundColor Gray
Write-Host "  python $TARGET_DIR\reframe\reframe_cli.py `"text`" --fresh" -ForegroundColor White
Write-Host ""
