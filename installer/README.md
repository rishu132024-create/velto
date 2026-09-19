# Velto Universal Installer

Velto provides platform-specific terminal installers.

## Linux

Run:

curl -fsSL https://raw.githubusercontent.com/rishu132024-create/velto/main/installer/linux/install.sh | sh

## macOS

Run:

curl -fsSL https://raw.githubusercontent.com/rishu132024-create/velto/main/installer/macos/install.sh | sh

## Android Termux

Run:

curl -fsSL https://raw.githubusercontent.com/rishu132024-create/velto/main/installer/termux/install.sh | bash

## Windows

Run the PowerShell installer:

irm https://raw.githubusercontent.com/rishu132024-create/velto/main/installer/windows/install.ps1 | iex

## After installation

Run:

velto --version

velto new myapp

velto run main.vlt
