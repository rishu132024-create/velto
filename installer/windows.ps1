$ErrorActionPreference = "Stop"

$VeltoHome = Join-Path $env:USERPROFILE ".velto"
$VeltoRepo = "https://github.com/rishu132024-create/velto.git"
$VeltoBin = Join-Path $VeltoHome "bin"

Write-Host "================================"
Write-Host "        Velto Installer"
Write-Host "================================"
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git is required."
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is required."
    exit 1
}

Write-Host "Installing Velto..."

if (Test-Path $VeltoHome) {
    Remove-Item -Recurse -Force $VeltoHome
}

git clone --depth 1 $VeltoRepo $VeltoHome

New-Item -ItemType Directory -Force $VeltoBin | Out-Null

$Launcher = Join-Path $VeltoBin "velto.cmd"

@"
@echo off
python "%USERPROFILE%\.velto\velto_cli.py" %*
"@ | Set-Content $Launcher

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($UserPath -notlike "*$VeltoBin*") {
    [Environment]::SetEnvironmentVariable(
        "Path",
        "$UserPath;$VeltoBin",
        "User"
    )
}

Write-Host ""
Write-Host "Velto installed successfully."
Write-Host ""
Write-Host "Restart your terminal."
Write-Host "Then run:"
Write-Host "velto --version"
