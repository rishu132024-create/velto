#!/data/data/com.termux/files/usr/bin/bash

set -e

VELTO_HOME="$HOME/.velto"
VELTO_BIN="$PREFIX/bin"
VELTO_REPO="https://github.com/rishu132024-create/velto.git"

echo "Installing Velto for Termux..."

pkg update -y
pkg install python git -y

rm -rf "$VELTO_HOME"

git clone --depth 1 "$VELTO_REPO" "$VELTO_HOME"

cat > "$VELTO_BIN/velto" <<'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
exec python "$HOME/.velto/velto_cli.py" "$@"
SCRIPT

chmod +x "$VELTO_BIN/velto"

echo ""
echo "Velto installed successfully."
echo ""
echo "Run:"
echo "velto --version"
