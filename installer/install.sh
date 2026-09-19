#!/bin/sh

set -e

VELTO_REPO="https://github.com/rishu132024-create/velto.git"
VELTO_HOME="$HOME/.velto"
VELTO_BIN="$HOME/.local/bin"

echo "================================"
echo "        Velto Installer"
echo "================================"
echo ""

OS="$(uname -s)"

case "$OS" in
    Linux)
        echo "Detected: Linux"
        ;;
    Darwin)
        echo "Detected: macOS"
        ;;
    *)
        echo "Unsupported operating system."
        exit 1
        ;;
esac

if ! command -v git >/dev/null 2>&1; then
    echo "Git is required."
    echo "Please install Git and run this installer again."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required."
    echo "Please install Python 3 and run this installer again."
    exit 1
fi

echo "Installing Velto..."

rm -rf "$VELTO_HOME"

git clone --depth 1 "$VELTO_REPO" "$VELTO_HOME"

mkdir -p "$VELTO_BIN"

cat > "$VELTO_BIN/velto" <<'SCRIPT'
#!/bin/sh
exec python3 "$HOME/.velto/velto_cli.py" "$@"
SCRIPT

chmod +x "$VELTO_BIN/velto"

case ":$PATH:" in
    *":$VELTO_BIN:"*)
        ;;
    *)
        SHELL_NAME="$(basename "${SHELL:-sh}")"

        if [ "$SHELL_NAME" = "zsh" ]; then
            PROFILE="$HOME/.zshrc"
        else
            PROFILE="$HOME/.bashrc"
        fi

        if [ -f "$PROFILE" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE"
        fi
        ;;
esac

echo ""
echo "Velto installed successfully."
echo ""
echo "Restart your terminal or run:"
echo ""
echo 'export PATH="$HOME/.local/bin:$PATH"'
echo ""
echo "Then:"
echo ""
echo "velto --version"
echo "velto --help"
