#!/bin/sh

set -e

VELTO_HOME="$HOME/.velto"
VELTO_BIN="$HOME/.local/bin"
VELTO_REPO="https://github.com/rishu132024-create/velto.git"

echo "Installing Velto..."

rm -rf "$VELTO_HOME"

git clone --depth 1 "$VELTO_REPO" "$VELTO_HOME"

mkdir -p "$VELTO_BIN"

cat > "$VELTO_BIN/velto" <<'SCRIPT'
#!/bin/sh
exec python3 "$HOME/.velto/velto_cli.py" "$@"
SCRIPT

chmod +x "$VELTO_BIN/velto"

echo ""
echo "Velto installed."
echo ""
echo "Run:"
echo "velto --version"
