# Installing Velto

Velto can be installed using Python's package manager.

## Requirements

Python 3.9 or newer.

## Linux

Install Python and pip, then run:

python3 -m pip install velto-lang

Check:

velto --version

Run a program:

velto hello.vlt

## macOS

Install Python 3.9 or newer.

Run:

python3 -m pip install velto-lang

Check:

velto --version

Run:

velto hello.vlt

## Windows

Install Python 3.9 or newer.

Open PowerShell and run:

py -m pip install velto-lang

Check:

velto --version

Run:

velto hello.vlt

## Android

Install Termux.

Install Python:

pkg update
pkg install python

Install Velto:

python -m pip install velto-lang

Check:

velto --version

Run:

velto hello.vlt

## Upgrade

Linux and macOS:

python3 -m pip install --upgrade velto-lang

Windows:

py -m pip install --upgrade velto-lang

Android Termux:

python -m pip install --upgrade velto-lang

## Uninstall

Linux and macOS:

python3 -m pip uninstall velto-lang

Windows:

py -m pip uninstall velto-lang

Android Termux:

python -m pip uninstall velto-lang

## First Program

Create:

hello.vlt

Add:

say "Hello, Velto!"

Run:

velto hello.vlt
