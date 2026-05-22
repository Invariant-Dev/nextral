# build.ps1 — build Nextral for Windows
# Usage: .\build.ps1 [-Installer] [-Clean]

param(
    [switch]$Installer,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "=== Nextral Build ===" -ForegroundColor Cyan

if ($Clean) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "$root\dist"  -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "$root\build" -ErrorAction SilentlyContinue
    Write-Host "Clean done." -ForegroundColor Green
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install -e "$root[dev]" --quiet
python -m pip install pyinstaller --quiet
Write-Host "Dependencies installed." -ForegroundColor Green

if ($Installer) {
    Write-Host "Building installer exe..." -ForegroundColor Yellow
    pyinstaller "$root\installer.spec" --distpath "$root\dist" --workpath "$root\build"
    Write-Host "Installer built: dist\nextral-installer\" -ForegroundColor Green
} else {
    Write-Host "Building main app exe..." -ForegroundColor Yellow
    pyinstaller "$root\nextral.spec" --distpath "$root\dist" --workpath "$root\build"
    Write-Host "App built: dist\nextral\" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run: .\dist\nextral\nextral.exe" -ForegroundColor Cyan
}
