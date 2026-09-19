$ErrorActionPreference = "Stop"

$VeltoHome = Join-Path $env:USERPROFILE ".velto"
$VeltoRepo = "https://github.com/rishu132024-create/velto.git"

Write-Host "Installing Velto..."

if (Test-Path $VeltoHome) {
    Remove-Item -Recurse -Force $VeltoHome
}

git clone --depth 1 $VeltoRepo $VeltoHome

$VeltoBin = Join-Path $VeltoHome "bin"

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
Write-Host "Velto installed."
Write-Host "Restart your terminal and run:"
Write-Host "velto --version"
