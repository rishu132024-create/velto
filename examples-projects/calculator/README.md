# Velto Calculator

A simple calculator example written in Velto.

## Run

```bash
velto main.vlt
### 3️⃣ Number Game

```bash
cd ~/velto/examples-projects/number-game
cat > main.vlt <<'VLT'
target = 7
guess = 7

say "Velto Number Game"

if guess == target:
    say "Correct!"
else:
    say "Try again!"
VLT

cat > README.md <<'MD'
# Velto Number Game

A simple number guessing game example.

## Run

```bash
velto main.vlt
### 4️⃣ Web example

```bash
cd ~/velto/examples-projects/web-app
cat > main.vlt <<'VLT'
message = "Hello from Velto Web!"

say message
VLT

cat > README.md <<'MD'
# Velto Web Example

A simple Velto web-project starting point.

## Run

```bash
velto main.vlt
### 5️⃣ Main examples README

```bash
cd ~/velto/examples-projects
cat > README.md <<'MD'
# Velto Example Projects

Ready-to-run example projects for learning Velto.

## Projects

### Calculator

A simple arithmetic calculator.

### Number Game

A basic condition-based game.

### Web App

A starting point for Velto web development.

## Goal

These examples are intended to help new Velto users
learn by modifying real programs.
